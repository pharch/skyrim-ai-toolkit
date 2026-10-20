#!/usr/bin/env python3
"""Register the bounded Q90 HitData snapshot-to-armor-award trace."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = "TX-20261020-0009"
CAPTURE = ROOT / ".local/alignment/transactions" / TX / "q90"
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
FRONTIER_PATH = ROOT / "research/FRONTIER.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private(path: Path) -> str:
    return "private-local:" + path.relative_to(ROOT).as_posix()


def main() -> int:
    CAPTURE.mkdir(parents=True, exist_ok=True)
    query_meta_paths = [
        ROOT / ".local/ghidra/gog-query-20261020T054830Z.meta.json",
        ROOT / ".local/ghidra/gog-query-20261020T055448Z.meta.json",
        ROOT / ".local/ghidra/gog-query-20261020T055659Z.meta.json",
    ]
    query_checks = []
    artifacts: dict[str, dict[str, str]] = {}
    for meta_path in query_meta_paths:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        if not (
            meta.get("ok") is True
            and meta.get("analysis_binary_product_version") == "1.6.1179"
            and meta.get("analysis_binary_sha256") == "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
            and meta.get("read_only") is True
            and meta.get("auto_analysis_disabled") is True
            and meta.get("import_attempted") is False
            and meta.get("overwrite_attempted") is False
            and meta.get("project_created") is False
        ):
            raise SystemExit(f"GOG identity/read-only validation failed: {meta_path.name}")
        paths = [meta_path, ROOT / meta["metadata_artifact"]]
        paths.extend(ROOT / rel for rel in meta.get("artifacts", {}).values())
        for path in paths:
            if not path.is_file():
                raise SystemExit(f"missing Ghidra capture: {path}")
            artifacts[path.relative_to(ROOT).as_posix()] = {"sha256": sha(path)}
        query_checks.append({
            "metadata": meta_path.relative_to(ROOT).as_posix(),
            "requested_rva": meta.get("requested_rva"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "ok": True,
            "read_only": True,
            "auto_analysis_disabled": True,
        })

    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": TX,
        "frontier": "Q-0090",
        "build": {
            "distribution": "GOG",
            "product_version": "1.6.1179.0",
            "executable_sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "steam_target_is_separate": "EV-0109",
        },
        "scope": "Read-only GOG native dataflow for HitData builders, target-side mitigation, and the Player armor skill award; no runtime result.",
        "queries": query_checks,
        "interpretation": {
            "snapshot": "FUN_1407ddf50 copies its current +0x50 value to +0x54 before subsequent target-side armor-factor/AV39 reduction of +0x50. Some upstream builder modifiers precede this copy; +0x54 must not be described as pre-all-modifiers.",
            "award": "FUN_1406bcaa0's unblocked Player armor branch screens worn ARMO records for positive raw DNAM rating, then passes the HitData +0x54 field as the points argument to PlayerCharacter slot +0x7b8 (0xf7).",
            "scope_limit": "Selector 0x55 is used in the separate cached armor-factor path. No direct selector-0x55 call occurs in the captured builder/mitigation/award bodies. Other upstream selectors and natural runtime conditions remain separate questions.",
        },
        "artifacts": artifacts,
    }
    manifest_path = CAPTURE / "capture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0699" for item in evidence.get("items", [])):
        raise SystemExit("EV-0699 already exists")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence["items"].append({
        "id": "EV-0699",
        "captured_utc": now,
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra captures of FUN_1407ddf50, its incoming HitData builders, FUN_1407ded20, FUN_1407dd220, and FUN_1406bcaa0's Player armor-skill branch.",
        "artifact": private(manifest_path),
        "sha256": sha(manifest_path),
        "edition": "AE",
        "runtime": "GOG static analysis only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Installed Steam AE 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x7ddf50 --list-call-edges --follow-incoming-calls 32",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x7ded20 --list-call-edges --follow-incoming-calls 16",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x7dd220 --list-call-edges --follow-incoming-calls 32",
        ],
        "coverage": "The helper copies HitData +0x50 to +0x54 before later target-side armor-factor/AV39 reductions to +0x50. The Player resolver's unblocked branch performs an independent positive raw ARMO DNAM eligibility scan and passes +0x54 as the armor skill points argument. Earlier builder selectors execute before the copy, so the result is not pre-all-modifiers. Full metadata/raw hashes and build identity are in the private capture manifest.",
        "result": "PASS for the bounded GOG static call/dataflow. The selector-0x55 cache adjustment has no direct call/data edge to the +0x54 armor points argument in the captured bodies; it may still alter the separate final damage-reduction path. The broad effect of all pre-snapshot modifiers, natural hit eligibility, measured AVSK, protection, and Steam behavior remain unknown.",
        "related_evidence": ["EV-0109", "EV-0221", "EV-0222", "EV-0260", "EV-0670", "EV-0674", "EV-0690", "EV-0696", "EV-0697"],
    })
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "CL-L484" in claims or "CL-L485" in claims:
        raise SystemExit("Q90 claim ID collision")
    claims += "\n| CL-L484 | In GOG AE 1.6.1179.0, FUN_1407ddf50 copies the current HitData +0x50 value into +0x54 before its later target-side AV39/armor-factor reductions to +0x50; the unblocked Player armor-award path uses +0x54 as its points argument after a separate positive raw ARMO DNAM scan. | supported for the captured GOG static dataflow | [EV-0670], [EV-0690], [EV-0699] | Upstream builder modifiers precede this copy, and later code can independently transform fields; no live hit, effective protection, raw AVSK, Steam equivalence, or zero-XP result is established. |\n"
    claims += "| CL-L485 | The captured GOG HitData builder and mitigation helper explicitly dispatch selectors 0x1A, 0x1C, 0x00, 0x23, 0x24, 0x12, 0x01, 0x11, 0x02, 0x25, and 0x27 at distinct points; selector 0x55 is not directly dispatched in those captured bodies. | supported for the bounded direct-call bodies | [EV-0696], [EV-0699] | This does not exclude indirect helpers, other builders, dynamic entrypoint rows, or effects on shared ActorValues; Q91 screens the pre-snapshot selectors and their official records. |\n"
    claims_path.write_text(claims, encoding="utf-8")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "M-0208" in mechanisms:
        raise SystemExit("M-0208 already exists")
    mechanisms += """

## M-0208 — HitData mitigation field is distinct from the armor XP points input (EV-0670, EV-0690, EV-0699)

In the captured GOG AE 1.6.1179.0 HitData route, `FUN_1407ddf50` copies the current `+0x50` value into `+0x54`, then performs later target-side AV39/armor-factor reduction on `+0x50` [EV-0699]. The unblocked Player resolver separately scans worn ARMO items for positive raw DNAM rating; after selecting armor AV11 or AV12 it passes the `+0x54` field as the points argument through PlayerCharacter vtable slot `+0x7b8` [EV-0670], [EV-0690], [EV-0699]. The captured bodies do not directly dispatch selector `0x55` on this points field [EV-0696], [EV-0699].

This is a bounded static ordering: `+0x54` is pre target-side AV39/armor-factor reduction, but it is populated after earlier builder modifiers and later shared-field scaling can occur. It does not show that the award is positive on every hit, or that zeroing the cached armor rating leaves armor itself protective. Q91 screens earlier selectors; EV-0260 remains the Steam landed-hit/protection/raw-AVSK test. Claim CL-L484–CL-L485.
"""
    mechanisms_path.write_text(mechanisms, encoding="utf-8")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

### Q-0090 — armor mitigation and armor XP read different HitData fields (EV-0699)

The bounded GOG builder/mitigation path copies the current HitData `+0x50` value to `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The Player resolver's unblocked armor branch screens for positive raw ARMO DNAM, then passes `+0x54` to the armor skill UseSkill slot [EV-0670], [EV-0690], [EV-0699]. This supports a causal edge from builder snapshot to the armor award points argument and a separate edge from raw equipment DNAM to award eligibility.

Selector `0x55` is directly observed only in the cached per-item armor-factor path [EV-0696]; it is not explicitly dispatched in the captured HitData builder/mitigation bodies [EV-0699]. Therefore this static scope does not support selector-0x55 zeroing as a direct way to suppress the armor points input. This is not a global negative: selectors `0x1A`, `0x1C`, `0x00`, `0x23`, `0x24`, `0x12`, `0x01`, `0x11`, and `0x02` occur before the `+0x54` copy and are the subject of Q91. No live protection/AVSK result or Steam transfer is established. Claims CL-L484 and CL-L485; mechanism M-0208. The falsifier is a direct pre-snapshot/data path showing selector `0x55` or an MGEF-linked zero row changes `+0x54`, followed by a matched Steam hit with positive armor protection and raw AVSK.
"""
    graph_path.write_text(graph, encoding="utf-8")

    exp = ROOT / "experiments/EXP-0137-hitdata-presnapshot-award-link"
    (exp / "README.md").write_text("""# EXP-0137 — HitData snapshot and armor skill award

**Status:** Q90 completed as a bounded static GOG trace; Q91 continues with earlier entry-point data.

**Objective:** Determine whether selector-0x55 cached armor-rating adjustments directly change the points argument to the Player's unblocked armor-skill award.

**Build:** GOG Skyrim AE 1.6.1179.0, executable SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`. This is distinct from installed Steam AE 1.6.1170.0 [EV-0109].

**Result:** In the captured path, `FUN_1407ddf50` copies HitData `+0x50` into `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The resolver's unblocked branch checks positive raw ARMO DNAM and passes `+0x54` as the armor skill points argument. The bodies do not directly dispatch selector 0x55 on that field [EV-0670], [EV-0690], [EV-0699].

**Limit:** Earlier builder modifiers run before the copy. No live landed hit, effective protection, Steam behavior, or raw AVSK delta is measured; preserve EV-0260. This experiment provides no vanilla exploit result.
""", encoding="utf-8")
    (exp / "hypothesis.md").write_text("""# EXP-0137 hypothesis outcome

- **H1 supported:** the target-side AV39/armor-factor reduction occurs after HitData `+0x54` receives the current `+0x50`; the unblocked armor award uses `+0x54` after a distinct positive raw-DNAM eligibility scan [EV-0670], [EV-0690], [EV-0699].
- **H2 falsified for the captured direct bodies:** the award is not shown reading post-mitigation `+0x50` or directly dispatching selector 0x55 on its points input [EV-0696], [EV-0699].
- **H3 retained as an adjacent question:** `FUN_1407dd220` and `FUN_1407ded20` apply other entrypoint adjustments before the `+0x54` copy. Whether any scoped official row can zero the pre-snapshot input and what level-one effects can reach it are not resolved here; Q91 screens this path.

No causal inference from zeroing an item's cached armor factor to zero armor XP is supported by these direct code paths alone. The runtime claim still requires EV-0260's matched hit, positive protection, and raw AVSK measurement.
""", encoding="utf-8")
    (exp / "expected-discriminants.md").write_text("""# Expected discriminants — EXP-0137

| Model | Static prediction | Runtime discriminator |
|---|---|---|
| Selector 0x55 alters only the later cached armor factor | No direct 0x55 dispatch to HitData `+0x54`; award reads `+0x54`, while positive DNAM controls armor eligibility | Selector-0x55 effect can alter protection, but repeated landed hits with positive effective protection still change AV11/AV12 AVSK |
| Award uses post-mitigation totalDamage | Resolver points argument reads `+0x50` after AV39/armor-factor transforms | A trace shows points track post-mitigation `+0x50` |
| Earlier modifier zeros pre-snapshot input | One pre-snapshot selector/data path writes the field or award guard before the copy | Hit remains registered, armor protection is separately positive, and raw armor AVSK remains unchanged |

The third model needs a separate source screen and cannot be decided from the selector-0x55 callback. A zero-damage event is not by itself proof that armor supplied protection.
""", encoding="utf-8")
    (exp / "protocol.md").write_text("""# EXP-0137 protocol

## Static phase

Use the existing configured GOG project read-only and confirm ProductVersion 1.6.1179.0 plus executable hash in every metadata record. Query `FUN_1407ddf50`, its builder callers, and `FUN_1406bcaa0`; preserve the exact copy, subsequent field writes, raw DNAM guard, and slot `+0x7b8` argument. Do not interpret a GOG RVA as a Steam address. Query official source records only through the tested five-master tool route; do not claim profile winners.

## Runtime discriminator (not run)

EV-0260 requires a verified Steam 1.6.1170.0 target, exact full active order, designated disposable save, and read-only Observer. Record matched positive physical hits with no armor and with representative Light/Heavy armor; measure positive protection and raw AVSK 11/12 before and after repeated hits. Keep blocked and zero-damage controls separate. Do not use console stage/level changes, injected scripts, or altered plugins as vanilla validation.

## Capture and interpretation

Raw Ghidra metadata/stdout and query manifest remain under ignored `.local/alignment/transactions/TX-20261020-0009/q90/`. EV-0699 is mechanism inference scoped to GOG static dataflow. A direct static dependency is not a measured XP result; a live Observer read is diagnostic only until an uninstrumented vanilla sequence reproduces the candidate.
""", encoding="utf-8")
    (exp / "results.md").write_text("""# EXP-0137 results

Fresh read-only GOG AE 1.6.1179.0 captures of `FUN_1407ddf50`, `FUN_1407ded20`, and the callers show the target-side mitigation helper copies its current `+0x50` value to `+0x54`, then reduces `+0x50` through the target-side AV39/armor-factor path. The Player resolver's unblocked armor branch separately counts worn ARMO items with positive base DNAM, selects AV11 or AV12, and passes HitData `+0x54` as the skill points argument [EV-0670], [EV-0690], [EV-0699].

This `+0x54` value includes earlier builder adjustments and is not proven immutable after the copy. The captured direct bodies do not invoke selector `0x55` on the award points field. This supports the bounded model that zeroing a cache contribution does not directly zero the armor award argument; it may change the separate protection calculation. Earlier selectors before the snapshot remain open for Q91.

No live game, Steam match, measured armor protection, AVSK delta, or vanilla reproduction was performed. EV-0260 remains required.
""", encoding="utf-8")

    # Q91 is a justified successor: these are direct pre-snapshot entrypoint calls.
    frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
    items = frontier["items"]
    q90 = next(item for item in items if item["id"] == "Q-0090")
    q90["question"] = "Does the selector-0x55 cached armor-rating adjustment directly suppress the Player's hit-earned armor-skill points by changing HitData +0x54, or is that points input a separate pre-target-mitigation field after a raw-DNAM eligibility scan?"
    q90["evidence"] = list(dict.fromkeys([*q90.get("evidence", []), "EV-0699"]))
    q90["linked_claims"] = ["CL-L484", "CL-L485"]
    q90["successors"] = ["Q-0091"]
    q90["next_action"] = "Close Q90 as a bounded direct-path result, then continue with Q-0091: identify and screen all official PERK rows and handler forms for the entrypoint selectors that mutate HitData +0x50 before the +0x54 snapshot."
    q90["hypotheses"] = [
        {"id": "Q-0090-H1", "model": "The unblocked armor award uses HitData +0x54 populated before target-side AV39/armor-factor reductions; selector 0x55 has no direct write to this points input in the captured bodies.", "predicted_discriminant": "The helper writes +0x54 from +0x50 before reducing +0x50, and the resolver passes +0x54 after a separate raw-DNAM eligibility scan.", "status": "supported", "evidence": ["EV-0670", "EV-0690", "EV-0696", "EV-0699"]},
        {"id": "Q-0090-H2", "model": "The armor award uses post-mitigation +0x50 or directly dispatches selector 0x55 on the skill points argument.", "predicted_discriminant": "The resolver reads +0x50 after target mitigation or calls selector 0x55 on the points field before UseSkill.", "status": "falsified", "evidence": ["EV-0696", "EV-0699"]},
        {"id": "Q-0090-H3", "model": "An upstream builder modifier can alter +0x50 before the +0x54 copy, so selector-0x55 separation does not establish independence from every incoming-damage effect.", "predicted_discriminant": "Direct builder calls before the snapshot mutate +0x50 using selectors other than 0x55; their records/handler arithmetic require a separate screen.", "status": "supported", "evidence": ["EV-0699"]}
    ]
    q90["attempts"].append({
        "action_key": "q90-register-snapshot-and-award-path",
        "outcome": "Registered EV-0699 with three complete identity-checked GOG queries. The points field +0x54 is copied before later target-side mitigation reductions to +0x50, and the resolver supplies +0x54 after a positive raw-DNAM scan. Upstream entrypoint adjustments precede that copy, so selector-0x55 separation is only a direct-path result.",
        "evidence": ["EV-0699"],
        "new_discriminant": "The upstream pre-snapshot selectors are now explicit: 0x1A, 0x1C, 0x00, 0x23, 0x24, 0x12, 0x01, 0x11, and 0x02. Determine their primary enum names, full five-master rows, handler forms, and level-one reachability before making a broader negative claim.",
        "recorded_utc": now
    })
    if any(item.get("id") == "Q-0091" for item in items):
        raise SystemExit("Q-0091 already exists")
    items.append({
        "id": "Q-0091", "objective": "OBJ-2", "kind": "mechanism", "status": "open",
        "question": "Can any official PERK entrypoint that runs before the HitData +0x54 snapshot set or scale +0x50 to zero under a level-one-reachable effect, and would that suppress armor XP without merely proving zero incoming damage?",
        "hypotheses": [
            {"id": "Q-0091-H1", "model": "At least one of the pre-snapshot selectors has a reachable official SetValue-zero or zero-magnitude row, and its handler writes the HitData value used by armor XP.", "predicted_discriminant": "Primary CommonLib enum mapping, complete five-master selector rows, DATA[1] handler code, EPFD values, conditions, and source MGEF/PERK links identify a zero-capable path.", "status": "proposed", "evidence": ["EV-0699"]},
            {"id": "Q-0091-H2", "model": "The scoped official pre-snapshot rows do not produce a zero point input under a level-one-reachable effect; relevant rows require positive multipliers/additions or inaccessible conditions.", "predicted_discriminant": "Complete five-master denominator and source-linked conditions contain no reachable zero assignment; level-one access remains a separate record/quest question.", "status": "proposed", "evidence": ["EV-0699"]},
            {"id": "Q-0091-H3", "model": "Even if a pre-snapshot modifier zeros the award input, it also eliminates hit registration or is not armor-derived protection, so it cannot alone satisfy OBJ-2.", "predicted_discriminant": "Native event/award guards or a matched runtime with no-armor control show the event is absent or protection does not depend on the worn armor.", "status": "proposed", "evidence": ["EV-0260", "EV-0699"]}
        ],
        "methods": [
            "Read the exact CommonLib BGSEntryPoint enum and map selectors 0x1A, 0x1C, 0x00, 0x23, 0x24, 0x12, 0x01, 0x11, and 0x02 from the GOG 1.6.1179.0 HitData builder/helper before the +0x54 copy.",
            "Run a complete configured five-master PERK DATA screen for those selectors; preserve row counts, plugin hashes, handler DATA[1], EPFT, EPFD, conditions and raw MGEF/PERK links.",
            "Trace only handler bodies and candidate source effects needed to test zero input; keep record-level candidate separate from ActiveEffect lifetime and natural level-one reachability.",
            "Do not treat zero damage as protection. Preserve EV-0260 matched Steam hit, naked/equipped protection control, and raw AVSK before/after; unavailable live data does not stop this static screen."
        ],
        "blocked_by": [], "evidence": ["EV-0260", "EV-0697", "EV-0699"],
        "priority": 0.97, "information_gain": 0.91,
        "next_action": "Read the local primary CommonLib EntryPoint enum for all nine selectors and screen official PERK rows for their DATA IDs. Begin with the exact enum declaration; do not assume the legacy labels from earlier captures.",
        "linked_claims": ["CL-L465", "CL-L484", "CL-L485"], "successors": [], "attempts": []
    })
    FRONTIER_PATH.write_text(json.dumps(frontier, indent=2) + "\n", encoding="utf-8")

    # Keep the earlier experiment's Q90 note aligned with the closed direct-path result.
    q89_hypothesis = ROOT / "experiments/EXP-0136-armor-entrypoint-selector-55/hypothesis.md"
    old = q89_hypothesis.read_text(encoding="utf-8")
    marker = "## Q90 competing models\n"
    if marker in old:
        old = old.split(marker)[0]
    old += """## Q90 bounded result and Q91 continuation

In the captured GOG path, `FUN_1407ddf50` copies HitData `+0x50` to `+0x54` before later target-side AV39/armor-factor reductions to `+0x50`. The unblocked armor award uses `+0x54` after a separate positive raw-DNAM scan [EV-0670], [EV-0690], [EV-0699]. The captured bodies do not directly dispatch selector 0x55 on the points field [EV-0696], [EV-0699]. This narrows the conclusion to the direct path; upstream selectors run before the copy.

Q91 screens those pre-snapshot selectors. Neither static investigation establishes effective armor protection or zero armor XP on Steam. EV-0260 remains the matched-hit, protection, raw-AVSK discriminator.
"""
    q89_hypothesis.write_text(old, encoding="utf-8")

    print(json.dumps({
        "registered": "EV-0699",
        "manifest": private(manifest_path),
        "manifest_sha256": sha(manifest_path),
        "experiment": "EXP-0137-hitdata-presnapshot-award-link",
        "frontier_added": "Q-0091",
        "claims": ["CL-L484", "CL-L485"],
        "mechanism": "M-0208",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
