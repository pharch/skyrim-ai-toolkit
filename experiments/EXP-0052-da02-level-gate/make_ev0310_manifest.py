from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TX = ROOT / ".local/alignment/transactions/TX-20261016-0045"
OUT = TX / "EV-0310-capture-manifest.json"

CAPTURES = [
    "da02-smqn-node.stdout.raw",
    "da02-global.stdout.raw",
    "da02-update-qust.stdout.raw",
    "da02-skyrim-qust.stdout.raw",
    "da02-hook-qust.stdout.raw",
    "da02-initial-decoded.stdout.raw",
    "da02-dialogue-join.stdout.raw",
    "da02-dialogue-join.json",
    "da02-dialogue-summary.stdout.raw",
    "da02-all-master-formid-scan.stdout.raw",
    "da02-book-reference-scan.stdout.raw",
    "da02-book-reference-cells.stdout.raw",
    "da02-qabookscontainer-references.stdout.raw",
    "da02-CONT-000C2D3B.stdout.raw",
    "da02-story-tree-decoded.stdout.raw",
    "da02-story-node-exact-formids.stdout.raw",
    "da02-specific-node-all-masters.stdout.raw",
    "da02-quest-node-all-all-masters.stdout.raw",
    "da02-priority-node-all-all-masters.stdout.raw",
    "DA02BookScript.pex",
    "DA02BookScript.extract.stdout.raw",
    "DA02BookScript.disassembly.stdout.raw",
    "WETriggerScript.pex",
    "WETriggerScript.extract.stdout.raw",
    "WETriggerScript.disassembly.stdout.raw",
    "WEDA02CultistScript.pex",
    "WEDA02CultistScript.extract.stdout.raw",
    "WEDA02CultistScript.disassembly.stdout.raw",
    "da02-native-WEQuestNode.stdout.raw",
]

INPUTS = [
    "experiments/EXP-0052-da02-level-gate/README.md",
    "experiments/EXP-0052-da02-level-gate/hypothesis.md",
    "experiments/EXP-0052-da02-level-gate/expected-discriminants.md",
    "experiments/EXP-0052-da02-level-gate/protocol.md",
    "experiments/EXP-0052-da02-level-gate/results.md",
    "experiments/EXP-0052-da02-level-gate/make_ev0310_manifest.py",
    "experiments/EXP-0052-da02-level-gate/register_ev0310.py",
    "experiments/EXP-0052-da02-level-gate/join_da02_dialogue.py",
    "experiments/EXP-0052-da02-level-gate/lookup_story_node_formids.py",
    "experiments/EXP-0052-da02-level-gate/resolve_da02_book_refs.py",
    "experiments/EXP-0052-da02-level-gate/scan_da02_container_references.py",
    "experiments/EXP-0052-da02-level-gate/scan_bsa_story_event_callers.py",
    "experiments/EXP-0052-da02-level-gate/summarize_da02_initial.py",
    "experiments/EXP-0052-da02-level-gate/summarize_da02_refs.py",
    "experiments/EXP-0052-da02-level-gate/summarize_da02_story_tree.py",
    "tools/plugin_reader.py",
    "tools/papyrus_pex.py",
    "scripts/python_env.py",
    "scripts/research_state.py",
    "scripts/research_transactions.py",
]

MASTERS = {
    "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
    "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
    "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
    "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
    "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def file_row(path: Path, display_path: str) -> dict[str, object]:
    if not path.is_file():
        raise FileNotFoundError(display_path)
    return {"artifact": display_path, "size_bytes": path.stat().st_size, "sha256": sha256(path)}


def main() -> None:
    note_path = TX / "EV-0310-note.md"
    private_files = [file_row(TX / name, f".local/alignment/transactions/TX-20261016-0045/{name}") for name in CAPTURES]
    private_files.append(file_row(note_path, ".local/alignment/transactions/TX-20261016-0045/EV-0310-note.md"))
    research_inputs = [
        {"artifact": name, "sha256": sha256(ROOT / name)}
        for name in INPUTS
    ]
    manifest = {
        "evidence_id": "EV-0310",
        "transaction_id": "TX-20261016-0045",
        "source_scope": "prepared five official-master DA02 Story Manager/QUST/DIAL/INFO/reference screens plus read-only base-Misc PEX extraction and disassembly; direct-parser evidence, no profile winner or live test",
        "prepared_master_sha256": MASTERS,
        "archive_sha256": {
            "Skyrim - Misc.bsa": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d"
        },
        "external_schema": {
            "url": "https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas",
            "revision": "TES5Edit dev-4.1.6",
            "areas": "SMEN/SMQN previous-node and event-type fields; CTDA GetEventData function/member packing; QUST conditions and aliases; CONT/REFR placement",
        },
        "private_capture_files": private_files,
        "research_input_hashes": research_inputs,
        "not_included": [
            "machine-specific configured paths or private indexes",
            "complete active plugin order or profile winners",
            "game process, save/co-save, live Story Manager state, or gameplay measurements",
            "console, injected script, or altered-plugin intervention",
        ],
    }
    OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} with {len(private_files)} captures and {len(research_inputs)} input hashes")


if __name__ == "__main__":
    main()
