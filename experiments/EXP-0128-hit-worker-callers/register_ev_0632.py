#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
CAPTURES = [
    ".local/ghidra/gog-query-20261019T195644Z",
    ".local/ghidra/gog-query-20261019T195821Z",
    ".local/ghidra/gog-query-20261019T200118Z",
    ".local/ghidra/gog-query-20261019T200257Z",
]
EXPECTED = {
    ".local/ghidra/gog-query-20261019T195644Z.stdout.raw": "62d628a8e008cff7d30127e133fa8aa48f9ba4292321e8225f3c6a9f9551df90",
    ".local/ghidra/gog-query-20261019T195644Z.meta.json": "026e2bb920dbe0f4973a54b5b220313be14ab096443b19ec1e46398513c3c2a7",
    ".local/ghidra/gog-query-20261019T195821Z.stdout.raw": "25125f0ef0ed62edff91e85156fe1f358347c8df1b50c2f777f99855133b8b38",
    ".local/ghidra/gog-query-20261019T195821Z.meta.json": "145ff262e3024f0ebf1016968b8ed43181a6c4b6e87c1acc4025e34572a7e61f",
    ".local/ghidra/gog-query-20261019T200118Z.stdout.raw": "029f55fa2a584c2fd985d48199be6f8e6a2f56b729a765c4ed1a26a91c065bff",
    ".local/ghidra/gog-query-20261019T200118Z.meta.json": "623d84d96d0358ee4e7c9ae61d87ce7f2f44e7eeca3561fe68cbbb950a676ed0",
    ".local/ghidra/gog-query-20261019T200257Z.stdout.raw": "44d6d6c7a1e39b55630d2cf422d99bb4dff0d06d57ed84afe007eb552aa75db5",
    ".local/ghidra/gog-query-20261019T200257Z.meta.json": "3cb0f62fcbbeaa914ceb660881c274bbbcd46825a686740ee1bc40800572a1b4",
}
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xcb4ae0 "
    "--list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600; "
    "test whether the DAT_1432740d8 input in caller 51 FUN_140cb41c0 and caller 50 "
    "FUN_1402c6810 reaches a common registration/configuration/update mechanism or reflects "
    "caller-specific value use; preserve the no-HitData/armor-edge boundary."
)


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p: Path, s: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(p: Path, marker: str, body: str) -> None:
    old = p.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit(f"duplicate marker: {marker}")
    write(p, old.rstrip() + "\n\n" + body.strip())


def main() -> None:
    for rel, expected in EXPECTED.items():
        p = ROOT / rel
        if not p.exists() or sha(p) != expected:
            raise SystemExit(f"capture missing or hash mismatch: {rel}")
    metas = []
    for base in CAPTURES:
        meta_path = ROOT / f"{base}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not (meta.get("ok") and meta.get("read_only") and meta.get("auto_analysis_disabled")):
            raise SystemExit("a Ghidra capture failed read-only or analysis-disabled verification")
        if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f":
            raise SystemExit("a Ghidra capture does not match the verified GOG binary")
        metas.append(meta)

    builder = (ROOT / f"{CAPTURES[0]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    producer = (ROOT / f"{CAPTURES[1]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    slot = (ROOT / f"{CAPTURES[2]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    helper = (ROOT / f"{CAPTURES[3]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    for token in ["local_88[0] = 0x4b;", "local_80 = param_2;", "local_88[0] = 0x4b;"]:
        if token not in builder:
            raise SystemExit("caller-51 tag/byte builder proof missing")
    for token in [
        "FUN_140658b50(DAT_14319a7c0,param_2);",
        "plVar6 = (longlong *)(**(code **)(*param_1 + 0x378))(param_1,1);",
        "plVar7 = (longlong *)(**(code **)(*param_1 + 0x378))(param_1,0);",
        "bVar5 = *(byte *)((longlong)plVar6 + 0xf4) & 1;",
        "bVar9 = *(byte *)((longlong)plVar7 + 0xf4) & 1;",
        "*(byte *)((longlong)param_1 + 0xbe3) = bVar5 & 0xfe | param_2 ^ 1;",
        "FUN_140cb41c0(uVar15,plVar10,plVar11);",
        "FUN_140744180(param_1);",
        "FUN_140661f60(param_1,uVar15);",
    ]:
        if token not in producer:
            raise SystemExit("caller-51 producer proof missing: " + token)
    if "OUTGOING_DIRECT_CALL_EDGE_COUNT=12" not in producer or "INDIRECT_CALL_SITE_COUNT=10" not in producer or "INCOMING_CALLER_FUNCTION_COUNT=13" not in producer:
        raise SystemExit("caller-51 call census completeness missing")
    if "VTABLE_RTTI_TYPE_NAME=.?AVPlayerCharacter@@" not in slot or "VTABLE_SLOT_INDEX=0x99" not in slot or "VTABLE_SLOT_TARGET_RVA=0x677100" not in slot:
        raise SystemExit("PlayerCharacter slot +0x4c8 mapping proof missing")
    if "*(uint *)(param_1 + 200)" not in slot or "0x1e00000" not in slot:
        raise SystemExit("PlayerCharacter +0xc8 state-bit predicate proof missing")
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=4",
        "INDIRECT_CALL_SITE_COUNT=2",
        "FUN_1401b5250(DAT_1420f7720",
        "FUN_140e2bd10(DAT_143285f88",
        "FUN_1402df6d0(lVar4)",
    ]:
        if token not in helper:
            raise SystemExit("recursive helper proof missing: " + token)

    ep = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(ep.read_text(encoding="utf-8"))
    by_id = {r.get("id") for r in evidence.get("items", [])}
    if "EV-0632" in by_id:
        raise SystemExit("EV-0632 already exists")
    for required in ["EV-0344", "EV-0337", "EV-0626", "EV-0631"]:
        if required not in by_id:
            raise SystemExit("missing contextual evidence: " + required)

    note = EXP / "EV-0632-caller51-tag4b-player-state-route.md"
    body = """# EV-0632 — Caller 51 tag-0x4b PlayerCharacter state route

## Competing models and discriminants

- H1: tag `0x4b` reaches a PlayerCharacter state transition and object-hierarchy update. It predicts a PlayerCharacter receiver, state-field predicates/writes, and bounded direct callees that are not the HitData/AV11/AV12/UseSkill sinks.
- H2: the same event is a hidden ordinary-hit or armor-skill route. It predicts a mapped HitData/protection/skill sink in the exact direct path, or a producer-backed dynamic call target that feeds one of those sinks.

The discriminants are caller/builder payload agreement, dispatcher receiver identity, RTTI-verified PlayerCharacter virtual slot targets, and complete direct/indirect call-site counts on the producer and its shared state helper.

## Direct GOG evidence

The four captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project with verified binary SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; queries were read-only, auto-analysis disabled, and performed no import or overwrite. GOG RVAs are not transferred to the separately verified Steam AE 1.6.1170.0 executable.

- Builder `FUN_140658b50` writes tag `0x4b` and one byte argument; its sole analyzed worker caller is `FUN_140738380` [EV-0632]. The worker dispatcher case `0x4b` calls `FUN_140738380(DAT_143188918, payload_byte)` [EV-0632]. The global is constructed with PlayerCharacter vftable, and PlayerCharacter slot `+0x378` returns `FUN_1407371f0` [EV-0344], [EV-0337].
- `FUN_140738380` returns through the event builder when shared gate `FUN_1406d4110` is set. Its clear-gate path obtains two objects from PlayerCharacter virtual slot `+0x378` with selectors 1 and 0; when the byte parameter is nonzero, PlayerCharacter slot `+0x4c8` gates the transition. It compares and changes bit 0 in both objects' `+0xf4` dwords and updates PlayerCharacter byte `+0xbe3`. It then builds paired state records, calls `FUN_140cb41c0`, iterates four pointers at PlayerCharacter `+0x1a8` through `FUN_1405b4900`, and reaches `FUN_140744180`, `FUN_140661f60` and a conditional `FUN_14074dd30` [EV-0632].
- The complete producer body has 12 direct edges and 10 unresolved virtual call sites; the complete incoming census reports 13 caller functions, including the worker dispatcher [EV-0632].
- RTTI-validated primary PlayerCharacter table RVA `0x18acd70`, slot `0x99` (`+0x4c8`), resolves to `FUN_140677100`. Its complete body checks `PlayerCharacter+0xc8 & 0x1e00000` against a small state-value set that depends on the byte argument, and has no direct calls or HitData/ActorValue/UseSkill sink [EV-0632].
- Recursive helper `FUN_1402df6d0` has three direct callees, two unresolved virtual sites and one recursive direct edge. Its bounded body walks a nested object collection, searches for a marker object, consults a keyed record bit at `+0x7a`, and on a match updates the selected object and calls `FUN_140e2bd10`; it has no direct HitData/protection/AV11/AV12/UseSkill edge [EV-0632]. The helper has multiple callers, so this is generic object-state infrastructure, not a tag-specific combat result.
- A cross-caller configuration lead remains: caller 50's fallback factory and caller 51's `FUN_140cb41c0` path both pass the same adjacent global tuple `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]. Its schema and relationship are unresolved; this observation adds no causal edge to armor or HitData.

## Result and limits

H1 is supported for the captured bounded static route. H2 has no direct support in this route and is narrowed: no direct mapped combat, HitData, protection, AV11/AV12 or UseSkill sink appears. Caller 51 is bounded for the worker-caller census, with dynamic virtual targets and deeper callback effects explicitly open. The result does not establish a global no-hit result, Steam behavior, effective armor protection, armor XP, or a vanilla exploit.

## Next discriminant

Query `FUN_140cb4ae0`, which receives the shared `DAT_1432740d8` tuple through `FUN_140cb41c0`. Compare that helper with caller 50's `FUN_1402c6810` route to determine whether the tuple participates in a shared keyed registration/update primitive or is only common static configuration. Preserve each caller's receiver and event context; do not infer a combat link from the tuple alone. Then resume worker caller 52/62.
"""
    write(note, body)

    local_hashes = {rel: sha(ROOT / rel) for rel in EXPECTED}
    note_rel = note.relative_to(ROOT).as_posix()
    local_hashes[note_rel] = sha(note)
    evidence["items"].append({
        "captured_utc": metas[0]["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0632",
        "kind": "native",
        "source": "Identity-checked GOG worker caller 51/tag-0x4b builder, producer and call graph; RTTI-validated PlayerCharacter slot +0x4c8; recursive state helper direct-call screen.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T195821Z.stdout.raw",
        "sha256": sha(ROOT / f"{CAPTURES[1]}.stdout.raw"),
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only captures, auto-analysis disabled, no import or overwrite. GOG RVAs are not transferred to Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge, disassembly, decompilation and PlayerCharacter vtable-slot queries"],
        "coverage": "Caller 51 worker builder FUN_140658b50 writes tag 0x4b and a byte. Producer FUN_140738380 dispatches the PlayerCharacter global, changes selected object +0xf4 flag bits and PlayerCharacter +0xbe3, uses RTTI-confirmed PlayerCharacter vtable slot +0x4c8 to gate on field +0xc8, and calls state/resource helpers. Its direct census has 12 direct edges, 10 unresolved virtual sites and 13 incoming caller functions. Recursive helper FUN_1402df6d0 has three direct edges, two virtual sites and a recursive call; its bounded body selects and updates keyed nested-object state. No direct HitData/protection/AV11/AV12/UseSkill sink appears in these captured bodies.",
        "result": "Caller 51 is bounded as a PlayerCharacter/object-state worker route in the captured GOG build. The direct evidence supports state gating and nested-object updates; it does not establish ordinary-hit or armor-XP behavior. Dynamic callbacks and transitive runtime behavior remain open. The adjacent global tuple DAT_1432740d8..+8 is also passed by caller 50's fallback factory and caller 51's callback path, creating a cross-caller configuration/registration lead but no causal armor edge.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0337", "EV-0344", "EV-0626", "EV-0631"]
    })
    write(ep, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    claim = "| CL-L445 | In GOG AE 1.6.1179.0, caller 51 builds worker tag 0x4b with one byte and dispatches to FUN_140738380 on the PlayerCharacter singleton; the bounded direct route updates object +0xf4 flag bits and PlayerCharacter +0xbe3 under a PlayerCharacter +0xc8 state gate, then enters keyed nested-object state helpers. | supported for captured static route | [EV-0632], [EV-0337], [EV-0344] | Ten producer virtual sites and deeper callbacks remain unresolved; no global no-hit, protection, AV11/AV12, UseSkill or Steam claim follows. |"
    append_once(claims, "| CL-L445 |", claim)

    mechanisms = ROOT / "research/MECHANISMS.md"
    mech = """## M-0185 — Caller 51 tag-0x4b PlayerCharacter state update (EV-0632)

`FUN_140658b50` queues a tag-0x4b byte event; case 0x4b calls `FUN_140738380` with the PlayerCharacter global [EV-0632], whose constructor and primary vtable were independently verified [EV-0344]. The producer's clear-gate path gets two objects through PlayerCharacter slot `+0x378`, tests a conditional primary slot `+0x4c8` predicate over PlayerCharacter `+0xc8`, toggles bit 0 at both selected objects `+0xf4`, and updates PlayerCharacter byte `+0xbe3`. It later runs paired-record and nested-object callbacks, including recursive `FUN_1402df6d0`. The bounded direct bodies contain no mapped HitData, protection, AV11/AV12 or UseSkill sink. Ten producer virtual sites and deeper dynamic callbacks remain open; do not generalize the bounded result into a global no-hit claim. Caller 50 and 51 also pass the same adjacent data tuple `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]; this is a configuration/registration lead only. Claim CL-L445; no OBJ-2 causal edge is established."""
    append_once(mechanisms, "## M-0185 —", mech)

    contradictions = ROOT / "research/CONTRADICTIONS.md"
    append_once(
        contradictions,
        "## C-OBJ2-Q79-TAG4B-PLAYERSTATE",
        """## C-OBJ2-Q79-TAG4B-PLAYERSTATE — player state transition versus hidden hit route

- **Model A:** tag 0x4b is a hidden incoming-hit/armor-skill route. It predicts a producer-backed HitData/protection/AV11/AV12/UseSkill edge in the exact route or resolved virtual descendants.
- **Model B:** tag 0x4b is a PlayerCharacter/object-state transition. It predicts PlayerCharacter receiver identity, state-bit gating, object flag writes and state callbacks without a mapped direct hit/skill sink.
- **Evidence:** caller 51 builder/producer and call graph; PlayerCharacter global identity and `+0x4c8` RTTI slot; bounded recursive keyed-object helper [EV-0337], [EV-0344], [EV-0632].
- **Assessment:** B is supported for the captured direct static route; A has no direct support. Ten producer virtual sites and deeper callbacks remain unresolved, so this is not a global no-hit result and does not resolve OBJ-2.
- **Cross-caller lead:** both caller 50 fallback construction and caller 51 state callback pass `DAT_1432740d8..+8` to different helpers [EV-0626], [EV-0632]. Trace `FUN_140cb4ae0` and compare the actual helper contracts before adding any shared-mechanism or HitData edge."""
    )

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    append_once(
        graph,
        "EV-0632 maps caller 51 tag-0x4b to PlayerCharacter state updates",
        """### EV-0632 maps caller 51 tag-0x4b to PlayerCharacter state updates

Caller 51 builds tag 0x4b with a byte; dispatcher case 0x4b passes that byte and verified PlayerCharacter global `DAT_143188918` to `FUN_140738380` [EV-0632], [EV-0344]. The bounded route updates paired object `+0xf4` flags and PlayerCharacter `+0xbe3` behind primary slot `+0x4c8` state checks at `+0xc8`, then uses nested keyed-object callbacks. The recursive helper has no direct HitData/protection/AV11/AV12/UseSkill edge; ten producer virtual sites remain unresolved. This is a bounded state edge, with no causal OBJ-2 edge [CL-L445], [M-0185].

Cross-caller synthesis: caller 50 fallback construction and caller 51 callback setup both reference the same adjacent tuple `DAT_1432740d8..+8`, but pass it to different helpers [EV-0626], [EV-0632]. Treat this as a shared-configuration lead only; exact schema/common mechanism is unproved. Next trace `FUN_140cb4ae0`."""
    )

    results = EXP / "results.md"
    append_once(
        results,
        "### Caller 51/62: tag-0x4b PlayerCharacter state route (EV-0632)",
        """### Caller 51/62: tag-0x4b PlayerCharacter state route (EV-0632)

`FUN_140658b50` builds tag `0x4b` with a byte from its sole producer `FUN_140738380`. In the queued branch the shared thread gate sends that byte; dispatcher case `0x4b` invokes `FUN_140738380(DAT_143188918, byte)`. The global is a verified PlayerCharacter object [EV-0344].

The producer's clear-gate path selects two objects through PlayerCharacter slot `+0x378` with selectors 1 and 0. For a nonzero byte it checks primary PlayerCharacter slot `+0x4c8` (`FUN_140677100`): RTTI identifies the vtable as `.?AVPlayerCharacter@@`, and the method tests masked field `+0xc8`. It compares and changes bit 0 at the selected objects' `+0xf4`, changes PlayerCharacter byte `+0xbe3`, builds paired state records, iterates four objects at PlayerCharacter `+0x1a8`, and calls resource/hierarchy helpers including `FUN_140661f60` [EV-0632].

The exact producer body has 12 direct call edges and 10 dynamic virtual sites; 13 direct caller functions are recorded. Recursive helper `FUN_1402df6d0` has three direct callees, two virtual sites and a recursive edge. It traverses nested keyed objects, checks a record bit and updates object state through `FUN_140e2bd10`. Neither bounded direct body has a mapped HitData/protection/AV11/AV12/UseSkill sink [EV-0632].

Cross-caller synthesis: caller 50 and caller 51 both pass `DAT_1432740d8..+8` to distinct helpers, respectively `FUN_1402c6810` and `FUN_140cb4ae0` [EV-0626], [EV-0632]. The tuple schema and shared-helper relationship are open; this adds no HitData or armor edge. Caller 51 is bounded for the worker census, with dynamic callbacks unresolved. Next query `FUN_140cb4ae0`, then continue caller 52/62 `FUN_140658be0`."""
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(r for r in frontier["items"] if r.get("id") == "Q-0079")
    ids = {h.get("id") for h in item.get("hypotheses", [])}
    if "Q79-H142" in ids or "Q79-H143" in ids:
        raise SystemExit("caller-51 hypotheses already exist")
    item["hypotheses"].extend([
        {
            "id": "Q79-H142",
            "model": "The tag-0x4b worker route reaches PlayerCharacter and performs a gated object-state transition through paired +0xf4 flag writes, PlayerCharacter +0xbe3, and nested keyed-object updates; its bounded direct path is separate from the mapped HitData/armor-skill sinks.",
            "predicted_discriminant": "RTTI-confirmed PlayerCharacter receiver and +0x4c8 state predicate, exact object/handler field writes, and a complete direct-helper screen show state/object updates without a mapped HitData/protection/AV11/AV12/UseSkill edge. Dynamic virtual descendants remain explicit.",
            "status": "supported",
            "evidence": ["EV-0337", "EV-0344", "EV-0632"]
        },
        {
            "id": "Q79-H143",
            "model": "A dynamic callback or transitive descendant of caller 51 tag 0x4b converts the PlayerCharacter/object-state transition into HitData, effective-protection or armor-skill processing.",
            "predicted_discriminant": "Resolve producer-backed virtual recipients or FUN_140cb4ae0 and demonstrate an exact data/call edge to mapped HitData, protection, AV11/AV12 or UseSkill targets; shared gate, PlayerCharacter identity and common DAT_1432740d8 tuple alone do not support the model.",
            "status": "proposed",
            "evidence": ["EV-0626", "EV-0632"]
        }
    ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0632"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L445"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: trace caller-50/51 shared configuration tuple through FUN_140cb4ae0, then continue worker caller 52.", "next_action": NEXT_ACTION}
    frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": NEXT_ACTION, "active_process": "TX-20261018-0013"}
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state = state.replace("51 of 62 initially uninspected worker callers are reviewed, with 11 remaining", "52 of 62 initially uninspected worker callers are reviewed, with 10 remaining")
    state = state.replace(
        "Caller 50 is bounded with no direct HitData/armor edge. Dynamic callbacks and the exact live armor result remain open.",
        "Caller 50 is bounded with no direct HitData/armor edge. EV-0632 maps caller 51/tag 0x4b to a PlayerCharacter +0xc8-gated paired-object flag transition and nested keyed-object updates; no direct HitData/protection/AV11/AV12/UseSkill sink appears. Ten producer virtual sites and callback effects remain open. Callers 50/51 both use the adjacent DAT_1432740d8 tuple in different helpers; schema/common mechanism unproved.")
    old = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x2df6d0 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600`; inspect the recursive `FUN_1402df6d0` state updater called by tag-0x4b producer `FUN_140738380` for any mapped HitData/protection/AV11/AV12/UseSkill descendants. Caller 51 is confirmed as PlayerCharacter state gating by slot +0x4c8; object callbacks remain unresolved."
    new = "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xcb4ae0 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600`; test whether caller 51 `FUN_140cb41c0` and caller 50 `FUN_1402c6810` use the shared `DAT_1432740d8..+8` tuple through a common registration/update mechanism or distinct caller-specific value paths. No HitData/armor edge is inferred from the tuple alone; after this synthesis discriminator, continue worker caller 52/62 `FUN_140658be0`."
    if state.count(old) != 1:
        raise SystemExit("STATE selected-next line did not match exactly")
    write(state_path, state.replace(old, new, 1))

    print("Registered EV-0632/CL-L445/M-0185, updated Q-0079 with caller-51 models, and checkpointed the cross-caller tuple discriminator.")


if __name__ == "__main__":
    main()
