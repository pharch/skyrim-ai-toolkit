from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T193633Z"
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
    "FUNCTION_LOOKUP=FUN_1402c6810 @ 1402c6810",
    "XREF_CALL_COUNT=2",
    "XREF_CALL_EDGE=1402c66bc -> 1402c6810 caller=FUN_1402c65b0",
    "if ((param_2 == 0) || ((*(byte *)(param_2 + 0x40) & 1) == 0))",
    "plVar5 = (longlong *)FUN_140ebdf30(lVar4,local_138,&local_148,&local_158);",
    "FUN_140ebdf30(undefined8 *param_1",
    "*param_1 = bhkWorldM::vftable;",
    "lVar4 = FUN_1402c6810(&local_30,0);",
):
    if token not in text:
        raise SystemExit(f"fallback object type path missing: {token}")

hashes = {f".local/ghidra/{path.name}": sha(path) for path in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0627",
    "source": "Identity-checked GOG FUN_1402c6810 fallback factory, both incoming callers, and constructors FUN_140e84cf0/FUN_140ebdf30",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x2c6810 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1402c6810 selects between two object-construction branches according to param2 and, when nonnull, byte[param2+0x40]&1. Its caller FUN_1402c65b0 passes param2=0, which selects the false branch and calls FUN_140ebdf30; that helper calls FUN_140e84cf0 and writes the symbol-labeled bhkWorldM::vftable into the object. FUN_1402c65b0 stores this result in the holder exposed by DAT_1420f9d28; the fallback resolver returns the holder's first qword [EV-0623], [EV-0626]. The other branch calls FUN_140e84cf0 directly and leaves its bhkWorld vftable. The factory has two analyzed direct callers: FUN_1402c65b0 and FUN_1402c1d80. The object class is therefore branch-dependent; the specific global fallback is bhkWorldM. The address of the bhkWorldM vtable, slot +0x1a8 target and caller-50 gameplay effect remain to be verified.",
    "result": "The global fallback built by FUN_1402c65b0 is a symbol-labeled bhkWorldM object: setter passes zero as factory param2, selecting FUN_140ebdf30, which delegates common initialization and installs bhkWorldM::vftable. A separate factory branch installs bhkWorld::vftable. Caller 50's unresolved virtual +0x1a8 is thus dispatched on the bhkWorldM fallback when the optional key-1 object is absent; no HitData/armor-skill edge is established.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0626", "EV-0625", "EV-0617", "EV-0619"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0627")
if old and old != item:
    raise SystemExit("EV-0627 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    file = ROOT / path
    current = file.read_text(encoding="utf-8")
    if marker not in current:
        file.write_text(current.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L440", "| CL-L440 | FUN_1402c65b0 passes zero to FUN_1402c6810, selecting FUN_140ebdf30, which installs the symbol-labeled bhkWorldM::vftable; this object is stored behind DAT_1420f9d28 and returned by the global fallback branch. | supported for captured GOG constructor/control-flow result | [EV-0623], [EV-0626], [EV-0627] | Vtable address, slot +0x1a8 target and gameplay effect remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0180 — Caller 50 global fallback constructs bhkWorldM (EV-0627)", "## M-0180 — Caller 50 global fallback constructs bhkWorldM (EV-0627)\n\n`FUN_1402c65b0` passes zero to factory `FUN_1402c6810`, selecting its false branch and constructor `FUN_140ebdf30`. That helper performs common `FUN_140e84cf0` initialization and installs `bhkWorldM::vftable` [EV-0626–EV-0627]. The fallback resolver returns the first qword stored in the global holder, so the missing optional key-1 object falls back to this bhkWorldM receiver [EV-0623], [EV-0627]. A separate branch constructs bhkWorld. The exact vtable address, slot `+0x1a8` target and gameplay effect remain open; no HitData/armor edge is established. Claim CL-L440.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 fallback receiver class (EV-0627)", "### Caller 50/62 fallback receiver class (EV-0627)\n\nThe fallback setter passes `0` into `FUN_1402c6810`, selecting its `FUN_140ebdf30` branch. The helper calls common `FUN_140e84cf0` initialization and installs the GOG symbol-labeled `bhkWorldM::vftable`; the other branch installs `bhkWorld::vftable` [EV-0626–EV-0627]. Since `FUN_1402b8b60` returns the first qword in the holder, the caller-50 fallback receiver is bhkWorldM when no optional key-1 object is present [EV-0623], [EV-0627]. Find its vtable address and query zero-based slot `0x35` (+`0x1a8`) before interpreting the method.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0627 identifies caller 50's fallback receiver as bhkWorldM", "EV-0627 ties caller 50's global fallback to the GOG symbol-labeled `bhkWorldM` class through the zero-argument factory branch and constructor vftable assignment. Its virtual slot `+0x1a8` remains unresolved; the class edge narrows dispatch context but adds no HitData/armor-skill edge [EV-0623], [EV-0626–EV-0627].")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0627"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L440"]))
h = {
    "id": "Q79-H136",
    "model": "Caller 50's global fallback receiver is a bhkWorldM object produced through FUN_1402c6810(param2=0), while the other factory branch constructs bhkWorld.",
    "predicted_discriminant": "The param2=0 branch calls FUN_140ebdf30, which installs bhkWorldM::vftable; query that vtable's address, RTTI and zero-based slot 0x35 to identify the +0x1a8 method.",
    "status": "supported", "evidence": ["EV-0623", "EV-0626", "EV-0627"]
}
prior = next((row for row in q["hypotheses"] if row.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H136")
next_action = "Query FUN_140ebdf30 and its instruction-level vftable relocation to recover the bhkWorldM vtable RVA; verify its RTTI and read zero-based slot 0x35 (+0x1a8), then trace that target for ordinary-hit/armor-skill sinks."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: global fallback receiver is bhkWorldM; recover its vtable and resolve +0x1a8.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_top = "EV-0626 traces the setter to a holder populated by FUN_1402c6810 from three adjacent global dwords. These routes add no HitData/armor edge."
new_top = "EV-0626 traces the setter to a holder populated by FUN_1402c6810 from three adjacent global dwords; EV-0627 identifies the no-optional-object fallback as bhkWorldM. Its slot +0x1a8 remains unresolved and no HitData/armor edge is added."
if old_top in state:
    state = state.replace(old_top, new_top, 1)
old_next = "**Selected next line:** trace `FUN_1402c6810`, which supplies the object stored in the global fallback holder [EV-0626], to identify its returned type before interpreting virtual `+0x1a8`; then map the clear path."
new_next = "**Selected next line:** recover the `bhkWorldM` vtable RVA from its constructor and read slot `0x35` (+`0x1a8`) [EV-0627], then trace the target for a HitData/armor-skill connection."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0627/CL-L440/M-0180; global fallback identified as bhkWorldM; checkpointed slot +0x1a8 resolution")
