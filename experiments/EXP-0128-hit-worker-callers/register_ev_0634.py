#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
CAPTURES = [
    ".local/ghidra/gog-query-20261019T201356Z",
    ".local/ghidra/gog-query-20261019T201510Z",
    ".local/ghidra/gog-query-20261019T201637Z",
    ".local/ghidra/gog-query-20261019T201753Z",
    ".local/ghidra/gog-query-20261019T201913Z",
]
EXPECTED = {
    ".local/ghidra/gog-query-20261019T201356Z.stdout.raw": "a909a8f4e68bdc85634755d7543d945a1eeedd9de10cbdf09bd99733ce49d4a3",
    ".local/ghidra/gog-query-20261019T201356Z.meta.json": "6fb119566dd8ef3d7f466e3b5eab6e592a16bc5a54de53388e73e37764deb9e6",
    ".local/ghidra/gog-query-20261019T201510Z.stdout.raw": "f629e4da674675574a2d813f4657b8fc20d75233526023884b65ec8f52af38de",
    ".local/ghidra/gog-query-20261019T201510Z.meta.json": "c0ccc67c95573ab65d45216b2a67521d4dc749ef2a2025e7fa7f26f4293aad00",
    ".local/ghidra/gog-query-20261019T201637Z.stdout.raw": "99f5145cb30f02c8cd11a928701cb18d647b4482f8d3dbace0a03e8e7b58a4f9",
    ".local/ghidra/gog-query-20261019T201637Z.meta.json": "b6954adeeeca9253005c7a4eff6d43c3e4826d385853bd1463ec1901c4b2c078",
    ".local/ghidra/gog-query-20261019T201753Z.stdout.raw": "5857e12b46bb8e9d7d0a81284fc67fe1ac3a00f8c36e73d4f7a140722316add0",
    ".local/ghidra/gog-query-20261019T201753Z.meta.json": "fcb12e2001f014fc4dfa4dbe85e462caadf9c19c10fd598a80069df8cd5d43f8",
    ".local/ghidra/gog-query-20261019T201913Z.stdout.raw": "1a8e222709ba7379892ea57ec2b6aa59c7fbcc1a2daba8596db458d1014d0d99",
    ".local/ghidra/gog-query-20261019T201913Z.meta.json": "a74c22f0fdfeb903fa0442d0db00fdd86c9ee9ab2b6c058b4a51385e5300312a",
}
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c10 "
    "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
    "review worker caller 53/62 FUN_140658c10 for its exact tag/payload and immediate producer, "
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
    builder, dispatcher, producer, registry, owner = raws
    for token in ["local_88[0] = 0x56;", "FUN_14065b800(param_1,local_88);", "OUTGOING_DIRECT_CALL_EDGE_COUNT=1", "INCOMING_CALLER_FUNCTION_COUNT=1"]:
        if token not in builder:
            raise SystemExit("caller-52 builder proof missing: " + token)
    for token in [
        "case 0x56:",
        "FUN_140777f40(DAT_1420f7db0,plVar14);",
        "(**(code **)(*plVar14 + 0x138))(plVar14);",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=198",
        "INDIRECT_CALL_SITE_COUNT=81",
    ]:
        if token not in dispatcher:
            raise SystemExit("tag-0x56 dispatcher proof missing: " + token)
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=2",
        "INDIRECT_CALL_SITE_COUNT=1",
        "FUN_140658be0(DAT_14319a7c0,param_1);",
        "(**(code **)(*param_1 + 0x138))(param_1);",
        "INCOMING_CALLER_FUNCTION_COUNT=1",
        "FUN_140774b80",
    ]:
        if token not in producer:
            raise SystemExit("caller-52 producer proof missing: " + token)
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=12",
        "INDIRECT_CALL_SITE_COUNT=2",
        "iVar2 = (**(code **)(*param_2 + 0x160))(param_2);",
        "cVar1 = (**(code **)(*param_2 + 0x180))(param_2);",
        "param_1 + 0x108",
        "param_1 + 0x128",
        "param_1 + 0xe8",
        "XREF_CALL_EDGE=14065b214 -> 140777f40",
    ]:
        if token not in registry:
            raise SystemExit("caller-52 registry helper proof missing: " + token)
    for token in [
        "FUN_140774b80(DAT_1420f7db0);",
        "XREF_CALL_EDGE=140644046 -> 140774b80",
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=12",
        "INDIRECT_CALL_SITE_COUNT=2",
        "puVar12 = (undefined8 *)*plVar3;",
        "FUN_140778a20(*puVar12)",
    ]:
        if token not in owner:
            raise SystemExit("caller-52 collection-owner proof missing: " + token)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    by_id = {row.get("id") for row in evidence.get("items", [])}
    if "EV-0634" in by_id:
        raise SystemExit("EV-0634 already exists")

    note = EXP / "EV-0634-caller52-tag56-object-list-lifecycle.md"
    note_body = """# EV-0634 — Caller 52 tag-0x56 retained-object/list route

## Competing models and discriminants

- H1: tag `0x56` is an ordinary incoming-hit or armor-skill path. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill target in the resolved recipient or its callback descendants.
- H2: tag `0x56` handles retained objects in a manager collection/lifecycle route. It predicts an object pointer payload, immediate/deferred calls to one object callback, and collection membership/refcount work under a manager context.

The discriminants are the builder/producer field agreement, dispatcher case, exact immediate/deferred virtual slot, direct/indirect call censuses for producer and manager helpers, and the only analyzed direct caller of the collection owner.

## Direct GOG evidence

The five captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled and did not import or overwrite the project. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- Builder `FUN_140658be0` writes tag `0x56`, increments the retained object's reference count, and calls `FUN_14065b800`; its sole analyzed direct producer is `FUN_140778a20` [EV-0634].
- `FUN_140778a20` tests shared gate `FUN_1406d4110`. If queued, it submits the object through tag `0x56`; otherwise it invokes the object's virtual slot `+0x138` with the object as receiver and no explicit argument. Its body has two direct call edges, one unresolved virtual site, two callsites from one direct caller, and no other analyzed direct callers [EV-0634].
- Dispatcher case `0x56` reads the same retained object from the event payload, calls `FUN_140777f40(DAT_1420f7db0, object)`, then invokes that object's slot `+0x138`, again without an explicit argument. The deferred path therefore matches the producer's receiver/slot call, with an extra manager helper first [EV-0634]. The full dispatcher has many unrelated cases and 81 indirect sites; those counts are not attributed to case `0x56`.
- The wrapper's only analyzed direct caller function is `FUN_140774b80`, which walks a pointer collection at receiver `+0xe8`, calls the wrapper on each element, decrements object references, and clears the collection. `FUN_140774b80` itself is directly called by `FUN_140643ec0` with `DAT_1420f7db0` during a broad cleanup sequence [EV-0634]. This supports a lifecycle/collection interpretation for the captured producer source; treating the outer routine as shutdown remains an inference.
- `FUN_140777f40` has 12 direct edges, two unresolved virtual sites, and two analyzed caller functions. It checks object slots `+0x160` and `+0x180`, then uses locked manager collections at `+0x108`, `+0x128`, or `+0xe8` with keyed lookup/removal and an additional manager update. This is collection-membership/state work; object class and dynamic callback targets remain unknown [EV-0634].
- No mapped HitData/protection/AV11/AV12/UseSkill target appears in the captured tag-specific producer, wrapper, or manager helper direct edges. The object's slot `+0x138` is unresolved, so the result is bounded and cannot exclude a dynamic descendant.

## Result and limits

H2 is supported for the captured direct route. H1 has no direct support in the producer/manager path, but the recipient's `+0x138` virtual target and deeper callbacks remain unresolved. The evidence establishes immediate/deferred receiver-slot parity, not the callback's terminal behavior, effective protection, armor XP, Steam behavior, or a vanilla exploit. Caller 52 is reviewed as a bounded object-list/lifecycle path; Q-0079 remains open.

## Next action

Continue with worker caller 53/62 `FUN_140658c10` and record its exact tag, payload and producer.
"""
    write(note, note_body)
    note_rel = note.relative_to(ROOT).as_posix()
    local_hashes = {relative: sha(ROOT / relative) for relative in EXPECTED}
    local_hashes[note_rel] = sha(note)
    evidence["items"].append({
        "captured_utc": metas[-1]["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0634",
        "kind": "native",
        "source": "Identity-checked GOG caller 52/tag-0x56 builder, dispatcher case, producer, manager helper and collection owner.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T201356Z.stdout.raw",
        "sha256": EXPECTED[".local/ghidra/gog-query-20261019T201356Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only captures, auto-analysis disabled, no import or overwrite. GOG RVAs are not transferred to Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge, disassembly and decompilation queries"],
        "coverage": "Caller 52 builder FUN_140658be0 writes tag 0x56 and retains an object; producer FUN_140778a20 chooses queued dispatch or immediate object slot +0x138. Dispatcher case 0x56 applies FUN_140777f40 to the same object before calling the same virtual slot. The producer's sole analyzed direct caller is collection owner FUN_140774b80, called by FUN_140643ec0 during a broad cleanup sequence. FUN_140777f40 performs keyed manager-list membership/state work. The virtual target and object RTTI remain unresolved.",
        "result": "Caller 52 is bounded as a retained-object/list lifecycle route for the captured direct path, with immediate/deferred slot +0x138 parity and an extra deferred manager update. No direct mapped HitData/protection/AV11/AV12/UseSkill sink appears in the captured tag-specific bodies; the unresolved virtual recipient prevents a global no-hit or armor-XP conclusion. No causal OBJ-2 edge is added.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0632", "EV-0633"],
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(
        ROOT / "research/CLAIMS.md",
        "| CL-L447 |",
        "| CL-L447 | In GOG AE 1.6.1179.0, caller 52/tag 0x56 retains an object and routes it through a gate to immediate or deferred virtual slot +0x138; deferred dispatch first calls a manager collection helper. Its sole analyzed producer source is an array walk/refcount cleanup path, and the captured manager helper performs keyed collection state updates. | supported for captured direct route | [EV-0634] | The object's RTTI, slot +0x138 target, dynamic descendants, Steam behavior, protection and armor XP remain unresolved; no causal OBJ-2 edge is established. |",
    )
    append_once(
        ROOT / "research/MECHANISMS.md",
        "## M-0187 —",
        """## M-0187 — Caller 52 tag-0x56 retained-object collection callback (EV-0634)

`FUN_140658be0` queues tag `0x56` with a retained object. Its producer `FUN_140778a20` tests shared gate `FUN_1406d4110` and either queues the object or calls its virtual `+0x138` slot. Dispatcher case `0x56` calls `FUN_140777f40(DAT_1420f7db0, object)` before invoking the same receiver slot without explicit arguments [EV-0634]. The producer's sole analyzed caller, `FUN_140774b80`, walks a manager collection at `+0xe8`, calls the wrapper for each member, decrements references and clears the collection; this owner is itself called by `FUN_140643ec0` in a broad cleanup sequence. The extra manager helper performs keyed membership/state work across multiple collections. Receiver RTTI and virtual descendants remain unresolved; no direct HitData/protection/AV11/AV12/UseSkill edge appears in the captured tag-specific route. Claim CL-L447; no causal armor-XP edge is established.""",
    )
    append_once(
        ROOT / "research/CONTRADICTIONS.md",
        "## C-OBJ2-Q79-TAG56-LIFECYCLE-VS-COMBAT",
        """## C-OBJ2-Q79-TAG56-LIFECYCLE-VS-COMBAT — collection callback versus hidden hit route

- **Model A:** tag 0x56 enters HitData, protection or armor-skill processing through its virtual +0x138 target.
- **Model B:** tag 0x56 is a retained-object callback in a manager collection/lifecycle path.
- **Evidence:** builder, producer/dispatcher slot parity, keyed manager helper and sole collection-owner caller [EV-0634].
- **Assessment:** B is supported for the captured direct source and helper route; A has no direct mapped sink. The +0x138 target and dynamic callback descendants remain unresolved, so this is not a global no-hit result and does not resolve OBJ-2.""",
    )
    append_once(
        ROOT / "research/KNOWLEDGE_GRAPH.md",
        "EV-0634 maps caller 52 tag-0x56 to retained-object collection callbacks",
        """### EV-0634 maps caller 52 tag-0x56 to retained-object collection callbacks

Caller 52 queues tag 0x56 with a retained object. The sole analyzed producer wrapper tests the shared queue gate, then either enqueues the object or invokes slot +0x138 directly. Deferred case 0x56 performs keyed manager collection work before invoking the same object slot. Its only analyzed producer source is an array walk/refcount cleanup path under `FUN_140643ec0` [EV-0634]. This supports a bounded lifecycle/object-list mechanism. **No causal edge is added** to HitData, effective armor protection, AV11/AV12, UseSkill or armor XP because the target slot is unresolved and the captured direct route contains no mapped sink [CL-L447], [M-0187]. Continue caller 53/62 `FUN_140658c10`.""",
    )
    append_once(
        EXP / "results.md",
        "### Caller 52/62: tag-0x56 retained-object collection route (EV-0634)",
        """### Caller 52/62: tag-0x56 retained-object collection route (EV-0634)

`FUN_140658be0` stores tag `0x56` and a retained object. Its only analyzed direct producer, `FUN_140778a20`, tests `FUN_1406d4110`: the queued branch calls the builder, while the clear-gate branch invokes receiver slot `+0x138` immediately. Dispatcher case 0x56 calls `FUN_140777f40(DAT_1420f7db0, object)` and then the same slot on the same receiver [EV-0634]. Thus the deferred route has one additional manager action but matches the immediate virtual call's receiver/slot and has no explicit arguments.

The producer wrapper is called twice by `FUN_140774b80`, which walks pointer collection `+0xe8`, invokes the wrapper for each member, decrements references and clears the collection. Its only analyzed caller is `FUN_140643ec0`, a broad cleanup sequence. The manager helper branches on object virtual slots `+0x160`/`+0x180` and searches or updates keyed collections at `+0x108`, `+0x128`, or `+0xe8`. Treat the outer cleanup interpretation as inference; the exact RTTI and `+0x138` target remain unknown [EV-0634].

No mapped HitData/protection/AV11/AV12/UseSkill target occurs in the captured tag-specific direct path. The unresolved virtual target keeps this bounded; no global negative, armor-XP bypass, or Steam behavior follows. Continue caller 53/62 `FUN_140658c10`.""",
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    hypothesis_ids = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H145" in hypothesis_ids or "Q79-H146" in hypothesis_ids:
        raise SystemExit("caller-52 hypotheses already exist")
    item["hypotheses"].extend([
        {
            "id": "Q79-H145",
            "model": "Caller 52 tag 0x56 is a retained-object lifecycle/list callback: producer and dispatcher converge on receiver slot +0x138, with deferred manager collection bookkeeping, and its sole producer source is collection cleanup.",
            "predicted_discriminant": "Builder payload, producer/dispatcher receiver-slot parity, manager keyed-list helper, and sole producer-source context show lifecycle/object-list behavior in the captured direct route; the dynamic slot target remains explicit.",
            "status": "supported",
            "evidence": ["EV-0634"],
        },
        {
            "id": "Q79-H146",
            "model": "Caller 52 tag 0x56's unresolved virtual +0x138 callback or descendants reach HitData, effective protection, AV11/AV12 or UseSkill processing.",
            "predicted_discriminant": "Resolve the producer-backed receiver RTTI/vtable and callback descendants and show a concrete data/control edge to mapped HitData, protection, AV11/AV12 or UseSkill targets; collection cleanup context alone does not decide this.",
            "status": "proposed",
            "evidence": ["EV-0634"],
        },
    ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0634"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L447"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 52/tag-0x56 is bounded as a retained-object collection callback; continue caller 53.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": NEXT_ACTION, "active_process": "TX-20261018-0013"}
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 52 of 62 initially uninspected worker callers are reviewed, with 10 remaining."
    new_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 53 of 62 initially uninspected worker callers are reviewed, with 9 remaining."
    if state.count(old_count) != 1:
        raise SystemExit("STATE active caller count did not match exactly once")
    state = state.replace(old_count, new_count, 1)
    old_summary = "Caller 50 is bounded with no direct HitData/armor edge. EV-0632 maps caller 51/tag 0x4b to a PlayerCharacter +0xc8-gated paired-object flag transition and nested keyed-object updates; no direct HitData/protection/AV11/AV12/UseSkill sink appears. Ten producer virtual sites and callback effects remain open."
    new_summary = "Caller 50 is bounded with no direct HitData/armor edge. EV-0632 maps caller 51/tag 0x4b to a PlayerCharacter +0xc8-gated paired-object flag transition and nested keyed-object updates; no direct HitData/protection/AV11/AV12/UseSkill sink appears. Ten producer virtual sites and callback effects remain open. EV-0634 maps caller 52/tag 0x56 to a retained-object collection path with immediate/deferred slot +0x138 parity and deferred manager bookkeeping; its target remains unresolved, with no direct mapped HitData/armor sink."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE caller-50/51 summary did not match exactly once")
    state = state.replace(old_summary, new_summary, 1)
    old_next = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658be0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; review worker caller 52/62 `FUN_140658be0` for its exact tag/payload and immediate producer, then continue the bounded caller census. Callers 50/51 use the shared tuple through distinct direct mechanisms, with scalar semantics unresolved and no HitData/armor edge established."
    new_next = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; review worker caller 53/62 `FUN_140658c10` for its exact tag/payload and immediate producer, then continue the bounded caller census. Caller 52's `+0x138` target remains unresolved; no direct HitData/armor edge is established."
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line did not match exactly")
    state = state.replace(old_next, new_next, 1)
    state = state.replace("Q-0079 has 50/62 exact worker callers reviewed; 12 remain.", "Q-0079 has 53/62 initially uninspected worker callers reviewed; 9 remain.", 1)
    write(state_path, state)

    print("Registered EV-0634/CL-L447/M-0187, added bounded caller-52 hypotheses, and checkpointed caller 53.")


if __name__ == "__main__":
    main()
