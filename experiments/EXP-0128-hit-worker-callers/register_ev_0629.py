from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T194200Z"
raw, err, mp = tuple(GH / f"{stem}.{ext}" for ext in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
expected_sha = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != expected_sha:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
text = raw.read_text(encoding="utf-8", errors="replace")
for token in ("VTABLE_RTTI_TABLE_RVA=0x19E9078", "VTABLE_RTTI_SIGNATURE=0x1", "VTABLE_RTTI_SUBOBJECT_OFFSET=0/0x0", "VTABLE_RTTI_TYPE_DESCRIPTOR_RVA=0x20CA2C0", "VTABLE_RTTI_TYPE_NAME=.?AVbhkWorldM@@", "VTABLE_RTTI_CENSUS_COMPLETE=true"):
    if token not in text:
        raise SystemExit(f"RTTI result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE", "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only RTTI census, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0629",
    "source": "Identity-checked GOG MSVC Complete Object Locator and type descriptor for vtable RVA 0x19e9078",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --vtable-rtti-rvas 0x19e9078 --timeout 600"],
    "coverage": "Ghidra's MSVC RTTI census identifies the table at GOG RVA 0x19e9078 with signature 1, subobject offset 0, Complete Object Locator VA 0x141bc69c0, and type descriptor RVA 0x20ca2c0 naming .?AVbhkWorldM@@. This independently confirms the constructor vptr label from EV-0628 and the fallback type from EV-0627. The virtual +0x1a8 target remains to be read in a separate slot-only query.",
    "result": "The global fallback's vtable is primary bhkWorldM RTTI at GOG RVA 0x19e9078, subobject offset zero. The class identity is now independently verified by RTTI; slot 0x35 (+0x1a8) remains unresolved.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0627", "EV-0628"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0629")
if old and old != item: raise SystemExit("EV-0629 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def append_once(path, marker, value):
    p = ROOT / path; s = p.read_text(encoding="utf-8")
    if marker not in s: p.write_text(s.rstrip()+"\n\n"+value.rstrip()+"\n", encoding="utf-8")
append_once("research/CLAIMS.md", "CL-L442", "| CL-L442 | GOG vtable RVA 0x19E9078 has primary MSVC RTTI type .?AVbhkWorldM@@ with subobject offset zero. | supported for captured RTTI census | [EV-0628], [EV-0629] | Slot 0x35 (+0x1a8) target and gameplay behavior remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0182 — RTTI confirms caller 50 fallback vtable as primary bhkWorldM (EV-0629)", "## M-0182 — RTTI confirms caller 50 fallback vtable as primary bhkWorldM (EV-0629)\n\nThe table at GOG RVA `0x19e9078` has MSVC type descriptor `.?AVbhkWorldM@@`, signature 1, and subobject offset zero [EV-0629]. This validates the constructor label and identifies a primary bhkWorldM fallback receiver [EV-0627–EV-0629]. Its byte-offset `+0x1a8` slot remains unresolved; no HitData or armor-skill edge is established. Claim CL-L442.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 fallback receiver RTTI (EV-0629)", "### Caller 50/62 fallback receiver RTTI (EV-0629)\n\nThe table at GOG RVA `0x19e9078` is primary MSVC RTTI type `.?AVbhkWorldM@@`, signature 1, subobject offset zero [EV-0629]. The constructor-symbol inference is now independently confirmed. Read vtable slot `0x35` (+`0x1a8`) next.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0629 validates caller 50 fallback receiver RTTI", "EV-0629 validates GOG vtable RVA `0x19e9078` as primary `.?AVbhkWorldM@@` RTTI at subobject offset zero. Caller 50's fallback class is supported; its slot `0x35` (+`0x1a8`) and gameplay effect remain open [EV-0627–EV-0629].")
fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8")); q = next(r for r in fr["items"] if r.get("id")=="Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0629"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L442"]))
h = {"id":"Q79-H138", "model":"The global fallback receiver's GOG table at RVA 0x19e9078 is primary bhkWorldM RTTI with subobject offset zero.", "predicted_discriminant":"The RTTI census should identify .?AVbhkWorldM@@ at table RVA 0x19e9078 and report offset zero; slot 0x35 must still be resolved separately.", "status":"supported", "evidence":["EV-0628","EV-0629"]}
prior=next((r for r in q["hypotheses"] if r.get("id")==h["id"]),None)
if prior is None: q["hypotheses"].append(h)
elif prior != h: raise SystemExit("hypothesis collision: Q79-H138")
next_action="Run a slot-only query on GOG vtable RVA 0x19e9078 for zero-based slot 0x35 (+0x1a8); trace the resulting function for direct HitData/protection/AV11/AV12/UseSkill sinks and compare its caller arguments."
q["next_action"]=next_action; fr["next_action"]=next_action; fr["session_next_action"]=next_action
now=datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"]={"timestamp_utc":now,"task":"Q-0079/TX-20261018-0013: primary bhkWorldM RTTI confirmed; resolve slot +0x1a8.","next_action":next_action}
fr["last_session_checkpoint"]={"recorded_utc":now,"next_action":next_action,"active_process":"TX-20261018-0013"}
fp.write_text(json.dumps(fr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sp=ROOT/"STATE.md"; state=sp.read_text(encoding="utf-8")
old="**Selected next line:** query RTTI separately for the GOG vtable at RVA `0x19e9078`, then read slot `0x35` (+`0x1a8`) in a second query [EV-0628]; the Ghidra adapter does not combine those modes."
new="**Selected next line:** read GOG bhkWorldM vtable slot `0x35` (+`0x1a8`) at RVA `0x19e9078`; RTTI confirms primary type `.?AVbhkWorldM@@` at offset zero [EV-0629]."
if old not in state: raise SystemExit("STATE selected-next checkpoint not found")
state=state.replace(old,new,1)
oldtop="EV-0628 locates its GOG vtable at RVA 0x19E9078. Resolve slot +0x1A8 next; no HitData/armor edge is added yet."
newtop="EV-0628 locates its GOG vtable at RVA 0x19E9078 and EV-0629 validates primary RTTI .?AVbhkWorldM@@ at offset zero. Resolve slot +0x1A8 next; no HitData/armor edge is added yet."
if oldtop in state: state=state.replace(oldtop,newtop,1)
sp.write_text(state,encoding="utf-8")
print("registered EV-0629/CL-L442/M-0182; primary bhkWorldM RTTI verified; checkpointed slot 0x35")
