from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T180636Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x6589f0":
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
    "id": "EV-0592",
    "source": "Identity-checked GOG worker caller 46 tag-0x43 builder and bounded producer census",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x6589f0 --list-call-edges --timeout 600",
    ],
    "coverage": "FUN_1406589f0 constructs worker event tag 0x43 with an object pointer and a dword, atomically increments the object's field +0x28 when non-null, and calls FUN_14065b800. It has one direct outgoing edge, zero indirect sites, and seven direct producer functions: FUN_1407bacf0, FUN_1407bad40, FUN_1407bad90, FUN_1407bade0, FUN_1407bae30, FUN_1407bae80, and FUN_1407baef0. The first decompiled producer FUN_1407bacf0 branches on FUN_1406d4110: when true, it submits the object with value 1 through the tag-0x43 builder; otherwise it calls FUN_14069e070(object,1) directly. Existing worker evidence EV-0574 maps case 0x43 to FUN_14069e070(object,payload_dword). Other six producers and the exact helper body remain to be examined. The builder has no direct mapped HitData/protection/AV11/AV12/UseSkill edge; this is not a transitive or runtime negative.",
    "result": "Caller 46 is a ref-counted object-plus-dword tag-0x43 event with seven producers. For the captured producer FUN_1407bacf0, gate-true queueing and gate-false direct execution both target FUN_14069e070 with object and value 1; worker case 0x43 also forwards its object/dword to that helper [EV-0574]. This supports queue/direct convergence for the sampled producer only. The other producers, helper semantics, and runtime identity remain unknown; Q79-H1/H2/H3 stay open and no OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0591", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0592" in existing and existing["EV-0592"] != item:
    raise SystemExit("EV-0592 collision")
if "EV-0592" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L404",
    "| CL-L404 | In GOG AE 1.6.1179.0, worker caller FUN_1406589f0 builds tag 0x43 with object+dword payload and seven producers; the sampled producer FUN_1407bacf0 uses FUN_14069e070(object,1) on the gate-clear path while its gate-set branch queues the same object/value, and worker case 0x43 calls FUN_14069e070. | supported for the captured producer and worker case | [EV-0592], [EV-0574] | Six producers, helper semantics, runtime object type, descendant effects, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0146 — Tag-0x43 object/dword queued update candidate (EV-0592)",
    """## M-0146 — Tag-0x43 object/dword queued update candidate (EV-0592)

`FUN_1406589f0` serializes tag `0x43`, an object pointer and a dword, retaining the object through an increment at `+0x28` before sending it to the shared worker [EV-0592]. It has seven direct producers. The sampled producer `FUN_1407bacf0` sends `(object,1)` through the builder when the shared gate is set and calls `FUN_14069e070(object,1)` directly when clear; worker case `0x43` also calls `FUN_14069e070(object,dword)` [EV-0574], [EV-0592]. This supports queue/direct convergence for the sampled route only. The other producers and helper body remain to be traced. No HitData/protection/AV11/AV12/UseSkill or OBJ-1 edge is established by the builder. Claim CL-L404.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 46/62: FUN_1406589f0 tag-0x43 sampled convergence (EV-0592)",
    """### Caller 46/62: FUN_1406589f0 tag-0x43 sampled convergence (EV-0592)

Caller `FUN_1406589f0` creates tag `0x43` with an object plus dword and increments the object refcount at `+0x28`; seven direct producer functions reach it [EV-0592]. The sampled `FUN_1407bacf0` calls `FUN_1406d4110`; gate true submits `(object,1)` through the worker builder, while gate false calls `FUN_14069e070(object,1)` directly. Existing worker evidence maps case `0x43` to `FUN_14069e070(object,payload_dword)` [EV-0574]. This supports direct/deferred helper convergence for that producer, not all seven. Inspect the shared helper and the remaining producer families; no direct armor/HitData edge is established by the builder.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 46 queue/direct and combat-sink models",
    """## Caller 46 queue/direct and combat-sink models

- Q79-H87: the sampled tag-0x43 producer's gate-set and gate-clear paths converge on `FUN_14069e070` with the same object and dword. Prediction: worker case 0x43 forwards the builder payload to that helper, matching the direct branch.
- Q79-H88: the sampled producer's queued route changes target or payload relative to its direct branch. Prediction: the worker case calls a different helper or reorders/drops the fields.

EV-0574 and EV-0592 support H87 and falsify H88 for the sampled `FUN_1407bacf0` route. Six producers and helper behavior remain to be traced; do not generalize to the whole tag family.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0592 maps caller 46 tag-0x43 sampled convergence",
    "EV-0592 maps tag 0x43 as a retained object+dword worker payload with seven producer functions. For sampled producer FUN_1407bacf0, gate-set queueing and gate-clear direct execution both target FUN_14069e070(object,1), matching worker case 0x43 [EV-0574]. Six producer bodies and helper semantics remain unresolved; no OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0592"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L404"]))
for candidate in (
    {
        "id": "Q79-H87",
        "model": "For the sampled tag-0x43 producer FUN_1407bacf0, gate-set worker submission and gate-clear immediate execution converge on FUN_14069e070 with the same object and dword.",
        "predicted_discriminant": "Worker case 0x43 forwards its object+dword to FUN_14069e070, matching the sampled immediate call arguments.",
        "status": "supported",
        "evidence": ["EV-0592", "EV-0574"],
    },
    {
        "id": "Q79-H88",
        "model": "For the sampled tag-0x43 producer, the queued route changes helper target or payload relative to its gate-clear immediate branch.",
        "predicted_discriminant": "Worker case 0x43 calls a different helper or changes the object/dword arguments relative to FUN_1407bacf0's immediate branch.",
        "status": "falsified",
        "evidence": ["EV-0592", "EV-0574"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0592 adds a seven-producer tag-0x43 object/dword family. The sampled first producer's immediate and deferred routes converge on FUN_14069e070 with the same values, but six producers and the helper body remain open. This adds no HitData/armor-skill or OBJ-1 edge."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x69e070 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; inspect the exact tag-0x43 shared helper and its direct/indirect sinks against mapped HitData/protection/AV11/AV12/UseSkill targets, then compare all seven producer bodies for direct/deferred payload parity. Keep event semantics and runtime type open."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 46/62 tag 0x43 is a retained object+dword event with seven producers. One sampled producer converges on FUN_14069e070 across its gate-set and gate-clear paths; inspect the helper before classifying the family. Sixteen original callers remain.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace("45 of 62 initially uninspected worker callers are reviewed, with 17 remaining.", "46 of 62 initially uninspected worker callers are reviewed, with 16 remaining.", 1)
state = state.replace("Q-0079 has 45/62 exact worker callers reviewed; 17 remain.", "Q-0079 has 46/62 exact worker callers reviewed; 16 remain.", 1)
state = state.replace(
    "EV-0591 reclassifies its sole data xref as likely x64 unwind metadata, not gameplay registration.",
    "EV-0591 reclassifies its sole data xref as likely x64 unwind metadata, not gameplay registration. EV-0592 maps caller 46/tag 0x43 as a retained object+dword event with seven producers; one sampled producer's immediate and worker routes converge on FUN_14069e070.",
    1,
)
state = state.replace(
    "EV-0591 identifies its sole data xref as likely x64 unwind metadata.",
    "EV-0591 identifies caller 45's sole data xref as likely x64 unwind metadata; EV-0592 maps caller 46/tag 0x43 to a seven-producer object+dword update candidate.",
    1,
)
old_next = "**Selected next line:** inspect caller 46/62 `FUN_1406589f0` for its payload, producer, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0591]. The caller-45 data xref matches likely x64 unwind metadata; keep tag-0x40 input provenance and decoded RTTI unresolved."
new_next = "**Selected next line:** inspect shared helper `FUN_14069e070` for tag-0x43 direct/indirect sinks and compare its direct/deferred producer routes [EV-0592]. Keep all seven source identities, event meaning, runtime type, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0592/CL-L404/M-0146; supported Q79-H87, falsified H88 for sampled route; checkpointed shared helper")
