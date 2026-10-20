#!/usr/bin/env python3
"""Register exact-class lineage for callers of the hkp callback cleanup helper."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/".local/ghidra"; TX=ROOT/".local/alignment/transactions/TX-20261017-0011"; EXP=Path(__file__).resolve().parent
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
FRESH={
"20261018T075746Z":["XREF_CALL_COUNT=3","INCOMING_CALLER_FUNCTION_COUNT=3","XREF_CALL_EDGE=140b60e18 -> 140b439e0"],
"20261018T075850Z":["XREF_CALL_COUNT=0","XREF_ANY=141975340 -> 140b5d5d0"],
"20261018T080007Z":["POINTER_TABLE_BASE_RVA=0x1975338","POINTER_TABLE_ENTRY=index:1 address:141975340 value:0x140B5D5D0 target:140b5d5d0 function:FUN_140b5d5d0"],
"20261018T080106Z":["DISASM=140b60e14 MOV RCX, qword ptr [RCX + 0x10]","DISASM=140b60e18 JMP 0x140b439e0","XREF_CALL_COUNT=0"],
"20261018T080209Z":["DECOMPILATION_BEGIN=FUN_140f60440","CALLER_DECOMPILATION_BEGIN=FUN_140f48210","INCOMING_CALLER_DECOMPILATION_BEGIN=FUN_140f47800","LtNarrowPhase","StPostCollide"],
"20261018T080315Z":["POINTER_TABLE_BASE_RVA=0x1977590","POINTER_TABLE_ENTRY=index:1 address:141977598 value:0x140B60E10 target:140b60e10 function:FUN_140b60e10"],
"20261018T080431Z":["DECOMPILATION_BEGIN=FUN_140b60780","\"ConMstPtr\"","\"ConInstance\"","\"ConData\""],
}
REUSED={"20261018T073344Z":["DECOMPILATION_BEGIN=FUN_140b48a20","hkpConstraintChainInstance::vftable","FUN_140b5d450"]}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def checked(stamp,markers):
 mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text(encoding="utf-8")); rp=ROOT/m["artifacts"]["stdout"]; c=m.get("checks",{})
 if not(m.get("analysis_distribution")=="GOG" and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BINARY and m.get("program_executable_path_matches_gog_binary") is True and m.get("exit_code")==0 and m.get("ok") is True and m.get("read_only") is True and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False and m.get("overwrite_attempted") is False and c.get("program_identity_matches_gog_binary") is True and c.get("script_no_error") is True and all(c.values()) and sha(rp)==m.get("stdout_sha256")): raise SystemExit(f"capture identity/completion check failed: {stamp}")
 raw=rp.read_text(errors="replace")
 if any(x not in raw for x in markers): raise SystemExit(f"capture marker missing: {stamp}")
 return m,mp,rp
def main():
 fresh={s:checked(s,ms) for s,ms in FRESH.items()}; reused={s:checked(s,ms) for s,ms in REUSED.items()}; note=TX/"EV-0359-note.md"; manifest=TX/"EV-0359-capture-manifest.json"
 write(note,f"""# EV-0359 — hkp callback cleanup caller lineage

## Build and method

Seven fresh identity-checked queries used the configured GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. One prior constructor trace is reused from this transaction's local capture. Binary SHA-256: {BINARY}. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_140b439e0 has three direct caller functions in the analyzed GOG program: FUN_140b5d5d0, FUN_140f60440, and FUN_140b60e10 [capture 20261018T075746Z].
- FUN_140b5d5d0 is a function pointer at index 1 (+0x8) of the table at RVA 0x1975338. Its adjacent RTTI bytes decode to hkpConstraintChainInstance; the reused constructor trace shows FUN_140b5d450 installs that table after calling FUN_140b48a20 [captures 20261018T080007Z, 20261018T073344Z]. This chain-instance override is a different vtable from the factory-created hkpConstraintInstance table in EV-0356.
- FUN_140b60e10 is a function pointer at index 1 (+0x8) of the table at RVA 0x1977590. Adjacent RTTI bytes decode to hkpSimulationIslandAndEntity. The thunk loads its receiver's +0x10 into RCX and tail-jumps to FUN_140b439e0 while preserving other argument registers [captures 20261018T080315Z, 20261018T080106Z].
- FUN_140b60780 serializes that island/entity class's entity pointers and per-entity constraints under the label ConMstPtr; its entries are labeled ConInstance and ConData. This establishes a class-level constraint collection but not that the ProcessTrapHit-created instance occupies one of those entries [capture 20261018T080431Z].
- FUN_140f60440 interprets command records: type 0 routes to FUN_140f604b0; type 1 calls FUN_140b439e0 with the record's pointer. FUN_140f48210 calls it within a labeled LtNarrowPhase/StPostCollide path; FUN_140f47800 is its other direct caller. The selected pointer's class and identity remain data-dependent [capture 20261018T080209Z].
- The three caller bodies and mapped callees show physics list/constraint cleanup. No direct Actor::UseSkill/AV11/AV12 call is identified; the island collection or command record could still carry the factory-created instance, so no transitive negative is established.

## Competing models and result

- Q64-H1 predicts producer-backed callbacks/member finalizers stay outside AV11/AV12 skill progress.
- Q64-H2 predicts a concrete callback/member finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

The chain-instance caller is excluded as the exact factory vtable. The island/entity bridge and post-collision command queue remain potential carriers, with no producer-backed identity link to the factory-created instance. Q64-H1/H2 remain unresolved.

## Scope and exact next action

This result maps analyzed direct callers and class layouts only. It does not prove which runtime constraint enters an island collection/command queue, callback population, live protection/damage, raw AVSK, or Steam behavior. Trace whether the ProcessTrapHit-created constraint becomes a member of the hkpSimulationIslandAndEntity ConMstPtr records or a type-1 command record, beginning with FUN_140b3a830/FUN_140b43ab0/FUN_140b67d60 field transitions. Resolve producer-backed members/callbacks and screen concrete descendants for AV11/AV12.
""")
 docs={
 "README.md":"# EXP-0097 — hkp callback caller lineage\n\nSeparate exact hkpConstraintInstance callbacks from chain-instance, island/entity, and post-collision command routes that share the cleanup helper.\n",
 "hypothesis.md":"# Competing models\n\n- Q64-H1: producer-backed callback/member descendants stay outside AV11/AV12 skill progress.\n- Q64-H2: a concrete callback/member descendant reaches Actor::UseSkill or mapped skill progress with AV11/AV12.\n\nA caller class or command label alone is not an exact runtime object identity.\n",
 "protocol.md":"# Protocol\n\nEnumerate direct callers of FUN_140b439e0, bind vtable callers to exact table/RTTI/constructor evidence, trace command-loop argument sources, and compare only exact factory receiver lineage. Keep dynamic data-selected records unresolved.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Identify the exact receiver class at each direct caller from its table and constructor.\n2. Trace the factory-created constraint through FUN_140b3a830/FUN_140b43ab0/FUN_140b67d60 into any island collection or command record.\n3. Follow producer-backed callback/member targets to Actor::UseSkill and inspect AV11/AV12.\n4. A different class or data-selected pointer without membership provenance is inconclusive.\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- An exact factory-instance edge into a concrete callback/member target that reaches AV11/AV12 supports Q64-H2.\n- A producer-backed non-skill cleanup chain strengthens Q64-H1 only for that resolved route.\n- Chain-instance exclusion, generic owner collection, or an unresolved command pointer alone does not settle either model.\n",
 "results.md":"# Results\n\nDirect callers split into a chain-instance vtable override, an island/entity vtable bridge that owns constraint records, and a post-collision command loop with type-1 cleanup records. The exact factory-created instance is not identified among the island or queue records; Q64-H1/H2 remain open [EV-0359].\n",
 "implications.md":"# Implications\n\nThe shared helper has distinct producer routes. The chain subclass is excluded from the exact base factory object, while the island collection and post-collision command queue remain plausible carriers and require exact membership provenance.\n"}
 for n,b in docs.items(): write(EXP/n,b)
 captures={}
 for s,(m,_,_) in fresh.items(): captures[s]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"requested_pointer_table_rva":m.get("requested_pointer_table_rva"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")}
 for s,(m,_,_) in reused.items(): captures[s+"-reused-local"]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"source_evidence":"EV-0356/EV-0358 transaction-local capture"}
 hashes={}
 for m,mp,rp in [*fresh.values(),*reused.values()]:
  for p in [mp,rp,*(ROOT/x for x in m["artifacts"].values())]:
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
 for p in [note,*EXP.iterdir(),Path(__file__)]:
  if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
 hashes.pop(manifest.relative_to(ROOT).as_posix(),None)
 write(manifest,json.dumps({"evidence_id":"EV-0359","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"captures":captures,"registered_local_hashes":hashes},indent=2)); hashes[manifest.relative_to(ROOT).as_posix()]=sha(manifest)
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0359" for x in evidence["items"]): raise SystemExit("EV-0359 already registered")
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0359","kind":"native","source":"Identity-checked read-only GOG Ghidra traces of direct callback-cleanup callers, their vtables, constraint collection serialization, and collision command routing.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0359-note.md","sha256":sha(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],"coverage":"Direct callers of FUN_140b439e0, chain-instance/island-entity table identity, island constraint collection labels, and post-collision command type routing.","result":"The direct callers include a chain-instance override, an island/entity thunk, and post-collision type-1 command records. The exact factory-created hkpConstraintInstance is not identified in the island collection or command queue; Q64 remains unresolved.","related_evidence":["EV-0356","EV-0357","EV-0358","EV-0355"],"local_hashes":hashes})
 write(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 cp=ROOT/"research/CLAIMS.md"; ct=cp.read_text(encoding="utf-8")
 if "| CL-L198 |" in ct: raise SystemExit("CL-L198 already registered")
 write(cp,ct.rstrip()+"\n| CL-L198 | In GOG AE 1.6.1179.0, FUN_140b439e0 has three analyzed direct caller functions: an hkpConstraintChainInstance override, an hkpSimulationIslandAndEntity bridge, and a post-collision command-record loop. | supported for the mapped caller classes/records | [EV-0359], [EV-0358] | The factory-created hkpConstraintInstance is not tied to the island collection or type-1 record; runtime membership and callback/member descendants remain unresolved. |")
 mp=ROOT/"research/MECHANISMS.md"
 write(mp,mp.read_text(encoding="utf-8").rstrip()+"\n\n## M-0079 — shared constraint-cleanup callers (Q-0064)\n\nFUN_140b439e0 is called through three routes: hkpConstraintChainInstance slot +0x8, hkpSimulationIslandAndEntity slot +0x8, and a type-1 post-collision command record. The chain override is a different vtable from the ProcessTrapHit factory class. The island/entity serializer exposes a constraint collection, and the post-collision record carries a data-selected pointer; neither is yet tied to the exact factory object. No AV11/AV12 conclusion follows [EV-0359], [EV-0356]. Claim CL-L198 -> M-0079.\n")
 gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
 write(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0359 distinguishes the chain-instance cleanup override from the base hkpConstraintInstance factory class and identifies potential island/entity and command-queue carriers. It adds no causal edge to Actor::UseSkill AV11/AV12 or to the Dawnguard quest candidate until exact object membership is proven [CL-L194], [CL-L198].\n")
 rp=ROOT/"research/ROADMAP.md"
 write(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0359 splits FUN_140b439e0 callers by class/record route. Next trace whether the ProcessTrapHit-created hkpConstraintInstance enters the hkpSimulationIslandAndEntity ConMstPtr collection or a post-collision type-1 command record; then follow producer-backed callback/member descendants against AV11/AV12.\n")
 ix=ROOT/"experiments/README.md"
 write(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0097 / EV-0359 separates chain-instance cleanup from potential island/entity and post-collision command carriers; exact factory-object membership remains unresolved.\n")
 fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in frontier["items"] if x.get("id")=="Q-0064")
 for bucket in [q.setdefault("evidence",[]),*(h.setdefault("evidence",[]) for h in q.get("hypotheses",[]))]:
  if "EV-0359" not in bucket: bucket.append("EV-0359")
 if "CL-L198" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L198")
 action="Trace whether the ProcessTrapHit-created constraint becomes a member of the hkpSimulationIslandAndEntity ConMstPtr records or a type-1 command record, beginning with FUN_140b3a830/FUN_140b43ab0/FUN_140b67d60 field transitions. Resolve producer-backed members/callbacks and screen concrete descendants for AV11/AV12."
 q["next_action"]=action; fp.write_text(json.dumps(frontier,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 checkpoint=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; src=checkpoint.read_text(encoding="utf-8")
 needle="- Q-0064 / EV-0358 maps the hkpConstraintInstance callback-array consumer and its two direct caller functions; constructor starts empty and broad +0x40/+0x48 scans identify no exact callback producer.\n"
 addition="- Q-0064 / EV-0359 separates a chain-instance cleanup override from potential island/entity and post-collision command carriers; exact factory-object membership remains unresolved.\n"
 if needle not in src: raise SystemExit("checkpoint helper lacks EV-0358 summary line")
 src=src.replace(needle,needle+addition).replace("trace FUN_140b439e0 receiver lineage and resolve producer-backed callback/member writers before screening descendants for AV11/AV12.","trace exact factory-object membership in the island constraint collection or post-collision type-1 command records, then follow producer-backed callbacks/members against AV11/AV12.")
 checkpoint.write_text(src,encoding="utf-8")
 print("registered EV-0359 / CL-L198 / M-0079; Q-0064 remains active")
if __name__=="__main__": main()
