from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T185349Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x658a80":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_140658a60 @ 140658a60",
    "local_88[0] = 0x45;",
    "OUTGOING_DIRECT_CALL_EDGE=140658a78 -> 14065b800",
    "XREF_CALL_EDGE=140774d53 -> 140658a60",
    "cVar8 = FUN_1406d4110()",
    "DVar10 = FUN_1401fa100(DAT_1420fd578,1)",
    "DVar10 = FUN_140658a60(DAT_14319a7c0)",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0609",
    "source": "Identity-checked GOG query of requested caller-48 RVA 0x658a80 (containing function FUN_140658a60), its sole producer and dispatcher case 0x45",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658a80 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "Requested RVA 0x658a80 resolves to containing Ghidra function FUN_140658a60 beginning at 0x658a60. It writes tag 0x45 and param_2 as one byte, then calls FUN_14065b800; one direct caller is FUN_140774b80. The matched dispatcher case 0x45 calls FUN_1401fa100(manager, payload byte). Caller FUN_140774b80 uses the same FUN_1406d4110 gate: gate clear calls FUN_1401fa100(DAT_1420fd578,1), gate set is decompiled as FUN_140658a60(DAT_14319a7c0) with its byte argument omitted. Caller register flow/payload equality are unresolved. Builder/caller/deferred helper bodies show no direct mapped HitData, protection, AV11/AV12 or UseSkill target; FUN_1401fa100 remains untraced.",
    "result": "Caller 48 is tag-0x45 with a byte payload and one process/thread-cleanup caller that selects queue versus immediate FUN_1401fa100 through the shared thread-state gate. The dispatcher returns to the same helper. This is a separate state/event route, not a tag-0x0B builder in the captured body. Exact deferred argument and helper descendants remain open; continue with FUN_1401fa100 before closing the caller.",
    "local_hashes": hashes, "related_evidence": ["EV-0608", "EV-0397", "EV-0574"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0609")
if old and old != item:
    raise SystemExit("EV-0609 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L422", "| CL-L422 | In GOG AE 1.6.1179.0, caller 48's requested RVA 0x658a80 resolves inside function FUN_140658a60, which builds tag 0x45 with a byte payload; its sole observed caller FUN_140774b80 selects a gated immediate FUN_1401fa100 or deferred builder route, and dispatcher case 0x45 calls FUN_1401fa100 with the byte. | supported for the captured builder/route | [EV-0609] | Deferred call arguments, FUN_1401fa100 descendants, ordinary runtime effect and Steam equivalence remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0162 — Caller 48 tag-0x45 byte event returns to a gated state helper (EV-0609)", "## M-0162 — Caller 48 tag-0x45 byte event returns to a gated state helper (EV-0609)\n\nThe builder at function start `FUN_140658a60` (requested caller-list address `0x658a80` is inside this function) queues tag `0x45` plus a byte. Its sole observed producer `FUN_140774b80` routes through `FUN_1406d4110`; the gate-clear branch calls `FUN_1401fa100(manager,1)`, while the deferred branch call's byte argument is omitted by decompilation. Dispatcher case `0x45` returns to `FUN_1401fa100` with the payload byte [EV-0609]. The producer register flow, helper descendants, and runtime effect remain open. No direct HitData/armor-skill edge is established. Claim CL-L422.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 48/62: tag-0x45 byte builder and gated producer (EV-0609)", "### Caller 48/62: tag-0x45 byte builder and gated producer (EV-0609)\n\nThe original listed RVA `0x658a80` falls inside `FUN_140658a60`, which writes tag `0x45` plus a byte. Its sole caller `FUN_140774b80` uses `FUN_1406d4110` to choose an immediate call to `FUN_1401fa100(manager,1)` or a queued call through the builder; case `0x45` routes back to `FUN_1401fa100` with the payload byte [EV-0609]. The deferred byte argument is omitted by decompilation and remains unresolved. No direct HitData/armor-skill target occurs in these captured bodies. Query FUN_1401fa100 and resolve the producer register path next.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0609 maps caller 48's tag-0x45 gate and return helper", "EV-0609 maps caller 48's containing function FUN_140658a60 as tag 0x45 with a byte payload. Its sole caller and dispatcher case route immediate/deferred work to FUN_1401fa100 through the shared thread-state gate. The deferred argument and helper effects remain open; no OBJ-1/OBJ-2 edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0609"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L422"]))
h = {"id": "Q79-H115", "model": "Caller 48 at requested RVA 0x658a80 is a tag-0x45 byte-event builder routed through the shared thread-state gate to FUN_1401fa100.", "predicted_discriminant": "Containing function FUN_140658a60 writes tag 0x45/byte, its sole caller FUN_140774b80 chooses immediate or queued route, and dispatcher case 0x45 calls FUN_1401fa100.", "status": "supported", "evidence": ["EV-0609"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H115")
h = {"id": "Q79-H116", "model": "Tag-0x45 immediate and deferred paths carry the same byte value into FUN_1401fa100.", "predicted_discriminant": "Producer disassembly passes byte 1 to the immediate helper and the same selector byte to the deferred builder; worker case 0x45 forwards that byte.", "status": "proposed", "evidence": ["EV-0609"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H116")
assessment = "EV-0609 records a separate tag-0x45 byte event with the same thread-state gate and a dispatcher return to FUN_1401fa100. The original requested RVA 0x658a80 is inside containing builder FUN_140658a60. No direct armor/HitData edge appears; exact queued-byte parity and the helper body remain next."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_1401fa100 with direct-call and incoming-caller coverage to resolve tag-0x45 gate-clear/deferred parity and screen the helper against mapped HitData/protection/AV11/AV12/UseSkill sinks. Then continue original worker caller 49/62 FUN_140658af0."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 48 is tag-0x45 byte-event builder FUN_140658a60 (requested RVA 0x658a80 lies inside); immediate/deferred routes target FUN_1401fa100, whose exact producer arguments remain unresolved.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** close caller 47/62 as bounded tag-0x44 keyed object-list lifecycle work [EV-0603–EV-0608], preserving unresolved virtual callbacks; then query caller 48/62 `FUN_140658a80` against the mapped HitData/protection/AV11/AV12/UseSkill route."
new = "**Selected next line:** query caller 48 helper `FUN_1401fa100` after the requested RVA `0x658a80` resolves inside tag-0x45 builder `FUN_140658a60` [EV-0609]; resolve the omitted deferred byte argument, then continue caller 49/62 `FUN_140658af0`."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0609/CL-L422/M-0162; caller 48 tag 0x45; checkpointed FUN_1401fa100")
