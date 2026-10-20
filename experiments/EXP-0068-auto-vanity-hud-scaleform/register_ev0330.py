#!/usr/bin/env python3
"""Register the bounded AutoVanity-to-HUD Scaleform branch under Q-0064."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0068-auto-vanity-hud-scaleform"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T012525Z", "20261018T012620Z", "20261018T012835Z", "20261018T020455Z", "20261018T020749Z",
    "20261018T020939Z", "20261018T021054Z", "20261018T021314Z",
    "20261018T021618Z", "20261018T021736Z", "20261018T021910Z",
    "20261018T022027Z", "20261018T022146Z", "20261018T022312Z",
    "20261018T022449Z",
]
MARKERS = {
    "20261018T012525Z": ["POINTER_TABLE_ENTRY=index:2", "value:0x1408E0080"],
    "20261018T012620Z": ["TARGET_RVA=0x8E0080", "FUN_140920df0(\"AutoVanity\")"],
    "20261018T012835Z": [
        "*(undefined4 *)(lVar2 + 0x10) = 0x17",
        "DAT_1420f9d58 + 0xa0", '"ShowElements"', "FUN_14091eed0",
    ],
    "20261018T020455Z": ["TARGET_RVA=0xFA5AA0", "INDIRECT_CALL_SITE_COUNT=10"],
    "20261018T021618Z": ["TARGET_RVA=0xFA6F80", "XREF_CALL_COUNT=36"],
    "20261018T021736Z": ["TARGET_RVA=0xFA7D30", "INDIRECT_CALL_SITE_COUNT=0"],
    "20261018T021910Z": ["FUN_1400b6be0", "s_HUD_Menu_1420186f0", "FUN_140928360"],
    "20261018T022027Z": ["TARGET_RVA=0x928360", "HUDMenu::vftable", "FUN_14091e290"],
    "20261018T022146Z": ["TARGET_RVA=0x91E290", "0x1418f9230", "HUDMenu::vftable"],
    "20261018T022312Z": ["POINTER_TABLE_ENTRY=index:4", "value:0x14091EED0"],
    "20261018T022449Z": ["TARGET_RVA=0xFADB20", "INDIRECT_CALL_SITE_COUNT=2", "FUN_140fab0c0"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0330" for row in evidence["items"]):
        raise SystemExit("EV-0330 already exists; refusing duplicate registration")

    hashes: dict[str, str] = {}
    records: list[dict] = []
    for stamp in STAMPS:
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if (
            meta.get("analysis_distribution") != "GOG"
            or meta.get("analysis_binary_product_version") != "1.6.1179"
            or meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("exit_code") != 0 or meta.get("ok") is not True
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("import_attempted") is not False
            or meta.get("overwrite_attempted") is not False
            or checks.get("program_identity_matches_gog_binary") is not True
            or checks.get("script_no_error") is not True
        ):
            raise SystemExit(f"identity, read-only, or completion checks failed: {stamp}")
        stdout = ROOT / meta["artifacts"]["stdout"]
        raw = stdout.read_text(encoding="utf-8", errors="replace")
        if sha(stdout) != meta.get("stdout_sha256"):
            raise SystemExit(f"stdout hash mismatch: {stamp}")
        for marker in MARKERS.get(stamp, []):
            if marker not in raw:
                raise SystemExit(f"required marker missing for {stamp}: {marker}")
        files = {"metadata": meta_path}
        for kind, relative in meta.get("artifacts", {}).items():
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing {kind} artifact for {stamp}")
            files[kind] = path
        hashes.update({path.relative_to(ROOT).as_posix(): sha(path) for path in files.values()})
        records.append({
            "stamp": stamp, "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_pointer_count": meta.get("requested_pointer_count"),
            "metadata_checks": checks, "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        })

    note = TX / "EV-0330-note.md"
    write(note, f"""# EV-0330 — AutoVanity HUD Scaleform callback branch

## Build identity and method

The existing GOG Skyrim AE 1.6.1179.0 Ghidra project identifies SkyrimSE.exe by SHA-256 {BINARY_SHA}. Fifteen bounded captures are retained with stdout, stderr, log, script-log, metadata hashes and query parameters. All report the matching GOG identity, read-only mode, automatic analysis disabled, no import or overwrite, and successful script completion. Addresses are GOG-build-only and are not transferred to Steam AE 1.6.1170.0.

## Direct observations

- The AutoVanity state callback invokes FUN_140920df0 with label `AutoVanity`. The event builder FUN_140922090 sets payload type `0x17` and queues it under outer key DAT_1420f9d58+0xA0 (HUD Menu), outer kind 0.
- The queue consumer FUN_140fa5aa0 looks up the registered outer-key handler and dispatches through the menu vtable at +0x20. Registration in FUN_1400b6be0 binds the HUD Menu key to factory FUN_140928360. That factory constructs HUDMenu; FUN_14091e290 writes the HUDMenu base vtable at absolute 0x1418f9230 (GOG RVA 0x18F9230). Its entry 4, byte offset +0x20, is FUN_14091eed0.
- FUN_14091eed0 matches the event's outer kind/key and payload type 0x17. Its case 0x17 builds UI parameters from the payload label and flag and calls FUN_140fadb20 with the Scaleform method name `ShowElements`.
- The bounded FUN_140fadb20 body obtains the GFx/Scaleform movie object and dispatches the supplied method and prepared UI values. In this callsite the optional native callback argument is zero, so its conditional FUN_140fab0c0 call is skipped. The two remaining indirect sites in that shared helper are not generalized here; the exact case-0x17 native branch contains no Actor::UseSkill or mapped AV11/AV12 skill-progress sink.

## Assessment and limits

This resolves only the AutoVanity/PlayerCamera HUD callback subbranch away from native armor-skill credit. It is not a negative result for the other PlayerCharacter teardown indirect calls or descendants; Q-0064 H1/H2 remain open. The Scaleform ActionScript implementation is not analyzed, and this is a static GOG 1.6.1179.0 result, not Steam runtime observation or a vanilla reproduction. No OBJ-1 edge is supported. No positive incoming damage, effective protection, active-profile winner, or raw AVSK measurement is established.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0330-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0330",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"distribution": "GOG", "product_version": "1.6.1179.0", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "captures": records, "private_hashes": hashes,
        "limitations": [
            "GOG 1.6.1179.0 addresses are not mapped to Steam 1.6.1170.0.",
            "The finding covers the exact AutoVanity type-0x17 HUD callback branch only.",
            "The Scaleform ActionScript implementation and other destructor indirect targets remain unresolved.",
            "No Steam runtime, effective protection, raw AVSK delta, profile winner, or vanilla reproduction is established.",
        ],
    }, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    docs = {
        "README.md": """# EXP-0068 — AutoVanity HUD callback boundary

Q-0064 follow-up that traces AutoVanity through the queued HUD event and exact HUDMenu type-0x17 callback to Scaleform `ShowElements`. EV-0330 preserves the GOG identity, capture hashes and limits. This resolves one PlayerCamera callback branch away from native armor-skill credit; the remaining teardown targets are still open.
""",
        "hypothesis.md": """# Competing models

- **Q64-H1:** captured teardown callbacks and their relevant descendants do not dispatch AV11/AV12 skill progress.
- **Q64-H2:** at least one teardown callback or descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **AutoVanity submodel A:** this callback is HUD-only native dispatch; the inspected case terminates at a Scaleform command.
- **AutoVanity submodel B:** the callback invokes a native skill-progress path on the inspected branch.

EV-0330 supports submodel A for the exact native case-0x17 branch. It does not select Q64-H1 because other indirect targets and the Scaleform script remain outside scope.
""",
        "protocol.md": """# Protocol

Use only the existing GOG AE 1.6.1179.0 project through the strict Ghidra dispatcher with analysis disabled and read-only mode. Preserve raw stdout, stderr, logs, script logs, query metadata, hashes and requested RVAs. Follow the exact AutoVanity producer, queued message, registered HUDMenu vtable slot and type-0x17 case. Do not infer Scaleform script behavior from its native invocation or transfer GOG addresses to Steam AE 1.6.1170.0.
""",
        "predicted-outcomes.md": """# Predicted outcomes

- **Supports AutoVanity submodel A:** exact event type/key registration reaches a UI command with no native skill sink or callback in the inspected branch.
- **Supports AutoVanity submodel B:** the exact branch resolves to Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.
- **Inconclusive for Q64-H1/H2:** any other teardown indirect target, descendant, or script behavior remains unresolved.
""",
        "results.md": """# Results — AutoVanity HUD dispatch

EV-0330 traces AutoVanity to queued message type 0x17 under the HUD Menu key, then through the registered HUDMenu vtable slot +0x20 to FUN_14091eed0. The exact case builds UI values and calls FUN_140fadb20 with Scaleform method `ShowElements`. For this call the optional native callback is zero. The captured native branch has no Actor skill-progress sink.

This bounds only one PlayerCamera callback branch. The Scaleform script and other teardown indirect targets are unresolved, so Q64-H1/H2 remain proposed [EV-0330], [EV-0329], [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324].
""",
        "implications.md": """# Implications

Continue Q-0064 at PlayerCharacter field +0x8F8: trace the resource returned by FUN_140e05900 through its concrete vtable and resolve FUN_140737210's final slot +0x8 target. Screen resolved descendants for Actor::UseSkill or the mapped skill-progress sink with AV11/AV12. Preserve the other PlayerCamera and PlayerCharacter indirect sites as unresolved until directly typed. Keep Steam positive-damage, effective-protection and raw-AVSK testing separate.
""",
    }
    for name, body in docs.items():
        path = EXP / name
        write(path, body)
        hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    script_hash_path = EXP / "register_ev0330.py"
    hashes[script_hash_path.relative_to(ROOT).as_posix()] = sha(script_hash_path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0330",
        "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 traces of the AutoVanity state callback, UI queue and consumer, HUD Menu registration/factory/vtable, type-0x17 handler, and Scaleform helper.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0330-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY_SHA}. Steam AE 1.6.1170.0 is separate.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Fifteen bounded identity-checked captures tracing AutoVanity to HUD message type 0x17, exact HUDMenu registration and vtable slot+0x20, and Scaleform ShowElements dispatch; the optional native callback argument is zero on this call.",
        "result": "The exact native AutoVanity type-0x17 branch is HUD Scaleform delivery and contains no Actor skill-progress sink. This resolves one callback subbranch only; other teardown targets, Scaleform script behavior, Steam runtime, positive damage, effective protection, raw AVSK, profile winner, and vanilla reproduction remain unverified.",
        "related_evidence": ["EV-0329", "EV-0328", "EV-0327", "EV-0325", "EV-0319", "EV-0324", "EV-0260"],
        "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L162 |" in claims:
        raise SystemExit("CL-L162 already exists; refusing duplicate claim")
    write(claims_path, claims.rstrip() + """
| CL-L162 | In GOG AE 1.6.1179.0, the AutoVanity state callback queues HUD message type 0x17 under the HUD Menu key; the registered HUDMenu slot +0x20 handler routes the matching payload to Scaleform ShowElements, with the optional native callback unset. The inspected native branch contains no Actor skill-progress sink. | supported (bounded build-attested GOG callback and vtable trace) | [EV-0330] | This bounds one PlayerCamera callback branch only. Other PlayerCharacter teardown indirect targets and Scaleform script behavior remain unresolved; Q64-H1/H2 stay open. No Steam runtime, zero armor XP, effective protection, raw AVSK delta, or vanilla reproduction is established. No OBJ-1 edge is supported. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "## M-0059 —" in mechanisms:
        raise SystemExit("M-0059 already exists; refusing duplicate mechanism")
    write(mechanisms_path, mechanisms.rstrip() + """

## M-0059 — AutoVanity queued HUD Scaleform branch (Q-0064)

The AutoVanity callback constructs queued message type 0x17 under the HUD Menu key. The exact HUDMenu slot+0x20 callback matches that payload and calls Scaleform ShowElements with UI values; the optional native callback argument is zero [EV-0330]. This resolves one PlayerCamera callback subbranch away from native Actor skill progress, but does not resolve other teardown callbacks, ActionScript behavior, or Q64-H1/H2. No OBJ-1 edge is supported. Claim CL-L162 -> M-0059.
""")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0330 maps the AutoVanity state callback to queued HUD message type 0x17, the registered HUDMenu slot+0x20 handler, and Scaleform ShowElements. The exact native branch has no Actor skill-progress sink and does not take its optional native callback. This is one bounded PlayerCamera callback branch; it adds no edge to AV11/AV12 skill progress and does not resolve Q64-H1/H2. Claim CL-L162 -> M-0059; no edge to OBJ-1 is supported [EV-0330].
""")

    contradictions_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradictions_path.read_text(encoding="utf-8")
    heading = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contradictions.find(heading)
    end = contradictions.find("\n## ", start + len(heading))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contradictions)
    section = contradictions[start:end]
    section = section.replace("- **Evidence:** [EV-0329]", "- **Evidence:** [EV-0330], [EV-0329]", 1)
    old = "the PlayerCharacter cleanup's global slot-0 callback uses a global initialized through FUN_1408e3f50 with a PlayerCamera::vftable object. Slot 0 targets FUN_1408e8b50 -> FUN_1408e4070. The camera cleanup body has five indirect resource calls; the primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown."
    new = "the PlayerCharacter cleanup's global slot-0 callback uses a global initialized through FUN_1408e3f50 with a PlayerCamera::vftable object. Slot 0 targets FUN_1408e8b50 -> FUN_1408e4070. EV-0330 resolves the AutoVanity HUD callback subbranch through Scaleform ShowElements with no native skill sink; the camera cleanup retains other unresolved indirect resource calls. The primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown."
    if old in section:
        section = section.replace(old, new, 1)
    else:
        anchor = "- **Current assessment:** "
        pos = section.find(anchor)
        if pos < 0:
            raise SystemExit("missing current assessment in contradiction")
        section = section[:pos] + section[pos:].replace(
            anchor,
            anchor + "EV-0330 resolves only the AutoVanity type-0x17 HUD branch to Scaleform ShowElements, with no native skill sink; other cleanup descendants remain open. ",
            1,
        )
    write(contradictions_path, contradictions[:start] + section + contradictions[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0068 / EV-0330 traces the AutoVanity HUD callback through type-0x17 dispatch to Scaleform ShowElements. This bounds one PlayerCamera callback branch away from native skill progress; Q-0064 remains active.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0330"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L162"]))
    method = "Resolve EV-0327's AutoVanity branch as bounded HUD dispatch only; continue on PlayerCharacter +0x8F8 from EV-0328 by mapping the FUN_140e05900 returned object's concrete vtable and FUN_140737210 final slot+0x8 target."
    item["methods"] = list(dict.fromkeys([*item.get("methods", []), method]))
    item["next_action"] = "Prioritize PlayerCharacter field +0x8F8: trace FUN_140736be0's FUN_140e05900 return to an exact object vtable, resolve FUN_140737210's final vtable slot +0x8 target, and screen resolved descendants for AV11/AV12 skill progress. Keep the AutoVanity HUD result scoped to EV-0330 and other teardown indirect sites unresolved."
    frontier["session_next_action"] = item["next_action"]
    frontier["next_action"] = item["next_action"]
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False) + "\n")

    log_path = ROOT / "research/SESSION_LOG.md"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n- {datetime.now(timezone.utc).isoformat(timespec='seconds')} transaction TX-20261017-0011 update: EV-0330 maps the AutoVanity type-0x17 event to the registered HUDMenu callback and Scaleform ShowElements; no native skill sink appears on this exact branch. Q64-H1/H2 remain open. Next action: resolve the +0x8F8 resource object's vtable and final slot+0x8 target.\n"
        )
    print("registered EV-0330, CL-L162, M-0059, experiment EXP-0068, and Q-0064 frontier links")
    print(f"note sha256={sha(note)}; capture manifest sha256={sha(manifest)}")


if __name__ == "__main__":
    main()
