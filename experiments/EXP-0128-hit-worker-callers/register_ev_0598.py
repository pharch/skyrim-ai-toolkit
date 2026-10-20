from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T182252Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x189ec20" or str(meta.get("requested_vtable_slot", "")).lower() != "0x10e":
    raise SystemExit("query identity/slot failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
stdout = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "VTABLE_SLOT_INDEX=0x10E",
    "VTABLE_SLOT_TARGET_RVA=0x699500",
    "VTABLE_RTTI_TYPE_NAME=.?AVActor@@",
):
    if token not in stdout:
        raise SystemExit(f"required Ghidra result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0598",
    "source": "Identity-checked GOG primary Actor vtable slot 0x10e query",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x189EC20 --vtable-slot 0x10e --timeout 600"],
    "coverage": "The GOG Actor vtable at RVA 0x189EC20 has RTTI .?AVActor@@ with subobject offset zero; slot index 0x10e (byte offset +0x870) targets FUN_140699500 at RVA 0x699500. One analyzed direct caller of the target is FUN_14074d8d0. The decompiled method accepts Actor-like receiver, a pointer-like second argument, an 8-byte value and two bytes; it gates on process/state and virtual slots +0x4c8/+0x2f0, clears state bits, and performs broad Actor/process update/cleanup work. This query did not request a complete direct-call edge census, so direct/transitive combat/skill sink coverage is not yet classified.",
    "result": "The tag-0x0A dispatcher's slot +0x870 is concretely primary Actor method FUN_140699500 in this GOG build. The method body appears to perform Actor/process state and cleanup work, but its full direct-call census and mapped combat/skill sink screen remain pending. Exact Actor RTTI is proven for the table, not runtime instance behavior; no OBJ-1/OBJ-2 edge is added.",
    "local_hashes": {f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)},
    "related_evidence": ["EV-0597", "EV-0596", "EV-0595", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0598" in existing and existing["EV-0598"] != item:
    raise SystemExit("EV-0598 collision")
if "EV-0598" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L410",
    "| CL-L410 | In GOG AE 1.6.1179.0, primary VTABLE::Actor slot 0x10e (+0x870) resolves to FUN_140699500 at RVA 0x699500. | supported for the exact GOG vtable slot | [EV-0598] | Full direct-call census, runtime instance behavior, downstream combat/skill effects, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0150 — Tag-0x0A callback resolves to primary Actor method FUN_140699500 (EV-0598)",
    """## M-0150 — Tag-0x0A callback resolves to primary Actor method FUN_140699500 (EV-0598)

Matching GOG `VTABLE::Actor` slot `0x10e` (`+0x870`) resolves to `FUN_140699500` at RVA `0x699500` under primary Actor RTTI [EV-0597], [EV-0598]. The method body includes Actor/process state and cleanup operations; a complete direct-call census and mapped combat/skill screen remain pending. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L410.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Tag-0x0A Actor callback target (EV-0598)",
    """### Tag-0x0A Actor callback target (EV-0598)

Primary GOG `VTABLE::Actor` slot `0x10e` (`+0x870`) maps to `FUN_140699500` / RVA `0x699500` under RTTI `.?AVActor@@` [EV-0598]. Its body has Actor/process state and cleanup work, but the slot query did not request a complete call-edge census. Next enumerate its direct callees and screen mapped HitData/protection/AV11/AV12/UseSkill sinks before continuing caller 47/62.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0598 resolves the tag-0x0A dynamic callback to an Actor method",
    "EV-0598 resolves primary Actor slot 0x10e (+0x870) to FUN_140699500 in GOG AE 1.6.1179.0. Its broad Actor/process cleanup body still needs a complete direct-call screen; no OBJ-1/OBJ-2 causal edge is yet supported.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0598"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L410"]))
candidate = {
    "id": "Q79-H100",
    "model": "Primary GOG Actor vtable slot 0x10e (+0x870) resolves to FUN_140699500 under .?AVActor@@ RTTI.",
    "predicted_discriminant": "An identity-checked vtable query returns FUN_140699500 at RVA 0x699500 and primary Actor RTTI; a separate direct-call census is still required for downstream behavior.",
    "status": "supported",
    "evidence": ["EV-0597", "EV-0598"],
}
hypotheses = q79["hypotheses"]
prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
if prior is None:
    hypotheses.append(candidate)
elif prior != candidate:
    raise SystemExit("hypothesis collision: Q79-H100")
assessment = "EV-0598 resolves the tag-0x0A dynamic callback to primary Actor method FUN_140699500 at GOG RVA 0x699500. Its Actor/process state cleanup body is captured, but a full direct-call census has not yet been run; do not infer absence of transitive hit/XP effects."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x699500 --list-call-edges --follow-direct-calls 8 --timeout 600; classify all direct edges and screen targets against mapped HitData/protection/AV11/AV12/UseSkill functions. Then continue original worker caller 47/62 FUN_140658a30 regardless of local resolution."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: tag-0x0A dispatcher slot +0x870 resolves to primary Actor method FUN_140699500. Its body performs Actor/process state cleanup; direct call census is next, with fifteen original callers still pending after caller 46 closes.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "matching GOG VTABLE::Actor is at RVA 0x189EC20, and slot 0x10e (+0x870) is next.",
    "matching GOG VTABLE::Actor is at RVA 0x189EC20; slot 0x10e (+0x870) resolves to Actor method FUN_140699500, whose direct-call census remains next.",
    1,
)
old_next = "**Selected next line:** query GOG vtable RVA `0x189EC20`, slot `0x10e` (+`0x870`) [EV-0597], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, exact runtime type, event meaning, and GOG/Steam boundaries open."
new_next = "**Selected next line:** enumerate direct callees of GOG Actor method `FUN_140699500` / RVA `0x699500` [EV-0598], screen mapped combat/skill sinks, then continue caller 47/62 `FUN_140658a30`. Keep transitive behavior and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0598/CL-L410/M-0150; supported H100; checkpointed FUN_140699500 direct-call census")
