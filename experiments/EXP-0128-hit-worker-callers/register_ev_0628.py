from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T193952Z"
raw, err, mp = tuple(GH / f"{stem}.{ext}" for ext in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
expected_sha = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != expected_sha:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
text = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_140ebdf30 @ 140ebdf30",
    "DISASM=140ebdf51 CALL 0x140e84cf0",
    "DISASM=140ebdf56 LEA RAX, [0x1419e9078]",
    "DISASM=140ebdf5d MOV qword ptr [R14], RAX",
    "*param_1 = bhkWorldM::vftable;",
    "XREF_CALL_EDGE=1402c697f -> 140ebdf30 caller=FUN_1402c6810",
):
    if token not in text:
        raise SystemExit(f"vtable constructor result missing: {token}")

hashes = {f".local/ghidra/{path.name}": sha(path) for path in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0628",
    "source": "Identity-checked GOG disassembly/decompilation for FUN_140ebdf30 and its bhkWorldM vftable assignment",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0xebdf30 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_140ebdf30 first calls FUN_140e84cf0, then its disassembly loads address 0x1419e9078 into RAX and stores that pointer at [R14], which is the returned object's first field. The decompiler labels this address bhkWorldM::vftable. This constructor is called from FUN_1402c6810's param2=0 branch, while caller 50's global setter passes param2=0 [EV-0626], [EV-0627]. With GOG image base 0x140000000, the vtable RVA is 0x19e9078. The table RTTI and zero-based slot 0x35 (+0x1a8) target remain unverified and are the next discriminants.",
    "result": "The fallback constructor writes the bhkWorldM vftable pointer at VA 0x1419e9078 (RVA 0x19e9078) into the returned object. Caller 50's global fallback selects this constructor branch. Validate the table's RTTI and inspect slot 0x35 before assigning the virtual method or gameplay semantics.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0626", "EV-0627"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0628")
if old and old != item:
    raise SystemExit("EV-0628 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    file = ROOT / path
    current = file.read_text(encoding="utf-8")
    if marker not in current:
        file.write_text(current.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L441", "| CL-L441 | GOG FUN_140ebdf30 writes symbol-labeled bhkWorldM::vftable at VA 0x1419E9078 (RVA 0x19E9078) into the returned object; caller 50's global fallback selects this constructor. | supported for captured GOG constructor disassembly | [EV-0626]–[EV-0628] | RTTI and vtable slot 0x35 (+0x1a8) target remain unverified. |")
append_once("research/MECHANISMS.md", "## M-0181 — bhkWorldM fallback vtable is at GOG RVA 0x19e9078 (EV-0628)", "## M-0181 — bhkWorldM fallback vtable is at GOG RVA 0x19e9078 (EV-0628)\n\n`FUN_140ebdf30` writes vtable address `0x1419e9078` into the returned object after common initialization; GOG image base `0x140000000` gives RVA `0x19e9078` [EV-0628]. Caller 50's global fallback selects this constructor through `FUN_1402c6810(param2=0)` [EV-0626–EV-0627]. Validate the table RTTI and zero-based slot `0x35` for byte offset `+0x1a8`; method identity and gameplay effect remain unknown. Claim CL-L441.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 bhkWorldM vtable address (EV-0628)", "### Caller 50/62 bhkWorldM vtable address (EV-0628)\n\nConstructor `FUN_140ebdf30` stores `0x1419e9078` into the object vptr, giving GOG RVA `0x19e9078` [EV-0628]. Use the RTTI query on this table and read zero-based slot `0x35` for caller 50's `+0x1a8` method; do not transfer the RVA to Steam AE.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0628 recovers the GOG bhkWorldM vtable RVA", "EV-0628 recovers the bhkWorldM vtable pointer written by `FUN_140ebdf30`: GOG VA `0x1419e9078`, RVA `0x19e9078`. Validate RTTI and inspect slot `0x35` (+`0x1a8`) before adding method or gameplay edges [EV-0626–EV-0628].")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0628"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L441"]))
h = {
    "id": "Q79-H137",
    "model": "Caller 50's bhkWorldM fallback uses the GOG vtable at RVA 0x19e9078, whose zero-based slot 0x35 is the target of virtual byte offset +0x1a8.",
    "predicted_discriminant": "A read-only Ghidra vtable query on RVA 0x19e9078 identifies RTTI and slot 0x35 target; the target's direct graph/decompilation tests for HitData, armor protection or UseSkill edges.",
    "status": "proposed", "evidence": ["EV-0627", "EV-0628"]
}
prior = next((row for row in q["hypotheses"] if row.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H137")
next_action = "Query GOG vtable RVA 0x19e9078 for RTTI and zero-based slot 0x35 (+0x1a8); then trace the resolved method for direct HitData/armor-skill edges and compare producer argument shapes."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 bhkWorldM vtable RVA recovered; resolve RTTI and virtual +0x1a8 slot.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_top = "EV-0627 identifies the no-optional-object fallback as bhkWorldM. Its slot +0x1a8 remains unresolved and no HitData/armor edge is added."
new_top = "EV-0627 identifies the no-optional-object fallback as bhkWorldM; EV-0628 locates its GOG vtable at RVA 0x19E9078. Resolve slot +0x1a8 next; no HitData/armor edge is added yet."
if old_top in state:
    state = state.replace(old_top, new_top, 1)
old_next = "**Selected next line:** recover the `bhkWorldM` vtable RVA from its constructor and read slot `0x35` (+`0x1a8`) [EV-0627], then trace the target for a HitData/armor-skill connection."
new_next = "**Selected next line:** validate RTTI and read zero-based slot `0x35` (+`0x1a8`) at GOG vtable RVA `0x19e9078` [EV-0628], then trace the target for a HitData/armor-skill connection."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0628/CL-L441/M-0181; GOG bhkWorldM vtable RVA identified; checkpointed RTTI and slot query")
