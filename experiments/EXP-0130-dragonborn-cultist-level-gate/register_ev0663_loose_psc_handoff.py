#!/usr/bin/env python3
"""Register hash-checked loose Dragonborn PSC observations as source-only evidence."""
from __future__ import annotations

from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = ROOT / ".local/alignment/transactions/TX-20261019-0002/q81-psc-source"
LEDGER = ROOT / "research/EVIDENCE.json"
MANIFEST = SOURCE_DIR / "manifest.json"
FILES = {
    "DLC2_QF_DLC2CultistAmbush_0203546D.psc": "f8db4cafaedf0f4f270ac5662b5ad6505745b1f4a79e6712fe8611137ed848ae",
    "DLC2WE09ActorScript.psc": "21c787fe2e67e4f842afcc34a47f1a3ae22508bd11d899b10746ba9eecc342bb",
    "DLC2WECultistAmbushPlayerScript.psc": "db724f3148c4f842cf1270b4cbbee5bce809416e79799f2b6502bd7a5a9bdd4d",
    "DLC2_QF_DLC2WE09_020331C0.psc": "65d2bf1fa1dbd63b73a1483c52b55525d24cb72f8bdc1e61aad337666b545b95",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = {entry["archive_relative_source"].split("/")[-1]: entry for entry in manifest.get("files", [])}
    if manifest.get("capture_method") != "read-only byte copy into ignored .local; no game source or plugin changed":
        raise SystemExit("unexpected source capture method")
    if set(entries) != set(FILES):
        raise SystemExit("unexpected source manifest inventory")
    for name, expected in FILES.items():
        if digest(SOURCE_DIR / name) != expected or entries[name].get("sha256") != expected:
            raise SystemExit(f"source hash mismatch: {name}")

    main_qf = (SOURCE_DIR / "DLC2_QF_DLC2CultistAmbush_0203546D.psc").read_text(encoding="utf-8")
    world_qf = (SOURCE_DIR / "DLC2_QF_DLC2WE09_020331C0.psc").read_text(encoding="utf-8")
    actor_script = (SOURCE_DIR / "DLC2WE09ActorScript.psc").read_text(encoding="utf-8")
    player_script = (SOURCE_DIR / "DLC2WECultistAmbushPlayerScript.psc").read_text(encoding="utf-8")
    required_fragments = [
        (main_qf, ";BEGIN FRAGMENT Fragment_0", "DLC2MQ01.Start()", "DLC2MQ01.SetStage(5)", "DLC2WE09Chance.setValue(5)"),
        (world_qf, ";BEGIN FRAGMENT Fragment_5", "DLC2MQ01.Start()", "DLC2MQ01.SetStage(5)", "DLC2WE09Chance.setValue(5)"),
    ]
    for text, *needles in required_fragments:
        if any(needle not in text for needle in needles):
            raise SystemExit("expected shared stage-10 handoff statements absent")
    if "if DLC2MQ01.GetStage() < 10" not in actor_script or "GetOwningQuest().setStage(10)" not in actor_script:
        raise SystemExit("actor alias stage-10 writer not present")
    if "if akAggressor == Game.GetPlayer()" not in actor_script or "GetReference().GetDistance(Game.GetPlayer()) < 1000" not in actor_script:
        raise SystemExit("actor event predicates differ from expected source")
    if "Event OnLocationChange" not in player_script or "GetOwningQuest().Stop()" not in player_script:
        raise SystemExit("player alias location cleanup route not present")

    hashes = {name: digest(SOURCE_DIR / name) for name in FILES}
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0663" for item in ledger["items"]):
        raise SystemExit("EV-0663 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0663",
        "captured_utc": "2026-10-19T23:58:06+00:00",
        "kind": "source",
        "source": "Loose Source/Scripts PSC files found in the configured Steam Skyrim AE Data tree; hashes and paths are in the private source manifest.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261019-0002/q81-psc-source/manifest.json",
        "sha256": digest(MANIFEST),
        "edition": "AE",
        "runtime": "Configured Steam Skyrim AE Data source tree associated with independently verified executable identity EV-0109 (Steam 1.6.1170.0). This does not establish that these PSC bytes produced the active PEX or match any profile winner.",
        "modified_state": False,
        "lane": "offline",
        "tools": ["python3 scripts/python_env.py run experiments/EXP-0130-dragonborn-cultist-level-gate/screen_q81_script_files.py", "python3 scripts/python_env.py run experiments/EXP-0130-dragonborn-cultist-level-gate/capture_q81_loose_sources.py", "experiments/EXP-0130-dragonborn-cultist-level-gate/register_ev0663_loose_psc_handoff.py"],
        "coverage": "Hash-checked loose PSC source set: DLC2CultistAmbush QF stage fragment 0 (source FormID label 0203546D), DLC2WE09 QF fragment 5 (020331C0), DLC2WE09ActorScript, and DLC2WECultistAmbushPlayerScript. Both QF fragments contain a stage-10 sequence that starts DLC2MQ01, waits for it to run, fills DLC2MQ01AliasForObjective with Cultist1, sets DLC2MQ01 stage 5, and writes DLC2WE09Chance=5; their actor/faction/note setup differs. The actor alias source requests owning-quest stage 10 on player hit or nearby death while DLC2MQ01 stage<10. The player alias source polls location/cultist loading and can stop its owning quest after leaving. The source manifest found no loose PEX and reports configured Data/Dragonborn.bsa absent; no general BSA absence claim is made.",
        "result": "PASS for exact loose PSC byte capture and source-level statement checks. PSC is not runtime PEX evidence; script compilation, active source provenance, a complete profile order, and in-game behavior remain unresolved.",
        "local_hashes": hashes,
        "related_evidence": ["EV-0260", "EV-0654", "EV-0655", "EV-0657", "EV-0660", "EV-0661"],
    })
    LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0663", "psc_hashes": hashes, "manifest_hash": digest(MANIFEST), "scope": "loose source bytes only; PEX/runtime unverified"}, indent=2))


if __name__ == "__main__":
    main()
