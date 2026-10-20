#!/usr/bin/env python3
"""Register bounded GOG model-resource adapter evidence for Q-0064."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0071-model-resource-callback-adapter"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
 "20261018T030840Z": ["TARGET_RVA=0xD19980", "INDIRECT_CALL_SITE=140d19998 CALL qword ptr [RAX + 0xb8]", "INDIRECT_CALL_SITE=140d199aa CALL qword ptr [R8 + 0xe8]"],
 "20261018T031038Z": ["TARGET_RVA=0xE1B8C0", "DECOMPILATION_BEGIN=FUN_140e1b8c0"],
 "20261018T031433Z": ["TARGET_RVA=0x216B40", "DECOMPILATION_BEGIN=FUN_140216b40", "INDIRECT_CALL_SITE_COUNT=11", "1402158ac -> 140216b40 caller=FUN_140215660"],
}
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p, s): p.parent.mkdir(parents=True, exist_ok=True); p.write_text(s.rstrip()+"\n", encoding="utf-8")
def main():
    ep = ROOT / "research/EVIDENCE.json"
    ev = json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id") == "EV-0333" for x in ev["items"]): raise SystemExit("EV-0333 already registered")
    hashes, rows = {}, []
    for stamp, markers in CAPTURES.items():
        mp = GH / f"gog-query-{stamp}.meta.json"
        m = json.loads(mp.read_text(encoding="utf-8"))
        c = m.get("checks", {})
        if (m.get("analysis_distribution") != "GOG" or m.get("analysis_binary_product_version") != "1.6.1179"
            or m.get("analysis_binary_sha256") != BINARY or m.get("exit_code") != 0 or m.get("ok") is not True
            or m.get("read_only") is not True or m.get("auto_analysis_disabled") is not True
            or m.get("import_attempted") is not False or m.get("overwrite_attempted") is not False
            or c.get("program_identity_matches_gog_binary") is not True or c.get("script_no_error") is not True):
            raise SystemExit("identity/read-only/completion check failed: "+stamp)
        out = ROOT / m["artifacts"]["stdout"]
        raw = out.read_text(encoding="utf-8", errors="replace")
        if digest(out) != m.get("stdout_sha256") or any(x not in raw for x in markers): raise SystemExit("capture/hash/marker failure: "+stamp)
        files = [mp] + [ROOT / x for x in m["artifacts"].values()]
        if any(not x.is_file() for x in files): raise SystemExit("missing capture artifact: "+stamp)
        hashes.update({x.relative_to(ROOT).as_posix(): digest(x) for x in files})
        rows.append({"stamp":stamp,"query_mode":m.get("query_mode"),"requested_rva":m.get("requested_rva"),
                     "checks":c,"stdout_sha256":m.get("stdout_sha256"),"stderr_sha256":m.get("stderr_sha256"),
                     "adapter_sha256":m.get("adapter_sha256"),"query_script_sha256":m.get("query_script_sha256")})
    note = TX / "EV-0333-note.md"
    put(note, f"""# EV-0333 — Model-resource callback in PlayerCharacter +0x9A0 producer

## Build and method

Three strict-dispatcher Ghidra queries used the existing GOG Skyrim AE 1.6.1179.0 project; analysis binary SHA-256 {BINARY}. Metadata confirms matching identity, read-only execution, auto-analysis disabled, successful completion, and no import or overwrite. Captures and metadata are hashed in the private manifest. These GOG addresses do not map to the installed Steam AE 1.6.1170.0 build.

## Direct observations

- FUN_140d19980 has no direct calls and two indirect calls. It invokes input-object slot +0xB8 with no explicit arguments, then slot +0xE8 with the input object and second parameter, and returns the first result [capture 20261018T030840Z].
- FUN_140216b40 obtains a resource name through input-object slot +0x20, calls generic loader FUN_140e05620, reads a refcounted object from the resource handle at +0x28, and conditionally passes it to FUN_140d19980 when FUN_140e1ad20 returns false. The returned pointer then enters model/configuration and named-child lookup helpers; retained objects are released through slot +0x8 [capture 20261018T031433Z].
- The caller census shows FUN_140215660 passes FUN_140216b40's return to FUN_1407445d0. EV-0329 maps that setter to candidate PlayerCharacter fields +0x9A0/+0x9A8. Receiver attribution remains a lifecycle-path inference, not a runtime observation [EV-0329].
- FUN_140e1ad20 wraps recursive FUN_140e1b8c0, which calls input slot +0x18 and walks nested elements using offsets +0x122 and +0x118. The Boolean-style hierarchy result does not identify the selected resource's concrete class [capture 20261018T031038Z].
- FUN_140216b40 has 21 direct calls and 11 indirect sites. Its bounded body establishes resource loading and adaptation, not the exact runtime asset or root vtable. Unresolved callbacks and finalizers prevent a transitive negative about skill progression.

## Assessment and limits

This advances the EV-0329 producer from generic resource loading to a data-selected model hierarchy and two-slot adapter. Slots +0xB8/+0xE8, exact loaded root class, and returned object's final slot+0x8 target remain unresolved. The local archive workflow supports only a narrow classic PEX extraction and has no general BSA or NIF route. Q64-H1/H2 remain proposed. No result about zero armor XP, effective protection, positive incoming damage, exact-profile behavior, Steam behavior, or vanilla reproduction follows. No OBJ-1 causal edge is supported.

## Cross-domain synthesis

Armor-hit and enchanting routes share the Actor::UseSkill sink but have distinct producers [EV-0217]–[EV-0223], [EV-0280], [EV-0281]. Current Q-0064 captures show no shared call or data edge from this model-resource producer to that sink. Since the resource class and callback targets remain dynamic, this is a no-edge rationale for the current graph, not a global reachability negative. The mapped Dawnguard Fort route is a distinct record/Papyrus transition path with no observed ActorValue dependency [EV-0326]. Exact target or runtime call/data evidence could change this assessment.

## Next discriminant

Resolve the remaining PlayerCharacter +0x730/+0x30 slot+0x1C0 callback reached by FUN_1407373e0 during cell removal. Find an exact writer or typed constructor for the nested object, recover its concrete vtable, and screen descendants for AV11/AV12 skill progress.
""")
    hashes[note.relative_to(ROOT).as_posix()] = digest(note)
    docs = {
      "README.md":"# EXP-0071 — Model-resource callback adapter\n\nQ-0064 trace of FUN_140d19980 and its FUN_140216b40 caller. EV-0333 identifies a data-selected model hierarchy and virtual +0xB8/+0xE8 adapter; root class, finalizer, and AV11/AV12 descendants remain unresolved.\n",
      "hypothesis.md":"# Competing models\n\nQ64-H1 predicts no relevant cleanup descendant awards AV11/AV12 skill progress. Q64-H2 predicts a resolved teardown descendant reaches the skill sink with AV11/AV12. The producer model has harmless resource finalization versus a callback path to that sink. EV-0333 maps the adapter but resolves neither model; all remain open.\n",
      "protocol.md":"# Protocol\n\nUse only the existing GOG 1.6.1179.0 project through the strict dispatcher with analysis disabled and read-only mode. Preserve capture hashes. Do not transfer GOG RVAs to Steam, infer the loaded asset from a generic path, or treat unresolved virtual targets as negative evidence.\n",
      "predicted-outcomes.md":"# Predicted outcomes\n\nA resolved root/vtable and final slot+0x8 chain with no AV11/AV12 sink supports the harmless producer model only within that branch. A concrete descendant reaching Actor::UseSkill with AV11/AV12 supports Q64-H2. Resolving all relevant cleanup descendants away from the sink supports Q64-H1. Any dynamic class or target leaves the result inconclusive.\n",
      "expected-discriminants.md":"# Expected discriminants\n\n- **H1:** identify the selected root class and final slot+0x8 chain and show no AV11/AV12 sink on the exact cleanup path; this supports only that bounded branch.\n- **H2:** identify a concrete descendant reaching Actor::UseSkill with AV11/AV12; this supports Q64-H2.\n- Any unresolved selected asset, class, or target remains inconclusive for Q64-H1/H2. [EV-0333]\n",
      "results.md":"# Results\n\nEV-0333 traces FUN_140216b40 from a generic resource handle to FUN_140d19980, whose two unresolved adapter slots are +0xB8 and +0xE8. Its caller passes the returned pointer into the EV-0329 candidate +0x9A0/+0x9A8 setter path. The recursive hierarchy test does not expose the selected root class. The final slot+0x8 target and AV11/AV12 descendants remain unknown. Q64-H1/H2 remain proposed [EV-0333], [EV-0329], [EV-0325].\n",
      "implications.md":"# Implications\n\nNo causal edge to the shared armor/enchanting Actor::UseSkill sink is added because the model-resource class and finalizer remain dynamic; this is not a global negative. Continue Q-0064 on PlayerCharacter +0x730/+0x30 slot +0x1C0 during cell removal, then reselect the highest-information ready P0 line.\n",
    }
    for name, body in docs.items():
        p=EXP/name; put(p,body); hashes[p.relative_to(ROOT).as_posix()]=digest(p)
    script=EXP/"register_ev0333.py"; hashes[script.relative_to(ROOT).as_posix()]=digest(script)
    manifest=TX/"EV-0333-capture-manifest.json"
    put(manifest,json.dumps({"evidence_id":"EV-0333","captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),
      "analysis_binary":{"distribution":"GOG","product_version":"1.6.1179.0","sha256":BINARY},
      "project_mode":{"existing_project":True,"read_only":True,"auto_analysis_disabled":True,"import_attempted":False,"overwrite_attempted":False},
      "captures":rows,"private_hashes":hashes,"limitations":["Adapter slots +0xB8/+0xE8 remain dynamic.","Loaded resource/root class is data-dependent.","Final slot+0x8 target and descendants remain unresolved.","No general BSA/NIF extraction route is available.","No Steam runtime, complete active order, raw AVSK delta, effective protection, or vanilla reproduction is established."]},indent=2,ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()]=digest(manifest)
    ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
      "id":"EV-0333","kind":"native","source":"Identity-checked GOG Skyrim AE 1.6.1179.0 traces of the PlayerCharacter +0x9A0/+0x9A8 model-resource producer and adapter.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0333-note.md","sha256":digest(note),
      "runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; no runtime asset or class selected.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
      "coverage":"Three identity-checked captures inspect FUN_140d19980, recursive hierarchy check, and FUN_140216b40 with direct callers and call-edge census.",
      "result":"FUN_140216b40 conditionally adapts a generic loaded resource through FUN_140d19980 slots +0xB8/+0xE8; its return enters the EV-0329 candidate +0x9A0/+0x9A8 setter path. The loaded root class and final slot+0x8 target remain data-dependent, so Q64-H1/H2 are unchanged.",
      "related_evidence":["EV-0329","EV-0328","EV-0325","EV-0331","EV-0217","EV-0223","EV-0280","EV-0281","EV-0326"],"local_hashes":hashes})
    put(ep,json.dumps(ev,indent=2,ensure_ascii=False))
    cp=ROOT/"research/CLAIMS.md"; claims=cp.read_text(encoding="utf-8")
    if "| CL-L165 |" in claims: raise SystemExit("CL-L165 already exists")
    put(cp,claims.rstrip()+"\n| CL-L165 | In GOG AE 1.6.1179.0, FUN_140216b40 routes a generic model resource through FUN_140d19980 slots +0xB8/+0xE8, and its caller passes the returned pointer into the EV-0329 candidate +0x9A0/+0x9A8 setter path. | supported (bounded build-attested producer trace) | [EV-0333], [EV-0329] | The loaded asset/root class, adapter targets, finalizer, and AV11/AV12 descendants remain unresolved; Q64-H1/H2 are unchanged. |")
    mp=ROOT/"research/MECHANISMS.md"; mech=mp.read_text(encoding="utf-8")
    if "## M-0062 —" in mech: raise SystemExit("M-0062 already exists")
    put(mp,mech.rstrip()+"\n\n## M-0062 — Data-selected model-resource adapter for +0x9A0/+0x9A8 (Q-0064)\n\nFUN_140216b40 loads a generic resource, conditionally calls FUN_140d19980, and passes its output into the EV-0329 candidate PlayerCharacter setter path. FUN_140d19980 invokes unresolved slots +0xB8 and +0xE8; the recursive hierarchy check does not recover a concrete loaded root. The final slot+0x8 target and descendants remain dynamic [EV-0333]. No edge to Actor::UseSkill AV11/AV12 is added or excluded. Claim CL-L165 -> M-0062.\n")
    gp=ROOT/"research/KNOWLEDGE_GRAPH.md"
    put(gp,gp.read_text(encoding="utf-8").rstrip()+"\n\nEV-0333 advances the candidate +0x9A0/+0x9A8 producer through a data-selected model resource and FUN_140d19980's unresolved +0xB8/+0xE8 adapter. The loaded root class and final slot+0x8 callback remain unknown. Armor-hit and enchanting producers share the Actor::UseSkill sink through separately mapped routes [EV-0217]–[EV-0223], [EV-0280], [EV-0281]; no shared call/data edge from this cleanup producer is established, so no causal edge is added and transitive reachability remains unresolved. The mapped Dawnguard Fort route has no observed ActorValue dependency [EV-0326]. Claim CL-L165 -> M-0062 [EV-0333].\n")
    xp=ROOT/"research/CONTRADICTIONS.md"; con=xp.read_text(encoding="utf-8")
    con=con.replace("- **Evidence:** [EV-0332], [EV-0331]", "- **Evidence:** [EV-0333], [EV-0332], [EV-0331]", 1)
    marker="EV-0332 traces a candidate +0x9D0 producer through a TES-owned cell/resource query; both returned-object branches remain dynamically untyped."
    if marker not in con: raise SystemExit("contradiction marker missing")
    con=con.replace(marker,marker+" EV-0333 traces the +0x9A0/+0x9A8 producer through a data-selected model-resource adapter, but its loaded root and finalizer remain unresolved.",1)
    put(xp,con)
    ix=ROOT/"experiments/README.md"
    put(ix,ix.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0071 / EV-0333 traces the +0x9A0/+0x9A8 producer through a data-selected model-resource adapter. Slots +0xB8/+0xE8, loaded root class, and final slot+0x8 target remain unresolved; Q-0064 stays open.\n")
    fp=ROOT/"research/FRONTIER.json"; frontier=json.loads(fp.read_text(encoding="utf-8"))
    q=next(x for x in frontier["items"] if x.get("id")=="Q-0064")
    for eid in ["EV-0333"]:
        if eid not in q.setdefault("evidence",[]): q["evidence"].append(eid)
    if "CL-L165" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L165")
    for h in q.get("hypotheses",[]):
        if "EV-0333" not in h.setdefault("evidence",[]): h["evidence"].append("EV-0333")
    nxt=("Continue the highest-risk remaining field branch: resolve the object rooted at PlayerCharacter+0x730/+0x30 "
         "on FUN_1407373e0's cell-removal slot+0x1C0 call. Search typed constructor/assignment flow and exact vtable owners, "
         "then screen descendants for the mapped AV11/AV12 skill sink. Preserve dynamic targets as unresolved; after this "
         "bounded branch, reselect the highest-information ready OBJ-1/OBJ-2 investigation.")
    q["next_action"]=nxt
    q.setdefault("attempts",[]).append({"action_key":"q64-model-resource-adapter-and-cross-domain-synthesis",
      "outcome":"EV-0333 confirms that FUN_140216b40 obtains a model name, loads a generic resource, conditionally calls FUN_140d19980, and passes its return into the EV-0329 candidate +0x9A0/+0x9A8 setter path. The +0xB8/+0xE8 targets and selected root class remain unresolved. The available archive extractor has no general BSA/NIF route. No shared call/data edge to the known Actor::UseSkill sink is established, but transitive reachability remains open. Q64-H1/H2 remain proposed.",
      "evidence":["EV-0333","EV-0329","EV-0217","EV-0223","EV-0280","EV-0281","EV-0326"],
      "new_discriminant":"Resolve the separate +0x730/+0x30 slot+0x1C0 cell-removal callback and its exact dynamic class/vtable; screen its descendants for AV11/AV12. Missing asset extraction is not a negative result.",
      "recorded_utc":datetime.now(timezone.utc).isoformat(timespec="seconds")})
    put(fp,json.dumps(frontier,indent=2,ensure_ascii=False))
    rp=ROOT/"ROADMAP.md"
    put(rp,rp.read_text(encoding="utf-8").rstrip()+"\n\n## Synthesis checkpoint — 2026-10-18\n\nEV-0330 resolves one PlayerCamera HUD callback away from native skill progress. EV-0331, EV-0332, and EV-0333 map conditional/resource producers but leave data-selected classes unresolved. Armor-hit and enchanting routes share Actor::UseSkill through distinct producers [EV-0217]–[EV-0223], [EV-0280], [EV-0281]. No shared call/data edge links current Q-0064 teardown branches to that sink, while unresolved dynamic targets prevent a global negative. The mapped Dawnguard Fort route has no observed ActorValue dependency [EV-0326]. Continue one bounded +0x730 callback trace, then reselect the highest-information P0 line; retain exact Steam damage/protection/raw-AVSK and level-one transition tests as open runtime discriminants.\n")
    with (ROOT/"research/SESSION_LOG.md").open("a",encoding="utf-8") as f:
        f.write("\n- "+datetime.now(timezone.utc).isoformat(timespec="seconds")+" TX-20261017-0011 checkpoint: EV-0333 / CL-L165 / M-0062 registered. The +0x9A0/+0x9A8 producer passes a data-selected model resource through FUN_140d19980 slots +0xB8/+0xE8; class and finalizer remain unknown, so Q64-H1/H2 are unchanged. Cross-domain review adds no causal edge from this branch to Actor::UseSkill or the mapped Dawnguard Fort route. Next: resolve PlayerCharacter +0x730/+0x30 slot+0x1C0 on cell removal, then reselect a ready P0 line.\n")
    print("registered EV-0333 / CL-L165 / M-0062; Q-0064 remains open")
if __name__ == "__main__": main()
