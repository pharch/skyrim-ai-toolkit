#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
BIN="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPS={
 "20261018T103135Z":{"requested_rva":"0xB5D450"},
 "20261018T103413Z":{"requested_pointer_table_rva":"0x1975320","requested_pointer_count":16},
 "20261018T110645Z":{"requested_rva":"0xB5D5D0"},
 "20261018T110830Z":{"requested_rva":"0xB36980"},
}
MARKERS={
 "20261018T103135Z":["FUN_140b5d450","FUN_140f28cb0"],
 "20261018T103413Z":["value:0x140B5D5D0"],
 "20261018T110645Z":["FUN_140b439e0(lVar2,param_1);","FUN_140b67d60(param_2);"],
 "20261018T110830Z":["hkpConstraintChainInstance::vftable","FUN_140b487e0(param_1);","FUN_140b5d520();"],
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def append_once(p,mark,s):
 old=p.read_text(encoding="utf-8")
 if mark in old: raise SystemExit("duplicate append: "+mark)
 write(p,old.rstrip()+"\n\n"+s.strip())
def load(stamp,expected):
 mp=GH/f"gog-query-{stamp}.meta.json"
 m=json.loads(mp.read_text(encoding="utf-8"))
 out=ROOT/m["artifacts"]["stdout"]; checks=m.get("checks",{})
 valid=(m.get("operation")=="existing_gog_project_read_only_query"
  and m.get("analysis_distribution")=="GOG" and m.get("analysis_binary_product_version")=="1.6.1179"
  and m.get("analysis_binary_sha256")==BIN and m.get("program")=="SkyrimSE.exe"
  and m.get("program_executable_path_matches_gog_binary") is True and m.get("exit_code")==0 and m.get("ok") is True
  and m.get("read_only") is True and m.get("auto_analysis_disabled") is True
  and m.get("import_attempted") is False and m.get("overwrite_attempted") is False
  and m.get("project_created") is False and bool(checks) and all(checks.values())
  and out.is_file() and sha(out)==m.get("stdout_sha256")
  and all(m.get(k)==v for k,v in expected.items()))
 if not valid: raise SystemExit("capture identity/policy/request/hash failed: "+stamp)
 raw=out.read_text(encoding="utf-8",errors="replace")
 missing=[x for x in MARKERS.get(stamp,[]) if x not in raw]
 if missing: raise SystemExit(f"capture markers missing {stamp}: {missing}")
 return stamp,m,mp,out

def main():
 caps=[load(s,e) for s,e in CAPS.items()]
 ep=ROOT/"research/EVIDENCE.json"; ev=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0370" for x in ev["items"]): raise SystemExit("EV-0370 exists")
 cp=ROOT/"research/CLAIMS.md"
 note=TX/"EV-0370-note.md"
 write(note,f"""# EV-0370 — hkpConstraintChainInstance callback phases

## Build and method

Four identity-checked queries use the existing GOG AE 1.6.1179.0 project in read-only/no-analysis mode; analysis binary SHA-256 {BIN}. The chain-instance vtable and constructor captures are reused from EV-0366. Callback consumers are sourced from EV-0358 and EV-0367.

## Competing models

- H1: the exact chain-instance virtual routes can dispatch callback entries through the inherited hkpConstraintInstance callback array.
- H2: the chain-instance vtable routes away from that callback array.
- The exact vtable slot target, receiver argument to helper calls, and chain destructor's base-finalizer call discriminate these models. Callback entry types and skill sink reachability are separate questions.

## Direct observations

- The exact hkpConstraintChainInstance vtable at 0x141975320 maps slot index 4, byte offset +0x20, to FUN_140b5d5d0 [EV-0366; capture 20261018T103413Z].
- FUN_140b5d5d0 receives the chain instance as param_1, obtains its owning context through param_2+0x10, then calls FUN_140b439e0(context,param_1). FUN_140b439e0 calls FUN_140b67350(param_1) and FUN_140b67d60(param_1) [capture 20261018T110645Z].
- FUN_140b67350 consumes the +0x40/+0x48 array on its receiver, emits TtconRemCb, invokes each populated callback entry through virtual slot +0x10 with the instance, then compacts null entries [EV-0358]. Thus chain-instance slot +0x20 reaches the removal-callback consumer on the chain receiver.
- The exact chain-instance slot-0 target FUN_140b36980 calls FUN_140b5d520. That helper restores the hkpConstraintChainInstance vtable, releases chain-owned references/storage, then calls base finalizer FUN_140b487e0 [capture 20261018T110830Z]. EV-0367 maps that base finalizer to FUN_140b674a0, which dispatches populated entries through slot +0x18 and later frees the callback array.
- FUN_140b5d450 constructs the chain subtype by calling FUN_140b48a20, installing the chain vtable, initializing its own fields, retaining an associated object, and creating a chain action [EV-0366; capture 20261018T103135Z]. Its observed callers are a chain utility and wrapper factory FUN_140f28cb0; neither capture establishes a call from ProcessTrapHit.
- The fixed/malleable ProcessTrapHit factory path directly constructs ordinary hkpConstraintInstance through FUN_140ecdfc0 [EV-0365, EV-0366]. Do not equate the chain factory with that object without a caller path.

## Result and uncertainty

H1 is supported for the exact chain-instance virtual mechanics: removal reaches the inherited callback array through entry slot +0x10, and final deletion reaches the same array through entry slot +0x18. This does not establish that the ProcessTrapHit teardown owns this chain subtype, that callback entries are populated, or that either callback class reaches Actor::UseSkill AV11/AV12. Q64-H1/H2 remain unresolved globally.

## Exact next action

Query FUN_140f28cb0 with incoming-call census and owner context. Determine all callers and whether any path descends from ProcessTrapHit/FUN_140ef43b0. Its chain factory uses wrapper slots +0x128/+0x188, so compare its receiver and callsites against the fixed/malleable route before applying chain callback evidence to Q64.
""")
 docs={
 "README.md":"# EXP-0108 — hkpConstraintChainInstance callback phases\n\nTrace the exact chain vtable's removal and final-delete routes through the inherited callback array. ProcessTrapHit ownership remains a separate discriminant.\n",
 "hypothesis.md":"# Competing models\n\n- H1: exact chain-instance virtuals reach the inherited callback array.\n- H2: the chain-instance virtual routes avoid that array.\n\nCallback entry classes and AV11/AV12 descendants remain untested.\n",
 "protocol.md":"# Protocol\n\nUse exact chain vtable and constructor identities. Follow slot +0x20 and slot 0 with receiver arguments. Reuse already verified removal/deletion consumer captures, then trace the concrete chain factory's incoming callers before connecting it to ProcessTrapHit.\n",
 "expected-discriminants.md":"# Expected discriminants\n\nRemoval model predicts chain slot +0x20 reaches FUN_140b67350 and entry slot +0x10. Final deletion predicts slot 0 -> FUN_140b5d520 -> FUN_140b487e0 -> FUN_140b674a0 and entry slot +0x18. Neither path proves callback population or skill progress.\n",
 "results.md":"# Results\n\nThe hkpConstraintChainInstance slot +0x20 route reaches the inherited removal-callback consumer; slot 0 reaches the base deletion-callback consumer. The concrete chain factory's relation to ProcessTrapHit and the callback entry targets remain open. See EV-0370.\n",
 "implications.md":"# Implications\n\nThis maps two possible callback phases on the chain subtype. It does not establish that the ProcessTrapHit object is a chain instance or that any callback awards armor XP. Resolve the chain factory's incoming callers and the exact callback producer next.\n",
 }
 for n,s in docs.items(): write(EXP/n,s)
 mf=TX/"EV-0370-capture-manifest.json"; hashes={}; summaries=[]
 for stamp,m,mp,out in caps:
  hashes[mp.relative_to(ROOT).as_posix()]=sha(mp)
  for a in m.get("artifacts",{}).values():
   p=ROOT/a
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
  summaries.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
    "requested_pointer_table_rva":m.get("requested_pointer_table_rva"),"requested_pointer_count":m.get("requested_pointer_count"),
    "checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")})
 hashes[note.relative_to(ROOT).as_posix()]=sha(note); hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
 write(mf,json.dumps({"evidence_id":"EV-0370","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":summaries,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
 hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
  "id":"EV-0370","kind":"native","source":"Identity-checked read-only GOG Ghidra trace of hkpConstraintChainInstance removal and deletion callback phases.",
  "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0370-note.md","sha256":sha(note),
  "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
  "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
  "coverage":"Exact chain vtable slot +0x20 removal route and slot-0 finalizer through inherited hkpConstraintInstance callback consumers; chain factory caller scope remains unresolved.",
  "result":"Chain slot +0x20 reaches FUN_140b67350 and invokes populated callback entries through slot +0x10. Chain slot 0 reaches FUN_140b5d520 -> base FUN_140b487e0 -> FUN_140b674a0, invoking populated entries through slot +0x18. Entry classes, targets, population and ProcessTrapHit ownership remain unresolved.",
  "related_evidence":["EV-0358","EV-0365","EV-0366","EV-0367","EV-0369"],"local_hashes":hashes})
 write(ep,json.dumps(ev,indent=2,ensure_ascii=False))
 append_once(cp,"| CL-L210 |","| CL-L210 | In GOG AE 1.6.1179.0, the exact hkpConstraintChainInstance slot +0x20 route reaches the inherited +0x40/+0x48 removal callback consumer through entry slot +0x10, and slot-0 finalization reaches the base deletion callback consumer through entry slot +0x18. | supported for the mapped chain subtype paths | [EV-0370], [EV-0358], [EV-0367] | Callback population, concrete targets, ProcessTrapHit ownership and AV11/AV12 flow remain unresolved. |")
 append_once(ROOT/"research/MECHANISMS.md","## M-0089 — hkpConstraintChainInstance inherited callback phases","""## M-0089 — hkpConstraintChainInstance inherited callback phases

The chain subtype's slot +0x20 removal route reaches FUN_140b67350, which calls populated +0x40/+0x48 entries through entry slot +0x10. Its slot-0 finalizer calls FUN_140b5d520 -> base FUN_140b487e0 -> FUN_140b674a0, which uses entry slot +0x18 on the same inherited array. Callback producers, entry classes and ActorValue arguments remain unresolved. Claim CL-L210 -> M-0089 [EV-0370].""")
 append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-CHAIN-CALLBACK-ENTRY","""## C-OBJ2-Q64-CHAIN-CALLBACK-ENTRY — chain callback descendants

- **Model A:** a removal or deletion callback entry on the chain subtype reaches Actor::UseSkill with AV11/AV12.
- **Model B:** callback entries only perform constraint cleanup.
- **Evidence:** exact chain virtual routes reach entry slots +0x10 and +0x18 on the inherited array [EV-0370].
- **Assessment:** neither model is selected; callback entry class, target and arguments are unknown. ProcessTrapHit ownership of the chain object is also unproven.
- **Discriminant:** trace the chain factory's incoming callers, then identify exact callback writers and resolve both entry slots.""")
 append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0370 maps two chain-instance callback phases","EV-0370 maps two hkpConstraintChainInstance phases over its inherited callback array: removal slot +0x20 -> FUN_140b439e0 -> FUN_140b67350 -> entry slot +0x10; slot-0 finalization -> FUN_140b5d520 -> base FUN_140b487e0 -> FUN_140b674a0 -> entry slot +0x18. No callback producer, skill sink, or ProcessTrapHit owner edge is established [CL-L210], [M-0089].")
 fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
 if q.get("status")!="in_progress": raise SystemExit("Q-0064 inactive")
 if "EV-0370" not in q.setdefault("evidence",[]): q["evidence"].append("EV-0370")
 for h in q.get("hypotheses",[]):
  if "EV-0370" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0370")
 if "CL-L210" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L210")
 nxt="Query FUN_140f28cb0 with incoming-call census and owner context. Determine whether any caller descends from ProcessTrapHit/FUN_140ef43b0; compare its chain wrapper receiver and slots +0x128/+0x188 with the fixed/malleable factory before applying chain callback evidence to Q64."
 q["next_action"]=nxt; q.setdefault("methods",[]).append("EV-0370 maps removal and final-delete callback phases on hkpConstraintChainInstance, but requires an exact caller path before treating it as the ProcessTrapHit object.")
 write(fp,json.dumps(fr,indent=2,ensure_ascii=False))
 append_once(ROOT/"STATE.md","Q-0064 / EV-0370","- Q-0064 / EV-0370 maps both chain-subtype callback phases: slot +0x20 reaches inherited removal slot +0x10; slot 0 reaches base deletion slot +0x18. Callback entries and ProcessTrapHit ownership remain unresolved. Next query callers of FUN_140f28cb0.")
 append_once(ROOT/"ROADMAP.md","EV-0370 maps hkpConstraintChainInstance callback phases","EV-0370 maps chain-instance removal and final-delete callbacks through the inherited array; callback producers and ProcessTrapHit ownership remain open. Claim CL-L210 -> M-0089.")
 append_once(ROOT/"experiments/README.md","EXP-0108 / EV-0370","EXP-0108 / EV-0370 maps hkpConstraintChainInstance removal and final-delete callback phases; chain-factory ownership remains open.")
 print("Registered EV-0370 and CL-L210/M-0089; Q-0064 remains active on the chain factory caller boundary.")
if __name__=="__main__": main()

