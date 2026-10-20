#!/usr/bin/env python3
"""Register the exact hkpConstraintInstance gate in the trap-hit cleanup helper."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=ROOT/"experiments/EXP-0094-q64-hkp-constraint-registration-gate"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
EXPECTED={
"20261018T070353Z":["DECOMPILATION_BEGIN=FUN_140b3a830","INDIRECT_CALL_SITE_COUNT=1","FUN_140e86bf0"],
"20261018T070548Z":["DECOMPILATION_BEGIN=FUN_140b3ac30","INDIRECT_CALL_SITE=140b3ac8e CALL qword ptr [RAX + 0x20]"],
"20261018T070646Z":["DECOMPILATION_BEGIN=FUN_140b48720","hkpConstraintInstance::vftable","FUN_140ecdfc0"],
"20261018T070746Z":["POINTER_TABLE_BASE_RVA=0x1973D58","POINTER_TABLE_ENTRY=index:4","POINTER_TABLE_ENTRY=index:6"],
"20261018T070840Z":["DECOMPILATION_BEGIN=FUN_140b37a30","return 0;"],
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s.rstrip()+"\n",encoding="utf-8")
def capture(stamp):
    mp=GH/f"gog-query-{stamp}.meta.json"
    m=json.loads(mp.read_text(encoding="utf-8"))
    raw=ROOT/m["artifacts"]["stdout"]; c=m.get("checks",{})
    ok=(m.get("analysis_distribution")=="GOG"
      and m.get("analysis_binary_product_version")=="1.6.1179"
      and m.get("analysis_binary_sha256")==BINARY
      and m.get("program_executable_path_matches_gog_binary") is True
      and m.get("ok") is True and m.get("exit_code")==0
      and m.get("read_only") is True and m.get("auto_analysis_disabled") is True
      and m.get("import_attempted") is False and m.get("overwrite_attempted") is False
      and c.get("program_identity_matches_gog_binary") is True
      and c.get("script_no_error") is True and sha(raw)==m.get("stdout_sha256"))
    if not ok: raise SystemExit(f"capture identity/completion failed: {stamp}")
    text=raw.read_text(errors="replace")
    if any(x not in text for x in EXPECTED[stamp]): raise SystemExit(f"capture marker failed: {stamp}")
    return m,mp,raw

def main():
    caps={s:capture(s) for s in EXPECTED}
    note=TX/"EV-0356-note.md"
    put(note,f"""# EV-0356 — The created hkpConstraintInstance skips one removal branch

## Build and method

Five identity-checked queries used the existing GOG Skyrim AE 1.6.1179.0 project, binary SHA-256 {BINARY}, in read-only/no-analysis mode through the strict dispatcher. Raw captures and hashes are listed in the manifest. These GOG RVAs are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- EV-0355 mapped the ProcessTrapHit caller into FUN_140e86bf0, which calls FUN_140b3a830 when its mode field is zero. That helper has one indirect call at receiver slot +0x30 and calls FUN_140b3ac30 only if the result equals 1 [capture 20261018T070353Z].
- The exact child factory path is FUN_140ef43b0 -> FUN_140ecdfc0 -> FUN_140b48720. FUN_140b48720 installs hkpConstraintInstance::vftable and initializes its fields; FUN_140ecdfc0 passes that returned object through the bhkConstraint setter to the child object's +0x10 member [captures 20261018T064133Z; 20261018T070646Z].
- The exact hkpConstraintInstance table at GOG RVA 0x1973D58 maps slot +0x30/index 6 to FUN_140b37a30 [capture 20261018T070746Z]. That function has no calls and returns zero [capture 20261018T070840Z].
- Therefore, for this factory-created hkpConstraintInstance, FUN_140b3a830's equality-to-one condition is false and the FUN_140b3ac30 list-removal branch is not taken. This says nothing about other classes passed to FUN_140b3a830 through its other callers.
- FUN_140b3ac30's slot +0x20 call enumerates related objects before removing references, but its route is excluded for this exact factory-created instance by the zero-returning +0x30 callback [capture 20261018T070548Z].
- The remainder of FUN_140b3a830 performs guarded physics-object registration, connection-list updates, and reference handling. The captured branch contains no Actor::UseSkill or AV11/AV12 argument. Remaining ProcessTrapHit indirect sites are not covered.

## Cross-domain synthesis

EV-0326 is a five-official-master Dawnguard source result for the Fort dialogue route to a VQ01 stage request; EV-0356 is static GOG native-code evidence for a ProcessTrapHit physics-constraint branch. Their provenance and object layers differ. The current evidence supports no causal edge between level-one quest entry and armor XP/protection. This is an unsupported connection, not proof of universal independence. A direct shared native call, shared state-bearing field, or a same-build discriminating event trace would falsify the no-edge assessment.

## Result and limits

The concrete constraint callback path is more narrowly physics-specific than EV-0355 alone established: the factory-created hkpConstraintInstance returns zero from the exact type-check slot, bypassing the one conditional removal branch. This strengthens Q64-H1 for this branch, but Q64-H1/H2 remain proposed for the larger ProcessTrapHit tree. Other callbacks, the exact scene/body instance identity, positive protected damage, effective armor, unchanged raw AVSK, and Steam runtime behavior remain unresolved.

## Exact next action

Continue with the remaining ProcessTrapHit indirect sites that can reach Actor::UseSkill slot +0xF7 or the mapped skill-progress sink. Preserve the unsupported OBJ-1/OBJ-2 edge unless a direct shared call/state path or discriminating same-build experiment appears.
""")
    rows={}
    for s,(m,mp,raw) in caps.items():
        rows[s]={"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
          "requested_pointer_table_rva":m.get("requested_pointer_table_rva"),"checks":m.get("checks"),
          "stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),
          "query_script_sha256":m.get("query_script_sha256")}
    manifest=TX/"EV-0356-capture-manifest.json"
    put(manifest,json.dumps({"evidence_id":"EV-0356","analysis_binary_product_version":"1.6.1179.0",
      "analysis_binary_sha256":BINARY,"captures":rows},indent=2))
    docs={
      "README.md":"# EXP-0094 — hkpConstraintInstance registration gate\n\nResolve the exact virtual type-check branch in the physics helper reached from the ProcessTrapHit constraint cleanup path.\n",
      "hypothesis.md":"# Competing models\n\n- Q64-H1: the mapped child cleanup stays within physics state and object lifetime handling.\n- Q64-H2: a concrete descendant reaches Actor::UseSkill with AV11/AV12.\n\nResolve the producer-backed dynamic receiver before counting a conditional branch.\n",
      "protocol.md":"# Protocol\n\nTrace from the exact constraint factory to its installed hkpConstraintInstance table, then inspect the called slot. Keep other callers of the shared helper separate.\n",
      "results.md":"# Results\n\nThe factory-created hkpConstraintInstance uses an exact slot+0x30 target that returns zero. FUN_140b3a830 therefore skips its conditional FUN_140b3ac30 branch for this object. The path remains physics registration/reference handling; this does not classify other callers or the remaining ProcessTrapHit sites [EV-0356].\n",
      "predicted-outcomes.md":"# Predicted outcomes\n\n- A nonzero type-check target on the exact receiver would activate the list-removal branch and require separate tracing.\n- The observed zero return rules out that branch for this factory-created class only.\n- A remaining concrete AV11/AV12 skill sink would support Q64-H2; otherwise the branch-specific Q64-H1 model strengthens.\n",
      "implications.md":"# Implications\n\nOne conditional helper branch is now excluded for the exact generated constraint class. No armor XP behavior or live protection result follows from this source trace.\n",
      "expected-discriminants.md":"# Expected discriminants\n\n1. Trace remaining ProcessTrapHit indirect sites to Actor::UseSkill slot +0xF7.\n2. Resolve the exact ActorValue argument at any such call.\n3. Preserve positive-damage, effective-protection, and raw-AVSK runtime measurements as separate tests.\n"}
    for n,t in docs.items(): put(EXP/n,t)
    hashes={}
    for s,(m,mp,raw) in caps.items():
        for p in [mp,raw]+[ROOT/x for x in m["artifacts"].values()]:
            if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    for p in [note,manifest,*EXP.iterdir(),Path(__file__)]:
        if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
    put(manifest,json.dumps({"evidence_id":"EV-0356","analysis_binary_product_version":"1.6.1179.0",
      "analysis_binary_sha256":BINARY,"captures":rows,"registered_local_hashes":hashes},indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()]=sha(manifest)

    ep=ROOT/"research/EVIDENCE.json"; e=json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id")=="EV-0356" for x in e["items"]): raise SystemExit("EV-0356 already registered")
    e["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "edition":"AE","modified_state":False,"id":"EV-0356","kind":"native",
      "source":"Read-only GOG Ghidra queries of the factory-created hkpConstraintInstance and its physics-world registration callback.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0356-note.md",
      "sha256":sha(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
      "coverage":"Constraint factory and hkpConstraintInstance table; FUN_140b3a830 slot+0x30 gate; conditional FUN_140b3ac30 branch and its exact type callback.",
      "result":"The factory-created hkpConstraintInstance uses slot+0x30 FUN_140b37a30, which returns zero, so FUN_140b3a830 skips its conditional FUN_140b3ac30 branch for this class. The mapped remaining path handles physics registration, object links, and references; other callers and ProcessTrapHit sites remain open.",
      "related_evidence":["EV-0355","EV-0326"],"local_hashes":hashes})
    put(ep,json.dumps(e,indent=2,ensure_ascii=False))

    cp=ROOT/"research/CLAIMS.md"; c=cp.read_text(encoding="utf-8")
    if "| CL-L195 |" in c: raise SystemExit("CL-L195 already exists")
    put(cp,c.rstrip()+"\n| CL-L195 | The hkpConstraintInstance created by the mapped trap-hit constraint factory returns zero from vtable slot +0x30, so FUN_140b3a830 skips its conditional FUN_140b3ac30 branch for that exact class. | supported for this factory-created class and branch | [EV-0356], [EV-0355] | Other callers of FUN_140b3a830 and the remaining ProcessTrapHit indirect sites remain unresolved. |\n| CL-L194 | Current evidence establishes no causal edge between the five-master Fort dialogue stage-request route and the GOG ProcessTrapHit physics-constraint branch. | no supported edge in the inspected source scopes | [EV-0326], [EV-0356] | A direct shared native call, state-bearing field, or discriminating same-build event trace would falsify this bounded no-edge assessment. |")
    mp=ROOT/"research/MECHANISMS.md"
    put(mp,mp.read_text(encoding="utf-8").rstrip()+"\n\n## M-0076 — hkpConstraintInstance gate skips conditional removal (Q-0064)\n\nThe child constraint factory installs hkpConstraintInstance::vftable. Its slot +0x30 target returns zero, while FUN_140b3a830 calls the related-object removal helper only when that result is one. The removal branch is therefore skipped for this factory-created class; the finding is limited to the captured producer and does not cover other helper callers [EV-0356]. Claim CL-L195 -> M-0076.\n")
    gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
    put(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0356 narrows the ProcessTrapHit constraint-helper branch: the factory-created hkpConstraintInstance's slot +0x30 returns zero, so its conditional list-removal path is skipped [EV-0355]. Cross-domain synthesis: EV-0326's five-master Dawnguard Fort stage-request route and EV-0356's GOG ProcessTrapHit physics branch have different provenance and no supported shared call/state dependency. Status: no causal edge established; falsifier: a direct shared native call, state-bearing field, or discriminating same-build event trace. Claim CL-L195 -> M-0076; CL-L194 records the bounded no-edge result.\n")
    ip=ROOT/"experiments/README.md"
    put(ip,ip.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0094 / EV-0356 resolves the factory-created hkpConstraintInstance slot+0x30 gate to zero, excluding one conditional physics list-removal branch for that exact class.\n")
    rp=ROOT/"research/ROADMAP.md"
    put(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0356 excludes FUN_140b3ac30 for the factory-created hkpConstraintInstance because its exact slot+0x30 returns zero. Continue with remaining ProcessTrapHit indirect sites against Actor::UseSkill slot +0xF7. Cross-domain review of EV-0326 and EV-0356 adds no quest-to-armor causal edge; a direct shared call/state dependency or same-build trace would falsify this [CL-L194].\n")

    fp=ROOT/"research/FRONTIER.json"; f=json.loads(fp.read_text(encoding="utf-8"))
    q63=next(x for x in f["items"] if x.get("id")=="Q-0063")
    q64=next(x for x in f["items"] if x.get("id")=="Q-0064")
    q65=next(x for x in f["items"] if x.get("id")=="Q-0065")
    for x in (q64,q65):
        if "EV-0356" not in x.setdefault("evidence",[]): x["evidence"].append("EV-0356")
        if "CL-L195" not in x.setdefault("linked_claims",[]): x["linked_claims"].append("CL-L195")
        for h in x.get("hypotheses",[]):
            if "EV-0356" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0356")
    if "EV-0356" not in q63.setdefault("evidence",[]): q63["evidence"].append("EV-0356")
    if "EV-0326" not in q64.setdefault("evidence",[]): q64["evidence"].append("EV-0326")
    if "CL-L194" not in q63.setdefault("linked_claims",[]): q63["linked_claims"].append("CL-L194")
    if "CL-L194" not in q64.setdefault("linked_claims",[]): q64["linked_claims"].append("CL-L194")
    q64["next_action"]="Continue with the remaining ProcessTrapHit indirect sites that can reach Actor::UseSkill slot +0xF7 or the mapped skill-progress sink. Keep the PlayerCamera-instance association unresolved unless exact receiver evidence establishes it."
    q64.setdefault("attempts",[]).append({"action_key":"q64-hkp-constraint-registration-gate",
      "outcome":"EV-0356 shows the exact factory-created hkpConstraintInstance slot+0x30 returns zero, so FUN_140b3a830 skips its conditional FUN_140b3ac30 branch for this class.",
      "evidence":["EV-0356"],"new_discriminant":"Other callers may pass different object classes; continue by resolving the remaining ProcessTrapHit indirect sites against Actor::UseSkill slot +0xF7.",
      "next_action":q64["next_action"]})
    q63.setdefault("attempts",[]).append({"action_key":"cross-domain-ev0326-ev0356-causal-edge-audit",
      "outcome":"EV-0326 and EV-0356 describe separate source scopes with no shared native call or state-bearing dependency in current evidence.",
      "evidence":["EV-0326","EV-0356"],"new_discriminant":"A direct shared call, state-bearing field, or discriminating same-build event trace would establish a testable cross-objective edge.",
      "next_action":q63.get("next_action","Retain the exact Steam level-one Fort dialogue and VQ01 state test.")})
    put(fp,json.dumps(f,indent=2,ensure_ascii=False))

    ck=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    src=ck.read_text(encoding="utf-8")
    needle="- Q-0064 / EV-0355 ties FUN_1406b9df0 to a flagged scene traversal that can append fixed/malleable physics constraints to rigid-body child vectors; mapped callbacks manipulate physics state, but FUN_140b3a830 descendants and remaining indirect sites stay open.\n"
    addition="- Q-0064 / EV-0356 maps the factory-created child payload as hkpConstraintInstance; its slot +0x30 returns zero, bypassing one conditional list-removal branch. CL-L194 records no supported causal edge between the EV-0326 Fort stage-request route and this OBJ-2 physics path; a shared call/state dependency would falsify it.\n"
    if needle not in src: raise SystemExit("checkpoint EV-0355 line missing")
    src=src.replace(needle,needle+addition)
    put(ck,src)
    print("registered EV-0356 / CL-L194 / CL-L195 / M-0076; Q-0064 continues")

if __name__=="__main__": main()
