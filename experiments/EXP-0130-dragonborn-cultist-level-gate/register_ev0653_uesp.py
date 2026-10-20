#!/usr/bin/env python3
"""Register revision-pinned local UESP grounding for Q-0081."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "research" / "EVIDENCE.json"
PAGES = {
    "Skyrim:Dragonborn (quest)": (".local/uesp/q81/dragonborn-quest.raw.json", 3632370),
    "Skyrim:Cultist": (".local/uesp/q81/cultist.raw.json", 3586604),
    "Skyrim:The Way of the Voice": (".local/uesp/q81/way-of-the-voice.raw.json", 3587321),
}


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def main() -> None:
    pages = {}
    for title, (path, revision) in PAGES.items():
        data = json.loads((ROOT / path).read_text(encoding="utf-8"))
        if data.get("title") != title or data.get("revision_id") != revision:
            raise SystemExit(f"unexpected UESP title/revision for {title}")
        pages[title] = data
    if "DLC2CultistAmbush" not in pages["Skyrim:Dragonborn (quest)"].get("content", "") or "DLC2WE09" not in pages["Skyrim:Dragonborn (quest)"].get("content", ""):
        raise SystemExit("Dragonborn quest page does not distinguish both cultist routes")
    if "Level 25" not in pages["Skyrim:The Way of the Voice"].get("content", ""):
        raise SystemExit("Way of the Voice page no longer carries the screened world-encounter threshold")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    known = {item["id"] for item in ledger["items"]}
    if "EV-0653" not in known:
        captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
        paths = {path for path, _ in PAGES.values()}
        primary = PAGES["Skyrim:Dragonborn (quest)"][0]
        ledger["items"].append({
            "id": "EV-0653",
            "captured_utc": captured,
            "kind": "wiki",
            "source": "Local UESP SQLite payloads, revision-pinned: Skyrim:Dragonborn (quest) rev 3632370; Skyrim:Cultist rev 3586604; Skyrim:The Way of the Voice rev 3587321. Local corpus completeness and dump provenance remain unverified.",
            "artifact": "private-local:" + primary,
            "sha256": sha256(primary),
            "runtime": "Secondary-source grounding only; no Skyrim runtime or official-record condition observed.",
            "lane": "offline",
            "tools": ["strict Python 3.12 dispatcher", "tools.uesp local page lookup"],
            "coverage": "Dragonborn quest giver alternatives and post-Way-of-the-Voice city/town path; world-encounter level note; cultist level scaling distinction.",
            "result": "The UESP Dragonborn quest page labels its two givers as DLC2CultistAmbush (two cultists) and DLC2WE09 (three cultists), and describes the stage-driven path after The Way of the Voice. The Way of the Voice page says the level-25 requirement applies to cultists in world encounters only. The Cultist page says player level changes the encountered combat variant. These secondary-source notes suggest separate stage-driven and world-encounter paths but do not prove the official record conditions or runtime behavior.",
            "local_hashes": {path: sha256(path) for path in sorted(paths)},
            "related_evidence": ["EV-0260"],
            "modified_state": False,
        })
        LEDGER.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"registered": "EV-0653", "count": len(ledger["items"])}, indent=2))
    else:
        print(json.dumps({"already_present": "EV-0653", "count": len(ledger["items"])}, indent=2))


if __name__ == "__main__":
    main()
