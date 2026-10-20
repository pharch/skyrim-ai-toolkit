#!/usr/bin/env python3
"""Register the bounded Q89 selector-0x55 source and code captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LOCAL = ROOT / ".local/alignment/transactions/TX-20261020-0008/q89"
EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
FRONTIER_PATH = ROOT / "research/FRONTIER.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def private(path: Path) -> str:
    return "private-local:" + path.relative_to(ROOT).as_posix()


def main() -> int:
    if not LOCAL.is_dir():
        raise SystemExit(f"missing Q89 capture directory: {LOCAL}")
    analysis_path = LOCAL / "q89-selector-analysis.json"
    analysis = json.loads(analysis_path.read_text(encoding="utf-8"))
    if analysis.get("decoded_row_count") != 31:
        raise SystemExit("Q89 analysis does not contain the complete 31-row screen")
    if analysis.get("handler_id_counts") != {"1_SetValue": 3, "3_Multiply": 28}:
        raise SystemExit("Q89 handler denominator changed")
    if not analysis.get("multiplier_data_summary", {}).get("all_positive"):
        raise SystemExit("Q89 multiplier rows are not all positive")

    ghidra_names = [
        "gog-query-20261020T051535Z.meta.json",
        "gog-query-20261020T051653Z.meta.json",
        "gog-query-20261020T051804Z.meta.json",
        "gog-query-20261020T051929Z.meta.json",
        "gog-query-20261020T052043Z.meta.json",
        "gog-query-20261020T052200Z.meta.json",
        "gog-query-20261020T052310Z.meta.json",
    ]
    artifacts: dict[str, dict[str, str]] = {}
    for path in sorted(LOCAL.iterdir()):
        if path.is_file():
            artifacts[path.relative_to(ROOT).as_posix()] = {"sha256": sha(path)}

    ghidra_checks = []
    for name in ghidra_names:
        path = ROOT / ".local/ghidra" / name
        meta = json.loads(path.read_text(encoding="utf-8"))
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
            raise SystemExit(f"Ghidra identity/read-only checks failed: {name}")
        referenced = [path, ROOT / meta["metadata_artifact"]]
        referenced.extend(ROOT / relative for relative in meta.get("artifacts", {}).values())
        for captured in referenced:
            if not captured.is_file():
                raise SystemExit(f"missing Ghidra artifact: {captured}")
            artifacts[captured.relative_to(ROOT).as_posix()] = {"sha256": sha(captured)}
        ghidra_checks.append({
            "metadata": path.relative_to(ROOT).as_posix(),
            "stdout_sha256": meta.get("stdout_sha256"),
            "requested_rva": meta.get("requested_rva"),
            "ok": meta.get("ok"),
            "read_only": meta.get("read_only"),
            "auto_analysis_disabled": meta.get("auto_analysis_disabled"),
        })

    xedit_paths = {
        "Dragonhide": ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T053708.253619Z/native-result.json",
        "EarthStone": ROOT / ".local/xedit-authoritative-copy/out/xedit/20261020T054328.751963Z/native-result.json",
    }
    xedit_artifacts = {}
    for label, result_path in xedit_paths.items():
        result = json.loads(result_path.read_text(encoding="utf-8"))
        expected = "ArmorFFSelf100" if label == "Dragonhide" else "DLC2StandingStonesEarthEffect"
        if result.get("loader_status") != "Background Loader: finished" or result.get("record", {}).get("editor_id") != expected:
            raise SystemExit(f"native xEdit query did not validate: {label}")
        if result.get("native_data_files") is None or len(result.get("plugins", [])) != 5:
            raise SystemExit(f"native xEdit scope was not the official five masters: {label}")
        tsv_path = result_path.parent / "native-records.tsv"
        for captured in (result_path, tsv_path):
            if not captured.is_file():
                raise SystemExit(f"missing native xEdit artifact: {captured}")
            artifacts[captured.relative_to(ROOT).as_posix()] = {"sha256": sha(captured)}
        xedit_artifacts[label] = {
            "result": result_path.relative_to(ROOT).as_posix(),
            "result_sha256": sha(result_path),
            "tsv": tsv_path.relative_to(ROOT).as_posix(),
            "tsv_sha256": sha(tsv_path),
            "record": result["record"],
            "field_count": result.get("field_count"),
            "official_five_master_scope": [
                row.get("filename") for row in result.get("native_data_files", [])
                if row.get("filename", "").lower().endswith(".esm")
            ],
        }

    manifest = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": "TX-20261020-0008",
        "frontier": "Q-0089",
        "analysis_build": {
            "distribution": "GOG",
            "product_version": "1.6.1179.0",
            "executable_sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "steam_target_is_separate": "EV-0109",
        },
        "scope": "Read-only static code and official five-master source-file screen; no profile winner or runtime test.",
        "ghidra_queries": ghidra_checks,
        "native_xedit_records": xedit_artifacts,
        "artifacts": artifacts,
    }
    manifest_path = LOCAL / "capture-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    uesp_specs = [
        ("uesp-dragonhide.raw", "Skyrim:Dragonhide", 3496944, "2026-02-05T04:33:16Z", "https://en.uesp.net/w/index.php?title=Skyrim:Dragonhide&oldid=3496944"),
        ("uesp-earth-stone.raw", "Skyrim:Earth_Stone", 3098352, "2024-08-02", "https://en.uesp.net/w/index.php?title=Skyrim:Earth_Stone&oldid=3098352"),
        ("uesp-alteration-ritual.raw", "Skyrim:Alteration_Ritual_Spell", 3176479, "2024-11-09", "https://en.uesp.net/w/index.php?title=Skyrim:Alteration_Ritual_Spell&oldid=3176479"),
    ]
    uesp = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "database": "uespwiki-2026-10-04-current.xml.bz2",
        "database_sha256": "b3ccaea9d10c653a1bf702d0da5d32c2bc9a5cafdcd374d258f5a063d6074ddb",
        "database_scope": "475,228 pages; 17,520 Skyrim namespace pages; zero parser errors; source completeness unverified.",
        "pages": [
            {"path": private(LOCAL / filename), "title": title, "revision": revision,
             "revision_timestamp": timestamp, "url": url,
             "raw_sha256": sha(LOCAL / filename)}
            for filename, title, revision, timestamp, url in uesp_specs
        ],
        "interpretation_limit": "Secondary wiki text is a lead, not proof of AE records, active-effect lifetime, level-one access, or live protection/armor XP behavior.",
    }
    uesp_path = LOCAL / "uesp-lead-manifest.json"
    uesp_path.write_text(json.dumps(uesp, indent=2) + "\n", encoding="utf-8")

    evidence = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    existing = {item["id"] for item in evidence["items"]}
    new_ids = {"EV-0696", "EV-0697", "EV-0698"}
    if existing & new_ids:
        raise SystemExit(f"evidence IDs already exist: {sorted(existing & new_ids)}")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    evidence["items"].extend([
        {
            "id": "EV-0696", "captured_utc": now, "kind": "native",
            "source": "Fresh read-only GOG Ghidra trace of the Actor/PlayerCharacter slot-0x100 entrypoint visitor, its selector-0x55 handler dispatch, and the PlayerCharacter cached armor-factor consumer.",
            "artifact": private(manifest_path), "sha256": sha(manifest_path), "edition": "AE",
            "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Installed Steam AE 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run tools/ghidra_probe.py --rva ... --vtable-slot ...", "Ghidra 12.0.4 existing configured GOG project in -noanalysis -readOnly mode"],
            "coverage": "The cached armor-factor path computes an item contribution, passes a float pointer through Actor slot 0x100 / FUN_140386070 with selector 0x55, then reloads and accumulates that value. The handler callback iterates entry-point handlers. Captures are identity-checked and read-only; raw artifacts and hashes are enumerated in the private manifest.",
            "result": "PASS for the bounded GOG callback/dataflow path. The callback can alter a per-item cache contribution. This does not establish active-effect lifetime, actual Steam invocation, final protection, or armor XP.",
            "related_evidence": ["EV-0109", "EV-0260", "EV-0311", "EV-0312", "EV-0670", "EV-0672", "EV-0681", "EV-0683", "EV-0684"],
        },
        {
            "id": "EV-0697", "captured_utc": now, "kind": "record",
            "source": "Official five-master PERK selector-0x55 source-file screen, raw FormID-link scan, two accepted native SSEView MGEF exports, and pinned CommonLib/TES5Edit schema provenance.",
            "artifact": private(analysis_path), "sha256": sha(analysis_path), "edition": "AE",
            "runtime": "Official Skyrim.esm, Update.esm, Dawnguard.esm, HearthFires.esm, Dragonborn.esm source-file scope only. No active profile order, Creation Club coverage, or live runtime result.",
            "modified_state": False, "lane": "mechanism_inference",
            "tools": ["python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature MGEF --plugin Skyrim.esm --editor-id ArmorFFSelf100", "python3 scripts/python_env.py run tools/xedit_bridge.py native-query --signature MGEF --plugin Dragonborn.esm --editor-id DLC2StandingStonesEarthEffect", "python3 scripts/python_env.py run experiments/EXP-0136-armor-entrypoint-selector-55/screen_official_perk_entries.py", "CommonLibSSE source commit b93280e832f263dbef44e44cbe2936622a02f91a", "TES5Edit dev-4.1.6 Core/wbDefinitionsTES5.pas"],
            "coverage": "The screen contains 785 PERK entrypoint rows across the five masters, including 31 selector-0x55 rows: three DATA[1]=1 SetValue rows with EPFD 0.0 and 28 DATA[1]=3 multipliers, all positive (1.1 to 2.0). DragonhideSpellPerk and DLC2StandingStoneEarthPerk are each directly linked from their MGEF Perk to Apply field. Earth selector-0x55 SetValue row has one HasMagicEffect(MGEF 000CDB75)==0 CTDA; its paired selector-0x24 row has the same condition. Native xEdit accepted exact EditorID queries and loaded the official five-master scope.",
            "result": "PASS for the bounded record screen: official source data includes zero-setting armor-rating rows and the identified MGEF-to-PERK links. One zero PERK (DrunkenMaster) has no raw FormID reference in the five masters; that absence is bounded to the raw scan. CTDA truth at runtime, actual effect application, profile winners, total protection, and zero-XP behavior remain unknown.",
            "related_evidence": ["EV-0109", "EV-0260", "EV-0311", "EV-0672", "EV-0681", "EV-0683", "EV-0684"],
        },
        {
            "id": "EV-0698", "captured_utc": now, "kind": "wiki",
            "source": "Revision-pinned local UESP XML database captures for Dragonhide, Earth Stone, and Alteration Ritual Spell; provenance and raw hashes are in the private lead manifest.",
            "artifact": private(uesp_path), "sha256": sha(uesp_path), "edition": "AE",
            "runtime": "Local UESP export snapshot dated 2026-10-04; page revisions individually pinned. Not an installed-game build or runtime observation.",
            "modified_state": False, "lane": "offline",
            "tools": ["python3 scripts/python_env.py run -m tools.uesp doctor --db .local/uesp.sqlite3", "python3 scripts/python_env.py run -m tools.uesp page --title ..."],
            "coverage": "Captured page text reports Dragonhide's physical-damage effect and armor-rating display behavior, Earth Stone power behavior, and the Alteration Ritual Spell acquisition threshold. The local source database parsed without errors but completeness is unverified.",
            "result": "Secondary-source leads only. These page statements are not accepted as proof of active MGEF state, level-one accessibility, effective armor protection, or armor XP behavior; the exact revisions and raw page hashes remain preserved.",
            "related_evidence": ["EV-0260", "EV-0697"],
        },
    ])
    EVIDENCE_PATH.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "CL-L481" in claims or "CL-L482" in claims or "CL-L483" in claims:
        raise SystemExit("one or more Q89 claim IDs already exist")
    claims += "\n| CL-L481 | In GOG AE 1.6.1179.0, the cached armor-factor visitor passes each non-clothing item contribution by pointer through Actor/PlayerCharacter vtable slot 0x100 as entry-point selector 0x55, reloads the possibly modified float, and then accumulates it. | supported for the captured GOG static dataflow | [EV-0311], [EV-0696] | This does not establish effect activation, Steam behavior, final damage reduction, or a qualifying armor/zero-XP outcome. |\n"
    claims += "| CL-L482 | The official five-master source screen contains 31 selector-0x55 PERK rows: three SetValue-zero rows and 28 positive Multiply rows; the Dragonhide and Earth Stone MGEFs link to their respective zero-setting perks, while Earth's zero row has a HasMagicEffect(Dragonhide MGEF)==0 condition. | supported for exact source-file records and accepted native five-master MGEF exports | [EV-0697] | This is not a profile winner or runtime predicate result. The unrelated DrunkenMaster zero row has no raw FormID reference in the scanned five masters; no negative multiplier occurs in this scoped screen. |\n"
    claims += "| CL-L483 | The revision-pinned local UESP Dragonhide page reports an 80% physical-damage effect and that displayed armor values can remain stale while item values are zero during the effect. | supported only as a statement about the captured secondary page | [EV-0698] | Wiki text is a lead, not AE engine proof or a measured result; it does not establish item protection, level-one access, or zero armor XP. |\n"
    claims_path.write_text(claims, encoding="utf-8")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "M-0207" in mechanisms:
        raise SystemExit("M-0207 already exists")
    mechanisms += """

## M-0207 — Data-driven per-item armor-rating cache adjustment (EV-0696–EV-0697)

In GOG AE 1.6.1179.0, the PlayerCharacter cached armor-factor visitor computes an equipped non-clothing item's candidate rating, calls the Actor entry-point visitor with selector `0x55` and a pointer to that float, reloads the value, and adds it to its cache accumulator [EV-0311], [EV-0696]. CommonLib source identifies selector `0x55` as `kModArmorRating`; the handler dispatch is through each entry's DATA handler ID, separate from EPFT's function-data class [EV-0681], [EV-0683].

The official five-master screen contains three SetValue-zero and 28 positive Multiply rows. Native MGEF records link Dragonhide and Earth Stone effects to their corresponding zero-setting perks; Earth Stone's selector-0x55 row is conditioned on `HasMagicEffect(ArmorFFSelf100) == 0` in the serialized CTDA [EV-0697]. This supplies a source-backed candidate route for zeroing an item contribution in the cache. It does not establish ActiveEffect/perk lifetime, condition evaluation timing, profile winners, final protection, or runtime invocation.

Cross-domain assessment: the cache callback and the later hit-earned armor-skill route are distinct code/data paths in the currently mapped GOG findings. No causal edge from this cache adjustment to zero AV11/AV12 is supported here; test the HitData points field and raw-DNAM eligibility separately in Q-0090. Steam matched-hit/protection/raw-AVSK evidence remains under EV-0260. Claims CL-L481–CL-L482.
"""
    mechanisms_path.write_text(mechanisms, encoding="utf-8")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    graph = graph_path.read_text(encoding="utf-8")
    graph += """

### Q-0089 — selector-0x55 adjusts cached item armor rating (EV-0696–EV-0698)

The GOG 1.6.1179.0 PlayerCharacter cached armor-factor visitor passes a candidate non-clothing item rating through Actor slot 0x100 / selector 0x55 before cache accumulation [EV-0311], [EV-0696]. The exact official five-master screen contains three SetValue-zero rows and 28 positive multipliers; Dragonhide and Earth Stone MGEFs each name a corresponding zero-setting perk in `Perk to Apply` [EV-0697]. This supports a bounded code-to-record candidate route for setting a per-item cache contribution to zero. It does not establish active-effect lifetime, final effective protection, profile winners, or Steam behavior.

No causal edge is added from selector-0x55 cache adjustment to the unblocked HitData armor-skill award. Existing GOG evidence places armor AV11/AV12 routing in a separate resolver that scans positive raw ARMO DNAM ratings [EV-0670], [EV-0690]; Q-0090 tests whether its points input is a pre-mitigation HitData field. UESP's Dragonhide description is retained only as a secondary lead [EV-0698]. Claims CL-L481–CL-L483; mechanism M-0207. The exact cross-system falsifier is a source path showing selector 0x55 changes the armor-award points/eligibility input, followed by EV-0260 runtime protection and raw-AVSK measurement.
"""
    graph_path.write_text(graph, encoding="utf-8")

    exp = ROOT / "experiments/EXP-0136-armor-entrypoint-selector-55"
    (exp / "results.md").write_text("""# EXP-0136 results — Q89 bounded selector-0x55 screen

## GOG code path

Fresh read-only GOG AE 1.6.1179.0 captures identify `Actor` and `PlayerCharacter` vtable slot `0x100` as `FUN_14068f0c0`, which traverses entry-point perk records and dispatches handler IDs. In `FUN_14072a500`, each eligible non-clothing item's candidate armor rating is passed by pointer to `FUN_140386070(0x55, actor, item, &value)`; the value is reloaded and accumulated only after the callback. The adapter confirms the GOG executable hash and disables auto-analysis; no RVA is transferred to Steam [EV-0696].

CommonLib source commit `b93280e832f263dbef44e44cbe2936622a02f91a`, `BGSEntryPoint.h`, names selector `0x55` `kModArmorRating`. The handler ID is `PERK DATA[1]`; EPFT is the function-data class [EV-0681], [EV-0683].

## Official record screen

The complete configured official five-master screen contains 785 PERK entry rows and 31 selector-0x55 rows (Skyrim 15, Update 3, Dawnguard 7, Dragonborn 6; HearthFires 0). All 31 use EPFT 1 / OneValue. Three use DATA[1]=1 / SetValue with EPFD 0.0; 28 use DATA[1]=3 / Multiply with positive factors 1.1–2.0. No negative multiplier appears in this scope [EV-0697].

Two zero rows are linked from MGEFs by raw FormID references and accepted native xEdit exports:

- `ArmorFFSelf100` (Skyrim.esm `000CDB75`) is a Peak Value Modifier for Damage Resist and names `DragonhideSpellPerk`; `DragonhideSpellPerk` sets selector 0x55 to zero without a CTDA.
- `DLC2StandingStonesEarthEffect` (Dragonborn.esm `0201DFA0`) is also a Peak Value Modifier for Damage Resist and names `DLC2StandingStoneEarthPerk`; its selector-0x55 SetValue-zero row has one CTDA for `HasMagicEffect(000CDB75) == 0.0`. Its paired selector-0x24 row has a matching condition. TES5Edit dev-4.1.6 maps function index 214 to `HasMagicEffect`, with Param1 type Magic Effect. Equality-to-zero as absence is an inference from boolean condition semantics, not a runtime result [EV-0697].
- `dlc2BBDrunkenMaster` has a third SetValue-zero row but no raw FormID references in the five-master scan. Its actual source/application path remains unknown.

The native queries were accepted by exact EditorID against the official five-master view. An earlier Earth query using a Dragonborn-local FormID was rejected after load-order remapping and is not evidence. No profile winner, Creation Club coverage, active effect lifetime, or live condition evaluation is established [EV-0697].

## Outcome and cross-domain boundary

Q89 is complete as a bounded static source result: selector 0x55 can modify the cached per-item armor factor, and scoped official data includes rows that set it to zero. This result does not show that an equipped item remains protective, that total protection remains positive, or that armor XP becomes zero. The hit resolver's armor eligibility scan and skill points are separate; Q90 traces the HitData points input. The Steam discriminator still requires a matched landed hit, measured positive protection, and raw AVSK before/after under EV-0260.

Local UESP revision captures report Dragonhide's 80% physical-damage effect and stale displayed armor totals, and list Alteration Ritual Spell acquisition requirements; these remain secondary leads only [EV-0698].
""", encoding="utf-8")
    (exp / "README.md").write_text("""# EXP-0136 — Selector 0x55 in the cached armor-factor path

**Status:** Q89 completed as a bounded GOG static code and official-record screen; Q90 continues the armor XP question.

**Result:** The cached PlayerCharacter armor-factor visitor sends each eligible non-clothing item contribution through Actor vtable slot 0x100 using selector 0x55 before accumulation. The five official masters contain zero-setting PERK rows, including Dragonhide and Earth Stone effects linked to zero-setting perks. This is a candidate cache adjustment, not proof of active protection or zero armor XP [EV-0696], [EV-0697].

**Build boundary:** GOG Skyrim AE 1.6.1179.0 for native analysis, separate from installed Steam AE 1.6.1170.0 [EV-0109].

**Open discriminant:** Does the unblocked HitData armor-skill path use a pre-mitigation physicalDamage field and independently require positive raw armor DNAM? Q-0090 traces the exact builder/resolver dataflow; EV-0260 remains the live Steam matched-hit, protection, and raw-AVSK protocol.

**Approved action surface:** Existing GOG Ghidra project and official five-master source files, read-only. No game launch, save, console, plugin, or profile winner claim.
""", encoding="utf-8")
    (exp / "hypothesis.md").write_text("""# EXP-0136 hypothesis outcome

Q89's initial alternatives were resolved only within the static scopes:

- **H1 supported:** the cached contribution is passed by pointer through selector 0x55; a concrete callback can alter it, and official source rows include SetValue 0.0 [EV-0696], [EV-0697].
- **H2 falsified for the captured static path:** the callback does not leave every value untouched, and two source MGEFs link to the zero-setting perks [EV-0696], [EV-0697]. Runtime activation remains unknown.
- **H3 falsified as a multiplier-only model:** the official selector rows are not all positive multipliers; SetValue 0.0 rows exist. No negative multiplier occurs in the five-master screen. A zero item contribution does not establish a negative or positive total armor rating [EV-0697].

## Q90 competing models

- **H1:** HitData `physicalDamage` is copied from totalDamage before AV39/armor-factor reductions; the unblocked armor award uses that snapshot and positive raw-DNAM armor eligibility, so zeroing the cache contribution alone cannot zero the points input.
- **H2:** A Dragonhide or earlier incoming-damage entry-point path modifies the points field before the snapshot or prevents the armor branch, allowing positive non-armor protection with zero armor XP.
- **H3:** Award points derive from post-mitigation totalDamage or a separate armor-factor query, so the selector-0x55 zero result directly affects XP.

**Predictions:** Compare the exact HitData field writes and order in `FUN_1407dd220` / `FUN_1407ddf50` against `FUN_1406bcaa0`'s raw DNAM scan and Player slot-0xF7 call. H1 predicts the award argument is the pre-mitigation snapshot; H2 predicts a pre-snapshot mutation/eligibility guard tied to the effect; H3 predicts a post-mitigation value or selector-0x55 dependency at the XP call. A GOG result does not replace EV-0260 Steam measurements.
""", encoding="utf-8")

    frontier = json.loads(FRONTIER_PATH.read_text(encoding="utf-8"))
    items = frontier["items"]
    q89 = next(item for item in items if item["id"] == "Q-0089")
    q89["evidence"] = ["EV-0309", "EV-0311", "EV-0312", "EV-0261", "EV-0260", "EV-0696", "EV-0697", "EV-0698"]
    q89["linked_claims"] = ["CL-L481", "CL-L482", "CL-L483"]
    q89["successors"] = ["Q-0090"]
    q89["next_action"] = "Close Q89 as a bounded static source result; continue immediately with Q-0090, tracing whether the armor UseSkill argument comes from pre-mitigation HitData and whether Dragonhide or an earlier entry point changes that field."
    q89["hypotheses"] = [
        {"id": "Q-0089-H1", "model": "The selector-0x55 callback can change a per-item cached armor-rating contribution, and a scoped official PERK row sets it to zero.", "predicted_discriminant": "A pointer-argument write in the callback plus a decoded official DATA[1]=SetValue row with EPFD 0.0 and a linked MGEF/PERK chain.", "status": "supported", "evidence": ["EV-0696", "EV-0697"]},
        {"id": "Q-0089-H2", "model": "The captured cache path leaves the candidate unchanged or has no relevant official source data linked to it.", "predicted_discriminant": "No callback mutation or no selector-0x55 official row/MGEF link in the complete source scope.", "status": "falsified", "evidence": ["EV-0696", "EV-0697"]},
        {"id": "Q-0089-H3", "model": "All scoped official selector-0x55 records are strictly positive multipliers, so they cannot set the per-item contribution to zero.", "predicted_discriminant": "A complete five-master row screen contains only positive multiplier operations and no SetValue-zero rows.", "status": "falsified", "evidence": ["EV-0697"]}
    ]
    q89["attempts"].append({
        "action_key": "q89-register-static-record-and-code-result",
        "outcome": "Registered EV-0696–EV-0698 with raw manifests and hashes; corrected the earlier EV-0695 identifier error, which remains a Q88-only record. The GOG cache callback accepts a mutable per-item float, and official source records include zero-setting Dragonhide/Earth PERKs. No runtime protection or armor-XP outcome is claimed.",
        "evidence": ["EV-0696", "EV-0697", "EV-0698"],
        "new_discriminant": "The remaining bounty-level question is whether the independent armor XP route consumes the same adjusted value, the pre-mitigation HitData snapshot, or raw positive ARMO DNAM. Test that separate dataflow in Q-0090.",
        "recorded_utc": now
    })

    if not any(item["id"] == "Q-0090" for item in items):
        items.append({
            "id": "Q-0090", "objective": "OBJ-2", "kind": "mechanism", "status": "open",
            "question": "In the GOG physical-hit resolver, does armor skill XP use the pre-mitigation HitData physicalDamage snapshot plus positive raw armor DNAM eligibility, making selector-0x55 cache zeroing irrelevant to XP, or can Dragonhide/another earlier modifier alter the XP input while leaving effective protection?",
            "hypotheses": [
                {"id": "Q-0090-H1", "model": "The builder copies physicalDamage before AV39/armor-factor mitigation and the unblocked armor award uses that snapshot after a separate positive raw-DNAM eligibility scan; selector 0x55 alone therefore cannot suppress the award input.", "predicted_discriminant": "Show exact builder writes/order and resolver field use; no selector-0x55 call or post-mitigation read feeds the armor award argument.", "status": "proposed", "evidence": ["EV-0670", "EV-0690", "EV-0696"]},
                {"id": "Q-0090-H2", "model": "A preceding HitData entry-point or Dragonhide effect changes the field used for armor XP before the snapshot or skips the armor award, while separate effect protection remains.", "predicted_discriminant": "A direct call/data edge from an effect-specific or incoming-damage handler to the pre-snapshot field or award eligibility guard, plus a distinguishable builder input.", "status": "proposed", "evidence": ["EV-0697"]},
                {"id": "Q-0090-H3", "model": "The armor award argument depends on post-mitigation totalDamage or the cached armor-rating result, so selector-0x55 zeroing can lower or zero hit-earned armor skill points.", "predicted_discriminant": "Resolver reads the post-mitigation field or re-queries selector 0x55 on the award path; compare that exact field with the callback output.", "status": "proposed", "evidence": ["EV-0670", "EV-0696"]}
            ],
            "methods": [
                "Freshly query the identity-checked GOG 1.6.1179.0 FUN_1407ddf50 body and callers; map exact writes to HitData totalDamage and physicalDamage before/after AV39 and armor-factor calculations.",
                "Cross-check current FUN_1407dd220 builder capture and FUN_1406bcaa0 receiver body: classify the +0x50/+0x54 fields, the positive raw ARMO DNAM scan, branch conditions, and PlayerCharacter slot 0xF7 argument.",
                "Inspect selector rows and direct call order for any earlier incoming-damage modifier that can touch the pre-mitigation snapshot; keep Dragonhide's MGEF record link separate from runtime ActiveEffect state.",
                "Preserve the exact Steam matched-hit, positive-protection, raw AV11/AV12 AVSK before/after discriminator under EV-0260; static GOG evidence cannot establish the bounty outcome."
            ],
            "blocked_by": [], "evidence": ["EV-0260", "EV-0670", "EV-0690", "EV-0696", "EV-0697"],
            "priority": 0.99, "information_gain": 0.96,
            "next_action": "Query fresh GOG FUN_1407ddf50 at RVA 0x7DDF50 with direct call edges and bounded incoming callers. State whether physicalDamage is a pre-mitigation snapshot, then trace any writes between the builder and the Player armor-award argument.",
            "linked_claims": ["CL-L465", "CL-L476", "CL-L481", "CL-L482"], "successors": [], "attempts": []
        })
    else:
        raise SystemExit("Q-0090 already exists; refusing duplicate frontier insertion")
    FRONTIER_PATH.write_text(json.dumps(frontier, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "registered": ["EV-0696", "EV-0697", "EV-0698"],
        "capture_manifest": private(manifest_path), "capture_manifest_sha256": sha(manifest_path),
        "uesp_manifest": private(uesp_path), "uesp_manifest_sha256": sha(uesp_path),
        "frontier_added": "Q-0090", "q89_claims": ["CL-L481", "CL-L482", "CL-L483"],
        "mechanism": "M-0207"
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
