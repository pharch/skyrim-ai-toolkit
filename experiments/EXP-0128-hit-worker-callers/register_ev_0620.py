from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T192019Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x65b800":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_14065b800 @ 14065b800",
    "OUTGOING_DIRECT_CALL_EDGE=14065b915 -> 140659160",
    "DISASM=14065b912 MOV RCX, RSI",
    "DISASM=14065b915 CALL 0x140659160",
    "DISASM=14065b8cf CALL qword ptr [RAX + 0x8]",
    "DISASM=14065b91a MOV RBX, qword ptr [RSP + 0x50]",
):
    if token not in out:
        raise SystemExit(f"worker callsite result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0620",
    "source": "Identity-checked GOG FUN_14065b800 worker wrapper disassembly at its sole call to FUN_140659160",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x65b800 --list-call-edges --timeout 600"],
    "coverage": "FUN_14065b800 receives the event pointer in RSI and calls FUN_140659160 at RVA 0x65b915 after explicitly moving only that pointer to RCX. The call block does not set RDX, R8, R9 or stack arguments; an earlier virtual slot +0x8 call and other synchronization code intervene, so these are not stable event fields. This bounds but does not identify the callee's virtual-call signature: case 0x12's R8 selector-byte setup is explicit, while extra values at that downstream call have no proven relationship to the AddRagdollHandler immediate call's R9/stack values.",
    "result": "The worker wrapper forwards only the dispatcher event pointer explicitly. It cannot supply evidence that case 0x12's extra register/stack values match the immediate +0x1a8 call; exact target signature and effects remain unresolved. This supports rejecting payload-level argument-parity claims without proving terminal behavioral inequality.",
    "local_hashes": hashes, "related_evidence": ["EV-0619", "EV-0618", "EV-0616", "EV-0608", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0620")
if old and old != item:
    raise SystemExit("EV-0620 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L433", "| CL-L433 | GOG worker wrapper FUN_14065b800 calls FUN_140659160 with only the event pointer explicitly moved into RCX; it does not set RDX/R8/R9/stack arguments at the callsite, so those values are not proven payload fields for case 0x12. | supported disassembly result | [EV-0620] | The dispatcher's downstream virtual-call signature and inherited volatile-register values remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0173 — Worker wrapper forwards only the event pointer to FUN_140659160 (EV-0620)", "## M-0173 — Worker wrapper forwards only the event pointer to FUN_140659160 (EV-0620)\n\nAt the sole direct call to dispatcher `FUN_140659160`, `FUN_14065b800` explicitly loads only `RCX` with the event pointer. It does not set `RDX/R8/R9` or stack arguments at that callsite [EV-0620]. Therefore case 0x12's uninitialized-looking extra call values are not proven payload fields and cannot support immediate/deferred argument parity. The callee signature remains unresolved; no behavior equivalence claim follows. Claim CL-L433.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Worker wrapper context for tag-0x12 virtual call (EV-0620)", "### Worker wrapper context for tag-0x12 virtual call (EV-0620)\n\n`FUN_14065b800`'s only direct call to dispatcher `FUN_140659160` moves the event pointer into `RCX` and sets no `RDX/R8/R9` or stack arguments at the callsite. Thus the tag-0x12 case's extra virtual-call values are not proven event payload fields, and they cannot restore parity with the producer's explicit immediate setup [EV-0620]. The target signature and terminal behavior remain unknown. Next query shared callback `FUN_14054e340`.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0620 bounds the worker-to-dispatcher call context", "EV-0620 shows the worker wrapper explicitly forwards only the event pointer to `FUN_140659160`; it supplies no proven extra event arguments for case 0x12. This supports rejecting a payload-parity claim while leaving virtual target behavior unresolved.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0620"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L433"]))
h = {"id": "Q79-H129", "model": "The tag-0x12 case's extra register/stack values are not supplied as event payload fields by FUN_14065b800; the worker wrapper explicitly forwards only the event pointer.", "predicted_discriminant": "At the sole call to FUN_140659160, RCX is set to the event pointer and no other payload arguments are placed in RDX/R8/R9 or stack slots.", "status": "supported", "evidence": ["EV-0620"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H129")
assessment = "EV-0620 shows the worker wrapper supplies only the dispatcher event pointer at its direct callsite; extra case-0x12 vcall argument values are not proven payload or parity fields."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_14054e340 with direct/incoming edges and its callback body, used in both AddRagdollHandler slot-1 producer and tag-0x49 dispatcher; bound its contract and inspect for mapped HitData/protection/AV11/AV12/UseSkill sinks."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: worker forwards only event pointer; trace shared tag-0x49 list callback FUN_14054e340 next.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("different visible argument setup.", "different visible argument setup; the worker wrapper forwards only the event pointer, so extra register/stack values do not establish parity.", 1)
old_next = "**Selected next line:** inspect `FUN_14065b800` callsite RVA `0x65b915` for register/stack context inherited by case 0x12, after disassembly falsified exact visible argument parity [EV-0619]; then trace shared tag-0x49 list callback `FUN_14054e340`."
new_next = "**Selected next line:** trace shared tag-0x49 list callback `FUN_14054e340`, now that the worker wrapper's callsite shows only the event pointer is explicitly forwarded to the dispatcher [EV-0620]; preserve unresolved virtual-call semantics."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0620/CL-L433/M-0173; bounded worker context; checkpointed FUN_14054e340")
