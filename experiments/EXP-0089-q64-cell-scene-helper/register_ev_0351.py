#!/usr/bin/env python3
"""Register the exact cell scene-member helper return path."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/".local/ghidra"; TX=ROOT/".local/alignment/transactions/TX-20261017-0011"; EXP=ROOT/"experiments/EXP-0089-q64-cell-scene-helper"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"; STAMP="20261018T055051Z"
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def main():
 mp=GH/f"gog-query-{STAMP}.meta.json"; m=json.loads(mp.read_text()); c=m.get("checks",{}); out=ROOT/m["artifacts"]["stdout"]; raw=out.read_text(errors="replace")
 markers=["TARGET_RVA=0x2B8510","OUTGOING_DIRECT_CALL_EDGE_COUNT=0","INDIRECT_CALL_SITE_COUNT=0","INCOMING_CALLER_FUNCTION_COUNT=39","XREF_CALL_EDGE=140737593 -> 1402b8510 caller=FUN_1407373e0","DECOMPILATION_BEGIN=FUN_1402b8510","param_1 + 0x130","*(undefined8 *)(*(longlong *)(param_1 + 0x130) + 8)","DECOMPILATION_END=FUN_1402b8510"]
 if (m.get("analysis_distribution")!="GOG" or m.get("analysis_binary_product_version")!="1.6.1179" or m.get("analysis_binary_sha256")!=BINARY or m.get("program_executable_path_matches_gog_binary") is not True or m.get("ok") is not True or m.get("exit_code")!=0 or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False or c.get("program_identity_matches_gog_binary") is not True or c.get("decompilation") is not True or c.get("script_no_error") is not True or digest(out)!=m.get("stdout_sha256") or any(x not in raw for x in markers)): raise SystemExit("EV-0351 identity/completion/marker validation failed")
 files=[mp]+[ROOT/x for x in m["artifacts"].values()]
 if any(not x.is_file() for x in files): raise SystemExit("capture artifact missing")
 hashes={x.relative_to(ROOT).as_posix():digest(x) for x in files}
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text())
 if any(x.get("id")=="EV-0351" for x in evidence["items"]): raise SystemExit("EV-0351 already registered")
 note=TX/"EV-0351-note.md"
 put(note,f"""# EV-0351 — Cell scene member helper returns a data-selected pointer

## Build and method

One identity-checked query used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. It queried FUN_1402b8510 with a complete caller census and decompilation. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_1402b8510 has no outgoing direct or indirect calls. It tests `param_1+0x130`; if non-null, it returns the 64-bit value stored at that member+0x8, otherwise it returns zero [capture {STAMP}].
- The bounded xref scan lists 39 caller functions, including the cell-transition function FUN_1407373e0 that handles the candidate PlayerCharacter+0x730 scene object [capture {STAMP}; EV-0334]. The other callers show this helper is reused broadly and do not establish the queried receiver's dynamic class.
- The returned pointer's concrete vtable and downstream array contents are data-dependent. EV-0332 records a TESObjectCELL constructor that zeroes the +0x130 field and a whole-binary +0x130 scan that did not identify an attributable non-null writer for this specific cell path. EV-0334 separately maps the cell-transition nested-array selection and NiNode-compatible parent/child operations, but not the child object's concrete class.

## Competing-model assessment

This confirms the helper's exact field return but does not identify the +0x730 child/finalizer chain or an AV11/AV12 sink. Q64-H1/H2 remain unresolved; the missing writer and data-selected child are not a no-skill result. No causal edge to OBJ-1 or armor XP is added.

## Exact next discriminant

Resolve the independent PlayerCamera global cleanup site at FUN_14072fd60: map its exact factory-installed vtable, slot-0 destructor, and direct/indirect descendants, then screen for AV11/AV12. Keep the +0x730 cell member and selected child unresolved until a non-null producer/class source is recovered.
""")
 manifest=TX/"EV-0351-capture-manifest.json"; put(manifest,json.dumps({"evidence_id":"EV-0351","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"capture":{"stamp":STAMP,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":c,"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")}},indent=2))
 hashes[note.relative_to(ROOT).as_posix()]=digest(note); hashes[manifest.relative_to(ROOT).as_posix()]=digest(manifest)
 docs={"README.md":"# EXP-0089 — Cell scene helper\n\nTrace the cell scene-member helper used by the +0x730 cell-transition branch and preserve unresolved field/class boundaries.\n","hypothesis.md":"# Competing models\n\n- Q64-H1: concrete +0x730 child finalizers avoid AV11/AV12 skill progress.\n- Q64-H2: at least one child finalizer descendant reaches AV11/AV12 skill progress.\n\nThe helper's pointer return does not discriminate the models.\n","protocol.md":"# Protocol\n\nUse the existing GOG project in read-only/no-analysis mode. Preserve the exact field read, null behavior, xrefs and caller context. Do not infer class from a helper name or pointer offset.\n","results.md":"# Results\n\nFUN_1402b8510 returns `cell+0x130+8` when `cell+0x130` is non-null, otherwise zero. The helper has 39 callers, including FUN_1407373e0, but exposes no class or finalizer [EV-0351].\n","predicted-outcomes.md":"# Predicted outcomes\n\n- A concrete +0x730 child vtable/finalizer reaching AV11/AV12 supports Q64-H2 for that branch.\n- A resolved descendant avoiding the sink narrows Q64-H1 to that branch only.\n- A non-null field read with an unknown class is inconclusive.\n","implications.md":"# Implications\n\nThe +0x730 helper return is an opaque pointer from cell+0x130+8. Existing evidence maps the surrounding scene-array behavior, while the non-null writer and child class remain unresolved.\n","expected-discriminants.md":"# Expected discriminants\n\n1. Recover a source-backed non-null writer for the exact cell +0x130 field.\n2. Identify the returned member and selected child vtables.\n3. Map slot +0x8 finalizers and descendants.\n4. Screen only resolved paths for Actor::UseSkill AV11/AV12.\n"}
 exp=ROOT/"experiments/EXP-0089-q64-cell-scene-helper"
 for n,s in docs.items(): put(exp/n,s)
 for f in exp.iterdir():
  if f.is_file(): hashes[f.relative_to(ROOT).as_posix()]=digest(f)
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0351","kind":"native","source":"Read-only GOG Ghidra query of FUN_1402b8510 and its callers on the cell-scene branch.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0351-note.md","sha256":digest(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],"coverage":"Exact helper body and 39-caller census including FUN_1407373e0; non-null +0x130 writer, return class and child finalizer remain unresolved.","result":"FUN_1402b8510 returns the pointer stored at cell+0x130+8 when cell+0x130 is non-null and zero otherwise. It does not identify the returned class or any AV11/AV12 path. Q64-H1/H2 remain proposed.","related_evidence":["EV-0332","EV-0334","EV-0346","EV-0350","EV-0217","EV-0220","EV-0221"],"local_hashes":hashes})
 put(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 claims=ROOT/"research/CLAIMS.md"; c=claims.read_text()
 if "| CL-L189 |" in c: raise SystemExit("CL-L189 already exists")
 put(claims,c.rstrip()+"\n| CL-L189 | In GOG AE 1.6.1179.0, FUN_1402b8510 returns the value at receiver+0x130+8 when receiver+0x130 is non-null and otherwise returns zero; its bounded caller census includes FUN_1407373e0. | supported for bounded helper flow | [EV-0351], [EV-0334] | The returned object's concrete class, non-null source, finalizer descendants, and AV11/AV12 reachability remain unresolved. |")
 mech=ROOT/"research/MECHANISMS.md"; put(mech,mech.read_text().rstrip()+"\n\n## M-0071 — Cell scene member helper at +0x130 (Q-0064)\n\nFUN_1402b8510 reads receiver+0x130 and returns the 64-bit member at +0x130+8 when non-null; it has no direct or indirect calls in its body. Its caller census includes FUN_1407373e0, but the non-null writer and returned object's class/finalizer remain unresolved [EV-0351], [EV-0332], [EV-0334]. Claim CL-L189 -> M-0071. No AV11/AV12 edge is established or excluded.\n")
 graph=ROOT/"research/KNOWLEDGE_GRAPH.md"; put(graph,graph.read_text().rstrip()+"\n\nEV-0351 confirms the +0x730 cell-transition helper reads a data-selected pointer at receiver+0x130+8. Existing evidence does not identify an attributable non-null writer or the selected object's vtable, so the scene child finalizer remains unresolved and no AV11/AV12 edge is added. The next bounded branch is the typed PlayerCamera global finalizer. Claim CL-L189 -> M-0071.\n")
 idx=ROOT/"experiments/README.md"; put(idx,idx.read_text().rstrip()+"\n\nEXP-0089 / EV-0351 maps FUN_1402b8510's cell+0x130+8 return; its non-null producer and result class remain unresolved.\n")
 road=ROOT/"research/ROADMAP.md"; put(road,road.read_text().rstrip()+"EV-0351 maps the +0x730 cell helper to an opaque cell+0x130+8 pointer; no class or non-null writer is recovered. Next resolve the PlayerCamera global slot-0 cleanup path, then return to the unresolved scene child. Claim CL-L189 -> M-0071.\n")
 fp=ROOT/"research/FRONTIER.json"; f=json.loads(fp.read_text()); q64=next(x for x in f["items"] if x.get("id")=="Q-0064"); q65=next(x for x in f["items"] if x.get("id")=="Q-0065")
 for item in (q64,q65):
  if "EV-0351" not in item.setdefault("evidence",[]): item["evidence"].append("EV-0351")
  for h in item.get("hypotheses",[]):
   if "EV-0351" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0351")
  if "CL-L189" not in item.setdefault("linked_claims",[]): item["linked_claims"].append("CL-L189")
 q64["next_action"]="Resolve the PlayerCamera global cleanup site in FUN_14072fd60: identify the exact factory-installed vtable for DAT_1430febf8, map slot 0 and the complete direct/indirect destructor descendants, then screen for Actor::UseSkill AV11/AV12. Preserve the +0x730 cell result as a data-selected pointer with no known non-null writer."
 q65["next_action"]="Compare exact producer-backed vtables for +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8 and ThirdPersonState+0xA0. EV-0351 leaves the cell+0x130+8 result untyped; only exact constructor/table evidence can distinguish Q65-H1/H2."
 if not any(a.get("action_key")=="q65-cell-member-source-bounded" for a in q65.get("attempts",[])):
  q65.setdefault("attempts",[]).append({"action_key":"q65-cell-member-source-bounded","outcome":"EV-0351 resolves the helper's pointer expression but not the returned class or non-null producer; Q65-H1/H2 remain unresolved.","evidence":["EV-0351"],"new_discriminant":"A concrete source-selected cell-member vtable must match or differ from the skeleton/model resource tables.","next_action":q65["next_action"]})
 put(fp,json.dumps(f,indent=2,ensure_ascii=False))
 cp=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; s=cp.read_text(); old="- Q-0064 / EV-0350 maps the mode-selected +0x9A8/+0x9A0 setter and model-resource caller, but the incoming class/finalizer remain unresolved. The next source branch is +0x730.\n"; new=old+"- Q-0064 / EV-0351 confirms the +0x730 helper returns a data-selected value at cell+0x130+8; class and non-null writer remain unknown. The next branch is the PlayerCamera global cleanup.\n"
 if old not in s: raise SystemExit("checkpoint EV-0350 line missing")
 put(cp,s.replace(old,new))
 print("registered EV-0351 / CL-L189 / M-0071; Q-0064 continues on the PlayerCamera cleanup")
if __name__=="__main__": main()
