#!/usr/bin/env python3
"""Validate and register the Q85 source-order and UESP ferry captures."""
from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TX = "TX-20261020-0004"
LOCAL_TX = ROOT / ".local/alignment/transactions" / TX
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
RECOVERY_PATH = ROOT / "research/RECOVERY.json"
DIRECT = {
    "dlc2we09": LOCAL_TX / "dlc2we09.raw.json",
    "priority_selector": LOCAL_TX / "dlc2we-priority.raw.json",
    "world_node": LOCAL_TX / "dlc2wenode.raw.json",
    "world_event_parent": LOCAL_TX / "world-script-event.raw.json",
    "gjalund_npcs": LOCAL_TX / "gjalund-npc.raw.json",
    "gjalund_topics": LOCAL_TX / "gjalund-dialogue-topics.raw.json",
    "dragonborn_infos": LOCAL_TX / "dragonborn-info-all.raw.json",
}
UESP = {
    "transport": ROOT / ".local/uesp/q85/transport.raw.json",
    "gjalund": ROOT / ".local/uesp/q85/gjalund.raw.json",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_capture(path: Path) -> tuple[dict, list[dict]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("exit_code") != 0:
        raise SystemExit(f"parser capture failed: {path}")
    rows = [json.loads(line) for line in payload.get("records_jsonl", "").splitlines() if line.strip()]
    if len(rows) != payload.get("record_count"):
        raise SystemExit(f"record count mismatch: {path}")
    return payload, rows


def get_record(rows: list[dict], signature: str, form_id: str) -> dict:
    matches = [r for r in rows if r.get("signature") == signature and r.get("file_form_id") == form_id]
    if len(matches) != 1:
        raise SystemExit(f"expected one {signature} {form_id}, found {len(matches)}")
    return matches[0]


def sub(record: dict, signature: str) -> list[bytes]:
    return [bytes.fromhex(row["hex"]) for row in record.get("subrecords", []) if row.get("signature") == signature]


def main() -> None:
    recovery = json.loads(RECOVERY_PATH.read_text(encoding="utf-8"))
    if recovery.get("status") != "running" or recovery.get("transaction_id") != TX or recovery.get("frontier_id") != "Q-0085":
        raise SystemExit("Q85 is not active; refusing evidence registration")
    for path in [*DIRECT.values(), *UESP.values()]:
        if not path.is_file():
            raise SystemExit(f"required raw capture missing: {path}")

    parsed = {name: load_capture(path) for name, path in DIRECT.items()}
    qust = get_record(parsed["dlc2we09"][1], "QUST", "020331C0")
    selector = get_record(parsed["priority_selector"][1], "SMQN", "020331C1")
    node = get_record(parsed["world_node"][1], "SMBN", "0201E7D9")
    parent = get_record(parsed["world_event_parent"][1], "SMEN", "0001379A")
    if len(sub(parent, "CTDA")) != 0:
        raise SystemExit("unexpected world event parent conditions")
    if len(parsed["dragonborn_infos"][1]) != 4421:
        raise SystemExit("unexpected Dragonborn INFO screen denominator")

    topic = get_record(parsed["gjalund_topics"][1], "DIAL", "0203A135")
    tifc = sub(topic, "TIFC")
    if len(tifc) != 1:
        raise SystemExit("expected one Windhelm passage TIFC")
    child_count = int.from_bytes(tifc[0], "little")
    infos = sorted((r for r in parsed["dragonborn_infos"][1] if r.get("offset", -1) > topic["offset"]), key=lambda r: r["offset"])
    children = infos[:child_count]
    if len(children) != child_count:
        raise SystemExit("not enough INFO records after Windhelm passage DIAL")
    child_functions = []
    for info in children:
        functions = []
        for raw in sub(info, "CTDA"):
            if len(raw) < 10:
                raise SystemExit(f"short CTDA in INFO {info.get('file_form_id')}")
            functions.append(int.from_bytes(raw[8:10], "little"))
        child_functions.append({"info_form_id": info["file_form_id"], "offset": info["offset"], "function_indices": functions})
    if any(80 in row["function_indices"] for row in child_functions):
        raise SystemExit("GetLevel function index 80 present in bounded ferry-topic INFO group")

    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    source_summary = {
        "captured_utc": captured,
        "source": "Configured Steam AE Dragonborn.esm Data file, direct read-only TES4 parser; no active-profile winner resolution.",
        "identity": "Steam SkyrimSE.exe 1.6.1170.0 identity is separately preserved in EV-0109; these parser results are source-file records only.",
        "captures": {
            name: {"artifact": f"private-local:{path.relative_to(ROOT).as_posix()}", "sha256": sha(path), "record_count": parsed[name][0]["record_count"], "query_route": parsed[name][0].get("query_route")}
            for name, path in DIRECT.items()
        },
        "records": {
            "DLC2WE09": {"signature": "QUST", "file_form_id": qust["file_form_id"], "editor_id": qust.get("editor_id"), "CTDA_count_in_record": len(sub(qust, "CTDA")), "related_primary_evidence": ["EV-0657", "EV-0665", "EV-0666", "EV-0667", "EV-0668", "EV-0669"]},
            "DLC2WEPriorityQuests": {"signature": "SMQN", "file_form_id": selector["file_form_id"], "CTDA_count": len(sub(selector, "CTDA")), "related_primary_evidence": ["EV-0661"]},
            "DLC2WENode": {"signature": "SMBN", "file_form_id": node["file_form_id"], "CTDA_count": len(sub(node, "CTDA")), "related_primary_evidence": ["EV-0664"]},
            "world_event_parent": {"signature": "SMEN", "file_form_id": parent["file_form_id"], "CTDA_count": len(sub(parent, "CTDA")), "related_primary_evidence": ["EV-0662"]},
            "DLC2SolstheimLocation": {"signature": "LCTN", "file_form_id": "04016E2A", "related_primary_evidence": ["EV-0657"]},
        },
        "ferry_topic_screen": {
            "topic_form_id": topic["file_form_id"], "editor_id": topic.get("editor_id"), "file_offset": topic["offset"], "TIFC_info_count": child_count,
            "association_method": "The six INFO records are associated by DIAL TIFC count and serialized file order after the DIAL topic; this is a source-order-derived association, not an xEdit native group export.",
            "infos": child_functions, "GetLevel_function_index_80_present": False,
            "scope_limit": "Direct Dragonborn.esm rows and schema-derived CTDA function index only; no winning-profile or live-dialogue claim.",
        },
        "world_trigger_chain": {
            "related_evidence": ["EV-0389", "EV-0390", "EV-0661", "EV-0662", "EV-0664"],
            "summary": "Previously captured official trigger placements/property assignments and WETriggerScript submit WEStart/WERoadStart events; the scoped trigger/selector chain has no explicit player-level predicate. It does not establish when the engine evaluates DLC2WE09 or whether Steam starts it at level 1.",
        },
        "interpretation": "Static condition decoding supports chance AND MQ105 stage >=160 AND DLC2MQ06 stage <550 AND (GetLevel >=25 OR current location is Solstheim). The SMEN/SMQN/SMBN route has no extra level row in the screened official records. The stage/chance preconditions, evaluation timing, natural level-one QUST startup, aliases, and winning profile remain unresolved.",
    }
    LOCAL_TX.mkdir(parents=True, exist_ok=True)
    summary_path = LOCAL_TX / "q85-source-summary.json"
    summary_path.write_text(json.dumps(source_summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    pages = {}
    for key, path in UESP.items():
        page = json.loads(path.read_text(encoding="utf-8"))
        expected = {"transport": (3560422, "Skyrim:Transport"), "gjalund": (3579973, "Skyrim:Gjalund Salt-Sage")}[key]
        if (page.get("revision_id"), page.get("title")) != expected or not page.get("url", "").endswith(f"oldid={expected[0]}"):
            raise SystemExit(f"unexpected UESP page identity for {key}")
        pages[key] = {"title": page["title"], "revision_id": page["revision_id"], "timestamp": page["timestamp"], "url": page["url"], "artifact": f"private-local:{path.relative_to(ROOT).as_posix()}", "sha256": sha(path)}
    gjalund_content = json.loads(UESP["gjalund"].read_text(encoding="utf-8"))["content"]
    required_phrases = ["If you have not encountered them", "250 gold", "If you have encountered the cultists"]
    if not all(phrase in gjalund_content for phrase in required_phrases):
        raise SystemExit("Gjalund revision lacks expected initial/post-cultist passage descriptions")
    uesp_manifest = {
        "captured_utc": captured,
        "pages": pages,
        "grounded_observation": "The revision-cited Gjalund page describes initial paid passage before the cultists are encountered and a refusal/dialogue check after they have been encountered. It does not state player level or prove dialogue availability at level 1.",
        "corpus_provenance": "Local UESP dump completeness/license/acquisition provenance remains unverified; see corpus doctor note. Secondary grounding only.",
    }
    manifest_path = LOCAL_TX / "q85-uesp-manifest.json"
    manifest_path.write_text(json.dumps(uesp_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    existing = {row["id"] for row in evidence["items"]}
    new_ids = {"EV-0686", "EV-0687"}
    if existing & new_ids or max(int(row["id"].split("-")[1]) for row in evidence["items"]) != 685:
        raise SystemExit("evidence IDs moved or Q85 IDs already exist; reselect instead of duplicating")
    items = [
        {
            "id": "EV-0686", "captured_utc": captured, "kind": "record",
            "source": "Configured Steam AE Dragonborn.esm records queried by the retained direct read-only TES4 parser; source-file scope only.",
            "artifact": f"private-local:{summary_path.relative_to(ROOT).as_posix()}", "sha256": sha(summary_path), "edition": "AE",
            "runtime": "Steam SkyrimSE.exe 1.6.1170.0 identity is in EV-0109; this is not a profile-specific winner screen.", "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py file-records (see exact per-record requests and source capture metadata in the private summary)", "python3 scripts/python_env.py run experiments/EXP-0134-dlc2we09-location-alternative/register_q85_evidence.py"],
            "coverage": "Seven direct parser captures include DLC2WE09 QUST, its Story Manager selector/node/parent records, two Gjalund NPC records, 23 Gjalund DIAL topics, and the complete 4,421-record Dragonborn.esm INFO screen. The bounded Windhelm passage topic has six INFO rows derived from TIFC and serialized offset order; its CTDA function indices contain no GetLevel index 80. The separate official world trigger/selector route and condition decoder findings remain EV-0389/EV-0390 and EV-0657–EV-0669. This does not resolve a winning load order, precondition reachability, runtime evaluation timing, or natural QUST start.",
            "result": "PASS for the bounded source-file screen. The five QUST predicates retain the location OR alternative after chance and stage constraints; screened upstream Story Manager selectors and the source-ordered initial ferry dialogue rows contain no explicit GetLevel predicate. These are static candidate conditions, not an observed level-one transition.",
            "local_hashes": {name: sha(path) for name, path in DIRECT.items()}, "related_evidence": ["EV-0109", "EV-0389", "EV-0390", "EV-0657", "EV-0661", "EV-0662", "EV-0664", "EV-0665", "EV-0666", "EV-0667", "EV-0668", "EV-0669", "EV-0260"]
        },
        {
            "id": "EV-0687", "captured_utc": captured, "kind": "wiki",
            "source": "Revision-pinned local UESP pages Skyrim:Transport rev 3560422 and Skyrim:Gjalund Salt-Sage rev 3579973.",
            "artifact": f"private-local:{manifest_path.relative_to(ROOT).as_posix()}", "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "Secondary-source pages only; no executable, plugin winner, save, or gameplay observation.", "modified_state": False, "lane": "offline",
            "tools": ["python3 scripts/python_env.py run -m tools.uesp page --db .local/uesp.sqlite3 <title> --raw", "python3 scripts/python_env.py run experiments/EXP-0134-dlc2we09-location-alternative/register_q85_evidence.py"],
            "coverage": "Both raw page JSON captures retain title, revision ID, timestamp, exact oldid URL, and SHA-256 in the private manifest. The Gjalund page describes the before-cultist 250-gold route and a different post-cultist refusal/check. The local UESP corpus doctor does not verify dump acquisition/completeness/license provenance; this remains secondary grounding, not a level-one behavioral result.",
            "result": "PASS as secondary grounding for an ordinary ferry route to Solstheim and its dialogue change after the cultist encounter. The page does not claim the player can reach or start DLC2WE09 at level 1.",
            "local_hashes": {key: sha(path) for key, path in UESP.items()}, "related_evidence": ["EV-0653", "EV-0654", "EV-0657", "EV-0686", "EV-0260"]
        }
    ]
    evidence["items"].extend(items)
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": [row["id"] for row in items], "summary_sha256": sha(summary_path), "manifest_sha256": sha(manifest_path), "ferry_topic_children": child_functions}, indent=2))

if __name__ == "__main__":
    main()
