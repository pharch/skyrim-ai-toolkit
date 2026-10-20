from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T173443Z"
EXPECTED_RVA = "0x5aed00"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != EXPECTED_RVA:
    raise SystemExit("FUN_1405aed00 query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f":
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0585",
    "source": "Identity-checked read-only GOG direct/incoming trace of FUN_1405aed00 and its shared handler FUN_1405b0730",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": sha(raw),
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x5aed00 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1405aed00 has 39 direct call xrefs in 37 caller functions and one outgoing direct edge to FUN_1405b0730; it also has an indirect call at record-related object slot +0x298. It returns if candidate+0x7c bit 18 is already set; otherwise it sets that bit. The Actor.DispelSpell matcher calls it with argument 1 for a candidate whose bit 18 was clear, which takes the path to FUN_1405b0730(candidate,0). The shared handler reads record fields +0x34/+0x7c/+0x74 and linked objects at +0x40/+0x48/+0x50, updates timing/state fields and status bits, and can call several virtual slots plus FUN_1405ae580 and FUN_1405b2950. Its exact record class, virtual method meanings, and terminal game effect are not established by this query.",
    "result": "EV-0584's Actor.DispelSpell match is a concrete record-state transition: a matched candidate with bit 18 clear is marked at candidate+0x7c and sent through a shared, multi-branch record handler. This refines the bounded lifecycle model but does not prove the candidate is an ActiveEffect or that the handler removes it. No direct HitData, protection, AV11/AV12, UseSkill, armor-XP, quest-initiation, or Steam runtime edge is established.",
    "local_hashes": {
        f".local/ghidra/{raw.name}": sha(raw),
        f".local/ghidra/{stderr.name}": sha(stderr),
        f".local/ghidra/{meta_path.name}": sha(meta_path),
    },
    "related_evidence": ["EV-0584", "EV-0583", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0585" in existing and existing["EV-0585"] != item:
    raise SystemExit("EV-0585 collision")
if "EV-0585" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L397",
    "| CL-L397 | In GOG AE 1.6.1179.0, the Actor.DispelSpell match path calls FUN_1405aed00(candidate,1); when candidate+0x7c bit 18 is clear, that routine sets bit 18 and sends the candidate to shared handler FUN_1405b0730(candidate,0). | supported for the exact bounded static path | [EV-0585], [EV-0584], [EV-0583] | Candidate RTTI, handler semantics, terminal effect and any HitData/protection/AV/skill consequence remain unresolved. |",
)

mechanisms = ROOT / "research/MECHANISMS.md"
mechanism_text = mechanisms.read_text(encoding="utf-8")
old = "The immediate helper sets candidate flag bit `0x40000` at `+0x7c` and conditionally calls `FUN_1405b0730`; a second caller walks `0xa8`-stride records and uses the same matcher. This supports a spell-linked effect-record state/lifecycle operation, but the candidate is not RTTI-confirmed as `ActiveEffect`, the list provider and queued branch are unresolved, and no link to HitData mitigation, effective armor, AV11/AV12, UseSkill or quest gates is established. Claims CL-L395–CL-L396; no objective causal edge is added."
new = "The immediate helper sets candidate flag bit `0x40000` (bit 18) at `+0x7c` and, for the tag-0x5e argument `1`, sends a candidate whose bit was clear to shared handler `FUN_1405b0730(candidate,0)` [EV-0585]. The handler changes record timing/status state and may call further virtual and direct helpers; their exact meanings and terminal effect remain open. A second caller walks `0xa8`-stride records and uses the same matcher [EV-0584]. This supports a spell-linked record-state/lifecycle operation, but the candidate is not RTTI-confirmed as `ActiveEffect`, the list provider and queued branch are unresolved, and no link to HitData mitigation, effective armor, AV11/AV12, UseSkill or quest gates is established. Claims CL-L395–CL-L397; no objective causal edge is added."
if old not in mechanism_text:
    raise SystemExit("M-0140 source paragraph not found")
mechanisms.write_text(mechanism_text.replace(old, new, 1), encoding="utf-8")

append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 42/62 follow-up: FUN_1405aed00 shared handler (EV-0585)",
    """### Caller 42/62 follow-up: FUN_1405aed00 shared handler (EV-0585)

The tag-0x5e `Actor.DispelSpell` path calls `FUN_1405aed00(candidate,1)` after `FUN_1405c4800` finds a matching candidate with bit 18 clear [EV-0584]. `FUN_1405aed00` sets candidate+`0x7c` bit 18 and takes the branch to `FUN_1405b0730(candidate,0)` [EV-0585]. The latter is a multi-branch timing/status handler that reads record and linked-object fields, changes status bits, and may call further virtual/direct helpers; this capture does not identify the record RTTI or prove a terminal removal effect. H77 remains supported as a spell-linked record-state/lifecycle model, while exact ActiveEffect identity remains open. No HitData/protection/AV11/AV12/UseSkill/armor-XP edge is added. Continue at worker caller 43/62 `FUN_140658890` [EV-0585].""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Q79-H77/H78 refinement after EV-0585",
    "Q79-H77/H78 refinement after EV-0585: `Actor.DispelSpell` calls `FUN_1405aed00(candidate,1)` for a SpellItem-matched candidate whose bit 18 is clear. The helper sets candidate+`0x7c` bit 18 and calls shared handler `FUN_1405b0730(candidate,0)` [EV-0585]. This strengthens a bounded record-state/lifecycle interpretation, while candidate RTTI, exact terminal effect, and any armor/protection/skill consequence remain unknown. The strict no-lifecycle H78 remains falsified for this branch; no OBJ-2 causal edge is added.",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0585 exact next worker caller",
    "EV-0585 bounds caller 42's transition to candidate bit-18 marking plus a shared status/timing handler; class and terminal effect remain unknown. Resume the primary census at `FUN_140658890` (caller 43/62), test its payload and producer against tag 0x0B and mapped HitData/AV11/AV12/UseSkill routes, and preserve no-edge results where direct evidence is absent.",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 42 shared state-handler synthesis: no armor causal edge",
    "Caller 42 shared state-handler synthesis: no armor causal edge\n\n"
    "EV-0585 narrows the Actor.DispelSpell route to an observed state transition: `FUN_1405aed00` sets bit 18 and calls `FUN_1405b0730`, whose broader state/timing and virtual-call behavior is not class-resolved. The record may be effect-related, but no source-backed path reaches effective armor, incoming HitData, AV11/AV12 or armor skill awards. Keep the P0-B search on mapped hit/skill sinks and measured protection/AVSK evidence rather than assigning those consequences to the spell-state route [EV-0585], [EV-0260].",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0585 refines the spell-linked state transition",
    "EV-0585 refines Actor.DispelSpell's matched-record route: it sets candidate+0x7c bit 18 and calls a shared timing/status handler. The handler and candidate class are not semantically resolved, so no edge to effective armor, HitData, AV11/AV12, UseSkill or OBJ-1 is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0585"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L397"]))
h77 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H77")
h77["model"] = "Actor.DispelSpell scans Actor+0xa0 for SpellItem-linked records and marks a matched candidate for shared state handling or queues deferred processing; exact record class and terminal effect remain unknown."
h77["predicted_discriminant"] = "The exact tag-0x5e path matches candidate+0x40, then calls FUN_1405aed00(candidate,1), which sets candidate+0x7c bit 18 and calls FUN_1405b0730(candidate,0); exact RTTI and downstream state effects remain open."
h77["status"] = "supported"
h77["evidence"] = list(dict.fromkeys([*h77.get("evidence", []), "EV-0585"]))
h78 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H78")
h78["status"] = "falsified"
h78["evidence"] = list(dict.fromkeys([*h78.get("evidence", []), "EV-0585"]))
assessment = "EV-0585 refines the bounded Actor.DispelSpell path: a SpellItem-matched record is marked at +0x7c bit 18 and enters shared timing/status handler FUN_1405b0730 [EV-0585]. This supports record-state/lifecycle handling but does not prove ActiveEffect RTTI or terminal removal, and it still provides no armor, HitData, AV11/AV12, UseSkill, or OBJ-1 causal edge."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658890 --list-call-edges --timeout 600; inspect worker caller 43/62 FUN_140658890 for payload/tag, producer provenance, dispatcher route, and any direct mapped HitData/AV11/AV12/UseSkill edge. Compare against Q79-H1/H2/H3, preserve tag/source uncertainty and the unavailable clean Steam matched-hit/protection/raw-AVSK discriminator, then continue caller 44/62."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 42/62 is bounded to Actor.DispelSpell/tag 0x5e matching a SpellItem-linked Actor+0xa0 record, setting bit 18, and entering shared state/timing handling. Exact record RTTI and terminal effect remain unknown; no HitData/protection/AV11/AV12/UseSkill or armor-XP edge is established. 20 callers remain.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0583/EV-0584 map caller 42 as Actor.DispelSpell/tag 0x5e to a SpellItem-matched Actor+0xa0 record lifecycle path; exact RTTI and final effects remain unresolved.",
    "EV-0583–EV-0585 map caller 42 as Actor.DispelSpell/tag 0x5e to a SpellItem-matched Actor+0xa0 record, bit-18 state transition, and shared timing/status handler; exact RTTI and terminal effect remain unresolved.",
    1,
)
state = state.replace(
    "EV-0583/EV-0584 map Actor.DispelSpell into a SpellItem-matched Actor+0xa0 record lifecycle path.",
    "EV-0583–EV-0585 map Actor.DispelSpell into a SpellItem-matched Actor+0xa0 record and shared bit-18 state handler.",
    1,
)
old_next = "**Selected next line:** query FUN_1405aed00, reached for matching Actor.DispelSpell records, to map its candidate state/deactivation transition and direct descendants; then resolve the list provider at receiver slot +0x38 and continue caller 43/62 FUN_140658890 [EV-0583], [EV-0584]."
new_next = "**Selected next line:** resume caller 43/62 `FUN_140658890` and classify its producer payload, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0585]. Keep the exact Actor.DispelSpell record class and handler terminal effect unresolved; caller 42 provides no direct armor/XP edge."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0585/CL-L397; refined M-0140 and Q79-H77/H78; checkpointed caller 43/62")
