#!/usr/bin/env python3
"""Register the bounded +0x9A0/+0x9A8 setter trace."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/".local/ghidra"; TX=ROOT/".local/alignment/transactions/TX-20261017-0011"; EXP=ROOT/"experiments/EXP-0088-q64-model-resource-setter"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"; STAMP="20261018T054851Z"
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def main():
 mp=GH/f"gog-query-{STAMP}.meta.json"; m=json.loads(mp.read_text()); c=m.get("checks",{}); out=ROOT/m["artifacts"]["stdout"]; raw=out.read_text(errors="replace")
 markers=["TARGET_RVA=0x7445D0","OUTGOING_DIRECT_CALL_EDGE_COUNT=0","INCOMING_CALLER_FUNCTION_COUNT=2","XREF_CALL_EDGE=140215921 -> 1407445d0 caller=FUN_140215660","DECOMPILATION_BEGIN=FUN_1407445d0","param_1 + 0x9a8","param_1 + 0x9a0","(*plVar3 + 8)","INCOMING_CALLER_DECOMPILATION_BEGIN=FUN_140215660"]
 if (m.get("analysis_distribution")!="GOG" or m.get("analysis_binary_product_version")!="1.6.1179" or m.get("analysis_binary_sha256")!=BINARY or m.get("program_executable_path_matches_gog_binary") is not True or m.get("ok") is not True or m.get("exit_code")!=0 or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False or c.get("program_identity_matches_gog_binary") is not True or c.get("decompilation") is not True or c.get("script_no_error") is not True or digest(out)!=m.get("stdout_sha256") or any(x not in raw for x in markers)): raise SystemExit("EV-0350 identity, completion or capture marker validation failed")
 files=[mp]+[ROOT/x for x in m["artifacts"].values()]
 if any(not x.is_file() for x in files): raise SystemExit("capture artifact missing")
 hashes={x.relative_to(ROOT).as_posix():digest(x) for x in files}
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text())
 if any(x.get("id")=="EV-0350" for x in evidence["items"]): raise SystemExit("EV-0350 already registered")
 note=TX/"EV-0350-note.md"
 put(note,f"""# EV-0350 — Candidate model-resource setter semantics

## Build and method

One identity-checked query used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. FUN_1407445d0 was queried with its complete analyzed caller census and caller decompilation. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_1407445d0 has no outgoing direct calls. With its third argument zero it selects receiver offset +0x9A8; with a nonzero value it selects +0x9A0. It returns early if the stored pointer equals the incoming pointer [capture {STAMP}].
- On replacement, the function increments the incoming object's reference count at +0x8, stores the pointer at the selected field, and decrements the replaced object's reference count. It calls the replaced object's dynamic vtable slot +0x8 only when the old count reaches one [capture {STAMP}; compare EV-0346].
- The bounded direct xref census lists two callers, including FUN_140215660. Its caller body shows the FUN_140216b40 model-resource output passed into the setter path [capture {STAMP}; EV-0333; EV-0349]. The source object is still data-selected through FUN_140d19980's slots +0xB8/+0xE8.
- The setter's field selection and reference-count behavior do not establish the incoming object's concrete class, vtable, slot +0x8 implementation, or any destructor descendant. The second caller FUN_140215af0 is a distinct source path and does not identify the model resource's class.

## Competing-model assessment

This strengthens the producer-to-field connection for the +0x9A0/+0x9A8 cleanup fields but does not distinguish Q64-H1 from Q64-H2. No call/data edge to Actor::UseSkill AV11/AV12 is resolved, and the dynamic finalizer remains open. Q65-H1/H2 also remain unresolved because a generic refcount setter is shared ABI evidence, not concrete class identity.

## Exact next discriminant

Move to the independent +0x730 cell-scene child source. Recover the exact object producer and concrete child vtable/finalizer, then screen only resolved descendants for AV11/AV12. Keep the +0x9A0/+0x9A8 object class untyped until a source-selected constructor or runtime vtable is found.
""")
 manifest=TX/"EV-0350-capture-manifest.json"; put(manifest,json.dumps({"evidence_id":"EV-0350","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"capture":{"stamp":STAMP,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":c,"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")}},indent=2))
 hashes[note.relative_to(ROOT).as_posix()]=digest(note); hashes[manifest.relative_to(ROOT).as_posix()]=digest(manifest)
 docs={"README.md":"# EXP-0088 — Model-resource setter\n\nTrace how the candidate FUN_140216b40 model-resource output is retained at PlayerCharacter+0x9A0/+0x9A8 and identify any exact source class.\n","hypothesis.md":"# Competing models\n\n- Q64-H1: the object's concrete finalizer descendants avoid AV11/AV12 skill progress.\n- Q64-H2: at least one finalizer descendant reaches skill progress with AV11/AV12.\n\nRefcount storage alone does not discriminate the models.\n","protocol.md":"# Protocol\n\nUse the existing GOG project read-only. Map setter arguments, selected field, new/replaced reference counts, direct callers, and the model-resource return. Do not infer a class from slot +0x8 ABI.\n","results.md":"# Results\n\nFUN_1407445d0 selects +0x9A8 when its mode is zero and +0x9A0 otherwise, retains the incoming pointer, and final-releases the replaced pointer through dynamic slot +0x8. One caller passes the model-resource output from FUN_140216b40; the object's class and destructor remain unresolved [EV-0350], [EV-0349].\n","predicted-outcomes.md":"# Predicted outcomes\n\n- A producer-backed class and finalizer reaching Actor::UseSkill AV11/AV12 supports Q64-H2 for this branch.\n- A resolved finalizer chain avoiding that sink narrows Q64-H1 to this branch.\n- Generic storage/refcount behavior is inconclusive.\n","implications.md":"# Implications\n\nThe candidate model-resource output reaches a setter with exact +0x9A0/+0x9A8 field selection, but the object's class remains dynamic. Continue to the separate +0x730 child producer.\n","expected-discriminants.md":"# Expected discriminants\n\n1. Identify the exact model-resource object passed to the setter.\n2. Resolve a constructor or data-selected vtable for that object.\n3. Map its final slot +0x8 target and descendants.\n4. Compare against the AV11/AV12 sink; unknown targets remain unresolved.\n"}
 exp=ROOT/"experiments/EXP-0088-q64-model-resource-setter"
 for n,s in docs.items(): put(exp/n,s)
 for f in exp.iterdir():
  if f.is_file(): hashes[f.relative_to(ROOT).as_posix()]=digest(f)
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0350","kind":"native","source":"Read-only GOG Ghidra trace of FUN_1407445d0's +0x9A0/+0x9A8 refcount setter and caller path.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0350-note.md","sha256":digest(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],"coverage":"Complete setter decompilation, two-caller census, and one caller body. Incoming object class, vtable, finalizer and AV11/AV12 descendants remain unresolved.","result":"FUN_1407445d0 writes +0x9A8 for mode zero and +0x9A0 otherwise, AddRefs the incoming pointer, and final-releases the replaced object through dynamic slot +0x8. FUN_140215660 is a caller that passes the model-resource output path. This does not resolve object class or Q64-H1/H2.","related_evidence":["EV-0329","EV-0333","EV-0346","EV-0349","EV-0217","EV-0220","EV-0221"],"local_hashes":hashes})
 put(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 claims=ROOT/"research/CLAIMS.md"; c=claims.read_text()
 if "| CL-L188 |" in c: raise SystemExit("CL-L188 already exists")
 put(claims,c.rstrip()+"\n| CL-L188 | In GOG AE 1.6.1179.0, FUN_1407445d0 writes the incoming pointer to +0x9A8 when its mode argument is zero and +0x9A0 otherwise; replacement increments the new reference and final-releases the prior value through dynamic slot +0x8. FUN_140215660 is a caller on the model-resource path. | supported for bounded setter/caller flow | [EV-0350], [EV-0349], [EV-0333] | Incoming object class, concrete slot +0x8 target, destructor descendants, and AV11/AV12 reachability remain unresolved. |")
 mech=ROOT/"research/MECHANISMS.md"; put(mech,mech.read_text().rstrip()+"\n\n## M-0070 — +0x9A0/+0x9A8 mode-selected reference setter (Q-0064)\n\nFUN_1407445d0 selects +0x9A8 for mode zero and +0x9A0 otherwise, AddRefs the incoming object, and final-releases a replaced pointer through dynamic slot +0x8. FUN_140215660 passes the model-resource producer output on one caller path [EV-0350], [EV-0349], [EV-0333]. The incoming object's concrete class and finalizer chain remain unresolved; no AV11/AV12 edge is added or excluded. Claim CL-L188 -> M-0070.\n")
 graph=ROOT/"research/KNOWLEDGE_GRAPH.md"; put(graph,graph.read_text().rstrip()+"\n\nEV-0350 maps the candidate +0x9A0/+0x9A8 setter's mode-selected fields and dynamic refcount-final slot +0x8. One caller passes the model-resource output traced in EV-0349/EV-0333, but the object class and descendants remain data-selected. No edge to Actor::UseSkill AV11/AV12 is resolved or excluded. The next independent branch is the +0x730 cell-scene child source. Claim CL-L188 -> M-0070.\n")
 idx=ROOT/"experiments/README.md"; put(idx,idx.read_text().rstrip()+"\n\nEXP-0088 / EV-0350 maps the +0x9A0/+0x9A8 setter modes, reference counts, and model-resource caller; stored object type remains unresolved.\n")
 road=ROOT/"research/ROADMAP.md"; put(road,road.read_text().rstrip()+"EV-0350 maps the +0x9A0/+0x9A8 setter and its model-resource caller, but leaves the incoming object's vtable and finalizer unknown. Continue on the independent +0x730 cell-scene child producer, then screen exact finalizer descendants for AV11/AV12. Claim CL-L188 -> M-0070.\n")
 fp=ROOT/"research/FRONTIER.json"; f=json.loads(fp.read_text()); q64=next(x for x in f["items"] if x.get("id")=="Q-0064"); q65=next(x for x in f["items"] if x.get("id")=="Q-0065")
 for item in (q64,q65):
  if "EV-0350" not in item.setdefault("evidence",[]): item["evidence"].append("EV-0350")
  for h in item.get("hypotheses",[]):
   if "EV-0350" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0350")
  if "CL-L188" not in item.setdefault("linked_claims",[]): item["linked_claims"].append("CL-L188")
 q64["next_action"]="Resolve the +0x730 cell-scene child source from FUN_1407373e0: trace the selected cell member and find a concrete child constructor/vtable, then map its final slot +0x8 target and descendants. Compare exact tables with the conditional NiNode candidate from EV-0334. Screen resolved descendants for Actor::UseSkill AV11/AV12; do not treat the +0x9A0/+0x9A8 setter's generic refcount behavior as a type result."
 q65["next_action"]="Compare exact producer-backed vtables for +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, and ThirdPersonState+0xA0. EV-0350 confirms a shared refcount setter ABI but no incoming class identity; generic slot +0x8 remains inconclusive."
 if not any(a.get("action_key")=="q65-model-setter-class-boundary" for a in q65.get("attempts",[])):
  q65.setdefault("attempts",[]).append({"action_key":"q65-model-setter-class-boundary","outcome":"EV-0350 confirms the candidate +0x9A0/+0x9A8 refcount setter but exposes no incoming class or vtable; Q65-H1/H2 remain unresolved.","evidence":["EV-0350"],"new_discriminant":"A source-selected concrete incoming vtable must match or differ from the exact scene/skeleton tables before family classification.","next_action":q65["next_action"]})
 put(fp,json.dumps(f,indent=2,ensure_ascii=False))
 cp=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; s=cp.read_text(); old="- Q-0064 / EV-0349 maps the +0x9A0/+0x9A8 candidate through a two-slot adapter and sorted-name lookup. Its concrete root/finalizer remains data-selected; the lookup contract differs from +0x8F8 without deciding class identity.\n"; new=old+"- Q-0064 / EV-0350 maps the mode-selected +0x9A8/+0x9A0 setter and model-resource caller, but the incoming class/finalizer remain unresolved. The next source branch is +0x730.\n"
 if old not in s: raise SystemExit("checkpoint EV-0349 line missing")
 put(cp,s.replace(old,new))
 print("registered EV-0350 / CL-L188 / M-0070; Q-0064 continues on the +0x730 child source")
if __name__=="__main__": main()
