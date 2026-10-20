#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
CAPTURES = [
    ".local/ghidra/gog-query-20261019T201510Z",
    ".local/ghidra/gog-query-20261019T202237Z",
    ".local/ghidra/gog-query-20261019T202353Z",
    ".local/ghidra/gog-query-20261019T202730Z",
    ".local/ghidra/gog-query-20261019T202930Z",
    ".local/ghidra/gog-query-20261019T203045Z",
    ".local/ghidra/gog-query-20261019T203230Z",
]
EXPECTED = {
    ".local/ghidra/gog-query-20261019T201510Z.stdout.raw": "f629e4da674675574a2d813f4657b8fc20d75233526023884b65ec8f52af38de",
    ".local/ghidra/gog-query-20261019T201510Z.meta.json": "c0ccc67c95573ab65d45216b2a67521d4dc749ef2a2025e7fa7f26f4293aad00",
    ".local/ghidra/gog-query-20261019T202237Z.stdout.raw": "79d47ccf08664e7a5a8f2144d091c299bab484a4b60082025d58422f64569398",
    ".local/ghidra/gog-query-20261019T202237Z.meta.json": "59ece2aaf34bdbf308e0fea2c5acec06105a6799541af2a6de953627df01ba0f",
    ".local/ghidra/gog-query-20261019T202353Z.stdout.raw": "457ca50119eee15fa155cba8f6c58eaa0e159440f1377215eb6b5e6b10fe0cec",
    ".local/ghidra/gog-query-20261019T202353Z.meta.json": "a557ab66316d13223b3756279cda22ca770fe494cfb90217483e5e864fb4dfa5",
    ".local/ghidra/gog-query-20261019T202730Z.stdout.raw": "feb76e04d29bb81a8e6706d7e28c15876b0716af558e8c69421177be747568c1",
    ".local/ghidra/gog-query-20261019T202730Z.meta.json": "0d4438199bbcae6ba7d61632a6d88138a9d4adb54e551094213d4679c5159ccf",
    ".local/ghidra/gog-query-20261019T202930Z.stdout.raw": "340a6ca35675d49f70fb36193944a4028f4cf4b00514dacaf9c7e85d88a0da6f",
    ".local/ghidra/gog-query-20261019T202930Z.meta.json": "c91b2d286ae4e08d9edc1cef1d6f2d3600056c0d163235f4d7b0a86836d8c85a",
    ".local/ghidra/gog-query-20261019T203045Z.stdout.raw": "431a64d4f5fe87fcefa87357ea1951859ef53187824900d7b743c732b9362d6f",
    ".local/ghidra/gog-query-20261019T203045Z.meta.json": "e8b975f93c3392630ce395bafb0b96999ca936bf23ee8ed6597c88006e1632e9",
    ".local/ghidra/gog-query-20261019T203230Z.stdout.raw": "7d35a99834ff79006abe5a9ea56c38b2ee9f1a9c9158937f87a06096548e8b26",
    ".local/ghidra/gog-query-20261019T203230Z.meta.json": "a27b39c13837e61d22068c05e9e6e3f72f28a249c212c83ff5c8439721ef4b32",
}
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c50 "
    "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
    "review worker caller 54/62 FUN_140658c50 for its exact tag/payload and producer, "
    "then continue the bounded caller census."
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, body: str) -> None:
    original = path.read_text(encoding="utf-8")
    if marker in original:
        raise SystemExit(f"duplicate marker: {marker}")
    write(path, original.rstrip() + "\n\n" + body.strip())


def main() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        if not path.exists() or sha(path) != expected:
            raise SystemExit(f"capture missing or hash mismatch: {relative}")
    metas = [json.loads((ROOT / f"{base}.meta.json").read_text(encoding="utf-8")) for base in CAPTURES]
    for meta in metas:
        if not (meta.get("ok") and meta.get("read_only") and meta.get("auto_analysis_disabled")):
            raise SystemExit("a Ghidra capture failed read-only or analysis-disabled verification")
        if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != GOG_SHA:
            raise SystemExit("a Ghidra capture does not match the verified GOG executable")

    raws = [(ROOT / f"{base}.stdout.raw").read_text(encoding="utf-8", errors="replace") for base in CAPTURES]
    dispatcher, builder, target, first_actor_block, producer, interior_rtti, actor_slots = raws
    if "case 0x50:" not in dispatcher or "thunk_FUN_1402ec610(plVar14);" not in dispatcher:
        raise SystemExit("tag-0x50 dispatcher target proof missing")
    for token in ["local_88[0] = 0x50;", "*(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + 1;", "FUN_14065b800(param_1,local_88);", "caller=FUN_140664cf0"]:
        if token not in builder:
            raise SystemExit("caller-53 builder/producer proof missing: " + token)
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=51",
        "INDIRECT_CALL_SITE_COUNT=17",
        "param_1 != DAT_143188918",
        "FUN_1406c21c0(plVar13,1)",
        "FUN_14073a380(DAT_143188918,param_1);",
        "XREF_ANY=140664d20 -> 1402ec610 type=UNCONDITIONAL_JUMP",
    ]:
        if token not in target:
            raise SystemExit("tag-0x50 target body proof missing: " + token)
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=1",
        "INDIRECT_CALL_SITE_COUNT=0",
        "FUN_140658c10(DAT_14319a7c0,param_1);",
        "INCOMING_CALLER_FUNCTION_COUNT=0",
        "XREF_ANY=14189f068 -> 140664cf0 type=DATA",
    ]:
        if token not in producer:
            raise SystemExit("caller-53 Actor producer context proof missing: " + token)
    if "POINTER_TABLE_BASE_RVA=0x189EC20" not in first_actor_block or "POINTER_TABLE_READ_COUNT=128" not in first_actor_block:
        raise SystemExit("bounded primary Actor table context is missing")
    if "VTABLE_RTTI_CENSUS_ENTRY=index:0 requested_rva:0x189F060" not in interior_rtti:
        raise SystemExit("misbased RTTI correction provenance missing")
    if "VTABLE_RTTI_SUBOBJECT_OFFSET=-1958207252/0x8B4820EC" not in interior_rtti:
        raise SystemExit("interior RTTI invalid-byte result missing")
    if "POINTER_TABLE_BASE_RVA=0x189F020" not in actor_slots or "POINTER_TABLE_ENTRY=index:9 address:14189f068 value:0x140664CF0" not in actor_slots:
        raise SystemExit("Actor slot +0x448 pointer proof missing")
    if "POINTER_TABLE_ENTRY=index:8 address:14189f060" not in actor_slots:
        raise SystemExit("adjacent Actor slot context missing")

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    by_id = {row.get("id") for row in evidence.get("items", [])}
    if "EV-0635" in by_id:
        raise SystemExit("EV-0635 already exists")
    for required in ["EV-0400", "EV-0344"]:
        if required not in by_id:
            raise SystemExit("missing contextual evidence: " + required)

    note = EXP / "EV-0635-caller53-tag50-actor-state-route.md"
    note_body = """# EV-0635 — Caller 53 tag-0x50 Actor state route

## Competing models and discriminants

- H1: tag `0x50` is part of an ordinary player-hit/effective-armor/armor-skill path. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill data or control edge, or a recipient path that performs this work on the PlayerCharacter.
- H2: tag `0x50` is an Actor/process state callback that is queued from an Actor virtual method and enters a separate state/update routine. It predicts an Actor-vtable producer, object-pointer payload, process-state predicates and no direct mapped HitData/armor-skill sink.

The discriminants are the exact builder payload, dispatcher callee, producer vtable identity and slot, target's direct/indirect call census, and its guard against the PlayerCharacter receiver.

## Direct GOG evidence

The captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled and did not import or overwrite the project. These GOG RVAs are not transferred to Steam AE 1.6.1170.0.

- Builder `FUN_140658c10` writes tag `0x50`, increments the retained object's reference count at `+0x28`, and queues the object through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_140664cf0` [EV-0635].
- `FUN_140664cf0` has no analyzed direct code callers. It is referenced as a function pointer at GOG address `0x14189f068` in the already identity-validated primary `VTABLE::Actor` table RVA `0x189ec20` [EV-0400], [EV-0635]. A bounded pointer capture beginning at RVA `0x189f020` confirms this is zero-based Actor slot `0x89` (`+0x448`). It excludes global `DAT_143138a98` and objects with bit 11 set at `+0x10`, then queues the remaining object [EV-0635].
- Dispatcher case `0x50` reads the object pointer from payload `+0x8` and calls thunk `FUN_140664d20`, which jumps to `FUN_1402ec610` [EV-0635]. This is the handler for the Actor-slot producer's retained pointer.
- `FUN_1402ec610` has 51 direct call edges and 17 unresolved virtual sites. Its entry guard skips the body if receiver flag bit 11 is set or the receiver equals `DAT_143188918`; that global is independently identified as PlayerCharacter [EV-0344]. Its remaining direct body compares Actor/process state, updates process/resource/object state, and calls helpers including `FUN_1406c21c0` and `FUN_14073a380`. No mapped HitData/protection/AV11/AV12/UseSkill direct target appears in the captured body [EV-0635].
- An initial RTTI query incorrectly treated interior Actor slot RVA `0x189f060` as a vtable start; its invalid COL bytes are superseded by the correct table-base/slot capture [EV-0635]. The separate data references to `FUN_1402ec610` do not establish its exact vtable slot or class. Keep its dynamic descendants open.

## Result and limits

H2 is supported for the captured direct route. The producer is an Actor primary-vtable method, and the worker handler skips PlayerCharacter receivers before performing its Actor/process state work. H1 has no direct support in the captured body. The handler still has 17 unresolved virtual sites, so this is not a global no-hit result; it does not establish Steam behavior, effective armor protection, armor XP, or a vanilla exploit. Caller 53 is closed as a bounded actor-state route, with no causal OBJ-2 edge.

## Next action

Continue with worker caller 54/62 `FUN_140658c50` and record its exact tag, payload and producer.
"""
    write(note, note_body)
    note_rel = note.relative_to(ROOT).as_posix()
    local_hashes = {relative: sha(ROOT / relative) for relative in EXPECTED}
    local_hashes[note_rel] = sha(note)
    evidence["items"].append({
        "captured_utc": metas[-1]["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0635",
        "kind": "native",
        "source": "Identity-checked GOG worker caller 53/tag-0x50 builder, Actor primary-vtable producer slot, dispatcher thunk and Actor/process handler call graph.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T202353Z.stdout.raw",
        "sha256": EXPECTED[".local/ghidra/gog-query-20261019T202353Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only captures, auto-analysis disabled, no import or overwrite. GOG RVAs are not transferred to Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": [
            "strict Python 3.12 dispatcher",
            "tools/ghidra_probe.py --rva call-edge/decompilation queries, Actor pointer-table query, and RTTI/address-context screens",
        ],
        "coverage": "Actor primary VTABLE::Actor RVA 0x189ec20 slot 0x89 (+0x448) is FUN_140664cf0, which emits tag 0x50 with the same object pointer retained by FUN_140658c10. Dispatcher case 0x50 invokes thunk FUN_140664d20 -> FUN_1402ec610. That target has 51 direct edges and 17 unresolved virtual sites, and returns without its main body when the receiver is PlayerCharacter or receiver flag bit 11 is set. The remaining body performs Actor/process and object-state work; no direct mapped HitData/protection/AV11/AV12/UseSkill edge is present.",
        "result": "Caller 53 is bounded as an Actor/process-state route for the captured direct path. The handler early-returns for verified PlayerCharacter receivers and has no direct mapped hit/protection/armor-skill sink. Seventeen dynamic virtual sites remain unresolved; no global no-hit, Steam, effective protection, armor-XP, or exploit conclusion follows. No causal OBJ-2 edge is added.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0400", "EV-0344"],
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(
        ROOT / "research/CLAIMS.md",
        "| CL-L448 |",
        "| CL-L448 | In GOG AE 1.6.1179.0, primary VTABLE::Actor slot 0x89 (+0x448) queues worker tag 0x50 with a retained object; case 0x50 calls FUN_1402ec610, whose body skips PlayerCharacter receivers and otherwise performs Actor/process state work. | supported for captured direct route | [EV-0400], [EV-0344], [EV-0635] | The target has 17 unresolved virtual sites; no global no-hit, Steam, protection, armor-XP, or exploit result follows. |",
    )
    append_once(
        ROOT / "research/MECHANISMS.md",
        "## M-0188 —",
        """## M-0188 — Actor slot-0x89 tag-0x50 process-state callback (EV-0635)

The primary Actor vtable's slot `0x89` (`+0x448`) is `FUN_140664cf0`; it excludes one global and Actor objects with flag bit 11, then queues tag `0x50` with the same object pointer [EV-0400], [EV-0635]. Case 0x50 dispatches through thunk `FUN_140664d20` to `FUN_1402ec610`. That handler returns when the receiver is PlayerCharacter or bit 11 is set; otherwise it performs Actor/process and object-state updates. Its direct census contains 51 edges and 17 unresolved virtual sites; no direct mapped HitData, protection, AV11/AV12 or UseSkill target appears [EV-0344], [EV-0635]. The bounded route adds no OBJ-2 causal edge; dynamic descendants remain open. Claim CL-L448.""",
    )
    append_once(
        ROOT / "research/CONTRADICTIONS.md",
        "## C-OBJ2-Q79-TAG50-ACTOR-STATE-VS-COMBAT",
        """## C-OBJ2-Q79-TAG50-ACTOR-STATE-VS-COMBAT — Actor state callback versus hit/armor route

- **Model A:** tag 0x50 is an ordinary player-hit/protection/armor-skill route.
- **Model B:** tag 0x50 is an Actor slot-0x89 process/object-state callback, whose target skips PlayerCharacter receivers.
- **Evidence:** Actor table identity and slot capture, tag builder/dispatcher, PlayerCharacter identity and target call graph [EV-0344], [EV-0400], [EV-0635].
- **Assessment:** B is supported for the captured direct path; A has no direct mapped sink. Seventeen dynamic virtual sites remain unresolved, so no global no-hit conclusion or bounty resolution follows.""",
    )
    append_once(
        ROOT / "research/KNOWLEDGE_GRAPH.md",
        "EV-0635 maps caller 53 tag-0x50 from Actor slot 0x89 to process state",
        """### EV-0635 maps caller 53 tag-0x50 from Actor slot 0x89 to process state

Primary `VTABLE::Actor` slot 0x89 (`+0x448`) emits tag 0x50 with a retained object pointer [EV-0400], [EV-0635]. The dispatcher passes that object through a thunk to `FUN_1402ec610`; its entry guard skips PlayerCharacter receivers, and its bounded direct body performs Actor/process and object-state work [EV-0344], [EV-0635]. **No causal edge is added** to HitData, protection, AV11/AV12, UseSkill or armor XP because no direct mapped sink is present and 17 dynamic virtual sites remain unresolved [CL-L448], [M-0188]. Continue caller 54/62 `FUN_140658c50`.""",
    )
    append_once(
        EXP / "results.md",
        "### Caller 53/62: Actor slot-0x89 tag-0x50 process-state route (EV-0635)",
        """### Caller 53/62: Actor slot-0x89 tag-0x50 process-state route (EV-0635)

`FUN_140658c10` queues tag `0x50` and retains the object. Its producer `FUN_140664cf0` is primary `VTABLE::Actor` slot 0x89 (`+0x448`); it filters one global and flag bit 11, then queues the object [EV-0400], [EV-0635]. Case 0x50 dispatches through thunk `FUN_140664d20` to `FUN_1402ec610` [EV-0635].

The handler's entry guard skips its body when receiver flag bit 11 is set or the receiver is verified PlayerCharacter [EV-0344], [EV-0635]. Its remaining direct code handles Actor/process and object-state updates, with 51 direct call edges and 17 unresolved virtual sites. No mapped HitData, protection, AV11/AV12 or UseSkill direct target appears in the bounded body. Caller 53 is closed as a bounded Actor-state path; dynamic descendants and Steam behavior remain open. No causal OBJ-2 edge is added. Continue caller 54/62 `FUN_140658c50`.""",
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    hypothesis_ids = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H147" in hypothesis_ids or "Q79-H148" in hypothesis_ids:
        raise SystemExit("caller-53 hypotheses already exist")
    item["hypotheses"].extend([
        {
            "id": "Q79-H147",
            "model": "Caller 53 tag 0x50 is emitted by primary Actor vtable slot 0x89 and routes a retained Actor pointer into FUN_1402ec610 for Actor/process state work; the handler skips PlayerCharacter receivers.",
            "predicted_discriminant": "The verified Actor vtable slot writes the tag/object payload, dispatcher target matches the object, and the target's entry guard excludes PlayerCharacter while its bounded direct body contains no mapped HitData/protection/AV11/AV12/UseSkill sink.",
            "status": "supported",
            "evidence": ["EV-0344", "EV-0400", "EV-0635"],
        },
        {
            "id": "Q79-H148",
            "model": "One of FUN_1402ec610's unresolved virtual descendants converts the tag-0x50 Actor/process state route into HitData, effective-protection or armor-skill work affecting the PlayerCharacter.",
            "predicted_discriminant": "Resolve producer-backed virtual recipients and show a concrete data/control edge into mapped HitData/protection/AV11/AV12/UseSkill code; the direct PlayerCharacter early-return and Actor state body alone do not support this model.",
            "status": "proposed",
            "evidence": ["EV-0344", "EV-0635"],
        },
    ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0635"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L448"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 53/tag-0x50 is bounded as an Actor slot-0x89 process-state route; continue caller 54.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": NEXT_ACTION, "active_process": "TX-20261018-0013"}
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 53 of 62 initially uninspected worker callers are reviewed, with 9 remaining."
    new_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 54 of 62 initially uninspected worker callers are reviewed, with 8 remaining."
    if state.count(old_count) != 1:
        raise SystemExit("STATE active caller count did not match exactly once")
    state = state.replace(old_count, new_count, 1)
    old_summary = "EV-0634 maps caller 52/tag 0x56 to a retained-object collection path with immediate/deferred slot +0x138 parity and deferred manager bookkeeping; its target remains unresolved, with no direct mapped HitData/armor sink."
    new_summary = old_summary + " EV-0635 maps caller 53/tag 0x50 from primary Actor slot +0x448 to an Actor/process handler that skips PlayerCharacter; 17 virtual sites remain unresolved, with no direct mapped HitData/armor sink."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE caller-52 summary did not match exactly once")
    state = state.replace(old_summary, new_summary, 1)
    old_next = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; review worker caller 53/62 `FUN_140658c10` for its exact tag/payload and immediate producer, then continue the bounded caller census. Caller 52's `+0x138` target remains unresolved; no direct HitData/armor edge is established."
    new_next = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c50 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; review worker caller 54/62 `FUN_140658c50` for its exact tag/payload and producer, then continue the bounded caller census. Caller 53's Actor handler has 17 unresolved virtual sites and no direct mapped HitData/armor sink."
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line did not match exactly")
    state = state.replace(old_next, new_next, 1)
    state = state.replace("Q-0079 has 53/62 initially uninspected worker callers reviewed; 9 remain.", "Q-0079 has 54/62 initially uninspected worker callers reviewed; 8 remain.", 1)
    write(state_path, state)

    print("Registered EV-0635/CL-L448/M-0188, linked caller 53 to Actor slot 0x89, and checkpointed caller 54.")


if __name__ == "__main__":
    main()
