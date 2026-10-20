from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T182837Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x6be430":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
stdout = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=5",
    "INDIRECT_CALL_SITE_COUNT=1",
    "INCOMING_CALLER_FUNCTION_COUNT=4",
    "FUN_140699500",
    "FUN_1406b9df0",
    "FUN_1403fd6b0",
):
    if token not in stdout:
        raise SystemExit(f"required helper trace result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0600",
    "source": "Identity-checked GOG full direct-caller and direct-callee trace for FUN_1406be430",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x6be430 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1406be430 has five direct callees, one indirect site, and four analyzed direct callers: FUN_1407ee620, FUN_1406b9df0, FUN_140699500, and FUN_1406be2c0. The helper normalizes/transforms 3D vector inputs, obtains an ActorValueOwner-like object at Actor+0xb8 and calls its virtual +0x8 with numeric ActorValue 0x24, computes an output vector and calls FUN_1403fd6b0; that callee resolves an object/physics-like state and passes a computed vector to a nested virtual +0x80 sink, with child traversal. In FUN_140699500's tag-0x0A path, the helper receives Actor/process-derived scalar/vector values, pointer Actor+0x54, flags (1,0), and a null final context. In FUN_1406b9df0's candidate HitData path, it receives a HitData-structured pointer and fields copied from that record. These argument shapes are distinct. The helper has no direct mapped HitData/armor-skill resolver or UseSkill call; exact ActorValue name, physics interface RTTI, transitive effects, and runtime impact remain open.",
    "result": "The shared helper is a vector-processing route with an ActorValue lookup at numeric 0x24 and a nested vector/physics-like sink; it is not itself a direct AV11/AV12/UseSkill route. The tag-0x0A caller uses Actor/process-derived state and Actor+0x54 with null final context, unlike FUN_1406b9df0's HitData-record arguments. The shared function identity does not make the tag-0x0A branch a HitData/armor-XP route. A follow-on Actor vtable slot +0x50 remains unresolved. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": {f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)},
    "related_evidence": ["EV-0599", "EV-0598", "EV-0429", "EV-0294", "EV-0261"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0600" in existing and existing["EV-0600"] != item:
    raise SystemExit("EV-0600 collision")
if "EV-0600" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L412",
    "| CL-L412 | In GOG AE 1.6.1179.0, FUN_1406be430 is a vector-processing helper with five direct callees, one indirect ActorValueOwner-like slot +0x8 call using numeric value 0x24, and a nested vector/physics-like sink FUN_1403fd6b0; its four callers include both tag-0x0A Actor state and candidate HitData paths with distinct argument shapes. | supported for the captured static paths | [EV-0600] | ActorValue name, exact nested interface RTTI, effects, and any runtime protection/XP result remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0152 — Shared FUN_1406be430 transforms vectors through an ActorValue-scaled physics-like sink (EV-0600)",
    """## M-0152 — Shared FUN_1406be430 transforms vectors through an ActorValue-scaled physics-like sink (EV-0600)

`FUN_1406be430` normalizes/transforms 3D vectors, queries an ActorValueOwner-like object at Actor `+0xb8` through virtual slot `+0x8` with numeric value `0x24`, then routes a computed vector to `FUN_1403fd6b0` and a nested virtual `+0x80` sink [EV-0600]. Its tag-0x0A caller passes Actor/process-derived state and Actor `+0x54`, while candidate HitData caller `FUN_1406b9df0` passes HitData-record fields; this is a shared utility with distinct data sources, not proof of the same damage or XP operation. The helper has no direct AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 edge is added. Claim CL-L412.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Shared vector helper separates tag-0x0A state from candidate HitData arguments (EV-0600)",
    """### Shared vector helper separates tag-0x0A state from candidate HitData arguments (EV-0600)

`FUN_1406be430` has five direct callees and one indirect ActorValueOwner-like getter. It transforms vector inputs, reads numeric ActorValue `0x24`, and passes a computed vector to a nested physics-like sink `FUN_1403fd6b0` [EV-0600]. The tag-0x0A Actor callback passes process-derived scalar/vector data, Actor `+0x54`, and null final context; `FUN_1406b9df0` supplies fields copied from a HitData-shaped record. No direct AV11/AV12/UseSkill sink occurs in the helper. This narrows away direct HitData argument equivalence while leaving high-level effects unknown. Resolve Actor slot `+0x50` called immediately after the helper, then continue caller 47/62.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "EV-0600 cross-domain vector/helper synthesis",
    "EV-0600 shows a shared vector-processing helper reached from both a candidate HitData handler and the tag-0x0A Actor state callback, but the callers supply distinct data shapes. The helper queries numeric ActorValue 0x24 and ends at a nested vector/physics-like interface; it contains no direct armor-skill award. This is a cross-system reuse of a low-level vector effect, not a causal bridge from the tag-0x0A event to incoming HitData, effective armor protection, or AV11/AV12. Keep the actor slot +0x50 and helper interface identity unresolved [EV-0600], [EV-0429], [EV-0294].",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0600 distinguishes two callers of shared vector helper FUN_1406be430",
    "EV-0600 connects the tag-0x0A Actor state callback and candidate HitData handler to shared FUN_1406be430 while preserving their distinct arguments. The helper queries numeric ActorValue 0x24 and reaches a vector/physics-like sink, with no direct AV11/AV12/UseSkill edge. No OBJ-1/OBJ-2 causal relationship is established.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0600"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L412"]))

for candidate in (
    {
        "id": "Q79-H102",
        "model": "The tag-0x0A call to FUN_1406be430 passes the same HitData pointer/source fields as the candidate HitData caller FUN_1406b9df0.",
        "predicted_discriminant": "The tag-0x0A call should pass the HitData-record pointer and fields used by FUN_1406b9df0; captured arguments instead come from Actor/process state and Actor+0x54, with a null final context.",
        "status": "falsified",
        "evidence": ["EV-0600"],
    },
    {
        "id": "Q79-H103",
        "model": "The bounded tag-0x0A shared-helper branch is a distinct Actor/process vector effect; its direct helper path contains no AV11/AV12/UseSkill award.",
        "predicted_discriminant": "The tag-0x0A caller uses process-derived vector/scalar inputs and Actor+0x54, while FUN_1406be430 transforms vectors through a numeric ActorValue lookup and nested vector/physics-like sink without a mapped skill award.",
        "status": "supported",
        "evidence": ["EV-0600"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    else:
        prior.update(candidate)

assessment = "EV-0600 resolves the shared helper's bounded direct body as vector transformation with numeric ActorValue 0x24 lookup and a nested vector/physics-like sink. The tag-0x0A caller and candidate HitData caller pass different argument shapes, falsifying direct HitData-record equivalence for this branch. No AV11/AV12/UseSkill edge appears in the helper; Actor slot +0x50 remains to resolve."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x189EC20 --vtable-slot 0xA --timeout 600 to identify the Actor method invoked at byte offset +0x50 after FUN_1406be430. Screen its target and direct callees, then close caller 46 as a bounded Actor/process vector event and continue caller 47/62 FUN_140658a30."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: caller 46's tag-0x0A Actor path reaches a shared vector helper but passes Actor/process data rather than the HitData-shaped inputs used by FUN_1406b9df0. The helper reads numeric ActorValue 0x24 and reaches a physics-like vector sink, with no direct AV11/AV12/UseSkill route. Resolve Actor slot +0x50, then continue caller 47/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "its 195-call census includes a process-conditioned call to shared candidate helper FUN_1406be430, while 45 virtual sites remain.",
    "its 195-call census includes a process-conditioned call to shared vector helper FUN_1406be430; that branch uses Actor/process data, not the HitData-shaped arguments from FUN_1406b9df0, and the helper has no direct AV11/AV12/UseSkill sink. 45 virtual sites remain.",
    1,
)
old_next = "**Selected next line:** trace caller context and descendants of `FUN_1406be430` shared by the tag-0x0A Actor callback and candidate hit route [EV-0599], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep 45 virtual sites and GOG/Steam boundaries open."
new_next = "**Selected next line:** resolve Actor vtable slot `0xA` / byte offset `+0x50` called after the tag-0x0A vector helper [EV-0600], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0600/CL-L412/M-0152; falsified H102, supported H103; checkpointed Actor slot 0xA")
