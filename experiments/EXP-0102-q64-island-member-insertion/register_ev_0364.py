#!/usr/bin/env python3
"""Register island-owner evidence and correct EV-0360's +0x10 interpretation."""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
EXP98=ROOT/"experiments/EXP-0098-q64-hkp-constraint-attach-route"
BIN="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
S={
"20261018T084404Z":("0xB678A0",None,["TARGET_RVA=0xB678A0","lVar18 = *(longlong *)(uVar5 + 0x130);","param_2[2] = lVar18;","plVar2 = (longlong *)(uVar5 + 0x100);","*(longlong **)(*plVar12 + 0x60) = plVar12"]),
"20261018T084504Z":(None,"EntityPtrs",["STRING_QUERY=EntityPtrs","STRING_REFERENCE=140b607c1 -> 1419775c8 type=DATA function=FUN_140b60780","STRING_REFERENCE_COUNT=1"]),
"20261018T084600Z":("0xB43F40",None,["TARGET_RVA=0xB43F40","FUN_140b43f90(param_1,*(undefined8 *)(param_2 + 0x130),*(undefined8 *)(param_3 + 0x130));","*(undefined8 **)(*(longlong *)(uVar20 + param_3[0xc]) + 0x130) = puVar12;","*(int *)(param_1 + 0x68) = *(int *)(param_1 + 0x68) + 1;"]),
"20261018T085103Z":("0xB44470",None,["TARGET_RVA=0xB44470","DECOMPILATION_BEGIN=FUN_140b44470","*(longlong *)(lVar21 + 0x130) = lVar22;"]),
"20261018T085242Z":("0xB60B10",None,["TARGET_RVA=0xB60B10","*param_1 = hkpSimulationIsland::vftable;","MOV qword ptr [RCX + 0x60], RAX","MOV dword ptr [RCX + 0x68], R8D"])}
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def W(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def check(stamp,spec):
 mpath=GH/("gog-query-"+stamp+".meta.json"); m=json.loads(mpath.read_text(encoding="utf-8"))
 rawpath=ROOT/m["artifacts"]["stdout"]; raw=rawpath.read_text(encoding="utf-8",errors="replace"); c=m.get("checks",{})
 ok=(m.get("analysis_distribution")=="GOG" and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BIN and m.get("requested_rva")==spec[0] and m.get("requested_string")==spec[1] and m.get("exit_code")==0 and m.get("ok") is True and m.get("read_only") is True and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False and m.get("overwrite_attempted") is False and c.get("program_identity_matches_gog_binary") is True and c.get("script_no_error") is True and all(c.values()) and H(rawpath)==m.get("stdout_sha256"))
 missing=[x for x in spec[2] if x not in raw]
 if not ok or missing: raise SystemExit(f"bad capture {stamp}; missing={missing}")
 return m,mpath,rawpath
def main():
 caps={t:check(t,spec) for t,spec in S.items()}
 ep=ROOT/"research/EVIDENCE.json"; ev=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0364" for x in ev["items"]): raise SystemExit("EV-0364 already registered")
 n360=TX/"EV-0360-note.md"; old="FUN_140b678a0 sets constraint +0x10 to the selected entity and inserts its 0x40-byte record into entity +0x100/+0x108; insertion updates constraint +0x60 back-pointers for shifted records."
 new="FUN_140b678a0 reads the selected endpoint's +0x130 island pointer into constraint +0x10, and separately inserts a 0x40-byte record into endpoint +0x100/+0x108. Constraint +0x60 record back-pointers are updated when records shift."
 note=n360.read_text(encoding="utf-8")
 if old in note: note=note.replace(old,new)
 elif new not in note: raise SystemExit("EV-0360 old field statement missing")
 if "Field-semantics correction from EV-0364" not in note:
  note+="""\n\n## Field-semantics correction from EV-0364\n\nThe earlier statement that constraint +0x10 was the selected endpoint pointer was incorrect. FUN_140b678a0 reads selected endpoint +0x130 into constraint +0x10. Endpoint +0x100/+0x108 and constraint +0x60 are separate record relations. Typed island initialization, EntityPtrs serialization, endpoint insertion and merge identify +0x130 structurally with hkpSimulationIsland [EV-0364]. Exact Steam runtime pointer and hit outcome remain unobserved.\n"""
 W(n360,note)

 r98=EXP98/"results.md"
 W(r98,"""# Results\n\nThe ProcessTrapHit-created hkpConstraintInstance reaches FUN_140e860d0 through wrapper +0x148. Immediate attachment calls FUN_140b3a710/FUN_140b43a20/FUN_140b678a0. The attach function copies selected endpoint +0x130 island pointer to constraint +0x10, inserts a 0x40-byte record into endpoint +0x100/+0x108, and maintains constraint +0x60 as the record back-pointer. Add-callback notification follows [EV-0360, EV-0364].\n\nIsland initialization, serialization, insertion and merge use a consistent hkpSimulationIsland/EntityPtrs/+0x130 layout. This corrects the prior owner-field description; live membership and callback population remain unobserved. Broad writer scans remain output-capped [EV-0363, EV-0364].\n""")
 regp=EXP98/"register_ev_0360.py"; reg=regp.read_text(encoding="utf-8")
 reg=reg.replace(old,"FUN_140b678a0 copies selected endpoint +0x130 island pointer to constraint +0x10, inserts a 0x40-byte record into endpoint +0x100/+0x108, and repairs constraint +0x60 back-pointers for shifted entries.")
 reg=reg.replace("The ProcessTrapHit-created hkpConstraintInstance is inserted into its selected entity constraint collection and linked by +0x10/+0x60. Add-callback notification follows but exact callback writers/classes remain unresolved; no AV11/AV12 sink appears in mapped direct bodies.","The ProcessTrapHit-created hkpConstraintInstance reaches endpoint +0x100/+0x108. Constraint +0x10 receives endpoint +0x130; constraint +0x60 points back to its record. Callback writers/classes and AV11/AV12 descendants remain unresolved.")
 reg=reg.replace("set instance +0x10 to that entity, insert a 0x40-byte record into entity +0x100/+0x108","read endpoint +0x130 into instance +0x10, insert a 0x40-byte record into endpoint +0x100/+0x108")
 W(regp,reg)

 docs={
 "results.md":"# Results\n\nThe exact ProcessTrapHit attach function reads endpoint +0x130 into hkpConstraintInstance +0x10. Separately it inserts a 0x40-byte record into endpoint +0x100/+0x108 and updates constraint +0x60 back-pointers [EV-0360, capture 20261018T084404Z].\n\nThe hkpSimulationIsland initializer sets up +0x60/+0x68; FUN_140b44470 appends endpoint pointers and writes endpoint +0x130 back-pointers; FUN_140b43f90 merges member arrays, rewrites moved endpoint +0x130 and updates member constraints +0x10 to the receiving island [EV-0362, EV-0364]. Exact live endpoint membership remains unobserved; the static owner model is strongly supported. Capped writer scans provide no negative [EV-0363]. No AV11/AV12 or live Steam hit/protection/raw-AVSK conclusion follows.\n",
 "hypothesis.md":"# Competing models\n\n- H1: endpoint +0x130 is its hkpSimulationIsland pointer; island +0x60/+0x68 EntityPtrs stores endpoints, and endpoint +0x100/+0x108 stores constraint records.\n- H2: matching offsets and serializer labels belong to different owner paths, so endpoint +0x130 does not identify the island used by EntityPtrs.\n\nExact attach read/assignment, typed initialization, serializer, insertion and merge discriminate H1/H2. Live ProcessTrapHit identity and AV11/AV12 remain separate.\n",
 "protocol.md":"# Protocol\n\nValidate identity-checked GOG captures. Trace exact attach endpoint +0x130 to constraint +0x10 separately from endpoint +0x100/+0x108 and constraint +0x60 record relations. Cross-check typed island initialization, EntityPtrs serialization, insertion and merge. Preserve EV-0360 correction history and leave live membership unknown without a live capture. Keep the Steam positive-damage/effective-protection/raw-AVSK discriminator open.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Attach reads endpoint +0x130 into constraint +0x10.\n2. EntityPtrs serializer traverses island +0x60/+0x68 and each endpoint's +0x100/+0x108 records.\n3. Insertion writes endpoint +0x130 to island and appends endpoint to EntityPtrs.\n4. Merge moves endpoints and repairs endpoint +0x130 plus constraint +0x10.\n5. Matching offsets alone leave live ProcessTrapHit membership unobserved.\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- Typed initialization, serializer labels and insertion/merge def-use support H1.\n- A different owner type or inconsistent receiver lineage supports H2.\n- Static owner mapping does not establish Steam hit damage, protection or armor XP.\n",
 "implications.md":"# Implications\n\nThe static +0x130 owner interpretation is strongly supported as an hkpSimulationIsland pointer. Constraint +0x10 stores the island pointer; endpoint +0x100/+0x108 stores constraint records; constraint +0x60 points back. Live endpoint membership remains unobserved. OBJ-2 only; no causal edge to OBJ-1.\n"}
 for name,body in docs.items(): W(EXP/name,body)

 cp=ROOT/"research/CLAIMS.md"; claims=cp.read_text(encoding="utf-8")
 row=next(x for x in claims.splitlines() if x.startswith("| CL-L199 |"))
 claims=claims.replace(row,"| CL-L199 | In GOG AE 1.6.1179.0, the ProcessTrapHit-created hkpConstraintInstance reaches FUN_140e860d0 and immediate registration through FUN_140b3a710/FUN_140b43a20/FUN_140b678a0; constraint +0x10 receives endpoint +0x130, while endpoint +0x100/+0x108 stores its constraint record and constraint +0x60 points back. | supported for captured static path | [EV-0360], [EV-0364], [EV-0355], [EV-0356] | Exact live membership, callback population/types, AV11/AV12 descendants and Steam hit behavior remain unresolved. |")
 if "| CL-L203 |" in claims: raise SystemExit("CL-L203 already exists")
 claims+="\n| CL-L203 | GOG hkpSimulationIsland EntityPtrs initialization, serialization, endpoint insertion and merge use island +0x60/+0x68, endpoint +0x130 back-pointers and endpoint +0x100/+0x108 constraint records; merge updates moved endpoints and their constraints' +0x10 island pointers. | supported for mapped static paths | [EV-0362], [EV-0364] | Exact ProcessTrapHit live membership and AV11/AV12 remain unresolved. |\n| CL-L204 | GOG FUN_140b678a0 assigns endpoint +0x130 to constraint +0x10 and separately inserts the constraint record into endpoint +0x100/+0x108 while maintaining instance +0x60 as record back-pointer. | supported for exact static attach function | [EV-0360], [EV-0364] | Runtime pointer value and callback/member AV11/AV12 reachability remain unresolved. |\n"
 W(cp,claims)

 mp=ROOT/"research/MECHANISMS.md"; mech=mp.read_text(encoding="utf-8")
 oldm="set instance +0x10 to that entity, insert a 0x40-byte record into entity +0x100/+0x108"
 if oldm in mech: mech=mech.replace(oldm,"read endpoint +0x130 into instance +0x10, separately insert a 0x40-byte record into endpoint +0x100/+0x108")
 oldtail="No no-skill conclusion follows [EV-0360]. Claim CL-L199 -> M-0080."
 mech=mech.replace(oldtail,"No no-skill conclusion follows [EV-0360], [EV-0364]. Claim CL-L199 -> M-0080.")
 if "## M-0083" in mech: raise SystemExit("M-0083 exists")
 mech+="""\n\n## M-0083 — hkpSimulationIsland EntityPtrs ownership and merge (Q-0064)\n\nFUN_140b60b10 installs hkpSimulationIsland::vftable and initializes island +0x60 EntityPtrs storage and +0x68 count. FUN_140b60780 serializes this array and each endpoint's +0x100/+0x108 records. FUN_140b44470 appends endpoint pointers, writes endpoint +0x130 to island, and stores its member index at +0xfc. FUN_140b43f90 merges arrays, rewrites moved endpoint +0x130, and updates endpoint constraints +0x10. The static model is supported; exact live membership and AV11/AV12 remain unknown [EV-0362], [EV-0364]. Claim CL-L203 -> M-0083.\n"""
 W(mp,mech)

 cont=ROOT/"research/CONTRADICTIONS.md"; con=cont.read_text(encoding="utf-8")
 if "C-OBJ2-Q64-CONSTRAINT-OWNER-FIELD" in con: raise SystemExit("owner contradiction exists")
 con+="""\n\n## C-OBJ2-Q64-CONSTRAINT-OWNER-FIELD — constraint +0x10 versus endpoint +0x130 and record fields\n\n- **Model A:** constraint +0x10 points to selected endpoint/entity owning its +0x100/+0x108 record.\n- **Model B:** constraint +0x10 receives endpoint +0x130; endpoint +0x100/+0x108 and instance +0x60 are separate record relations.\n- **Source:** exact attach body [EV-0360], typed island initializer, endpoint insertion, EntityPtrs serializer reference and merge body [EV-0364], with type/serializer context [EV-0362].\n- **Current assessment:** Model B is supported for mapped static code. Island initialization/serialization match +0x60/+0x68 EntityPtrs; insertion writes endpoint +0x130; merge repairs endpoint +0x130 and constraint +0x10. EV-0360's earlier description is corrected. Live membership, callback population and AV11/AV12 remain unknown.\n- **Discriminant:** capture exact endpoint/constraint identities during verified Steam positive damage and effective protection; measure raw AVSK. Static GOG RVAs do not substitute for runtime observation.\n"""
 W(cont,con)
 kg=ROOT/"research/KNOWLEDGE_GRAPH.md"; graph=kg.read_text(encoding="utf-8")
 graph+="""\n\nEV-0364 corrects EV-0360: constraint +0x10 copies endpoint +0x130; endpoint +0x100/+0x108 stores records, with instance +0x60 pointing back. Typed island initialization, EntityPtrs serialization, insertion and merge support this owner relation [CL-L203], [CL-L204], [M-0083]. Live membership and AV11/AV12 are unresolved. No causal edge to OBJ-1 is supported.\n"""
 W(kg,graph)

 ix=ROOT/"experiments/README.md"; W(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0102 / EV-0364 maps hkpSimulationIsland EntityPtrs insertion/merge and corrects EV-0360's constraint +0x10 interpretation. Live membership and AV11/AV12 remain open.\n")
 road=ROOT/"ROADMAP.md"; W(road,road.read_text(encoding="utf-8").rstrip()+"\n\n## Q-0064 update — 2026-10-18\n\nEV-0364 corrects attachment: constraint +0x10 receives endpoint +0x130, endpoint +0x100/+0x108 stores records, and constraint +0x60 points back. Typed island initialization, EntityPtrs serialization, insertion and merge support hkpSimulationIsland ownership. Continue with callback +0x40/+0x48 producers and concrete callback/member descendants; keep Steam positive-damage/effective-protection/raw-AVSK testing open. OBJ-2 evidence only; no edge to OBJ-1.\n")
 statep=ROOT/"STATE.md"; state=statep.read_text(encoding="utf-8")
 bullet="- Q-0064 / EV-0363 withdraws the EV-0362 +0x60/+0x68 writer negative: both broad scans printed only the first 2,048 accesses and stopped before 0x140b."
 state=state.replace(bullet,bullet+"\n- Q-0064 / EV-0364 corrects the constraint owner field: instance +0x10 receives endpoint +0x130; endpoint +0x100/+0x108 stores its record and instance +0x60 points back. Island initialization, EntityPtrs serialization, insertion and merge support the owner model; live membership and AV11/AV12 remain unresolved.")
 active="TX-20261017-0011 / Q-0064 tests whether any teardown indirect call reaches AV11/AV12. EV-0364 supports the hkpSimulationIsland owner model and corrects EV-0360. Next action: trace exact constraint +0x40/+0x48 callback writers and entry classes; follow attach slot +0x8/removal slot +0x10 and member finalizers to Actor::UseSkill AV11/AV12. Preserve Steam positive-damage/effective-protection/raw-AVSK discriminator; query existing GOG AE 1.6.1179.0 project read-only and keep GOG/Steam addresses separate."
 state=re.sub(r"(?m)^.*TX-20261017-0011.*$",active,state,count=1)
 W(statep,state)

 m360=TX/"EV-0360-capture-manifest.json"; j=json.loads(m360.read_text(encoding="utf-8")); h=j.setdefault("registered_local_hashes",{})
 regp=EXP98/"register_ev_0360.py"
 for p in [n360,r98,regp]: h[p.relative_to(ROOT).as_posix()]=H(p)
 j["field_semantics_correction"]={"recorded_by":"EV-0364","prior":"constraint +0x10 was endpoint","correct":"constraint +0x10 receives endpoint +0x130; endpoint +0x100/+0x108 stores record; constraint +0x60 points back","history_preserved":True}
 W(m360,json.dumps(j,indent=2,ensure_ascii=False))

 note=TX/"EV-0364-note.md"
 W(note,f"""# EV-0364 — island owner path and constraint +0x10 correction

## Build and method

Five identity-checked queries used the existing GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. Analysis binary SHA-256: {BIN}. GOG RVAs do not transfer to Steam AE 1.6.1170.0. Raw captures remain under ignored .local.

## Competing models

- H1: endpoint +0x130 is its hkpSimulationIsland pointer; island +0x60/+0x68 EntityPtrs stores endpoints, and endpoint +0x100/+0x108 stores constraint records.
- H2: matching offsets and serializer labels belong to different owner paths, so endpoint +0x130 does not identify the island used by EntityPtrs.

## Direct observations

- FUN_140b678a0 reads selected endpoint +0x130 into constraint +0x10 and separately inserts its 0x40-byte record into endpoint +0x100/+0x108; constraint +0x60 back-pointers are updated when records shift [20261018T084404Z; EV-0360].
- EntityPtrs has one analyzed reference in FUN_140b60780 [20261018T084504Z]. The serializer traverses island +0x60/+0x68 and endpoint +0x100/+0x108 records [EV-0362, 20261018T080431Z].
- FUN_140b60b10 installs hkpSimulationIsland::vftable and initializes +0x60 entity storage and +0x68 count [20261018T085242Z].
- FUN_140b44470 appends endpoint pointers, writes endpoint +0x130 to the island, and stores the member index at +0xfc [20261018T085103Z].
- FUN_140b678a0 calls FUN_140b43f40 when endpoint +0x130 values differ. FUN_140b43f90 merges endpoint arrays, rewrites moved endpoint +0x130, and updates moved endpoint constraints +0x10 to the receiving island [20261018T084600Z].
- EV-0363 established the broad +0x60/+0x68 access lists were capped at 2,048 entries; they provide no physics-range writer negative.

## Result and uncertainty

H1 is strongly supported for the mapped static data flow; H2 is weakened. This supersedes EV-0360's phrase that +0x10 pointed to the selected endpoint. Exact Steam runtime pointer, live endpoint membership, callback population and AV11/AV12 remain unobserved. No positive damage, effective protection, zero Light/Heavy Armor XP or vanilla exploit is established. No causal edge to OBJ-1 is supported.

## Exact next action

Trace producer-backed writes to exact hkpConstraintInstance +0x40/+0x48 callback array/count. Identify callback-entry classes and follow attach slot +0x8, removal slot +0x10 and member finalizers to Actor::UseSkill AV11/AV12; preserve the exact Steam hit/protection/raw-AVSK discriminator.
""")
 m364=TX/"EV-0364-capture-manifest.json"; cm={"evidence_id":"EV-0364","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":{},"registered_local_hashes":{}}
 local={}
 for stamp,(m,mp,rp) in caps.items():
  cm["captures"][stamp]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"requested_string":m.get("requested_string"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")}
  for p in [mp,rp]+[ROOT/x for x in m.get("artifacts",{}).values()]:
   if p.is_file(): local[p.relative_to(ROOT).as_posix()]=H(p)
 for p in [note,n360,m360,r98,regp,cp,mp,cont,kg,ix,road,statep,Path(__file__)]+[EXP/x for x in ("README.md","hypothesis.md","protocol.md","expected-discriminants.md","predicted-outcomes.md","results.md","implications.md")]:
  if p.is_file(): local[p.relative_to(ROOT).as_posix()]=H(p)
 cm["registered_local_hashes"]=local.copy(); W(m364,json.dumps(cm,indent=2,ensure_ascii=False)); local[m364.relative_to(ROOT).as_posix()]=H(m364)
 i360=next(x for x in ev["items"] if x.get("id")=="EV-0360"); i360["sha256"]=H(n360)
 i360["result"]="The ProcessTrapHit-created hkpConstraintInstance receives endpoint +0x130 at +0x10; endpoint +0x100/+0x108 separately stores its record, and instance +0x60 points back. Typed island initialization/serialization/insertion/merge support hkpSimulationIsland ownership [EV-0364]. Callback producers, live membership and AV11/AV12 remain unresolved."
 i360.setdefault("local_hashes",{}).update({n360.relative_to(ROOT).as_posix():H(n360),m360.relative_to(ROOT).as_posix():H(m360),r98.relative_to(ROOT).as_posix():H(r98),regp.relative_to(ROOT).as_posix():H(regp)})
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0364","kind":"native","source":"Identity-checked read-only GOG Ghidra queries of constraint attachment, EntityPtrs reference, island initialization, endpoint insertion, and island merge.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0364-note.md","sha256":H(note),"runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],"coverage":"Constraint +0x10 source, endpoint +0x100/+0x108 insertion, instance +0x60 back-pointer, island EntityPtrs initialization/serialization/insertion/merge, and EV-0360 correction.","result":"Attach assigns endpoint +0x130 to constraint +0x10 and separately inserts its record into endpoint +0x100/+0x108. Typed island initialization, serializer, insertion and merge support +0x130 as an hkpSimulationIsland back-pointer. Live membership and AV11/AV12 remain unresolved.","related_evidence":["EV-0360","EV-0362","EV-0363","EV-0359"],"local_hashes":local})
 W(ep,json.dumps(ev,indent=2,ensure_ascii=False))
 print("Registered EV-0364; corrected EV-0360/CL-L199; added CL-L203/CL-L204 and M-0083.")
if __name__=="__main__": main()

