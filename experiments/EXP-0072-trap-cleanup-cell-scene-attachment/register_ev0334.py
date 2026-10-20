#!/usr/bin/env python3
"""Register the bounded GOG PlayerCharacter cell-scene attachment trace."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/".local/ghidra"
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=ROOT/"experiments/EXP-0072-trap-cleanup-cell-scene-attachment"
BINARY="9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES={
 "20261018T031930Z":["TARGET_RVA=0x7373E0","INDIRECT_CALL_SITE=1407375e4 CALL qword ptr [RAX + 0x1c0]","FUN_1402b8510(param_2)"],
 "20261018T032040Z":["TARGET_RVA=0x2B8510","FUN_1402b8510(longlong param_1)"],
 "20261018T032159Z":["VTABLE_BASE_RVA=0x19AC3F0","VTABLE_SLOT_INDEX=0x35","VTABLE_SLOT_TARGET_RVA=0xD1EB20"],
 "20261018T032254Z":["TARGET_RVA=0xD1EB20","FUN_140d1df50(param_2,param_1)"],
 "20261018T032526Z":["POINTER_TABLE_BASE_RVA=0x19AC3F0","POINTER_TABLE_ENTRY=index:53","POINTER_TABLE_ENTRY=index:56"],
 "20261018T032724Z":["TARGET_RVA=0xD200B0","NiNode::vftable","NiTObjectArray<class_NiPointer<class_NiAVObject>_>::vftable"],
 "20261018T032833Z":["TARGET_RVA=0xD1ED80","FUN_140d1ed80","plVar2[6] = 0"],
 "20261018T033013Z":["TARGET_RVA=0xD1ED30","FUN_140d1ed30","param_1 + 0x1b8"],
}
DIAGNOSTIC="20261018T032417Z"

def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def check_capture(stamp,markers):
    mp=GH/f"gog-query-{stamp}.meta.json"
    m=json.loads(mp.read_text(encoding="utf-8"))
    c=m.get("checks",{})
    if (m.get("analysis_distribution")!="GOG" or m.get("analysis_binary_product_version")!="1.6.1179"
      or m.get("analysis_binary_sha256")!=BINARY or m.get("exit_code")!=0 or m.get("ok") is not True
      or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True
      or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False
      or c.get("program_identity_matches_gog_binary") is not True or c.get("script_no_error") is not True):
        raise SystemExit("identity/read-only/completion check failed: "+stamp)
    out=ROOT/m["artifacts"]["stdout"]
    raw=out.read_text(encoding="utf-8",errors="replace")
    if h(out)!=m.get("stdout_sha256") or any(x not in raw for x in markers):
        raise SystemExit("capture/hash/marker failure: "+stamp)
    files=[mp]+[ROOT/x for x in m["artifacts"].values()]
    if any(not x.is_file() for x in files): raise SystemExit("missing raw capture: "+stamp)
    return m,{x.relative_to(ROOT).as_posix():h(x) for x in files}

def main():
    ep=ROOT/"research/EVIDENCE.json"
    ev=json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id")=="EV-0334" for x in ev["items"]): raise SystemExit("EV-0334 already registered")
    hashes={}
    rows=[]
    for stamp,markers in CAPTURES.items():
        m,hs=check_capture(stamp,markers); hashes.update(hs)
        rows.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
          "requested_vtable_slot":m.get("requested_vtable_slot"),"requested_pointer_table_rva":m.get("requested_pointer_table_rva"),
          "requested_pointer_count":m.get("requested_pointer_count"),"checks":m.get("checks"),
          "stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),
          "adapter_sha256":m.get("adapter_sha256"),"query_script_sha256":m.get("query_script_sha256")})
    dm=json.loads((GH/f"gog-query-{DIAGNOSTIC}.meta.json").read_text(encoding="utf-8"))
    diagnostic={"stamp":DIAGNOSTIC,"ok":dm.get("ok"),"checks":dm.get("checks"),
      "stdout_sha256":dm.get("stdout_sha256"),"diagnostic":"Single-slot query had xref_call_edge=false; excluded from positive claims. A complete pointer-table scan and a direct FUN_140d1ed30 query independently validate the needed table target/body."}
    for kind,rel in dm.get("artifacts",{}).items():
        p=ROOT/rel
        if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=h(p)

    note=TX/"EV-0334-note.md"
    put(note,f"""# EV-0334 — PlayerCharacter +0x730 cell-scene attach and detach

## Build and method

Eight successful read-only queries used the existing GOG Skyrim AE 1.6.1179.0 project; analysis binary SHA-256 {BINARY}. Metadata confirms matching program identity, auto-analysis disabled, successful completion, and no import or overwrite. A separate single-slot probe with one false direct-xref check is retained as a diagnostic and excluded from positive claims. A complete NiNode pointer-table scan and a direct removal-wrapper query independently validate that target. Full capture hashes are in the private manifest. No GOG RVA is transferred to Steam 1.6.1170.0.

## Direct observations

- PlayerCharacter primary slot 0x98 is FUN_1407373e0 [EV-0327]. On the cell-removal branch, if field +0x730 exists, the function loads its +0x30 pointer as a receiver, invokes receiver slot +0x1C0, then clears +0x730 and releases its reference. The child pointer remains in RDX at the callsite; exact dynamic parent vtable is not observed [capture 20261018T031930Z].
- On the cell-addition branch, FUN_1407373e0 calls FUN_1402b8510 on the incoming cell. That helper returns cell+0x130+8 when +0x130 is non-null. The caller selects child index 1 from a nested +0x118 array when count exceeds one, then calls its slot +0x1A8 with the PlayerCharacter +0x730 object and flag 1 [captures 20261018T031930Z, 20261018T032040Z].
- In the GOG NiNode vtable at RVA 0x19AC3F0, slot 0x35 (+0x1A8) is FUN_140d1eb20 and slot 0x38 (+0x1C0) is FUN_140d1ed30. The 57-entry pointer-table scan is complete and confirms both entries. NiNode constructor FUN_140d200b0 installs NiNode::vftable and a NiTObjectArray of NiAVObject smart pointers at the child-array region; its base initializer clears object+0x30 [captures 20261018T032159Z, 20261018T032526Z, 20261018T032724Z].
- FUN_140d1eb20 adds a child to the NiNode array and calls FUN_140d1df50(child,parent). FUN_140d1df50 checks an existing child+0x30 parent, calls that parent's slot+0x1C0 with the child if needed, then stores the new parent at child+0x30 [capture 20261018T032254Z].
- NiNode slot+0x1C0 FUN_140d1ed30 calls its slot+0x1B8 with the child and releases the returned reference. The NiNode slot+0x1B8 target FUN_140d1ed80 searches the child array, clears child+0x30 when found, removes the child entry, and balances references [captures 20261018T033013Z, 20261018T032833Z].
- Together, these operations make the +0x730 value behave as a refcounted NiAVObject-compatible scene child with a parent pointer at +0x30; the cell transition attaches it to a selected scene node and detaches it from its current parent. This is a strong static structural inference. The exact loaded parent vtable, the child object's concrete class, and its final slot+0x8 destructor remain unresolved.
- The inspected add/remove helpers contain no direct Actor::UseSkill or mapped AV11/AV12 sink. Removal/refcount release can still reach the child object's unresolved finalizer. Q64-H1/H2 therefore remain proposed.

## Cross-domain synthesis

EV-0334 connects the PlayerCharacter +0x730 lifetime to NiAVObject/NiNode parent-child management. EV-0331's +0x8F8 first-person skeleton is only a conditional NiNode candidate, and EV-0333's +0x9A0/+0x9A8 producer is a data-selected model resource; the current evidence does not prove those fields share a concrete vtable or finalizer with +0x730. No causal edge from these branches to the known Actor::UseSkill armor/enchanting sink is added, while unresolved child finalizers prevent a global negative [EV-0217]–[EV-0223], [EV-0280], [EV-0281], [EV-0331], [EV-0333]. The mapped Dawnguard Fort route remains a distinct record/Papyrus transition path with no observed ActorValue dependency [EV-0326].

## Exact next discriminant

Search for a non-null source of PlayerCharacter+0x730 or a typed constructor/assignment path for the child object, then recover the concrete parent and child vtables and final slot+0x8 target. If static data cannot select the child class, preserve that boundary and reselect an independent P0 line.
""")
    hashes[note.relative_to(ROOT).as_posix()]=h(note)
    docs={
      "README.md":"# EXP-0072 — PlayerCharacter cell-scene attachment\n\nQ-0064 trace of PlayerCharacter +0x730 through cell addition/removal and conditional NiNode parent-child methods. EV-0334 identifies a refcounted NiAVObject-compatible child pattern; the concrete child/finalizer remains unknown.\n",
      "hypothesis.md":"# Competing models\n\n- Q64-H1: relevant teardown descendants do not award AV11/AV12 skill progress.\n- Q64-H2: a relevant descendant reaches that sink with AV11/AV12.\n- Scene model A: PlayerCharacter +0x730 is an NiAVObject-compatible child attached to the cell scene, with +0x30 as parent and NiNode add/remove methods.\n- Scene model B: the same offsets are implemented by a different dynamic parent interface or subclass target.\n\nEV-0334 supports the structural child/parent relationship, but the runtime parent table and child finalizer remain unknown. None of the Q64 hypotheses is decided.\n",
      "protocol.md":"# Protocol\n\nUse only identity-checked GOG 1.6.1179.0 captures through the strict dispatcher in read-only, no-analysis mode. Treat NiNode vtable targets as conditional until the actual cell-scene parent table is observed. Preserve failed probes separately; never transfer GOG RVAs to Steam.\n",
      "predicted-outcomes.md":"# Predicted outcomes\n\nA concrete cell-scene NiNode parent and NiAVObject child type matching the captured add/remove functions supports Scene model A. A different observed parent table or field layout supports Scene model B. A resolved child finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2. A mapped finalizer without that path contributes to Q64-H1 but does not resolve other cleanup branches. Missing runtime class evidence is inconclusive.\n",
      "expected-discriminants.md":"# Expected discriminants\n\n- **H1:** the exact cell-scene parent uses the NiNode add/remove family, child+0x30 is its parent link, and a concrete child finalizer resolves.\n- **H2:** an observed parent table or field layout differs from the NiNode candidate.\n- A child finalizer reaching Actor::UseSkill with AV11/AV12 supports Q64-H2; missing runtime class evidence remains inconclusive. [EV-0334]\n",
      "results.md":"# Results\n\nEV-0334 maps a cell-transition attach/detach pattern for PlayerCharacter +0x730. The cell-add path selects a child scene node and calls its +0x1A8 method with the field object; the NiNode candidate implementation stores child+0x30 as parent. The cell-removal path reads child+0x30 and calls slot+0x1C0 with the child. NiNode table entries map these methods to add-child FUN_140d1eb20 and remove-child FUN_140d1ed30; the remove helper delegates to child-array removal FUN_140d1ed80.\n\nThis supports an NiAVObject-compatible child/parent structural inference but does not observe the actual parent table or child class. The child final slot+0x8 destructor remains dynamic, so Q64-H1/H2 are unchanged [EV-0334], [EV-0327], [EV-0331].\n",
      "implications.md":"# Implications\n\nThe +0x730 callback is a scene-child detach candidate rather than a resolved skill award. Compare it with the conditional +0x8F8 NiNode candidate and +0x9A0/+0x9A8 model-resource adapter only through concrete vtables/finalizers. Keep class equality and skill-sink reachability unresolved until those targets are observed.\n",
    }
    for n,s in docs.items():
        p=EXP/n; put(p,s); hashes[p.relative_to(ROOT).as_posix()]=h(p)
    script=EXP/"register_ev0334.py"; hashes[script.relative_to(ROOT).as_posix()]=h(script)
    manifest=TX/"EV-0334-capture-manifest.json"
    put(manifest,json.dumps({"evidence_id":"EV-0334","captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "analysis_binary":{"distribution":"GOG","product_version":"1.6.1179.0","sha256":BINARY},
      "project_mode":{"existing_project":True,"read_only":True,"auto_analysis_disabled":True,"import_attempted":False,"overwrite_attempted":False},
      "captures":rows,"diagnostic_probe":diagnostic,"private_hashes":hashes,
      "limitations":["The actual selected cell parent vtable is data-dependent and not observed.","The +0x730 child concrete class and final slot+0x8 target remain unresolved.","The NiNode table mapping is conditional for this cell transition; no runtime class observation exists.","No Steam runtime, full active order, positive damage, effective protection, raw AVSK delta, or vanilla reproduction is established."]},indent=2,ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()]=h(manifest)
    ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
      "id":"EV-0334","kind":"native","source":"Identity-checked GOG Skyrim AE 1.6.1179.0 PlayerCharacter cell-transition, NiNode vtable, constructor, add-child, remove-child, and cell scene helper traces.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0334-note.md","sha256":h(note),
      "runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; no runtime parent/child class selected.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
      "coverage":"Eight complete identity-checked captures map PlayerCharacter+0x730 cell-transition context, the +0x130 cell helper, NiNode slots +0x1A8/+0x1C0, parent field assignment, child-array removal, and the NiNode constructor.",
      "result":"FUN_1407373e0 adds PlayerCharacter+0x730 to a selected cell scene child through slot+0x1A8 and removes it via the pointer at child+0x30 through slot+0x1C0. The captured NiNode implementation stores parent at child+0x30, adds/removes NiAVObject child references, and clears that parent on removal. The actual runtime parent table and child final slot+0x8 target remain unresolved; Q64-H1/H2 are unchanged.",
      "related_evidence":["EV-0327","EV-0331","EV-0333","EV-0217","EV-0223","EV-0280","EV-0281","EV-0326"],"local_hashes":hashes})
    put(ep,json.dumps(ev,indent=2,ensure_ascii=False))
    cp=ROOT/"research/CLAIMS.md"; claims=cp.read_text(encoding="utf-8")
    if "| CL-L166 |" in claims: raise SystemExit("CL-L166 already exists")
    put(cp,claims.rstrip()+"\n| CL-L166 | In GOG AE 1.6.1179.0, PlayerCharacter cell-transition FUN_1407373e0 treats +0x730 as a refcounted scene child: the cell-add route passes it to a candidate NiNode +0x1A8 child adder, whose helper stores the parent at child+0x30; the removal route uses that parent pointer and slot+0x1C0 to detach it. | supported (bounded structural path inference) | [EV-0334], [EV-0327] | The actual cell parent table, child concrete class, and final slot+0x8 destructor are not observed. This narrows one Q64 callback but leaves Q64-H1/H2 unresolved and establishes no global no-skill result. |")
    mp=ROOT/"research/MECHANISMS.md"; mech=mp.read_text(encoding="utf-8")
    if "## M-0063 —" in mech: raise SystemExit("M-0063 already exists")
    put(mp,mech.rstrip()+"\n\n## M-0063 — PlayerCharacter +0x730 cell-scene child lifecycle (Q-0064)\n\nFUN_1407373e0 adds the +0x730 object through a cell-scene child node's slot+0x1A8 and removes it through the parent pointer at child+0x30 via slot+0x1C0. The GOG NiNode candidate add method stores child+0x30 as parent; its remove wrapper delegates to slot+0x1B8 and the child-array remover clears the parent and releases references [EV-0334]. The actual runtime parent table and child finalizer remain unresolved. Claim CL-L166 -> M-0063.\n")
    gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
    put(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0334 connects PlayerCharacter +0x730 cell transitions to a candidate NiAVObject/NiNode parent-child lifecycle: add stores the parent at child+0x30; removal detaches the child from the parent and releases refs. The exact parent vtable and child finalizer remain data-dependent, so this branch does not exclude a destructor descendant reaching skill progress. EV-0331's +0x8F8 NiNode remains conditional, and EV-0333's +0x9A0/+0x9A8 model resource has no mapped vtable; common class/finalizer identity is a new testable hypothesis, not an established edge. No causal edge to Actor::UseSkill AV11/AV12 or OBJ-1 is added [EV-0334], [EV-0331], [EV-0333]. Claim CL-L166 -> M-0063.\n")
    xp=ROOT/"research/CONTRADICTIONS.md"; con=xp.read_text(encoding="utf-8")
    con=con.replace("- **Evidence:** [EV-0333], [EV-0332]", "- **Evidence:** [EV-0334], [EV-0333], [EV-0332]", 1)
    marker="EV-0333 traces the +0x9A0/+0x9A8 producer through a data-selected model-resource adapter, but its loaded root and finalizer remain unresolved."
    if marker not in con: raise SystemExit("trap contradiction marker missing")
    con=con.replace(marker,marker+" EV-0334 maps +0x730 as a scene-child attach/detach candidate through NiNode methods; actual parent table and child finalizer remain unresolved.",1)
    put(xp,con)
    ix=ROOT/"experiments/README.md"
    put(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0072 / EV-0334 maps PlayerCharacter +0x730 cell-scene attach/detach through NiNode candidate methods and an NiAVObject-compatible child/parent field at +0x30. The concrete child finalizer remains unresolved; Q-0064 stays open.\n")
    fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8"))
    q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
    for eid in ["EV-0334"]:
        if eid not in q.setdefault("evidence",[]): q["evidence"].append(eid)
    if "CL-L166" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L166")
    for hyp in q.get("hypotheses",[]):
        if "EV-0334" not in hyp.setdefault("evidence",[]): hyp["evidence"].append("EV-0334")
    q["next_action"]=("Resolve the actual parent/child class and final slot+0x8 target for the +0x730 cell-scene child, using an exact writer/constructor or observed data-selected vtable. "
      "If the class remains data-dependent, preserve this branch as unresolved and reselect the highest-information ready OBJ-1/OBJ-2 line.")
    q.setdefault("attempts",[]).append({"action_key":"q64-cell-scene-parent-child-lifecycle",
      "outcome":"EV-0334 maps PlayerCharacter+0x730 cell addition/removal to a NiNode candidate child-attach/detach pattern. The candidate add helper stores parent at child+0x30; the candidate removal wrapper removes the child and clears that field. This narrows the +0x1C0 callback to scene graph housekeeping under a NiNode parent, but the actual parent table, child class, and final slot+0x8 target remain unresolved. Q64-H1/H2 remain proposed.",
      "evidence":["EV-0334","EV-0327","EV-0331","EV-0333"],
      "new_discriminant":"Recover the exact field writer/parent vtable and child finalizer; screen the final slot+0x8 path for the mapped AV11/AV12 sink. The current NiNode mapping is conditional, not a runtime class result.",
      "recorded_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")})
    if not any(x.get("id")=="Q-0065" for x in fr["items"]):
        fr["items"].append({
          "id":"Q-0065","objective":"OBJ-2","kind":"mechanism","status":"ready",
          "question":"Do PlayerCharacter +0x730 cell-scene child, +0x8F8 first-person skeleton, and +0x9A0/+0x9A8 model-resource outputs converge on a shared NiAVObject/NiNode finalizer family, or are they distinct resource classes?",
          "hypotheses":[
            {"id":"Q65-H1","model":"The mapped cleanup fields return a shared NiAVObject/NiNode family whose common refcount/finalizer chain can be screened once.","predicted_discriminant":"Identity-checked producer paths recover matching concrete vtables and slot+0x8 targets across the fields, with source/resource evidence tying each runtime object to the same class family.","status":"proposed","evidence":["EV-0334","EV-0331","EV-0333"]},
            {"id":"Q65-H2","model":"The fields hold distinct data-selected scene/resource classes that only share the generic refcount slot ABI.","predicted_discriminant":"Exact producer or runtime vtable evidence shows differing concrete tables/finalizers; each descendant must remain separately screened.","status":"proposed","evidence":["EV-0334","EV-0331","EV-0333"]}
          ],
          "methods":[
            "Compare only build-attested GOG producer paths and parser/constructor vtables; do not infer a shared class from refcount slot +0x8 alone.",
            "Use EV-0334's cell-scene parent-child mapping, EV-0331's conditional NiNode path, and EV-0333's model-resource adapter as separate starting points.",
            "Identify exact loaded NIF roots or same-build read-only runtime vtables if static code remains data-selected; keep GOG and Steam addresses separate.",
            "Screen any common finalizer descendants for Actor::UseSkill AV11/AV12 and preserve unknown child destructors as unresolved."
          ],
          "blocked_by":[],"evidence":["EV-0334","EV-0331","EV-0333","EV-0328","EV-0329"],
          "priority":0.93,"information_gain":0.87,
          "next_action":"Compare parser and constructor ownership for the +0x8F8 skeleton resource and +0x9A0/+0x9A8 model adapter against the +0x730 NiNode child contract; seek a concrete shared vtable/finalizer or falsify class identity.",
          "linked_claims":["CL-L163","CL-L165","CL-L166"],"successors":[],"attempts":[]
        })
        q.setdefault("successors",[])
        if "Q-0065" not in q["successors"]: q["successors"].append("Q-0065")
    put(fp,json.dumps(fr,indent=2,ensure_ascii=False))
    rp=ROOT/"ROADMAP.md"
    put(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0334 maps the +0x730 cell transition to a NiNode candidate child attach/detach operation, with child+0x30 as the parent link; the concrete runtime vtable and child finalizer remain unresolved. Together with the conditional +0x8F8 NiNode candidate [EV-0331] and +0x9A0/+0x9A8 model adapter [EV-0333], this creates a falsifiable cross-field class-family question Q-0065. Refcount slot similarity alone does not establish a shared type. Continue Q-0064's exact finalizer discriminator, then reselect among the P0 frontier.\n")
    with (ROOT/"research/SESSION_LOG.md").open("a",encoding="utf-8") as f:
        f.write("\n- "+datetime.now(timezone.utc).isoformat(timespec="seconds")+" TX-20261017-0011 checkpoint: EV-0334 / CL-L166 / M-0063 registered. FUN_1407373e0 adds/removes PlayerCharacter+0x730 through a NiNode candidate; the add helper sets child+0x30 parent and removal clears it. This narrows one Q64 callsite but leaves actual table, child class, and finalizer unresolved. Cross-field class-family test Q-0065 added from EV-0331/0333/0334; Q64-H1/H2 unchanged. Next: resolve exact +0x730 writer/parent vtable/finalizer, then reselect the highest-information P0 line.\n")
    print("registered EV-0334 / CL-L166 / M-0063; added ready Q-0065; Q-0064 remains open")
if __name__=="__main__": main()
