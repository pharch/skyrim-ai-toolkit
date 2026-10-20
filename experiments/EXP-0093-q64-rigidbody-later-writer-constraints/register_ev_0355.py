#!/usr/bin/env python3
"""Register the ProcessTrapHit-to-rigidbody constraint child writer trace."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0093-q64-rigidbody-later-writer-constraints"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
EXPECTED = {
"20261018T063523Z":["DECOMPILATION_BEGIN=FUN_140ebf0b0","FUN_140e86750"],
"20261018T063623Z":["DECOMPILATION_BEGIN=FUN_140e83e50","FUN_140e95df0"],
"20261018T063731Z":["DECOMPILATION_BEGIN=FUN_140e95df0","FUN_140e98120"],
"20261018T063833Z":["DECOMPILATION_BEGIN=FUN_140e98120","DECOMPILATION_BEGIN=FUN_140e962d0","FUN_14018a900","FUN_1402f39c0"],
"20261018T064026Z":["DECOMPILATION_BEGIN=FUN_140e962d0","CALLER_DECOMPILATION_BEGIN=FUN_1407136e0","CALLER_DECOMPILATION_BEGIN=FUN_1407c9980"],
"20261018T064133Z":["DECOMPILATION_BEGIN=FUN_140ef43b0","bhkFixedConstraint::vftable","bhkMalleableConstraint::vftable"],
"20261018T064300Z":["POINTER_TABLE_BASE_RVA=0x19EB9C0","POINTER_TABLE_ENTRY=index:41","POINTER_TABLE_ENTRY=index:42"],
"20261018T064352Z":["POINTER_TABLE_BASE_RVA=0x19F50A8","POINTER_TABLE_ENTRY=index:41","POINTER_TABLE_ENTRY=index:42"],
"20261018T064447Z":["DECOMPILATION_BEGIN=FUN_140ecdc90","FUN_140e86bf0","0x1b0"],
"20261018T064548Z":["DECOMPILATION_BEGIN=FUN_140ecdbe0","0x150","0x1b0"],
"20261018T064650Z":["DECOMPILATION_BEGIN=FUN_140ecc720","bhkMalleableConstraint::vftable","FUN_140ebea60"],
"20261018T064746Z":["DECOMPILATION_BEGIN=FUN_140ef49f0","bhkFixedConstraint::vftable","FUN_140eff4f0"],
"20261018T064846Z":["POINTER_TABLE_BASE_RVA=0x19EB9C0","POINTER_TABLE_ENTRY=index:43"],
"20261018T064938Z":["POINTER_TABLE_BASE_RVA=0x19F50A8","POINTER_TABLE_ENTRY=index:43"],
"20261018T065035Z":["DECOMPILATION_BEGIN=FUN_140ecd680","FUN_140ebe4a0"],
"20261018T065134Z":["DECOMPILATION_BEGIN=FUN_140ecc300","FUN_140cc7590"],
"20261018T065233Z":["DECOMPILATION_BEGIN=FUN_140ef47c0","FUN_140cc7590"],
"20261018T065347Z":["DECOMPILATION_BEGIN=FUN_140e86bf0","INDIRECT_CALL_SITE_COUNT=2","FUN_140b3a830"],
"20261018T065452Z":["DECOMPILATION_BEGIN=FUN_1407c9980","XREF_CALL_EDGE=1406bab55 -> 1407c9980","FUN_140e962d0(uVar9,1,1,0);"],
"20261018T065627Z":["DECOMPILATION_BEGIN=FUN_140ecd630","INDIRECT_CALL_SITE_COUNT=1","0x1a0"],
"20261018T065723Z":["DECOMPILATION_BEGIN=FUN_140ecd670","0x138"],
"20261018T065823Z":["POINTER_TABLE_BASE_RVA=0x19EB9C0","POINTER_TABLE_ENTRY=index:52"],
"20261018T065918Z":["POINTER_TABLE_BASE_RVA=0x19F50A8","POINTER_TABLE_ENTRY=index:52"],
"20261018T070013Z":["DECOMPILATION_BEGIN=FUN_140ecd870","param_1 + 0x10"],
}

def digest(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def put(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n", encoding="utf-8")

def load_capture(stamp: str):
    mp = GH / f"gog-query-{stamp}.meta.json"
    m = json.loads(mp.read_text(encoding="utf-8"))
    raw = ROOT / m["artifacts"]["stdout"]
    c = m.get("checks", {})
    ok = (m.get("analysis_distribution") == "GOG"
          and m.get("analysis_binary_product_version") == "1.6.1179"
          and m.get("analysis_binary_sha256") == BINARY
          and m.get("program_executable_path_matches_gog_binary") is True
          and m.get("ok") is True and m.get("exit_code") == 0
          and m.get("read_only") is True and m.get("auto_analysis_disabled") is True
          and m.get("import_attempted") is False and m.get("overwrite_attempted") is False
          and c.get("program_identity_matches_gog_binary") is True
          and c.get("script_no_error") is True and digest(raw) == m.get("stdout_sha256"))
    if not ok:
        raise SystemExit(f"identity/completion check failed: {stamp}")
    txt = raw.read_text(errors="replace")
    if any(s not in txt for s in EXPECTED[stamp]):
        raise SystemExit(f"marker check failed: {stamp}")
    return m, mp, raw

def main():
    captures = {s: load_capture(s) for s in EXPECTED}
    note = TX / "EV-0355-note.md"
    put(note, f"""# EV-0355 — ProcessTrapHit reaches a physics constraint child writer

## Build and method

Queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher with auto-analysis disabled and read-only project access. The 24 capture stamps and hashes are preserved in the capture manifest. These GOG addresses are not transferred to Steam AE 1.6.1170.0.

## Competing models and discriminant

- Q64-H1 predicts the mapped teardown descendants do not call Actor::UseSkill with AV11/AV12. Its discriminant is concrete receiver/vtable resolution away from the skill-progress sink.
- Q64-H2 predicts a resolved callback or descendant reaches that sink with an armor ActorValue. A generic unresolved virtual call is inconclusive.
- The tested discriminant was the later body+0x28/+0x38 child writer and each concrete child callback reachable through the two constraint classes it produces.

## Direct observations

- FUN_140e98120 has one nonrecursive direct caller, FUN_140e962d0. That wrapper selects FUN_140e98120 when its second argument is nonzero; otherwise it selects FUN_140e98200 [captures 20261018T063833Z; 20261018T064026Z].
- FUN_1406b9df0 directly calls FUN_1407c9980 at GOG address 0x1406BAB55. FUN_1407c9980 invokes FUN_140e962d0(uVar9,1,1,0), placing the flag-1 recursive traversal on this captured ProcessTrapHit route [capture 20261018T065452Z].
- FUN_140e98120 walks child pointers from +0x118 under the count at +0x122. Its two link-chain type checks use FUN_14018a900 and FUN_1402f39c0; a recognized rigid-body object is passed to FUN_140e95df0 [captures 20261018T063833Z; 20261018T063731Z].
- FUN_140e95df0 traverses body+0x28 under the count at +0x38. For qualifying existing children it calls FUN_140ef43b0, appends successful results to the body vector, then calls the old child's slot +0x150 and the new child's slot +0x148 [captures 20261018T063731Z; 20261018T064133Z].
- The factory installs bhkFixedConstraint or bhkMalleableConstraint according to its float parameter and the observed DAT_141ad3990 threshold. Their exact vtable bases are GOG RVAs 0x19EB9C0 and 0x19F50A8 [capture 20261018T064133Z].
- Both vtables map +0x148/index 41 to FUN_140ecdbe0, +0x150/index 42 to FUN_140ecdc90, +0x128/index 37 to FUN_140ecd680, +0x138/index 39 to FUN_140ecd630, +0x140/index 40 to FUN_140ecd670, and +0x1A0/index 52 to FUN_140ecd870. Their +0x158/index 43 destructors differ: fixed uses FUN_140ecc300; malleable uses FUN_140ef47c0 [captures 20261018T064300Z; 20261018T064352Z; 20261018T064846Z; 20261018T064938Z; 20261018T065823Z; 20261018T065918Z].
- The +0x150 callback obtains associated physics state and calls FUN_140e86bf0 when present, then invokes physics-state slot +0x1B0. The +0x148 callback detaches/rebinds constraint state. Destructors release the wrapped physics object through the physics allocator [captures 20261018T064447Z; 20261018T064548Z; 20261018T064650Z; 20261018T064746Z; 20261018T065134Z; 20261018T065233Z].
- FUN_140e86bf0's two indirect sites resolve through these tables to FUN_140ecd630/FUN_140ecd670; those resolve to FUN_140ecd870, which reads a nested state field. Its direct helper FUN_140b3a830 remains a bounded branch not traced to completion [captures 20261018T065347Z; 20261018T065627Z; 20261018T065723Z; 20261018T070013Z].
- No Actor::UseSkill call or AV11/AV12 skill-credit argument appears in the mapped branch. This is not a census of every callback below FUN_140b3a830 or every unresolved indirect site in the larger ProcessTrapHit function.

## Result and causal model

This resolves one later child-array producer and a concrete ProcessTrapHit-to-scene-traversal path. The producer creates and links physics constraints; their resolved update, attach, and destruction methods manipulate associated physics state and resource references. Q64-H1 is strengthened for this mapped branch and Q64-H2 is narrowed here, while both hypotheses remain proposed for the larger route because other teardown sites and a direct helper branch remain unresolved.

The exact scene/body instance visited by the traversal is not proven to be the PlayerCamera+0x128 instance; EV-0354 establishes that PlayerCamera-owned producer separately. No causal edge to AV11/AV12 skill progress, effective armor protection, or OBJ-1 is added. The exact Steam level-one save, full plugin order, positive-damage hit, effective-protection sample, and raw AVSK before/after measurements remain required for vanilla behavior claims.

## Exact next action

Trace the remaining direct branch FUN_140b3a830 and the outstanding indirect sites in the captured ProcessTrapHit route against Actor::UseSkill slot +0xF7 and the mapped skill-progress sink. Keep the PlayerCamera-instance association unresolved unless receiver evidence establishes it. Then reselect the next ready P0 frontier item and preserve the exact Steam runtime discriminator separately.
""")
    rows = {}
    for s,(m,mp,raw) in captures.items():
        rows[s] = {"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
                   "requested_pointer_table_rva":m.get("requested_pointer_table_rva"),
                   "checks":m.get("checks"),"stdout_sha256":m.get("stdout_sha256"),
                   "stderr_sha256":m.get("stderr_sha256"),"query_script_sha256":m.get("query_script_sha256")}
    manifest = TX / "EV-0355-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id":"EV-0355","analysis_binary_product_version":"1.6.1179.0",
        "analysis_binary_sha256":BINARY,"captures":rows}, indent=2))
    docs = {
      "README.md":"# EXP-0093 — Later rigid-body child population\n\nResolve the ProcessTrapHit scene traversal's later rigid-body child writer and class-specific cleanup callbacks.\n",
      "hypothesis.md":"# Competing models\n\n- Q64-H1: the mapped trap-hit cleanup branch resolves away from AV11/AV12 skill progress.\n- Q64-H2: a concrete callback reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.\n\nA generic unresolved callback does not decide either model.\n",
      "protocol.md":"# Protocol\n\nUse build-attested read-only GOG queries. Require producer-backed vector population, exact vtables, and callback targets. Keep unresolved callsites and the Steam runtime test separate.\n",
      "results.md":"# Results\n\nFUN_1406b9df0 calls FUN_1407c9980, whose flag-1 traversal reaches FUN_140e95df0. That writer can append bhkFixedConstraint or bhkMalleableConstraint children to a recognized rigid body. The mapped attach, cleanup, and destruction callbacks manipulate physics state and references; no AV11/AV12 sink appears in this bounded chain [EV-0355].\n",
      "predicted-outcomes.md":"# Predicted outcomes\n\n- A resolved Actor::UseSkill call with AV11/AV12 from a remaining callback supports Q64-H2.\n- A callback resolved to physics/state/resource operations without an AV sink strengthens Q64-H1 for that branch only.\n- An unresolved dispatch or missing runtime sample remains inconclusive.\n",
      "implications.md":"# Implications\n\nThe later body child list can contain physics constraints during a trap-hit scene traversal. The source trace does not establish armor XP behavior, effective protection, or that the exact PlayerCamera-owned body is visited.\n",
      "expected-discriminants.md":"# Expected discriminants\n\n1. Trace FUN_140b3a830 and its callback table.\n2. Resolve the remaining ProcessTrapHit indirect sites.\n3. Screen each target and argument for Actor::UseSkill slot +0xF7 with AV11/AV12.\n4. Keep the exact Steam positive-damage/effective-protection/raw-AVSK test open.\n"}
    for n,t in docs.items(): put(EXP/n,t)

    hashes = {}
    for s,(m,mp,raw) in captures.items():
        for p in [mp,raw] + [ROOT/x for x in m["artifacts"].values()]:
            if p.is_file(): hashes[p.relative_to(ROOT).as_posix()] = digest(p)
    for p in [note,manifest,*EXP.iterdir(),Path(__file__)]:
        if p.is_file(): hashes[p.relative_to(ROOT).as_posix()] = digest(p)
    put(manifest,json.dumps({"evidence_id":"EV-0355","analysis_binary_product_version":"1.6.1179.0",
        "analysis_binary_sha256":BINARY,"captures":rows,"registered_local_hashes":hashes},indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    ep=ROOT/"research/EVIDENCE.json"; e=json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id")=="EV-0355" for x in e["items"]): raise SystemExit("EV-0355 already registered")
    e["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "edition":"AE","modified_state":False,"id":"EV-0355","kind":"native",
      "source":"Read-only GOG Ghidra queries of the ProcessTrapHit caller, scene traversal, body child writer, and exact physics constraint vtables and callbacks.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0355-note.md",
      "sha256":digest(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
      "coverage":"Direct ProcessTrapHit-to-FUN_1407c9980-to-flagged scene traversal; later rigid-body child-vector producer; constraint factory, two vtables, attach/cleanup/destruction methods, nested state getters, and helper branch boundary.",
      "result":"FUN_1406b9df0 reaches recursive scene traversal that can append bhkFixedConstraint or bhkMalleableConstraint children to recognized rigid bodies. Mapped callbacks operate on physics state and wrapped resources; no AV11/AV12 sink appears in this bounded branch. The PlayerCamera instance identity, FUN_140b3a830 descendants, other indirect sites, and exact Steam XP behavior remain unresolved.",
      "related_evidence":["EV-0325","EV-0353","EV-0354"],"local_hashes":hashes})
    put(ep,json.dumps(e,indent=2,ensure_ascii=False))

    cp=ROOT/"research/CLAIMS.md"; c=cp.read_text(encoding="utf-8")
    if "| CL-L193 |" in c: raise SystemExit("CL-L193 already exists")
    put(cp,c.rstrip()+"\n| CL-L193 | The captured ProcessTrapHit route reaches a recursive scene traversal that can append bhkFixedConstraint or bhkMalleableConstraint children to recognized rigid bodies; mapped callbacks manipulate physics state and resources, with no AV11/AV12 skill sink in this bounded branch. | supported for the mapped static branch | [EV-0355], [EV-0354] | FUN_140b3a830 descendants, other indirect sites, exact PlayerCamera instance identity, and live Steam XP behavior remain unresolved. |")

    mp=ROOT/"research/MECHANISMS.md"
    put(mp,mp.read_text(encoding="utf-8").rstrip()+"\n\n## M-0075 — Trap-hit scene traversal updates rigid-body constraints (Q-0064)\n\nFUN_1406b9df0 calls FUN_1407c9980, which requests the flag-1 recursive scene traversal. The traversal routes recognized rigid-body objects through FUN_140e95df0, which can append bhkFixedConstraint or bhkMalleableConstraint objects. Their mapped callbacks attach, detach, update, or release physics state and wrapped resources. This is a bounded physics-path result; unresolved helper descendants and live armor XP remain open [EV-0355]. Claim CL-L193 -> M-0075.\n")
    gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
    put(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0355 adds a source-backed edge from FUN_1406b9df0 through FUN_1407c9980 and FUN_140e962d0 into recursive rigid-body constraint handling. The resolved descendants manipulate physics constraints and resources; no edge to AV11/AV12 skill credit is established. Claim CL-L193 -> M-0075.\n")
    ip=ROOT/"experiments/README.md"
    put(ip,ip.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0093 / EV-0355 traces the ProcessTrapHit scene traversal into rigid-body physics constraint updates; remaining helper and indirect branches stay open.\n")
    rp=ROOT/"research/ROADMAP.md"
    put(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0355 resolves the later body child writer as physics constraint setup on a flagged ProcessTrapHit scene traversal. Next trace FUN_140b3a830 descendants and the remaining indirect sites against the AV11/AV12 skill sink; keep Steam runtime tests separate. Claim CL-L193 -> M-0075.\n")

    fp=ROOT/"research/FRONTIER.json"; f=json.loads(fp.read_text(encoding="utf-8"))
    q64=next(x for x in f["items"] if x.get("id")=="Q-0064")
    q65=next(x for x in f["items"] if x.get("id")=="Q-0065")
    for x in (q64,q65):
        if "EV-0355" not in x.setdefault("evidence",[]): x["evidence"].append("EV-0355")
        if "CL-L193" not in x.setdefault("linked_claims",[]): x["linked_claims"].append("CL-L193")
        for h in x.get("hypotheses",[]):
            if "EV-0355" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0355")
    q64["next_action"]="Trace FUN_140b3a830 descendants and remaining indirect sites on the captured ProcessTrapHit route against Actor::UseSkill slot +0xF7 and the mapped skill-progress sink. Keep the PlayerCamera-instance association unresolved unless receiver evidence establishes it."
    q65["next_action"]="Compare producer-backed vtables for PlayerCharacter +0x730, +0x8F8, +0x9D0, +0x9A0/+0x9A8, ThirdPersonState+0xA0, and the mapped physics constraint classes; retain receiver provenance and keep the Steam runtime discriminator open."
    q64.setdefault("attempts",[]).append({"action_key":"q64-process-trap-hit-rigidbody-constraint-writer",
      "outcome":"EV-0355 resolves a direct ProcessTrapHit-to-flagged scene traversal and a later rigid-body child writer that appends fixed/malleable physics constraints; mapped callback descendants manipulate physics state and resources, with no AV11/AV12 sink in this bounded branch.",
      "evidence":["EV-0355"],"new_discriminant":"Trace FUN_140b3a830 descendants and remaining ProcessTrapHit indirect sites against Actor::UseSkill slot +0xF7; runtime XP remains unmeasured.","next_action":q64["next_action"]})
    q65.setdefault("attempts",[]).append({"action_key":"q65-constraint-vtable-comparison",
      "outcome":"EV-0355 maps two physics constraint vtables and their shared attach/cleanup/state getter slots; it does not establish identity for the other PlayerCamera-owned resources.",
      "evidence":["EV-0355"],"new_discriminant":"A producer-backed receiver for each PlayerCamera field and exact vtable entry is required before comparing its finalizer.","next_action":q65["next_action"]})
    put(fp,json.dumps(f,indent=2,ensure_ascii=False))

    ck=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    src=ck.read_text(encoding="utf-8")
    needle="- Q-0064 / EV-0354 proves the rigid body's +0x28 pointer and +0x38 count start zero, so its first slot+0x150 loop skips; later vector population is still unknown. The next query is FUN_140ebf0b0 and post-constructor writers.\n"
    add="- Q-0064 / EV-0355 ties FUN_1406b9df0 to a flagged scene traversal that can append fixed/malleable physics constraints to rigid-body child vectors; mapped callbacks manipulate physics state, but FUN_140b3a830 descendants and remaining indirect sites stay open.\n"
    if needle not in src: raise SystemExit("checkpoint EV-0354 line missing")
    put(ck,src.replace(needle,needle+add))
    print("registered EV-0355 / CL-L193 / M-0075; Q-0064 continues on remaining call-tree branches")

if __name__ == "__main__":
    main()
