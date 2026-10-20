from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T185131Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x1fa010":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=1401fa067 -> 1404a28a0",
    "OUTGOING_DIRECT_CALL_EDGE=1401fa06e -> 1404a27f0",
    "DISASM=1401fa05b MOV EDX, EBX",
    "DISASM=1401fa05d LEA RCX, [RSP + 0x20]",
    "DISASM=1401fa067 CALL 0x1404a28a0",
    "DISASM=1401fa06e CALL 0x1404a27f0",
    "FUN_1401fa010(param_1,(int)plVar3[5],*(undefined1 *)((longlong)plVar3 + 0x54))",
    "puVar6 = (undefined8 *)(**(code **)(*plVar3 + 0x10))(plVar3)",
    "FUN_1401fa010(DAT_1420fd578,param_1[2],*(undefined1 *)(param_1 + 4))",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0608",
    "source": "Identity-checked GOG instruction/call-edge trace of tag-0x44 producer FUN_1401fa010 and three callers",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x1fa010 --list-call-edges --follow-incoming-calls 8 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1401fa010 has five direct callees and two unresolved refcount-finalizer virtual calls. Before its selector branch, it loads param_2 into EBX/RDX and LEA's &local_18 into RCX; both FUN_1404a28a0 and FUN_1404a27f0 receive this same output pointer and key, resolving the decompiler's omitted-arguments mismatch. The clear-gate object lookup then conditionally calls FUN_1401fdb80(local_18+0x170,local_18). Three direct callers are FUN_1401fa3d0, FUN_1401fbd10, and dispatcher FUN_140659160 case 0x44. FUN_1401fa3d0 iterates object-child entries, compares their virtual +0x10 result to DAT_143146390 and an owner pointer to its argument, then calls FUN_1401fa010 with child +0x28 key and byte +0x54. FUN_1401fbd10 iterates a dword list into the same producer. The registry factories are also used by two Ghidra-labeled BGSDecalNode cleanup callers [EV-0606]. The selected route is object-list/key lifecycle handling; dynamic type and virtual cleanup remain unresolved. No direct HitData/protection/AV11/AV12/UseSkill target appears.",
    "result": "Both tag-0x44 factory branches receive exactly the same output pointer and key. Together with the object-child filter/callback, dword-list wrapper, and BGSDecalNode cleanup use of the shared registry, caller 47 is bounded as generic keyed object-lifecycle work. It does not construct tag 0x0B or expose a direct mapped combat/armor-skill edge. Unresolved manager/object virtual callbacks mean this is a bounded local result, not a global negative. Close caller 47 and continue caller 48/62 FUN_140658a80.",
    "local_hashes": hashes, "related_evidence": ["EV-0607", "EV-0606", "EV-0605", "EV-0604", "EV-0603", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0608")
if old and old != item:
    raise SystemExit("EV-0608 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L421", "| CL-L421 | In GOG AE 1.6.1179.0, tag-0x44 producer FUN_1401fa010 passes the same key/output pointer to both global-array factories; one incoming caller iterates object children selected by virtual +0x10 identity and invokes it with child +0x28/+0x54 fields, while another drains a dword list. | supported for the captured caller/producer flow | [EV-0608], [EV-0606] | Child type and virtual effects remain unresolved; this is not a global combat/armor negative or Steam result. |")
append_once("research/MECHANISMS.md", "## M-0161 — Tag-0x44 callback is keyed object-list lifecycle work (EV-0608)", "## M-0161 — Tag-0x44 callback is keyed object-list lifecycle work (EV-0608)\n\n`FUN_1401fa010` passes identical `&local_18`/key arguments to the two parallel array factories, then conditionally sends the acquired object and its `+0x170` manager to `FUN_1401fdb80`. One direct caller traverses child objects, filters by unresolved vtable `+0x10`/owner identity, and calls the producer with child `+0x28` and `+0x54`; another drains a dword list. The keyed factories' shared registry is also used by BGSDecalNode cleanup [EV-0606], [EV-0607], [EV-0608]. This bounds caller 47 as generic object lifecycle work with unresolved virtual callbacks, not a direct tag-0x0B/armor-skill constructor. No global negative or OBJ-1/OBJ-2 edge is added. Claim CL-L421.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 47/62: tag-0x44 object callback and factory arguments resolved (EV-0608)", "### Caller 47/62: tag-0x44 object callback and factory arguments resolved (EV-0608)\n\nProducer disassembly shows both factory branches receive the same output pointer and key, correcting the omitted-argument decompilation. `FUN_1401fa3d0` filters child entries by unresolved virtual `+0x10` identity and owner pointer, then calls the producer with child `+0x28`/+0x54 values; `FUN_1401fbd10` drains a dword list into the same producer. The global keyed arrays are also used by BGSDecalNode-labeled cleanup callers [EV-0606]–[EV-0608]. Caller 47 is bounded as generic object-list lifecycle work with unresolved virtual cleanup, no direct tag-0x0B/HitData/armor-skill edge, and no global negative. Continue caller 48/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0608 closes caller 47 as a bounded keyed object-list path", "EV-0608 resolves identical output/key arguments to both tag-0x44 factory branches and maps another caller's child-key callback into the same producer. Together with BGSDecalNode cleanup use of the same registry [EV-0606], this supports a generic object-list lifecycle route for caller 47. Unresolved virtuals remain; no HitData/armor-skill edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0608"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L421"]))
for hid in ("Q79-H108", "Q79-H109", "Q79-H112", "Q79-H113"):
    h = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if h:
        h["evidence"] = list(dict.fromkeys([*h.get("evidence", []), "EV-0608"]))
h = {"id": "Q79-H114", "model": "Both tag-0x44 keyed factory branches receive the same output pointer/key; a caller selects object children by virtual +0x10 identity and routes child key/flag fields back into the shared producer.", "predicted_discriminant": "Producer instructions set RCX=&local_18 and RDX=param_2 before the selector, and both factory callsites use those unchanged registers; the child-list caller passes fields +0x28/+0x54 after a vtable/owner predicate.", "status": "supported", "evidence": ["EV-0608"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H114")
assessment = "EV-0608 resolves the parallel factory argument mismatch and bounds caller 47 as a keyed object-list lifecycle route, with BGSDecalNode cleanup use and unresolved virtual finalizers. H109 remains only a narrowed dynamic-path possibility; this local line adds no OBJ-1/OBJ-2 edge."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Close caller 47/62 as a bounded tag-0x44 keyed object-list lifecycle path (EV-0603–EV-0608), preserving its unresolved virtual callbacks and no-global-negative limit. Then query caller 48/62 FUN_140658a80 for tag/payload, exact producers, dispatcher route and mapped HitData/protection/AV11/AV12/UseSkill edges."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 47/62 is bounded as tag-0x44 keyed object-list lifecycle work by EV-0603–EV-0608; manager/object virtual cleanup remains unresolved.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** inspect producer `FUN_1401fa010` instructions to resolve the arguments omitted from its `FUN_1404a28a0` decompilation [EV-0607]; then close caller 47 as bounded if no combat/armor sink appears and continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
new = "**Selected next line:** close caller 47/62 as bounded tag-0x44 keyed object-list lifecycle work [EV-0603–EV-0608], preserving unresolved virtual callbacks; then query caller 48/62 `FUN_140658a80` against the mapped HitData/protection/AV11/AV12/UseSkill route."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0608/CL-L421/M-0161; caller 47 bounded; checkpointed caller 48")
