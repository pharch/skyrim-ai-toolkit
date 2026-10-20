#!/usr/bin/env python3
"""Resolve and identify the configured GOG Actor subobject vtables read-only."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.address_library_probe import probe as probe_address_library
from tools.ghidra_probe import run_query


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    config = read_local_config(ROOT)
    commonlib_value = config.get("COMMONLIBSSE_ROOT", "").strip()
    if not commonlib_value:
        raise RuntimeError("COMMONLIBSSE_ROOT is not configured")
    include = _native_path(commonlib_value) / "include" / "RE"
    source_hashes = {
        "Offsets_VTABLE.h": sha256(include / "Offsets_VTABLE.h"),
        "A/Actor.h": sha256(include / "A" / "Actor.h"),
    }

    address_rows = [
        probe_address_library(symbol="VTABLE::Actor", vtable_index=index)
        for index in range(10)
    ]
    if any(not row.get("ok") for row in address_rows):
        raise RuntimeError("one or more CommonLib Actor vtable entries did not resolve")
    rvas = [int(str(row["address_library_rva"]), 16) for row in address_rows]

    ghidra_meta = run_query(timeout=600, vtable_rtti_rvas=rvas)
    if not ghidra_meta.get("ok"):
        raise RuntimeError("GOG Actor vtable RTTI census was incomplete; inspect the preserved adapter metadata")
    stdout_path = ROOT / str(ghidra_meta["artifacts"]["stdout"])
    rtti_lines = [
        line.strip()
        for line in stdout_path.read_text(encoding="utf-8", errors="replace").splitlines()
        if "VTABLE_RTTI_" in line
    ]
    captured = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "read_only": True,
        "transaction_id": "TX-20261018-0008",
        "source_header_sha256": source_hashes,
        "address_library_rows": address_rows,
        "ghidra_metadata": ghidra_meta,
        "ghidra_rtti_lines": rtti_lines,
    }
    out_dir = ROOT / ".local" / "alignment" / "transactions" / "TX-20261018-0008"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = out_dir / f"actor-vtable-rtti-census-{stamp}.json"
    output.write_text(json.dumps(captured, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "capture": output.relative_to(ROOT).as_posix(),
        "capture_sha256": sha256(output),
        "ghidra_stdout": ghidra_meta["artifacts"]["stdout"],
        "ghidra_stdout_sha256": ghidra_meta["stdout_sha256"],
        "rtti_lines": rtti_lines,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        raise SystemExit(2)
