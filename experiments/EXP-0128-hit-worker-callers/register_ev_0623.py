from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
captures = []
for stem in ("gog-query-20261019T191026Z", "gog-query-20261019T192617Z"):
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"read-only/hash gate failed: {stem}")
    captures.append((raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace")))
producer = captures[0][4]
resolver = captures[1][4]
for token in ("DISASM=1407bbbb4 MOV RCX, qword ptr [RDX + 0x60]", "OUTGOING_DIRECT_CALL_EDGE=1407bbbbf -> 1402b8b60"):
    if token not in producer:
        raise SystemExit(f"caller-50 resolver input missing: {token}")
for token in (
    "FUNCTION_LOOKUP=FUN_1402b8b60 @ 1402b8b60",
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=1",
    "OUTGOING_DIRECT_CALL_EDGE=1402b8b6a -> 1401699e0",
    "XREF_CALL_COUNT=117",
    "INCOMING_CALLER_FUNCTION_COUNT=64",
    "if ((*(byte *)(param_1 + 0x40) & 1) != 0)",
    "uVar1 = FUN_1401699e0(param_1 + 0x48);",
    "return *DAT_1420f9d28;",
):
    if token not in resolver:
        raise SystemExit(f"object resolver result missing: {token}")
hashes = {}
for raw, err, mp, _, _ in captures:
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0623",
    "source": "Identity-checked GOG caller-50 resolver callsite and FUN_1402b8b60 function graph/decompilation",
    "artifact": f"private-local:.local/ghidra/{captures[1][0].name}", "sha256": captures[1][3]["stdout_sha256"], "captured_utc": captures[1][3]["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x2b8b60 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "paired with caller 50 producer raw from EV-0616"],
    "coverage": "Caller 50 passes qword [param_2+0x60] to FUN_1402b8b60 as RCX. The resolver checks bit 0 of byte at resolver-input +0x40; when set, it returns FUN_1401699e0(input+0x48), otherwise it returns the pointer stored in DAT_1420f9d28. The resolver has one direct callee and 117 analyzed direct call sites across 64 caller functions. Its selected object is the receiver for caller 50's immediate vtable +0x1a8 call and the object pointer retained in the tag-0x12 deferred payload [EV-0615]–[EV-0619]. Concrete object type and method target remain unresolved; no direct HitData/protection/AV11/AV12/UseSkill sink is established.",
    "result": "Caller 50's +0x1a8 receiver is selected by an optional-object/global-fallback resolver keyed by flag bit 0 at subobject +0x40. Trace FUN_1401699e0 and the global fallback identity before interpreting the virtual slot; no armor/HitData conclusion follows from this resolver alone.",
    "local_hashes": hashes, "related_evidence": ["EV-0615", "EV-0616", "EV-0617", "EV-0619", "EV-0620", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0623")
if old and old != item:
    raise SystemExit("EV-0623 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L436", "| CL-L436 | Caller 50 passes its param+0x60 subobject to FUN_1402b8b60; that resolver chooses FUN_1401699e0(subobject+0x48) when byte[subobject+0x40]&1 is set, otherwise the global pointer DAT_1420f9d28. | supported for captured GOG control flow | [EV-0616], [EV-0623] | Returned object type and its virtual +0x1a8 target remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0176 — Caller 50 selects +0x1a8 receiver through optional-object/global fallback (EV-0623)", "## M-0176 — Caller 50 selects +0x1a8 receiver through optional-object/global fallback (EV-0623)\n\nThe AddRagdollHandler producer passes its `param+0x60` subobject to `FUN_1402b8b60`. Bit 0 at subobject `+0x40` selects `FUN_1401699e0(subobject+0x48)`; otherwise the resolver returns `DAT_1420f9d28` [EV-0616], [EV-0623]. That result becomes the receiver for slot `+0x1a8`. Type identity and slot target remain unknown; no HitData/armor edge is established.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 virtual receiver resolver (EV-0623)", "### Caller 50/62 virtual receiver resolver (EV-0623)\n\nCaller 50 passes `param+0x60` to `FUN_1402b8b60`. A bit at that subobject's `+0x40` selects an owned-object lookup through `FUN_1401699e0(subobject+0x48)`; otherwise the resolver returns global `DAT_1420f9d28`. That object receives the unresolved `+0x1a8` call and is retained in tag 0x12 for deferred dispatch [EV-0623]. Trace the owned-object lookup and global type before slot interpretation.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0623 maps caller 50's +0x1a8 receiver selection", "EV-0623 shows caller 50 selects its `+0x1a8` receiver via an optional-object lookup or global fallback keyed by bit 0 at subobject `+0x40`. Receiver type and slot target remain unresolved; no HitData/armor edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0623"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L436"]))
h = {"id": "Q79-H132", "model": "Caller 50's vtable +0x1a8 receiver is selected by FUN_1402b8b60 from an optional object at input+0x48 when input+0x40 bit 0 is set, otherwise from global DAT_1420f9d28.", "predicted_discriminant": "FUN_1402b8b60 branches on byte[input+0x40]&1 and returns FUN_1401699e0(input+0x48) or DAT_1420f9d28; caller 50 supplies param+0x60 as input.", "status": "supported", "evidence": ["EV-0623", "EV-0616"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H132")
next_action = "Trace FUN_1401699e0 used by the optional-object branch of FUN_1402b8b60 and inspect global DAT_1420f9d28's exact pointer/vtable; identify receiver type before interpreting slot +0x1a8."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 +0x1a8 receiver uses optional-object/global fallback; trace FUN_1401699e0 and global type.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0621 maps the shared +0x10 any-match predicate used in FUN_140699500; EV-0622 maps a prior per-entry +0x28 side-effect callback also used in FUN_140713d90. These shared primitives add no HitData/armor edge.", "EV-0621 maps the shared +0x10 any-match predicate used in FUN_140699500; EV-0622 maps a prior per-entry +0x28 side-effect callback also used in FUN_140713d90; EV-0623 maps caller 50's +0x1a8 receiver to an optional-object/global fallback. These routes add no HitData/armor edge.", 1)
old_next = "**Selected next line:** query `FUN_1402b8b60`, whose returned object receives caller 50's unresolved virtual `+0x1a8` call after the two bounded list passes [EV-0621–EV-0622]; establish RTTI/type before slot interpretation."
new_next = "**Selected next line:** trace optional-object accessor `FUN_1401699e0` and global fallback `DAT_1420f9d28` returned through `FUN_1402b8b60` [EV-0623]; identify the selected receiver's type before interpreting virtual `+0x1a8`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0623/CL-L436/M-0176; bounded optional/global receiver resolver; checkpointed FUN_1401699e0")
