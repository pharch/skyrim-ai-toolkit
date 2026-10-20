#!/usr/bin/env python3
"""Register exact ProcessTrapHit hkpConstraintInstance attachment provenance."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/".local/ghidra"; TX=ROOT/".local/alignment/transactions/TX-20261017-0011"; EXP=Path(__file__).resolve().parent
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
FRESH={
"20261018T080907Z":["DECOMPILATION_BEGIN=FUN_140e860d0","FUN_140b3a710(lVar1,param_2)","XREF_CALL_EDGE=140ecdc4e -> 140e860d0"],
"20261018T081009Z":["DECOMPILATION_BEGIN=FUN_140b3a710","FUN_140b43a20(param_1,param_2,1)","FUN_140b67200"],
"20261018T081116Z":["DECOMPILATION_BEGIN=FUN_140b43a20","CALLEE_DECOMPILATION_BEGIN=FUN_140b678a0","param_2[2] = lVar18","FUN_140b67200(param_2)"],
"20261018T081252Z":["XREF_CALL_COUNT=2","INCOMING_CALLER_FUNCTION_COUNT=2","caller=FUN_140b43a20","caller=FUN_140b439a0"],
}
REUSED={
"20261018T064133Z":["DECOMPILATION_BEGIN=FUN_140e95df0","FUN_140ef43b0","(*plVar9 + 0x148)"],
"20261018T064548Z":["DECOMPILATION_BEGIN=FUN_140ecdbe0","FUN_140e860d0(param_2,lVar1)"],
"20261018T065347Z":["DECOMPILATION_BEGIN=FUN_140e86bf0","FUN_140b3a830(lVar1,local_res8,param_2"],
"20261018T070646Z":["DECOMPILATION_BEGIN=FUN_140b48720","hkpConstraintInstance::vftable","param_1[8] = 0","*(undefined4 *)(param_1 + 9) = 0x80000000"],
"20261018T070746Z":["POINTER_TABLE_BASE_RVA=0x1973D58","POINTER_TABLE_ENTRY=index:0"],
"20261018T070840Z":["DECOMPILATION_BEGIN=FUN_140b37a30","return 0;"],
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def checked(stamp,markers):
 mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text(encoding="utf-8")); rp=ROOT/m["artifacts"]["stdout"]; c=m.get("checks",{})
 if not(m.get("analysis_distribution")=="GOG" and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BINARY and m.get("program_executable_path_matches_gog_binary") is True and m.get("exit_code")==0 and m.get("ok") is True and m.get("read_only") is True and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False and m.get("overwrite_attempted") is False and c.get("program_identity_matches_gog_binary") is True and c.get("script_no_error") is True and all(c.values()) and sha(rp)==m.get("stdout_sha256")): raise SystemExit(f"capture identity/completion check failed: {stamp}")
 raw=rp.read_text(errors="replace")
 if any(x not in raw for x in markers): raise SystemExit(f"capture marker missing: {stamp}")
 return m,mp,rp
def main():
 fresh={s:checked(s,ms) for s,ms in FRESH.items()}; reused={s:checked(s,ms) for s,ms in REUSED.items()}; note=TX/"EV-0360-note.md"; manifest=TX/"EV-0360-capture-manifest.json"
 write(note,f"""# EV-0360 — ProcessTrapHit constraint attach and entity membership

## Build and method

Four fresh identity-checked GOG AE 1.6.1179.0 queries used the configured existing project through the strict dispatcher in read-only/no-analysis mode. Six earlier captures from EV-0355/0356 are reused for factory, wrapper, and exact-vtable provenance. Analysis binary SHA-256: {BINARY}. These GOG RVAs do not transfer to Steam AE 1.6.1170.0.

## Direct observations

- On the captured ProcessTrapHit child traversal, FUN_140e95df0 creates a new bhk constraint wrapper through FUN_140ef43b0, appends it to the scene/body child list, then invokes the old child's slot +0x150 and the new wrapper's slot +0x148 [capture 20261018T064133Z; EV-0355].
- The new wrapper's FUN_140ecdbe0 slot +0x148 compares physics-state identity and, on a state change, calls FUN_140e860d0 with `param_1[2]` (the wrapper's stored hkpConstraintInstance at +0x10) [reused capture 20261018T064548Z]. The wrapper's +0x150 path also passes its stored hkp instance into FUN_140e86bf0; that helper selects FUN_140b3a830 in its non-queued branch [reused capture 20261018T065347Z; EV-0356].
- FUN_140e860d0 receives the selected physics state and exact hkp instance. In its immediate branch it requires the instance to be detached (`constraint+0x10 == 0`) and endpoint references to be ready, then calls FUN_140b3a710. In its queued branch it acquires and stores the same instance in the state's pending array [capture 20261018T080907Z].
- FUN_140b3a710 resolves/retains endpoint references, assigns the instance index, and calls FUN_140b43a20. The exact hkpConstraintInstance slot +0x30 returns zero [captures 20261018T081009Z, 20261018T070840Z].
- FUN_140b43a20 calls FUN_140b678a0, then the world-level add-listener pass FUN_140b4fa40 and exact constraint add-callback pass FUN_140b67200. FUN_140b678a0 copies selected endpoint +0x130 island pointer to constraint +0x10, inserts a 0x40-byte record into endpoint +0x100/+0x108, and repairs constraint +0x60 back-pointers for shifted entries. The matching entity serializer labels this per-entity collection `ConMstPtr` and its entries `ConInstance`/`ConData` [captures 20261018T081116Z, 20261018T080431Z].
- The constructor FUN_140b48720 installs the exact hkpConstraintInstance vtable and starts callback pointer +0x40 null with low count zero at +0x48. FUN_140b67200 dispatches any existing callback entries through slot +0x8, but this pass identifies no exact post-constructor callback-array writer. Its complete direct-reference census finds FUN_140b43a20 and FUN_140b439a0 as caller functions [captures 20261018T070646Z, 20261018T081252Z].
- No direct Actor::UseSkill or AV11/AV12 call appears in these mapped attach bodies. Callback entries and their class/targets remain unresolved; constructor-empty state alone does not prove they remain empty later.

## Competing models and result

- Q64-H1 predicts producer-backed add/remove callbacks and member finalizers stay outside AV11/AV12 skill progress.
- Q64-H2 predicts a concrete callback/member finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

The exact ProcessTrapHit-created hkpConstraintInstance is now linked to its entity's constraint collection and callback notification path. H1 is strengthened only for the resolved direct attach operations; Q64-H1/H2 remain proposed because callback-array writers, callback classes, later removal, and other indirect sites are unresolved.

## Scope and exact next action

This is static GOG evidence for the mapped construction/attach path. It does not establish that a callback remains absent at runtime, exact live collision damage/protection, raw AVSK change, or Steam behavior. Resolve producer-backed writes to constraint +0x40/+0x48 and the callback entries consumed through slot +0x8 on attach/+0x10 on removal. Then follow concrete listener/member targets to Actor::UseSkill AV11/AV12. Keep the exact Steam hit/armor/raw-AVSK discriminator open.
""")
 docs={
 "README.md":"# EXP-0098 — ProcessTrapHit constraint attach route\n\nTrace the exact factory-created hkpConstraintInstance through the ProcessTrapHit wrapper attach call into its owning entity's constraint collection and callback notifications.\n",
 "hypothesis.md":"# Competing models\n\n- Q64-H1: producer-backed attach/removal callbacks and member finalizers stay outside AV11/AV12 skill progress.\n- Q64-H2: a concrete callback/member descendant reaches Actor::UseSkill or mapped skill progress with AV11/AV12.\n\nThe exact instance-to-entity edge is now mapped; callback population and targets remain unknown.\n",
 "protocol.md":"# Protocol\n\nFollow ProcessTrapHit child creation through wrapper slots +0x148/+0x150, then require exact hkpConstraintInstance argument identity at attach/detach helpers. Resolve the entity list record and callback consumers; do not infer empty runtime callbacks from constructor state alone.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Confirm the factory-created hkp instance reaches the attach helper through an exact wrapper member.\n2. Map its entity-list record/back-pointer and callback dispatch phase.\n3. Find producer-backed +0x40/+0x48 writes and exact callback classes.\n4. Follow concrete listener/member methods to Actor::UseSkill and check AV11/AV12; unresolved callbacks remain inconclusive.\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- A producer-backed callback or member edge to AV11/AV12 supports Q64-H2.\n- Exact physics attach/removal and listener callbacks without a skill sink strengthen Q64-H1 only for those resolved targets.\n- Constructor-zero fields without complete later-writer coverage do not settle H1/H2.\n",
 "results.md":"# Results\n\nThe ProcessTrapHit-created hkpConstraintInstance reaches FUN_140e860d0 through the new wrapper's +0x148 path. Immediate attach calls FUN_140b3a710/FUN_140b43a20/FUN_140b678a0, which links the instance into the entity constraint array via +0x10 and +0x60 back-pointers; callback notification follows. Exact callback-array writers/listener types remain unresolved [EV-0360].\n",
 "implications.md":"# Implications\n\nThe same exact object is now present on the entity's constraint list, so the island/entity cleanup route from EV-0359 is a real reachable class path. The remaining discriminant is the concrete callback/member producer and target, not object membership.\n"}
 for n,b in docs.items(): write(EXP/n,b)
 captures={}
 for s,(m,_,_) in fresh.items(): captures[s]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")}
 for s,(m,_,_) in reused.items(): captures[s+"-reused"]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"requested_pointer_table_rva":m.get("requested_pointer_table_rva"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"source_evidence":"EV-0355/EV-0356"}
 hashes={}
 for m,mp,rp in [*fresh.values(),*reused.values()]:
  for p in [mp,rp,*(ROOT/x for x in m["artifacts"].values())]:
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
 for p in [note,*EXP.iterdir(),Path(__file__)]:
  if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
 manifest=TX/"EV-0360-capture-manifest.json"; hashes.pop(manifest.relative_to(ROOT).as_posix(),None)
 write(manifest,json.dumps({"evidence_id":"EV-0360","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"captures":captures,"registered_local_hashes":hashes},indent=2)); hashes[manifest.relative_to(ROOT).as_posix()]=sha(manifest)
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0360" for x in evidence["items"]): raise SystemExit("EV-0360 already registered")
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0360","kind":"native","source":"Identity-checked read-only GOG Ghidra traces of the ProcessTrapHit constraint wrapper attach path, hkp constraint registration, and entity-list insertion.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0360-note.md","sha256":sha(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],"coverage":"Exact factory hkpConstraintInstance argument flow through FUN_140e860d0/FUN_140b3a710/FUN_140b43a20/FUN_140b678a0, entity record insertion, and add-callback dispatch callers.","result":"The ProcessTrapHit-created hkpConstraintInstance reaches endpoint +0x100/+0x108. Constraint +0x10 receives endpoint +0x130; constraint +0x60 points back to its record. Callback writers/classes and AV11/AV12 descendants remain unresolved.","related_evidence":["EV-0355","EV-0356","EV-0358","EV-0359"],"local_hashes":hashes})
 write(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 cp=ROOT/"research/CLAIMS.md"; ct=cp.read_text(encoding="utf-8")
 if "| CL-L199 |" in ct: raise SystemExit("CL-L199 already registered")
 write(cp,ct.rstrip()+"\n| CL-L199 | In GOG AE 1.6.1179.0, the ProcessTrapHit-created hkpConstraintInstance reaches FUN_140e860d0 and immediate registration through FUN_140b3a710/FUN_140b43a20/FUN_140b678a0; it is linked into the selected entity's +0x100/+0x108 constraint collection by its +0x10 owner and +0x60 record back-pointer. | supported for the captured static factory/attach path | [EV-0360], [EV-0355], [EV-0356] | Exact runtime callback population, callback/member types, AV11/AV12 descendants, and Steam behavior remain unresolved. |")
 mp=ROOT/"research/MECHANISMS.md"
 write(mp,mp.read_text(encoding="utf-8").rstrip()+"\n\n## M-0080 — ProcessTrapHit hkp constraint attachment (Q-0064)\n\nThe ProcessTrapHit child factory creates a bhk constraint wrapper holding an hkpConstraintInstance. The wrapper's +0x148 path can call FUN_140e860d0 with that exact instance. In the immediate non-queued branch, FUN_140b3a710/FUN_140b43a20/FUN_140b678a0 attach it to the selected entity, read endpoint +0x130 into instance +0x10, insert a 0x40-byte record into endpoint +0x100/+0x108, and set the instance +0x60 record back-pointer. FUN_140b67200 then notifies existing add callbacks; the constructor begins with an empty callback array, but later writers/types are unresolved. No no-skill conclusion follows [EV-0360]. Claim CL-L199 -> M-0080.\n")
 gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
 write(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0360 establishes the exact ProcessTrapHit-created hkpConstraintInstance -> FUN_140e860d0 -> FUN_140b3a710/FUN_140b43a20/FUN_140b678a0 -> entity constraint-record edge. It also links attachment to the existing add-callback consumer, but no callback producer/target or AV11/AV12 edge is established [CL-L199].\n")
 rp=ROOT/"research/ROADMAP.md"
 write(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0360 ties the exact ProcessTrapHit hkpConstraintInstance to its entity constraint record and add-callback notification. Next resolve exact +0x40/+0x48 callback writers and callback entry classes; follow attach slot +0x8 and detach slot +0x10 targets plus member finalizers to AV11/AV12. Preserve the open Steam effective-protection/raw-AVSK experiment.\n")
 ix=ROOT/"experiments/README.md"
 write(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0098 / EV-0360 maps the ProcessTrapHit-created hkpConstraintInstance into its entity constraint record; callback producers and descendants remain unresolved.\n")
 fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in frontier["items"] if x.get("id")=="Q-0064")
 for bucket in [q.setdefault("evidence",[]),*(h.setdefault("evidence",[]) for h in q.get("hypotheses",[]))]:
  if "EV-0360" not in bucket: bucket.append("EV-0360")
 if "CL-L199" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L199")
 action="Resolve producer-backed writers to the exact hkpConstraintInstance +0x40/+0x48 callback array/count and identify callback entry classes. Trace attach slot +0x8 and removal slot +0x10 methods plus member finalizers to Actor::UseSkill AV11/AV12; retain the exact Steam positive-damage, effective-protection, and raw-AVSK discriminator."
 q["next_action"]=action; fp.write_text(json.dumps(frontier,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 checkpoint=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; src=checkpoint.read_text(encoding="utf-8")
 needle="- Q-0064 / EV-0359 separates a chain-instance cleanup override from potential island/entity and post-collision command carriers; exact factory-object membership remains unresolved.\n"
 addition="- Q-0064 / EV-0360 links the exact ProcessTrapHit-created hkpConstraintInstance to its entity +0x100/+0x108 constraint record and +0x60 back-pointer; attach callback dispatch follows but listener writers/classes remain unresolved.\n"
 if needle not in src: raise SystemExit("checkpoint helper lacks EV-0359 summary line")
 src=src.replace(needle,needle+addition).replace("trace exact factory-object membership in the island constraint collection or post-collision type-1 command records, then follow producer-backed callbacks/members against AV11/AV12.","resolve exact +0x40/+0x48 callback writers/classes and follow attach/remove callback and member descendants against AV11/AV12.")
 checkpoint.write_text(src,encoding="utf-8")
 print("registered EV-0360 / CL-L199 / M-0080; Q-0064 remains active")
if __name__=="__main__": main()
