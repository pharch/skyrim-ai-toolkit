from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T183817Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{suffix}" for suffix in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x1fdb80":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in ("OUTGOING_DIRECT_CALL_EDGE=1401fdc06 -> 1401fe380", "OUTGOING_DIRECT_CALL_EDGE=1401fdc2d -> 140d1ed80", "INDIRECT_CALL_SITE=1401fdc1c CALL qword ptr [RAX + 0x148]", "INCOMING_CALLER_DECOMPILATION_BEGIN=FUN_1404ab530", "FUN_1401fe380(param_1 + 0x128", "FUN_140d1ed80(param_1,uVar6,&local_res10)", "FUN_1401fdb80(plVar3,param_1)"):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0604",
    "source": "Identity-checked GOG direct-edge census/decompilation of FUN_1401fdb80 and its two incoming callers",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x1fdb80 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1401fdb80 has two direct callees (FUN_1401fe380 and FUN_140d1ed80), two unresolved indirect calls (object vtable +0x148 and refcounted object's +0x8), and two direct callers. It scans a pointer array at param_1+0x128 with count at +0x138; a match with param_2 is removed through FUN_1401fe380. If no match is removed, it calls param_2 vtable +0x148 for a key and invokes FUN_140d1ed80(param_1,key,&out). Caller FUN_1401fa010 supplies acquired object and its +0x170 member; caller FUN_1404ab530 reaches the helper after a float/time comparison, passing a component and parent object. Dynamic types, virtual method, lookup semantics, and descendants remain unresolved.",
    "result": "The target is structurally a pointer-array membership cleanup with a virtual-key fallback lookup, not a direct HitData/armor-skill routine. The second caller's float/time branch weakens a caller-47-specific combat interpretation, but unresolved virtual and lookup paths prevent a broad negative. H109 remains open/narrowed; no OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": hashes, "related_evidence": ["EV-0603", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0604")
if old and old != item:
    raise SystemExit("EV-0604 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L416", "| CL-L416 | In GOG AE 1.6.1179.0, FUN_1401fdb80 scans a pointer array for an object, removes a match through FUN_1401fe380, or invokes object vtable +0x148 and passes its key to FUN_140d1ed80; its two observed callers include FUN_1401fa010 and float/time-branch caller FUN_1404ab530. | supported for captured static structure | [EV-0604] | Object types, virtual meaning, lookup descendants and runtime effects remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0156 — Tag-0x44 helper is a pointer-array cleanup/keyed fallback (EV-0604)", "## M-0156 — Tag-0x44 helper is a pointer-array cleanup/keyed fallback (EV-0604)\n\n`FUN_1401fdb80` scans a pointer array at `param_1+0x128` for `param_2`, removes a match through `FUN_1401fe380`, or calls object vtable `+0x148` and forwards the returned key to `FUN_140d1ed80` [EV-0604]. Its other caller enters from a float/time branch. Dynamic types and effects remain open. This weakens a combat-specific interpretation but does not establish a broad negative or an OBJ-1/OBJ-2 edge. Claim CL-L416.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 47/62: collection cleanup helper narrows tag-0x44 route (EV-0604)", "### Caller 47/62: collection cleanup helper narrows tag-0x44 route (EV-0604)\n\n`FUN_1401fdb80` searches a pointer array at `param_1+0x128` for `param_2`. A match is removed by `FUN_1401fe380`; otherwise object vtable `+0x148` supplies a key to `FUN_140d1ed80`. Its second caller reaches it from a float/time comparison, passing a component and parent [EV-0604]. This favors generic membership cleanup/keyed lookup over combat work but leaves virtual and lookup descendants open. Identify the acquired object and trace `FUN_140d1ed80`; then continue caller 48/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0604 narrows tag-0x44 helper to membership cleanup/keyed lookup", "EV-0604 shows FUN_1401fdb80 scanning/removing a pointer-array entry or deriving a key from unresolved object vtable +0x148 for FUN_140d1ed80. Its second caller arises in a float/time branch, weakening but not eliminating a combat interpretation. No OBJ-1/OBJ-2 causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0604"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L416"]))
for h in (
    {"id": "Q79-H109", "model": "The clear-gate object helper FUN_1401fdb80 carries combat/protection/AV11/AV12/UseSkill effects.", "predicted_discriminant": "The helper or producer-backed direct descendants resolve to mapped HitData, effective protection, or armor-skill sinks.", "status": "proposed", "evidence": ["EV-0603", "EV-0604"]},
    {"id": "Q79-H110", "model": "FUN_1401fdb80 is general pointer-array membership cleanup with keyed fallback, rather than a combat-specific handler.", "predicted_discriminant": "The helper removes a matching object pointer, otherwise invokes a virtual key accessor and separate lookup; another caller is reached from a float/time branch.", "status": "supported", "evidence": ["EV-0604"]},
):
    prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
    if prior is None:
        q["hypotheses"].append(h)
    else:
        for key, value in h.items():
            if key != "evidence" and prior.get(key) != value:
                raise SystemExit(f"hypothesis collision: {h['id']}")
        prior["evidence"] = list(dict.fromkeys([*prior.get("evidence", []), *h["evidence"]]))
assessment = "EV-0604 narrows tag-0x44's immediate helper to pointer-array membership cleanup/keyed fallback. Its other caller arrives from a float/time comparison, reducing the combat-specific prior without resolving the virtual key callback or lookup descendants."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xd1ed80 --list-call-edges --follow-incoming-calls 8 --follow-direct-calls 8 --timeout 600 to inspect the keyed fallback. Then query object acquisition helpers FUN_1404a27f0 and FUN_1404a28a0 to identify caller-47's concrete family, and continue caller 48/62 FUN_140658a80."
q["next_action"] = next_action
fr["next_action"] = next_action
fr["session_next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: EV-0604 bounds caller 47's tag-0x44 helper as pointer-array cleanup/keyed fallback with a second float/time-branch caller; virtual and lookup descendants remain unresolved.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** trace clear-gate helper `FUN_1401fdb80` from caller 47's tag-0x44 producer [EV-0603], then continue caller 48/62 `FUN_140658a80`. Caller 46 is bounded by EV-0602; keep its indirect sites and GOG/Steam boundaries open."
new = "**Selected next line:** inspect keyed fallback `FUN_140d1ed80` and caller-47 object acquisition helpers after EV-0604 bounds `FUN_1401fdb80` as pointer-array cleanup; then continue caller 48/62 `FUN_140658a80`. Keep unresolved virtual effects and GOG/Steam boundaries open."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0604/CL-L416/M-0156; H110 supported, H109 remains proposed; checkpointed FUN_140d1ed80")
