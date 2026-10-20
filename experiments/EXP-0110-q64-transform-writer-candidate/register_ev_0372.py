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
 "20261018T092923Z":{"requested_search_displacement":"0x40"},
 "20261018T102003Z":{"requested_search_displacement":"0x48"},
 "20261018T112519Z":{"requested_rva":"0xB48150"},
}
MARKERS={
 "20261018T092923Z":["OFFSET_WRITER_CANDIDATE=FUN_140b48150"],
 "20261018T102003Z":["OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=2301"],
 "20261018T112519Z":["MOVAPS xmmword ptr [RCX + 0x40], XMM1","XREF_CALL_EDGE=140b5760b -> 140b48150","XREF_CALL_EDGE=140b59f1f -> 140b48150","INCOMING_CALLER_FUNCTION_COUNT=3","DECOMPILATION_END=FUN_140b48150"],
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
 if any(x.get("id")=="EV-0372" for x in ev["items"]): raise SystemExit("EV-0372 exists")
 note=TX/"EV-0372-note.md"
 write(note,f"""# EV-0372 — +0x40 transform writer receiver classification

## Build and competing models

The writer scan and targeted function query use the existing GOG AE 1.6.1179.0 SkyrimSE.exe project, binary SHA-256 {BIN}, in read-only/no-analysis mode. H1 predicts FUN_140b48150 writes hkpConstraintInstance callback storage. H2 predicts its +0x40 access belongs to another receiver/payload. Exact instruction width, data type, allocation size, caller argument flow and the instance constructor's stored data argument discriminate the models.

## Direct observations

- FUN_140b48150 is in the complete +0x40 direct-writer candidate set; the +0x48 scan does not list it [captures 20261018T092923Z, 20261018T102003Z; candidate pool summarized in EV-0369].
- Its machine code writes 16-byte vector values at receiver offsets +0x30, +0x40 and +0x50. The decompiler shows four float components at +0x40 through +0x4c; this is a vector write, not an 8-byte callback pointer plus encoded count [capture 20261018T112519Z].
- Two incoming callers, FUN_140b57550 and FUN_140b59e80, allocate 0xe0-byte objects, call FUN_140b47d90 and then populate those objects with FUN_140b48150. Each passes the returned object as the fourth argument to FUN_140b48720 [capture 20261018T112519Z].
- FUN_140b48720 stores its fourth argument at the constructed hkpConstraintInstance +0x18; its own +0x40/+0x48 callback array starts empty [EV-0365, EV-0366]. Thus the candidate writer's +0x40 is on the separate constraint-data object, not the instance callback array.

## Result and uncertainty

H2 is supported for FUN_140b48150. This candidate is excluded as an hkpConstraintInstance callback producer for the captured callers. The third analyzed caller and other same-offset candidates remain independently unresolved; this result does not prove callback-array emptiness after later virtual dispatch or world/island setup, and it says nothing about AV11/AV12 or Steam gameplay.

## Exact next action

Query FUN_140b49260, another nearby +0x40 direct-writer candidate, with incoming/outgoing call edges. Establish its exact receiver and field width before deciding whether it advances the callback producer search.
""")
 docs={
  "README.md":"# EXP-0110 — transform writer receiver classification\n\nClassify FUN_140b48150's +0x40 direct-writer candidate by exact instruction width and caller data flow.\n",
  "hypothesis.md":"# Competing models\n\n- H1: FUN_140b48150 populates hkpConstraintInstance callback storage.\n- H2: its +0x40 write belongs to a separate receiver or payload.\n\n",
  "protocol.md":"# Protocol\n\nVerify candidate membership in both displacement scans, inspect the exact instruction width and function body, then trace caller allocation and argument flow into the known hkpConstraintInstance constructor.\n",
  "expected-discriminants.md":"# Expected discriminants\n\nAn exact callback write must target the hkpConstraintInstance receiver and its pointer/count representation. A vector-width write to a separately allocated object passed as instance data supports the false-positive model.\n",
  "results.md":"# Results\n\nFUN_140b48150 writes four float components through +0x4c as part of 16-byte vectors. Captured callers pass its separately allocated 0xe0-byte object to hkpConstraintInstance construction at +0x18. This candidate does not populate the callback array. See EV-0372.\n",
  "implications.md":"# Implications\n\nThe +0x40 candidate is a receiver collision, not evidence of callback registration. Continue with direct receiver and argument-flow checks; Q-0064 remains open.\n",
 }
 for n,s in docs.items(): write(EXP/n,s)
 mf=TX/"EV-0372-capture-manifest.json"; hashes={}; summaries=[]
 for stamp,m,mp,out in caps:
  hashes[mp.relative_to(ROOT).as_posix()]=sha(mp)
  for a in m.get("artifacts",{}).values():
   p=ROOT/a
   if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
  summaries.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
   "requested_search_displacement":m.get("requested_search_displacement"),"checks":m.get("checks"),
   "stdout_sha256":m.get("stdout_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")})
 hashes[note.relative_to(ROOT).as_posix()]=sha(note); hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
 for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
 write(mf,json.dumps({"evidence_id":"EV-0372","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":summaries,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
 hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
  "id":"EV-0372","kind":"native","source":"Identity-checked read-only GOG Ghidra classification of a +0x40 writer candidate and its constructor callers.",
  "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0372-note.md","sha256":sha(note),
  "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
  "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
  "coverage":"FUN_140b48150 machine/decompiler field accesses, direct callers, and allocation/constructor argument context.",
  "result":"FUN_140b48150 writes 16-byte vector values, including four floats at +0x40..+0x4f, on a separate 0xe0-byte object passed as hkpConstraintInstance data at +0x18. It does not write the callback pointer/count.",
  "related_evidence":["EV-0365","EV-0366","EV-0369"],"local_hashes":hashes})
 write(ep,json.dumps(ev,indent=2,ensure_ascii=False))
 cp=ROOT/"research/CLAIMS.md"
 append_once(cp,"| CL-L212 |","| CL-L212 | In the analyzed GOG AE 1.6.1179.0 callers, FUN_140b48150 writes vector components at +0x40..+0x4f on a separate 0xe0-byte object passed as hkpConstraintInstance data at +0x18; this candidate does not populate the instance callback pointer/count. | supported for the captured callers | [EV-0372], [EV-0365], [EV-0366] | Other callers/candidates and post-construction callback population remain unresolved. |")
 append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-WRITER-48150","""## C-OBJ2-Q64-WRITER-48150 — +0x40 writer candidate

- **Model A:** FUN_140b48150 populates the hkpConstraintInstance callback pointer/count.
- **Model B:** it writes a vector in separate constraint-data storage.
- **Evidence:** exact machine code uses a 16-byte MOVAPS at receiver +0x40, callers allocate 0xe0-byte objects and pass the result as hkpConstraintInstance data at +0x18 [EV-0372, EV-0365].
- **Assessment:** B is supported for the captured callers. Other callers or candidates are not classified by this result.
- **Discriminant:** inspect the next receiver-backed candidate's exact write width and constructor path.""")
 append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0372 classifies FUN_140b48150 as a transform writer","EV-0372 classifies FUN_140b48150's +0x40 access as a 16-byte vector write on separate 0xe0-byte constraint-data storage, which hkpConstraintInstance retains at +0x18. The candidate adds no edge to callback registration or AV11/AV12 [CL-L212].")
 fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
 if q.get("status")!="in_progress": raise SystemExit("Q-0064 inactive")
 if "EV-0372" not in q.setdefault("evidence",[]): q["evidence"].append("EV-0372")
 for h in q.get("hypotheses",[]):
  if "EV-0372" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0372")
 if "CL-L212" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L212")
 q["next_action"]="Query FUN_140b49260, another nearby +0x40 direct-writer candidate, with incoming/outgoing call edges. Establish its exact receiver and field width before deciding whether it advances the callback producer search."
 q.setdefault("methods",[]).append("EV-0372 excludes FUN_140b48150 as a callback producer for the captured callers because it writes vector data on the separate constraint-data object.")
 write(fp,json.dumps(fr,indent=2,ensure_ascii=False))
 append_once(ROOT/"STATE.md","Q-0064 / EV-0372","- Q-0064 / EV-0372 classifies FUN_140b48150's +0x40 operation as a 16-byte vector write on separate constraint-data storage retained at instance +0x18. This candidate is excluded for the captured callers; callback population after construction remains open. Next query FUN_140b49260.")
 append_once(ROOT/"ROADMAP.md","EV-0372 excludes a transform writer","EV-0372 confirms FUN_140b48150 writes transform vector data on the separate constraint-data receiver, not the callback array. Continue Q-0064 with receiver-backed candidates [CL-L212].")
 append_once(ROOT/"experiments/README.md","EXP-0110 / EV-0372","EXP-0110 / EV-0372 classifies FUN_140b48150 as a transform vector writer on constraint-data storage; the callback producer search continues.")
 print("Registered EV-0372 / CL-L212; Q-0064 remains active on candidate receiver classification.")

if __name__=="__main__": main()
