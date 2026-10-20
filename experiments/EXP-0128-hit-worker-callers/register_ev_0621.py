from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T192206Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x54e340":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_14054e340 @ 14054e340",
    "INDIRECT_CALL_SITE=14054e359 CALL qword ptr [RAX + 0x10]",
    "XREF_CALL_EDGE=1407bbde1 -> 14054e340 caller=FUN_1407bbb90",
    "XREF_CALL_EDGE=14065ae71 -> 14054e340 caller=FUN_140659160",
    "XREF_CALL_EDGE=14069a921 -> 14054e340 caller=FUN_140699500",
    "XREF_CALL_COUNT=6",
    "if (*param_1 == '\\0')",
    "cVar1 = (**(code **)(*(longlong *)*param_2 + 0x10))();",
    "*param_1 = '\\x01';",
):
    if token not in out:
        raise SystemExit(f"callback result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0621",
    "source": "Identity-checked GOG decompilation and caller census for FUN_14054e340",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x54e340 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_14054e340 has no direct callees, one unresolved virtual call at entry-object vtable +0x10, and six direct callers. For a non-null entry and false accumulator, it invokes that no-argument predicate; a true return sets context byte to 1. Once set, the predicate is skipped for later entries; false results preserve 0. Null entries preserve the state. It therefore implements an any-match list predicate at the observed level. Direct callers include AddRagdollHandler producer FUN_1407bbb90, dispatcher FUN_140659160 tag 0x49 and actor/process routine FUN_140699500 [EV-0621]. The shared helper is structural evidence only; element type and callback semantics remain unresolved, with no direct HitData/protection/AV11/AV12/UseSkill edge.",
    "result": "The tag-0x49 list helper is an any-match predicate aggregator over element virtual slot +0x10. Its direct reuse in FUN_140699500 establishes a shared native collection primitive across two caller families, not a shared HitData/armor effect or causal gameplay edge.",
    "local_hashes": hashes, "related_evidence": ["EV-0615", "EV-0616", "EV-0617", "EV-0600", "EV-0601", "EV-0602", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0621")
if old and old != item:
    raise SystemExit("EV-0621 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L434", "| CL-L434 | GOG FUN_14054e340 is an any-match list predicate: for non-null entries it calls vtable slot +0x10 until a predicate returns true, then sets the context byte; it has six callers including tag-0x49 producer/dispatcher and FUN_140699500. | supported for captured helper structure and caller set | [EV-0621] | Concrete element type, virtual predicate semantics and cross-caller gameplay effect remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0174 — FUN_14054e340 performs a short-circuit any-match predicate over a list (EV-0621)", "## M-0174 — FUN_14054e340 performs a short-circuit any-match predicate over a list (EV-0621)\n\nFor each non-null entry, if the context byte is false, the helper invokes element vtable `+0x10`; a true result sets the byte and short-circuits later predicate calls. False/null results preserve 0. It has six direct callers, including AddRagdollHandler producer/dispatcher and `FUN_140699500` [EV-0621]. This proves shared helper reuse, not shared semantic outcome; element types and predicate behavior are unresolved. No HitData/armor-skill causal edge is established.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 tag-0x49 any-match list callback (EV-0621)", "### Caller 50/62 tag-0x49 any-match list callback (EV-0621)\n\n`FUN_14054e340` visits non-null list entries through virtual slot `+0x10` while the context byte is false; a true predicate sets the byte and stops later checks. This is a generic any-match helper with six callers, including tag-0x49 producer/dispatcher and prior actor/process routine `FUN_140699500` [EV-0621]. Shared helper reuse is an engine-level connection only; element type and predicate meaning remain unknown. Trace sibling `FUN_14054e3c0` next.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0621 establishes shared any-match helper reuse without a causal edge", "EV-0621 establishes that AddRagdollHandler tag-0x49 producer/dispatcher and actor/process routine `FUN_140699500` directly reuse `FUN_14054e340`, an any-match list-predicate helper. This is a shared native primitive, not evidence that the caller families share hit, armor-skill or quest-gate behavior; no causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0621"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L434"]))
h = {"id": "Q79-H130", "model": "Caller 50's tag-0x49 list helper computes an any-match predicate over entry virtual slot +0x10; its shared use by FUN_140699500 is a generic primitive, not evidence of common combat/armor semantics.", "predicted_discriminant": "FUN_14054e340 short-circuits after a true predicate, has six callers including FUN_140699500, and resolves no direct HitData/protection/AV11/AV12/UseSkill target.", "status": "supported", "evidence": ["EV-0621", "EV-0600", "EV-0602"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H130")
assessment = "EV-0621 identifies a shared any-match callback primitive used by AddRagdollHandler tag 0x49 and FUN_140699500; this is cross-caller helper reuse only and adds no HitData/armor causal edge."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query sibling helper FUN_14054e3c0 with direct/incoming edges; determine its predicate/state contract for AddRagdollHandler's first list scan, then return to the unresolved returned object and vtable +0x1a8 target."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: tag-0x49 shared list helper is an any-match predicate reused in FUN_140699500; trace sibling FUN_14054e3c0.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0615–EV-0618 map caller 50 tag 0x49 to RTTI-identified AddRagdollHandler slot 1; its immediate and deferred tag-0x12 routes share virtual +0x1a8 and pointer roles but have different visible argument setup; the worker wrapper forwards only the event pointer, so extra register/stack values do not establish parity.", "EV-0615–EV-0620 map caller 50 tag 0x49 to RTTI-identified AddRagdollHandler slot 1; its immediate and deferred tag-0x12 routes share virtual +0x1a8 and pointer roles but not visible argument setup, and the worker wrapper forwards only the event pointer. EV-0621 maps its shared list callback as an any-match predicate also reused in FUN_140699500; no HitData/armor edge follows from that reuse.", 1)
old_next = "**Selected next line:** trace shared tag-0x49 list callback `FUN_14054e340`, now that the worker wrapper's callsite shows only the event pointer is explicitly forwarded to the dispatcher [EV-0620]; preserve unresolved virtual-call semantics."
new_next = "**Selected next line:** query sibling list predicate `FUN_14054e3c0` after identifying `FUN_14054e340`'s any-match semantics and shared use in `FUN_140699500` [EV-0621]; then trace the returned object and unresolved `+0x1a8` target."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0621/CL-L434/M-0174; identified shared any-match callback; checkpointed FUN_14054e3c0")
