from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T173122Z"
EXPECTED_RVA = "0x5c4800"
raw, stderr, meta_path = (GH / f"{STEM}.stdout.raw", GH / f"{STEM}.stderr.raw", GH / f"{STEM}.meta.json")
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != EXPECTED_RVA:
    raise SystemExit("FUN_1405c4800 query identity failed")
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
    "id": "EV-0584",
    "source": "Identity-checked read-only GOG direct/incoming trace of FUN_1405c4800 from the Actor.DispelSpell route",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": sha(raw),
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x5c4800 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1405c4800 has three direct callees, one unresolved virtual call at receiver slot +0x38, 11 direct callsites from nine caller functions. It iterates entries returned by the container vslot +0x38. For each candidate it reads candidate+0x7c flags, matches candidate+0x40 against the SpellItem argument and conditionally candidate+0x34 against a supplied selector; additional filter arguments compare fields +0x58/+0x48. With the tag-0x5e route's default selector and zero final filter, a matched candidate goes to FUN_1405aed00(candidate,1) when the container's +0x10 bit is clear, or to FUN_1405c74e0 for deferred processing when set. FUN_1405aed00 sets bit 0x40000 at candidate+0x7c and calls FUN_1405b0730 on its non-early-return path. Caller FUN_1406c5950 independently walks a pointer-backed +0xa8-stride object list and calls FUN_1405c4800 on selected records; its body also constructs a DispelAliasSpellVisitor. Exact candidate RTTI/class and vslot +0x38 target remain unresolved.",
    "result": "The Actor.DispelSpell route does more than generic spell-registry membership: it scans a per-Actor+0xa0 collection for records matching the SpellItem and invokes a candidate state/deactivation routine or queues deferred processing. This supports a spell-linked effect-record lifecycle model and falsifies the strict no-lifecycle alternative for the bounded branch. The records are not yet RTTI-confirmed as ActiveEffect, the deferred target and virtual list provider remain unresolved, and no direct HitData, protection, AV11/AV12, UseSkill, armor-XP, quest-start, or Steam runtime edge is established.",
    "local_hashes": {
        f".local/ghidra/{raw.name}": sha(raw),
        f".local/ghidra/{stderr.name}": sha(stderr),
        f".local/ghidra/{meta_path.name}": sha(meta_path),
    },
    "related_evidence": ["EV-0583", "EV-0582", "EV-0581", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0584" in existing and existing["EV-0584"] != item:
    raise SystemExit("EV-0584 collision")
if "EV-0584" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

append_once(
    "research/CLAIMS.md",
    "CL-L395",
    "| CL-L395 | In GOG AE 1.6.1179.0, FUN_1405c4800 iterates a container-provided record list, matches a candidate's +0x40 to the supplied SpellItem and optional +0x34 selector, then either calls FUN_1405aed00(candidate,1) or queues FUN_1405c74e0 according to container bit +0x10. | supported for the exact helper body and tag-0x5e call arguments | [EV-0584], [EV-0583] | The record's exact RTTI/class and slot +0x38 list provider remain unresolved; no HitData/protection/AV11/AV12/UseSkill edge is established. |",
)
append_once(
    "research/CLAIMS.md",
    "CL-L396",
    "| CL-L396 | In the captured GOG path, FUN_1405aed00 marks a candidate at +0x7c with bit 0x40000 and conditionally calls FUN_1405b0730; FUN_1405c4800 reaches it for matching spell-linked records when deferred processing is not selected. | supported for the exact bounded helper/callee path | [EV-0584] | Candidate class, terminal effect and actual hit-mitigation or skill consequences remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0140 — Actor.DispelSpell spell-linked effect-record transition (EV-0583/0584)",
    """## M-0140 — Actor.DispelSpell spell-linked effect-record transition (EV-0583/0584)

The exact `Actor.DispelSpell` tag-0x5e path passes its SpellItem to `FUN_1405c4800` on Actor+`0xa0` [EV-0583]. The helper obtains a record list through an unresolved vslot `+0x38`, selects candidates by candidate+`0x40` SpellItem identity and optional fields, then either calls `FUN_1405aed00(candidate,1)` or queues `FUN_1405c74e0` depending on receiver bit `+0x10` [EV-0584]. The immediate helper sets candidate flag bit `0x40000` at `+0x7c` and conditionally calls `FUN_1405b0730`; a second caller walks `0xa8`-stride records and uses the same matcher. This supports a spell-linked effect-record state/lifecycle operation, but the candidate is not RTTI-confirmed as `ActiveEffect`, the list provider and queued branch are unresolved, and no link to HitData mitigation, effective armor, AV11/AV12, UseSkill or quest gates is established. Claims CL-L395–CL-L396; no objective causal edge is added.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 42/62: FUN_1405c4800 effect-record discriminator (EV-0584)",
    """### Caller 42/62: FUN_1405c4800 effect-record discriminator (EV-0584)

`FUN_1405c4800` iterates a record list through unresolved receiver vslot `+0x38`, matches candidate+`0x40` against the SpellItem argument, checks candidate+`0x34` when a non-default selector is supplied, and applies additional optional identity filters [EV-0584]. For the tag-0x5e arguments, a matched candidate calls `FUN_1405aed00(candidate,1)` unless receiver bit `+0x10` selects deferred queue helper `FUN_1405c74e0`. The immediate routine sets candidate flag bit `0x40000` at `+0x7c` and conditionally calls `FUN_1405b0730`; another direct caller walks a pointer-backed `0xa8`-stride list and passes its selected records to the same helper [EV-0584]. This supports Q79-H77 as a spell-linked effect-record lifecycle model and falsifies Q79-H78's strict no-lifecycle alternative. The records are not RTTI-confirmed as ActiveEffect, dynamic list provider/queue targets remain open, and no HitData/protection/AV11/AV12/UseSkill/armor-XP link is established. Next query FUN_1405aed00, then resolve the vslot +0x38 provider if needed.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Q79-H77/H78 result after EV-0584",
    """Q79-H77/H78 result after EV-0584: H77 is **supported for the bounded path** after `FUN_1405c4800` matches a SpellItem-backed record and routes it to candidate flag/deactivation handling or a deferred queue [EV-0584]. H78 is **falsified in its strict no-lifecycle form** because `FUN_1405aed00` writes candidate flag `+0x7c |= 0x40000` and conditionally calls `FUN_1405b0730`. Exact ActiveEffect RTTI and final effects remain unresolved; no protection/armor-XP edge follows.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0584 bounded spell-effect lifecycle result",
    """EV-0584 bounded result: SpellItem matching plus candidate flag/deactivation handling supports an effect-record lifecycle operation; the candidate class is not RTTI-confirmed. Resolve `FUN_1405aed00` direct/incoming descendants and the concrete list provider for receiver slot `+0x38`. A producer-backed target into damage/protection/AV11/AV12/UseSkill is required before adding a P0-B edge.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 42 cross-domain synthesis: effect-record lifecycle without armor causal edge",
    """Caller 42 cross-domain synthesis: effect-record lifecycle without armor causal edge

The Papyrus `Actor.DispelSpell` registration, tag-0x5e worker serialization, SpellItem match at Actor+`0xa0`, and candidate flag/deactivation call form a concrete bridge from script dispatch into Actor spell-effect state [EV-0583], [EV-0584]. This refines the earlier generic spell-state model. The candidate's exact class and final behavior remain unresolved; no link reaches effective armor rating, incoming HitData, AV11/AV12, UseSkill, or level-gated quests. The static path therefore does not qualify as a functional-armor/zero-XP candidate.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0584 adds spell-linked effect-record mutation",
    """EV-0584 refines Actor.DispelSpell: tag-0x5e's Actor+0xa0 helper matches a SpellItem-linked record, then sets candidate lifecycle/status state or defers the operation. Its list provider, record RTTI and terminal effect remain unresolved. No causal edge to armor protection, HitData, AV11/AV12, UseSkill, or OBJ-1 is supported.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0584"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L395", "CL-L396"]))
h77 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H77")
h77["model"] = "Actor.DispelSpell scans Actor+0xa0 for SpellItem-linked effect records and deactivates matched records or queues removal."
h77["predicted_discriminant"] = "FUN_1405c4800 matches candidate+0x40 against the SpellItem and routes the candidate to FUN_1405aed00 or deferred FUN_1405c74e0; exact record RTTI remains open."
h77["status"] = "supported"
h77["evidence"] = list(dict.fromkeys([*h77.get("evidence", []), "EV-0584"]))
h78 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H78")
h78["model"] = "FUN_1405c4800 only changes spell registry state and has no effect-record lifecycle operation."
h78["predicted_discriminant"] = "No producer-backed helper branch marks/deactivates a matching candidate or queues its removal; matching is limited to generic spell registry membership."
h78["status"] = "falsified"
h78["evidence"] = list(dict.fromkeys([*h78.get("evidence", []), "EV-0584"]))
assessment = "EV-0584 supports spell-linked effect-record lifecycle handling: FUN_1405c4800 matches candidates by SpellItem and routes them to flag/deactivation or deferred queue handling [EV-0584]. This falsifies the strict generic-registry/no-lifecycle alternative, but exact ActiveEffect class and protection/skill effects remain unknown. No armor-XP or OBJ-1 causal edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x5aed00 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; inspect the exact candidate deactivation/status transition reached by FUN_1405c4800, its incoming effect-record contexts, and direct descendants. Keep candidate RTTI, ActiveEffect identity, Steam mapping, and any armor/HitData/AV11/AV12 edge unresolved until direct evidence supports them."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 42/62 Actor.DispelSpell/tag 0x5e reaches FUN_1405c4800 on Actor+0xa0; the helper matches a SpellItem-linked record and deactivates/queues the candidate. Q79-H77 is supported and strict no-lifecycle H78 is falsified; candidate RTTI, concrete ActiveEffect identity, final effect, and armor/HitData/skill consequences remain unknown. 20 callers remain; next resolve FUN_1405aed00.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("registered EV-0584/CL-L395-396/M-0140; supported Q79-H77, falsified strict H78, checkpointed candidate deactivation query")
