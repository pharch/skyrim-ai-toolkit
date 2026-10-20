#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
CAPTURES = [
    ".local/ghidra/gog-query-20261019T200612Z",
    ".local/ghidra/gog-query-20261019T200854Z",
    ".local/ghidra/gog-query-20261019T201009Z",
]
EXPECTED = {
    ".local/ghidra/gog-query-20261019T200612Z.stdout.raw": "c4925c53bd3545e0ea73958ba800dbfa257f7551260d798ad843ea38593de5fa",
    ".local/ghidra/gog-query-20261019T200612Z.meta.json": "b9f93fc33fdfc054b1e8c5deb4e2529d901a37c73caca379eb6e391be6311760",
    ".local/ghidra/gog-query-20261019T200854Z.stdout.raw": "99ec5e396c805ab6db6c4ab9239b0349c8d7857c00e755d88c9f69bb7f5a6054",
    ".local/ghidra/gog-query-20261019T200854Z.meta.json": "044d8d8bc9b00d5a3b57f49217d78d30f2d8ad9fd9ac2097088c7b8ae91b1e50",
    ".local/ghidra/gog-query-20261019T201009Z.stdout.raw": "b4360bc0eb87cfb51e6806b1efa794073418684bbdf6addc47ddc61c05583301",
    ".local/ghidra/gog-query-20261019T201009Z.meta.json": "a6b96d09f202558f881ba72ce74cdc512d0894152af4e5472a420afc8be6ed26",
}
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658be0 "
    "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
    "review worker caller 52/62 FUN_140658be0 for its exact tag/payload and immediate "
    "producer, then continue the bounded caller census while preserving the no-HitData/armor-edge boundary."
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

    helper = (ROOT / f"{CAPTURES[0]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    factory = (ROOT / f"{CAPTURES[1]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    global_query = (ROOT / f"{CAPTURES[2]}.stdout.raw").read_text(encoding="utf-8", errors="replace")
    for token in [
        "OUTGOING_DIRECT_CALL_EDGE_COUNT=4",
        "piVar3[8] = *param_7;",
        "piVar3[9] = param_7[1];",
        "piVar3[10] = param_7[2];",
        "FUN_140cbc770(*(undefined8 *)(param_1 + (longlong)*param_1 * 2 + 2),piVar3);",
    ]:
        if token not in helper:
            raise SystemExit("queued-event helper proof missing: " + token)
    for token in [
        "local_30 = DAT_1432740d8;",
        "local_2c = DAT_1432740dc;",
        "local_28 = DAT_1432740e0;",
        "local_170 = 0;",
        "local_178 = *param_1;",
        "local_174 = param_1[1];",
        "FUN_140e854e0(plVar5,&local_178);",
    ]:
        if token not in factory:
            raise SystemExit("caller-50 factory-consumption proof missing: " + token)
    if "ADDRESS_TARGET=1432740d8" not in global_query or "ADDRESS_TARGET_XREF_COUNT=1349" not in global_query:
        raise SystemExit("global-address reference census proof missing")
    if "ADDRESS_CONTEXT_INSTRUCTION_COUNT=0" not in global_query:
        raise SystemExit("address query scope proof missing")

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    by_id = {row.get("id") for row in evidence.get("items", [])}
    if "EV-0633" in by_id:
        raise SystemExit("EV-0633 already exists")
    for required in ["EV-0626", "EV-0632"]:
        if required not in by_id:
            raise SystemExit("missing contextual evidence: " + required)

    note = EXP / "EV-0633-shared-global-tuple-consumers.md"
    note_body = """# EV-0633 — Shared global tuple has distinct direct consumers

## Competing models and discriminants

- H1: caller 50 fallback construction and caller 51's queued callback use the same tuple as one shared registration/update mechanism. It predicts a shared helper path or matching direct field transformation.
- H2: the adjacent global dwords are reused as common configuration input in distinct mechanisms. It predicts different direct consumers and context-specific field handling, while leaving scalar meanings unresolved.

The discriminants are the exact direct call graph and field copies in `FUN_140cb4ae0` and `FUN_1402c6810`, caller 50's fallback arguments, and the bounded address query for `DAT_1432740d8`.

## Direct GOG evidence

Three captures use the existing GOG AE 1.6.1179.0 SkyrimSE.exe Ghidra project, verified SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. Queries were read-only with auto-analysis disabled; they did not import or overwrite the project. These GOG addresses are not transferred to the separately verified Steam AE 1.6.1170.0 executable.

- `FUN_140cb4ae0` has four direct callees and no unresolved indirect call site in its body. Its queueing path allocates an event record, copies all three dwords from `param_7` to record dwords `+0x20`, `+0x24`, and `+0x28`, retains a separate object pointer, and submits the record through `FUN_140cbc770`. Its analyzed incoming callers include `FUN_140cb41c0`, which supplies `DAT_1432740d8` [EV-0633]. The helper has 42 call edges across 39 caller functions.
- Caller 50's factory `FUN_1402c6810` is a separate function with 26 direct call edges, two unresolved virtual sites, and two analyzed direct caller functions. Its caller `FUN_1402c65b0` copies `DAT_1432740d8`, `+4`, and `+8` into a local three-dword input, then invokes the factory with second argument zero [EV-0626], [EV-0633]. The false/fallback factory path copies the first two dwords to fields passed by `FUN_140e854e0`; it sets the third field to zero. The factory's other construction branch assigns the third input dword. The full semantic names of the three fields are not established.
- A bounded address-context query for image RVA `0x32740d8` reports 1,349 xrefs to the first dword, but no instruction context or initialized scalar values [EV-0633]. This does not identify the tuple's values or names.
- The two direct helper paths and field transformations differ. The evidence falsifies the specific shared-direct-registration/update model; it supports reuse of the same adjacent storage by distinct callers only. Caller 51's dynamic virtual callbacks and any transitive relation remain unresolved.

## Result and limits

H2 is supported for the captured direct call paths; H1's shared-direct-primitive prediction is falsified. The `DAT_1432740d8..+8` values and schema remain unknown. The result adds no causal edge to HitData, effective armor protection, AV11/AV12, UseSkill, armor XP, or OBJ-1 quest/encounter gates; it does not resolve Q-0079 or the bounty.

## Next action

Continue worker caller 52/62 at `FUN_140658be0`, record its exact tag and producer, and resume independent caller review.
"""
    write(note, note_body)

    note_rel = note.relative_to(ROOT).as_posix()
    local_hashes = {relative: sha(ROOT / relative) for relative in EXPECTED}
    local_hashes[note_rel] = sha(note)
    evidence["items"].append({
        "captured_utc": metas[2]["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0633",
        "kind": "native",
        "source": "Identity-checked GOG direct call paths for worker callback helper FUN_140cb4ae0 and caller-50 factory FUN_1402c6810; bounded address query at DAT_1432740d8.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T200612Z.stdout.raw",
        "sha256": EXPECTED[".local/ghidra/gog-query-20261019T200612Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only captures, auto-analysis disabled, no import or overwrite. GOG RVAs are not transferred to Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": [
            "strict Python 3.12 dispatcher",
            "tools/ghidra_probe.py --rva call-edge/decompilation queries and --address-rva 0x32740d8",
        ],
        "coverage": "FUN_140cb4ae0 copies three dwords from its supplied tuple into a queued event record and schedules it through FUN_140cbc770. Caller-50 FUN_1402c6810 separately consumes a local copy of DAT_1432740d8..+8; in its false/fallback branch the first two dwords reach FUN_140e854e0 and the third is set to zero. The address query reports 1,349 xrefs to the first dword but no scalar initializer values. No direct HitData/protection/AV11/AV12/UseSkill edge is shown in these captured bodies.",
        "result": "The shared-direct-registration/update model is falsified for the captured call paths: caller 50's object factory and caller 51's queued-event record helper are distinct functions with different direct field transformations. Reuse of the adjacent global tuple is supported, but its values, full schema, and any deeper relation remain unresolved. No causal armor-XP or HitData edge is added.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0626", "EV-0632"],
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(
        ROOT / "research/CLAIMS.md",
        "| CL-L446 |",
        "| CL-L446 | In GOG AE 1.6.1179.0, caller 50's fallback factory and caller 51's queued-event helper read the same adjacent `DAT_1432740d8..+8` tuple through distinct direct paths; the fallback factory forwards its first two dwords and zero as the third field, while the queue helper copies all three into event-record fields. | supported for captured direct call paths | [EV-0626], [EV-0632], [EV-0633] | The tuple's scalar values/names and any transitive relationship are unresolved; no HitData, protection, AV11/AV12, UseSkill or armor-XP edge is established. |",
    )
    append_once(
        ROOT / "research/MECHANISMS.md",
        "## M-0186 —",
        """## M-0186 — Shared tuple reused by distinct factory and event-record paths (EV-0633)

Caller 50's `FUN_1402c6810` consumes a local copy of `DAT_1432740d8..+8` as a three-dword constructor input. In its false/fallback branch it sends the first two values to `FUN_140e854e0` and sets the third to zero. Caller 51 reaches `FUN_140cb4ae0`, which copies all three supplied values into a queued event record before scheduling it through `FUN_140cbc770` [EV-0626], [EV-0632], [EV-0633]. These are distinct direct mechanisms, not a shared registration/update primitive. The tuple values and field semantics remain unknown; this synthesis adds no causal HitData/armor/quest edge. Claim CL-L446.""",
    )
    append_once(
        ROOT / "research/CONTRADICTIONS.md",
        "## C-OBJ2-Q79-SHARED-TUPLE-CONSUMERS",
        """## C-OBJ2-Q79-SHARED-TUPLE-CONSUMERS — shared mechanism versus shared input storage

- **Model A:** caller 50 fallback construction and caller 51's state callback share a registration/update primitive because both pass `DAT_1432740d8..+8`.
- **Model B:** the same adjacent input storage is reused by distinct mechanisms with caller-specific field transformations.
- **Evidence:** caller 50 factory provenance [EV-0626], caller 51 producer path [EV-0632], and the direct helper/factory/address captures [EV-0633].
- **Assessment:** B is supported for the captured direct paths: `FUN_140cb4ae0` serializes all three dwords into a queued event record, whereas `FUN_1402c6810` configures a factory object and zeroes the third fallback field. A's predicted shared direct primitive is falsified. The tuple's values/names and any deeper transitive relation remain unresolved; no causal HitData/armor edge is added.""",
    )
    append_once(
        ROOT / "research/KNOWLEDGE_GRAPH.md",
        "EV-0633 disambiguates the shared DAT_1432740d8 tuple consumers",
        """### EV-0633 disambiguates the shared DAT_1432740d8 tuple consumers

Caller 50's fallback factory consumes the tuple as object-configuration input and replaces the third field with zero on its false branch. Caller 51's helper copies all three supplied dwords into queued event metadata. The direct helpers and transformations differ; reuse of one global input does not establish a shared registration/update mechanism [EV-0626], [EV-0632], [EV-0633], [CL-L446], [M-0186]. The address query reports 1,349 references to the first dword but exposes no initialized values. **No causal edge is added** from this tuple to HitData, protection, armor XP or quest gates because the captured paths contain no data/control edge to those mechanisms and the tuple semantics remain unknown. Continue caller 52/62 `FUN_140658be0`.""",
    )
    append_once(
        EXP / "results.md",
        "### Cross-caller synthesis: shared tuple consumers (EV-0633)",
        """### Cross-caller synthesis: shared tuple consumers (EV-0633)

Caller 51 reaches `FUN_140cb4ae0` through `FUN_140cb41c0`; that helper copies all three dwords at its supplied tuple pointer into event-record fields and queues the record through `FUN_140cbc770`. Caller 50 independently copies `DAT_1432740d8`, `+4`, and `+8` into a factory input for `FUN_1402c6810`; its false/fallback branch sends the first two dwords through `FUN_140e854e0` and sets the third to zero [EV-0626], [EV-0632], [EV-0633].

The direct consumers and field transformations differ, falsifying the proposed shared direct registration/update primitive. The tuple's values and semantic names remain unknown; the address query finds 1,349 xrefs to the first dword but provides no initialized scalar values. This shared-storage observation adds no HitData, armor protection, AV11/AV12, UseSkill, armor-XP, or quest-gate edge. Resume caller 52/62 `FUN_140658be0`.""",
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    hypothesis_ids = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H144" in hypothesis_ids:
        raise SystemExit("Q79-H144 already exists")
    item["hypotheses"].append({
        "id": "Q79-H144",
        "model": "Caller 50 fallback construction and caller 51's queued state callback use one shared direct registration/update primitive because both receive DAT_1432740d8..+8.",
        "predicted_discriminant": "A shared direct helper or matching field transformation should appear in FUN_1402c6810 and FUN_140cb4ae0; distinct consumers and different field copies falsify this direct-path model while leaving deeper transitive relations open.",
        "status": "falsified",
        "evidence": ["EV-0626", "EV-0632", "EV-0633"],
    })
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0633"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L446"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: cross-caller shared-tuple model narrowed by distinct direct consumers; continue caller 52.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": NEXT_ACTION, "active_process": "TX-20261018-0013"}
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old_summary = "Callers 50/51 both use the adjacent DAT_1432740d8 tuple in different helpers; schema/common mechanism unproved."
    new_summary = "EV-0633 shows callers 50/51 consume the adjacent DAT_1432740d8 tuple through distinct direct paths: the fallback factory forwards the first two dwords and zero as the third field, while the queued-event helper copies all three; no common direct primitive or HitData/armor edge is established, and scalar semantics remain unknown."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE tuple summary did not match exactly once")
    state = state.replace(old_summary, new_summary, 1)
    old_next = """**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0xcb4ae0 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600`; test whether caller 51 `FUN_140cb41c0` and caller 50 `FUN_1402c6810` use the shared `DAT_1432740d8..+8` tuple through a common registration/update mechanism or distinct caller-specific value paths. No HitData/armor edge is inferred from the tuple alone; after this synthesis discriminator, continue worker caller 52/62 `FUN_140658be0`.
"""
    new_next = """**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658be0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; review worker caller 52/62 `FUN_140658be0` for its exact tag/payload and immediate producer, then continue the bounded caller census. Callers 50/51 use the shared tuple through distinct direct mechanisms, with scalar semantics unresolved and no HitData/armor edge established.
"""
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line did not match exactly")
    state = state.replace(old_next, new_next, 1)
    state = state.replace("Q-0079 has 50/62 exact worker callers reviewed; 12 remain.", "Q-0079 has 52/62 initially uninspected worker callers reviewed; 10 remain.", 1)
    write(state_path, state)

    print("Registered EV-0633/CL-L446/M-0186, falsified Q79-H144's shared-direct-path prediction, and checkpointed caller 52.")


if __name__ == "__main__":
    main()
