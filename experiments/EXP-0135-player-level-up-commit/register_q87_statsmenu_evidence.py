#!/usr/bin/env python3
"""Register the StatsMenu::ProcessMessage / kUpdate identity for Q87."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.local_config import read_local_config

TX = "TX-20261020-0006"
REVISION = "b93280e832f263dbef44e44cbe2936622a02f91a"
GHIDRA = ROOT / ".local/ghidra"
RECOVERY = ROOT / "research/RECOVERY.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions" / TX / "q87-statsmenu-update-semantics.json"


def resolve_root(value: str) -> Path:
    win = PureWindowsPath(value)
    if os.name != "nt" and win.drive and len(win.drive) == 2 and win.drive[1] == ":":
        path = Path("/mnt") / win.drive[0].lower() / Path(*win.parts[1:])
    else:
        path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> None:
    recovery = load(RECOVERY)
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != ("running", TX, "Q-0087"):
        raise SystemExit("Q87 is not the active transaction")
    expected_binary = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
    capture_specs = {
        "statsmenu_constructor": ("20261020T042304Z", "0x960D40"),
        "statsmenu_vtable": ("20261020T042411Z", None),
        "statsmenu_vtable_slots": ("20261020T042206Z", None),
        "post_write_ui_event": ("20261020T041854Z", "0x9366D0"),
    }
    manifest = {}
    texts = {}
    for name, (stamp, expected_rva) in capture_specs.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = load(meta_path)
        if (meta.get("ok") is not True or meta.get("read_only") is not True or
            meta.get("auto_analysis_disabled") is not True or
            meta.get("analysis_binary_product_version") != "1.6.1179" or
            meta.get("analysis_binary_sha256") != expected_binary or
            meta.get("stdout_sha256") != sha(stdout)):
            raise SystemExit(f"identity/read-only/hash check failed: {name}")
        if expected_rva and str(meta.get("requested_rva", "")).lower() != expected_rva.lower():
            raise SystemExit(f"requested RVA mismatch: {name}")
        manifest[name] = {
            "metadata": f"private-local:{meta_path.relative_to(ROOT).as_posix()}",
            "metadata_sha256": sha(meta_path),
            "stdout": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
            "stdout_sha256": sha(stdout),
            "requested_rva": meta.get("requested_rva"),
            "query_mode": meta.get("query_mode"),
        }
        texts[name] = stdout.read_text(encoding="utf-8", errors="replace")

    if ".?AVStatsMenu@@" not in texts["statsmenu_vtable"]:
        raise SystemExit("StatsMenu RTTI name is missing")
    if "VTABLE_RTTI_TABLE_RVA=0x19026A8" not in texts["statsmenu_vtable"]:
        raise SystemExit("StatsMenu vtable address is missing")
    if "POINTER_TABLE_ENTRY=index:1 address:1419026c8 value:0x1409611E0 target:1409611e0" not in texts["statsmenu_vtable_slots"]:
        raise SystemExit("StatsMenu vtable slot 4 target is missing")
    if "LEA RAX, [0x1419026a8]" not in texts["statsmenu_constructor"] or "MOV qword ptr [RCX], RAX" not in texts["statsmenu_constructor"]:
        raise SystemExit("constructor does not install the RTTI-identified vtable")
    if "*puVar2 = 0x46" not in texts["post_write_ui_event"]:
        raise SystemExit("post-write UI event marker is missing")

    config = read_local_config(ROOT)
    source = resolve_root(config.get("COMMONLIBSSE_ROOT", "").strip())
    current_revision = subprocess.run(["git", "-C", str(source), "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    if current_revision != REVISION:
        raise SystemExit("CommonLib source revision changed")
    stats_header = source / "include/RE/S/StatsMenu.h"
    message_header = source / "include/RE/U/UIMessage.h"
    stats_text = stats_header.read_text(encoding="utf-8")
    message_text = message_header.read_text(encoding="utf-8")
    required_stats = ("kRequiresUpdate", "ProcessMessage(UIMessage& a_message) override;", "// 04")
    required_message = ("kUpdate = 0", "stl::enumeration<UI_MESSAGE_TYPE, std::uint32_t> type;")
    if not all(term in stats_text for term in required_stats) or not all(term in message_text for term in required_message):
        raise SystemExit("pinned CommonLib StatsMenu/UIMessage declarations changed")
    stats_hash, message_hash = sha(stats_header), sha(message_header)
    if stats_hash != "ae9252150831d06fa41a03a4b8fc7b8bb1c2de419c0bddd16fab0fe0ea262c51" or message_hash != "e8ba08918aa5c7a24f6a24d56257832d3e476323c6232eeb5f869366b35c3f59":
        raise SystemExit("CommonLib source header hash mismatch")

    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {
        "captured_utc": captured,
        "transaction": TX,
        "gog_build": {"product_version": "1.6.1179.0", "sha256": expected_binary, "rvas_transferred_to_steam": False},
        "ghidra_captures": manifest,
        "commonlib": {
            "revision": current_revision,
            "StatsMenu_header": {"source_relative": "include/RE/S/StatsMenu.h", "sha256": stats_hash, "declaration": "StatsMenu inherits IMenu; flags include kRequiresUpdate; ProcessMessage(UIMessage&) override is vtable slot 0x04."},
            "UIMessage_header": {"source_relative": "include/RE/U/UIMessage.h", "sha256": message_hash, "declaration": "UIMessage type field is at +0x08; UI_MESSAGE_TYPE::kUpdate is numeric 0."},
        },
        "mapping": "GOG vtable RTTI at RVA 0x19026A8 is .?AVStatsMenu@@. Constructor FUN_140960d40 installs that vtable on its object. FUN_1409611e0 is at vtable base +0x20, slot 4, matching CommonLib StatsMenu::ProcessMessage. Its switch reads UIMessage type at +0x08 and the captured level-writer branch is under case 0, which CommonLib identifies as kUpdate. In that branch, the progress predicate is checked, the field writer FUN_14077d650 runs, and then FUN_1409366d0 dispatches a post-write UI event.",
        "limits": "The field write is in a StatsMenu update-message handler, separate from the resolved ConfirmLevelUpAttributeCallback body. StatsMenu declares kRequiresUpdate, but this static mapping does not prove which player action opened the menu or whether that action counts as acceptance in the pending-level premise. Exact Skill/Level event callback registrations and Steam 1.6.1170.0 runtime behavior remain unresolved.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = load(EVIDENCE)
    if any(row.get("id") == "EV-0692" for row in ledger.get("items", [])):
        raise SystemExit("EV-0692 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0692",
        "captured_utc": captured,
        "kind": "native",
        "source": "GOG StatsMenu vtable RTTI, constructor-assigned vtable, bounded pointer-table read, and pinned CommonLibSSE-NG StatsMenu/UIMessage declarations.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": sha(SUMMARY),
        "edition": "AE",
        "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. CommonLibSSE-NG revision b93280e832f263dbef44e44cbe2936622a02f91a. Steam 1.6.1170.0 remains separate [EV-0109].",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --vtable-rtti-rvas 0x19026a8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --pointer-table-rva 0x19026c0 --pointer-count 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x960d40 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/inspect_stats_menu_api.py",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/inspect_ui_message_type.py",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q87_statsmenu_evidence.py",
        ],
        "coverage": "RTTI identifies the constructor-installed vtable as StatsMenu. Pointer-table indexing from vtable base +0x18 places FUN_1409611e0 at slot 4, which pinned CommonLib declares as StatsMenu::ProcessMessage. Its switch cases on UIMessage type; case 0 is UI_MESSAGE_TYPE::kUpdate. The captured writer branch is in that case and dispatches a UI event after the level-field write.",
        "result": "PASS for identifying a threshold-gated Player level-field write in the StatsMenu update-message path, before the post-write UI event and outside the resolved attribute-confirm callback. This supports the bounded GOG notification/update model. It does not establish whether opening StatsMenu itself is the player's acceptance action, whether the handler executes before the UI is opened, Steam behavior, or a natural level-one quest-gate result.",
        "local_hashes": {
            "statsmenu_header": stats_hash,
            "ui_message_header": message_hash,
            "vtable_rtti_stdout": manifest["statsmenu_vtable"]["stdout_sha256"],
            "vtable_slot_stdout": manifest["statsmenu_vtable_slots"]["stdout_sha256"],
            "constructor_stdout": manifest["statsmenu_constructor"]["stdout_sha256"],
        },
        "related_evidence": ["EV-0109", "EV-0260", "EV-0688", "EV-0689", "EV-0691"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0692", "summary_sha256": sha(SUMMARY), "CommonLib_revision": current_revision}, indent=2))


if __name__ == "__main__":
    main()
