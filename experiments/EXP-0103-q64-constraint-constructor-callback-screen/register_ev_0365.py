#!/usr/bin/env python3
"""Register EV-0365's hkpConstraintInstance constructor-caller screen."""
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
BIN="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMP="20261018T090112Z"
def H(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def W(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def main():
 mp=GH/("gog-query-"+STAMP+".meta.json"); m=json.loads(mp.read_text(encoding="utf-8"))
 rp=ROOT/m["artifacts"]["stdout"]; raw=rp.read_text(encoding="utf-8",errors="replace"); c=m.get("checks",{})
 markers=["TARGET_RVA=0xB48720","INCOMING_CALLER_FUNCTION_COUNT=9","caller=FUN_140ecdfc0","caller=FUN_140b91bb0","param_1[8] = 0;","*(undefined4 *)(param_1 + 9) = 0x80000000;","FUN_140b48720(lVar3,*puVar6,*puVar5,*puVar8,*(undefined4 *)puVar4);","*(longlong *)(lVar9 + 0x40) = plVar1[8];","*(longlong *)(lVar9 + 0x48) = lVar8;","FUN_140b48720(lVar8,*(undefined8 *)(param_1 + 0x28),*(undefined8 *)(param_1 + 0x30),lVar9,"]
 good=(m.get("analysis_distribution")=="GOG" and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BIN and m.get("requested_rva")=="0xB48720" and m.get("exit_code")==0 and m.get("ok") is True and m.get("read_only") is True and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False and m.get("overwrite_attempted") is False and c.get("program_identity_matches_gog_binary") is True and c.get("script_no_error") is True and all(c.values()) and H(rp)==m.get("stdout_sha256"))
 missing=[x for x in markers if x not in raw]
 if not good or missing: raise SystemExit(f"capture validation failed; missing={missing}")
 ep=ROOT/"research/EVIDENCE.json"; ev=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0365" for x in ev["items"]): raise SystemExit("EV-0365 exists")
 note=TX/"EV-0365-note.md"
 W(note,f"""# EV-0365 — hkpConstraintInstance constructor caller and callback-offset screen

## Build and method

One fresh identity-checked query used the existing GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. Analysis binary SHA-256: {BIN}. The existing ProcessTrapHit wrapper capture from EV-0355 is reused for the call from FUN_140ef43b0 into FUN_140ecdfc0.

## Competing models

- H1: same-offset writes at +0x40/+0x48 in a constructor caller populate the exact hkpConstraintInstance callback pointer and count.
- H2: those writes target the separate constraint-data payload passed to the constructor; the hkpConstraintInstance callback fields remain at their initialized empty values through the direct constructor caller.

## Direct observations

- FUN_140b48720 installs hkpConstraintInstance::vftable, initializes callback pointer +0x40 to null and initializes +0x48 to 0x80000000, whose low count bits are zero [capture {STAMP}; prior constructor evidence EV-0358].
- The constructor has nine analyzed caller functions and eleven call edges; the query decompiles eight incoming caller functions plus the primary caller view [capture {STAMP}]. One caller is FUN_140ecdfc0, which calls FUN_140b48720 with its fourth argument sourced from the constraint-data object and then calls wrapper virtual slots +0x128 and +0x188.
- The ProcessTrapHit child wrapper factory FUN_140ef43b0 calls FUN_140ecdfc0 in its fixed and malleable constraint branches [EV-0355, reused capture 20261018T064133Z]. This ties the constructor caller to the mapped factory branch.
- FUN_140b91bb0 writes fields +0x40/+0x48 on local object lVar9. That object is allocated as a 0xB0- or 0xD0-byte constraint-data payload and passed as the fourth constructor argument; FUN_140b48720 stores that argument at instance +0x18. The matching offsets therefore belong to a different receiver than the exact instance callback array [capture {STAMP}].
- No +0x40/+0x48 write appears in the direct FUN_140ecdfc0 constructor-caller body after construction. Its virtual +0x128/+0x188 targets remain dynamic, so later population through those methods is unresolved.

## Result and uncertainty

H2 is supported for this specific +0x40/+0x48 false positive; H1 is not supported by those writes. The exact ProcessTrapHit factory reaches a constructor that starts with an empty callback array, and its direct wrapper caller contains no callback-field write. This does not establish that callbacks remain empty after virtual dispatch or later world/island setup. No AV11/AV12 path is resolved, and no zero-armor-XP or live Steam result follows.

## Exact next action

Resolve the bhkFixedConstraint and bhkMalleableConstraint receiver tables for FUN_140ecdfc0 virtual slots +0x128 and +0x188. Test whether those targets register callbacks or otherwise populate the exact hkpConstraintInstance +0x40/+0x48 array, then follow concrete entries through attach +0x8, removal +0x10 and member finalizers to Actor::UseSkill AV11/AV12. Preserve the exact Steam hit/protection/raw-AVSK test.
""")
 docs={
 "README.md":"# EXP-0103 — hkpConstraintInstance constructor callback screen\n\nMap constructor callers, separate callback-array writes from constraint-data fields, and follow the ProcessTrapHit wrapper's exact virtual setup calls.\n",
 "hypothesis.md":"# Competing models\n\n- H1: matching +0x40/+0x48 writes populate the hkpConstraintInstance callback array.\n- H2: the writes belong to a separate constraint-data object passed into constructor +0x18.\n\nExact receiver identity and constructor argument flow discriminate these models.\n",
 "protocol.md":"# Protocol\n\nValidate the constructor caller census and query identity. Trace each +0x40/+0x48 store's base object and the hkpConstraintInstance constructor arguments. Then follow exact ProcessTrapHit wrapper virtual slots +0x128/+0x188; constructor-zero state alone is not a no-writer result.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Identify the destination object for every matching +0x40/+0x48 store.\n2. Map constructor argument four to instance +0x18.\n3. Confirm the ProcessTrapHit factory reaches the exact constructor caller.\n4. Resolve wrapper slots +0x128/+0x188 before inferring callback lifetime.\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- Stores on the hkp instance support H1.\n- Stores on a separately passed constraint-data payload support H2.\n- A constructor-empty array without later writer coverage leaves later callback state unresolved.\n",
 "results.md":"# Results\n\nFUN_140b48720 initializes the exact callback pointer/count empty. FUN_140b91bb0's matching +0x40/+0x48 writes target a separate 0xB0/0xD0 constraint-data payload passed into the constructor and stored at instance +0x18. The ProcessTrapHit factory reaches FUN_140ecdfc0, whose direct body has no callback-field store after construction but makes unresolved virtual calls at +0x128/+0x188 [EV-0365].\n",
 "implications.md":"# Implications\n\nThis rejects one same-offset callback-writer candidate, not all producers. Resolve fixed/malleable wrapper slots +0x128/+0x188 and preserve the Steam hit/protection/raw-AVSK test.\n"}
 for name,body in docs.items(): W(EXP/name,body)
 manifest=TX/"EV-0365-capture-manifest.json"
 hashes={mp.relative_to(ROOT).as_posix():H(mp),rp.relative_to(ROOT).as_posix():H(rp)}
 for x in m.get("artifacts",{}).values():
  p=ROOT/x
  if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=H(p)
 for p in [note,Path(__file__)]+[EXP/n for n in docs]:
  hashes[p.relative_to(ROOT).as_posix()]=H(p)
 W(manifest,json.dumps({"evidence_id":"EV-0365","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"capture":{"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"query_script_sha256":m.get("query_script_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")},"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
 hashes[manifest.relative_to(ROOT).as_posix()]=H(manifest)
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0365","kind":"native","source":"Identity-checked read-only GOG Ghidra constructor caller census for hkpConstraintInstance, with reused ProcessTrapHit factory context from EV-0355.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0365-note.md","sha256":H(note),"runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],"coverage":"Nine constructor caller functions, hkpConstraintInstance +0x40/+0x48 initialization, exact ProcessTrapHit factory caller, one same-offset constraint-data false positive, and unresolved wrapper slots +0x128/+0x188.","result":"The exact instance constructor starts callback pointer +0x40 null and count +0x48 zero. FUN_140b91bb0's matching stores target a separate constraint-data payload passed at instance +0x18, not the callback array. ProcessTrapHit factory caller FUN_140ecdfc0 has no direct callback-field store after construction but dispatches unresolved wrapper slots +0x128/+0x188.","related_evidence":["EV-0355","EV-0357","EV-0358","EV-0364"],"local_hashes":hashes})
 W(ep,json.dumps(ev,indent=2,ensure_ascii=False))

 cp=ROOT/"research/CLAIMS.md"; claims=cp.read_text(encoding="utf-8")
 if "| CL-L205 |" in claims: raise SystemExit("CL-L205 exists")
 claims+="\n| CL-L205 | In GOG AE 1.6.1179.0, FUN_140b91bb0 writes +0x40/+0x48 on a separate constraint-data payload passed as hkpConstraintInstance constructor argument four and stored at instance +0x18; those stores do not populate the exact instance callback array. FUN_140ecdfc0 initializes the instance through FUN_140b48720 and then dispatches unresolved wrapper slots +0x128/+0x188. | supported for the mapped caller bodies | [EV-0365], [EV-0355], [EV-0358] | Later callback producers and the wrapper slot targets remain unresolved. |\n"
 W(cp,claims)

 mp=ROOT/"research/MECHANISMS.md"; mech=mp.read_text(encoding="utf-8")
 mech+="""\n\n## M-0084 — constructor callback-offset false-positive screen (Q-0064)\n\nThe ProcessTrapHit factory reaches FUN_140ecdfc0 and FUN_140b48720. The exact constructor initializes its callback pointer/count at +0x40/+0x48 empty. FUN_140b91bb0's same-offset stores belong to a distinct 0xB0/0xD0 constraint-data payload passed as constructor argument four and stored at instance +0x18. FUN_140ecdfc0 then invokes wrapper slots +0x128/+0x188; their targets may still alter callback state. This rejects one false positive only and does not settle Q64-H1/H2 or AV11/AV12 [EV-0365]. Claim CL-L205 -> M-0084.\n"""
 W(mp,mech)

 cpcon=ROOT/"research/CONTRADICTIONS.md"; con=cpcon.read_text(encoding="utf-8")
 con+="""\n\n## C-OBJ2-Q64-CALLBACK-OFFSET-ALIAS — same-offset data fields versus callback array\n\n- **Model A:** FUN_140b91bb0 writes at +0x40/+0x48 and therefore populates hkpConstraintInstance callbacks.\n- **Model B:** those writes target a separately allocated constraint-data payload passed into the instance at +0x18; the callback array remains constructor-initialized empty in the direct creation path.\n- **Source:** complete constructor caller census, argument mapping, and exact factory caller body [EV-0365], with callback consumer/initializer baseline [EV-0358].\n- **Current assessment:** Model B is supported for the FUN_140b91bb0 candidate. No post-constructor callback-field write appears in the direct FUN_140ecdfc0 body. Wrapper virtual slots +0x128/+0x188 remain unresolved, so callback emptiness is not established beyond the mapped body.\n- **Discriminant:** resolve the exact fixed/malleable wrapper slot tables and inspect producer-backed writes to the exact instance +0x40/+0x48.\n"""
 W(cpcon,con)

 kg=ROOT/"research/KNOWLEDGE_GRAPH.md"; graph=kg.read_text(encoding="utf-8")
 graph+="""\n\nEV-0365 rejects one +0x40/+0x48 alias as a callback producer: FUN_140b91bb0 writes those offsets on constraint-data payload stored at instance +0x18. The ProcessTrapHit constructor path initializes the exact callback fields empty, then invokes wrapper slots +0x128/+0x188. No skill-progress or OBJ-1 causal edge is established; resolve those exact wrapper targets next [CL-L205], [M-0084].\n"""
 W(kg,graph)

 fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8"))
 q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
 q.setdefault("claims",[])
 if "CL-L205" not in q["claims"]: q["claims"].append("CL-L205")
 fp.write_text(json.dumps(fr,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

 statep=ROOT/"STATE.md"; state=statep.read_text(encoding="utf-8")
 anchor="- Q-0064 / EV-0364 corrects the constraint owner field: instance +0x10 receives endpoint +0x130; endpoint +0x100/+0x108 stores its constraint record and instance +0x60 points back. Island initialization, EntityPtrs serialization, insertion and merge support the owner model; live membership and AV11/AV12 remain unresolved."
 state=state.replace(anchor,anchor+"\n- Q-0064 / EV-0365 distinguishes one false +0x40/+0x48 writer: FUN_140b91bb0 stores into constraint-data payload passed at instance +0x18. The exact callback array starts empty, but wrapper slots +0x128/+0x188 remain unresolved.")
 action="TX-20261017-0011 / Q-0064: resolve bhkFixedConstraint and bhkMalleableConstraint receiver tables for FUN_140ecdfc0 slots +0x128/+0x188; test whether those methods populate exact hkpConstraintInstance callbacks and follow resulting entries/member finalizers to Actor::UseSkill AV11/AV12. Preserve Steam positive-damage/effective-protection/raw-AVSK discriminator."
 state=re.sub(r"(?m)^.*TX-20261017-0011.*$",action,state,count=1)
 W(statep,state)

 road=ROOT/"ROADMAP.md"; W(road,road.read_text(encoding="utf-8").rstrip()+"\n\nEV-0365 rejects one +0x40/+0x48 callback-writer candidate as a separate constraint-data payload. The ProcessTrapHit constructor path still dispatches wrapper slots +0x128/+0x188; resolve those exact class tables before concluding about callback population.\n")
 ix=ROOT/"experiments/README.md"; W(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0103 / EV-0365 separates constraint-data +0x40/+0x48 fields from the hkpConstraintInstance callback array; fixed/malleable wrapper slots +0x128/+0x188 remain open.\n")
 print("Registered EV-0365 and CL-L205/M-0084; callback screen remains open.")
if __name__=="__main__": main()

