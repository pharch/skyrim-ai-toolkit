#!/usr/bin/env python3
"""Register the caller-59/tag-0x5B disarm-related Actor action route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    ".local/ghidra/gog-query-20261019T215314Z.stdout.raw": "d58de94a262be89dc95bde73d341940dabdfa5f6afae8c6469d32f91f3df28f6",
    ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": "adf7fe696c42d26eede69497ec1ec5d1745908d4d31c206915f07e2a921492ff",
    ".local/ghidra/gog-query-20261019T215533Z.stdout.raw": "1908d3339e5d3660cf4110c886447f12dc5b1e6fc953a786ac3fb715166bb8d9",
    ".local/ghidra/gog-query-20261019T215802Z.stdout.raw": "3f78e212918f438955a4f0ce775f00b10703fb110b91e3cc843aae066c82c565",
    ".local/ghidra/gog-query-20261019T215906Z.stdout.raw": "e111a8ebe95849f093d3542fef7bd92646ecfa992a762e76507d8b5ef7de69cd",
}
METAS = {
    ".local/ghidra/gog-query-20261019T215314Z.meta.json": "568b140fe9d90d44b9de1f7743aab936701dd6833d0699a72257a721ef140820",
    ".local/ghidra/gog-query-20261019T215421Z.meta.json": "b2091e46fbe7de2af95b156f394076a0dafbb1ce9ae9b18353458ff06a50d1be",
    ".local/ghidra/gog-query-20261019T215533Z.meta.json": "badf54732b3f91a3ab3623def2f7c0409b6ac61f2fdb52873fa6b51e538739c1",
    ".local/ghidra/gog-query-20261019T215802Z.meta.json": "b8ee2d98e12fb7e9f3be9621899d51c3337167aab86635a5707117b4d564849c",
    ".local/ghidra/gog-query-20261019T215906Z.meta.json": "f78461f50ec029bff99e353f9de74cb8106cc1c5e4ea8749426110edc2ce4291",
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
        ".local/ghidra/gog-query-20261019T215314Z.stdout.raw": [
            "TARGET_RVA=0x658E10", "local_88[0] = 0x5b;",
            "caller=FUN_1405b93a0", "FUN_1405aed00(param_1,0);",
        ],
        ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": [
            "case 0x5b:", "FUN_14067aea0(lVar15,local_160);",
            "PTR_s_You_have_been_disarmed__14200cb30",
            "OUTGOING_DIRECT_CALL_EDGE_COUNT=14", "INDIRECT_CALL_SITE_COUNT=5",
        ],
        ".local/ghidra/gog-query-20261019T215533Z.stdout.raw": [
            "TARGET_RVA=0x5AED00", "DECOMPILATION_BEGIN=FUN_1405aed00",
            "FUN_1405b0730(param_1,0);", "INCOMING_CALLER_FUNCTION_COUNT=37",
        ],
        ".local/ghidra/gog-query-20261019T215802Z.stdout.raw": [
            "POINTER_TABLE_BASE_RVA=0x189F020", "POINTER_TABLE_READ_COUNT=76",
            "address:14189f278 value:0x14067A400 target:14067a400",
            "POINTER_TABLE_SCAN_COMPLETE=true",
        ],
        ".local/ghidra/gog-query-20261019T215906Z.stdout.raw": [
            "TARGET_RVA=0x67A400", "OUTGOING_DIRECT_CALL_EDGE_COUNT=25",
            "INDIRECT_CALL_SITE_COUNT=16", "DECOMPILATION_BEGIN=FUN_14067a400",
        ],
    }
    for rel, tokens in proof_sets.items():
        for token in tokens:
            if token not in raws[rel]:
                raise SystemExit(f"proof token missing from {rel}: {token}")

    note = EXP / "EV-0641-caller59-tag5b-disarm-related-actor-action.md"
    write(note, """# EV-0641 — Caller 59/tag-0x5B disarm-related Actor action

## Competing models and discriminants

- H1, deferred Actor action with a disarm-related player outcome: the tag carries two handles into an Actor method that reports “You have been disarmed.” when its receiver is the PlayerCharacter global. It predicts the exact dispatcher call and player-global message branch.
- H2, level-gate or armor-XP/protection mechanism: the event or its Actor virtual descendants directly inspect player level, start a gated quest/encounter, change effective armor protection, or reach HitData/AV11/AV12/UseSkill. It predicts a mapped direct call or producer-backed state edge to those systems; a disarm message alone does not support it.
- H3, immediate/deferred parity: the producer's immediate helper converges on the tag-0x5B handler. It predicts a direct path from FUN_1405aed00/FUN_1405b0730 to FUN_14067aea0 with equivalent resolved handle arguments.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. All query metadata confirms read-only execution, disabled auto-analysis, and matching executable identity. This build is distinct from Steam AE 1.6.1170.0; no GOG RVA is transferred to Steam.

- Caller 59 `FUN_140658e10` writes worker tag 0x5B and copies one dword from each of its two payload arguments before enqueueing through `FUN_14065b800`. Its sole analyzed direct producer is `FUN_1405b93a0`. The producer resolves the object stored at `param_1+0x50`, tests bit 13 at the resolved object's `+0xCC`, derives the two payloads through `FUN_140676b60` and `param_1+0x34`, queues tag 0x5B, then calls `FUN_1405aed00(param_1,0)` [EV-0641].
- Dispatcher case 0x5B resolves both stored dwords as object handles and calls `FUN_14067aea0(resolved_first,resolved_second)` [EV-0641]. In the successful-result branch, `FUN_14067aea0` invokes the primary Actor virtual slot `+0x658` with a form/object and context arguments, continues object/effect and manager updates, and emits the literal “You have been disarmed.” message when the first Actor pointer equals `DAT_143138a98` [EV-0641].
- The primary Actor vtable is independently identified at GOG RVA 0x189EC20 [EV-0400]. A bounded continuation capture from `0x189F020` reaches absolute table slot 0xCB (`+0x658`) at RVA 0x189F278, whose function pointer is `FUN_14067a400` [EV-0641]. That method has 25 direct call edges and 16 unresolved indirect sites. Its captured direct body contains no explicit Player-level comparison or mapped direct HitData, effective-protection, AV11/AV12, or UseSkill call [EV-0641].
- The producer's immediate `FUN_1405aed00(param_1,0)` path sets/tests state bit `0x40000` and can tail-call `FUN_1405b0730(param_1,0)`. The bounded helper/worker captures do not call `FUN_14067aea0`; direct immediate/deferred handler convergence is therefore not established. `FUN_1405aed00` has 37 analyzed incoming caller functions, so its meaning is broader than this producer [EV-0641].

## Result and limits

H1 is supported for the captured deferred route: the PlayerCharacter branch's explicit message identifies a disarm-related outcome, and the dispatch target applies a primary Actor virtual operation. H3 is not supported by the bounded direct path; the immediate helper performs separate state/update work. H2 has no mapped direct level, quest-start, HitData, protection, AV11/AV12, or UseSkill edge in the captured bodies, but 16 virtual sites in `FUN_14067a400`, deeper descendants, and runtime effects remain unresolved. This is not a vanilla level-one bypass, armor-XP result, effective-protection result, Steam result, or bounty resolution. No OBJ-1/OBJ-2 causal edge is added.

## Next action

Continue the exact worker-caller census at caller 60/62, `FUN_140658e50`; prioritize explicit level/quest and armor protection/skill discriminants while retaining the two remaining uninspected callers and Q-0079's independent open status.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ids = {row.get("id") for row in evidence.get("items", [])}
    if not {"EV-0400", "EV-0637", "EV-0640", "EV-0260"} <= ids:
        raise SystemExit("missing contextual evidence")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    record = {
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0641", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 59/tag 0x5B, producer, dispatcher/receiver, Actor slot 0xCB, and producer immediate state/update path.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T215314Z.stdout.raw",
        "sha256": CAPTURES[".local/ghidra/gog-query-20261019T215314Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries with auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge and Actor-vtable queries"],
        "coverage": "Tag-0x5B builder/sole analyzed producer/dispatcher; two resolved object handles; disarm message branch; primary Actor slot 0xCB/FUN_14067a400; 25 direct calls and 16 unresolved virtual sites; immediate FUN_1405aed00/FUN_1405b0730 state path.",
        "result": "The deferred route supports a disarm-related PlayerCharacter outcome through a primary Actor virtual operation. The producer's immediate helper follows a separate state/update path with no captured direct convergence. No explicit level check or mapped direct HitData/protection/AV11/AV12/UseSkill sink appears in the bounded bodies; unresolved virtual descendants and runtime effects remain open.",
        "local_hashes": local_hashes, "related_evidence": ["EV-0400", "EV-0637", "EV-0640", "EV-0260"],
    }
    if "EV-0641" not in ids:
        evidence["items"].append(record)
        write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L454 |",
        "| CL-L454 | In GOG AE 1.6.1179.0, caller 59/tag 0x5B resolves two object handles and reaches a successful PlayerCharacter branch that emits “You have been disarmed.” through FUN_14067aea0; its primary Actor slot +0x658 maps to FUN_14067a400. | supported for captured deferred route | [EV-0400], [EV-0641] | The Actor method has 16 unresolved virtual sites and downstream/runtime effects remain open; the producer's immediate FUN_1405aed00/FUN_1405b0730 route does not show direct convergence. No level-one, armor protection, armor-XP, Steam, or bounty result follows. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0194 —",
        """## M-0194 — Tag-0x5B deferred disarm-related Actor action (EV-0641)

Caller 59 `FUN_140658e10` writes tag 0x5B with two dwords; sole analyzed producer `FUN_1405b93a0` emits it when the object at `param_1+0x50` resolves and its `+0xCC` bit 13 is set. It derives the payloads from `FUN_140676b60` and `param_1+0x34`, queues the event, then calls `FUN_1405aed00(param_1,0)` [EV-0641]. Dispatcher case 0x5B resolves both dwords as handles and calls `FUN_14067aea0`. On a successful result that function calls primary Actor slot +0x658 and, when its first Actor pointer is the PlayerCharacter global, emits “You have been disarmed.” [EV-0400], [EV-0641].

The Actor table slot +0x658 is slot 0xCB and resolves to `FUN_14067a400`; its complete captured body has 25 direct edges and 16 unresolved virtual sites. No explicit level check or mapped direct HitData/protection/AV11/AV12/UseSkill sink appears in the bounded bodies [EV-0641]. The immediate producer helper sets/tests bit `0x40000` and may call `FUN_1405b0730(param_1,0)`; no direct convergence with the deferred receiver is captured, so keep immediate state/update and deferred Actor action as separate routes. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L454.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q79-TAG5B-DISARM-VS-HIT-ARMOR",
        """## C-OBJ2-Q79-TAG5B-DISARM-VS-HIT-ARMOR — deferred disarm action versus armor/XP route

- Model A: tag 0x5B is a deferred Actor action with a disarm-related PlayerCharacter outcome. The receiver calls Actor slot +0x658 and emits the explicit disarm message on the PlayerCharacter branch.
- Model B: the producer/Actor descendants directly implement level-gated access, effective armor protection, or zero armor XP while retaining protection.
- Model C: the producer's immediate helper is equivalent to the deferred handler.
- Evidence: tag builder, producer, case 0x5B, receiver, Actor slot 0xCB map, and `FUN_1405aed00`/`FUN_1405b0730` captures [EV-0400], [EV-0641].
- Assessment: A is supported for the bounded deferred route. B has no mapped direct level/quest/HitData/protection/AV11/AV12/UseSkill edge; 16 Actor virtual sites, deeper descendants, and runtime remain unresolved. C is unsupported by the captured direct path: immediate state/update work does not directly call `FUN_14067aea0`. No OBJ-1/OBJ-2 causal edge is added.
- Discriminant: continue remaining worker callers; only extend this branch if a producer-backed virtual descendant maps to an exact level, protection, HitData, AV11/AV12, or UseSkill primitive, or if a clean Steam matched-hit test measures protection and armor XP.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0641 maps caller 59 tag-0x5B disarm-related Actor action",
        """### EV-0641 maps caller 59 tag-0x5B disarm-related Actor action

Caller 59's producer queues two object handles under an object bit-13 gate, then runs a separate immediate state/update helper. Deferred case 0x5B resolves both handles, applies a primary Actor slot +0x658 operation, and emits “You have been disarmed.” for the PlayerCharacter branch [EV-0400], [EV-0641]. The actor method retains 16 unresolved virtual sites. This connects to the shared Actor table identity and worker transport only; no causal edge to OBJ-1 level gates, HitData protection, AV11/AV12, or armor XP is established. Claim mapping: CL-L454 -> M-0194; no OBJ-1/OBJ-2 graph edge.""")
    append_once(EXP / "results.md", "### Caller 59/62: tag-0x5B disarm-related Actor action (EV-0641)",
        """### Caller 59/62: tag-0x5B disarm-related Actor action (EV-0641)

Caller 59 writes tag 0x5B with two dwords. Its producer queues them when a resolved object's +0xCC bit 13 is set, then invokes `FUN_1405aed00(param_1,0)`. Dispatcher case 0x5B resolves both payloads and calls `FUN_14067aea0`; its successful PlayerCharacter branch emits “You have been disarmed.” and calls primary Actor slot +0x658/FUN_14067a400 [EV-0400], [EV-0641]. That Actor method has 25 direct calls and 16 unresolved virtual sites. The producer's immediate helper instead updates bit `0x40000` and may call `FUN_1405b0730(param_1,0)`; direct convergence is not shown. The bounded captures show no explicit level check or direct mapped HitData/protection/AV11/AV12/UseSkill sink. No OBJ-1/OBJ-2 causal edge is added. Continue caller 60/62 FUN_140658e50.""")
    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 caller 59 (EV-0641)",
        """## Cross-domain synthesis — Q-0079 caller 59 (EV-0641)

The latest callers occupy distinct systems: caller 56 removes matching perk-rank entries, caller 57 adds/updates rank pairs under a perk rank-count bound, caller 58 maintains handle-keyed coordinates with Actor/physics producers, and caller 59 dispatches a disarm-related Actor action [EV-0638]–[EV-0641]. The shared worker is transport infrastructure; no common receiver, progression gate, HitData field, protection calculation, or armor-skill writer links these routes. Caller 59's explicit PlayerCharacter message makes the disarm outcome the supported model, while 16 Actor virtual sites and runtime descendants remain open. No OBJ-1/OBJ-2 causal edge is added. Continue caller 60/62 FUN_140658e50; retain the clean Steam protection/raw-AVSK discriminator [EV-0260].""")

    next_action = ("Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658e50 "
                   "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
                   "review worker caller 60/62 FUN_140658e50 for its exact tag/payload, producer and dispatcher route; "
                   "prioritize explicit level/quest and armor protection/skill discriminants, then continue caller 61/62.")
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    known = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H159" not in known:
        item["hypotheses"].append({
            "id": "Q79-H159",
            "model": "Caller 59 tag 0x5B is a deferred Actor action with a disarm-related PlayerCharacter outcome; its producer's immediate helper is separate state/update work.",
            "predicted_discriminant": "The tag-0x5B dispatcher receiver, Actor slot +0x658 identity and explicit PlayerCharacter disarm message support the deferred-action model; immediate-path convergence requires a direct data/control edge not shown in the bounded captures.",
            "status": "supported", "evidence": ["EV-0400", "EV-0641"],
        })
    if "Q79-H160" not in known:
        item["hypotheses"].append({
            "id": "Q79-H160",
            "model": "Caller 59 or its Actor descendants directly alter level-one quest eligibility, effective armor protection, or hit-earned armor XP while preserving protection.",
            "predicted_discriminant": "A producer-backed path must reach an explicit level/quest gate, effective-protection calculation, HitData, AV11/AV12, or UseSkill sink; current direct bodies show none and 16 Actor virtual sites remain unresolved.",
            "status": "proposed", "evidence": ["EV-0641", "EV-0260"],
        })
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0641"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L454"]))
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 59/tag 0x5B supports a deferred disarm-related Actor action; immediate state/update path remains distinct; continue caller 60.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state = replace_once(state, "59 of 62 initially uninspected worker callers are reviewed, with 3 remaining.",
                         "60 of 62 initially uninspected worker callers are reviewed, with 2 remaining.", "STATE main count")
    state = replace_once(state, "Q-0079 has 59/62 initially uninspected worker callers reviewed; 3 remain.",
                         "Q-0079 has 60/62 initially uninspected worker callers reviewed; 2 remain.", "STATE OBJ-2 count")
    old_summary = "EV-0640 maps caller 58/tag 0x5A to handle-keyed coordinate/physics state; Actor slot 0x9C is one producer and 13 manager virtual sites remain open, with no mapped direct HitData/armor sink."
    new_summary = old_summary + " EV-0641 maps caller 59/tag 0x5B to a deferred disarm-related Actor action; primary Actor slot +0x658 is FUN_14067a400 with 16 unresolved virtual sites, while its immediate producer helper follows a separate state/update path."
    state = replace_once(state, old_summary, new_summary, "STATE caller-58 summary")
    old_next_line = next((line for line in state.splitlines() if line.startswith("**Selected next line:**")), None)
    if old_next_line is None or "caller 59/62 `FUN_140658e10`" not in old_next_line:
        raise SystemExit("STATE selected-next checkpoint mismatch")
    new_next_line = ("**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658e50 "
                     "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; "
                     "review worker caller 60/62 `FUN_140658e50` for its exact tag/payload, producer and dispatcher route; "
                     "prioritize explicit level/quest and armor protection/skill discriminants, then continue caller 61/62. "
                     "Caller 59 tag 0x5B is a deferred disarm-related Actor action; its immediate state/update path does not show direct convergence.")
    state = state.replace(old_next_line, new_next_line, 1)
    state = replace_once(state, "# Current research state — 2026-10-19", "# Current research state — 2026-10-20", "STATE date")
    checkpoint = ("\n\nActive checkpoint " + now + " (`TX-20261018-0013`, Q-0079): 60/62 initially uninspected worker callers reviewed; 2 remain. "
                  "EV-0641 maps caller 59/tag 0x5B to a deferred disarm-related Actor action; Actor slot +0x658 resolves to FUN_14067a400 with 16 unresolved virtual sites. "
                  "The producer's immediate FUN_1405aed00/FUN_1405b0730 path is separate in the captured direct route. No level-one or armor-XP/protection result is established. "
                  "Next action: " + next_action)
    state += checkpoint
    write(state_path, state)
    print("Registered EV-0641/CL-L454/M-0194 and checkpointed caller 60.")


if __name__ == "__main__":
    main()
