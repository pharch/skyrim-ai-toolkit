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
 "20261018T112751Z":{"requested_rva":"0xB49260"},
 "20261018T112918Z":{"requested_rva":"0xB67FB0"},
}
MARKERS={
 "20261018T112751Z":["MOVAPS xmmword ptr [RAX + 0x40], XMM1","INCOMING_CALLER_FUNCTION_COUNT=0","*(undefined8 *)(lVar5 + 0x48) = uVar4;"],
 "20261018T112918Z":["INCOMING_CALLER_FUNCTION_COUNT=8","if ((*param_3 == 0x1d)","*(short **)(param_1 + 0x20) = param_3;","*(longlong *)(param_1 + 0x60)"],
}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def append_once(p,marker,body):
 old=p.read_text(encoding="utf-8")
 if marker in old: raise SystemExit("duplicate append: "+marker)
 write(p,old.rstrip()+"\n\n"+body.strip())
def load(stamp,expected):
 mp=GH/f"gog-query-{stamp}.meta.json"; m=json.loads(mp.read_text(encoding="utf-8"))
 out=ROOT/m["artifacts"]["stdout"]; checks=m.get("checks",{})
 valid=(m.get("operation")=="existing_gog_project_read_only_query" and m.get("analysis_distribution")=="GOG"
  and m.get("analysis_binary_product_version")=="1.6.1179" and m.get("analysis_binary_sha256")==BIN
  and m.get("program")=="SkyrimSE.exe" and m.get("program_executable_path_matches_gog_binary") is True
  and m.get("exit_code")==0 and m.get("ok") is True and m.get("read_only") is True
  and m.get("auto_analysis_disabled") is True and m.get("import_attempted") is False
  and m.get("overwrite_attempted") is False and m.get("project_created") is False
  and bool(checks) and all(checks.values()) and out.is_file() and sha(out)==m.get("stdout_sha256")
  and all(m.get(k)==v for k,v in expected.items()))
 if not valid: raise SystemExit("capture identity/policy/request/hash failed: "+stamp)
 raw=out.read_text(encoding="utf-8",errors="replace")
 missing=[x for x in MARKERS[stamp] if x not in raw]
 if missing: raise SystemExit(f"capture markers missing {stamp}: {missing}")
 return stamp,m,mp,out

def main():
 caps=[load(s,e) for s,e in CAPS.items()]
 ep=ROOT/"research/EVIDENCE.json"; ev=json.loads(ep.read_text(encoding="utf-8"))
 if any(x.get("id")=="EV-0373" for x in ev["items"]): raise SystemExit("EV-0373 exists")
 note=TX/"EV-0373-note.md"
 write(note,f"""# EV-0373 — typed record candidate and recipient

## Build and competing models

Two identity-checked GOG AE 1.6.1179.0 queries used the existing SkyrimSE.exe project in read-only/no-analysis mode; analysis binary SHA-256 {BIN}. H1 predicts FUN_140b49260's +0x40/+0x48 pair is the hkpConstraintInstance callback pointer/count. H2 predicts the function writes a separate typed record consumed by another collection. Write width, allocation/type tag, recipient receiver fields and exact call edges discriminate the models.

## Direct observations

- FUN_140b49260 has zero analyzed incoming code callers. It calls FUN_140b68310(param_1,0x1b); if no type-0x1b record exists, it allocates 0x50 bytes, tags the record 0x1b, copies two 16-byte values to +0x30 and +0x40, then calls FUN_140b67fb0(param_1,param_1+0x10,record) [capture 20261018T112751Z].
- The machine code uses MOVAPS at receiver +0x40. The decompiler's +0x48 qword is the second half of the same 16-byte vector, not a separate 8-byte callback count. The helper's no-incoming-code result is scoped to this analyzed GOG listing; its data references are unresolved pointer/metadata tables.
- FUN_140b67fb0 has eight analyzed incoming callers, including FUN_140b49260. Its body handles type tags 0x1d and 0x1e in separate branches, links records through param_1+0x20 and a record reached through param_1+0x60, invokes a virtual slot +0x30 on param_2, and updates associated size/counter fields. This is typed-record/list management, not a demonstrated write to hkpConstraintInstance +0x40/+0x48 [capture 20261018T112918Z].
- No source-backed class identity or ProcessTrapHit edge is established for the type-0x1b record collection. The exact ProcessTrapHit constructor initializes the separate hkpConstraintInstance callback array empty [EV-0365, EV-0366].

## Result and uncertainty

H2 is supported for this candidate path: the observed +0x40/+0x48 accesses are a 16-byte vector in a 0x50-byte typed record, which is passed to a routine maintaining typed records and counters. The record's concrete class and any indirect route from the containing object to ProcessTrapHit remain unknown. This is a candidate-level exclusion only; other callbacks and later setup paths remain open, and no AV11/AV12 or Steam gameplay result follows.

## Exact next action

Return to the original Q-0064 teardown call sites and identify one unresolved indirect call with exact receiver, vtable and argument evidence. Trace that concrete target toward the already mapped Actor::UseSkill AV11/AV12 sink; do not use unrelated same-offset record writers as a proxy for the teardown route.
""")
 docs={
  "README.md":"# EXP-0111 — typed record recipient classification\n\nTest whether a shared-offset candidate is constraint callback storage or a separate typed record handled by FUN_140b67fb0.\n",
  "hypothesis.md":"# Competing models\n\n- H1: FUN_140b49260 writes hkpConstraintInstance callback pointer/count storage.\n- H2: it writes a separate typed record consumed by a distinct list manager.\n",
  "protocol.md":"# Protocol\n\nResolve the direct-writer instruction width, typed allocation branch, recipient body, incoming call edges, and exact receiver fields. Keep Ghidra's data-only references separate from code-call edges.\n",
  "expected-discriminants.md":"# Expected discriminants\n\nA callback writer must target the exact hkpConstraintInstance array representation. A 16-byte vector in a tagged 0x50-byte record, followed by typed-list/counter handling, supports the separate-record model for this candidate.\n",
  "results.md":"# Results\n\nFUN_140b49260's +0x40 write is a 16-byte vector in a 0x50-byte type-0x1b record. FUN_140b67fb0 links typed records and updates their list metadata; no exact hkpConstraintInstance or ProcessTrapHit connection is established. See EV-0373.\n",
  "implications.md":"# Implications\n\nThis narrows one shared-offset candidate and its recipient only. Return to concrete indirect call targets on the ProcessTrapHit teardown chain for the AV11/AV12 question.\n",
 }
 for n,s in docs.items(): write(EXP/n,s)
 mf=TX/"EV-0373-capture-manifest.json"; hashes={}; summaries=[]
 for stamp,m,mp,out in caps:
  hashes[mp.relative_to(ROOT).as_posix()]=sha(mp)
  for a in m.get("artifacts",{}).values():
   p=ROOT/a
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
  summaries.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
   "checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")})
 hashes[note.relative_to(ROOT).as_posix()]=sha(note); hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
 write(mf,json.dumps({"evidence_id":"EV-0373","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":summaries,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
 hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
  "id":"EV-0373","kind":"native","source":"Identity-checked read-only GOG Ghidra trace of a +0x40 record candidate and its typed-list recipient.",
  "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0373-note.md","sha256":sha(note),
  "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
  "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
  "coverage":"FUN_140b49260 exact vector-width writes, type-0x1b allocation and recipient call; FUN_140b67fb0 typed-list receiver fields and analyzed callers.",
  "result":"The +0x40/+0x48 view in FUN_140b49260 is a 16-byte vector in a tagged 0x50-byte record; FUN_140b67fb0 manages type-coded lists and counters. Neither exact hkpConstraintInstance callback ownership nor a ProcessTrapHit edge is established.",
  "related_evidence":["EV-0365","EV-0366","EV-0369","EV-0372"],"local_hashes":hashes})
 write(ep,json.dumps(ev,indent=2,ensure_ascii=False))
 cp=ROOT/"research/CLAIMS.md"
 append_once(cp,"| CL-L213 |","| CL-L213 | In the analyzed GOG AE 1.6.1179.0 candidate path, FUN_140b49260 stores a 16-byte vector in a tagged 0x50-byte type-0x1b record and passes it to FUN_140b67fb0, whose body maintains type-coded record lists and counters; this does not establish hkpConstraintInstance callback storage. | supported for the queried path/listing | [EV-0373], [EV-0365], [EV-0366] | Record class, indirect owner path and all other candidate writers remain unresolved. |")
 append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-WRITER-49260","""## C-OBJ2-Q64-WRITER-49260 — typed record candidate

- **Model A:** the decompiler's +0x40/+0x48 pair is the hkpConstraintInstance callback pointer/count.
- **Model B:** the machine instruction writes one 16-byte vector in a typed record managed by a separate list.
- **Evidence:** type tag 0x1b, 0x50-byte allocation, MOVAPS at +0x40, and recipient list/counter operations [EV-0373].
- **Assessment:** B is supported for the queried path. Concrete class and ProcessTrapHit ownership remain unresolved.
- **Discriminant:** resolve an exact unresolved teardown indirect call and its receiver/target instead of inferring from same-offset candidates.""")
 append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0373 separates a typed record from callback storage","EV-0373 classifies FUN_140b49260's +0x40 access as a vector in a tagged 0x50-byte record passed to a typed-list manager. It adds no causal edge from this record path to hkpConstraintInstance callback storage, ProcessTrapHit teardown or AV11/AV12 [CL-L213].")
 fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
 if q.get("status")!="in_progress": raise SystemExit("Q-0064 inactive")
 if "EV-0373" not in q.setdefault("evidence",[]): q["evidence"].append("EV-0373")
 for h in q.get("hypotheses",[]):
  if "EV-0373" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0373")
 if "CL-L213" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L213")
 q["next_action"]="Review EV-0325/EV-0319/EV-0324 captures and select one still-unresolved indirect call on the exact ProcessTrapHit PlayerCharacter teardown route. Query its concrete receiver/vtable target and arguments, then trace that target toward Actor::UseSkill AV11/AV12."
 q.setdefault("methods",[]).append("EV-0373 excludes one typed-vector/list candidate; return to the exact eight ProcessTrapHit teardown indirect callsites and avoid using unrelated offset collisions as proxies.")
 write(fp,json.dumps(fr,indent=2,ensure_ascii=False))
 append_once(ROOT/"STATE.md","Q-0064 / EV-0373","- Q-0064 / EV-0373 classifies the B49260 +0x40/+0x48 view as one 16-byte vector inside a tagged type-0x1b record handled by typed-list logic. No callback-array or ProcessTrapHit edge is established. Resume the exact eight teardown indirect callsites and resolve one concrete receiver/target.")
 append_once(ROOT/"ROADMAP.md","EV-0373 excludes a typed-vector record candidate","EV-0373 finds that the B49260 candidate belongs to a typed record/list path, with no callback-array or ProcessTrapHit edge. Return Q-0064 to the exact teardown indirect callsites [CL-L213].")
 append_once(ROOT/"experiments/README.md","EXP-0111 / EV-0373","EXP-0111 / EV-0373 classifies a same-offset candidate as a typed vector record/list path; Q-0064 returns to exact ProcessTrapHit teardown indirect calls.")
 print("Registered EV-0373 / CL-L213; returned Q-0064 to exact ProcessTrapHit teardown callsites.")

if __name__=="__main__": main()
