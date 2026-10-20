#!/usr/bin/env python3
"""Register caller 61/tag 0x61 as an eye-texture replacement route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    ".local/ghidra/gog-query-20261019T220705Z.stdout.raw": "03e9e4bde1e1c7a09a370186b46de50494de93ef67630eb457f7ef67035c5fc6",
    ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": "adf7fe696c42d26eede69497ec1ec5d1745908d4d31c206915f07e2a921492ff",
}
METAS = {
    ".local/ghidra/gog-query-20261019T220705Z.meta.json": "4f9dd6384543fac78b80fd4d8bd938dc3b888cdcd2e2fc2f870aa9e9f010266c",
    ".local/ghidra/gog-query-20261019T215421Z.meta.json": "b2091e46fbe7de2af95b156f394076a0dafbb1ce9ae9b18353458ff06a50d1be",
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
        ".local/ghidra/gog-query-20261019T220705Z.stdout.raw": [
            "TARGET_RVA=0x658F70", "local_88[0] = 0x61;",
            "INCOMING_CALLER_FUNCTION_COUNT=1", "FUN_140658f70(DAT_14319a7c0,lVar1,param_4);",
        ],
        ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": [
            "case 0x61:", "DAT_14332c3a0", "DAT_14332c3d8",
            "FUN_1414ae320(plVar8,plVar14);", "FUN_1414ae4c0(plVar8,plVar14);",
        ],
    }
    for rel, tokens in proof_sets.items():
        for token in tokens:
            if token not in raws[rel]:
                raise SystemExit(f"proof token missing from {rel}: {token}")

    note = EXP / "EV-0643-caller61-tag61-eye-texture-replacement.md"
    write(note, """# EV-0643 — Caller 61/tag-0x61 eye-texture replacement

## Competing models and discriminants

- H1, render/texture update: caller 61 queues a retained object and texture payload; its producer reaches the builder only after finding eye headpart geometry, and dispatcher case 0x61 replaces a nested texture pointer for two recognized object-type identities. It predicts the producer strings, tag, object/texture payload, and nested pointer update.
- H2, level-gated quest/encounter or HitData/armor-skill route: the payload or consumer also gates level-one content or reaches effective protection, HitData, AV11/AV12, or UseSkill. It predicts an explicit gate or mapped producer-backed edge; a shared worker queue alone is insufficient.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This project is distinct from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 61 `FUN_140658f70` writes tag 0x61, retains its object argument by incrementing its reference count, stores the supplied second payload, and queues through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1409ebcb0` [EV-0643].
- The producer reports errors when the TextureSet is null, the target has no 3D, there are no eye-tagged headparts, or eye geometry cannot be found. On success, it resolves a texture-related value from the passed TextureSet and eye headpart, resolves the eye geometry, then queues tag 0x61 with the geometry object and supplied TextureSet [EV-0643].
- Dispatcher case 0x61 reads the two payloads, checks an object stored at receiver `+0x25` against two exact type-identity pointers (`DAT_14332c3a0` and `DAT_14332c3d8`), resolves the supplied value with `FUN_140326ef0`, replaces a nested pointer at `+0x78` when it differs, then calls a nested virtual slot +0x48 and three geometry/resource helpers [EV-0643]. The type identities and deeper rendering behavior remain unnamed.
- The builder has one direct outgoing call and the producer/dispatcher bodies show no explicit player-level predicate or mapped direct HitData, effective-protection, AV11/AV12, or UseSkill operation [EV-0643]. This is a bounded direct-body result, not a transitive or runtime negative.

## Result and limits

H1 is supported as an eye-geometry texture replacement route. H2 is unsupported by the captured direct producer and dispatcher bodies: no level, quest-start, HitData, protection, AV11/AV12, or UseSkill edge appears. Dynamic type descendants and runtime scheduling remain open. This is not a level-one bypass, armor-XP result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Inspect the final exact worker caller 62/62, `FUN_140658fb0`, then reconcile the complete 62-body census and reselect an independent P0 line; caller completion does not resolve the bounty.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ids = {row.get("id") for row in evidence.get("items", [])}
    if not {"EV-0642", "EV-0637", "EV-0260"} <= ids:
        raise SystemExit("missing contextual evidence")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    record = {
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0643", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 61/tag 0x61, sole producer and dispatcher case.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T220705Z.stdout.raw",
        "sha256": CAPTURES[".local/ghidra/gog-query-20261019T220705Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries with auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge query"],
        "coverage": "Tag-0x61 builder and sole direct producer; TextureSet/eye headpart geometry conditions; dispatcher type-identity guard, nested texture-pointer replacement and geometry/resource callbacks.",
        "result": "Caller 61/tag 0x61 maps to an eye-headpart geometry texture replacement path. The bounded direct producer and consumer show no explicit level/quest gate or mapped HitData/protection/AV11/AV12/UseSkill sink; dynamic descendants and runtime behavior remain unresolved.",
        "local_hashes": local_hashes, "related_evidence": ["EV-0637", "EV-0642", "EV-0260"],
    }
    if "EV-0643" not in ids:
        evidence["items"].append(record)
        write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L456 |",
        "| CL-L456 | In GOG AE 1.6.1179.0, caller 61/tag 0x61 is produced by FUN_1409ebcb0 after resolving eye-headpart geometry and a supplied TextureSet; dispatcher case 0x61 checks two object type identities and conditionally replaces a nested texture pointer. | supported for the captured eye-texture route | [EV-0643] | Type identities, dynamic geometry descendants, and runtime behavior remain open; no level-one, quest, HitData, effective-protection, AV11/AV12, UseSkill, Steam, or bounty result follows. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0196 —",
        """## M-0196 — Tag-0x61 eye-headpart texture replacement (EV-0643)

Caller 61 `FUN_140658f70` retains an object, stores a supplied TextureSet-like payload, and queues tag 0x61. Its sole analyzed producer `FUN_1409ebcb0` checks for target 3D and eye-tagged headparts, resolves eye geometry, then queues that geometry with the supplied TextureSet [EV-0643]. Dispatcher case 0x61 checks the object's nested `+0x25` member against two untyped identity pointers, resolves the new texture value, swaps a nested `+0x78` pointer when different, and invokes a virtual +0x48 callback plus geometry/resource helpers [EV-0643]. This supports a render/texture-update interpretation; exact types and dynamic callbacks remain unresolved. No level-gate, HitData, protection, AV11/AV12, UseSkill, or armor-XP edge is established. No OBJ-1/OBJ-2 edge is added. Claim CL-L456.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q79-TAG61-EYE-TEXTURE-VS-PROGRESSION-COMBAT",
        """## C-OBJ2-Q79-TAG61-EYE-TEXTURE-VS-PROGRESSION-COMBAT — rendering update versus quest/armor route

- Model A: tag 0x61 replaces an eye-headpart geometry texture after producer-side 3D/headpart/geometry checks.
- Model B: the tag is a level-one access, HitData, effective-protection, or armor-skill route.
- Evidence: caller builder, sole producer, dispatcher type-identity guard and nested texture pointer update [EV-0643].
- Assessment: A is supported for the captured static route. B has no explicit level/quest predicate or mapped direct HitData/protection/AV11/AV12/UseSkill sink. Unresolved virtual/resource descendants and runtime behavior remain open. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: keep B closed unless a producer-backed descendant reaches a mapped quest gate, protection calculation, HitData, AV11/AV12 or UseSkill primitive.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0643 maps caller 61 tag-0x61 eye texture update",
        """### EV-0643 maps caller 61 tag-0x61 eye texture update

Caller 61's producer validates a target 3D, eye-tagged headparts, and eye geometry, then sends a geometry/TextureSet pair through tag 0x61 [EV-0643]. The dispatcher conditionally replaces a nested texture pointer and invokes geometry/resource callbacks. This follows caller 60's HitData-derived shared helper as an independent rendering system; the worker is shared transport, not a gameplay cause. No OBJ-1/OBJ-2 causal edge is established. Claim mapping: CL-L456 -> M-0196.""")
    append_once(EXP / "results.md", "### Caller 61/62: tag-0x61 eye-texture update (EV-0643)",
        """### Caller 61/62: tag-0x61 eye-texture update (EV-0643)

Caller 61 writes tag 0x61, retains its object argument, and stores a supplied second payload. Its sole producer reports failures for missing TextureSet, 3D, eye-tagged headparts, or geometry; success queues the resolved eye geometry with the supplied TextureSet. Dispatcher case 0x61 checks two object-type identity pointers, conditionally replaces a nested +0x78 texture pointer, then calls a nested virtual callback and three geometry/resource helpers [EV-0643]. The bounded path shows no explicit level/quest predicate or direct HitData/protection/AV11/AV12/UseSkill edge. No OBJ-1/OBJ-2 causal edge is added. Continue final caller 62/62 FUN_140658fb0.""")
    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 caller 61 (EV-0643)",
        """## Cross-domain synthesis — Q-0079 caller 61 (EV-0643)

Caller 60 is a HitData-derived event that rejoins a vector/physics-like helper; caller 61 is an independent eye-headpart texture replacement after geometry validation [EV-0642], [EV-0643]. Both use the worker queue, but no shared receiver, progression state, damage record, armor protection, or skill writer links them. This separates transport reuse from a causal gameplay relation. No OBJ-1/OBJ-2 edge is added. Inspect final caller 62/62 FUN_140658fb0 and reconcile the exact inventory.""")

    next_action = ("Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658fb0 "
                   "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
                   "inspect final worker caller 62/62 FUN_140658fb0, then reconcile all 62 initially uninspected caller bodies and their direct tags before closing Q-0079.")
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    known = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H163" not in known:
        item["hypotheses"].append({
            "id": "Q79-H163",
            "model": "Caller 61/tag 0x61 is an eye-headpart geometry texture replacement through two guarded object identities.",
            "predicted_discriminant": "The producer's eye-geometry checks, tag payload and dispatcher nested texture-pointer replacement support the render/update route.",
            "status": "supported", "evidence": ["EV-0643"],
        })
    if "Q79-H164" not in known:
        item["hypotheses"].append({
            "id": "Q79-H164",
            "model": "Caller 61 or a dynamic texture callback changes level-one quest eligibility, effective armor protection, or armor-skill XP.",
            "predicted_discriminant": "A producer-backed descendant must reach a level/quest gate, protection calculation, HitData, AV11/AV12 or UseSkill; current bounded bodies show a nested texture update and no such direct edge.",
            "status": "proposed", "evidence": ["EV-0643", "EV-0260"],
        })
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0643"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L456"]))
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 61/tag 0x61 is bounded as eye-headpart texture replacement; inspect and reconcile final caller 62.",
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
    old_summary = "EV-0642 maps caller 60/tag 0x5C as a HitData-derived serialized path from FUN_1406b9df0 that rejoins shared helper FUN_1406be430; its bounded vector/physics route has no direct armor-skill sink."
    new_summary = old_summary + " EV-0643 maps caller 61/tag 0x61 to an eye-headpart texture update through a guarded nested pointer replacement; caller 62 remains to be inspected before closing the exact census."
    state = replace_once(state, old_summary, new_summary, "STATE caller-60 summary")
    old_next_line = next((line for line in state.splitlines() if line.startswith("**Selected next line:**")), None)
    if old_next_line is None or "caller 61/62 `FUN_140658f70`" not in old_next_line:
        raise SystemExit("STATE selected-next checkpoint mismatch")
    new_next_line = ("**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658fb0 "
                     "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; "
                     "inspect final worker caller 62/62 `FUN_140658fb0`, then reconcile all 62 initially uninspected caller bodies and their direct tags before closing Q-0079. "
                     "Caller 61 tag 0x61 is an eye-headpart geometry texture update.")
    state = state.replace(old_next_line, new_next_line, 1)
    checkpoint = ("\n\nActive checkpoint " + now + " (`TX-20261018-0013`, Q-0079): 61/62 initially uninspected worker callers reviewed; 1 remains in the planned inventory. "
                  "EV-0643 maps caller 61/tag 0x61 to guarded eye-headpart texture replacement. This is independent of caller 60's HitData-derived vector/helper branch and adds no OBJ-1/OBJ-2 edge. "
                  "Next action: " + next_action)
    state += checkpoint
    write(state_path, state)
    print("Registered EV-0643/CL-L456/M-0196 and checkpointed final caller 62.")


if __name__ == "__main__":
    main()
