#!/usr/bin/env python3
"""Register the +0x9A0/+0x9A8 model-resource adapter and member lookup trace."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/".local/ghidra"; TX=ROOT/".local/alignment/transactions/TX-20261017-0011"; EXP=ROOT/"experiments/EXP-0087-q64-model-resource-adapter"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES=[
 {"stamp":"20261018T054436Z","markers":["TARGET_RVA=0x216B40","OUTGOING_DIRECT_CALL_EDGE_COUNT=21","INDIRECT_CALL_SITE_COUNT=11","FUN_140e05620(pcVar9,&local_f8,&local_f0)","FUN_140d19980(local_100,local_d8)","FUN_140d27eb0(plVar10,lVar11 + 0xa0)","INCOMING_CALLER_FUNCTION_COUNT=4","DECOMPILATION_END=FUN_140216b40"]},
 {"stamp":"20261018T054537Z","markers":["TARGET_RVA=0xD19980","INDIRECT_CALL_SITE_COUNT=2","DECOMPILATION_BEGIN=FUN_140d19980","(*param_1 + 0xb8)","(*param_1 + 0xe8)","return uVar1","INCOMING_CALLER_FUNCTION_COUNT=24"]},
 {"stamp":"20261018T054645Z","markers":["TARGET_RVA=0xD27EB0","OUTGOING_DIRECT_CALL_EDGE_COUNT=5","INDIRECT_CALL_SITE_COUNT=0","DECOMPILATION_BEGIN=FUN_140d27eb0","param_1 + 0x28","param_1 + 0x20","FUN_140d36b10","INCOMING_CALLER_FUNCTION_COUNT=64"]},
]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def validate(spec):
 stamp=spec["stamp"]; mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text()); c=m.get("checks",{})
 if (m.get("analysis_distribution")!="GOG" or m.get("analysis_binary_product_version")!="1.6.1179" or m.get("analysis_binary_sha256")!=BINARY or m.get("program_executable_path_matches_gog_binary") is not True or m.get("ok") is not True or m.get("exit_code")!=0 or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False or c.get("program_identity_matches_gog_binary") is not True or c.get("decompilation") is not True or c.get("script_no_error") is not True): raise SystemExit(f"identity/read-only/decompilation validation failed: {stamp}")
 out=ROOT/m["artifacts"]["stdout"]; raw=out.read_text(errors="replace")
 if digest(out)!=m.get("stdout_sha256") or any(x not in raw for x in spec["markers"]): raise SystemExit(f"capture marker/hash validation failed: {stamp}")
 files=[mp]+[ROOT/x for x in m["artifacts"].values()]
 if any(not x.is_file() for x in files): raise SystemExit(f"capture artifact missing: {stamp}")
 hashes={x.relative_to(ROOT).as_posix():digest(x) for x in files}
 return {"stamp":stamp,"requested_rva":m.get("requested_rva"),"query_mode":m.get("query_mode"),"checks":c,"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")},hashes
def main():
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text())
 if any(x.get("id")=="EV-0349" for x in evidence["items"]): raise SystemExit("EV-0349 already registered")
 rows=[]; hashes={}
 for spec in CAPTURES:
  row,h=validate(spec); rows.append(row); hashes.update(h)
 note=TX/"EV-0349-note.md"
 put(note,f"""# EV-0349 — Model-resource adapter and sorted member lookup

## Build and method

Three identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. The queries cover FUN_140216b40, its adapter FUN_140d19980, and the member lookup FUN_140d27eb0. All requested decompilation and completion checks passed. These addresses are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_140216b40 gets a model name from a dynamic slot +0x20, loads it through FUN_140e05620, and obtains a refcounted resource object from handle member +0x28. When FUN_140e1ad20 returns false, it calls FUN_140d19980 on the retained object and uses the adapter result as the working object. Its callers include FUN_140215660, which EV-0333 connects to the candidate PlayerCharacter +0x9A0/+0x9A8 setter FUN_1407445d0 [capture 20261018T054436Z; EV-0333].
- FUN_140d19980 has two indirect calls and no direct code call edges in its own body: it returns the result of input slot +0xB8, then calls input slot +0xE8 with the second argument. The fresh xref census includes FUN_140216b40 and 23 other caller functions. The adapter does not itself expose a constructor or concrete vtable for the returned object [capture 20261018T054537Z].
- FUN_140216b40 calls FUN_140d27eb0 three times on the working object with a descriptor-derived name and two static-name pointers. FUN_140d27eb0 reads a count at object+0x28 and a pointer array at object+0x20, binary-searches entries by a key returned through FUN_140d36b10, and returns the matched array member. Its body has five direct calls and no indirect call sites; the complete bounded xref census lists 64 caller functions [capture 20261018T054645Z].
- This member lookup is structurally different from the +0x8F8 use-site dispatch, where FUN_140736be0 calls the loaded object's vtable slot +0x150 with named markers [EV-0347]. The difference identifies two lookup paths, but does not prove the roots have distinct concrete classes or vtables.
- The exact adapter-selected values, the working object's vtable, the array members' classes, and the candidate setter's exact runtime input remain data-selected. The adapter and lookup helper show no direct Actor::UseSkill AV11/AV12 edge, but unresolved virtual slots and object finalizers prevent a transitive negative.

## Competing-model assessment

Q64-H1 predicts that concrete finalizer descendants of the +0x9A0/+0x9A8 objects avoid AV11/AV12 skill progress. Q64-H2 predicts at least one resolved descendant reaches that sink with an armor AV. The adapter and sorted-array lookup expose no class identity and do not discriminate these models. Q65-H1/H2 also remain unresolved: differing lookup contracts are not themselves differing vtables.

## Exact next discriminant

Trace candidate setter FUN_1407445d0 and its player-path callers against the adapter return, then recover a concrete constructor or vtable source if one is selected. If it remains data-dependent, continue with the exact +0x730 scene child source and retain both model-resource classes as unresolved.
""")
 manifest=TX/"EV-0349-capture-manifest.json"; put(manifest,json.dumps({"evidence_id":"EV-0349","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"captures":rows},indent=2))
 hashes[note.relative_to(ROOT).as_posix()]=digest(note); hashes[manifest.relative_to(ROOT).as_posix()]=digest(manifest)
 docs={
 "README.md":"# EXP-0087 — Model-resource adapter\n\nTrace the +0x9A0/+0x9A8 resource producer through its dynamic adapter and named-member lookup. Compare its lookup contract with the +0x8F8 first-person resource without inferring class identity from method shape.\n",
 "hypothesis.md":"# Competing models\n\n- Q64-H1: concrete +0x9A0/+0x9A8 finalizer descendants do not reach AV11/AV12 skill progress.\n- Q64-H2: at least one model-resource finalizer descendant routes AV11/AV12 into skill progress.\n- Q65-H1: the model-resource outputs and first-person/scene fields share a concrete NiAVObject/NiNode finalizer family.\n- Q65-H2: the fields hold distinct data-selected resource classes.\n",
 "protocol.md":"# Protocol\n\nUse build-attested read-only GOG queries. Follow the model-name source, generic resource handle, adapter's indirect slots, sorted member array and candidate setter. Compare exact vtable evidence only; lookup shape and generic refcount ABI are not class evidence.\n",
 "results.md":"# Results\n\nFUN_140216b40 loads a generic mesh resource and adapts it through FUN_140d19980, which returns slot +0xB8 and calls slot +0xE8. Named members are found by FUN_140d27eb0 in a count/pointer sorted array. The output can feed the candidate PlayerCharacter +0x9A0/+0x9A8 setter, but its exact vtable remains data-selected [EV-0349], [EV-0333].\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- A concrete model-resource constructor/vtable matching +0x8F8 or +0x730 supports Q65-H1.\n- A concrete different vtable supports Q65-H2.\n- Different lookup contracts alone do not decide class identity.\n- A resolved finalizer path to AV11/AV12 supports Q64-H2 for that branch; otherwise only that branch is narrowed.\n",
 "implications.md":"# Implications\n\nThe +0x9A0/+0x9A8 path uses a dynamic adapter and a sorted-name array helper, while the +0x8F8 use site calls virtual slot +0x150. Neither currently supplies a concrete root or finalizer.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Trace the exact object passed from FUN_140216b40 into FUN_1407445d0.\n2. Recover its source constructor or runtime vtable from the exact producer branch.\n3. Compare slot +0x8 and descendants with the mapped cleanup sites.\n4. Screen for Actor::UseSkill AV11/AV12 without treating unresolved virtual calls as negatives.\n"}
 for n,s in docs.items(): put(EXP/n,s)
 for f in EXP.iterdir():
  if f.is_file(): hashes[f.relative_to(ROOT).as_posix()]=digest(f)
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0349","kind":"native","source":"Read-only GOG Ghidra traces of the +0x9A0/+0x9A8 model-resource producer, two-slot adapter and sorted member lookup.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0349-note.md","sha256":digest(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],"coverage":"Three complete function queries map the model-resource loader, adapter slots +0xB8/+0xE8, and sorted-array member lookup. Exact returned object vtables, finalizers and AV11/AV12 descendants remain unresolved.","result":"FUN_140216b40 loads a model resource through FUN_140e05620, adapts the retained object via FUN_140d19980 and performs sorted-name lookups through FUN_140d27eb0 before returning a candidate value to the EV-0333 setter path. The adapter's class and member output types remain data-selected. The +0x8F8 virtual slot +0x150 path is structurally different, but no distinct class or shared finalizer family is proven. No Q64/Q65 resolution or skill-sink negative follows.","related_evidence":["EV-0329","EV-0333","EV-0346","EV-0347","EV-0348","EV-0217","EV-0220","EV-0221"],"local_hashes":hashes})
 put(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 claims=ROOT/"research/CLAIMS.md"; c=claims.read_text()
 if "| CL-L187 |" in c: raise SystemExit("CL-L187 already exists")
 put(claims,c.rstrip()+"\n| CL-L187 | In GOG AE 1.6.1179.0, FUN_140216b40 loads a model resource, passes its retained handle object through FUN_140d19980 (dynamic slots +0xB8/+0xE8), and uses FUN_140d27eb0 for sorted-name member lookups before the candidate +0x9A0/+0x9A8 setter path. | supported for bounded producer/helper flow | [EV-0349], [EV-0333] | The adapter return, named members, concrete vtables, slot +0x8 finalizers, and AV11/AV12 descendants remain data-dependent. Different lookup contracts do not prove distinct classes. |")
 mech=ROOT/"research/MECHANISMS.md"; put(mech,mech.read_text().rstrip()+"\n\n## M-0069 — Model-resource adapter and sorted member lookup (Q-0064/Q-0065)\n\nThe candidate +0x9A0/+0x9A8 producer loads a generic mesh resource, passes its retained object through an adapter that returns virtual slot +0xB8 and invokes slot +0xE8, then resolves named members through a sorted pointer array helper [EV-0349], [EV-0333]. This differs from the +0x8F8 slot +0x150 lookup callsite [EV-0347] but does not identify either concrete root class or prove distinct vtables. No finalizer descendant reaches or is excluded from the AV11/AV12 sink. Claim CL-L187 -> M-0069.\n")
 graph=ROOT/"research/KNOWLEDGE_GRAPH.md"; put(graph,graph.read_text().rstrip()+"\n\nEV-0349 maps the candidate +0x9A0/+0x9A8 model path through FUN_140d19980's dynamic +0xB8/+0xE8 adapter and FUN_140d27eb0's sorted-name array. The +0x8F8 path instead calls its root's slot +0x150 [EV-0347]; these use-site differences do not establish different concrete classes or a shared NiNode family. The finalizer/AV11/AV12 relationship remains unresolved. Claim CL-L187 -> M-0069; no causal sink edge is added.\n")
 idx=ROOT/"experiments/README.md"; put(idx,idx.read_text().rstrip()+"\n\nEXP-0087 / EV-0349 maps the +0x9A0/+0x9A8 model-resource adapter and sorted member lookup; concrete output classes remain data-selected.\n")
 road=ROOT/"research/ROADMAP.md"; put(road,road.read_text().rstrip()+"EV-0349 maps the +0x9A0/+0x9A8 model path through a two-slot adapter and sorted-name array lookup. Its lookup contract differs from +0x8F8 slot +0x150 use but does not resolve class identity. Next, inspect candidate setter FUN_1407445d0 and its exact callers for a concrete producer-backed vtable; otherwise continue with the +0x730 source. Claim CL-L187 -> M-0069.\n")
 fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text()); q64=next(x for x in frontier["items"] if x.get("id")=="Q-0064"); q65=next(x for x in frontier["items"] if x.get("id")=="Q-0065")
 for item in (q64,q65):
  if "EV-0349" not in item.setdefault("evidence",[]): item["evidence"].append("EV-0349")
  for h in item.get("hypotheses",[]):
   if "EV-0349" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0349")
  if "CL-L187" not in item.setdefault("linked_claims",[]): item["linked_claims"].append("CL-L187")
 q64["next_action"]="Inspect candidate setter FUN_1407445d0 and its exact caller data flow to determine whether a concrete producer-backed vtable is selected for +0x9A0/+0x9A8. If still data-dependent, resolve the +0x730 cell-scene child producer and compare only exact vtable/finalizer evidence; screen all resolved descendants for AV11/AV12."
 q65["next_action"]="Compare exact producer-backed vtables for +0x8F8, +0x730, +0x9D0, +0x9A0/+0x9A8 and ThirdPersonState+0xA0. EV-0349 shows different lookup contracts for +0x8F8 and +0x9A0/+0x9A8 without proving different concrete classes."
 if not any(a.get("action_key")=="q65-model-lookup-contract-comparison" for a in q65.get("attempts",[])):
  q65.setdefault("attempts",[]).append({"action_key":"q65-model-lookup-contract-comparison","outcome":"EV-0349 distinguishes the +0x9A0 sorted-name lookup from the +0x8F8 virtual slot +0x150 use, but exact object vtables are still unknown; Q65-H1/H2 remain unresolved.","evidence":["EV-0349","EV-0347"],"new_discriminant":"Recover matching or differing concrete producer-backed vtables; lookup behavior alone is not class evidence.","next_action":q65["next_action"]})
 put(fp,json.dumps(frontier,indent=2,ensure_ascii=False))
 cp=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; s=cp.read_text(); old="- Q-0064 / EV-0348 maps the +0x9D0 fallback to descriptor key-2/key-1 values, with the concrete object class still data-dependent. The next path is the +0x9A0/+0x9A8 model resource.\n"; new=old+"- Q-0064 / EV-0349 maps the +0x9A0/+0x9A8 candidate through a two-slot adapter and sorted-name lookup. Its concrete root/finalizer remains data-selected; the lookup contract differs from +0x8F8 without deciding class identity.\n"
 if old not in s: raise SystemExit("checkpoint EV-0348 line missing")
 put(cp,s.replace(old,new))
 print("registered EV-0349 / CL-L187 / M-0069; Q-0064 continues at the +0x9A0/+0x9A8 setter")
if __name__=="__main__": main()
