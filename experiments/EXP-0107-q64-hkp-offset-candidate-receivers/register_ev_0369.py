#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
BIN="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPS={
 "20261018T105524Z":{"requested_rva":"0xB57860"},
 "20261018T105638Z":{"requested_rva":"0xB58550"},
 "20261018T105828Z":{"requested_rva":"0xB5B8D0"},
 "20261018T105942Z":{"requested_rva":"0xB5CD10"},
 "20261018T110047Z":{"requested_rva":"0xB5D800"},
 "20261018T110156Z":{"requested_rva":"0xB5D890"},
}
SCANS={
 "20261018T092923Z":{"requested_search_displacement":"0x40"},
 "20261018T102003Z":{"requested_search_displacement":"0x48"},
}
MARKERS={
 "20261018T105524Z":["hkpLinearParametricCurve::vftable","FUN_140b58550"],
 "20261018T105638Z":["FUN_140b57860","XREF_CALL_COUNT=0"],
 "20261018T105828Z":["hkpBallSocketChainData::vftable","FUN_140ef2060","FUN_140ef2450"],
 "20261018T105942Z":["hkpStiffSpringChainData::vftable","XREF_CALL_COUNT=0"],
 "20261018T110047Z":["hkpGenericConstraintData::vftable","FUN_140ef3f70"],
 "20261018T110156Z":["hkpGenericConstraintData::vftable","FUN_140b5e7d0","FUN_140a89e60"],
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s.rstrip()+"\n",encoding="utf-8")
def append_once(p,marker,body):
    old=p.read_text(encoding="utf-8")
    if marker in old: raise SystemExit("duplicate append: "+marker)
    write(p,old.rstrip()+"\n\n"+body.strip())

def load_capture(stamp,expected):
    mp=GH/f"gog-query-{stamp}.meta.json"
    if not mp.is_file(): raise SystemExit(f"missing metadata {stamp}")
    m=json.loads(mp.read_text(encoding="utf-8"))
    out=ROOT/m.get("artifacts",{}).get("stdout","")
    checks=m.get("checks",{})
    valid=(m.get("operation")=="existing_gog_project_read_only_query"
      and m.get("analysis_distribution")=="GOG"
      and m.get("analysis_binary_product_version")=="1.6.1179"
      and m.get("analysis_binary_sha256")==BIN and m.get("program")=="SkyrimSE.exe"
      and m.get("program_executable_path_matches_gog_binary") is True
      and m.get("exit_code")==0 and m.get("ok") is True
      and m.get("read_only") is True and m.get("auto_analysis_disabled") is True
      and m.get("import_attempted") is False and m.get("overwrite_attempted") is False
      and m.get("project_created") is False and bool(checks) and all(checks.values())
      and out.is_file() and sha(out)==m.get("stdout_sha256")
      and all(m.get(k)==v for k,v in expected.items()))
    if not valid: raise SystemExit(f"capture identity/policy/request/hash failed: {stamp}")
    raw=out.read_text(encoding="utf-8",errors="replace")
    if stamp in MARKERS:
        missing=[x for x in MARKERS[stamp] if x not in raw]
        if missing: raise SystemExit(f"markers missing {stamp}: {missing}")
    return stamp,m,mp,out,raw

def main():
    captures=[load_capture(s,e) for s,e in {**SCANS,**CAPS}.items()]
    by={x[0]:x for x in captures}
    ids={}
    for stamp in SCANS:
        found=set(re.findall(r"OFFSET_WRITER_CANDIDATE=([^ ]+)",by[stamp][4]))
        ids[stamp]=found
    if len(ids["20261018T092923Z"])!=3136 or len(ids["20261018T102003Z"])!=2301:
        raise SystemExit(f"unexpected direct-writer candidate counts: {len(ids['20261018T092923Z'])}, {len(ids['20261018T102003Z'])}")
    overlap=ids["20261018T092923Z"] & ids["20261018T102003Z"]
    if len(overlap)!=1271: raise SystemExit(f"unexpected overlap count: {len(overlap)}")

    ep=ROOT/"research/EVIDENCE.json"
    ev=json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id")=="EV-0369" for x in ev["items"]): raise SystemExit("EV-0369 exists")
    cp=ROOT/"research/CLAIMS.md"
    if "| CL-L209 |" in cp.read_text(encoding="utf-8"): raise SystemExit("CL-L209 exists")
    note=TX/"EV-0369-note.md"
    write(note,f"""# EV-0369 — hkp-region same-offset writer candidate receiver screen

## Build and method

Six targeted GOG AE 1.6.1179.0 Ghidra queries are validated against the existing analysis binary SHA-256 {BIN}; all run read-only with auto-analysis disabled. Two prior complete identity-checked displacement scans provide the candidate pools. Their candidate identities are extracted from the recorded raw output and intersected reproducibly: +0x40 has 3,136 direct-writer candidates, +0x48 has 2,301, with 1,271 identities in both. The scan's body sample is capped, so only the specifically queried receivers are classified here.

## Competing models

- H1: the screened same-offset hkp-region candidates write hkpConstraintInstance callback pointer/count at +0x40/+0x48.
- H2: those offsets belong to other Havok curve or constraint-data receivers.
- Exact vtable identity, constructor initialization, field shape and caller provenance discriminate these models. Results apply only to these six candidates.

## Direct observations

- FUN_140b57860 installs the named hkpLinearParametricCurve vtable and initializes fields including +0x40/+0x48. FUN_140b58550 allocates 0x50 bytes, calls that constructor, copies curve storage/count fields at +0x40/+0x48, and has no direct incoming call xrefs in the analyzed project [captures 20261018T105524Z, 20261018T105638Z].
- FUN_140b5b8d0 installs hkpBallSocketChainData vtable; +0x40/+0x48 are initialized with scalar constants while its point array/count are at +0x30/+0x38. Its two direct callers allocate 0x50-byte objects [capture 20261018T105828Z].
- FUN_140b5cd10 installs hkpStiffSpringChainData vtable and initializes +0x40/+0x48 as scalar constants; no direct incoming call xrefs are present [capture 20261018T105942Z].
- FUN_140b5d800 installs hkpGenericConstraintData vtable and initializes four separate array pointer/count regions through +0x7f; its callers allocate 0x80-byte objects [capture 20261018T110047Z].
- FUN_140b5d890 is the hkpGenericConstraintData destructor, reached by its deleting-destructor wrapper FUN_140b5e7d0. It releases that type's own array entries/storage; the offset is on a distinct receiver and does not dispatch the hkpConstraintInstance deletion-callback consumer [capture 20261018T110156Z].
- These exact bodies and vtable names classify the queried same-offset hits as other receiver layouts. They do not rule out any of the remaining 1,271 intersected functions or the other 0x40/+0x48 writer candidates.

## Result and uncertainty

H2 is supported for the six screened candidates; none populates the exact hkpConstraintInstance callback array. Same-offset screens are therefore insufficient without exact receiver provenance. The complete candidate intersection remains large, the remaining receiver identities are unresolved, and no edge to AV11/AV12 or zero armor XP is established.

## Exact next action

Trace hkpConstraintChainInstance vtable slot +0x20 target FUN_140b5d5d0 and its slot-0 finalizer FUN_140b36980. Determine whether either inherits or dispatches the exact hkpConstraintInstance deletion callback path, and whether any concrete registration helper writes the instance callback array. Continue candidate screening from the 1,271-function intersection only when receiver evidence is available.
""")
    docs={
      "README.md":"# EXP-0107 — hkp-region same-offset candidate receivers\n\nClassify selected +0x40/+0x48 candidates by exact Havok receiver and caller provenance. The remaining intersection is open.\n",
      "hypothesis.md":"# Competing models\n\n- H1: same-offset candidates write the hkpConstraintInstance callback array.\n- H2: those candidates belong to separate curve or constraint-data receiver layouts.\n\nVtable, constructor, field shape and caller context discriminate them.\n",
      "protocol.md":"# Protocol\n\nVerify both displacement scans and intersect complete candidate identity lists. Query exact candidates through the read-only GOG route. Classify receiver from vtable/constructor and callers before assigning semantics to offsets.\n",
      "expected-discriminants.md":"# Expected discriminants\n\nAn exact hkpConstraintInstance callback writer must have receiver provenance to that instance and manipulate the +0x40 pointer/+0x48 encoded callback count. Other named receiver vtables or scalar/array layouts support the false-positive model for that candidate only.\n",
      "results.md":"# Results\n\nThe two direct-writer candidate sets intersect in 1,271 functions. Six hkp-region candidates were queried; their exact receivers are curve or constraint-data classes, not hkpConstraintInstance. The larger candidate pool remains unresolved. See EV-0369.\n",
      "implications.md":"# Implications\n\nOffset matching alone does not establish callback registration. The queried candidates add no AV11/AV12 route and do not resolve Q64 globally. Exact chain-instance virtual dispatch and remaining receiver-backed writers are next.\n",
    }
    for n,s in docs.items(): write(EXP/n,s)

    mf=TX/"EV-0369-capture-manifest.json"
    hashes={}
    summaries=[]
    for stamp,m,mp,out,raw in captures:
        hashes[mp.relative_to(ROOT).as_posix()]=sha(mp)
        for a in m.get("artifacts",{}).values():
            p=ROOT/a
            if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        summaries.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
          "requested_search_displacement":m.get("requested_search_displacement"),"checks":m.get("checks"),
          "stdout_sha256":m.get("stdout_sha256"),"read_only":m.get("read_only"),"auto_analysis_disabled":m.get("auto_analysis_disabled")})
    hashes[note.relative_to(ROOT).as_posix()]=sha(note)
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
    scan_result={"direct_writer_counts":{"offset_0x40":len(ids["20261018T092923Z"]),"offset_0x48":len(ids["20261018T102003Z"]),"intersection":len(overlap)}}
    write(mf,json.dumps({"evidence_id":"EV-0369","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,
      "captures":summaries,"candidate_pool_result":scan_result,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
    hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
    ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
      "id":"EV-0369","kind":"native","source":"Identity-checked read-only GOG Ghidra exact-receiver classification of +0x40/+0x48 writer candidates.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0369-note.md","sha256":sha(note),
      "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
      "coverage":"Intersection of complete +0x40/+0x48 candidate identities and six exact hkp-region candidates; candidate body sample remains capped.",
      "result":"The two direct-writer sets contain 3,136 and 2,301 identities with 1,271 in common. Six queried candidates are hkpLinearParametricCurve, hkpBallSocketChainData, hkpStiffSpringChainData or hkpGenericConstraintData receivers; none is the exact hkpConstraintInstance callback-array writer.",
      "related_evidence":["EV-0365","EV-0366","EV-0368"],"local_hashes":hashes})
    write(ep,json.dumps(ev,indent=2,ensure_ascii=False))
    append_once(cp,"| CL-L209 |","| CL-L209 | In GOG AE 1.6.1179.0, six screened same-offset +0x40/+0x48 candidates in the hkp region are constructors/copy/destructor paths for hkpLinearParametricCurve, hkpBallSocketChainData, hkpStiffSpringChainData and hkpGenericConstraintData; none is the exact hkpConstraintInstance callback-array writer. | supported for these six candidates | [EV-0369] | The remaining candidate pool is large and unresolved; no AV11/AV12 or zero-armor-XP conclusion follows. |")
    append_once(ROOT/"research/MECHANISMS.md","## M-0088 — hkp offset candidates require exact receiver identity","""## M-0088 — hkp offset candidates require exact receiver identity

In the queried hkp-region candidates, +0x40/+0x48 denote curve fields, chain-data scalar parameters or GenericConstraintData-owned arrays depending on receiver type. The offset-only scan therefore does not identify the hkpConstraintInstance callback writer. Claim CL-L209 -> M-0088 [EV-0369].""")
    append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-HKP-OFFSET-RECEIVER","""## C-OBJ2-Q64-HKP-OFFSET-RECEIVER — same-offset writer candidates

- **Model A:** selected hkp-region +0x40/+0x48 candidates populate the exact hkpConstraintInstance deletion callback array.
- **Model B:** the same offsets belong to other Havok receiver layouts.
- **Evidence:** exact constructors/vtables identify curve and constraint-data classes for six queried candidates [EV-0369].
- **Assessment:** Model B is supported for those six only. The 1,271-function intersection and remaining writer candidates are unresolved.
- **Discriminant:** continue exact receiver/caller checks and trace a concrete instance callback registration path.""")
    append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0369 classifies six hkp-region candidates","EV-0369 classifies six hkp-region +0x40/+0x48 candidates as curve or constraint-data receiver paths, not the exact hkpConstraintInstance callback array. No edge to the callback entry slot +0x18 consumer or AV11/AV12 sink is added. The complete candidate intersection has 1,271 functions and remains open [CL-L209], [M-0088].")
    fp=ROOT/"research/FRONTIER.json"
    fr=json.loads(fp.read_text(encoding="utf-8"))
    q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
    if q.get("status")!="in_progress": raise SystemExit("Q-0064 inactive")
    if "EV-0369" not in q.setdefault("evidence",[]): q["evidence"].append("EV-0369")
    for h in q.get("hypotheses",[]):
        if "EV-0369" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0369")
    if "CL-L209" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L209")
    nxt="Trace hkpConstraintChainInstance vtable slot +0x20 target FUN_140b5d5d0 and slot-0 finalizer FUN_140b36980. Determine whether either reaches the exact hkpConstraintInstance deletion callback path or a concrete registration helper writes its callback array. Then select remaining candidates from the 1,271-function +0x40/+0x48 intersection using receiver provenance."
    q["next_action"]=nxt
    q.setdefault("methods",[]).append("EV-0369 uses exact receiver vtables and constructor/caller context to classify six same-offset hkp candidates; continue with chain-instance virtuals and do not treat the 1,271-function overlap as a writer verdict.")
    write(fp,json.dumps(fr,indent=2,ensure_ascii=False))
    append_once(ROOT/"STATE.md","Q-0064 / EV-0369","- Q-0064 / EV-0369 classifies six same-offset hkp candidates as curve or constraint-data receiver layouts. The +0x40/+0x48 direct-writer lists contain 1,271 shared function identities; exact callback producer remains unresolved. Next trace hkpConstraintChainInstance slot +0x20 FUN_140b5d5d0 and slot-0 FUN_140b36980.")
    append_once(ROOT/"ROADMAP.md","EV-0369 classifies six hkp-region same-offset candidates","EV-0369 classifies six hkp-region same-offset candidates as curve or constraint-data layouts. The direct writer candidate lists intersect in 1,271 functions; callback production remains open. Claim CL-L209 -> M-0088.")
    append_once(ROOT/"experiments/README.md","EXP-0107 / EV-0369","EXP-0107 / EV-0369 classifies six hkp-region +0x40/+0x48 candidates by exact receiver; the 1,271-function overlap remains open.")
    print("Registered EV-0369 and CL-L209/M-0088; Q-0064 remains active on chain-instance virtuals and exact callback writers.")

if __name__=="__main__": main()

