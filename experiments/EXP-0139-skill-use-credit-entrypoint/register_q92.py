#!/usr/bin/env python3
"""Register Q92's GOG skill-credit path and five-master AVIF/EP22 results."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX = "TX-20261020-0011"
CAPTURE = ROOT / ".local/alignment/transactions" / TX / "q92"
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
FRONTIER_PATH = ROOT / "research/FRONTIER.json"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
COMMONLIB_COMMIT = "b93280e832f263dbef44e44cbe2936622a02f91a"
PLUGINS = ["Skyrim.esm", "Update.esm", "Dawnguard.esm", "HearthFires.esm", "Dragonborn.esm"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private(path: Path) -> str:
    return "private-local:" + path.relative_to(ROOT).as_posix()


def main() -> int:
    ghidra_meta_path = ROOT / ".local/ghidra/gog-query-20261020T062010Z.meta.json"
    ghidra_meta = json.loads(ghidra_meta_path.read_text(encoding="utf-8"))
    if not (
        ghidra_meta.get("ok") is True
        and ghidra_meta.get("analysis_binary_product_version") == "1.6.1179"
        and ghidra_meta.get("analysis_binary_sha256") == BINARY_SHA
        and ghidra_meta.get("requested_rva") == "0x77D090"
        and ghidra_meta.get("read_only") is True
        and ghidra_meta.get("auto_analysis_disabled") is True
        and ghidra_meta.get("import_attempted") is False
        and ghidra_meta.get("overwrite_attempted") is False
        and ghidra_meta.get("project_created") is False
    ):
        raise SystemExit("Q92 GOG identity/read-only checks failed")
    capture_json = CAPTURE / "skill-avif-records.json"
    avif = json.loads(capture_json.read_text(encoding="utf-8"))
    if avif.get("source_commit") != COMMONLIB_COMMIT or avif.get("AVIF_total") != 153:
        raise SystemExit("Q92 AVIF source/count mismatch")
    plugin_hashes = avif.get("plugin_sha256", {})
    if list(plugin_hashes) != PLUGINS:
        raise SystemExit("Q92 official master set/order changed")
    target_values = {}
    for row in avif.get("HeavyLight_EditorID_candidates", []):
        if row.get("editor_id") in {"AVHeavyArmor", "AVLightArmor"} and row.get("AVSK"):
            target_values[row["editor_id"]] = row["AVSK"].get("decoded_four_floats")
    if target_values.get("AVHeavyArmor") != [3.799999952316284, 0.0, 2.0, 0.0] or target_values.get("AVLightArmor") != [4.0, 0.0, 2.0, 0.0]:
        raise SystemExit("Q92 Heavy/Light AVSK values changed")

    ep22_path = ROOT / ".local/alignment/transactions/TX-20261016-0002/perk_skill_use_screen.json"
    ep22 = json.loads(ep22_path.read_text(encoding="utf-8"))
    ep22_rows = [row for plugin in ep22.get("plugins", []) for row in plugin.get("entrypoint22_record_rows", [])]
    if len(ep22_rows) != 8 or any(row.get("effect", {}).get("epfd_float", 0.0) <= 0.0 for row in ep22_rows):
        raise SystemExit("Q92 EP22 screen does not have eight positive rows")

    xedit_specs = [
        ("AVHeavyArmor", ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T062358.055991Z"),
        ("AVLightArmor", ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T062639.132906Z"),
    ]
    xedit_checks = {}
    for editor_id, directory in xedit_specs:
        result_path = directory / "native-result.json"
        tsv_path = directory / "native-records.tsv"
        if not result_path.is_file() or not tsv_path.is_file():
            raise SystemExit(f"missing native xEdit export for {editor_id}")
        result = json.loads(result_path.read_text(encoding="utf-8"))
        if result.get("loader_status") != "Background Loader: finished" or result.get("record", {}).get("editor_id") != editor_id:
            raise SystemExit(f"native xEdit result did not validate for {editor_id}")
        if result.get("plugins") != PLUGINS or len(result.get("native_data_files", [])) != 5:
            raise SystemExit(f"native xEdit scope differs for {editor_id}")
        skill_fields = [row for row in result.get("fields", []) if row.get("field_path", "").startswith("AVIF\\5:AVSK - Skill\\")]
        expected_use = "3.800000" if editor_id == "AVHeavyArmor" else "4.000000"
        expected_offset = "0.000000"
        if not any(row.get("field_path", "").endswith("Skill Use Mult") and row.get("value") == expected_use for row in skill_fields):
            raise SystemExit(f"native xEdit use multiplier differs for {editor_id}")
        if not any(row.get("field_path", "").endswith("Skill Offset Mult") and row.get("value") == expected_offset for row in skill_fields):
            raise SystemExit(f"native xEdit use offset differs for {editor_id}")
        xedit_checks[editor_id] = {
            "result": result_path.relative_to(ROOT).as_posix(),
            "result_sha256": sha(result_path),
            "tsv": tsv_path.relative_to(ROOT).as_posix(),
            "tsv_sha256": sha(tsv_path),
            "capture": result.get("capture"),
            "field_count": result.get("field_count"),
            "record": result.get("record"),
            "native_data_files": result.get("native_data_files"),
        }

    captures: dict[str, dict[str, str]] = {capture_json.relative_to(ROOT).as_posix(): {"sha256": sha(capture_json)}}
    captures[ep22_path.relative_to(ROOT).as_posix()] = {"sha256": sha(ep22_path)}
    skill_note = ROOT / ".local/alignment/transactions/TX-20261016-0002/skill_advance_record_screen.md"
    captures[skill_note.relative_to(ROOT).as_posix()] = {"sha256": sha(skill_note)}
    for relative in ghidra_meta.get("artifacts", {}).values():
        path = ROOT / relative
        if not path.is_file():
            raise SystemExit(f"missing Ghidra artifact: {relative}")
        captures[relative] = {"sha256": sha(path)}
    captures[ghidra_meta_path.relative_to(ROOT).as_posix()] = {"sha256": sha(ghidra_meta_path)}
    for paths in xedit_checks.values():
        for key in ("result", "tsv"):
            path = ROOT / paths[key]
            captures[path.relative_to(ROOT).as_posix()] = {"sha256": sha(path)}
        capture_rel = paths.get("capture")
        if capture_rel:
            capture_dir = ROOT / capture_rel
            for path in sorted(capture_dir.iterdir()):
                if path.is_file():
                    captures[path.relative_to(ROOT).as_posix()] = {"sha256": sha(path)}

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    manifest = {
        "captured_utc": now,
        "transaction": TX,
        "frontier": "Q-0092",
        "analysis_build": {"distribution": "GOG", "product_version": "1.6.1179.0", "executable_sha256": BINARY_SHA, "installed_steam_runtime": "separate 1.6.1170.0 target [EV-0109]; no RVA transfer"},
        "scope": "Read-only GOG progression helper/caller query, CommonLib field/selector provenance, all five-master AVIF record screen, two native xEdit AVIF exports, and prior complete EP22 record screen. No gameplay or active profile winner.",
        "ghidra_query": {"metadata": ghidra_meta_path.relative_to(ROOT).as_posix(), "requested_rva": ghidra_meta.get("requested_rva"), "checks": ghidra_meta.get("checks"), "stdout_sha256": ghidra_meta.get("stdout_sha256")},
        "commonlib_source": {"commit": COMMONLIB_COMMIT, "actor_value_info_header": avif.get("source_headers", {}).get("actor_value_info"), "actor_values_header": avif.get("source_headers", {}).get("actor_values"), "entry_point_enum_source": "EV-0700 CommonLibSSE BGSEntryPoint.h; decimal 22 is kModSkillUse"},
        "record_scope": {"plugin_sha256": plugin_hashes, "avif_record_count_by_plugin": avif.get("AVIF_record_count_by_plugin"), "avif_total": avif.get("AVIF_total"), "heavy_light_avsk": target_values, "ep22_row_count": len(ep22_rows), "ep22_amounts_all_positive": True, "ep22_artifact": ep22_path.relative_to(ROOT).as_posix()},
        "native_xedit": xedit_checks,
        "artifacts": captures,
        "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0262", "EV-0683", "EV-0700", "EV-0699"],
    }
    manifest_path = CAPTURE / "capture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    if any(item.get("id") in {"EV-0703", "EV-0704"} for item in evidence.get("items", [])):
        raise SystemExit("Q92 evidence ID collision")
    evidence["items"].extend([
        {
            "id": "EV-0703", "captured_utc": now, "kind": "native",
            "source": "Fresh read-only GOG Ghidra query of FUN_14077d090 and its direct callers/callees for skill-credit transformation and progress-store order.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "GOG analysis build ProductVersion 1.6.1179.0, executable SHA-256 " + BINARY_SHA + "; installed Steam AE 1.6.1170.0 is separate [EV-0109].",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x77d090 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 240"],
            "coverage": "Function lookup, direct/incoming call edges, disassembly and decompilation passed on the existing read-only GOG project. The captured helper loads per-skill AVIF Skill fields, invokes selector 0x16 on the credit float, adds the returned value to a skill progress field, and enters the threshold loop; one direct caller is the PlayerCharacter UseSkill wrapper.",
            "result": "In the captured path, the wrapper rejects points unless strictly positive before calling the helper. The helper then dispatches selector decimal 22 / hex 0x16 (CommonLib kModSkillUse) against a float before adding it to the per-skill progress field. This establishes a distinct award-side numeric control point after the positive input gate, not a zero source or protection result.",
            "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0683", "EV-0700"],
        },
        {
            "id": "EV-0704", "captured_utc": now, "kind": "record",
            "source": "Read-only direct TES4 AVIF/AVSK screen across five official masters, pinned CommonLib ActorValueInfo schema, exact native xEdit AVIF exports for Heavy/Light Armor, and the complete prior official five-master PERK EntryPoint 22 screen.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "Installed official-master source scope; exact five-master native xEdit exports. No selected profile order or winner resolution.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run experiments/EXP-0139-skill-use-credit-entrypoint/screen_skill_avif.py", "python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature AVIF --plugin Skyrim.esm --editor-id AVHeavyArmor", "python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature AVIF --plugin Skyrim.esm --editor-id AVLightArmor", "EV-0262 five-master PERK EntryPoint 22 screen"],
            "coverage": "153 AVIF records and all five plugin file hashes were screened. Heavy Armor AVSK use multiplier/offset are 3.8/0.0; Light Armor 4.0/0.0. Native xEdit exported 115 and 95 fields respectively and loaded exactly the official five masters. The complete EP22 screen EV-0262 has eight rows, all with positive function data; targeted Heavy/Light rows are positive 1.20 multipliers.",
            "result": "The exact official AVIF/EP22 sources screened here contain no zero or negative Heavy/Light award coefficient. This is a bounded source negative; it does not exclude optional plugins, runtime state, or other native paths, and it establishes no protection or AVSK runtime result.",
            "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0262", "EV-0700", "EV-0703"],
        },
    ])
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "CL-L488" in claims or "CL-L489" in claims:
        raise SystemExit("Q92 claim ID collision")
    claims += "\n| CL-L488 | In the captured GOG Player skill progression path, FUN_14077d090 dispatches EntryPoint decimal 22 / hex 0x16 on its skill-credit float before adding the result to the per-skill progress field; its PlayerCharacter caller rejects the input unless strictly positive. | supported for the captured GOG static path | [EV-0221], [EV-0700], [EV-0703] | This does not show a player-accessible zeroing source, live AVSK delta, Steam equivalence, or effective armor protection. |\n"
    claims += "| CL-L489 | In the five official masters, AVIF AVSK use coefficients are 3.8 for Heavy Armor and 4.0 for Light Armor with zero offsets; all eight official Mod Skill Use PERK rows have positive amounts, including targeted Heavy/Light 1.20 multipliers. | supported within the five-master AVIF/EP22 source screen | [EV-0262], [EV-0704] | No profile winner, optional Creation coverage, runtime mutation, or universal no-suppressor conclusion is established. |\n"
    claims_path.write_text(claims, encoding="utf-8")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "M-0210" in mechanisms:
        raise SystemExit("M-0210 already exists")
    mechanisms += """

## M-0210 — award-side skill-use transformation precedes skill progress storage (EV-0221, EV-0262, EV-0703–EV-0704)

In GOG AE 1.6.1179.0, the PlayerCharacter UseSkill wrapper rejects non-positive points, then calls `FUN_14077d090` [EV-0221], [EV-0703]. The helper reads the skill AVIF's AVSK coefficients, conditionally forms `useMult * points + offsetMult`, dispatches selector decimal 22 / hex `0x16` (`kModSkillUse`) against the float, and adds the returned credit to the per-skill progress field before the threshold loop [EV-0700], [EV-0703]. This is an award-side control point downstream of the captured HitData points argument, distinct from the armor mitigation path.

The five-master source screen gives Heavy/Light use multipliers 3.8/4.0 with zero offsets; all eight official EntryPoint 22 records have positive amounts and the targeted Heavy/Light rows are positive 1.20 multipliers [EV-0262], [EV-0704]. No zero-capable source is established in this scoped layer. This does not exclude optional plugin records, runtime state, unqueried native routes, or a separate source mechanism. No effective armor protection or zero raw AVSK result is claimed. Claims CL-L488–CL-L489; Q92.
"""
    mechanisms_path.write_text(mechanisms, encoding="utf-8")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

## Q-0092 synthesis — a separate award-side modifier exists, but no official zero row was found (EV-0703–EV-0704)

The captured PlayerCharacter route separates the incoming-hit points gate from skill-credit calculation: positive points enter the skill helper; AVIF `useMult`/`offsetMult` and EntryPoint 22 (`kModSkillUse`) are applied before the per-skill progress field is updated [EV-0221], [EV-0700], [EV-0703]. The five-master Heavy/Light coefficients are nonzero, and the complete official EP22 screen has only positive amounts [EV-0262], [EV-0704].

This makes award credit structurally separable from the earlier HitData/protection computation, but the screened official source records provide no zero/negative modifier. No causal edge from the award visitor to positive protection or an observed zero AVSK is added. Q91's DeftMovement route acts earlier by zeroing incoming damage on a conditional proc; Q92's downstream route is distinct, and neither is a qualifying OBJ-2 result. No OBJ-1 edge is added. Claims CL-L488–CL-L489 -> M-0210.
"""
    graph_path.write_text(graph, encoding="utf-8")

    frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
    q92 = next(item for item in frontier["items"] if item.get("id") == "Q-0092")
    q92["question"] = "Does the PlayerCharacter post-positive-points progression path contain a vanilla, player-applicable zeroing layer for Heavy or Light Armor credit through AVIF coefficients or Mod Skill Use, separate from HitData protection?"
    q92["evidence"] = list(dict.fromkeys([*q92.get("evidence", []), "EV-0703", "EV-0704"]))
    q92["linked_claims"] = ["CL-L488", "CL-L489"]
    q92["hypotheses"] = [
        {"id": "Q-0092-H1", "model": "An official player-applicable AVIF coefficient or Mod Skill Use row can reduce Heavy/Light credit to zero after a positive HitData points value reaches the progression helper.", "predicted_discriminant": "The helper mutates the credit before storage and the complete official source screen finds a non-positive AVIF use coefficient or targeted EntryPoint 22 row.", "status": "falsified", "evidence": ["EV-0221", "EV-0262", "EV-0703", "EV-0704"]},
        {"id": "Q-0092-H2", "model": "The helper exposes a downstream Mod Skill Use control point, but the scoped official Heavy/Light coefficients and EntryPoint 22 records are all positive.", "predicted_discriminant": "GOG call order shows selector 0x16 before progress accumulation, while xEdit/schema-backed source records show nonzero base multipliers and positive targeted PERK amounts.", "status": "supported", "evidence": ["EV-0262", "EV-0700", "EV-0703", "EV-0704"]},
    ]
    q92["attempts"].append({
        "action_key": "q92-trace-modskilluse-credit-and-screen-avif",
        "outcome": "Fresh identity-checked GOG query shows the post-positive-points helper applies the AVIF skill-use transform, dispatches Mod Skill Use on the credit float, then adds the result to skill progress. The five-master AVIF screen and native xEdit exports show Heavy/Light use multipliers 3.8/4.0 with zero offset; the complete official EP22 screen has eight positive rows and positive 1.20 armor-skill modifiers. No zero-capable official source is found in this layer.",
        "evidence": ["EV-0262", "EV-0703", "EV-0704"],
        "new_discriminant": "Return to OBJ-1 with the highest-value tractable source route. Reassess Q-0020's DA07 museum-entrance geometry lead against the installed archive-discovery skill and existing read-only extraction capabilities; only reopen it if exact provenance-preserving static geometry work is available.",
        "recorded_utc": now,
    })
    FRONTIER_PATH.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(json.dumps({"registered": ["EV-0703", "EV-0704"], "manifest": private(manifest_path), "manifest_sha256": sha(manifest_path), "claims": ["CL-L488", "CL-L489"], "mechanism": "M-0210", "frontier": "Q-0092"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
