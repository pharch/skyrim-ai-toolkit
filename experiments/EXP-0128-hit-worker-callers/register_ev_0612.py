from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T190025Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x658af0":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_140658ac0 @ 140658ac0",
    "OUTGOING_DIRECT_CALL_EDGE=140658af1 -> 14065b800",
    "XREF_CALL_COUNT=0",
    "local_88[0] = 0x48;",
    "local_80 = param_2;",
    "local_78 = param_3;",
    "FUN_14065b800(param_1,local_88)",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")
dispatcher = (GH / "gog-query-20261019T185131Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
for token in (
    "case 0x48:",
    "FUN_14054e390(&local_a8,puVar20 + uVar21)",
    "FUN_140659160",
):
    if token not in dispatcher:
        raise SystemExit(f"dispatcher result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0612",
    "source": "Identity-checked GOG caller-49 tag-0x48 builder and matched dispatcher case",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658af0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "matched case 0x48 from EV-0608 capture"],
    "coverage": "Requested RVA 0x658af0 resolves inside Ghidra function FUN_140658ac0 (start 0x658ac0). The builder writes tag 0x48, copies a refcounted object pointer as param_2 and a second pointer-sized value as param_3, then calls FUN_14065b800. It has zero analyzed direct incoming code-call edges and one source-less DATA xref at RVA 0x3657848; whether that reference is a function table, exception metadata or other registration is unresolved. The identity-checked worker dispatcher case 0x48 reads both payload pointers, obtains a list-like object through the first object's +0x38 virtual slot +0x10, iterates its +0x14-backed entries, and calls FUN_14054e390 on entries before releasing both refs [EV-0608]. No direct mapped HitData/protection/AV11/AV12/UseSkill target appears in the builder/case excerpt; list helper semantics and the source of the data xref remain unresolved.",
    "result": "Caller 49 is a tag-0x48 refcounted object/pointer-pair event with a matched list-iteration case. The builder has no analyzed incoming direct caller; one data xref remains unclassified. The dispatcher operates through an unresolved object interface and calls FUN_14054e390 for list entries. This is a bounded generic object/list route, not a direct tag-0x0B/armor-skill constructor; trace FUN_14054e390 and classify the data reference before closing it.",
    "local_hashes": hashes, "related_evidence": ["EV-0608", "EV-0397", "EV-0574"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0612")
if old and old != item:
    raise SystemExit("EV-0612 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L425", "| CL-L425 | In GOG AE 1.6.1179.0, requested caller-list RVA 0x658af0 resolves inside FUN_140658ac0, which builds tag 0x48 with a refcounted object pointer and a second pointer-sized payload before queue submission; the matched case obtains a list through object+0x38 vtable +0x10 and calls FUN_14054e390 on each entry. | supported for captured builder/case structure | [EV-0612], [EV-0608] | Builder source xref, list helper semantics, receiver RTTI, runtime effects and Steam equivalence remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0165 — Caller 49 tag-0x48 object-pair event enters list iteration (EV-0612)", "## M-0165 — Caller 49 tag-0x48 object-pair event enters list iteration (EV-0612)\n\nBuilder `FUN_140658ac0` writes tag `0x48` with a retained object pointer and a second pointer-sized payload, then queues it. Dispatcher case 0x48 obtains a list through the first object+`0x38` virtual slot `+0x10`, iterates its `+0x14` entries and calls `FUN_14054e390` [EV-0612], [EV-0608]. The builder has zero analyzed incoming direct calls and one unclassified DATA xref; RTTI, helper semantics, and runtime behavior remain open. No direct HitData/armor-skill or OBJ-1 edge is established. Claim CL-L425.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 49/62: tag-0x48 refcounted object-pair and list case (EV-0612)", "### Caller 49/62: tag-0x48 refcounted object-pair and list case (EV-0612)\n\nThe requested RVA `0x658af0` lies inside builder `FUN_140658ac0`, which queues tag `0x48` with a retained object pointer and second pointer-sized value. No incoming direct caller is analyzed; one data xref at RVA `0x3657848` remains unclassified. Case 0x48 obtains a list through object+`0x38` vslot `+0x10`, iterates entries and calls `FUN_14054e390` [EV-0612], [EV-0608]. Trace that helper and classify the xref before closure; no direct HitData/armor-skill sink appears in the bounded builder/case.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0612 maps caller 49 into a tag-0x48 list iteration", "EV-0612 maps caller 49's tag-0x48 object/pointer-pair payload to a dispatcher list-iteration route through unresolved object vtable +0x10 and FUN_14054e390. The builder's sole data xref remains unclassified; no OBJ-1/OBJ-2 edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0612"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L425"]))
h = {"id": "Q79-H119", "model": "Caller 49 at requested RVA 0x658af0 is a tag-0x48 refcounted object/pointer-pair builder whose matched case enters list iteration through an unresolved object interface.", "predicted_discriminant": "Containing function FUN_140658ac0 writes tag 0x48 plus two pointer-sized fields; case 0x48 calls object+0x38 vtable +0x10 for a list and then FUN_14054e390 for entries.", "status": "supported", "evidence": ["EV-0612", "EV-0608"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H119")
assessment = "EV-0612 adds caller 49 tag 0x48: a refcounted object/pointer pair with a dispatcher list-iteration case. No direct tag-0x0B/HitData/armor-skill edge appears; its sole data xref and list helper remain unresolved."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_14054e390 with direct/incoming edges to identify the tag-0x48 list helper's exact collection/state operation and screen for mapped HitData/protection/AV11/AV12/UseSkill sinks; then inspect source-less data xref RVA 0x3657848 to classify function-table versus exception/registration metadata."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 49 is a tag-0x48 refcounted object/pointer-pair builder with one unclassified data xref and a case-local list iterator; trace FUN_14054e390 next.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 48 of 62 initially uninspected worker callers are reviewed, with 14 remaining. EV-0603–EV-0608 bound caller 47's tag-0x44 route to keyed object-list lifecycle work; EV-0609–EV-0611 bound caller 48's tag-0x45 manager-list cleanup with immediate/deferred selector parity, while dynamic callbacks remain open."
new = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 49 of 62 initially uninspected worker callers are reviewed, with 13 remaining. EV-0603–EV-0608 bound caller 47's tag-0x44 route to keyed object-list lifecycle work; EV-0609–EV-0611 bound caller 48's tag-0x45 manager-list cleanup with immediate/deferred selector parity; EV-0612 begins caller 49's tag-0x48 list route. Dynamic callbacks and the exact live armor result remain open."
if old not in state:
    raise SystemExit("STATE active checkpoint summary not found")
state = state.replace(old, new, 1)
state = state.replace("**OBJ-2:** Q-0079 has 48/62 exact worker callers reviewed; 14 remain.", "**OBJ-2:** Q-0079 has 49/62 exact worker callers reviewed; 13 remain.", 1)
old_next = "**Selected next line:** continue caller 49/62 `FUN_140658af0` after caller 48's bounded tag-0x45 manager-list cleanup and parity result [EV-0609–EV-0611]; test its tag/payload and direct route against the mapped HitData/protection/AV11/AV12/UseSkill functions."
new_next = "**Selected next line:** trace tag-0x48 list helper `FUN_14054e390` and then classify caller 49's sole data xref RVA `0x3657848` [EV-0612]; continue to caller 50 after the bounded list-path result."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0612/CL-L425/M-0165; caller 49 tag 0x48; checkpointed FUN_14054e390")
