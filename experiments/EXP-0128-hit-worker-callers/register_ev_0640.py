#!/usr/bin/env python3
"""Register caller 58/tag 0x5A as a bounded spatial-state route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    ".local/ghidra/gog-query-20261019T214305Z": "3c7664f6e0fc3c3e5953f171e9ea3847a33be4d4b480d6bc0298aee8f173b20e",
    ".local/ghidra/gog-query-20261019T214415Z": "1e7d537f89338f76538499f8fd2bdce1119ee6710ed24eb691678cdaac073cb8",
    ".local/ghidra/gog-query-20261019T214527Z": "b31a7cf3036e5597fa0286bebb3a3fcd4adf23cb54007f12272094a626a5d29f",
    ".local/ghidra/gog-query-20261019T214639Z": "2bfc3dd5529b1680b187bb9d669d010e926e1142c48a02a730a40f58941530c5",
    ".local/ghidra/gog-query-20261019T214751Z": "cea89c8881d380aa7b92dd90e89f62aebb41682afbe0f72c4da68653e401d8df",
    ".local/ghidra/gog-query-20261019T214951Z": "e6a714e94ed99dd51eab84a549a14a2e55db39cfd0bee678923524229b8deb6d",
}
META_HASHES = {
    ".local/ghidra/gog-query-20261019T214305Z.meta.json": "06744a7e3a6331df45d42b049ee0b599a1ce4d63cb6631b0ff2fb64cf0e1d00e",
    ".local/ghidra/gog-query-20261019T214415Z.meta.json": "2fc3c8bf3dc9ae12b4860aad96de94ce2e538f3e1247a393b0feb3e327cf6cb3",
    ".local/ghidra/gog-query-20261019T214527Z.meta.json": "cd5c006136d1aa2dd0206636d4e5a8c3716fe04afdf42f8cffba5c9d1191b619",
    ".local/ghidra/gog-query-20261019T214639Z.meta.json": "65b85df8668c3d34b1977a8a2d7feeb434534003f4ff7d9593f5ef0cebcd75cf",
    ".local/ghidra/gog-query-20261019T214751Z.meta.json": "118b5ecd43f05df4414036012c0d1f0fdc3b49ac91e2fd25781955de3de15b23",
    ".local/ghidra/gog-query-20261019T214951Z.meta.json": "bd80c1eff795e6651d35e176a98c98c1031c2c61c1265177b5b0f5b7ee23a6f0",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        return
    write(path, old.rstrip() + "\n\n" + body.strip())


def main() -> None:
    raws: dict[str, str] = {}
    local_hashes: dict[str, str] = {}
    metas = []
    for base, expected in CAPTURES.items():
        rel = base + ".stdout.raw"
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("capture/hash mismatch: " + rel)
        raws[base] = path.read_text(encoding="utf-8", errors="replace")
        local_hashes[rel] = expected
    for rel, expected in META_HASHES.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("metadata/hash mismatch: " + rel)
        meta = json.loads(path.read_text(encoding="utf-8"))
        if not (meta.get("ok") and meta.get("read_only") and meta.get("auto_analysis_disabled")
                and meta.get("program_executable_path_matches_gog_binary")
                and meta.get("analysis_binary_product_version") == "1.6.1179"
                and meta.get("analysis_binary_sha256") == GOG_SHA):
            raise SystemExit("failed GOG identity/read-only gate: " + rel)
        metas.append(meta)
        local_hashes[rel] = expected
    proof_sets = [
        (".local/ghidra/gog-query-20261019T214305Z", [
            "TARGET_RVA=0x658DD0", "local_88[0] = 0x5a;",
            "OUTGOING_DIRECT_CALL_EDGE_COUNT=1", "caller=FUN_14051df20",
            "caller=FUN_140686320",
        ]),
        (".local/ghidra/gog-query-20261019T214415Z", [
            "case 0x5a:", "FUN_1405259c0(DAT_1420f9d78,&local_20c,*(undefined1 *)(param_1 + 4));",
            "OUTGOING_DIRECT_CALL_EDGE_COUNT=5", "INDIRECT_CALL_SITE_COUNT=13",
            "DAT_143188918 + 0x54", "param_1 + 0xd8",
        ]),
        (".local/ghidra/gog-query-20261019T214527Z", [
            "DECOMPILATION_BEGIN=FUN_14051df20", "hkpAllCdBodyPairTempCollector::vftable",
            "FUN_140658dd0(uVar11,uVar17,0);", "INCOMING_CALLER_FUNCTION_COUNT=4",
        ]),
        (".local/ghidra/gog-query-20261019T214639Z", [
            "DECOMPILATION_BEGIN=FUN_140686320", "param_2 + 0x2c) & 0x7f",
            "FUN_140658dd0(DAT_14319a7c0,local_res10,bVar9);",
            "XREF_ANY=14189f100 -> 140686320",
        ]),
        (".local/ghidra/gog-query-20261019T214751Z", [
            "INCOMING_CALLER_FUNCTION_COUNT=0", "DECOMPILATION_BEGIN=FUN_140731e80",
            "fStack_30 < param_3", "FUN_1405257b0(DAT_1420f9d78,bVar4,fVar7);",
        ]),
        (".local/ghidra/gog-query-20261019T214951Z", [
            "VTABLE_SLOT_INDEX=0x9C", "VTABLE_SLOT_TARGET_RVA=0x686320",
            "VTABLE_RTTI_TYPE_NAME=.?AVActor@@", "VTABLE_RTTI_SUBOBJECT_OFFSET=0/0x0",
        ]),
    ]
    for base, tokens in proof_sets:
        for token in tokens:
            if token not in raws[base]:
                raise SystemExit("proof token missing: " + token)

    note = EXP / "EV-0640-caller58-tag5a-spatial-state-route.md"
    write(note, """# EV-0640 — Caller 58 tag-0x5A spatial-state update

## Competing models and discriminants

- H1, spatial/physics state: tag 0x5A updates a handle-keyed coordinate record after a geometry or object-state predicate. It predicts the Player/object coordinate reads, shared manager collection, Actor threshold producer, and Havok contact-list producer.
- H2, progression/quest gate: the threshold or callback changes level eligibility or starts level-gated content. It predicts a Player-level comparison or a producer-backed edge into a mapped Story Manager/quest-start transition.
- H3, incoming-hit/armor route: the event reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed edge to those mapped sinks; the handler's unresolved virtual calls alone are not sufficient.

## Direct GOG evidence

All captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. No GOG RVA transfers to Steam AE 1.6.1170.0.

- FUN_140658dd0 writes tag 0x5A with a dword copied from an object and one boolean byte, then queues through FUN_14065b800 [EV-0640]. Worker case 0x5A resolves the object handle and calls FUN_1405259c0 with the manager DAT_1420f9d78 and the byte [EV-0637], [EV-0640].
- FUN_1405259c0 has five direct calls and 13 unresolved indirect sites. When the handle resolves and the boolean is true, it reads PlayerCharacter position at +0x54/+0x58 and the resolved object's +0x54/+0x58/+0x5C coordinates, creates or updates a record in the manager's keyed collections, and stores coordinate-derived floats. A null handle or false boolean follows a cleanup/removal branch. Its dynamic manager callbacks are unresolved [EV-0640].
- One producer is FUN_140686320, verified as primary VTABLE::Actor slot 0x9C (+0x4E0) under RTTI type .?AVActor@@ and subobject offset zero. The method checks object-form type bits, Actor process presence, two process virtual results, and a float threshold derived from FUN_1406751a0(Actor), Actor+0x5C, and a scale constant. It queues tag 0x5A with an object identifier and the threshold result [EV-0640]. Its sole analyzed direct caller is FUN_140731e80; that method compares a supplied float with a geometry-derived value and calls FUN_1405257b0 on the same manager. FUN_140731e80 itself has no analyzed incoming direct caller; its owner remains unknown [EV-0640].
- The second producer FUN_14051df20 removes a matching object/member from a keyed manager collection and may emit tag 0x5A with a false byte while cleaning the last entry. One of its four analyzed direct callers, FUN_14051d8c0, builds an hkpAllCdBodyPairTempCollector and processes collision-body pairs before calling this helper. Other callers include FUN_14051e3b0, FUN_14051e650 and FUN_14051f800; their wider runtime roles remain open [EV-0640].

## Result and limits

H1 is supported for the bounded spatial/coordinate-state path. H2 is not supported by the captured bodies: no Player-level predicate or mapped quest-start edge appears. H3 has no mapped direct HitData/protection/AV11/AV12/UseSkill sink, but 13 manager virtual sites and descendants remain unresolved. The result is not a vanilla level-one bypass, effective-protection/armor-XP result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Continue the exact worker-caller census at caller 59/62, FUN_140658e10; keep the manager virtual sites scoped and prioritize any caller with an explicit level or combat/skill discriminator.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ids = {row.get("id") for row in evidence.get("items", [])}
    if not {"EV-0344", "EV-0400", "EV-0637"} <= ids:
        raise SystemExit("missing contextual evidence")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    ev640 = {
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0640", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 58/tag 0x5A, both direct producers, Actor vtable slot, dispatcher, spatial manager target, and Havok collision-pair caller.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T214305Z.stdout.raw",
        "sha256": CAPTURES[".local/ghidra/gog-query-20261019T214305Z"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries with auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge and Actor-vtable-slot queries"],
        "coverage": "Tag-0x5A builder/dispatcher; keyed coordinate manager target; 13 unresolved virtual sites; Actor slot 0x9C producer; float/geometry caller; keyed collection removal producer; Havok overlap caller.",
        "result": "Caller 58 routes a dword/boolean payload into a handle-keyed spatial coordinate update/removal path. A producer is verified at primary Actor slot 0x9C; another producer is called from a Havok contact-pair path. The bounded bodies show no Player-level comparison or mapped direct HitData/protection/AV11/AV12/UseSkill sink. Manager callbacks and wider invoker context remain unresolved.",
        "local_hashes": local_hashes, "related_evidence": ["EV-0344", "EV-0400", "EV-0637"],
    }
    if "EV-0640" not in ids:
        evidence["items"].append(ev640)
        write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L453 |",
        "| CL-L453 | In GOG AE 1.6.1179.0, caller 58 tag 0x5A carries a dword/boolean payload to a handle-keyed coordinate-state manager; one producer is primary Actor slot 0x9C and another is reached from a Havok contact-pair path. | supported for captured static route | [EV-0637], [EV-0640] | The 13 manager virtual sites, wider invoker context, quest/level effects, HitData/protection/armor-skill effects, and Steam behavior remain unresolved. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0193 —",
        """## M-0193 — Tag-0x5A handle-keyed coordinate state update (EV-0640)

Caller 58 FUN_140658dd0 writes tag 0x5A with an object-derived dword and boolean byte. Dispatcher case 0x5A resolves the handle and calls FUN_1405259c0 on manager DAT_1420f9d78 [EV-0637], [EV-0640]. When the handle and boolean permit, the target reads PlayerCharacter and object coordinates and creates or updates a handle-keyed record; false/null cases remove or clean state. The target has five direct calls and 13 unresolved manager virtual sites [EV-0640].

Producer FUN_140686320 is primary Actor vtable slot 0x9C under verified RTTI .?AVActor@@. It checks process/object predicates and a float threshold from Actor state, then emits the event; FUN_140731e80 is its sole analyzed direct caller, compares a supplied float against geometry-derived state, and updates the same manager [EV-0400], [EV-0640]. Producer FUN_14051df20 removes matching collection entries and can emit a false-byte cleanup event; one of its callers processes Havok contact pairs with hkpAllCdBodyPairTempCollector [EV-0640]. The route is bounded spatial/physics state, not a mapped quest level check or incoming-hit/armor-skill path. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L453.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q79-TAG5A-SPATIAL-STATE-VS-HIT-ARMOR",
        """## C-OBJ2-Q79-TAG5A-SPATIAL-STATE-VS-HIT-ARMOR — coordinate manager versus hit/skill route

- Model A: tag 0x5A updates or removes handle-keyed coordinate state from Player/object geometry and Actor/physics predicates.
- Model B: an unresolved manager virtual callback converts the event into HitData, protection, AV11/AV12, or UseSkill processing.
- Evidence: builder, two producers, tag-0x5A dispatcher, coordinate manager body, Actor slot 0x9C identity, and Havok contact-pair caller [EV-0637], [EV-0640].
- Assessment: Model A is supported for the bounded static route. Model B has no mapped direct sink; 13 manager virtual sites and descendants remain open. This is not a transitive/runtime negative or a Steam result. No OBJ-2 causal edge is added.
- Discriminant: resolve only producer-backed manager virtual targets and show a data/control path into a mapped HitData/armor-skill sink; otherwise retain the spatial-state scope.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0640 maps caller 58 tag-0x5A coordinate state",
        """### EV-0640 maps caller 58 tag-0x5A coordinate state

Caller 58's tag 0x5A reaches a handle-keyed spatial manager. Its two producers include primary Actor slot 0x9C threshold logic and a keyed collection cleanup path called from Havok contact-pair processing [EV-0640]. The manager reads Player/object coordinates and keeps 13 indirect callbacks unresolved. This shares only a broad spatial/physics domain with caller 54's Actor context work; no common object, manager, quest predicate, HitData field, protection calculation, or armor-skill writer is established [EV-0636], [EV-0640]. No OBJ-1/OBJ-2 causal edge is added. Claim mapping: CL-L453 -> M-0193.""")
    append_once(EXP / "results.md", "### Caller 58/62: tag-0x5A spatial-state route (EV-0640)",
        """### Caller 58/62: tag-0x5A spatial-state route (EV-0640)

Caller 58 writes tag 0x5A with a dword and boolean. Dispatcher case 0x5A resolves the object handle and calls FUN_1405259c0 on a manager; its true branch uses PlayerCharacter and object coordinates to create/update a keyed record, while false/null cases clean up state. The target has five direct calls and 13 unresolved virtual sites [EV-0637], [EV-0640].

Producer FUN_140686320 is verified as primary Actor slot 0x9C and emits the tag under object/process/float-threshold predicates. Its only analyzed direct caller FUN_140731e80 compares a float with geometry-derived state. Producer FUN_14051df20 removes keyed entries; one caller processes hkpAllCdBodyPairTempCollector collision pairs [EV-0640]. The bounded route shows no Player-level check or mapped direct HitData/protection/AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 causal edge is added. Continue caller 59/62 FUN_140658e10.""")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    known_hypotheses = {row.get("id") for row in item.get("hypotheses", [])}
    has_new_hypotheses = {"Q79-H157", "Q79-H158"} <= known_hypotheses
    next_action = ("Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658e10 "
                   "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
                   "review worker caller 59/62 FUN_140658e10 for its exact tag, payload, producer, and "
                   "dispatcher route, prioritizing explicit level/combat discriminants.")
    if not has_new_hypotheses:
        item["hypotheses"].extend([
        {"id": "Q79-H157",
         "model": "Caller 58 tag 0x5A updates/removes handle-keyed coordinate state from Player/object geometry and Actor/physics predicates.",
         "predicted_discriminant": "The dispatcher target's coordinate reads and keyed manager record, Actor slot 0x9C threshold producer, and Havok contact-pair producer establish the bounded spatial route.",
         "status": "supported", "evidence": ["EV-0637", "EV-0640"]},
        {"id": "Q79-H158",
         "model": "A tag-0x5A manager callback or upstream condition changes level-one quest eligibility or reaches HitData/effective protection/armor-skill processing.",
         "predicted_discriminant": "Resolve producer-backed manager virtual targets and show a Player-level/quest-start condition or data/control edge into mapped HitData, protection, AV11/AV12, or UseSkill; the direct coordinate path alone does not support this.",
         "status": "proposed", "evidence": ["EV-0640", "EV-0260"]},
        ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0640"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L453"]))
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 58/tag-0x5A is bounded as coordinate/physics state with unresolved manager callbacks; continue caller 59.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 58 of 62 initially uninspected worker callers are reviewed, with 4 remaining."
    new_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 59 of 62 initially uninspected worker callers are reviewed, with 3 remaining."
    if state.count(old_count) != 1:
        raise SystemExit("STATE active caller-count mismatch")
    state = state.replace(old_count, new_count, 1)
    old_summary = "EV-0639 maps caller 57/tag 0x5F to perk-rank addition under a perk rank-count bound; wrapper callers and per-rank virtual effects remain unresolved, with no level-one bypass or mapped HitData/armor sink."
    new_summary = old_summary + " EV-0640 maps caller 58/tag 0x5A to handle-keyed coordinate/physics state; Actor slot 0x9C is one producer and 13 manager virtual sites remain open, with no mapped direct HitData/armor sink."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE caller-57 summary mismatch")
    state = state.replace(old_summary, new_summary, 1)
    count_old = "Q-0079 has 58/62 initially uninspected worker callers reviewed; 4 remain."
    count_new = "Q-0079 has 59/62 initially uninspected worker callers reviewed; 3 remain."
    if count_old in state:
        state = state.replace(count_old, count_new, 1)
    b = chr(96)
    old_next = ("**Selected next line:** run " + b + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658dd0 "
                "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600" + b +
                "; review worker caller 58/62 " + b + "FUN_140658dd0" + b +
                " for its exact tag, payload, producer and dispatcher route, then continue the bounded caller census. "
                "Caller 57 tag 0x5F is a perk-rank addition path; wrapper invokers and per-rank callbacks remain unresolved.")
    new_next = ("**Selected next line:** run " + b + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658e10 "
                "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600" + b +
                "; review worker caller 59/62 " + b + "FUN_140658e10" + b +
                " for its exact tag, payload, producer, and dispatcher route, prioritizing explicit level/combat "
                "discriminants. Caller 58 tag 0x5A is bounded as coordinate/physics state with 13 manager virtual sites open.")
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line mismatch")
    state = state.replace(old_next, new_next, 1)
    write(state_path, state)

    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 caller 58 (EV-0640)",
        """## Cross-domain synthesis — Q-0079 caller 58 (EV-0640)

Caller 58's tag 0x5A updates a handle-keyed coordinate record from Player/object positions; one producer is an Actor slot-0x9C threshold method and another comes from a Havok contact-pair collection [EV-0640]. Caller 54 also uses spatial predicates but reaches a different Actor/context state route; no shared receiver, manager, quest gate, HitData field, or armor-skill writer has been identified [EV-0636], [EV-0640]. The worker queue is shared infrastructure, not a common gameplay cause. The 13 manager virtual callbacks remain unresolved. No OBJ-1/OBJ-2 edge is added. Continue caller 59/62 FUN_140658e10, preferring explicit level or combat discriminants.""")
    print("Registered EV-0640/CL-L453/M-0193 and checkpointed caller 59.")


if __name__ == "__main__":
    main()
