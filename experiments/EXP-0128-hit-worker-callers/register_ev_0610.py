from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T185607Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x1fa100":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=1401fa181 -> 1401fdab0",
    "INDIRECT_CALL_SITE=1401fa1ac CALL qword ptr [RAX + 0x1c0]",
    "XREF_CALL_EDGE=140774d61 -> 1401fa100",
    "XREF_CALL_EDGE=14065aa2c -> 1401fa100",
    "if (param_2 == '\\0')",
    "FUN_1401fdab0(lVar1,0)",
    "FUN_1414a33c0(uVar2,*plVar6,1,1)",
    "FUN_1401fc320(param_1 + 0x30,1)",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0610",
    "source": "Identity-checked GOG direct-edge census/decompilation of tag-0x45 handler FUN_1401fa100 and four callers",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x1fa100 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1401fa100 has eight direct-call edges to six targets and five unresolved virtual/refcount sites, including object vtable +0x1c0. With param_2==0 it calls each child object vtable +0x1c0, releases all list references and clears the list at manager +0x48/+0x58. With param_2!=0 it walks that list, may call FUN_1401fdab0(child,0), a gated FUN_1414a33c0(global,child,1,1), and child vtable +0x1c0, then removes/compacts entries; it also clears lists at +0x18 and +0x60 and calls FUN_1401fc320(manager+0x30,1). Four callers include FUN_140774b80 immediate route, dispatcher FUN_140659160 case 0x45, destructor-like FUN_1401f9530 with flag 0, and FUN_140776c60. Captured bodies are manager/collection teardown and contain no direct mapped HitData/protection/AV11/AV12/UseSkill call; dynamic targets remain open.",
    "result": "Tag-0x45 handler FUN_1401fa100 is a flag-dependent manager child-list cleanup/update route, with the immediate caller passing 1 and the dispatcher forwarding the event byte. It is not a direct tag-0x0B/HitData/armor-skill route. Caller 48 remains bounded but open until the deferred builder call's actual byte register is verified; no global negative or OBJ-1/OBJ-2 edge is added.",
    "local_hashes": hashes, "related_evidence": ["EV-0609", "EV-0608", "EV-0574", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0610")
if old and old != item:
    raise SystemExit("EV-0610 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L423", "| CL-L423 | In GOG AE 1.6.1179.0, tag-0x45 target FUN_1401fa100 performs flag-dependent manager child-list cleanup/update with unresolved object vtable +0x1c0 callbacks; its callers include the immediate FUN_140774b80 path, dispatcher case 0x45, and a flag-0 teardown caller. | supported for the captured local state path | [EV-0610] | Runtime object type, virtual effects, deferred caller byte and Steam equivalence remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0163 — Tag-0x45 target performs flag-dependent manager-list cleanup (EV-0610)", "## M-0163 — Tag-0x45 target performs flag-dependent manager-list cleanup (EV-0610)\n\n`FUN_1401fa100` walks and clears manager child lists, invokes unresolved child vtable `+0x1c0`, and in the nonzero mode calls `FUN_1401fdab0`, a gated `FUN_1414a33c0`, and an array compaction helper [EV-0610]. Its callers include the tag-0x45 immediate path, dispatcher case 0x45, and a flag-0 teardown path. The bounded body is manager/list state work with no direct mapped HitData or armor-skill sink; dynamic effects and deferred argument flow remain open. No OBJ-1/OBJ-2 edge is added. Claim CL-L423.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 48/62: tag-0x45 target is flag-dependent manager-list cleanup (EV-0610)", "### Caller 48/62: tag-0x45 target is flag-dependent manager-list cleanup (EV-0610)\n\n`FUN_1401fa100` clears manager child lists in flag-0 mode; in nonzero mode it removes/compacts entries, calls `FUN_1401fdab0`, conditionally reaches `FUN_1414a33c0`, and invokes unresolved child vtable `+0x1c0` [EV-0610]. The immediate tag-0x45 caller passes 1, while the dispatcher forwards the byte payload. No direct HitData/AV11/AV12/UseSkill route occurs in the captured body. Query producer register arguments before closing caller 48.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0610 bounds tag-0x45 target as manager-list cleanup", "EV-0610 bounds FUN_1401fa100 as a flag-dependent manager child-list cleanup/update path with dynamic +0x1c0 callbacks and no direct mapped armor-skill target. The deferred producer byte remains unresolved. No OBJ-1/OBJ-2 causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0610"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L423"]))
h = {"id": "Q79-H117", "model": "The tag-0x45 target is a flag-dependent manager child-list cleanup/update, not a direct HitData/armor-skill handler.", "predicted_discriminant": "Flag zero clears child references; nonzero removes/compacts entries and invokes object-management callbacks, with no direct mapped HitData/AV11/AV12/UseSkill edge.", "status": "supported", "evidence": ["EV-0610"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H117")
for hid in ("Q79-H115", "Q79-H116"):
    old_h = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if old_h:
        old_h["evidence"] = list(dict.fromkeys([*old_h.get("evidence", []), "EV-0610"]))
assessment = "EV-0610 shows tag-0x45 target FUN_1401fa100 as flag-dependent manager-list teardown/update with unresolved +0x1c0 callbacks and no direct mapped HitData/armor-skill sink. Immediate flag 1 and worker-byte forwarding converge on this helper; caller disassembly must confirm the queued byte before closure."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query producer FUN_140774b80 instructions to verify register arguments to FUN_140658a60 and confirm the queued byte equals immediate selector 1; then close caller 48 as bounded manager-list cleanup if no unexpected call edge appears and continue caller 49/62 FUN_140658af0."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: EV-0610 bounds caller 48 tag-0x45 target as flag-dependent manager-list cleanup; exact byte register on the deferred FUN_140658a60 call remains unresolved.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("Q-0079/TX-20261018-0013 remains active on OBJ-2: 47 of 62 initially uninspected worker callers are reviewed, with 15 remaining. EV-0603–EV-0605 bound caller 47's tag-0x44 immediate route to generic manager-array cleanup with unresolved virtual effects.", "Q-0079/TX-20261018-0013 remains active on OBJ-2: 48 of 62 initially uninspected worker callers are reviewed, with 14 remaining. EV-0603–EV-0608 bound caller 47's tag-0x44 route to keyed object-list lifecycle work; EV-0609–EV-0610 map caller 48's tag-0x45 manager-list path, with its deferred byte register still to verify.", 1)
state = state.replace("**OBJ-2:** Q-0079 has 47/62 exact worker callers reviewed; 15 remain.", "**OBJ-2:** Q-0079 has 48/62 exact worker callers reviewed; 14 remain.", 1)
old = "**Selected next line:** query caller 48 helper `FUN_1401fa100` after the requested RVA `0x658a80` resolves inside tag-0x45 builder `FUN_140658a60` [EV-0609]; resolve the omitted deferred byte argument, then continue caller 49/62 `FUN_140658af0`."
new = "**Selected next line:** inspect `FUN_140774b80` instructions to verify the byte argument to queued tag-0x45 builder `FUN_140658a60` [EV-0609/EV-0610]; then close caller 48 as bounded manager-list cleanup and continue caller 49/62 `FUN_140658af0`."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0610/CL-L423/M-0163; caller 48 helper bounded; checkpointed producer registers")
