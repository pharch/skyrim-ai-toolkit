#!/usr/bin/env python3
"""Register the bounded Dawnguard dialogue-to-Awakening source trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261017-0010"

CAPTURES = {
    ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-join.json": "89e0d2b4965071054cff8c05cfe0cbaeb26aac5e0f12d5a2c4d4cea7987c2b92",
    ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-callbacks.json": "9d93d8644e7c135ca0332b06f27b01b9de991b26326299362a46485092a633f0",
    ".local/alignment/transactions/TX-20261017-0010/dawnguard-vq-topic-summary.json": "01c57760ca0fb3972100718ab60025adad9312a3849ea8e50ce2178bf13f2c46",
    ".local/alignment/transactions/TX-20261017-0010/dawnguard-quest-vmad-summary.json": "765c7c3d32b3e6646b115759696a71813c1e035dc030d3d77fd6acf850cf2abe",
    ".local/alignment/transactions/TX-20261017-0010/dial-rumor-officials.json": "5b3191d19c5f0834d64c27b9603fcc4ff9b475aa9b5e79d142355fb16e9d7fc9",
    ".local/alignment/transactions/TX-20261017-0010/info-dlc1vq.json": "597a8153203edcfdb9822f0b698194ada18f182208deba429edd827591131828",
    ".local/alignment/transactions/TX-20261017-0010/qust-00D06C.json": "be2ca0c18ecd3a020800eafd6be309105e335aa14044f0e65fb4fdeda17dc223",
    ".local/alignment/transactions/TX-20261017-0010/qust-01A415.json": "fa4c403675139c9b959293f2e1c297fa36812a9d4fa988c7236514c75f2aab62",
    ".local/alignment/transactions/TX-20261017-0010/dawnguard-pex-probe/manifest.json": "3d5f0f26cf6bdfb0f76524d2567906342e98806fc054a7d7a0de0ea3341c8c80",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224108.719602Z/native-records.tsv": "91d1f3fc4b7b54bd791c5bf01af64f63e911c67e13f910fb6c025d35211d1963",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224108.719602Z/native-result.json": "f9630cae347312a1fb1021bcf2537ebe5a7a2b49d4db7fe8ce9c865f356884b6",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224108.719602Z/manifest.json": "d8919bf89405b3698d5c73eb7288d25ce19ef81a8f5fccf9ed148d526dff9159",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224108.719602Z/session.log": "36a5f556064ff3a8d92dbe40073c3d39cf38dfacdc46fa9b58a5c453285a31d9",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224108.719602Z/native-query-status.txt": "91fe73124ca5228bafbfc4d5af74b4c3de62a1c3ee01335f4ec36267a0c9278d",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/native-records.tsv": "2a7e08eb95219dd4c20d0c33549f4db570cc9030fa7c71c51d6935a674e8b036",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/native-result.json": "a59324b00d5532256b283d64b34ddb8f207f6f558ab7e99149ceeab9a0ad8e7b",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/manifest.json": "d5cecc6e6dd9d333f9459775be8148bc7fd3e0fa3aded9758b4e7a0a04866204",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/session.log": "dc7b0b20909017126382e8e02649faa51fbd4bfef5b1b3716f086e85fd5e5066",
    ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/native-query-status.txt": "91fe73124ca5228bafbfc4d5af74b4c3de62a1c3ee01335f4ec36267a0c9278d",
}

SOURCE_SHA256 = "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4"
MISC_BSA_SHA256 = "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    hashes: dict[str, str] = {}
    for relative, expected in CAPTURES.items():
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing capture: {relative}")
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"capture hash changed: {relative}: {actual}")
        hashes[relative] = actual

    results = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/results.md"
    if not results.is_file():
        raise SystemExit("missing EXP-0064 results.md")
    hashes[results.relative_to(ROOT).as_posix()] = sha(results)

    note = TX / "EV-0326-note.md"
    note.write_text(f"""# EV-0326 — Dawnguard Fort dialogue path to Awakening stage 10

## Source and query scope

The captured plugin is the official `Dawnguard.esm`, SHA-256 `{SOURCE_SHA256}`. The DIAL/INFO/QUST join resolves the fixed five-official-master source order only; it is not a selected-profile winner. A native xEdit query independently exported QUST `DLC1VQ00` (`0200D90E`) and `DLC1VQ01` (`0200352A`) from the five-master overlay. Both query sessions report `status=PASS`, `matches=1`; their TSV, JSON, session and query-status files are hashed in the capture manifest. The complete active plugin order remains unavailable under EV-0260.

The official source join covers 97 DIAL topics and 147 INFO children under `DLC1VQ00`, `DLC1VQ01`, `DLC1VQ01MiscObjective`, and `DLC1VQCastleGuard`. Linked INFO/QF PEX files were parsed from `Skyrim - Misc.bsa`, SHA-256 `{MISC_BSA_SHA256}`; the configured Data directory had no `Dawnguard.bsa`. The generic `defaultsetstagealiasscript` was not recovered by this narrow extractor. Its miss does not establish that the script is absent.

## Direct source observations

1. Native xEdit reports `DLC1VQ00` General Flags `Start Game Enabled=1`, `Starts Enabled=1`, `Run Once=1`. Durak INFO `0200D908` on `DLC1VQ00IntroTopic` has attached TIF `DLC1_TIF__0100D908`, which sets the owning VQ00 quest to stage 20. Durak INFO `0200D8E2` on `DLC1VQ00IntroC` has attached TIF `DLC1_TIF__0100D8E2`, which sets VQ00 to stage 50. Captured conditions constrain speaker identity and quest stage; neither INFO has a serialized `GetLevel` condition.
2. VQ00 stage-50 QF `Fragment_7` sets `DLC1VQ01MiscObjective` to stage 10. This is the separate Isran/Agmaer helper quest.
3. The captured Isran INFO callbacks advance that helper to stages 120 and 150; Tolan INFO `0200E8A6` advances it to stage 180. These INFOs have no `GetLevel` condition in the joined source data.
4. Helper stage-180 QF `Fragment_16` calls `DLC1VQ01.SetStage(10)`. Main VQ01 stage 10 sets the Dimhollow objective and map marker. Thus the source-linked Fort dialogue chain reaches a main-quest stage request rather than ending at a rumor/helper stage.
5. Native xEdit reports `DLC1VQ01` has `Run Once=1` and `Start Game Enabled=0`. Its four captured `GetInCell` conditions occur under objective-target fields for the two Dimhollow cells, not as whole-quest start or level conditions. Separate VQ00 approach INFOs `0200D057` and `0200D058` do carry `GetLevel >= DLC1VQMinLevel (10)`.
6. The QF/TIF capture contains 28 parsed PEX files linked to the four joined QUST owners, plus the ChangeLocation helper QF and three attached alias scripts. The separate main-owned Tolan INFO `02019AAB` also requests VQ01 stage 10, but its availability while VQ01 is stopped is unknown.

## Assessment and limits

These exact records support a strong source-level level-one candidate: the Fort dialogue route has no serialized level-10 condition and eventually requests VQ01 stage 10. The serialized level gate remains on the distinct Durak Story Manager helper/approach route. This does not prove that the Steam 1.6.1170.0 engine starts a stopped VQ01 quest through this `SetStage` call, that the relevant dialogue is naturally available at level 1, that aliases fill, or that the player can reach/progress through Dimhollow. GOG AE 1.6.1179.0 SetStage startup evidence EV-0313 is separate-build mechanism context and is not transferred to Steam. The exact next test remains a verified fresh level-one Steam save, complete selected profile order, no console or injected changes, and read-only before/after quest, alias, journal and access observations [EV-0260].

This OBJ-1 source path shares no identified ActorValue, HitData, armor-skill award, ActiveEffect, or serialization primitive with the OBJ-2 armor/XP route; no cross-objective causal edge is supported.
""", encoding="utf-8")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest_path = TX / "EV-0326-capture-manifest.json"
    manifest = {
        "evidence_id": "EV-0326",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "official_source": {"plugin": "Dawnguard.esm", "sha256": SOURCE_SHA256},
        "archive": {"name": "Skyrim - Misc.bsa", "sha256": MISC_BSA_SHA256, "version": 105},
        "source_order": ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"],
        "profile_winner_verified": False,
        "native_xedit_queries": [
            {"record": "DLC1VQ00", "form_id": "0200D90E", "session": "20261017T224108.719602Z", "status": "PASS", "matches": 1},
            {"record": "DLC1VQ01", "form_id": "0200352A", "session": "20261017T224439.768640Z", "status": "PASS", "matches": 1},
        ],
        "local_hashes": hashes,
        "limitations": ["No level-one runtime test", "No active profile winner", "Generic alias script extraction miss is not evidence of absence"],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    hashes[manifest_path.relative_to(ROOT).as_posix()] = sha(manifest_path)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0326" for row in evidence["items"]):
        raise SystemExit("EV-0326 already exists; refusing duplicate registration")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0326",
        "kind": "record",
        "source": "Dawnguard.esm DIAL/INFO/QUST/VMAD callbacks, linked PEX streams, and native xEdit five-official-master QUST exports.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0010/EV-0326-note.md",
        "sha256": sha(note),
        "runtime": f"Official Dawnguard.esm SHA-256 {SOURCE_SHA256}; fixed five-official-master source scope only, not an active-profile winner or runtime result.",
        "lane": "mechanism_inference",
        "tools": [
            "strict-dispatcher record-source join and VMAD decoder",
            "tested narrow Skyrim BSA PEX extractor and PEX parser",
            "native xEdit read-only official five-master QUST queries",
        ],
        "coverage": "97 joined DIAL topics and 147 INFO children under four VQ QUST owners; linked QF/TIF PEX bodies parsed; exact native QUST fields for VQ00 and VQ01. Generic defaultsetstagealiasscript extraction miss and live/runtime/profile scope are explicitly retained.",
        "result": "The start-enabled VQ00 Fort dialogue and Isran/Tolan helper callbacks form a source-linked no-GetLevel route to DLC1VQ01.SetStage(10), distinct from the level-10 Story Manager helper. This is a level-one candidate only; stopped-quest startup, natural dialogue availability, aliases, Steam behavior, useful access and vanilla reproduction are unverified.",
        "related_evidence": ["EV-0298", "EV-0299", "EV-0313", "EV-0260"],
        "local_hashes": hashes,
    })
    evidence_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"registered EV-0326; note sha256={sha(note)}; manifest sha256={sha(manifest_path)}")


if __name__ == "__main__":
    main()
