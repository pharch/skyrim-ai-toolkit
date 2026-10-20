from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T183329Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x606580":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
stdout = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=3",
    "INDIRECT_CALL_SITE_COUNT=1",
    "INCOMING_CALLER_FUNCTION_COUNT=2",
    "FUN_140602e40",
    "local_48 = CONCAT44(local_48._4_4_,uVar5 | param_3)",
):
    if token not in stdout:
        raise SystemExit(f"required manager result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0602",
    "source": "Identity-checked GOG direct-call trace of Actor slot +0x50 manager helper FUN_140606580",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x606580 --list-call-edges --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_140606580 has three direct callees, one unresolved Actor virtual site at receiver slot +0x160, and two direct callers (FUN_1401dfdc0 and FUN_1401dfdf0). It gates on TLS byte +0x670, manager field +0x340, Actor flags at +0x10, nonzero Actor field +0x14, selector flags, and optionally the Actor slot +0x160/process helper. The accepted branch calls FUN_140602e40(manager+0x330, Actor+0x14, selector). FUN_140602e40 takes a lock, hashes/looks up the integer key in a linked bucket, ORs the selector into a stored value, and calls generic update helper FUN_140603310. The bounded direct target/helper bodies contain no mapped HitData/protection/AV11/AV12/UseSkill function. Exact manager owner type, Actor slot +0x160, generic update descendants, runtime use and Steam equivalence remain unresolved.",
    "result": "The Actor slot +0x50 continuation is a gated keyed-state update: it checks thread/global/Actor predicates and forwards Actor+0x14 plus selector to a manager-owned map, where the selector is ORed into keyed state. This bounds caller 46's tag-0x0A path as Actor/process vector plus state work, with one other unresolved virtual site and generic update descendants. No direct armor/protection/skill sink or OBJ-1/OBJ-2 causal edge appears. Close caller 46 as a bounded negative for direct P0 sinks and proceed to original caller 47/62 FUN_140658a30.",
    "local_hashes": {f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)},
    "related_evidence": ["EV-0601", "EV-0600", "EV-0599", "EV-0595", "EV-0397"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0602" in existing and existing["EV-0602"] != item:
    raise SystemExit("EV-0602 collision")
if "EV-0602" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L414",
    "| CL-L414 | In GOG AE 1.6.1179.0, tag-0x0A Actor slot +0x50 delegates through FUN_140606580 to FUN_140602e40, which hashes/looks up Actor+0x14 and ORs a selector into manager-owned keyed state after thread/global/Actor gates. | supported for the bounded static update path | [EV-0602] | Exact manager type, one unresolved Actor slot +0x160, generic update descendants, runtime use, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0154 — Tag-0x0A follow-up updates selector bits in a gated manager map (EV-0602)",
    """## M-0154 — Tag-0x0A follow-up updates selector bits in a gated manager map (EV-0602)

Actor slot `+0x50` reaches `FUN_140606580`, which checks TLS/global/Actor flags and conditionally calls `FUN_140602e40(manager+0x330, Actor+0x14, selector)`. The helper hashes and looks up the integer key, ORs the selector into stored state, and calls generic update helper `FUN_140603310` [EV-0602]. One Actor virtual slot `+0x160` and generic update behavior remain unresolved. No direct OBJ-1/OBJ-2 sink or causal edge is established. Claim CL-L414.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 46/62 bounded closure: tag-0x0A vector and keyed-state path (EV-0602)",
    """### Caller 46/62 bounded closure: tag-0x0A vector and keyed-state path (EV-0602)

The secondary tag-0x0A path reaches primary Actor slot `+0x870` (`FUN_140699500`), which has a process-conditioned vector helper branch (`FUN_1406be430`) and then Actor slot `+0x50` (`FUN_1401dfdc0`). The manager continuation checks TLS/global/Actor flags and updates a manager-owned keyed record with `Actor+0x14` and a selector bit [EV-0595]–[EV-0602]. The shared vector helper reads numeric ActorValue `0x24` and reaches a vector/physics-like sink, but the tag-0x0A caller's inputs differ from the HitData-shaped caller, and no direct AV11/AV12/UseSkill or mapped protection sink appears. This closes caller 46 only as a bounded static Actor/process vector/state route; one Actor slot `+0x160`, generic update descendants, the 45 other vtable sites on FUN_140699500, runtime effects, and GOG/Steam equivalence remain unresolved. Continue caller 47/62 `FUN_140658a30`. No OBJ-1/OBJ-2 causal edge is added.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0602 bounds the tag-0x0A manager continuation as keyed Actor state",
    "EV-0602 extends the tag-0x0A Actor route from its vector helper through Actor slot +0x50 into a gated manager-owned map keyed by Actor+0x14, where a selector is ORed into stored state. This bounds caller 46's direct path without linking it to HitData/protection/AV11/AV12/UseSkill or OBJ-1/OBJ-2.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0602"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L414"]))
for candidate in (
    {
        "id": "Q79-H105",
        "model": "The tag-0x0A follow-up manager call FUN_140606580 reaches HitData/protection/AV11/AV12/UseSkill behavior.",
        "predicted_discriminant": "The bounded manager target or its direct callees resolve to combat/protection/skill award sinks; the captured path instead checks flags and updates keyed state through FUN_140602e40.",
        "status": "falsified",
        "evidence": ["EV-0602"],
    },
    {
        "id": "Q79-H106",
        "model": "The bounded tag-0x0A Actor slot +0x50 continuation conditionally ORs a selector into manager-owned keyed Actor state.",
        "predicted_discriminant": "FUN_140606580 passes Actor+0x14 and selector to a gated hash-map update where the selector is ORed into a stored value.",
        "status": "supported",
        "evidence": ["EV-0602"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    else:
        prior.update(candidate)
assessment = "EV-0602 bounds caller 46's secondary tag-0x0A continuation as a gated manager-map update keyed by Actor+0x14, after the process-conditioned vector helper. No direct HitData/protection/AV11/AV12/UseSkill sink appears in this local route; unresolved virtual sites and runtime effects remain open. Caller 46 is now bounded; resume at caller 47/62."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658a30 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; identify caller 47's worker tag/payload and screen its producer/dispatcher path against tag 0x0B, mapped HitData/protection and AV11/AV12/UseSkill functions."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: caller 46/62 closed as a bounded tag-0x0A Actor/process vector and keyed-state update. One Actor slot +0x160, generic update descendants, and 45 other Actor-method virtuals remain unresolved but no direct P0 sink was found. Fifteen original callers remain; next is caller 47/62 FUN_140658a30.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "trace that manager target, then close caller 46 and continue caller 47/62 `FUN_140658a30`.",
    "EV-0602 bounds that continuation as a gated keyed Actor-state update; caller 46 is now closed and caller 47/62 `FUN_140658a30` is next.",
    1,
)
old_next = "**Selected next line:** inspect `FUN_140606580` reached by the Actor slot `+0x50` transition [EV-0601], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open."
new_next = "**Selected next line:** continue the 62-caller census at caller 47/62 `FUN_140658a30`; test its tag and payload against the tag-0x0B HitData/AV11/AV12 route. Caller 46 is bounded by EV-0602; keep its indirect sites and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0602/CL-L414/M-0154; falsified H105, supported H106; closed caller 46, checkpointed caller 47")
