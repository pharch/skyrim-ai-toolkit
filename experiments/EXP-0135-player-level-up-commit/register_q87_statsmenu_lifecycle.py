#!/usr/bin/env python3
"""Register the corrected StatsMenu constructor/factory/destructor trace."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
EVIDENCE = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions/TX-20261020-0006/q87-statsmenu-factory-lifecycle.json"
BUILD_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> None:
    specs = {
        "destructor_wrapper": ("20261020T043113Z", "0x96DF50"),
        "destructor_body": ("20261020T043222Z", "0x960D40"),
        "constructor": ("20261020T043335Z", "0x9607F0"),
        "menu_factory": ("20261020T043445Z", "0x96E280"),
        "factory_registration": ("20261020T043545Z", "0xBC3F0"),
    }
    manifests: dict[str, dict] = {}
    raw: dict[str, str] = {}
    for name, (stamp, rva) in specs.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = load(meta_path)
        if (meta.get("ok") is not True or meta.get("read_only") is not True or
                meta.get("auto_analysis_disabled") is not True or
                meta.get("analysis_binary_product_version") != "1.6.1179" or
                meta.get("analysis_binary_sha256") != BUILD_SHA or
                str(meta.get("requested_rva", "")).lower() != rva.lower() or
                meta.get("stdout_sha256") != digest(stdout)):
            raise SystemExit(f"build/read-only/hash/RVA verification failed: {name}")
        manifests[name] = {
            "metadata": f"private-local:{meta_path.relative_to(ROOT).as_posix()}",
            "metadata_sha256": digest(meta_path),
            "stdout": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
            "stdout_sha256": digest(stdout),
            "requested_rva": meta.get("requested_rva"),
        }
        raw[name] = stdout.read_text(encoding="utf-8", errors="replace")

    required = {
        "destructor_wrapper": ("XREF_ANY=1419026a8 -> 14096df50", "CALL 0x140960d40"),
        "destructor_body": ("*param_1 = StatsMenu::vftable", "param_1[0x58]", "FUN_140cc8800"),
        "constructor": ("*param_1 = StatsMenu::vftable", "XREF_CALL_EDGE=14096e2dd -> 1409607f0"),
        "menu_factory": ("CALL qword ptr [RAX + 0x50]", "CALL 0x1409607f0", "XREF_ANY_SOURCE_USER=1400bc3fe"),
        "factory_registration": ("s_StatsMenu_142019370,FUN_14096e280", "StatsMenu"),
    }
    for name, needles in required.items():
        if not all(needle in raw[name] for needle in needles):
            raise SystemExit(f"required constructor/factory/destructor evidence missing: {name}")

    summary = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": "TX-20261020-0006",
        "gog_build": {"product_version": "1.6.1179.0", "sha256": BUILD_SHA, "rvas_transferred_to_steam": False},
        "captures": manifests,
        "mapping": {
            "constructor": "FUN_1409607f0 zeros/initializes StatsMenu fields and installs the RTTI-identified vtable at RVA 0x19026A8; its one analyzed direct caller is FUN_14096E280.",
            "factory": "FUN_14096E280 obtains a 0x328-byte object from a UI-manager virtual slot +0x50, then calls the constructor. FUN_1400BC3F0 registers the string StatsMenu with FUN_14096E280 as its factory callback. FUN_14096E280 has zero analyzed direct-call incoming edges; the callback is referenced by the registration body.",
            "destructor_correction": "FUN_140960D40 releases/refcounts owned fields and calls cleanup routines before resetting the StatsMenu vftable; its analyzed direct caller is FUN_14096DF50, which occupies the vftable's first entry. Thus EV-0692's constructor attribution to FUN_140960D40 is corrected: the RTTI and ProcessMessage slot mapping remain valid, while FUN_1409607F0 is the observed constructor.",
            "update_relation": "EV-0692 maps FUN_1409611E0 to StatsMenu::ProcessMessage slot 4 and UI_MESSAGE_TYPE::kUpdate. Its threshold branch calls FUN_14077D650, which writes GetLevel+1 to the same base-data field. This is an update-message-gated threshold writer on a StatsMenu instance.",
        },
        "limits": "The static factory registration identifies the menu type and callback, not the user input or exact runtime timing that requests the menu. The captures do not show whether the kUpdate branch runs before, during, or after the player's acceptance of a pending level-up, nor establish Steam 1.6.1170.0 behavior or a natural level-one gate result.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = load(EVIDENCE)
    if any(row.get("id") == "EV-0693" for row in ledger.get("items", [])):
        raise SystemExit("EV-0693 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0693",
        "captured_utc": summary["captured_utc"],
        "kind": "native",
        "source": "Identity-checked read-only GOG StatsMenu constructor, menu-factory callback and registration function, plus vtable destructor caller path.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": digest(SUMMARY),
        "edition": "AE",
        "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Steam 1.6.1170.0 is separate [EV-0109].",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x96df50 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x960d40 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x9607f0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x96e280 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xbc3f0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q87_statsmenu_lifecycle.py",
        ],
        "coverage": "Corrects the StatsMenu construction/destruction direction: FUN_1409607F0 is the observed constructor; FUN_140960D40 is a cleanup/destructor body called by vtable slot-0 wrapper FUN_14096DF50. FUN_1400BC3F0 registers the StatsMenu factory callback FUN_14096E280, which allocates an object through the UI manager and invokes the constructor. This relates to EV-0692's RTTI/slot-4 kUpdate mapping.",
        "result": "PASS for the bounded GOG factory lifecycle and correction of EV-0692's constructor attribution. It supports that the threshold writer identified in EV-0691/EV-0692 runs in StatsMenu::ProcessMessage(kUpdate) on an instantiated StatsMenu object. It does not establish the exact user action or whether that update is before/after level-up acceptance.",
        "local_hashes": {name: meta["stdout_sha256"] for name, meta in manifests.items()},
        "related_evidence": ["EV-0109", "EV-0260", "EV-0689", "EV-0691", "EV-0692"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0693", "summary_sha256": digest(SUMMARY)}, indent=2))


if __name__ == "__main__":
    main()
