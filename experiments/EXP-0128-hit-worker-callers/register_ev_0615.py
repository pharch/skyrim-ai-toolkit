from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEMS = {"builder": "gog-query-20261019T190815Z", "dispatcher": "gog-query-20261019T185131Z"}
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
data = {}
for label, stem in STEMS.items():
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed: {stem}")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed: {stem}")
    data[label] = (raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace"))
builder_raw, builder_err, builder_meta, bm, builder = data["builder"]
for token in (
    "FUNCTION_LOOKUP=FUN_140658b10 @ 140658b10",
    "OUTGOING_DIRECT_CALL_EDGE=140658b32 -> 14065b800",
    "XREF_CALL_EDGE=1407bbd2c -> 140658b10 caller=FUN_1407bbb90",
    "local_88[0] = 0x49;",
    "local_80 = param_2;",
    "FUN_14065b800(param_1,local_88)",
    "FUN_140658b10(DAT_14319a7c0,param_2);",
    "FUN_14054e3c0(local_res10,puVar9 + uVar12)",
    "FUN_14054e340(local_res20,puVar9 + uVar11)",
    "(**(code **)(*plVar6 + 0x1a8))(plVar6,lVar8,1,1,uVar13,0)",
):
    if token not in builder:
        raise SystemExit(f"producer/caller result missing: {token}")
dispatcher_raw, dispatcher_err, dispatcher_meta, dm, dispatcher = data["dispatcher"]
if "case 0x49:" not in dispatcher or "FUN_14054e340(local_res10,puVar20 + uVar21)" not in dispatcher:
    raise SystemExit("matched tag-0x49 dispatcher evidence missing")
hashes = {}
for raw, err, mp, _, _ in data.values():
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0615",
    "source": "Identity-checked GOG caller-50 tag-0x49 builder/producer body and matched dispatcher case",
    "artifact": f"private-local:.local/ghidra/{builder_raw.name}", "sha256": bm["stdout_sha256"], "captured_utc": bm["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658b10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "matched case 0x49 from EV-0608 capture"],
    "coverage": "Caller 50 builder FUN_140658b10 writes tag 0x49 and a retained object pointer; its sole direct producer is FUN_1407bbb90. That producer uses object/process-like fields and virtual calls, enumerates an object list through FUN_14054e3c0 and FUN_14054e340, then either calls an unresolved vtable slot +0x1a8 immediately or queues tag 0x49 followed by FUN_140657c30 when FUN_1406d4110 is set. Matched dispatcher case 0x49 obtains a list through object+0x38 vtable +0x10, calls FUN_14054e340 for each entry, then reaches a state path at object+0x20. Exact type, callback contracts, virtual targets and runtime effects remain unresolved; direct mapped HitData/protection/AV11/AV12/UseSkill reachability is not established by this bounded body.",
    "result": "Caller 50 is a retained-object tag-0x49 list/update route with one producer and immediate/deferred branches. The body contains actor/process-like conditions and unresolved callbacks, so a generic actor-state model and a hit/armor-related model remain competing hypotheses pending callee and producer tracing.",
    "local_hashes": hashes, "related_evidence": ["EV-0614", "EV-0608", "EV-0397", "EV-0260"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0615")
if old and old != item:
    raise SystemExit("EV-0615 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L428", "| CL-L428 | In GOG AE 1.6.1179.0, caller 50 builder FUN_140658b10 queues tag 0x49 with a retained object; sole producer FUN_1407bbb90 has list callbacks and branches between an unresolved immediate virtual call and queued tag-0x49 plus FUN_140657c30, while dispatcher case 0x49 traverses an object list through FUN_14054e340. | supported for captured structure | [EV-0615] | Object identity, callback semantics, virtual targets and connection to HitData/armor skill remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0168 — Caller 50 tag-0x49 retained-object list/update route (EV-0615)", "## M-0168 — Caller 50 tag-0x49 retained-object list/update route (EV-0615)\n\n`FUN_140658b10` queues tag `0x49` with a retained object pointer. Its sole producer `FUN_1407bbb90` traverses an object list through `FUN_14054e3c0`/`FUN_14054e340` and selects an immediate virtual `+0x1a8` path or queued tag 0x49 followed by `FUN_140657c30`; the dispatcher traverses the object list through `FUN_14054e340` [EV-0615]. Type identity, callback contracts, virtual target and runtime effects remain open. No direct HitData/armor-skill edge is established. Claim CL-L428.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62: tag-0x49 retained-object list/update route (EV-0615)", "### Caller 50/62: tag-0x49 retained-object list/update route (EV-0615)\n\n`FUN_140658b10` queues tag `0x49` with a retained object. Its sole producer `FUN_1407bbb90` has process/object-conditioned branches and two list callback helpers, then chooses an unresolved immediate vtable `+0x1a8` call or a deferred tag-0x49 event plus `FUN_140657c30`. Case 0x49 independently obtains an object list and visits entries with `FUN_14054e340` [EV-0615]. Object type and callbacks remain unresolved; compare the producer's direct/incoming call graph and callback targets before interpreting the route.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0615 maps caller 50 tag 0x49 to an object-list update route", "EV-0615 maps caller 50's tag-0x49 retained-object event to a producer with list callbacks and immediate/deferred paths. This is a structural route with unresolved type/virtual semantics; no HitData, armor-skill or quest-gate causal edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0615"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L428"]))
for h in (
    {"id": "Q79-H123", "model": "Caller 50 tag 0x49 is a generic actor/object-list update that runs through matching immediate and deferred callbacks, without a direct HitData/armor-skill edge.", "predicted_discriminant": "Tracing FUN_1407bbb90 and its callbacks resolves collection/state operations and finds no mapped HitData/protection/AV11/AV12/UseSkill sink.", "status": "proposed", "evidence": ["EV-0615"]},
    {"id": "Q79-H124", "model": "Caller 50 tag 0x49 participates in a hit/armor-related path through its producer gates, list callback or unresolved virtual dispatch.", "predicted_discriminant": "Producer/callback xrefs or a resolved virtual target connects this tag-0x49 path to mapped HitData, protection or armor-skill entry points, or a discriminating runtime hit/AVSK observation.", "status": "proposed", "evidence": ["EV-0615"]},
):
    prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
    if prior is None:
        q["hypotheses"].append(h)
    elif prior != h:
        raise SystemExit(f"hypothesis collision: {h['id']}")
next_action = "Query FUN_1407bbb90 with complete direct call edges, direct callees and incoming callers; prioritize resolving FUN_14054e3c0/FUN_14054e340, FUN_140657c30 and the producer's immediate/deferred parity before classifying caller 50."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 tag 0x49 has a sole process/object-conditioned producer and competing generic-state versus hit/armor models; trace producer/callback graph.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("49 of 62 initially uninspected worker callers are reviewed, with 13 remaining.", "50 of 62 initially uninspected worker callers are reviewed, with 12 remaining.", 1)
state = state.replace("EV-0612–EV-0614 bound caller 49's tag-0x48 list route to a generic vtable callback and classified its sole data xref as likely unwind metadata.", "EV-0612–EV-0614 bound caller 49's tag-0x48 list route to a generic vtable callback and classified its sole data xref as likely unwind metadata; EV-0615 begins caller 50's tag-0x49 retained-object route.", 1)
state = state.replace("**OBJ-2:** Q-0079 has 49/62 exact worker callers reviewed; 13 remain.", "**OBJ-2:** Q-0079 has 50/62 exact worker callers reviewed; 12 remain.", 1)
old_next = "**Selected next line:** inspect caller 50/62 `FUN_140658b10` for its tag/payload, producer and direct route to mapped HitData/protection/AV11/AV12/UseSkill sinks after closing caller 49's bounded list route and likely unwind-metadata xref [EV-0612–EV-0614]."
new_next = "**Selected next line:** trace caller 50's sole producer `FUN_1407bbb90`, its direct callees and incoming callers; resolve list callbacks `FUN_14054e3c0`/`FUN_14054e340`, manager continuation `FUN_140657c30`, and immediate/deferred parity before classifying its tag-0x49 path [EV-0615]."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0615/CL-L428/M-0168; caller 50 tag 0x49 open; checkpointed producer trace")
