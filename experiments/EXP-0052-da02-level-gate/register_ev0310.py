from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261016-0045"
NOTE = TX / "EV-0310-note.md"
MANIFEST = TX / "EV-0310-capture-manifest.json"
REGISTER = ROOT / "research/EVIDENCE.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    register = json.loads(REGISTER.read_text(encoding="utf-8"))
    items = register["items"]
    if any(row.get("id") == "EV-0310" for row in items):
        raise ValueError("EV-0310 already exists in research/EVIDENCE.json")

    local_hashes = {
        Path(row["artifact"]).name: row["sha256"]
        for row in manifest["private_capture_files"]
    }
    local_hashes[MANIFEST.name] = digest(MANIFEST)
    evidence = {
        "id": "EV-0310",
        "kind": "record",
        "source": "Prepared five official-master DA02 Story Manager/QUST/DIAL/INFO/reference records and bound base-Misc PEX, read through tested local source routes",
        "artifact": ".local/alignment/transactions/TX-20261016-0045/EV-0310-note.md",
        "sha256": digest(NOTE),
        "captured_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "edition": "AE",
        "runtime": "Prepared master and Skyrim - Misc.bsa hashes are in the capture manifest. Installed Steam AE 1.6.1170.0 identity is EV-0109 and was not used for runtime claims. Complete active order, profile winner, and live quest state are unverified.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "tools/plugin_reader.py and direct read-only TES4 parsing through the strict Python 3.12 dispatcher",
            "EXP-0052 group-aware DA02 DIAL/INFO join, source-reference scanners, Story Manager decoder, and exact FormID resolution",
            "tools/papyrus_pex.py read-only extraction/disassembly from the prepared Skyrim - Misc.bsa source",
            "TES5Edit dev-4.1.6 schema source for CTDA GetEventData, SMEN/SMQN, QUST aliases, and reference placement fields",
            "Native xEdit bridge attempted; WSL interop failed before record enumeration, preserved as a failed route rather than xEdit evidence",
        ],
        "coverage": "Prepared Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, and Dragonborn.esm (1,178,548 records and 5,791,306 subrecords in the prepared corpus); targeted DA02 and WEDA02 records; Skyrim.esm Story Manager census; 73 DA02 DIAL topics and 95 linked INFO children; focused all-signature FormID/book-reference scans; fixed book-reference locations; selected base-Misc book, encounter-trigger, and cultist scripts. Non-official plugins, active-profile winners, other archives, dynamic/native callers, complete runtime state, and gameplay are outside scope.",
        "result": "DA02 main QUST 0004D8D6 is the child of a level-30 Story Manager node and Start Game Enabled is clear. WEDA02's own Story Manager conditions require DA02 already running at a stage below 1, so it is downstream in the inspected source path. Four fixed book references disable below the level-30 global; book OnRead still calls DA02.SetStage(1) below stage 1, with stopped-quest behavior unknown. Generic list rows have minimum level 24; QABooksContainer's only source placement is in QASmoke. No level-one main-quest start, functional progression, or Sacellum access is established.",
        "local_hashes": local_hashes,
    }
    items.append(evidence)
    REGISTER.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0310 with {len(local_hashes)} local artifact hashes")


if __name__ == "__main__":
    main()
