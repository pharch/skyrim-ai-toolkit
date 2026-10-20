#!/usr/bin/env python3
"""Register the bounded hkpConstraintInstance callback-field writer census."""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
FRESH = {
 "20261018T074001Z": ["DECOMPILATION_BEGIN=FUN_140b43ab0", "CALLEE_DECOMPILATION_BEGIN=FUN_140b67350", "XREF_CALL_EDGE=140b3a8bc -> 140b43ab0"],
 "20261018T074223Z": ["DECOMPILATION_BEGIN=FUN_140b49450", "*plVar1 = 0"],
 "20261018T074324Z": ["DECOMPILATION_BEGIN=FUN_140b49260", "*(undefined8 *)(lVar5 + 0x40)", "*(undefined8 *)(lVar5 + 0x48)"],
 "20261018T074420Z": ["DECOMPILATION_BEGIN=FUN_140b494b0", "hkpLimitedHingeConstraintData::vftable"],
 "20261018T074533Z": ["XREF_CALL_COUNT=3", "INCOMING_CALLER_FUNCTION_COUNT=2", "INCOMING_CALLER_DECOMPILATION_BEGIN=FUN_140b439e0"],
 "20261018T074645Z": ["OFFSET_ACCESS_COUNT=14360", "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=2301", "OFFSET_WRITER_ANALYSIS_COMPLETE=true", "OFFSET_WRITER_FUNCTION_OUTPUT_LIMIT=16"],
 "20261018T074851Z": ["DECOMPILATION_BEGIN=FUN_140b43b80", "*(int *)(param_1 + 0x48) = *(int *)(param_1 + 0x48) + 1", "CALLEE_DECOMPILATION_BEGIN=FUN_140b43f90"],
}
REUSED = {"20261018T072523Z": ["OFFSET_ACCESS_COUNT=28807", "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT=3136", "OFFSET_WRITER_ANALYSIS_COMPLETE=true"]}
def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path: Path, value: str) -> None:
 path.parent.mkdir(parents=True, exist_ok=True); path.write_text(value.rstrip()+"\n",encoding="utf-8")
def checked(stamp: str, markers: list[str]):
 meta_path=GH/f"gog-query-{stamp}.meta.json"; meta=json.loads(meta_path.read_text(encoding="utf-8")); raw_path=ROOT/meta["artifacts"]["stdout"]; checks=meta.get("checks",{})
 valid=(meta.get("analysis_distribution")=="GOG" and meta.get("analysis_binary_product_version")=="1.6.1179" and meta.get("analysis_binary_sha256")==BINARY and meta.get("program_executable_path_matches_gog_binary") is True and meta.get("exit_code")==0 and meta.get("ok") is True and meta.get("read_only") is True and meta.get("auto_analysis_disabled") is True and meta.get("import_attempted") is False and meta.get("overwrite_attempted") is False and checks.get("program_identity_matches_gog_binary") is True and checks.get("script_no_error") is True and all(checks.values()) and sha(raw_path)==meta.get("stdout_sha256"))
 if not valid: raise SystemExit(f"capture identity/completion check failed: {stamp}")
 raw=raw_path.read_text(errors="replace")
 if any(marker not in raw for marker in markers): raise SystemExit(f"capture marker missing: {stamp}")
 return meta,meta_path,raw_path
def main() -> None:
 fresh={stamp:checked(stamp,markers) for stamp,markers in FRESH.items()}; reused={stamp:checked(stamp,markers) for stamp,markers in REUSED.items()}
 note=TX/"EV-0358-note.md"; manifest=TX/"EV-0358-capture-manifest.json"
 write(note,f"""# EV-0358 — hkpConstraintInstance callback-array writer census

## Build and method

Seven fresh identity-checked queries used the configured GOG AE 1.6.1179.0 project through the strict dispatcher in read-only/no-analysis mode. The prior whole-program +0x40 scan is reused from its local capture. The analysis binary SHA-256 is {BINARY}; these RVAs are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- FUN_140b43ab0 reaches FUN_140b67350 for its constraint argument. FUN_140b67350 reads the array pointer at +0x40 and low 16-bit count at +0x48, dispatches each non-null entry through that entry's virtual slot +0x10, then compacts null entries and reduces the count [capture 20261018T074001Z].
- The factory's post-registration FUN_140b49450 scans the constraint's +0x28 and +0x30 members for a match to the owner field at +0x38; a match triggers generic reference release and clears that member. It does not touch callback storage [capture 20261018T074223Z].
- Offset-only candidates do not identify a callback producer. FUN_140b49260's +0x40/+0x48 writes target a record returned by a keyed lookup and store coordinate pairs, not the exact constraint object [capture 20261018T074324Z]. FUN_140b494b0 initializes hkpLimitedHingeConstraintData, a distinct class [capture 20261018T074420Z].
- A complete direct-reference census of FUN_140b67350 finds three call sites in two functions: the two branches in FUN_140b43ab0 and one call in FUN_140b439e0. The latter then calls FUN_140b67d60; its incoming receiver lineage is not yet tied to the ProcessTrapHit factory object [capture 20261018T074533Z].
- The whole-program +0x48 scan reports 2,301 candidate writer functions and caps detailed output at 16; the reused +0x40 scan reports 3,136 candidate writers. The exact constructor FUN_140b48720 is among the nearby candidates, but it initializes the callback pointer to null and the low count to zero [captures 20261018T074645Z, 20261018T072523Z; constructor in EV-0356].
- Nearby FUN_140b43b80 writes +0x40/+0x48 fields in a separate owner-vector operation: it appends a larger record to a vector, updates a list index, and calls FUN_140b43f90 to merge records. This receiver/field contract does not match the constraint's callback pointer and packed count [capture 20261018T074851Z].

## Competing models and result

- Q64-H1 predicts producer-backed constraint callbacks/member finalizers stay outside AV11/AV12 skill progress.
- Q64-H2 predicts a concrete callback/member finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

This pass narrows the callback invocation site and rejects several nearby/global displacement matches as type evidence. No post-constructor callback-array writer or producer-backed callback target has been identified. H1/H2 remain unresolved; a capped offset scan cannot establish that no writer exists.

## Scope and exact next action

The result applies to the factory-created hkpConstraintInstance path and mapped helpers only. It does not establish runtime callback population, all possible computed-address writers, the exact receiver of FUN_140b439e0, effective armor protection, final damage, raw AVSK change, or Steam behavior. Trace FUN_140b439e0's incoming callers and concrete receiver lineage relative to the ProcessTrapHit factory object; then identify producer-backed writes to the exact +0x18/+0x28/+0x30 members or a callback-array registration call. Screen each resolved slot +0x18/final-release target for Actor::UseSkill AV11/AV12.
""")
 captures={}
 for stamp,(meta,_,_) in fresh.items(): captures[stamp]={"query_mode":meta.get("query_mode"),"requested_rva":meta.get("requested_rva"),"requested_search_displacement":meta.get("requested_search_displacement"),"checks":meta.get("checks"),"stdout_sha256":meta.get("stdout_sha256"),"stderr_sha256":meta.get("stderr_sha256"),"query_script_sha256":meta.get("query_script_sha256")}
 for stamp,(meta,_,_) in reused.items(): captures[f"{stamp}-reused-local-scan"]={"query_mode":meta.get("query_mode"),"requested_search_displacement":meta.get("requested_search_displacement"),"checks":meta.get("checks"),"stdout_sha256":meta.get("stdout_sha256"),"source_evidence":"EV-0357/EV-0356 transaction-local capture"}
 docs={
 "README.md":"# EXP-0096 — hkpConstraintInstance callback-array writers\n\nIdentify whether the ProcessTrapHit factory-created hkpConstraintInstance gains callback entries after construction, then follow any concrete callback target toward AV11/AV12.\n",
 "hypothesis.md":"# Competing models\n\n- Q64-H1: producer-backed callback/member descendants stay outside AV11/AV12 skill progress.\n- Q64-H2: a concrete callback/member finalizer reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.\n\nUnresolved dynamic receivers and capped offset scans leave both models open.\n",
 "protocol.md":"# Protocol\n\nStart from the exact FUN_140b48720 factory and the FUN_140b67350 consumer. Require build-identified read-only captures; match field offsets only after proving receiver lineage. Treat displacement scans as candidate generators with explicit caps.\n",
 "expected-discriminants.md":"# Expected discriminants\n\n1. Find a producer-backed write to the exact constraint's +0x40 callback pointer/+0x48 count or a concrete registration call.\n2. Resolve the callback entry class and slot +0x10 target from its exact producer.\n3. Resolve member classes at constraint +0x18/+0x28/+0x30 from their constructors or exact writers.\n4. Follow concrete targets to Actor::UseSkill and inspect the AV11/AV12 argument. A global offset match without receiver identity is inconclusive.\n",
 "predicted-outcomes.md":"# Predicted outcomes\n\n- A concrete callback/member-to-AV11/AV12 edge supports Q64-H2 for the resolved branch.\n- A producer-backed physics cleanup chain with no skill sink strengthens Q64-H1 only for those resolved descendants.\n- Missing receiver identity, capped scans, or unresolved virtual targets leave Q64-H1/H2 undecided.\n",
 "results.md":"# Results\n\nFUN_140b67350 consumes the exact hkpConstraintInstance callback array at +0x40/+0x48, but this pass finds no producer-backed writer. The complete direct callsite census has two caller functions; adjacent and whole-program offset matches include other records and remain untyped. Q64-H1/H2 remain open [EV-0358].\n",
 "implications.md":"# Implications\n\nThe callback consumer and its direct call boundary are mapped, but callback population is not. Continue from FUN_140b439e0's incoming receiver lineage and producer-backed member writes; do not treat offset-only results as a no-writer proof.\n"}
 for name,body in docs.items(): write(EXP/name,body)
 local_hashes={}
 for meta,meta_path,raw_path in [*fresh.values(),*reused.values()]:
  for path in [meta_path,raw_path,*(ROOT/item for item in meta["artifacts"].values())]:
   if path.is_file(): local_hashes[path.relative_to(ROOT).as_posix()]=sha(path)
 for path in [note,*EXP.iterdir(),Path(__file__)]:
  if path.is_file(): local_hashes[path.relative_to(ROOT).as_posix()]=sha(path)
 local_hashes.pop(manifest.relative_to(ROOT).as_posix(),None)
 write(manifest,json.dumps({"evidence_id":"EV-0358","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BINARY,"captures":captures,"registered_local_hashes":local_hashes},indent=2))
 local_hashes[manifest.relative_to(ROOT).as_posix()]=sha(manifest)
 evidence_path=ROOT/"research/EVIDENCE.json"; evidence=json.loads(evidence_path.read_text(encoding="utf-8"))
 if any(item.get("id")=="EV-0358" for item in evidence["items"]): raise SystemExit("EV-0358 is already registered")
 evidence["items"].append({"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,"id":"EV-0358","kind":"native","source":"Identity-checked read-only GOG Ghidra traces of the exact hkpConstraintInstance callback consumer, caller census, post-registration helper, and bounded displacement candidates.","artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0358-note.md","sha256":sha(note),"runtime":f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.","lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],"coverage":"FUN_140b67350 callback array consumer/callers, exact factory path, post-registration member cleanup, and nearby/global +0x40/+0x48 offset candidates.","result":"The exact callback consumer uses hkpConstraintInstance +0x40/+0x48 and dispatches populated entries through slot +0x10; its direct callers are FUN_140b43ab0 and FUN_140b439e0. Nearby/global displacement matches do not identify an exact producer. H1/H2 and callback population remain unresolved.","related_evidence":["EV-0355","EV-0356","EV-0357","EV-0324"],"local_hashes":local_hashes})
 write(evidence_path,json.dumps(evidence,indent=2,ensure_ascii=False))
 claims=ROOT/"research/CLAIMS.md"; ct=claims.read_text(encoding="utf-8")
 if "| CL-L197 |" in ct: raise SystemExit("CL-L197 is already registered")
 write(claims,ct.rstrip()+"\n| CL-L197 | In GOG AE 1.6.1179.0, the factory-created hkpConstraintInstance callback consumer uses +0x40/+0x48 and dispatches each populated callback through entry slot +0x10; its complete direct-call census has FUN_140b43ab0 and FUN_140b439e0 as caller functions. | supported for the exact consumer and analyzed direct references | [EV-0358], [EV-0356] | No post-constructor producer-backed callback writer or concrete callback class is identified; displacement scans are broad/capped, and transitive AV11/AV12 reachability remains unresolved. |")
 mechanisms=ROOT/"research/MECHANISMS.md"
 write(mechanisms,mechanisms.read_text(encoding="utf-8").rstrip()+"\n\n## M-0078 — hkpConstraintInstance callback-array consumer boundary (Q-0064)\n\nThe ProcessTrapHit factory path can reach FUN_140b67350, which iterates the exact constraint's +0x40 callback array using the low +0x48 count and calls each non-null entry through virtual slot +0x10. The constructor begins with null pointer/count zero. The direct call census finds FUN_140b43ab0 and FUN_140b439e0; nearby and global +0x40/+0x48 matches do not prove a writer for this receiver. Callback population and concrete callback/member descendants remain open; no no-skill conclusion follows [EV-0358], [EV-0356]. Claim CL-L197 -> M-0078.\n")
 graph=ROOT/"research/KNOWLEDGE_GRAPH.md"
 write(graph,graph.read_text(encoding="utf-8").rstrip()+"\n\nEV-0358 maps the hkpConstraintInstance callback consumer and bounds its direct callers, while exact callback population remains unresolved. The +0x40/+0x48 scan candidates include other receiver layouts and add no causal edge to Actor::UseSkill AV11/AV12 or to the EV-0326 Dawnguard quest route [CL-L194], [CL-L197].\n")
 roadmap=ROOT/"research/ROADMAP.md"
 write(roadmap,roadmap.read_text(encoding="utf-8").rstrip()+"\n\nEV-0358 maps the hkpConstraintInstance callback-array consumer and its direct callers, but identifies no exact producer. Next trace FUN_140b439e0's incoming callers/receiver lineage, then resolve producer-backed writes to +0x18/+0x28/+0x30 or callback registration. Broad offset scans remain candidate-only.\n")
 index=ROOT/"experiments/README.md"
 write(index,index.read_text(encoding="utf-8").rstrip()+"\n\nEXP-0096 / EV-0358 maps the hkpConstraintInstance callback-array consumer and direct call boundary; callback population and concrete targets remain unresolved.\n")
 frontier_path=ROOT/"research/FRONTIER.json"; frontier=json.loads(frontier_path.read_text(encoding="utf-8")); q64=next(item for item in frontier["items"] if item.get("id")=="Q-0064")
 for bucket in [q64.setdefault("evidence",[]),*(h.setdefault("evidence",[]) for h in q64.get("hypotheses",[]))]:
  if "EV-0358" not in bucket: bucket.append("EV-0358")
 if "CL-L197" not in q64.setdefault("linked_claims",[]): q64["linked_claims"].append("CL-L197")
 next_action="Trace FUN_140b439e0's incoming callers and concrete receiver lineage relative to the ProcessTrapHit factory object; then identify producer-backed writes to the exact +0x18/+0x28/+0x30 members or a callback-array registration call. Screen each resolved slot +0x18/final-release target for Actor::UseSkill AV11/AV12."
 q64["next_action"]=next_action; frontier_path.write_text(json.dumps(frontier,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 checkpoint=ROOT/"experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"; source=checkpoint.read_text(encoding="utf-8")
 needle="- Q-0064 / EV-0357 resolves the factory-created hkpConstraintInstance slot-0 finalizer to callback/member ownership cleanup and TLS allocation; callback +0x18 targets and member classes remain unresolved.\n"
 addition="- Q-0064 / EV-0358 maps the hkpConstraintInstance callback-array consumer and its two direct caller functions; constructor starts empty and broad +0x40/+0x48 scans identify no exact callback producer.\n"
 if needle not in source: raise SystemExit("checkpoint helper lacks EV-0357 summary line")
 source=source.replace(needle,needle+addition).replace("resolve producer-backed cleanup object classes and screen their descendants for AV11/AV12.","trace FUN_140b439e0 receiver lineage and resolve producer-backed callback/member writers before screening descendants for AV11/AV12.")
 checkpoint.write_text(source,encoding="utf-8")
 print("registered EV-0358 / CL-L197 / M-0078; Q-0064 remains active")
if __name__=="__main__": main()
