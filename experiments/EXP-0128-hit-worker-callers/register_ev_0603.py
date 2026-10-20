from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
CAPTURES = {
    "gog-query-20261019T183544Z": "0x658a30",
    "gog-query-20261019T113125Z": "0xe89260",
}
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
hashes: dict[str, str] = {}
metas: dict[str, dict] = {}
outputs: dict[str, str] = {}
for stem, rva in CAPTURES.items():
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != rva:
        raise SystemExit(f"query identity failed: {stem}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed: {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed: {stem}")
    hashes.update({f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)})
    metas[stem] = meta
    outputs[stem] = raw.read_text(encoding="utf-8", errors="replace")

for token in ("local_88[0] = 0x44;", "FUN_1401fa010", "FUN_1406d4110", "FUN_1401fdb80"):
    if token not in outputs["gog-query-20261019T183544Z"]:
        raise SystemExit(f"producer result missing: {token}")
for token in ("case 0x44:", "FUN_1401fa010(DAT_1420fd578,param_1[2],*(undefined1 *)(param_1 + 4))"):
    if token not in outputs["gog-query-20261019T113125Z"]:
        raise SystemExit(f"dispatcher result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0603",
    "source": "Identity-checked GOG caller-47 tag-0x44 builder/producer with existing worker dispatcher case 0x44",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T183544Z.stdout.raw",
    "sha256": metas["gog-query-20261019T183544Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T183544Z"]["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658a30 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "existing identity-checked dispatcher capture at 0xE89260"],
    "coverage": "Exact caller 47 builder FUN_140658a30 has one direct call to FUN_14065b800, no indirect sites, and one direct producer FUN_1401fa010. The builder writes tag 0x44, stores param_2 as a dword and param_3 as a byte, then queues it. Producer FUN_1401fa010 queues tag 0x44 when FUN_1406d4110 is nonzero and returns; when the gate is clear it selects FUN_1404a27f0 or FUN_1404a28a0 based on param_3, and if the resulting object has field +0x170 nonzero it calls FUN_1401fdb80(object+0x170,object), releases its reference and returns success. Existing dispatcher case 0x44 routes back to FUN_1401fa010 with the payload dword/byte. No direct HitData/AV11/AV12/UseSkill target appears in the captured producer; object type and FUN_1401fdb80 behavior remain unresolved.",
    "result": "Caller 47 is a tag-0x44 deferred/immediate producer family: the gate-set event re-enters the same producer through dispatcher case 0x44, while the clear-gate path can call object helper FUN_1401fdb80 after conditional object acquisition. This does not construct tag 0x0B or establish a HitData/armor-skill edge. Trace FUN_1401fdb80 and its owner/descendants, then continue caller 48/62. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": hashes,
    "related_evidence": ["EV-0602", "EV-0397", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0603" in existing and existing["EV-0603"] != item:
    raise SystemExit("EV-0603 collision")
if "EV-0603" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L415",
    "| CL-L415 | In GOG AE 1.6.1179.0, caller 47 FUN_140658a30 emits tag 0x44 with a dword/byte payload; producer FUN_1401fa010 either queues it under FUN_1406d4110 or conditionally calls FUN_1401fdb80 on an acquired object's +0x170 member, and dispatcher case 0x44 re-enters FUN_1401fa010. | supported for the captured static route | [EV-0603] | Object type, FUN_1401fdb80 behavior, transitive effects, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0155 — Tag-0x44 worker event re-enters a gated object producer (EV-0603)",
    """## M-0155 — Tag-0x44 worker event re-enters a gated object producer (EV-0603)

`FUN_140658a30` builds tag `0x44` from a dword and byte. Producer `FUN_1401fa010` queues the same data under `FUN_1406d4110`; the worker's case `0x44` calls that producer again. The clear-gate route conditionally calls `FUN_1401fdb80` on an acquired object's `+0x170` member [EV-0603]. The object type and helper behavior remain open. No OBJ-1/OBJ-2 edge is established. Claim CL-L415.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 47/62: tag-0x44 gated producer and self-reentry (EV-0603)",
    """### Caller 47/62: tag-0x44 gated producer and self-reentry (EV-0603)

`FUN_140658a30` writes tag `0x44`, a dword and a byte. Its sole producer `FUN_1401fa010` queues this payload under `FUN_1406d4110`; dispatcher case `0x44` re-enters the same producer. On the clear-gate path, the producer may acquire an object and call `FUN_1401fdb80` on its `+0x170` member [EV-0603]. No tag `0x0B` or direct mapped HitData/AV11/AV12/UseSkill edge appears. Identify the object helper, then continue caller 48/62.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0603 maps caller 47 tag-0x44 queue/direct split",
    "EV-0603 shows caller 47's tag-0x44 deferred event re-enters FUN_1401fa010, while its gate-clear path may call FUN_1401fdb80 on an acquired object's +0x170 member. No HitData/armor-skill or OBJ-1/OBJ-2 edge is established; the recipient/helper remain unresolved.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0603"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L415"]))
for candidate in (
    {
        "id": "Q79-H107",
        "model": "Caller 47 builds tag 0x44 and the dispatcher routes it back into producer FUN_1401fa010; the clear-gate path selects a separate acquired-object helper.",
        "predicted_discriminant": "The builder writes tag 0x44, its sole producer selects queued/direct branches through FUN_1406d4110, and dispatcher case 0x44 re-enters the producer.",
        "status": "supported",
        "evidence": ["EV-0603"],
    },
    {
        "id": "Q79-H108",
        "model": "Caller 47 directly constructs tag 0x0B or calls the mapped HitData/AV11/AV12 resolver.",
        "predicted_discriminant": "The builder tag or producer body selects tag 0x0B / a mapped HitData or skill-award target.",
        "status": "falsified",
        "evidence": ["EV-0603"],
    },
    {
        "id": "Q79-H109",
        "model": "The clear-gate object helper FUN_1401fdb80 carries combat/protection/AV11/AV12/UseSkill effects.",
        "predicted_discriminant": "The helper or producer-backed direct descendants resolve to mapped HitData, effective protection, or armor-skill sinks.",
        "status": "proposed",
        "evidence": ["EV-0603"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0603 begins caller 47/62: tag 0x44 is a gated producer self-reentry with a distinct clear-gate object-helper route. It is not a tag-0x0B constructor and supplies no direct mapped hit/armor-skill edge. Trace FUN_1401fdb80 before moving to caller 48."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1fdb80 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600; trace the tag-0x44 clear-gate object's +0x170 helper receiver and screen direct descendants for mapped HitData/protection/AV11/AV12/UseSkill sinks. Then continue original worker caller 48/62 FUN_140658a80."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: caller 47/62 builds tag 0x44. Its deferred route self-reenters the producer; its immediate route may call FUN_1401fdb80 on an acquired object's +0x170 member. No direct HitData/armor-skill edge; resolve the helper before caller 48/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "caller 47/62 `FUN_140658a30` is next.",
    "caller 47/62 `FUN_140658a30` is now mapped as tag 0x44; its immediate object helper `FUN_1401fdb80` is next.",
    1,
)
old_next = "**Selected next line:** continue the 62-caller census at caller 47/62 `FUN_140658a30`; test its tag and payload against the tag-0x0B HitData/AV11/AV12 route. Caller 46 is bounded by EV-0602; keep its indirect sites and GOG/Steam boundaries open."
new_next = "**Selected next line:** trace clear-gate helper `FUN_1401fdb80` from caller 47's tag-0x44 producer [EV-0603], then continue caller 48/62 `FUN_140658a80`. Caller 46 is bounded by EV-0602; keep its indirect sites and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0603/CL-L415/M-0155; supported H107, falsified H108, proposed H109; checkpointed FUN_1401fdb80")
