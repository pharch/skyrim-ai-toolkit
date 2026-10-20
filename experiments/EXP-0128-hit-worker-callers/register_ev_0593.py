from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T180847Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x69e070":
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
    "id": "EV-0593",
    "source": "Identity-checked GOG tag-0x43 helper census and complete seven-producer comparison",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x69e070 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_14069e070 has eight unique direct targets (12 call instructions) and three unresolved indirect call sites. It compares the input dword to a three-bit selection at object offset +0xc8, updates bits 0x1c0000 on change, uses the +0xf8 component and other state/ref helpers, and ends through conditional FUN_1406bc0c0/FUN_1406bc100 transitions. Its dynamic sites include receiver +0x150/vtable +0x88 and two object +0x8 callbacks; types remain unknown. The direct callee set includes FUN_1406bc0c0 and FUN_1406bc100 but no mapped HitData, effective-protection, AV11/AV12, or UseSkill target. FUN_1406bc0c0's inspected body writes fields on a nested object; FUN_1406bc100 forwards to FUN_140717d10, which remains untraced. All seven tag-0x43 producers are decompiled: six use values 0,1,2,3,4,5 and the seventh uses value 6 after a separate action; for each tag-0x43 transition, gate-set calls FUN_1406589f0(object,value) and gate-clear calls FUN_14069e070(object,value). Worker case 0x43 also calls FUN_14069e070(object,payload_dword) [EV-0574].",
    "result": "The tag-0x43 family has queue/direct parity across all seven captured producers, not only the sampled first producer. The shared helper changes an encoded three-bit state field and runs process/component/reference updates; its three virtual calls and downstream FUN_140717d10 remain unresolved. The exact object/runtime type is unknown, and the helper's direct callee census contains no mapped HitData/effective-protection/AV11/AV12/UseSkill target. This falsifies a direct mapped combat-sink model for the exact function body, not all dynamic descendants or runtime outcomes. Q79-H91 is supported/H92 falsified; H89 is falsified/H90 supported within this scope. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0592", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0593" in existing and existing["EV-0593"] != item:
    raise SystemExit("EV-0593 collision")
if "EV-0593" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L405",
    "| CL-L405 | In GOG AE 1.6.1179.0, all seven tag-0x43 producers preserve the same object+dword across gate-set queueing and gate-clear direct calls to FUN_14069e070; that helper updates a three-bit field at object+0xc8 and has 3 unresolved indirect sites but no direct mapped HitData/effective-protection/AV11/AV12/UseSkill target. | supported for the captured producer/helper bodies | [EV-0593], [EV-0574] | Runtime object type, virtual consumers and FUN_140717d10 remain unresolved; no whole-path or Steam-runtime negative is claimed. |",
)

mechanism_path = ROOT / "research/MECHANISMS.md"
mechanisms = mechanism_path.read_text(encoding="utf-8")
old = "## M-0146 — Tag-0x43 object/dword queued update candidate (EV-0592)\n\n`FUN_1406589f0` serializes tag `0x43`, an object pointer and a dword, retaining the object through an increment at `+0x28` before sending it to the shared worker [EV-0592]. It has seven direct producers. The sampled producer `FUN_1407bacf0` sends `(object,1)` through the builder when the shared gate is set and calls `FUN_14069e070(object,1)` directly when clear; worker case `0x43` also calls `FUN_14069e070(object,dword)` [EV-0574], [EV-0592]. This supports queue/direct convergence for the sampled route only. The other producers and helper body remain to be traced. No HitData/protection/AV11/AV12/UseSkill or OBJ-1 edge is established by the builder. Claim CL-L404."
new = "## M-0146 — Tag-0x43 object/dword queued state update (EV-0592/0593)\n\n`FUN_1406589f0` serializes tag `0x43`, an object pointer and a dword, retaining the object through an increment at `+0x28` before sending it to the shared worker [EV-0592]. All seven direct producers are captured: their tag-0x43 branch preserves the same object and values 0–6 across gate-set queueing and gate-clear direct calls to `FUN_14069e070` [EV-0593]. The worker case also forwards its object/dword to that helper [EV-0574]. `FUN_14069e070` updates a three-bit field at object `+0xc8` and performs component/reference/state work; its direct callee census has no mapped HitData/effective-protection/AV11/AV12/UseSkill sink [EV-0593]. Three indirect callbacks, runtime type, and downstream `FUN_140717d10` remain unresolved; no whole-path/runtime negative or OBJ-1/OBJ-2 edge is claimed. Claims CL-L404/CL-L405."
if old not in mechanisms:
    raise SystemExit("M-0146 source text not found")
mechanism_path.write_text(mechanisms.replace(old, new, 1), encoding="utf-8")

append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 46/62: tag-0x43 complete producer and helper trace (EV-0593)",
    """### Caller 46/62: tag-0x43 complete producer and helper trace (EV-0593)

All seven producer bodies preserve object plus selector 0–6 across the gate-set worker path (`FUN_1406589f0`) and gate-clear direct path (`FUN_14069e070`); `FUN_1407baef0` also performs a separate earlier action [EV-0593]. The shared handler compares the selector to the three-bit value at object `+0xc8`, updates bitfield mask `0x1c0000`, and runs component/reference/state helpers. Its direct census has 12 call instructions, eight unique targets and three unresolved indirect sites. Direct helpers `FUN_1406bc0c0`/`FUN_1406bc100` are not the mapped HitData/AV11/AV12/UseSkill targets; `FUN_140717d10` and virtual consumers remain open [EV-0593]. H91 is supported/H92 falsified for all seven captured producer branches; H89 is falsified/H90 supported for the direct helper body only. No runtime object identity or full transitive negative is claimed.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 46 complete parity and direct-sink models",
    """## Caller 46 complete parity and direct-sink models

- Q79-H89: `FUN_14069e070` directly reaches a mapped HitData, effective-protection, AV11/AV12 or UseSkill target. Prediction: its complete direct call-edge census includes one of those targets.
- Q79-H90: the exact helper body changes an encoded state selector and performs component/reference updates; any combat relation would require an unresolved dynamic callback or descendant. Prediction: the direct body shows the state-field transition, while its direct callees lack mapped hit/armor-skill sinks.
- Q79-H91: all seven tag-0x43 producers preserve object and selector across gate-set queueing and gate-clear direct execution.
- Q79-H92: at least one producer changes target or payload between its immediate and queued branches.

EV-0593 falsifies H89 and supports H90 for the exact helper body; it supports H91 and falsifies H92 for all seven captured producers. Three virtual sites, FUN_140717d10, runtime object type and actual gameplay behavior remain open.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0593 completes tag-0x43 producer parity and helper census",
    "EV-0593 shows that all seven tag-0x43 producers preserve object+selector across queue/direct branches and converge on FUN_14069e070. The helper updates a three-bit object state and calls component/reference helpers, with three unresolved virtuals and no direct mapped HitData/protection/AV11/AV12/UseSkill edge. No causal edge to OBJ-1 or armor M-0009 is added [EV-0592], [EV-0593].",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0593"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L405"]))
for candidate in (
    {
        "id": "Q79-H89",
        "model": "The exact FUN_14069e070 helper body directly reaches a mapped HitData, effective-protection, AV11/AV12 or UseSkill target.",
        "predicted_discriminant": "A complete direct-call census identifies one of the mapped hit/armor-skill targets as a direct callee.",
        "status": "falsified",
        "evidence": ["EV-0593"],
    },
    {
        "id": "Q79-H90",
        "model": "The exact FUN_14069e070 body updates an encoded state selector and performs component/reference work; any combat relation would require an unresolved callback or descendant.",
        "predicted_discriminant": "The body updates the +0xc8 selector bitfield, while direct callees contain no mapped hit/armor-skill target and indirect callbacks remain unresolved.",
        "status": "supported",
        "evidence": ["EV-0593"],
    },
    {
        "id": "Q79-H91",
        "model": "All seven tag-0x43 producers preserve object and selector across gate-set queueing and gate-clear direct execution.",
        "predicted_discriminant": "Each producer's queued builder arguments match its direct helper arguments in object identity and selector value.",
        "status": "supported",
        "evidence": ["EV-0593", "EV-0574"],
    },
    {
        "id": "Q79-H92",
        "model": "At least one of the seven tag-0x43 producers changes helper target or payload between its immediate and queued branches.",
        "predicted_discriminant": "At least one captured producer has a different direct target or object/selector argument across gate branches.",
        "status": "falsified",
        "evidence": ["EV-0593", "EV-0574"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0593 completes all seven tag-0x43 producer bodies: each preserves object+selector across queue/direct routes. The helper updates a three-bit field and component/reference state; its direct call census has no mapped HitData/protection/AV11/AV12/UseSkill target, but three virtual callbacks and FUN_140717d10 remain unresolved. No whole-path/runtime negative or OBJ-1/OBJ-2 causal edge follows."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x717d10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; test the helper descendant reached from FUN_1406bc100 for direct HitData/protection/AV11/AV12/UseSkill sinks. If it remains generic state work, close caller 46 as a bounded negative and continue caller 47/62 FUN_140658a30."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 46/62 tag 0x43 has seven producer branches with exact queue/direct payload parity. FUN_14069e070 updates a three-bit selector/component state and has no direct mapped HitData/armor-skill sink; three virtual callbacks and FUN_140717d10 remain open. Test that direct descendant, then continue caller 47/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "46 of 62 initially uninspected worker callers are reviewed, with 16 remaining.",
    "46 of 62 initially uninspected worker callers are reviewed, with 16 remaining.",
    1,
)
state = state.replace("Q-0079 has 46/62 exact worker callers reviewed; 16 remain.", "Q-0079 has 46/62 exact worker callers reviewed; 16 remain.", 1)
state = state.replace(
    "EV-0592 maps caller 46/tag 0x43 as a retained object+dword event with seven producers; one sampled producer's immediate and worker routes converge on FUN_14069e070.",
    "EV-0592 maps caller 46/tag 0x43 as a retained object+dword event with seven producers; EV-0593 confirms all seven immediate/worker branches converge on FUN_14069e070 with matching values. The helper updates a three-bit state and has no direct mapped hit/armor-skill sink, though three virtual callbacks and FUN_140717d10 remain open.",
    1,
)
state = state.replace(
    "EV-0592 maps caller 46/tag 0x43 to a seven-producer object+dword update candidate.",
    "EV-0592 maps caller 46/tag 0x43 to a seven-producer object+dword update; EV-0593 resolves queue/direct parity and bounds the helper's direct edges.",
    1,
)
old_next = "**Selected next line:** inspect shared helper `FUN_14069e070` for tag-0x43 direct/indirect sinks and compare its direct/deferred producer routes [EV-0592]. Keep all seven source identities, event meaning, runtime type, and GOG/Steam boundaries open."
new_next = "**Selected next line:** inspect descendant `FUN_140717d10` reached through `FUN_1406bc100` [EV-0593]; if it remains state work, continue caller 47/62 `FUN_140658a30`. Keep virtual callback types, event meaning, runtime object type, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0593/CL-L405; updated M-0146; supported H90/H91, falsified H89/H92; checkpointed FUN_140717d10")
