#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c90 "
    "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
    "review worker caller 55/62 FUN_140658c90 for its exact tag/payload and producer, "
    "then continue the bounded caller census."
)
CAPTURE_BASES = [
    ".local/ghidra/gog-query-20261019T203707Z",
    ".local/ghidra/gog-query-20261019T201510Z",
    ".local/ghidra/gog-query-20261019T203854Z",
    ".local/ghidra/gog-query-20261019T204036Z",
    ".local/ghidra/gog-query-20261019T204151Z",
    ".local/ghidra/gog-query-20261019T204458Z",
    ".local/ghidra/gog-query-20261019T204627Z",
    ".local/ghidra/gog-query-20261019T201753Z",
]
EXPECTED = {
    ".local/ghidra/gog-query-20261019T203707Z.stdout.raw": "555d3af024684b9ab54e44eb8818ff98a949893109edb185817a32131305d5ec",
    ".local/ghidra/gog-query-20261019T203707Z.meta.json": "0ef8dff490a6dbb5830e67ce817fdf09b15e43431b7a3bf380f435b067c28479",
    ".local/ghidra/gog-query-20261019T201510Z.stdout.raw": "f629e4da674675574a2d813f4657b8fc20d75233526023884b65ec8f52af38de",
    ".local/ghidra/gog-query-20261019T201510Z.meta.json": "c0ccc67c95573ab65d45216b2a67521d4dc749ef2a2025e7fa7f26f4293aad00",
    ".local/ghidra/gog-query-20261019T203854Z.stdout.raw": "92b15de4d66a5a87ce18d8d41ce1f1f1a9163fad48672816241655fad37bf053",
    ".local/ghidra/gog-query-20261019T203854Z.meta.json": "f65987165fdb92f34bfed0ad0376e00b4937cde2ece5b123a53bc01029f9fb5b",
    ".local/ghidra/gog-query-20261019T204036Z.stdout.raw": "73ab2a0e94f7f31f63a1bfafab010732b41df1256e1348e91f7369df5356e3c4",
    ".local/ghidra/gog-query-20261019T204036Z.meta.json": "e4f25f19476deb77e746c97673c568cbb55a5f5c07eec2f753957c0f2d6d22ee",
    ".local/ghidra/gog-query-20261019T204151Z.stdout.raw": "28ac6ab103ad4fb8dd89f8275cfc6ab84746ec91403aa8323b7de9bb159fa63f",
    ".local/ghidra/gog-query-20261019T204151Z.meta.json": "db4700cc1384fdc70a6e39f407f5f5701a4e537b1f192bd2c2915bb272a3cbfa",
    ".local/ghidra/gog-query-20261019T204458Z.stdout.raw": "fdc999d4ab2b33e1980f578ccd470814adf2597ed4091538d52d84cfb60060f4",
    ".local/ghidra/gog-query-20261019T204458Z.meta.json": "9c6286354e75d3a50a2096c1ceed70408d6eb16bac5b6057303552024aee31b7",
    ".local/ghidra/gog-query-20261019T204627Z.stdout.raw": "e6b1df4f1b90446e4af498e2e0b7d888754d301b0cc376ca3012311115bf008c",
    ".local/ghidra/gog-query-20261019T204627Z.meta.json": "a9b79dd262780279049b96a5a50476cfe8b068e5c080575b87edc83b1121e29a",
    ".local/ghidra/gog-query-20261019T201753Z.stdout.raw": "5857e12b46bb8e9d7d0a81284fc67fe1ac3a00f8c36e73d4f7a140722316add0",
    ".local/ghidra/gog-query-20261019T201753Z.meta.json": "fcb12e2001f014fc4dfa4dbe85e462caadf9c19c10fd598a80069df8cd5d43f8",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def replace_once(path: Path, old: str, new: str) -> None:
    content = path.read_text(encoding="utf-8")
    if content.count(old) != 1:
        raise SystemExit(f"expected exactly one replacement target in {path}: {old[:90]}")
    write(path, content.replace(old, new, 1))


def append_once(path: Path, marker: str, body: str) -> None:
    original = path.read_text(encoding="utf-8")
    if marker in original:
        raise SystemExit(f"duplicate marker in {path}: {marker}")
    write(path, original.rstrip() + "\n\n" + body.strip())


def main() -> None:
    for relative, expected in EXPECTED.items():
        path = ROOT / relative
        if not path.exists() or sha(path) != expected:
            raise SystemExit(f"capture missing or hash mismatch: {relative}")
    metas = [
        json.loads((ROOT / f"{base}.meta.json").read_text(encoding="utf-8"))
        for base in CAPTURE_BASES
    ]
    for meta in metas:
        if not (
            meta.get("ok")
            and meta.get("read_only")
            and meta.get("auto_analysis_disabled")
            and meta.get("program_executable_path_matches_gog_binary")
        ):
            raise SystemExit("a Ghidra capture failed read-only, identity, or analysis-disabled verification")
        if (
            meta.get("analysis_binary_product_version") != "1.6.1179"
            or meta.get("analysis_binary_sha256") != GOG_SHA
        ):
            raise SystemExit("a Ghidra capture does not match the verified GOG executable")

    raws = {
        base: (ROOT / f"{base}.stdout.raw").read_text(encoding="utf-8", errors="replace")
        for base in CAPTURE_BASES
    }
    builder = raws[".local/ghidra/gog-query-20261019T203707Z"]
    dispatcher54 = raws[".local/ghidra/gog-query-20261019T201510Z"]
    target = raws[".local/ghidra/gog-query-20261019T203854Z"]
    spatial = raws[".local/ghidra/gog-query-20261019T204036Z"]
    world_rect = raws[".local/ghidra/gog-query-20261019T204151Z"]
    slot65 = raws[".local/ghidra/gog-query-20261019T204458Z"]
    builder32 = raws[".local/ghidra/gog-query-20261019T204627Z"]
    dispatcher32 = raws[".local/ghidra/gog-query-20261019T201753Z"]

    for token in [
        "local_88[0] = 0x54;",
        "FUN_140658c50(DAT_14319a7c0,param_1,0,uVar3);",
        "caller=FUN_14066b6e0",
        "cVar1 = FUN_1402bec30(lVar2,&local_18);",
        "cVar1 = FUN_14019ca70(DAT_1431886f0,&local_28);",
    ]:
        if token not in builder:
            raise SystemExit("caller-54 producer proof missing: " + token)
    if "case 0x54:" not in dispatcher54 or "FUN_1402eb6f0(plVar14," not in dispatcher54:
        raise SystemExit("tag-0x54 dispatcher proof missing")
    if (
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=63" not in target
        or "INDIRECT_CALL_SITE_COUNT=21" not in target
        or "FUN_140657f00(DAT_14319a7c0,param_1);" not in target
    ):
        raise SystemExit("tag-0x54 target census or tag-0x32 branch proof missing")
    target_body = target.split("DECOMPILATION_BEGIN=FUN_1402eb6f0", 1)[1].split(
        "DECOMPILATION_END=FUN_1402eb6f0", 1
    )[0]
    for sink in ["FUN_1406b9df0", "FUN_1406bb690", "FUN_1406bcaa0", "UseSkill"]:
        if sink in target_body:
            raise SystemExit("unexpected mapped direct combat/skill sink in target body: " + sink)
    for token in [
        "FUN_1402bec30(longlong param_1,float *param_2)",
        "*(uint *)(param_1 + 0x10) >> 0xd",
        "param_2[1]",
    ]:
        if token not in spatial:
            raise SystemExit("spatial-grid predicate proof missing: " + token)
    for token in [
        "FUN_14019ca70(longlong param_1,float *param_2)",
        "DAT_141fd7eb0",
        "param_1 + 0xc0",
    ]:
        if token not in world_rect:
            raise SystemExit("alternate spatial-predicate proof missing: " + token)
    if (
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=5" not in slot65
        or "INDIRECT_CALL_SITE_COUNT=1" not in slot65
        or "FUN_140e88c50(lVar3,1,0)" not in slot65
        or "FUN_1402e55a0(param_1)" not in slot65
    ):
        raise SystemExit("Actor slot-0x65 nested-state callback proof missing")
    if (
        "local_88[0] = 0x32;" not in builder32
        or "caller=FUN_1402eb6f0" not in builder32
        or "case 0x32:" not in dispatcher32
        or "FUN_140e88c50(plVar8,1,0);" not in dispatcher32
        or "+ 0x328" not in dispatcher32
    ):
        raise SystemExit("tag-0x32 builder/dispatcher proof missing")

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    by_id = {row.get("id") for row in evidence.get("items", [])}
    if "EV-0636" in by_id:
        raise SystemExit("EV-0636 already exists")
    for required in ["EV-0295", "EV-0296", "EV-0483", "EV-0484", "EV-0485", "EV-0486", "EV-0512", "EV-0635"]:
        if required not in by_id:
            raise SystemExit("missing synthesis evidence: " + required)

    note = EXP / "EV-0636-caller54-tag54-spatial-context-route.md"
    note_body = """# EV-0636 — Caller 54 tag-0x54 spatial/context route

## Competing models and discriminants

- **H1, combat/armor route:** the Actor+0x128/context payload or a descendant of the tag-0x54 handler reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed direct/virtual call or data edge from this payload into one of those mapped sinks.
- **H2, spatial/context update:** the producer selects tag 0x54 from process and world-grid predicates; the dispatcher enters a broad Actor update handler and its nested-state helpers. It predicts the observed coordinate tests, Actor/context payload, worker-gated state callbacks, and no mapped direct HitData/armor-skill sink.
- **Cross-domain identity remains a separate question:** Actor slot +0x380 reaches the same FUN_1402e55a0 used by the HitData receiver, but shared code alone predicts neither the same runtime pointer nor a causal hit/XP effect. A verified different owner/type or disjoint continuation would falsify a shared-object model; a same-pointer trace followed into a common HitData/ActorValue continuation would support it.

The discriminants are the builder payload, producer branch predicates, dispatcher target, complete direct/indirect census, the exact Actor slots and the immediate/deferred tag-0x32 continuation.

## Direct GOG evidence

All queries use the existing GOG SkyrimSE.exe Ghidra project for ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Adapter metadata confirms read-only operation with auto-analysis disabled, no import or overwrite, and matching program identity. GOG RVAs are not transferred to Steam AE 1.6.1170.0.

- FUN_140658c50 writes tag 0x54, retains the supplied Actor, and stores zero plus a producer-selected fourth field before submitting the record to FUN_14065b800. Its sole direct producer is FUN_14066b6e0 [EV-0636].
- In FUN_14066b6e0, the first branch requires a nonnull Actor+0x60 object with its byte +0x40 bit 0 clear and Actor flag bit 13 clear. It passes Actor coordinates at +0x54/+0x58 to FUN_1402bec30; a false result calls the tag-0x54 builder. The helper is a no-call predicate: after its +0x40 bit-0 and +0x10 bit-13 checks, it compares the floored horizontal coordinates against a pair of dwords at receiver +0x68 using a 0x1000 shift [EV-0636]. This is a spatial/process-grid interpretation of the field use, not a record-name or gameplay claim.
- On the alternate Actor+0x10 bit-13 branch, FUN_14019ca70 tests horizontal coordinates against a rectangle derived from fields +0xb0/+0xb4 and global DAT_141fd7eb0, unless its +0xc0 pointer is nonzero. In FUN_14066b6e0 this predicate selects other gated worker/direct callbacks; it does not construct tag 0x54 [EV-0636]. The global's concrete type is unknown.
- Dispatcher case 0x54 passes the retained Actor and both queued fields to FUN_1402eb6f0. That target has a complete 63-direct-edge census and 21 unresolved virtual sites. Its captured direct body has no mapped call to the HitData handlers, protection, AV11/AV12, or UseSkill; this is a bounded direct-body result, not a transitive negative [EV-0636].
- The target also has a shared-gate branch that either queues tag 0x32 with Actor and its slot-0x380 context result or, when the gate is clear, invokes Actor slot +0x328 immediately. The retained-context builder FUN_140657f00 adds reference counts for both pointers [EV-0636]. Dispatcher case 0x32 checks the retained/current context, calls FUN_140e88c50 when the current getter returns null, releases the retained reference, then invokes the same Actor slot +0x328 [EV-0636]. The RTTI-verified primary Actor table maps slot 0x65 (+0x328) to FUN_140666770 [EV-0400], [EV-0635]. Its bounded body clears nested state, calls the TLS/nested selector FUN_1402e55a0, and can enter FUN_140e88c50; one virtual site at +0x538 remains unresolved [EV-0636].
- The same FUN_1402e55a0 is primary Actor slot +0x380 and is used by the GOG HitData receiver FUN_1406b9df0 [EV-0512], [EV-0295], [EV-0296]. Caller 54's target reads a nested object's +0x18 state after the selector; the bounded tag-0x32 cleanup path reaches FUN_140e88c50, the recursive object-tree helper mapped on tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code paths, but no concrete same-pointer result or downstream HitData/armor/skill effect is captured.

## Cross-domain synthesis and result

Model H2 is supported for the captured direct route. The verified connections are code reuse from the tag-0x54 Actor update into the shared TLS/nested selector and recursive object-tree helper; the HitData connection remains a code-reuse edge, not a causal edge. The same returned object, event semantics, and runtime scheduling are not observed. Keep Q79-H46 proposed and update Q79-H47 as the supported conservative shared-helper model.

One of the target's 21 virtual sites, the slot-0x65 target's +0x538 call, and recursive descendants remain open. No causal edge is added to HitData, protection, AV11/AV12, armor skill XP, or OBJ-1 quest state. The clean Steam matched-hit/protection/raw-AVSK test remains outstanding [EV-0260].

## Next action

Continue caller 55/62, FUN_140658c90, with an exact producer/tag/payload trace.
"""
    write(note, note_body)
    note_rel = note.relative_to(ROOT).as_posix()
    local_hashes = {relative: sha(ROOT / relative) for relative in EXPECTED}
    local_hashes[note_rel] = sha(note)

    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    evidence["items"].append({
        "captured_utc": latest["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0636",
        "kind": "native",
        "source": "Identity-checked read-only GOG trace of worker caller 54/tag 0x54, spatial producer predicates, Actor update handler, tag-0x32 gated callback, and existing Actor/tree helper targets.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T203854Z.stdout.raw",
        "sha256": EXPECTED[".local/ghidra/gog-query-20261019T203854Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries, auto-analysis disabled, no import or overwrite. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": [
            "strict Python 3.12 dispatcher",
            "tools/ghidra_probe.py direct call-edge/decompilation and existing Actor pointer-table captures",
        ],
        "coverage": "Caller 54 builder/producer, case 0x54, complete direct census of FUN_1402eb6f0, both spatial predicates, Actor slot-0x65 target, tag-0x32 builder and dispatcher. Cross-links to verified Actor vtable, HitData receiver, shared helper, and tag-0x3C recursive object callback are cited separately.",
        "result": "Caller 54 is bounded as a spatial/context Actor update route with a tag-0x32 immediate/deferred slot-0x65 continuation. The direct target census is 63 calls and 21 unresolved virtual sites; slot-0x65 target has five direct calls and one unresolved +0x538 site. No mapped direct HitData/protection/AV11/AV12/UseSkill sink appears. Exact helper reuse with HitData and tag-0x3C is supported as code reuse only; no same object or causal OBJ-2 edge is established.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0400", "EV-0295", "EV-0296", "EV-0483", "EV-0484", "EV-0485", "EV-0486", "EV-0512", "EV-0635"],
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(
        ROOT / "research/CLAIMS.md",
        "| CL-L449 |",
        "| CL-L449 | In GOG AE 1.6.1179.0, caller 54's tag-0x54 Actor update is selected by a spatial/process predicate and routes through FUN_1402eb6f0 (63 direct edges, 21 unresolved virtual sites); its gated tag-0x32 branch and immediate path converge on Actor slot +0x328/FUN_140666770, whose nested-state route reuses FUN_1402e55a0 and FUN_140e88c50. | supported for captured direct routes and exact code reuse | [EV-0636], [EV-0400], [EV-0483]–[EV-0486], [EV-0512] | No direct mapped HitData/protection/AV11/AV12/UseSkill sink or same-runtime-object identity is established; dynamic descendants remain open. No OBJ-2 causal edge follows. |",
    )
    append_once(
        ROOT / "research/MECHANISMS.md",
        "## M-0189 —",
        """## M-0189 — Tag-0x54 spatial/context Actor update and tag-0x32 state callback (EV-0636)

Caller 54 builder FUN_140658c50 writes tag 0x54 with a retained Actor and producer-selected context field. Sole producer FUN_14066b6e0 selects this branch only under Actor process/flag conditions and when FUN_1402bec30 rejects the Actor's horizontal coordinates against a process-grid pair; a separate FUN_14019ca70 rectangle check gates different worker/direct callbacks [EV-0636]. These field and coordinate patterns support a spatial/context inference; the globals and runtime object semantics remain unnamed.

Dispatcher case 0x54 enters FUN_1402eb6f0, whose complete direct census has 63 edges and 21 unresolved virtual sites. No mapped direct HitData, protection, AV11/AV12 or UseSkill target appears [EV-0636]. A shared-gate branch queues tag 0x32 with Actor and its slot-0x380 context or calls Actor slot +0x328 immediately. The dispatcher case and immediate route converge on slot +0x328, mapped to FUN_140666770; its body clears nested state, uses FUN_1402e55a0, and may call recursive object-tree helper FUN_140e88c50 [EV-0400], [EV-0635], [EV-0636]. The context selector is also used by the HitData receiver [EV-0295], [EV-0296], [EV-0512], while the recursive helper is mapped on tag 0x3C [EV-0483]–[EV-0486]. Shared call targets establish code reuse, not same-pointer identity or hit/armor causality. No OBJ-2/OBJ-1 edge is added; 21 virtual sites and nested descendants remain open. Claim CL-L449.""",
    )
    append_once(
        ROOT / "research/CONTRADICTIONS.md",
        "## C-OBJ2-Q79-TAG54-SPATIAL-CONTEXT-VS-COMBAT",
        """## C-OBJ2-Q79-TAG54-SPATIAL-CONTEXT-VS-COMBAT — Actor update versus hit/armor route

- **Model A:** tag 0x54's Actor+0x128/context payload reaches HitData, effective protection, AV11/AV12 or armor-skill processing.
- **Model B:** producer FUN_14066b6e0 selects tag 0x54 from process/grid predicates; the target performs Actor/context and nested object-state work, including a tag-0x32 gated continuation.
- **Evidence:** producer coordinates and process fields, helper predicates, dispatcher and complete direct census, Actor slot-0x65 target, tag-0x32 builder/dispatcher [EV-0636]; Actor slot identity [EV-0400], shared selector [EV-0512], recursive helper [EV-0483]–[EV-0486].
- **Assessment:** B is supported for the captured direct path. A has no mapped direct sink, but 21 virtual sites, one slot-0x538 target and recursive descendants remain unresolved. No global no-hit, Steam, effective-protection, armor-XP, or bounty conclusion follows.
- **Discriminant:** resolve producer-backed virtual targets and preserve a clean Steam matched-hit/protection/raw-AVSK observation; same helper code alone cannot establish same-pointer identity.""",
    )
    append_once(
        ROOT / "research/KNOWLEDGE_GRAPH.md",
        "EV-0636 maps caller 54 tag-0x54 spatial/context state",
        """### EV-0636 maps caller 54 tag-0x54 spatial/context state

In GOG AE 1.6.1179.0, producer FUN_14066b6e0 uses process and horizontal grid predicates before building tag 0x54; case 0x54 calls FUN_1402eb6f0, whose complete direct census has 63 edges and 21 unresolved virtual sites [EV-0636]. This route also has a tag-0x32 immediate/deferred branch converging on Actor slot +0x328/FUN_140666770, which uses FUN_1402e55a0 and recursive helper FUN_140e88c50 [EV-0636], [EV-0400]. The selector is also used by the HitData receiver and tag-0x17 route [EV-0295], [EV-0296], [EV-0512]; the recursive helper is independently mapped on tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code edges, not a causal edge: no same runtime pointer, HitData effect, protection change, AV11/AV12 award, or armor XP effect is shown. H47 is supported as conservative code-reuse model; H46 remains proposed pending runtime identity evidence. Continue caller 55/62 FUN_140658c90.""",
    )

    mechanism_path = ROOT / "research/MECHANISMS.md"
    mechanism = mechanism_path.read_text(encoding="utf-8")
    old_m113 = """The helper selects TLS +0x5f0 when the receiver matches TLS +0x5f8; otherwise it returns a nested +0x68/+0x68 field or null.

The exact helper identity"""
    new_m113 = """The helper selects TLS +0x5f0 when the receiver matches TLS +0x5f8; otherwise it returns a nested +0x68/+0x68 field or null. EV-0636 adds the tag-0x54 Actor update and tag-0x32 slot-0x65 cleanup as additional consumers; this route reads nested state and can enter the recursive object-tree helper, but it does not establish the same returned pointer as the HitData route.

The exact helper identity"""
    if mechanism.count(old_m113) != 1:
        raise SystemExit("M-0113 insertion point was not unique")
    write(mechanism_path, mechanism.replace(old_m113, new_m113, 1))

    append_once(
        EXP / "results.md",
        "### Caller 54/62: tag-0x54 spatial/context update (EV-0636)",
        """### Caller 54/62: tag-0x54 spatial/context update (EV-0636)

The producer selects tag 0x54 under process/grid predicates and dispatches to FUN_1402eb6f0, whose full direct census has 63 edges and 21 unresolved virtual sites. Its gated tag-0x32 route and immediate branch converge on Actor slot +0x328/FUN_140666770; this callback reuses the TLS/nested selector FUN_1402e55a0 and recursive object-tree helper FUN_140e88c50 [EV-0636]. Those helpers also appear in the HitData receiver and tag-0x3C route [EV-0295], [EV-0296], [EV-0483]–[EV-0486], [EV-0512]. Treat this as exact code reuse only. No same-pointer or armor/HitData causal edge is established. Caller 54 is closed as a bounded route; caller 55/62 is FUN_140658c90.""",
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    hypotheses = {row.get("id"): row for row in item.get("hypotheses", [])}
    if "Q79-H149" in hypotheses or "Q79-H150" in hypotheses:
        raise SystemExit("caller-54 hypotheses already exist")
    h47 = hypotheses["Q79-H47"]
    h47["status"] = "supported"
    h47["model"] = "FUN_1402e55a0 is a generic TLS/nested-field selector reused by independent consumers: the HitData receiver, tag-0x17 object/node route, and the tag-0x54 Actor/context update. Identical helper code does not establish a shared runtime object or event semantics."
    h47["predicted_discriminant"] = "The captured consumers have separate call paths and bounded HitData-versus-state continuations. A same-pointer trace followed by a common HitData/ActorValue continuation would falsify this conservative code-reuse model; distinct producer-backed owners/types or separate continuations support it. Keep Steam observations separate from GOG mapping."
    h47["evidence"] = list(dict.fromkeys([*h47.get("evidence", []), "EV-0636"]))
    item["hypotheses"].extend([
        {
            "id": "Q79-H149",
            "model": "Caller 54 tag 0x54 is a spatial/process-gated Actor/context update; its tag-0x32 branch has immediate/deferred parity at Actor slot +0x328/FUN_140666770 and continues through nested-state/object-tree helpers.",
            "predicted_discriminant": "The producer predicates, builder payload, dispatcher case, verified Actor slot, and direct/deferred callsites establish this bounded route; exact globals and runtime object identity remain unknown.",
            "status": "supported",
            "evidence": ["EV-0636", "EV-0400", "EV-0483", "EV-0484", "EV-0512"],
        },
        {
            "id": "Q79-H150",
            "model": "One of FUN_1402eb6f0's 21 unresolved virtual descendants, the slot-0x65 target's +0x538 site, or a recursive descendant converts the caller-54 context update into HitData, effective protection, AV11/AV12, or armor-skill processing.",
            "predicted_discriminant": "Resolve producer-backed virtual targets and show a data/control edge from the tag-0x54 Actor/context payload into a mapped HitData, protection, AV11/AV12 or UseSkill sink. A bounded recipient path without such an edge narrows the model but cannot establish a runtime negative.",
            "status": "proposed",
            "evidence": ["EV-0636", "EV-0260"],
        },
    ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0636"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L449"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 54/tag-0x54 is bounded as spatial/context Actor state work; continue caller 55.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now,
        "next_action": NEXT_ACTION,
        "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 54 of 62 initially uninspected worker callers are reviewed, with 8 remaining."
    new_count = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 55 of 62 initially uninspected worker callers are reviewed, with 7 remaining."
    if state.count(old_count) != 1:
        raise SystemExit("STATE active caller count did not match exactly once")
    state = state.replace(old_count, new_count, 1)
    old_summary = "EV-0635 maps caller 53/tag 0x50 from primary Actor slot +0x448 to an Actor/process handler that skips PlayerCharacter; 17 virtual sites remain unresolved, with no direct mapped HitData/armor sink."
    new_summary = old_summary + " EV-0636 bounds caller 54/tag 0x54 as a spatial/context Actor update with tag-0x32 immediate/deferred slot +0x328 convergence; 21 target virtual sites remain open, with no direct mapped HitData/armor sink."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE caller-53 summary did not match exactly once")
    state = state.replace(old_summary, new_summary, 1)
    state = state.replace(
        "Q-0079 has 52/62 initially uninspected worker callers reviewed; 10 remain.",
        "Q-0079 has 55/62 initially uninspected worker callers reviewed; 7 remain.",
        1,
    )
    tick = chr(96)
    old_next = (
        "**Selected next line:** run " + tick
        + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c50 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"
        + tick + "; review worker caller 54/62 " + tick + "FUN_140658c50" + tick
        + " for its exact tag/payload and producer, then continue the bounded caller census. "
        + "Caller 53's Actor handler has 17 unresolved virtual sites and no direct mapped HitData/armor sink."
    )
    new_next = (
        "**Selected next line:** run " + tick
        + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c90 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"
        + tick + "; review worker caller 55/62 " + tick + "FUN_140658c90" + tick
        + " for its exact tag/payload and producer, then continue the bounded caller census. "
        + "Caller 54's tag-0x54 target has 21 unresolved virtual sites and no direct mapped HitData/armor sink."
    )
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line did not match exactly")
    state = state.replace(old_next, new_next, 1)
    state = state.replace(
        "EV-0593 resolves queue/direct parity and bounds the helper's direct edges.",
        "EV-0593 resolves queue/direct parity and bounds the helper's direct edges; EV-0636 maps caller 54/tag 0x54 as spatial/context Actor state work with a tag-0x32 slot-0x65 continuation and shared-code links, but no HitData causal edge.",
        1,
    )
    write(state_path, state)

    append_once(
        ROOT / "research/ROADMAP.md",
        "## Cross-domain synthesis — Q-0079 caller 54 (EV-0636)",
        """## Cross-domain synthesis — Q-0079 caller 54 (EV-0636)

The tag-0x54 Actor update uses primary Actor slot +0x380/FUN_1402e55a0, the exact selector also present in the HitData receiver and tag-0x17 route [EV-0295], [EV-0296], [EV-0512], [EV-0636]. The tag-0x32 immediate/deferred state callback also reaches the recursive object-tree helper already mapped for tag 0x3C [EV-0483]–[EV-0486]. These are verified shared-code edges; the selected runtime pointer and downstream HitData/armor effect remain unknown. Q79-H47 is supported as the conservative code-reuse model, while H46's shared-object claim remains proposed. Caller 54 has no mapped direct HitData/protection/AV11/AV12/UseSkill sink, but 21 virtual sites and recursive descendants remain open [EV-0636]. No causal edge is added. OBJ-2 still requires the clean Steam matched-hit/protection/raw-AVSK test [EV-0260]; OBJ-1 remains separate. Continue caller 55/62 FUN_140658c90.""",
    )
    print("Registered EV-0636/CL-L449/M-0189, synthesized helper reuse without a causal edge, and checkpointed caller 55.")


if __name__ == "__main__":
    main()
