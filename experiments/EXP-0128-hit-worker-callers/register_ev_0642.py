#!/usr/bin/env python3
"""Register caller 60/tag 0x5C as a HitData-derived serialized shared-helper route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    ".local/ghidra/gog-query-20261019T220221Z.stdout.raw": "0edb99b54cfe50fd55f5755cb9ed77dcd984c416fc4abc2502454b65df1929d5",
    ".local/ghidra/gog-query-20261019T220352Z.stdout.raw": "0ec2eda0963fcd7a4b3e993455a871d8db5f206b3e077aaac36f144a4a085263",
}
METAS = {
    ".local/ghidra/gog-query-20261019T220221Z.meta.json": "87375885871ac2be1d049d6270e8d50fd69ca4fc2b4f7499716b573c500a2f9f",
    ".local/ghidra/gog-query-20261019T220352Z.meta.json": "ab392859f8ec3e382ebcd86277afda9d8fd76f39165d57b2427e64ac70f5d8e7",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker not in old:
        write(path, old.rstrip() + "\n\n" + body.strip())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise SystemExit(f"{label} expected exactly once, found {text.count(old)}")
    return text.replace(old, new, 1)


def main() -> None:
    raws: dict[str, str] = {}
    local_hashes: dict[str, str] = {}
    metas = []
    for rel, expected in CAPTURES.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("capture/hash mismatch: " + rel)
        raws[rel] = path.read_text(encoding="utf-8", errors="replace")
        local_hashes[rel] = expected
    for rel, expected in METAS.items():
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
    proof_sets = {
        ".local/ghidra/gog-query-20261019T220221Z.stdout.raw": [
            "TARGET_RVA=0x658E50", "local_88[0] = 0x5c;",
            "FUN_1407dce10(local_res10,param_2)",
            "FUN_140658e50(DAT_14319a7c0,param_2);",
            "FUN_1406be430(lVar20,pfVar25,param_2[0x14]",
            "OUTGOING_DIRECT_CALL_EDGE_COUNT=5", "INDIRECT_CALL_SITE_COUNT=2",
        ],
        ".local/ghidra/gog-query-20261019T220352Z.stdout.raw": [
            "case 0x5c:", "FUN_1406be2c0(local_158,lVar15,*(undefined1 *)(param_1 + 4));",
            "DECOMPILATION_BEGIN=FUN_1406be2c0", "FUN_1406be430(lVar7,param_1,param_2[0x14]",
            "OUTGOING_DIRECT_CALL_EDGE_COUNT=3", "INDIRECT_CALL_SITE_COUNT=3",
            "(**(code **)(*(longlong *)(param_1 + 0xb8) + 8))",
            "FUN_1403fd6b0(lVar5,&local_98",
        ],
    }
    for rel, tokens in proof_sets.items():
        for token in tokens:
            if token not in raws[rel]:
                raise SystemExit(f"proof token missing from {rel}: {token}")

    note = EXP / "EV-0642-caller60-tag5c-hitdata-derived-helper-route.md"
    write(note, """# EV-0642 — Caller 60/tag-0x5C HitData-derived serialized helper route

## Competing models and discriminants

- H1, HitData-derived serialized branch: `FUN_1406b9df0` selects caller 60/tag 0x5C from a mapped HitData handler, clones its second argument with `FUN_1407dce10`, and the dispatcher returns the cloned context to `FUN_1406be2c0`, which calls shared helper `FUN_1406be430`. It predicts the producer edge, copied handler fields, tag-0x5C case, and common helper identity.
- H2, unrelated Actor/process update: the tag may use worker infrastructure but is produced elsewhere or changes only unrelated actor state. It predicts no producer edge from the mapped HitData handler or copy of its event context.
- H3, armor protection or armor-XP operation: the serialized helper directly changes effective protection or routes to AV11/AV12/UseSkill while retaining protection. It predicts a mapped sink/field in the bounded helper chain, or a clean Steam matched-hit observation; helper reuse alone is insufficient.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This project is separate from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 60 `FUN_140658e50` writes tag 0x5C, allocates an event/context object, calls `FUN_1407dce10(local_res10,param_2)` to clone the producer's second argument, derives a byte flag through a virtual `+0x478` call, and queues through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1406b9df0`, the mapped HitData handler [EV-0295], [EV-0296], [EV-0642].
- In `FUN_1406b9df0`, after Actor/process and HitData-field predicates, a branch where `FUN_140667430(param_1)` is nonzero calls caller 60/tag 0x5C. The alternate zero branch directly calls `FUN_1406be430`; the queued route later reaches that same exact function through `FUN_1406be2c0`. The common callee identity is established, but receiver and argument identity/equivalence are not [EV-0642].
- Dispatcher case 0x5C reads the cloned context's object identifier at `+0x18`, resolves it, and calls `FUN_1406be2c0(resolved_object,context,flag)`. The target has three direct call edges and three unresolved indirect sites. Under its captured object/context predicates it copies vector fields and calls `FUN_1406be430` [EV-0642].
- Existing EV-0431 maps `FUN_1407dce10` as copying handler fields at offsets 0x50, 0x54, 0x5C, and 0x80 consumed by `FUN_1406b9df0`; caller 60 invokes this helper on the same handler argument [EV-0431], [EV-0642]. This supports a HitData-derived serialized context, not proof that every field has the same runtime object identity.
- Existing EV-0600 maps `FUN_1406be430` as vector transformation with a numeric ActorValue query at receiver `+0xB8` using value `0x24`, then a vector/physics-like sink `FUN_1403fd6b0`; the helper has no direct AV11/AV12/UseSkill sink [EV-0600]. The caller-60 route adds no direct protection or armor-skill sink in the captured dispatcher/target bodies [EV-0642].

## Result and limits

H1 is supported: caller 60 is a HitData-derived worker branch and its dispatcher target rejoins the same helper used on the alternate direct branch of `FUN_1406b9df0`. H2 is contradicted for producer origin, though worker transport and shared helpers still serve other systems. H3 is not supported by the bounded direct call chain; effective protection, armor XP, runtime AV award, the exact meaning of ActorValue 0x24, and descendants of three unresolved virtual sites remain open. The tag is 0x5C, not the tag-0xB constructor sought by the wider caller census. This does not establish ordinary enemy-hit coverage, a level-one bypass, an armor-XP result, Steam behavior, or bounty resolution. Record the supported HitData/helper edge; add no OBJ-1/OBJ-2 causal edge.

## Next action

Continue caller 61/62, `FUN_140658f70`; preserve caller 62/62 and the independent clean Steam matched-hit/effective-protection/raw-AVSK test.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ids = {row.get("id") for row in evidence.get("items", [])}
    if not {"EV-0295", "EV-0296", "EV-0431", "EV-0600", "EV-0260"} <= ids:
        raise SystemExit("missing contextual evidence")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    record = {
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0642", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 60/tag 0x5C, its mapped HitData producer, dispatcher and shared helper target.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T220221Z.stdout.raw",
        "sha256": CAPTURES[".local/ghidra/gog-query-20261019T220221Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries with auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge queries"],
        "coverage": "Tag-0x5C builder/sole analyzed producer/dispatcher; HitData context clone through FUN_1407dce10; conditional direct/deferred paths to shared FUN_1406be430; ActorValue 0x24 query and vector/physics-like direct sink; three unresolved virtual sites in FUN_1406be2c0.",
        "result": "Caller 60/tag 0x5C is directly produced within mapped HitData handler FUN_1406b9df0, clones its handler context, and rejoins the same FUN_1406be430 helper through dispatcher target FUN_1406be2c0 that the alternate branch calls directly. The bounded helper is vector/physics-like and has no direct AV11/AV12/UseSkill sink; effective protection, XP, runtime behavior and three virtual descendants remain unresolved.",
        "local_hashes": local_hashes, "related_evidence": ["EV-0295", "EV-0296", "EV-0431", "EV-0600", "EV-0260"],
    }
    if "EV-0642" not in ids:
        evidence["items"].append(record)
        write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L455 |",
        "| CL-L455 | In GOG AE 1.6.1179.0, caller 60/tag 0x5C is produced directly by mapped HitData handler FUN_1406b9df0, clones its handler context with FUN_1407dce10, and returns through dispatcher target FUN_1406be2c0 to shared helper FUN_1406be430. | supported for the captured producer/copy/dispatch/common-helper route | [EV-0295], [EV-0296], [EV-0431], [EV-0600], [EV-0642] | Shared helper use does not establish identical receiver/arguments, ordinary enemy-hit coverage, effective protection or armor XP; AV 0x24 meaning and three target virtual sites remain open, and no direct AV11/AV12/UseSkill sink is mapped. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0195 —",
        """## M-0195 — Tag-0x5C HitData-derived serialized branch to shared vector helper (EV-0642)

Caller 60 `FUN_140658e50` builds tag 0x5C, clones its second argument through `FUN_1407dce10`, derives a byte flag through virtual slot +0x478, and queues the context. Its sole analyzed producer is `FUN_1406b9df0`, the mapped HitData handler [EV-0295], [EV-0296], [EV-0642]. EV-0431 maps the clone helper's copied fields at 0x50/0x54/0x5C/0x80 against fields consumed by that handler [EV-0431].

In the producer, one guarded branch queues tag 0x5C when `FUN_140667430` is nonzero; the alternate zero branch calls `FUN_1406be430` directly. Dispatcher case 0x5C resolves an object identifier from the copied context and calls `FUN_1406be2c0`, which uses three direct calls and three unresolved virtual sites and conditionally calls the exact same `FUN_1406be430` helper [EV-0642]. The common function identity supports a direct/deferred shared-helper relationship, not identical receiver or arguments. EV-0600 maps the helper as vector transformation, numeric ActorValue query 0x24, and a vector/physics-like `FUN_1403fd6b0` sink, without a direct AV11/AV12/UseSkill call [EV-0600]. No level/protection/armor-XP or ordinary-hit result follows. No OBJ-1/OBJ-2 edge is added. Claim CL-L455.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q79-TAG5C-HITDATA-HELPER-VS-ARMOR-XP",
        """## C-OBJ2-Q79-TAG5C-HITDATA-HELPER-VS-ARMOR-XP — serialized hit context versus armor-skill effect

- Model A: tag 0x5C is a HitData-derived serialized branch; its producer is FUN_1406b9df0, it clones handler context, and its dispatcher returns to shared FUN_1406be430 through FUN_1406be2c0.
- Model B: the route directly alters effective armor protection or changes hit-earned AV11/AV12/UseSkill credit while preserving protection.
- Evidence: caller 60 builder, producer, cloned fields, case 0x5C, target, and shared helper capture [EV-0295], [EV-0296], [EV-0431], [EV-0600], [EV-0642].
- Assessment: A is supported for the captured producer/copy/dispatcher/common-helper relationship. B has no mapped direct sink in the bounded bodies. The helper queries numeric ActorValue 0x24 and calls a vector/physics-like sink, but that is not an identified armor or XP effect. Three indirect sites, descendants, exact runtime receiver/data, ordinary-hit coverage, and clean Steam behavior remain open. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: only extend descendants if a producer-backed dynamic target reaches effective protection, HitData award logic, AV11/AV12, or UseSkill; independently complete the clean Steam matched-hit/protection/raw-AVSK test [EV-0260].""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0642 connects caller 60 tag-0x5C to mapped HitData context",
        """### EV-0642 connects caller 60 tag-0x5C to mapped HitData context

Caller 60 tag 0x5C is produced by mapped HitData handler `FUN_1406b9df0`; it clones handler fields with `FUN_1407dce10`, then dispatches to `FUN_1406be2c0`, which calls the same `FUN_1406be430` helper used in the producer's alternate direct branch [EV-0295], [EV-0296], [EV-0431], [EV-0642]. EV-0600 maps that helper to a vector/physics-like operation and numeric ActorValue query 0x24, with no direct AV11/AV12/UseSkill sink [EV-0600]. This is a supported HitData-to-shared-helper relationship; it does not connect to effective armor protection or XP. No OBJ-1/OBJ-2 edge is added. Claim mapping: CL-L455 -> M-0195.""")
    append_once(EXP / "results.md", "### Caller 60/62: tag-0x5C HitData-derived serialized helper route (EV-0642)",
        """### Caller 60/62: tag-0x5C HitData-derived serialized helper route (EV-0642)

Caller 60's sole producer is mapped HitData handler `FUN_1406b9df0`. It builds tag 0x5C after cloning its handler argument with `FUN_1407dce10`; dispatcher case 0x5C resolves the cloned context's object identifier and calls `FUN_1406be2c0`. The target conditionally calls `FUN_1406be430`, the exact helper called directly on the producer's alternate predicate branch [EV-0295], [EV-0296], [EV-0431], [EV-0642]. This supports a HitData-derived direct/deferred shared-helper relationship, not identical runtime arguments or ordinary enemy-hit coverage. `FUN_1406be430` queries numeric ActorValue 0x24 and reaches a vector/physics-like sink, with no direct AV11/AV12/UseSkill target [EV-0600]. Effective protection, armor XP and dynamic descendants remain unmeasured; no OBJ-1/OBJ-2 causal edge is added. Continue caller 61/62 FUN_140658f70.""")
    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 caller 60 (EV-0642)",
        """## Cross-domain synthesis — Q-0079 caller 60 (EV-0642)

Caller 59 is a deferred disarm-related Actor action; caller 60 is a distinct tag-0x5C event produced inside mapped HitData handler `FUN_1406b9df0` and serialized through `FUN_1407dce10` [EV-0641], [EV-0642]. The tag-0x5C dispatcher returns to `FUN_1406be430`, which is also called on the producer's alternate branch and is shared with an Actor/process callback [EV-0599], [EV-0600]. This is verified cross-system helper reuse with distinct runtime arguments. Its bounded effect is vector/physics-like plus an unnamed numeric ActorValue-0x24 query; no direct effective-protection/AV11/AV12/UseSkill edge is established. The two worker events are not one mechanism. Continue caller 61/62 FUN_140658f70 and retain clean Steam evidence requirements [EV-0260].""")

    next_action = ("Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658f70 "
                   "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
                   "review worker caller 61/62 FUN_140658f70 for tag/payload, producer and dispatcher route; "
                   "then inspect final caller 62/62 FUN_140658fb0 and only close Q-0079 after the exact caller census reconciles.")
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    known = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H161" not in known:
        item["hypotheses"].append({
            "id": "Q79-H161",
            "model": "Caller 60/tag 0x5C is a HitData-derived serialized branch from FUN_1406b9df0 that returns to shared helper FUN_1406be430 through FUN_1406be2c0.",
            "predicted_discriminant": "The mapped HitData producer, context-clone helper and tag-0x5C dispatcher-to-shared-helper path support this model; common helper identity does not prove same runtime receiver or ordinary-hit coverage.",
            "status": "supported", "evidence": ["EV-0295", "EV-0296", "EV-0431", "EV-0600", "EV-0642"],
        })
    if "Q79-H162" not in known:
        item["hypotheses"].append({
            "id": "Q79-H162",
            "model": "The tag-0x5C shared-helper route directly changes effective armor protection or armor-skill XP while preserving protection.",
            "predicted_discriminant": "Map a producer-backed descendant to a protection/HitData award/AV11/AV12/UseSkill sink or measure matched Steam hits with positive protection and raw AVSK; current direct helper evidence shows only a vector/physics-like sink and numeric ActorValue 0x24.",
            "status": "proposed", "evidence": ["EV-0600", "EV-0642", "EV-0260"],
        })
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0642"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L455"]))
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 60/tag 0x5C is a HitData-derived serialized branch to shared FUN_1406be430; continue caller 61.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state = replace_once(state, "60 of 62 initially uninspected worker callers are reviewed, with 2 remaining.",
                         "61 of 62 initially uninspected worker callers are reviewed, with 1 remaining.", "STATE main count")
    state = replace_once(state, "Q-0079 has 60/62 initially uninspected worker callers reviewed; 2 remain.",
                         "Q-0079 has 61/62 initially uninspected worker callers reviewed; 1 remains.", "STATE OBJ-2 count")
    old_summary = "EV-0641 maps caller 59/tag 0x5B to a deferred disarm-related Actor action; primary Actor slot +0x658 is FUN_14067a400 with 16 unresolved virtual sites, while its immediate producer helper follows a separate state/update path."
    new_summary = old_summary + " EV-0642 maps caller 60/tag 0x5C as a HitData-derived serialized path from FUN_1406b9df0 that rejoins shared helper FUN_1406be430; its bounded vector/physics route has no direct armor-skill sink."
    state = replace_once(state, old_summary, new_summary, "STATE caller-59 summary")
    old_next_line = next((line for line in state.splitlines() if line.startswith("**Selected next line:**")), None)
    if old_next_line is None or "caller 60/62 `FUN_140658e50`" not in old_next_line:
        raise SystemExit("STATE selected-next checkpoint mismatch")
    new_next_line = ("**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658f70 "
                     "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; "
                     "review worker caller 61/62 `FUN_140658f70` for tag/payload, producer and dispatcher route; "
                     "then inspect final caller 62/62 `FUN_140658fb0` and only close Q-0079 after the exact caller census reconciles. "
                     "Caller 60 tag 0x5C is a HitData-derived serialized branch that rejoins shared helper FUN_1406be430.")
    state = state.replace(old_next_line, new_next_line, 1)
    checkpoint = ("\n\nActive checkpoint " + now + " (`TX-20261018-0013`, Q-0079): 61/62 initially uninspected worker callers reviewed; 1 remains. "
                  "EV-0642 maps caller 60/tag 0x5C from mapped HitData handler FUN_1406b9df0 through cloned context to dispatcher target FUN_1406be2c0 and shared helper FUN_1406be430. "
                  "This is a supported HitData/helper relationship, not an armor-protection or XP result. "
                  "Next action: " + next_action)
    state += checkpoint
    write(state_path, state)
    print("Registered EV-0642/CL-L455/M-0195 and checkpointed caller 61.")


if __name__ == "__main__":
    main()
