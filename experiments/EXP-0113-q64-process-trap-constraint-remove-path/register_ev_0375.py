#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
BIN="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPS={
"20261018T113835Z":("0xB3A830","direct_call_edge_census",["INDIRECT_CALL_SITE=140b3a88b CALL qword ptr [RAX + 0x30]","OUTGOING_DIRECT_CALL_EDGE=140b3a8bc -> 140b43ab0"]),
"20261018T113949Z":("0xB3A830","function_query",["DECOMPILATION_BEGIN=FUN_140b3a830","FUN_140b43ab0(param_1,param_3,1)"]),
"20261018T114052Z":("0xB67D60","direct_call_edge_census",["INDIRECT_CALL_SITE_COUNT=0","OUTGOING_DIRECT_CALL_EDGE=140b67e56 -> 140a8d670"]),
"20261018T114251Z":("0xB67350","direct_call_edge_census",["INDIRECT_CALL_SITE=140b673d9 CALL qword ptr [RAX + 0x10]","TtconRemCb"])}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
 p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def append_once(p,marker,body):
 old=p.read_text(encoding="utf-8")
 if marker in old: raise SystemExit("duplicate append: "+marker)
 write(p,old.rstrip()+"\n\n"+body.strip())
def main():
 evp=ROOT/"research/EVIDENCE.json"; evidence=json.loads(evp.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0375" for x in evidence["items"]): raise SystemExit("EV-0375 exists")
 caps=[]; hashes={}
 for stamp,(rva,mode,markers) in CAPS.items():
  mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text(encoding="utf-8"))
  out=ROOT/m["artifacts"]["stdout"]; checks=m.get("checks",{})
  ok=(m.get("operation")=="existing_gog_project_read_only_query" and m.get("analysis_distribution")=="GOG"
   and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BIN
   and m.get("program")=="SkyrimSE.exe" and m.get("program_executable_path_matches_gog_binary") is True
   and m.get("requested_rva")==rva and m.get("query_mode")==mode and m.get("exit_code")==0 and m.get("ok") is True
   and m.get("read_only") is True and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False
   and m.get("overwrite_attempted") is False and m.get("project_created") is False and bool(checks) and all(checks.values())
   and out.is_file() and sha(out)==m.get("stdout_sha256"))
  if not ok: raise SystemExit("capture identity/policy/hash failed: "+stamp)
  raw=out.read_text(encoding="utf-8",errors="replace")
  if any(x not in raw for x in markers): raise SystemExit("capture marker missing: "+stamp)
  caps.append({"stamp":stamp,"requested_rva":rva,"query_mode":mode,"checks":checks,"stdout_sha256":m["stdout_sha256"],"read_only":True,"auto_analysis_disabled":True})
  for p in (mp,out): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
  for rel in m.get("artifacts",{}).values():
   p=ROOT/rel
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
 note=TX/"EV-0375-note.md"
 write(note,f"""# EV-0375 — ProcessTrapHit constraint removal callbacks and endpoint record

## Build and competing models

Four fresh identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project in read-only/no-analysis mode. The analysis binary SHA-256 is {BIN}; GOG addresses do not transfer to Steam AE 1.6.1170.0. H1 predicts this ProcessTrapHit-associated branch performs constraint and endpoint bookkeeping without armor-skill progress. H2 predicts a populated callback entry or resolved descendant reaches Actor::UseSkill AV11/AV12. Concrete receiver flow, indirect target and argument evidence discriminate them; an unresolved callback remains open.

## Direct observations

- FUN_140b3a830 has one indirect call through its third argument's vtable slot +0x30. Its factory-created hkpConstraintInstance receiver returns zero at that slot, so the conditional FUN_140b3ac30 branch is skipped [EV-0356; capture 20261018T113835Z]. The helper then performs reference handling, invokes FUN_140b43ab0 with mode 1, updates the linked record through FUN_140b49450, and releases the reference [capture 20261018T113949Z].
- FUN_140b43ab0's mode-1 branch calls FUN_140b67350(param_2) followed by FUN_140b67d60(param_2). Here param_2 is the same factory-created hkpConstraintInstance passed by FUN_140b3a830 [captures 20261018T113949Z, 20261018T114052Z; EV-0355, EV-0356].
- FUN_140b67350 walks the instance callback array at +0x40 using the count at +0x48; each non-null entry receives the instance through its own virtual slot +0x10. The trace label is TtconRemCb. This is a concrete remove-callback consumer, but the entry class, slot target, and entry producer remain unresolved [capture 20261018T114251Z; EV-0361].
- FUN_140b67d60 removes the instance from its linked endpoint's +0x100 record array, decrements endpoint/count fields, compacts fixed-size records, and releases the object reference. Its census has two direct calls and zero indirect call sites; no Actor::UseSkill or AV11/AV12 argument appears in the captured body [capture 20261018T114052Z].
- The exact constructor starts callback storage empty and mapped wrapper setup does not write +0x40/+0x48 [EV-0365, EV-0366]. Those observations do not exclude later callback population. No complete writer census or concrete callback target is established here.

## Result and limits

H1 is strengthened for the resolved detach and endpoint-record branch: it performs physics callback dispatch and entity-record cleanup, with no mapped armor-skill sink in the direct body. H2 remains possible through the unresolved +0x10 callback target if an entry is later installed. This does not decide Q64 globally, prove zero armor XP, positive final damage, effective protection, Steam behavior, or vanilla reproduction. No causal edge to OBJ-1 is supported.

## Exact next action

Return to the eight indirect sites in FUN_14072fd60. Continue with the PlayerCharacter+0x8F8 release site at GOG address 0x140730647: use the existing FUN_140736be0/FUN_140e05900 producer trace to seek a concrete returned-object vtable and slot +0x8 finalizer. If the result stays data-selected because the skeleton NIF root is unavailable through a tested local parser, preserve this field as unresolved and move to another producer-backed teardown site. Keep the Steam hit/protection/raw-AVSK discriminator separate.
""")
 docs={
"README.md":"# EXP-0113 — ProcessTrapHit constraint removal path\n\nTrace the exact hkpConstraintInstance removal callback dispatcher and endpoint-record cleanup, preserving unresolved callback targets.\n",
"hypothesis.md":"# Competing models\n\n- H1: the exact detach branch performs physics and endpoint-record bookkeeping without armor skill credit.\n- H2: a populated removal callback or concrete descendant reaches Actor::UseSkill with AV11/AV12.\n",
"protocol.md":"# Protocol\n\nUse the identity-checked GOG project in read-only/no-analysis mode. Trace the ProcessTrapHit factory instance through FUN_140b3a830, FUN_140b43ab0, the removal callback consumer and endpoint record removal. Resolve targets only with exact receiver and argument evidence.\n",
"expected-discriminants.md":"# Expected discriminants\n\nDirect physics cleanup with no skill sink supports H1 only for the mapped branch. A concrete non-null callback target receiving the instance and reaching the AV11/AV12 skill sink supports H2. Unknown callback entries stay unresolved.\n",
"results.md":"# Results\n\nThe exact factory instance is passed through the mode-1 remove path; its callback loop dispatches non-null entries through slot +0x10, then the instance is removed from its endpoint record array. The entry class and target remain unknown. See EV-0375.\n",
"implications.md":"# Implications\n\nThe mapped detach body supports physics bookkeeping and adds no AV11/AV12 edge. Continue Q64 at a concrete PlayerCharacter teardown site; do not convert the unknown callback into a global negative.\n"}
 for n,s in docs.items(): write(EXP/n,s)
 manifest=TX/"EV-0375-capture-manifest.json"
 hashes[note.relative_to(ROOT).as_posix()]=sha(note); hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
 write(manifest,json.dumps({"evidence_id":"EV-0375","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":caps,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
 hashes[manifest.relative_to(ROOT).as_posix()]=sha(manifest)
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0375","kind":"native",
  "source":"Identity-checked GOG Ghidra trace of the ProcessTrapHit-associated hkpConstraintInstance removal callback and endpoint-record path.",
  "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0375-note.md","sha256":sha(note),
  "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.","lane":"mechanism_inference",
  "tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
  "coverage":"FUN_140b3a830 and direct callee/caller contexts; FUN_140b67d60 endpoint removal; FUN_140b67350 callback dispatch and analyzed direct/incoming call edges.",
  "result":"The exact ProcessTrapHit factory instance reaches mode-1 removal dispatch through callback slot +0x10 and endpoint-record compaction. Direct cleanup bodies show no AV11/AV12 sink; callback entry class, target and producer remain unresolved.",
  "related_evidence":["EV-0355","EV-0356","EV-0360","EV-0361","EV-0365","EV-0366","EV-0367","EV-0374"],"local_hashes":hashes})
 write(evp,json.dumps(evidence,indent=2,ensure_ascii=False))
 append_once(ROOT/"research/CLAIMS.md","| CL-L215 |","| CL-L215 | In the captured GOG ProcessTrapHit-associated hkpConstraintInstance detach branch, FUN_140b43ab0 reaches FUN_140b67350, which dispatches non-null +0x40/+0x48 callback entries through entry slot +0x10, then FUN_140b67d60 removes the constraint from its endpoint record; the direct cleanup body contains no mapped AV11/AV12 skill sink. | supported for this branch/build | [EV-0375], [EV-0355], [EV-0356] | Callback entry producer/class/target and the other PlayerCharacter cleanup sites remain unresolved. |")
 append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-REMOVE-CALLBACK","""## C-OBJ2-Q64-REMOVE-CALLBACK — constraint detach callback

- **Model A:** the ProcessTrapHit-associated detach path performs constraint/endpoint bookkeeping without armor-skill progress.
- **Model B:** a populated remove callback reaches Actor::UseSkill with AV11/AV12.
- **Evidence:** the exact factory instance reaches the +0x10 remove-callback dispatcher and endpoint record compaction; the callback target remains virtual and unresolved [EV-0375]. Constructor and wrapper setup evidence shows empty callback fields initially but does not exclude later population [EV-0365, EV-0366].
- **Assessment:** A is supported for the direct mapped body; B remains possible through an unresolved populated callback. Neither Q64 hypothesis is selected globally.
- **Falsifier for A:** producer-backed callback receiver/vtable and argument evidence that reaches the AV11/AV12 skill-progress sink.""")
 append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0375 maps a bounded constraint-removal branch","""### ProcessTrapHit constraint removal branch (EV-0375)

The factory-created hkpConstraintInstance reaches the mode-1 removal path through FUN_140b3a830/FUN_140b43ab0. FUN_140b67350 dispatches any non-null callback through its entry slot +0x10; FUN_140b67d60 removes the instance from its endpoint record. The callback class, writer and concrete target remain unresolved [CL-L215]. The mapped direct cleanup adds no Actor::UseSkill AV11/AV12 edge; no global negative or causal edge to OBJ-1 is supported.""")
 fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text(encoding="utf-8")); item=next(x for x in frontier["items"] if x.get("id")=="Q-0064")
 if item.get("status")!="in_progress": raise SystemExit("Q-0064 is not in progress")
 item["evidence"]=list(dict.fromkeys([*item.get("evidence",[]),"EV-0375"]))
 item["linked_claims"]=list(dict.fromkeys([*item.get("linked_claims",[]),"CL-L215"]))
 for h in item.get("hypotheses",[]): h["evidence"]=list(dict.fromkeys([*h.get("evidence",[]),"EV-0375"]))
 item.setdefault("methods",[]).append("EV-0375 resolves one ProcessTrapHit-associated detach branch through the removal callback consumer and endpoint record; callback target remains open, so continue at a concrete PlayerCharacter cleanup site.")
 item["next_action"]="Return to the eight indirect sites in FUN_14072fd60. Continue with the PlayerCharacter+0x8F8 release site at GOG address 0x140730647: use the existing FUN_140736be0/FUN_140e05900 producer trace to seek a concrete returned-object vtable and slot +0x8 finalizer. If the result stays data-selected because the skeleton NIF root is unavailable through a tested local parser, preserve this field as unresolved and move to another producer-backed teardown site. Keep the Steam hit/protection/raw-AVSK discriminator separate."
 write(fp,json.dumps(frontier,indent=2,ensure_ascii=False))
 append_once(ROOT/"STATE.md","Q-0064 / EV-0375","- Q-0064 / EV-0375 maps the ProcessTrapHit-associated constraint detach through the +0x10 removal-callback dispatcher and endpoint record compaction. Direct cleanup has no AV11/AV12 sink, but callback writer/class/target remain unknown. Resume at PlayerCharacter+0x8F8 and seek a concrete finalizer discriminator.")
 append_once(ROOT/"ROADMAP.md","EV-0375 constraint removal branch","EV-0375 bounds one ProcessTrapHit constraint detach branch to callback notification and endpoint record removal; callback targets remain unresolved. Continue Q-0064 at a concrete PlayerCharacter teardown field [CL-L215].")
 append_once(ROOT/"experiments/README.md","EXP-0113 / EV-0375","EXP-0113 / EV-0375 maps ProcessTrapHit constraint removal callbacks and endpoint record cleanup; Q-0064 continues at PlayerCharacter+0x8F8.")
 print("Registered EV-0375 / CL-L215; preserved the bounded branch result and selected PlayerCharacter+0x8F8 as the next discriminator.")
if __name__=="__main__": main()

