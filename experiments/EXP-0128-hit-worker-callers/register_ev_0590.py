from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T180053Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x357c70":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")

local_hashes = {
    f".local/ghidra/{raw.name}": sha(raw),
    f".local/ghidra/{stderr.name}": sha(stderr),
    f".local/ghidra/{meta_path.name}": sha(meta_path),
}
item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0590",
    "source": "Identity-checked GOG direct/data-reference census for tag-0x40 producer FUN_140357c70",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x357c70 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_140357c70 has two outgoing direct calls (FUN_14033e470 and FUN_140658950), zero indirect sites, zero analyzed direct call xrefs, and one data xref to address RVA 0x362ffb4. The surrounding reported words include nearby code-relative values, but the query does not identify a containing object, source owner, descriptor schema, or registration type. Thus the wrapper is table-referenced in this analysis, but the table's semantics remain unknown.",
    "result": "The producer's direct construction path is bounded to decode-then-submit, while its sole analyzed incoming reference is a data location rather than a direct caller. The data-reference neighborhood does not resolve the selected decoder descriptor or output object's type. No gameplay, HitData, armor, quest-gate, or ActorValue interpretation is added; inspect the exact data address once, then continue caller 46/62 if the entry remains opaque.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0587", "EV-0588", "EV-0589", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0590" in existing and existing["EV-0590"] != item:
    raise SystemExit("EV-0590 collision")
if "EV-0590" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L402",
    "| CL-L402 | In GOG AE 1.6.1179.0, tag-0x40 producer FUN_140357c70 has no analyzed direct call xrefs and one data xref at RVA 0x362ffb4; the captured query does not identify the containing table's owner or descriptor semantics. | supported for the exact xref census | [EV-0590] | Static callback/descriptor registration and decoded type remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0145 — Tag-0x40 producer has unresolved data-table registration (EV-0590)",
    """## M-0145 — Tag-0x40 producer has unresolved data-table registration (EV-0590)

`FUN_140357c70` directly calls only the shared decoder and tag-0x40 builder, has no analyzed direct callers, and has one data xref at RVA `0x362ffb4` [EV-0590]. The nearby words are not enough to classify the containing object or selected decode descriptor. Treat this as a table-reference lead, not proof of a native command, event source, Actor type, or gameplay role. No OBJ-1/OBJ-2 causal edge is established. Claim CL-L402.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 45/62 data-registration census (EV-0590)",
    """### Caller 45/62 data-registration census (EV-0590)

`FUN_140357c70` has two direct outgoing calls (typed decoder `FUN_14033e470` and builder `FUN_140658950`), no indirect sites, no analyzed direct callers, and one data xref at RVA `0x362ffb4` [EV-0590]. Its containing table and descriptor semantics are not resolved by the captured context. Inspect that data location once; if it remains opaque, continue caller 46/62. No gameplay or OBJ-1/OBJ-2 meaning is assigned.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0590 retains an unresolved typed-value table reference",
    "EV-0590 records one data xref to tag-0x40 producer FUN_140357c70 at RVA 0x362ffb4, with no analyzed direct callers and no resolved containing-table semantics. The decode descriptor and runtime source remain unknown; no OBJ-1/OBJ-2 causal edge is added [EV-0589], [EV-0590].",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 45 registration reference (EV-0590)",
    """## Q-0079 update — caller 45 registration reference (EV-0590)

The tag-0x40 producer has no analyzed direct callers and one unresolved data reference at RVA `0x362ffb4`; the containing table does not yet identify the decoder descriptor or payload type [EV-0590]. Inspect that data address once, then continue caller 46/62 if it remains opaque [CL-L402], [M-0145].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0590"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L402"]))
assessment = "EV-0590 bounds caller 45's producer references to one unresolved data-table entry and no direct callers. The static table owner/descriptor remains unknown; no gameplay classification or OBJ-1/OBJ-2 edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --address-rva 0x362ffb4 --timeout 600; inspect the single table reference to FUN_140357c70 for a recoverable descriptor/registration owner. If the read-only address window stays untyped, preserve the uncertainty and continue caller 46/62 from the remaining-worker-callers baseline."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 45/62 uses typed-value decoding before tag-0x40 submission, and its sole incoming reference is an unresolved data-table entry at RVA 0x362ffb4. Seventeen original callers remain; inspect the address once, then continue caller 46.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
old_next = "**Selected next line:** inspect `FUN_140357c70` code/data references for its typed-value descriptor registration after EV-0589; if static registration remains opaque, continue caller 46/62. Keep input provenance, decoded RTTI, transitive behavior, and GOG/Steam boundaries unresolved."
new_next = "**Selected next line:** inspect the unresolved producer data reference at RVA `0x362ffb4` once [EV-0590]; if the table remains untyped, continue caller 46/62. Keep input provenance, decoded RTTI, transitive behavior, and GOG/Steam boundaries unresolved."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0590/CL-L402/M-0145; checkpointed unresolved data-reference inspection")
