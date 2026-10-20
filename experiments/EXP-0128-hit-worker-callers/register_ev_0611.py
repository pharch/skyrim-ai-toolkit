from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T185825Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x774b80":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=140774d53 -> 140658a60",
    "OUTGOING_DIRECT_CALL_EDGE=140774d61 -> 1401fa100",
    "DISASM=140774d41 CALL 0x1406d4110",
    "DISASM=140774d46 MOV DL, 0x1",
    "DISASM=140774d53 CALL 0x140658a60",
    "DISASM=140774d61 CALL 0x1401fa100",
    "XREF_CALL_EDGE=140644046 -> 140774b80",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0611",
    "source": "Identity-checked GOG instruction/call-edge trace of caller-48 producer FUN_140774b80",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x774b80 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_140774b80 has 12 direct-call edges and two unresolved refcount-finalizer virtual calls; one direct caller is FUN_140643ec0. After clearing three manager arrays, it calls FUN_1406d4110. The instructions load MOV DL,1 before the gate branch; the gate-set branch calls FUN_140658a60(manager) with RDX still 1, while the gate-clear branch calls FUN_1401fa100(manager,1). Dispatcher case 0x45 also forwards the payload byte to FUN_1401fa100 [EV-0608]. This confirms immediate/deferred flag parity at value 1. The function's captured body is thread/manager collection release and state synchronization; it contains no direct HitData/protection/AV11/AV12/UseSkill target. Downstream dynamic object callbacks remain unresolved.",
    "result": "Caller 48 immediate and deferred routes use selector byte 1 and converge on the same flag-1 manager-list cleanup behavior. The event is generic thread/manager collection teardown with unresolved object virtuals, not a direct tag-0x0B/armor-skill path. Close caller 48 as bounded and continue caller 49/62 FUN_140658af0; do not treat this as a global negative.",
    "local_hashes": hashes, "related_evidence": ["EV-0610", "EV-0609", "EV-0608", "EV-0574", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0611")
if old and old != item:
    raise SystemExit("EV-0611 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L424", "| CL-L424 | In GOG AE 1.6.1179.0, caller FUN_140774b80 loads selector byte 1 before its FUN_1406d4110 gate; the immediate branch calls FUN_1401fa100(manager,1), and the deferred branch calls FUN_140658a60 with RDX still 1, matching dispatcher case 0x45's byte forwarding. | supported for captured callsite registers | [EV-0611], [EV-0608] | Dynamic object callbacks, runtime effect and Steam equivalence remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0164 — Tag-0x45 immediate/deferred selector parity confirmed (EV-0611)", "## M-0164 — Tag-0x45 immediate/deferred selector parity confirmed (EV-0611)\n\n`FUN_140774b80` loads `RDX=1` before testing `FUN_1406d4110`; the immediate branch calls `FUN_1401fa100(manager,1)`, while the queued branch calls `FUN_140658a60(manager)` with `RDX` still 1 [EV-0611]. The builder copies that byte and dispatcher case 0x45 forwards it to `FUN_1401fa100` [EV-0608], [EV-0609]. This confirms queue/direct parameter parity for the flag-1 manager-list cleanup path. The route has unresolved virtual callbacks but no direct HitData/armor-skill sink. No global negative or OBJ-1/OBJ-2 edge is added. Claim CL-L424.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 48/62 closure: tag-0x45 selector parity and manager cleanup (EV-0611)", "### Caller 48/62 closure: tag-0x45 selector parity and manager cleanup (EV-0611)\n\nProducer instructions set `RDX=1` before the thread-state gate. The direct branch calls `FUN_1401fa100(manager,1)`; the queued branch calls tag-0x45 builder `FUN_140658a60(manager)` with the byte still in `RDX`, and dispatcher case 0x45 forwards it back [EV-0608], [EV-0609], [EV-0611]. Immediate and deferred paths therefore converge on the same flag-1 manager-list cleanup. No direct mapped HitData/armor-skill edge occurs; two finalizer sites remain unresolved, so this is a bounded local result only. Continue caller 49/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0611 closes caller 48's deferred byte ambiguity", "EV-0611 confirms immediate and deferred caller-48 tag-0x45 paths both use selector byte 1 before reaching FUN_1401fa100. This closes the payload-parity ambiguity while leaving dynamic object callbacks open. No OBJ-1/OBJ-2 edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0611"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L424"]))
for hid in ("Q79-H115", "Q79-H116", "Q79-H117"):
    h = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if h:
        h["evidence"] = list(dict.fromkeys([*h.get("evidence", []), "EV-0611"]))
h = {"id": "Q79-H118", "model": "Caller 48 direct and queued branches both use tag-0x45 selector byte 1 and converge on FUN_1401fa100 flag-1 cleanup.", "predicted_discriminant": "FUN_140774b80 loads RDX=1 before the gate test; direct FUN_1401fa100 sees 1 and queued FUN_140658a60 receives the still-live RDX value, later forwarded by case 0x45.", "status": "supported", "evidence": ["EV-0608", "EV-0609", "EV-0611"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H118")
assessment = "EV-0611 resolves caller 48's queued byte: both the immediate and deferred tag-0x45 route pass selector 1 to FUN_1401fa100. This closes the local queue/direct mismatch; unresolved virtual cleanup prevents a whole-path negative."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Continue original worker caller 49/62 FUN_140658af0: query its direct/incoming call graph, exact tag/payload, producer provenance, dispatcher case and any mapped HitData/protection/AV11/AV12/UseSkill route."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 48/62 is bounded as tag-0x45 flag-1 manager-list cleanup; EV-0611 confirms exact queue/direct selector parity, while dynamic callbacks remain open.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 48 of 62 initially uninspected worker callers are reviewed, with 14 remaining. EV-0603–EV-0608 bound caller 47's tag-0x44 route to keyed object-list lifecycle work; EV-0609–EV-0610 map caller 48's tag-0x45 manager-list path, with its deferred byte register still to verify."
new = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 48 of 62 initially uninspected worker callers are reviewed, with 14 remaining. EV-0603–EV-0608 bound caller 47's tag-0x44 route to keyed object-list lifecycle work; EV-0609–EV-0611 bound caller 48's tag-0x45 manager-list cleanup with immediate/deferred selector parity, while dynamic callbacks remain open."
if old not in state:
    raise SystemExit("STATE active checkpoint summary not found")
state = state.replace(old, new, 1)
old_next = "**Selected next line:** inspect `FUN_140774b80` instructions to verify the byte argument to queued tag-0x45 builder `FUN_140658a60` [EV-0609/EV-0610]; then close caller 48 as bounded manager-list cleanup and continue caller 49/62 `FUN_140658af0`."
new_next = "**Selected next line:** continue caller 49/62 `FUN_140658af0` after caller 48's bounded tag-0x45 manager-list cleanup and parity result [EV-0609–EV-0611]; test its tag/payload and direct route against the mapped HitData/protection/AV11/AV12/UseSkill functions."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0611/CL-L424/M-0164; caller 48 bounded; checkpointed caller 49")
