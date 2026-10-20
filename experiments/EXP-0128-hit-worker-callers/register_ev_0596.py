from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T181830Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x657870":
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
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0596",
    "source": "Identity-checked GOG incoming-caller trace for tag-0x0A builder FUN_140657870",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x657870 --list-call-edges --follow-incoming-calls 8 --timeout 600"],
    "coverage": "The complete direct caller set has three functions: FUN_1406671b0, FUN_1406694e0, and FUN_140665950. FUN_1406671b0 forwards its param_1 object with caller-supplied scalar/byte fields. FUN_1406694e0 includes a branch that passes its param_1 object to the builder. FUN_140665950 checks object/process state, invokes virtual slot +0x4c8 on param_1 (byte offset /8 = slot 0x99), calls FUN_1406b8b60, checks param_1+0xf8 and FUN_140717610, writes param_1+0x108 on one branch, and passes that same param_1 to the builder. Existing EV-0291 maps primary VTABLE::Actor slot 0x99 (+0x4c8) to FUN_140677100. This makes the object Actor-vtable-compatible in the captured FUN_140665950 route, but does not prove exact RTTI for all callers. The tag-0x0A dispatcher recipient slot +0x870 (index 0x10e) is still unresolved; no skill/protection conclusion follows.",
    "result": "Two captured update callers pass their param_1 object into the tag-0x0A builder; one invokes the same +0x4c8 offset mapped to primary Actor slot 0x99 by EV-0291. This supports an Actor-vtable-compatible object for that route, not exact RTTI for every producer and not the meaning of dispatcher slot +0x870. The unresolved virtual target remains a possible transitive gameplay path; no OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0595", "EV-0594", "EV-0291"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0596" in existing and existing["EV-0596"] != item:
    raise SystemExit("EV-0596 collision")
if "EV-0596" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L408",
    "| CL-L408 | In the captured GOG tag-0x0A producer set, FUN_140665950 passes its param_1 object to the builder after invoking virtual byte offset +0x4c8, which existing evidence maps to primary VTABLE::Actor slot 0x99; this supports Actor-vtable compatibility for that route. | supported for the exact caller path | [EV-0596], [EV-0291] | Exact RTTI for all three callers and dispatcher slot +0x870's target/behavior remain unknown. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0149 — Tag-0x0A event has an Actor-vtable-compatible producer route (EV-0596)",
    """## M-0149 — Tag-0x0A event has an Actor-vtable-compatible producer route (EV-0596)

Of the three direct callers to `FUN_140657870`, `FUN_140665950` passes its object `param_1` after invoking virtual byte offset `+0x4c8`, which matches primary `VTABLE::Actor` slot `0x99` and target `FUN_140677100` [EV-0596], [EV-0291]. This supports Actor-vtable compatibility for that producer route; exact RTTI for all callers is not proven. Dispatcher slot `+0x870` remains unresolved. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L408.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Tag-0x0A caller-type discriminator (EV-0596)",
    """### Tag-0x0A caller-type discriminator (EV-0596)

The builder has three direct callers. `FUN_140665950` invokes virtual byte offset `+0x4c8` on `param_1` and then passes that same object to the builder; EV-0291 maps that byte offset to primary `VTABLE::Actor` slot `0x99` [EV-0596], [EV-0291]. This supports Actor-vtable compatibility for that exact route, but not exact RTTI for all callers. Resolve the Actor vtable slot `0x10e` corresponding to dispatcher byte offset `+0x870`; then continue caller 47/62.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0596 links one tag-0x0A producer to an Actor-compatible vtable slot",
    "EV-0596 shows FUN_140665950 passes the same object to the tag-0x0A builder after invoking byte offset +0x4c8, which EV-0291 maps to primary Actor slot 0x99. This supports Actor-vtable compatibility for that producer route; dispatcher byte offset +0x870 remains unresolved. No OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0596"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L408"]))
for candidate in (
    {
        "id": "Q79-H98",
        "model": "The tag-0x0A object passed by FUN_140665950 is Actor-vtable-compatible: the same param_1 object receives virtual byte offset +0x4c8 before being submitted to the builder.",
        "predicted_discriminant": "Existing primary VTABLE::Actor slot 0x99 resolves to the same +0x4c8 method invoked on param_1; this supports compatibility for this caller but not exact RTTI for all sources.",
        "status": "supported",
        "evidence": ["EV-0596", "EV-0291"],
    },
    {
        "id": "Q79-H99",
        "model": "The sampled FUN_140665950 tag-0x0A route passes an object unrelated to the Actor vtable family.",
        "predicted_discriminant": "The same submitted param_1 would not use the primary Actor-mapped +0x4c8 slot.",
        "status": "falsified",
        "evidence": ["EV-0596", "EV-0291"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")

assessment = "EV-0596 adds producer-side type evidence: FUN_140665950 passes its object after invoking byte offset +0x4c8, mapped to primary Actor slot 0x99 by EV-0291. This supports Actor-vtable compatibility for that route only. The tag-0x0A dispatcher recipient slot +0x870 remains unresolved, so no transitive combat/XP conclusion follows."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Resolve primary GOG VTABLE::Actor slot 0x10e (byte offset +0x870) and inspect the target/callees against mapped HitData/protection/AV11/AV12/UseSkill functions. Then continue original worker caller 47/62 FUN_140658a30 regardless of local resolution."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 continues caller 46/62: the secondary tag-0x0A event has an Actor-vtable-compatible producer route under EV-0596, but recipient slot +0x870 remains unresolved. Resolve Actor vtable slot 0x10e against mapped combat/skill functions; sixteen original callers remain.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0594/0595 map FUN_140717d10 to a secondary tag-0x0A handle/vector worker update; its fallback calls unresolved recipient vtable slot +0x870, so receiver type and transitive effects remain open.",
    "EV-0594–0596 map FUN_140717d10 to a secondary tag-0x0A handle/vector worker update. One producer is Actor-vtable-compatible through +0x4c8/slot 0x99, but dispatcher slot +0x870 and transitive effects remain open.",
    1,
)
old_next = "**Selected next line:** query the three direct callers of `FUN_140657870` and resolve the recipient type/vtable slot `+0x870` [EV-0595], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, event meaning, runtime object type, and GOG/Steam boundaries open."
new_next = "**Selected next line:** resolve primary GOG `VTABLE::Actor` slot `0x10e` (byte offset `+0x870`) [EV-0596], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, exact runtime type, event meaning, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0596/CL-L408/M-0149; supported H98, falsified H99; checkpointed Actor slot 0x10e")
