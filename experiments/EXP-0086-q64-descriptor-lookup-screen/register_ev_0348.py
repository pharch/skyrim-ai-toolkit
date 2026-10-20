#!/usr/bin/env python3
"""Register the bounded +0x9D0 descriptor lookup screen."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=ROOT/"experiments/EXP-0086-q64-descriptor-lookup-screen"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES=[
 {"stamp":"20261018T054022Z","markers":["TARGET_RVA=0xE84AD0","INCOMING_CALLER_FUNCTION_COUNT=1","XREF_CALL_EDGE=1402b8d99 -> 140e84ad0 caller=FUN_1402b8cf0","DECOMPILATION_BEGIN=FUN_140e84ad0","FUN_140e83f10(auStackX_8,lVar3,2)","FUN_140e84220(*(longlong *)(lVar3 + 0x18),0)","DECOMPILATION_END=FUN_140e84ad0"]},
 {"stamp":"20261018T054124Z","markers":["TARGET_RVA=0xE84220","INCOMING_CALLER_FUNCTION_COUNT=5","DECOMPILATION_BEGIN=FUN_140e84220","*(int **)(lVar2 + 0xb8)","*(int *)(lVar2 + 0xc0)","*(ulonglong *)(piVar3 + (longlong)(int)uVar5 * 4 + 2)","DECOMPILATION_END=FUN_140e84220"]},
 {"stamp":"20261018T054219Z","markers":["TARGET_RVA=0xE83F10","INCOMING_CALLER_FUNCTION_COUNT=26","DECOMPILATION_BEGIN=FUN_140e83f10","*(int *)(param_2 + 0xc0)","*(int **)(param_2 + 0xb8)","*(ulonglong *)(*(int **)(param_2 + 0xb8) + (longlong)(int)uVar3 * 4 + 2)","DECOMPILATION_END=FUN_140e83f10"]},
]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def validate(spec):
 stamp=spec["stamp"]; mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text()); c=m.get("checks",{})
 if (m.get("analysis_distribution")!="GOG" or m.get("analysis_binary_product_version")!="1.6.1179" or m.get("analysis_binary_sha256")!=BINARY or m.get("program_executable_path_matches_gog_binary") is not True or m.get("ok") is not True or m.get("exit_code")!=0 or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False or c.get("program_identity_matches_gog_binary") is not True or c.get("decompilation") is not True or c.get("script_no_error") is not True): raise SystemExit(f"identity/read-only/decompilation check failed: {stamp}")
 raw=(ROOT/m["artifacts"]["stdout"]).read_text(errors="replace")
 if digest(ROOT/m["artifacts"]["stdout"])!=m.get("stdout_sha256") or any(x not in raw for x in spec["markers"]): raise SystemExit(f"capture marker/hash failure: {stamp}")
 files=[mp]+[ROOT/x for x in m["artifacts"].values()]
 if any(not x.is_file() for x in files): raise SystemExit(f"missing capture artifact: {stamp}")
 h={x.relative_to(ROOT).as_posix():digest(x) for x in files}
 return {"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),"checks":c,"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")},h
def main():
 ep=ROOT/"research/EVIDENCE.json"; evidence=json.loads(ep.read_text())
 if any(x.get("id")=="EV-0348" for x in evidence["items"]): raise SystemExit("EV-0348 already registered")
 rows=[]; hashes={}
 for s in CAPTURES:
  row,h=validate(s); rows.append(row); hashes.update(h)
 note=TX/"EV-0348-note.md"
 put(note,f"""# EV-0348 — +0x9D0 descriptor fallback returns opaque table values

## Build and method

Three bounded queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. They query FUN_140e84ad0, FUN_140e84220 and FUN_140e83f10. Identity, decompilation and query completion checks passed. These GOG addresses are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_1402b8cf0 is the only analyzed direct caller of FUN_140e84ad0 in the bounded xref result. Its fallback invokes FUN_140e84ad0 after the separate descriptor type-0x11 branch [capture 20261018T054022Z; prior producer context EV-0332].
- FUN_140e84ad0 reads descriptor data at +0x80, resolves a table-like member, searches key 2 with FUN_140e83f10, and returns the selected entry's 64-bit field at entry+0x10. If that lookup misses, it calls FUN_140e84220 with key 0, which its body normalizes to key 1 [capture 20261018T054022Z].
- FUN_140e84220 treats its first argument as a wrapper containing a table pointer at +0xB8 and count at +0xC0. It scans 16-byte entries for the selected integer key and returns the 64-bit value in the entry's latter half. The queried body contains no explicit constructor or vtable write [capture 20261018T054124Z].
- FUN_140e83f10 performs the corresponding key search over a table pointer at +0xB8/count +0xC0, writes the selected 64-bit entry value through its out parameter, or writes zero on a miss. The queried body contains no explicit constructor or vtable write [capture 20261018T054219Z].
- The array contents and the selected return values are data-dependent. This source slice therefore identifies lookup shape and selection keys, but not the dynamic object class, vtable, slot +0x8 target, or descendant chain stored by the PlayerCharacter +0x9D0 candidate writer.

## Competing-model assessment

Q64-H1 predicts the concrete returned object's finalizer descendants avoid the mapped AV11/AV12 skill-progress sink. Q64-H2 predicts a resolved descendant reaches that sink with an armor AV. These table-lookup bodies provide no class or sink edge and do not discriminate the hypotheses. The type-0x11 branch remains conditional, and the fallback's returned pointers remain opaque. No zero-XP result or global no-skill conclusion follows.

## Exact next discriminant

Follow the independent +0x9A0/+0x9A8 model-resource producer from FUN_140216b40 through its adapter callbacks and compare the exact returned/finalizer vtable against the mapped teardown sites. Retain each unresolved metadata table entry as data-selected.
""")
 manifest=TX/"EV-0348-capture-manifest.json"
 put(manifest,json.dumps({"evidence_id":"EV-0348","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"captures":rows},indent=2))
 hashes[note.relative_to(ROOT).as_posix()]=digest(note); hashes[manifest.relative_to(ROOT).as_posix()]=digest(manifest)
 docs={
 "README.md":"# EXP-0086 — +0x9D0 descriptor lookup screen\n\nTrace the data-selected descriptor fallback and test whether its lookup code exposes a concrete return class or finalizer.\n",
 "hypothesis.md":"# Competing models\n\n- Q64-H1: the returned metadata object's concrete finalizer descendants do not reach AV11/AV12 skill progress.\n- Q64-H2: at least one returned-object descendant routes AV11/AV12 into skill progress.\n\nA descriptor lookup result without a class and argument path does not distinguish these models.\n",
 "protocol.md":"# Protocol\n\nQuery the existing GOG 1.6.1179.0 project read-only through the strict dispatcher. Preserve function identity, callers, table offsets, keys and return expressions. Do not assign a class to data-selected pointers.\n",
 "results.md":"# Results\n\nThe +0x9D0 fallback checks descriptor key 2, then key 1, and returns an opaque 64-bit table value. The helper bodies expose table layout and selection but no constructor, concrete vtable, or skill sink [EV-0348].\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- A producer-backed concrete class/finalizer path to Actor::UseSkill AV11/AV12 supports Q64-H2 for that branch.\n- A resolved path avoiding the mapped sink narrows Q64-H1 to that branch.\n- Opaque descriptor values and absence of a direct sink in lookup helpers are inconclusive.\n",
 "implications.md":"# Implications\n\nThe +0x9D0 metadata fallback is a data lookup, not a statically resolved object construction path in the audited bodies. Continue through independent model-resource producers.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Identify the exact data entry selected by the producer.\n2. Recover its runtime class/vtable and slot +0x8 finalizer.\n3. Trace descendants to the mapped AV11/AV12 skill-progress sink.\n4. Keep type-0x11 and all unresolved table values conditional.\n"}
 for n,s in docs.items(): put(EXP/n,s)
 for f in EXP.iterdir():
  if f.is_file(): hashes[f.relative_to(ROOT).as_posix()]=digest(f)
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0348","kind":"native","source":"Read-only GOG Ghidra traces of the +0x9D0 descriptor fallback and its two metadata table lookup helpers.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0348-note.md","sha256":digest(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],"coverage":"Three complete function queries map the +0x9D0 fallback's key-2/key-1 descriptor lookups. The selected entry values, concrete classes, finalizers and AV11/AV12 descendants remain unresolved.","result":"FUN_140e84ad0 selects descriptor table values using key 2 then key 1; FUN_140e83f10 and FUN_140e84220 scan count/pointer-backed 16-byte entries and return opaque 64-bit data. No concrete class, vtable, slot +0x8 target or skill-sink edge is resolved. Q64-H1/H2 remain proposed.","related_evidence":["EV-0332","EV-0328","EV-0346","EV-0347","EV-0217","EV-0220","EV-0221"],"local_hashes":hashes})
 put(ep,json.dumps(evidence,indent=2,ensure_ascii=False))
 claims=ROOT/"research/CLAIMS.md"; c=claims.read_text()
 if "| CL-L186 |" in c: raise SystemExit("CL-L186 already exists")
 put(claims,c.rstrip()+"\n| CL-L186 | In GOG AE 1.6.1179.0, the mapped FUN_140e84ad0 fallback checks descriptor entry key 2 and then key 1; FUN_140e83f10/FUN_140e84220 scan count/pointer-backed 16-byte entries and return opaque 64-bit values. | supported for the bounded lookup bodies | [EV-0348], [EV-0332] | The selected entry data's concrete class/vtable, finalizer descendants, and AV11/AV12 reachability remain unresolved. |")
 mech=ROOT/"research/MECHANISMS.md"
 put(mech,mech.read_text().rstrip()+"\n\n## M-0068 — Descriptor-selected +0x9D0 fallback values (Q-0064)\n\nThe mapped metadata fallback checks key 2 and then key 1 in descriptor-backed arrays; the helpers return 64-bit entry values without establishing the selected object's class or vtable [EV-0348]. The separate type-0x11 path remains conditional [EV-0332]. Claim CL-L186 -> M-0068. This does not establish or exclude an AV11/AV12 skill-progress descendant.\n")
 graph=ROOT/"research/KNOWLEDGE_GRAPH.md"
 put(graph,graph.read_text().rstrip()+"\n\nEV-0348 bounds the +0x9D0 metadata fallback to key-2/key-1 descriptor-table lookups that return data-selected 64-bit values. Neither helper body provides a concrete finalizer or Actor::UseSkill edge, so Q64-H1/H2 remain unresolved and no no-skill edge is added. The independent +0x9A0/+0x9A8 model-resource path remains the next static discriminator [EV-0333]. Claim CL-L186 -> M-0068.\n")
 idx=ROOT/"experiments/README.md"; put(idx,idx.read_text().rstrip()+"\n\nEXP-0086 / EV-0348 maps the +0x9D0 descriptor fallback's key-2/key-1 table lookup; selected object classes remain data-dependent.\n")
 roadmap=ROOT/"research/ROADMAP.md"; put(roadmap,roadmap.read_text().rstrip()+"EV-0348 maps the +0x9D0 fallback to descriptor key-2/key-1 lookup values but does not resolve their concrete classes or finalizers. Continue through the independent +0x9A0/+0x9A8 model-resource producer and compare exact vtables; preserve unresolved data branches. Claim CL-L186 -> M-0068.\n")
 fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text())
 q64=next(x for x in frontier["items"] if x.get("id")=="Q-0064"); q65=next(x for x in frontier["items"] if x.get("id")=="Q-0065")
 for item in (q64,q65):
  if "EV-0348" not in item.setdefault("evidence",[]): item["evidence"].append("EV-0348")
  for h in item.get("hypotheses",[]):
   if "EV-0348" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0348")
  if "CL-L186" not in item.setdefault("linked_claims",[]): item["linked_claims"].append("CL-L186")
 q64["next_action"]="Follow the independent +0x9A0/+0x9A8 model-resource producer from FUN_140216b40 through its adapter callbacks and candidate setter FUN_1407445d0. Recover the exact returned-object vtable and slot +0x8 finalizer if the producer data permits; compare against the cleanup sites and screen resolved descendants for Actor::UseSkill AV11/AV12. Keep descriptor values and NIF root classes unresolved where data-selected."
 q65["next_action"]="Compare producer-backed concrete tables for +0x8F8, +0x730, +0x9D0, +0x9A0/+0x9A8, and ThirdPersonState+0xA0. EV-0348 shows +0x9D0 returns descriptor-selected values without a concrete class; do not count generic refcount ABI as a shared NiNode family."
 if not any(a.get("action_key")=="q65-descriptor-fallback-bounded" for a in q65.get("attempts",[])):
  q65.setdefault("attempts",[]).append({"action_key":"q65-descriptor-fallback-bounded","outcome":"EV-0348 maps the +0x9D0 fallback to descriptor-selected opaque values but recovers no concrete class/vtable; this is inconclusive for Q65-H1/H2.","evidence":["EV-0348"],"new_discriminant":"Exact producer-selected entry values must resolve to matching or differing concrete vtables before class-family comparison.","next_action":q65["next_action"]})
 put(fp,json.dumps(frontier,indent=2,ensure_ascii=False))
 cp=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; s=cp.read_text()
 old="- Q-0064 / EV-0347 ties PlayerCharacter+0x8F8 to `Actors\\\\Character\\\\1stPerson\\\\Skel` through the generic mesh loader. The exact NIF root class and slot +0x8 descendants remain unresolved; the +0x730 scan adds no concrete class.\n"
 new=old+"- Q-0064 / EV-0348 maps the +0x9D0 fallback to descriptor key-2/key-1 values, with the concrete object class still data-dependent. The next path is the +0x9A0/+0x9A8 model resource.\n"
 if old not in s: raise SystemExit("checkpoint EV-0347 line missing")
 put(cp,s.replace(old,new))
 print("registered EV-0348 / CL-L186 / M-0068; Q-0064 continues through +0x9A0/+0x9A8")
if __name__=="__main__": main()
