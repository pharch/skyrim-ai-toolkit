from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
QUERY_SPECS = [
    ("gog-query-20261019T173944Z", "0x658890"),
    ("gog-query-20261019T174056Z", "0x658890"),
    ("gog-query-20261019T174341Z", "0x6c6ee0"),
]
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
metas = {}
local_hashes = {}
for stem, rva in QUERY_SPECS:
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != rva:
        raise SystemExit(f"query identity failed for {stem}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG binary identity failed for {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed for {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed for {stem}")
    metas[stem] = meta
    local_hashes[f".local/ghidra/{raw.name}"] = sha(raw)
    local_hashes[f".local/ghidra/{stderr.name}"] = sha(stderr)
    local_hashes[f".local/ghidra/{meta_path.name}"] = sha(meta_path)

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only queries, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0586",
    "source": "Identity-checked read-only GOG caller-43 builder, complete incoming producer census, and tag-0x3d target trace",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T174056Z.stdout.raw",
    "sha256": metas["gog-query-20261019T174056Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T174056Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x658890 --list-call-edges --timeout 600",
        "tools/ghidra_probe.py --rva 0x658890 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x6c6ee0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_140658890 builds tag 0x3d, retains its object argument at +0x28, copies an index and two byte flags, and calls FUN_14065b800; it has no indirect sites. Its five direct call xrefs come from four functions: FUN_1405b4900, FUN_1405b49a0, FUN_1405b4a00, and two sites in FUN_1406c9160. The producer bodies supply different index/flag combinations; FUN_1406c9160 also writes a property named iMagicEquipped and, on its non-player path, calls FUN_1406b98f0 followed by receiver slot +0x688. Existing worker evidence EV-0574 shows fallback case 0x3d calls FUN_1406c6ee0(object,index,flag1,flag2) and releases the retained reference. FUN_1406c6ee0 has six direct callees and two unresolved virtual sites at receiver slots +0x380 and +0x2e0; it uses those results to select indexed state and call update/cleanup helpers. No direct mapped HitData resolver, effective-armor function, AV11/AV12 award, or UseSkill target appears in this bounded case/helper path. The virtual targets, object RTTI, and runtime consequences remain unresolved.",
    "result": "Caller 43 is a tag-0x3d indexed state/equipment-related continuation, not a tag-0x0b builder. The exact producer contexts and worker case converge on FUN_1406c6ee0, whose bounded body routes through two virtual calls and state/update helpers. One source function directly references iMagicEquipped, but this does not establish armor behavior. H79 is supported for the bounded indexed state route; H80, which predicts a direct mapped hit/protection/ActorValue/UseSkill sink in this case/helper, is falsified. Q79-H1/H2 remain open because one non-tag-0x0b caller does not complete the remaining caller census. No OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0260", "EV-0585"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0586" in existing and existing["EV-0586"] != item:
    raise SystemExit("EV-0586 collision")
if "EV-0586" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L398",
    "| CL-L398 | In GOG AE 1.6.1179.0, caller 43 FUN_140658890 builds tag 0x3d and the fallback case routes its object/index/flags to FUN_1406c6ee0; that helper uses unresolved virtual slots +0x380/+0x2e0 and direct state/update helpers, with no direct mapped HitData, effective-armor, AV11/AV12 award, or UseSkill target in the bounded body. | supported for the exact builder/producers/case/helper path | [EV-0586], [EV-0574] | Object RTTI, virtual targets, descendants, and runtime gameplay effects remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0141 — Tag-0x3d indexed state continuation (EV-0574/0586)",
    """## M-0141 — Tag-0x3d indexed state continuation (EV-0574/0586)

`FUN_140658890` serializes tag `0x3d`, a retained object, an index and two byte flags, then submits the payload to `FUN_14065b800` [EV-0586]. Four producer functions supply distinct flag/index combinations; the `FUN_1406c9160` context also writes the string property `iMagicEquipped` and conditionally invokes an object getter and receiver slot `+0x688` [EV-0586]. Worker fallback case `0x3d` calls `FUN_1406c6ee0` with the object/index/flags [EV-0574]. That helper uses unresolved receiver slots `+0x380` and `+0x2e0` to gate and select indexed state, then calls state/update/cleanup helpers. The exact object RTTI and dynamic targets remain unknown. No direct mapped HitData, effective-armor, AV11/AV12, UseSkill, or quest-initiation edge is established; no objective causal edge is added. Claim CL-L398.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 43/62: FUN_140658890 tag-0x3d indexed state route (EV-0586)",
    """### Caller 43/62: FUN_140658890 tag-0x3d indexed state route (EV-0586)

`FUN_140658890` stores tag `0x3d`, retains its object argument, copies the index and two byte flags, and submits the payload to `FUN_14065b800` [EV-0586]. Five xrefs across four producer functions supply different combinations. The fallback case `0x3d` calls `FUN_1406c6ee0(object,index,flag1,flag2)` and releases the retained reference [EV-0574]. `FUN_1406c6ee0` has six direct callees plus unresolved receiver slots `+0x380` and `+0x2e0`; it gates and selects indexed object state before invoking cleanup/update helpers [EV-0586]. One producer references `iMagicEquipped` and conditionally calls receiver slot `+0x688`, but its dynamic type and gameplay meaning are not established. H79 supports the bounded state route; H80's direct mapped hit/protection/ActorValue/UseSkill sink prediction is falsified for this exact helper. This is not a tag-0x0b producer, and Q79-H1/H2 remain open with 19 callers left. No OBJ-2 causal edge is added. Next inspect caller 44/62 `FUN_1406588e0`.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 43 competing models",
    """## Caller 43 competing models

- Q79-H79: tag 0x3d is an indexed object-state/equipment-related continuation whose bounded worker case reaches FUN_1406c6ee0 and state/update helpers. Prediction: producer index/flags and helper calls select state; no direct mapped HitData, protection, AV11/AV12, or UseSkill sink is required.
- Q79-H80: tag 0x3d directly routes to a mapped HitData/protection/ActorValue/UseSkill sink. Prediction: the exact fallback case or FUN_1406c6ee0 direct callee list contains one of those mapped sinks.

EV-0586 supports H79 and falsifies H80 for the exact direct case/helper body; virtual slots +0x380/+0x2e0 and producer descendants remain open. The `iMagicEquipped` property reference does not establish functional armor behavior.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0586 caller-43 result and frontier",
    "EV-0586 resolves caller 43 as tag 0x3d and its fallback target as an indexed state/update helper with unresolved virtuals; no direct mapped hit/armor-skill sink appears. Resume the original census at caller 44/62 FUN_1406588e0 to test Q79-H1/H2/H3 and preserve the clean Steam matched-hit/protection/raw-AVSK discriminator.",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 43 equipment-state cue is not armor evidence",
    """Caller 43 equipment-state cue is not armor evidence

The tag-0x3d route is an indexed object-state continuation; one producer writes a property string `iMagicEquipped`, while the exact owner type and receiver slots remain unknown [EV-0586]. That makes equipment-related state a grounded description for the producer context, but it does not demonstrate armor rating, effective protection, or armor-skill awards. Keep this separate from the P0-B causal model until a producer-backed mapped protection/AVSK edge or matched-hit observation appears [EV-0586], [EV-0260].""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0586 adds tag-0x3d indexed state routing",
    "EV-0586 adds a second bounded Actor-state family to the worker census: tag 0x3d routes an indexed object and flags to FUN_1406c6ee0, which selects state through unresolved virtual slots and invokes update/cleanup helpers. One producer references `iMagicEquipped`, but this does not establish armor or skill effects. No HitData/protection/AV/UseSkill/OBJ-1 causal edge is added [EV-0574], [EV-0586].",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 43 tag-0x3d indexed state route (EV-0586)",
    """## Q-0079 update — caller 43 tag-0x3d indexed state route (EV-0586)

Caller 43 builds tag `0x3d`; four producer functions provide different indices/flags and the fallback case calls `FUN_1406c6ee0` [EV-0574], [EV-0586]. The helper uses two unresolved virtual slots to select indexed state and calls update/cleanup helpers. One producer references `iMagicEquipped`, but no direct mapped HitData/protection/AV/UseSkill path is established. Nineteen of the original 62 callers remain; resume at `FUN_1406588e0` [CL-L398], [M-0141].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0586"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L398"]))
h79 = {
    "id": "Q79-H79",
    "model": "Tag 0x3d is an indexed object-state/equipment-related continuation whose bounded worker case reaches FUN_1406c6ee0 and state/update helpers.",
    "predicted_discriminant": "Producer index/flags and helper calls select object state; exact direct case/helper bodies contain no mapped HitData, protection, AV11/AV12, or UseSkill sink.",
    "status": "supported",
    "evidence": ["EV-0586", "EV-0574"],
}
h80 = {
    "id": "Q79-H80",
    "model": "Tag 0x3d directly routes through its fallback case or FUN_1406c6ee0 to a mapped HitData/protection/ActorValue/UseSkill sink.",
    "predicted_discriminant": "The exact case or complete direct body of FUN_1406c6ee0 contains a call to a mapped HitData resolver, effective-armor function, AV11/AV12 award, or UseSkill target.",
    "status": "falsified",
    "evidence": ["EV-0586", "EV-0574"],
}
hypotheses = q79["hypotheses"]
for candidate in (h79, h80):
    found = next((h for h in hypotheses if h.get("id") == candidate["id"]), None)
    if found is None:
        hypotheses.append(candidate)
    elif found != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0586 adds caller 43's tag-0x3d indexed object-state/equipment-related route. The exact helper body uses unresolved virtual selectors and state/update callees, with no direct mapped HitData, protection, AV11/AV12 or UseSkill sink; `iMagicEquipped` is only a property-name cue, not armor evidence. The original tag-0x0b census remains open with 19 callers to review."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6588e0 --list-call-edges --timeout 600; inspect worker caller 44/62 FUN_1406588e0 for payload/tag, producer provenance, dispatcher route, and any direct mapped HitData/AV11/AV12/UseSkill edge. Compare against Q79-H1/H2/H3, preserve tag/source uncertainty and the unavailable clean Steam matched-hit/protection/raw-AVSK discriminator, then continue caller 45/62."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 43/62 is a tag-0x3d indexed object-state route into FUN_1406c6ee0, with two unresolved virtual selectors and direct state/update helpers. No mapped HitData/protection/AV11/AV12/UseSkill edge is established. Nineteen original callers remain; caller 44 is next.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace("42 of 62 initially uninspected worker callers are reviewed, with 20 remaining.", "43 of 62 initially uninspected worker callers are reviewed, with 19 remaining.", 1)
state = state.replace(
    "EV-0583–EV-0585 map caller 42 as Actor.DispelSpell/tag 0x5e to a SpellItem-matched Actor+0xa0 record, bit-18 state transition, and shared timing/status handler; exact RTTI and terminal effect remain unresolved. No direct HitData/AV/armor-skill edge or armor-XP bypass is established; Q79-H3 and clean Steam protection/raw-AVSK remain open.",
    "EV-0583–EV-0585 map caller 42 as Actor.DispelSpell/tag 0x5e to a SpellItem-matched Actor+0xa0 record, bit-18 state transition, and shared timing/status handler; exact RTTI and terminal effect remain unresolved. EV-0586 maps caller 43/tag 0x3d to indexed object-state updates with unresolved virtual selectors and no direct mapped hit/armor-skill sink. No armor-XP bypass is established; Q79-H1/H2/H3 and clean Steam protection/raw-AVSK remain open.",
    1,
)
state = state.replace("Q-0079 has 42/62 exact worker callers reviewed; 20 remain.", "Q-0079 has 43/62 exact worker callers reviewed; 19 remain.", 1)
state = state.replace(
    "EV-0583–EV-0585 map Actor.DispelSpell into a SpellItem-matched Actor+0xa0 record and shared bit-18 state handler.",
    "EV-0583–EV-0585 map Actor.DispelSpell into a SpellItem-matched Actor+0xa0 record and shared bit-18 state handler; EV-0586 maps tag 0x3d into indexed object-state updates with unresolved virtual selectors.",
    1,
)
old_next = "**Selected next line:** resume caller 43/62 `FUN_140658890` and classify its producer payload, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0585]. Keep the exact Actor.DispelSpell record class and handler terminal effect unresolved; caller 42 provides no direct armor/XP edge."
new_next = "**Selected next line:** inspect caller 44/62 `FUN_1406588e0` for its producer payload, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0586]. Keep caller 43's dynamic object type and virtual selectors unresolved; no armor causal edge is established."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0586/CL-L398/M-0141; supported Q79-H79, falsified bounded H80, checkpointed caller 44/62")
