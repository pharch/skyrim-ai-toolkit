from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T182509Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x699500":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
stdout = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=195",
    "INDIRECT_CALL_SITE_COUNT=45",
    "14069aab6 -> 1406be430 target=FUN_1406be430",
    "FUN_1406be430(param_1,local_res10,fVar22,uVar25,uVar15,lVar10,1,0)",
):
    if token not in stdout:
        raise SystemExit(f"required call-census result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0599",
    "source": "Identity-checked GOG direct-call census for primary Actor method FUN_140699500 reached by tag-0x0A",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x699500 --list-call-edges --follow-direct-calls 8 --timeout 600"],
    "coverage": "Complete analyzed direct-call edge scan for FUN_140699500: 195 direct call instructions/edges and 45 unresolved indirect sites. No exact direct edge to mapped FUN_1406bb690, FUN_1406bcaa0, FUN_1407ddf50, or known Actor slot-0x104 damage handler FUN_1406bbb80 appears. One conditional branch at callsite RVA 0x69AAB6 calls FUN_1406be430(param_1,local_res10,fVar22,uVar25,uVar15,lVar10,1,0), where fVar22 comes from FUN_1406ee850(param_1[0x1f]), uVar15 from FUN_1406ee8c0(), and lVar10 points to Actor+0x54; it then calls FUN_1406ee8a0 and unresolved Actor vtable byte offset +0x50. Existing EV-0294 records FUN_1406be430 as a helper in a candidate ProcessTrapHit route but did not identify a skill-use call in its bounded body. The 45 indirect sites and transitive behavior remain unresolved.",
    "result": "The tag-0x0A Actor callback has a process-conditioned edge into shared helper FUN_1406be430, also present in the earlier candidate hit/damage path [EV-0429], [EV-0294]. This is a concrete code-identity convergence, not proof that the current arguments are HitData or that armor protection/AV11/AV12/UseSkill is affected. No direct edge to the mapped resolver/HealthDamage targets appears in this method's complete direct census; 45 indirect sites remain open. Investigate FUN_1406be430's incoming contexts and helper body before assigning damage or armor-XP significance. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": {f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)},
    "related_evidence": ["EV-0598", "EV-0294", "EV-0429", "EV-0261"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0599" in existing and existing["EV-0599"] != item:
    raise SystemExit("EV-0599 collision")
if "EV-0599" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L411",
    "| CL-L411 | In GOG AE 1.6.1179.0, tag-0x0A Actor method FUN_140699500 has 195 direct call edges and 45 unresolved indirect sites; one process-conditioned branch directly calls FUN_1406be430 with Actor/process-derived values and then Actor vtable byte offset +0x50. | supported for the exact static branch | [EV-0599] | FUN_1406be430's semantics on these arguments, the dynamic +0x50 target, transitive effects, and runtime armor/skill outcome remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0151 — Tag-0x0A Actor callback converges on shared helper FUN_1406be430 (EV-0599)",
    """## M-0151 — Tag-0x0A Actor callback converges on shared helper FUN_1406be430 (EV-0599)

The primary Actor callback `FUN_140699500` has 195 direct call edges and 45 unresolved indirect sites. One process-conditioned branch calls `FUN_1406be430` with Actor/process-derived scalar/vector values and a pointer to Actor `+0x54`, then invokes Actor vtable byte offset `+0x50` [EV-0599]. `FUN_1406be430` is also called from the earlier candidate hit/damage route [EV-0429]; the shared function identity does not prove shared HitData, protection, or XP semantics. No direct resolver/HealthDamage edge is present in the callback census. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L411.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### FUN_140699500 direct-call screen and shared-helper discriminator (EV-0599)",
    """### FUN_140699500 direct-call screen and shared-helper discriminator (EV-0599)

The complete direct-call census finds 195 edges and 45 unresolved indirect sites. No exact direct call reaches mapped `FUN_1406bb690`, `FUN_1406bcaa0`, `FUN_1407ddf50`, or `FUN_1406bbb80`. A process-conditioned branch calls `FUN_1406be430` with Actor/process-derived values and pointer `Actor+0x54`, then calls unresolved Actor vtable byte offset `+0x50` [EV-0599]. The same helper occurs in the earlier candidate hit/damage route [EV-0429], but no shared HitData or XP behavior is established. Query all direct callers and descendants of `FUN_1406be430` to test the competing models; preserve the 45 unresolved virtual sites as open.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0599 links tag-0x0A Actor callback to a shared candidate hit helper",
    "EV-0599 records a process-conditioned direct edge from tag-0x0A target FUN_140699500 to FUN_1406be430, the same helper called in the candidate hit/damage path EV-0429. Arguments differ and the helper lacks a confirmed AV11/AV12 sink in prior bounded evidence EV-0294, so this is a shared-code convergence only; no OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0599"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L411"]))
for candidate in (
    {
        "id": "Q79-H101",
        "model": "The tag-0x0A Actor callback contains a process-conditioned direct edge to shared helper FUN_1406be430, which also appears in the earlier candidate hit/damage route.",
        "predicted_discriminant": "The complete FUN_140699500 call census contains the exact direct callsite to FUN_1406be430 with Actor/process-derived scalar/vector inputs; this establishes shared code identity only.",
        "status": "supported",
        "evidence": ["EV-0599", "EV-0429"],
    },
    {
        "id": "Q79-H102",
        "model": "The tag-0x0A call to FUN_1406be430 carries or reconstructs a HitData/effective-protection/AV11/AV12/UseSkill flow and can affect armor XP.",
        "predicted_discriminant": "Incoming caller arguments, function descendants, or dynamic slots resolve the Actor/process values to HitData/protection/skill award sinks.",
        "status": "proposed",
        "evidence": ["EV-0599", "EV-0429", "EV-0294"],
    },
    {
        "id": "Q79-H103",
        "model": "The tag-0x0A call to FUN_1406be430 is a distinct Actor/process effect route without an armor-skill award, despite sharing code identity with the candidate hit/damage route.",
        "predicted_discriminant": "The captured caller arguments remain Actor/process scalar/vector state and the bounded helper descendants have no mapped HitData/protection/AV11/AV12/UseSkill target.",
        "status": "proposed",
        "evidence": ["EV-0599", "EV-0294"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0599 reveals a shared code-identity path: tag-0x0A Actor method FUN_140699500 conditionally calls FUN_1406be430, which also appears in the candidate hit/damage route EV-0429. The current call carries Actor/process-derived scalar/vector data and Actor+0x54; this does not prove HitData or armor-skill semantics. Trace the helper's callers/body and unresolved Actor slot +0x50 before closing caller 46."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6be430 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600; compare the FUN_140699500 call context with existing FUN_1406b9df0/HitData callers and screen all direct descendants against mapped protection/AV11/AV12/UseSkill targets. Then query Actor slot 0xA (+0x50) if needed, close caller 46 as bounded, and continue original caller 47/62 FUN_140658a30."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: caller 46's tag-0x0A Actor target has a process-conditioned direct call to shared candidate hit/damage helper FUN_1406be430. Direct data are Actor/process-derived; 45 indirect sites remain. Resolve the helper's callers and descendants before bounded closure, then continue caller 47/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "slot 0x10e (+0x870) resolves to Actor method FUN_140699500, whose direct-call census remains next.",
    "slot 0x10e (+0x870) resolves to Actor method FUN_140699500; its 195-call census includes a process-conditioned call to shared candidate helper FUN_1406be430, while 45 virtual sites remain.",
    1,
)
old_next = "**Selected next line:** enumerate direct callees of GOG Actor method `FUN_140699500` / RVA `0x699500` [EV-0598], screen mapped combat/skill sinks, then continue caller 47/62 `FUN_140658a30`. Keep transitive behavior and GOG/Steam boundaries open."
new_next = "**Selected next line:** trace caller context and descendants of `FUN_1406be430` shared by the tag-0x0A Actor callback and candidate hit route [EV-0599], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep 45 virtual sites and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0599/CL-L411/M-0151; supported H101, proposed H102/H103; checkpointed FUN_1406be430 route")
