from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T184930Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x4a28a0":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=1404a2912 -> 1401fe280",
    "INDIRECT_CALL_SITE=1404a2900 CALL qword ptr [RAX + 0x8]",
    "XREF_CALL_EDGE=1401fa067 -> 1404a28a0",
    "plVar1 = *(longlong **)(DAT_143146200 + uVar5 * 8)",
    "FUN_1401fe280(&DAT_143146200,uVar5,1)",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0607",
    "source": "Identity-checked GOG direct-edge census/decompilation of alternate tag-0x44 factory FUN_1404a28a0",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x4a28a0 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1404a28a0 scans a distinct global pointer array DAT_143146200/count DAT_143146210 for entry field +0x28 matching its second parameter, retains the object, and removes the slot through the same helper FUN_1401fe280 used by FUN_1404a27f0. It has one unresolved refcount-finalizer virtual call and one observed caller, tag-0x44 producer FUN_1401fa010. Ghidra's caller decompilation displays this branch as a no-argument call despite the callee's two-parameter prototype; argument-register flow remains unverified and must be checked from producer disassembly. No direct combat/protection/AV11/AV12/UseSkill target appears.",
    "result": "The tag-0x44 producer selects between two structurally parallel keyed global object arrays, each removing a matched entry through shared FUN_1401fe280. The second array is not shared with BGSDecalNode cleanup in the observed caller census. This reinforces object-registry/lifecycle behavior and weakens a combat interpretation, while the producer's second-branch argument mismatch and dynamic object types remain unresolved. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": hashes, "related_evidence": ["EV-0606", "EV-0605", "EV-0604", "EV-0603", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0607")
if old and old != item:
    raise SystemExit("EV-0607 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L420", "| CL-L420 | In GOG AE 1.6.1179.0, alternate factory FUN_1404a28a0 scans global array DAT_143146200 by entry field +0x28 and removes a matching slot through shared helper FUN_1401fe280; its sole observed caller is tag-0x44 producer FUN_1401fa010. | supported for captured static body/call edge | [EV-0607] | Producer register arguments, returned dynamic type, one unresolved finalizer and runtime effects remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0160 — Tag-0x44 selects between parallel keyed object arrays (EV-0607)", "## M-0160 — Tag-0x44 selects between parallel keyed object arrays (EV-0607)\n\n`FUN_1404a28a0` scans a second global object array by field +0x28 and removes a match through the same `FUN_1401fe280` array helper used by `FUN_1404a27f0` [EV-0607], [EV-0606]. Its only observed caller is the tag-0x44 producer. The decompiler omits arguments at that call despite the callee's two-parameter prototype; producer register flow and returned type remain unresolved. The bounded helper is generic registry lifecycle work with no direct HitData/armor-skill edge. No OBJ-1/OBJ-2 edge is added. Claim CL-L420.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 47/62: parallel registry factory and shared array erase helper (EV-0607)", "### Caller 47/62: parallel registry factory and shared array erase helper (EV-0607)\n\nThe alternate factory `FUN_1404a28a0` scans a second global array by field +0x28 and removes a matching entry through the same `FUN_1401fe280` helper as the first factory [EV-0606], [EV-0607]. Its sole caller is the tag-0x44 producer. Ghidra's producer decomp omits arguments at the call despite the callee prototype; inspect producer instructions before interpreting key parity. No mapped hit/armor-skill edge occurs in the factory. Next query producer callsite registers, then continue caller 48/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0607 connects both tag-0x44 registries to one array erase helper", "EV-0607 shows the alternate tag-0x44 factory uses a second keyed global array but shares FUN_1401fe280 with the first factory [EV-0606]. The producer decompilation omits arguments at the second call, so register parity is still unverified. This supports a shared collection primitive within caller 47, not a combat/armor or quest edge.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0607"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L420"]))
h = {"id": "Q79-H113", "model": "Caller 47 selects between parallel key-indexed global object arrays, and both factories use the same array-erasure helper FUN_1401fe280.", "predicted_discriminant": "Each factory scans a separate array by entry +0x28 key and removes the match through FUN_1401fe280; the second factory is called from tag-0x44 case producer.", "status": "supported", "evidence": ["EV-0606", "EV-0607"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H113")
q["hypotheses"] = [dict(x, evidence=list(dict.fromkeys([*x.get("evidence", []), "EV-0607"]))) if x.get("id") in {"Q79-H109", "Q79-H112"} else x for x in q["hypotheses"]]
assessment = "EV-0607 shows the alternate branch scans a second global array and shares array erasure helper FUN_1401fe280 with the first factory. Ghidra omits arguments at the producer's second call despite the callee prototype, so compare producer instructions before treating payload parity as established."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_1401fa010 with its call-edge census and disassembly to resolve actual register arguments at FUN_1404a27f0/FUN_1404a28a0 and verify the second-branch prototype mismatch. Then close caller 47 as bounded generic registry cleanup if no mapped combat/protection/AV11/AV12/UseSkill sink emerges, and continue caller 48/62 FUN_140658a80."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: EV-0607 maps tag-0x44's alternate keyed registry to the same array-erasure helper as the first factory; exact producer registers remain to resolve.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** inspect alternate factory `FUN_1404a28a0` against the keyed registry association with BGSDecalNode cleanup [EV-0606]; then close caller 47 as bounded if no combat/armor sink appears and continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
new = "**Selected next line:** inspect producer `FUN_1401fa010` instructions to resolve the arguments omitted from its `FUN_1404a28a0` decompilation [EV-0607]; then close caller 47 as bounded if no combat/armor sink appears and continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0607/CL-L420/M-0160; H113 supported; checkpointed producer register-flow query")
