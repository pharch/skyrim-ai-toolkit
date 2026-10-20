#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
TX=ROOT/".local/alignment/transactions/TX-20261017-0011"
EXP=Path(__file__).resolve().parent
SOURCES=["EV-0301","EV-0217","EV-0222","EV-0261","EV-0260","EV-0319","EV-0324","EV-0325","EV-0331","EV-0347","EV-0365","EV-0366","EV-0367","EV-0368","EV-0370","EV-0371","EV-0372","EV-0373"]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(s.rstrip()+"\n",encoding="utf-8")
def append_once(p,marker,body):
 old=p.read_text(encoding="utf-8")
 if marker in old: raise SystemExit("duplicate append: "+marker)
 write(p,old.rstrip()+"\n\n"+body.strip())

def main():
 ep=ROOT/"research/EVIDENCE.json"; ev=json.loads(ep.read_text(encoding="utf-8"))
 by={x.get("id"):x for x in ev["items"]}
 missing=[x for x in SOURCES if x not in by]
 if missing: raise SystemExit("missing synthesis sources: "+", ".join(missing))
 if "EV-0374" in by: raise SystemExit("EV-0374 exists")
 note=TX/"EV-0374-note.md"
 write(note,"""# EV-0374 — P0 cross-domain synthesis: quest initiation, HitData, and teardown callbacks

## Scope and method

This is a source-linked synthesis of prior record, native-code, readiness, and callback investigations. It adds no new game or runtime observation. Source build/runtime limits remain attached to the cited evidence: quest records are bounded to the scanned official-master corpus, native code is GOG AE 1.6.1179.0 static analysis, the installed Steam executable is separately 1.6.1170.0, and exact profile/live telemetry is unverified.

## Competing cross-domain models and discriminants

- H1: the DA04 book/quest path and the ProcessTrapHit armor-XP path share an engine call, ActorValue, serialized field, or runtime state that creates a causal cross-objective route.
- H2: the mapped quest and hit/skill paths are independent; generic event, callback, reference-count, or skill-use names are analogies without a causal edge.
- H1 requires an exact shared call/data path or a controlled runtime observation linking DA04 stage state to HitData, armor protection, or AVSK. A clean trace showing separate calls and state with no cross-read/write would falsify H1 for these paths.

## Source-backed synthesis

- OBJ-1: DA04 is Start Game Enabled, and its forced RuminationsBook alias script requests stage 1 on read; the level-15 GetLevel helper is a separate courier route. This is an ordinary low-level stage/progression candidate, not proof of a level-gate bypass or level-one runtime result: alias fill, physical access, native startup, useful progression, and the exact Steam transition remain unobserved [EV-0301].
- OBJ-2: the GOG HitData builder copies physicalDamage before applying AV39 and worn-armor base-factor reduction to totalDamage; ProcessTrapHit reaches the common handler without a direct call through the known AV11/AV12 or AV9 skill resolver. The handler's mapped visible UseSkill site is AV15 Sneak. This is a physical-trap zero-armor-XP candidate, not proof of positive final damage, effective protection, zero raw AVSK, Steam equivalence, or vanilla reproduction [EV-0217, EV-0222, EV-0261, EV-0324].
- Q-0064: the ProcessTrapHit constraint starts with an empty callback array; the wrapper attachment and temporary release leave its reference count above the finalizer boundary. Deletion/removal consumers can invoke populated callback entries, but the pointer-window screen, vector-width candidate screens, and typed-record candidate establish no callback producer, ProcessTrapHit chain-factory owner, Actor::UseSkill descendant, or AV11/AV12 argument [EV-0365–EV-0368, EV-0370–EV-0373].
- Cross-domain assessment: no mapped DA04 call, ActorValue, HitData field, constraint callback, or serialized state is shared with the physical-hit/armor-skill path. H2 is supported only for the paths examined. Do not infer that the systems can never share a lower-level engine service.
- Runtime boundary: the exact clean Steam profile/order, disposable save, loaded read-only Observer, and raw AVSK/protection test are unavailable in EV-0260; that does not block the available GOG static path.

## Result and next discriminant

The current P0 candidates remain independent: pursue DA04's level-one book-read/start transition under its own live gate, and keep physical-trap mitigation/zero-armor-XP under its own matched hit test. Do not promote a cross-domain edge from shared generic APIs. Within Q-0064, select the still-unresolved PlayerCharacter +0x8F8 release site because its producer is tied to the explicit `Actors\\Character\\1stPerson\\Skel` resource path. Resolve the retained object's class/vtable through the GOG loader return and exact slot +0x8 finalizer; follow the concrete target toward PlayerCharacter slot 0xF7 / FUN_140739050 and FUN_14077d090. The archive route documented by the repository is a narrow classic-PEX extractor, not a general NIF parser, so use a NIF source only if a tested read-only route is present.

## Falsifying observation

The no-edge assessment would be falsified for the mapped paths by an exact shared native call or state field, a direct caller/dataflow edge between DA04 stage handling and HitData/armor skill progress, or a controlled clean runtime trace showing that changing DA04 quest state changes the trap's armor mitigation or raw AVSK outcome without an intervention.
""")
 docs={
  "README.md":"# EXP-0112 — P0 cross-domain synthesis\n\nCompare DA04 ordinary initiation, physical-trap HitData mitigation, and Q-0064 callback teardown without treating shared generic APIs as causal evidence.\n",
  "hypothesis.md":"# Competing models\n\n- H1: the mapped DA04 path and ProcessTrapHit armor-XP path share an exact engine call, ActorValue, serialized field, or state dependency.\n- H2: the paths remain independent in the evidence examined; generic callback/event names are analogy only.\n",
  "protocol.md":"# Protocol\n\nRead source IDs, linked claims/mechanisms and the existing experiment notes. Compare exact calls, records, ActorValues, HitData fields and serialized state. Preserve build/runtime provenance and record a falsifier for any proposed edge.\n",
  "expected-discriminants.md":"# Expected discriminants\n\nA causal cross-objective link requires an exact shared call/data/state edge or a controlled runtime dependency. Separate mapped paths support a bounded no-edge assessment.\n",
  "results.md":"# Results\n\nDA04's ordinary book-read path and the physical-trap HitData/armor-skill path remain separate in the source evidence. The latter is the stronger static OBJ-2 candidate, but its protection and raw AVSK result are unmeasured. Q-0064 callback producer/target remains unresolved. See EV-0374.\n",
  "implications.md":"# Implications\n\nKeep the DA04 level-one transition test and the trap hit/protection/AVSK test as separate frontier lines. Continue static Q-0064 on the exact +0x8F8 retained resource and slot +0x8 finalizer.\n",
 }
 for n,s in docs.items(): write(EXP/n,s)
 mf=TX/"EV-0374-source-manifest.json"
 manifest={"evidence_id":"EV-0374","synthesis_only":True,"source_evidence_ids":SOURCES,
  "source_claim_ids":["CL-L136","CL-L137","CL-L138","CL-L184","CL-L205","CL-L206","CL-L207","CL-L208","CL-L210","CL-L211","CL-L212","CL-L213"],
  "registered_local_hashes":{}}
 hashes={note.relative_to(ROOT).as_posix():sha(note),Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))}
 for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
 manifest["registered_local_hashes"]=hashes
 write(mf,json.dumps(manifest,indent=2,ensure_ascii=False)); hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
 ev["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
  "id":"EV-0374","kind":"native","source":"Source-linked P0 cross-domain synthesis of DA04 quest initiation, GOG ProcessTrapHit armor mitigation, and hkp teardown callback research.",
  "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0374-note.md","sha256":sha(note),
  "runtime":"Synthesis only; inputs retain their own official-master/GOG/Steam scope. No new live or runtime observation.","lane":"mechanism_inference",
  "tools":["research evidence, claims, mechanisms, frontier, and experiment ledger review"],
  "coverage":"Bounded comparison of DA04's book-read start path, physical-trap HitData mitigation/skill routing, and ProcessTrapHit constraint callback ownership.",
  "result":"No causal edge is supported between the mapped DA04 path and the physical-trap armor/skill path. Physical-trap mitigation-before-skill routing remains the strongest static OBJ-2 candidate; DA04 book-read remains a separate OBJ-1 candidate. The Q-0064 callback producer/target remains unresolved.",
  "related_evidence":SOURCES,"local_hashes":hashes})
 write(ep,json.dumps(ev,indent=2,ensure_ascii=False))
 cp=ROOT/"research/CLAIMS.md"
 append_once(cp,"| CL-L214 |","| CL-L214 | Within the mapped evidence, DA04's book-read quest path shares no identified native call, ActorValue, HitData field, constraint callback, or serialized state with the ProcessTrapHit armor/skill path; generic callbacks or event APIs remain analogy only. | supported for the examined paths/build scopes | [EV-0374], [EV-0301], [EV-0261], [EV-0324], [EV-0370] | A shared call/data path or controlled clean runtime dependency would falsify this bounded no-edge assessment. |")
 append_once(ROOT/"research/CONTRADICTIONS.md","## C-SYN-OBJ1-OBJ2-DA04-HITDATA","""## C-SYN-OBJ1-OBJ2-DA04-HITDATA — quest state and armor skill route

- **Model A:** DA04 book-read/start state shares a causal engine call or state field with ProcessTrapHit armor mitigation or skill progress.
- **Model B:** the mapped DA04 and physical-hit paths are independent; shared generic callback/event names are analogy only.
- **Evidence:** DA04's ordinary book-read SetStage path [EV-0301]; HitData mitigation and trap-handler route [EV-0261, EV-0324]; bounded constraint callback ownership [EV-0365–EV-0373].
- **Assessment:** B is supported for the paths examined. No exact shared call, ActorValue, HitData field, or serialized state is identified [EV-0374].
- **Falsifier:** an exact shared native/data edge or a controlled clean runtime trace where changing DA04 state changes trap mitigation or raw AVSK without intervention.""")
 append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0374 synthesizes the DA04 and trap armor paths","""### P0 cross-domain synthesis — DA04 and physical-trap armor XP (EV-0374)

DA04 book-read stage transition [EV-0301] and ProcessTrapHit HitData mitigation/skill routing [EV-0261, EV-0324] remain a **bounded no-edge** in the mapped evidence. No shared call, ActorValue, HitData field, constraint callback owner, or serialized state is identified [CL-L214]. Generic event/callback vocabulary is analogy only. This assessment is falsified by an exact common call/data dependency or a controlled clean runtime result showing DA04 stage state changes trap mitigation or raw AVSK. The physical-trap route remains the strongest static OBJ-2 candidate, while DA04 remains an independent OBJ-1 low-level-start candidate. EV-0370–EV-0373 do not identify a callback producer/target; Q-0064 continues at the PlayerCharacter +0x8F8 resource finalizer.""")
 fp=ROOT/"research/FRONTIER.json"; fr=json.loads(fp.read_text(encoding="utf-8")); q=next(x for x in fr["items"] if x.get("id")=="Q-0064")
 if q.get("status")!="in_progress": raise SystemExit("Q-0064 inactive")
 if "EV-0374" not in q.setdefault("evidence",[]): q["evidence"].append("EV-0374")
 if "CL-L214" not in q.setdefault("linked_claims",[]): q["linked_claims"].append("CL-L214")
 q["cross_domain_synthesis"]={"assessment":"bounded_no_edge_supported","source_ids":["EV-0301","EV-0261","EV-0324","EV-0370","EV-0373"],
  "status":"generic event/callback sharing is analogy only","falsifier":"an exact shared native/data edge or a controlled clean runtime trace showing DA04 stage state changes ProcessTrapHit mitigation or raw AVSK"}
 q["next_action"]="Select the unresolved PlayerCharacter +0x8F8 release site. Trace FUN_140736be0 through FUN_140e05900 and its handle member +0x28 to identify the retained object's exact class/vtable; resolve that object's slot +0x8 finalizer and follow its bounded target toward PlayerCharacter slot 0xF7 / FUN_140739050 and FUN_14077d090. Keep any negative limited to this field and build."
 q.setdefault("methods",[]).append("EV-0374 preserves a bounded no-edge between DA04 book-read initiation and ProcessTrapHit armor/skill routing; the two P0 runtime discriminators remain separate.")
 write(fp,json.dumps(fr,indent=2,ensure_ascii=False))
 append_once(ROOT/"STATE.md","P0 cross-domain synthesis / EV-0374","- EV-0374 keeps DA04 book-read initiation and ProcessTrapHit armor mitigation/skill routing as independent P0 candidates; no shared call, ActorValue, HitData field, callback owner, or serialized state is mapped. Q-0064 next resolves PlayerCharacter+0x8F8's retained resource class and slot+0x8 finalizer.")
 append_once(ROOT/"ROADMAP.md","EV-0374 cross-domain synthesis","EV-0374 confirms no causal bridge between the examined DA04 and physical-trap paths; keep the DA04 level-one and trap protection/raw-AVSK tests separate. Q-0064 proceeds at the exact +0x8F8 resource finalizer [CL-L214].")
 append_once(ROOT/"experiments/README.md","EXP-0112 / EV-0374","EXP-0112 / EV-0374 synthesizes DA04 initiation and physical-trap armor routing as separate P0 candidates; Q-0064 moves to +0x8F8 resource/finalizer resolution.")
 print("Registered EV-0374 / CL-L214; preserved the bounded no-edge and selected the exact +0x8F8 teardown discriminator.")

if __name__=="__main__": main()
