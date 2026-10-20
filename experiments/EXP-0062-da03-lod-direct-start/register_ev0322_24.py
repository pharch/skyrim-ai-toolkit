#!/usr/bin/env python3
"""Register bounded DA03Start and trap-route evidence captured in this session."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TX8 = ROOT / ".local/alignment/transactions/TX-20261017-0008"
TX9 = ROOT / ".local/alignment/transactions/TX-20261017-0009"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def append_tail(path: Path, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker not in text:
        path.write_text(text.rstrip() + "\n\n" + body.rstrip() + "\n", encoding="utf-8")


def append_after(path: Path, anchor: str, marker: str, body: str) -> None:
    text = path.read_text(encoding="utf-8")
    if marker in text:
        return
    index = text.find(anchor)
    if index < 0:
        raise SystemExit(f"missing anchor {anchor} in {path}")
    end = text.find("\n", index)
    if end < 0:
        end = len(text)
    path.write_text(text[:end + 1] + "\n" + body.rstrip() + "\n" + text[end + 1:], encoding="utf-8")


def add_evidence(row: dict) -> None:
    path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if any(item.get("id") == row["id"] for item in evidence["items"]):
        raise SystemExit(f"{row['id']} already registered; refusing duplicate")
    evidence["items"].append(row)
    path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    # Verify the Q-0061 source artifacts before creating durable notes.
    raw_names = [
        "EV-0322-da03-vmad.json",
        "EV-0322-da03-topics.json",
        "EV-0322-da03-topic-summary.json",
        "EV-0322-da03-topic-analysis.json",
        "EV-0323-da03-pex.json",
    ]
    raw = {name: TX8 / name for name in raw_names}
    expected = {
        "EV-0322-da03-vmad.json": "6fd9ea82af9acf12716e142581b93ddacd5dc60342831c6e4cf101688dd13005",
        "EV-0322-da03-topics.json": "cda621d0bf8332b06f294a54e28b9b641eaafaafd7e2914285dc3d92d8dd758a",
        "EV-0322-da03-topic-summary.json": "d95497a8128d23a713f7d168c3d885b8f1b43d8ff8759954f9a2735ac768ef04",
        "EV-0322-da03-topic-analysis.json": "63df84182f9f107496e3d2a6b23d6b86d3f1dcce3856f57a04a4f8b02233698e",
        "EV-0323-da03-pex.json": "b75085a0e1e60615bc0c7218adc46e12e30bb2a03f06470929f5bfe4ed3baca3",
    }
    for name, path in raw.items():
        if not path.is_file() or sha(path) != expected[name]:
            raise SystemExit(f"missing or hash-mismatched source artifact: {path}")
    analysis = json.loads(raw["EV-0322-da03-topic-analysis.json"].read_text(encoding="utf-8"))
    pex = json.loads(raw["EV-0323-da03-pex.json"].read_text(encoding="utf-8"))
    scripts = {item["script"]: item for item in pex["scripts"]}
    required = {"TIF__000D7933", "TIF__000E0D47", "TIF__0010F590", "QF_DA03Start_000D7939"}
    if not required <= scripts.keys():
        raise SystemExit("PEX source capture is missing a required topic or QF script")

    note322 = TX8 / "EV-0322-note.md"
    write(note322, """# EV-0322 — DA03Start Lod dialogue and source-layer join

## Source identity and method

The installed Steam AE 1.6.1170.0 identity is separately preserved in EV-0109. The five official master hashes were rechecked against EV-0321: Skyrim.esm 2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107; Update.esm c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9; Dawnguard.esm 1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4; HearthFires.esm ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97; Dragonborn.esm 5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b.

A source-bound TES4 join resolves every DA03Start QNAM-owned DIAL topic, fixed official-source copies, and INFO children using GRUP type-7 ancestry. It identified 15 logical DIAL/INFO topic-child pairs. This fixed official source-layer view is not a profile winner.

## Direct observations

- The QUST alias map identifies Lod as alias 6 with base actor FormID 00013650.
- DIAL 000D7930 (DA03StartLodBranchPersuadeTopic) -> INFO 000D7933 has GetLevel >= 10, GetStage(DA03Start 000D7939) < 10, and a condition with function index 72 referring to base FormID 00013650. This capture does not assign a name to function index 72.
- INFO 000D7933 attaches TIF__000D7933. Its bounded PEX callback grants items and sets its owning DA03Start helper to stage 10. DIAL 000E0D3F -> INFO 000E0D47 is another Lod topic with the same level/stage conditions and a TIF callback setting helper stage 10.
- DA03Start stage 10 maps to QF Fragment_27, which calls DA03.SetStage(5). The known main-quest handoff is therefore downstream of Lod's level-gated helper stage-10 response.
- The unlevelled DIAL 0010F58E -> INFO 0010F590 reward goodbye has one captured function-index-72 condition referring to Lod's base FormID and attaches TIF__0010F590, which sets DA03Start to stage 20. QF stage 20 is Fragment_29, which gives 25 gold and sets the helper to stage 200; stage 200 is Fragment_31, which stops the helper. The captured unlevelled callback contains no DA03 main-quest start/stage call.
- No other direct Lod callback into DA03 was identified in this bounded 15-topic join. Stage-15 topics have advanced-helper predicates and the captured stage-15 fragment only changes objectives.

## Interpretation and limits

Within this fixed official-source scope, the direct Lod handoff to DA03Start stage 10 is gated at level 10, while the captured unlevelled goodbye is a helper reward/stop path. This falsifies the specific model that Lod's direct unlevelled response starts DA03 below level 10 and supports the helper-only alternative for that callback.

The source join does not establish profile-specific winners, runtime dialogue accessibility, level-one quest state, useful progression, or vanilla reproduction. Localized response text was not inferred from string IDs; function-index-72 semantics remain unverified. The tested PEX extraction is limited to the base Skyrim - Misc.bsa. No OBJ-2 edge is supported.
""")

    note323 = TX8 / "EV-0323-note.md"
    write(note323, f"""# EV-0323 — DA03Start Lod TIF and QF PEX bodies

## Source identity and method

The classic PEX 3.2 streams were extracted from the hash-identified base Skyrim - Misc.bsa (SHA-256 ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d) and parsed with the tested PEX reader through the strict dispatcher. The QF extraction provenance is cross-linked to EV-0321. Each stream parsed fully with zero trailing bytes.

## Direct observations

- TIF__000D7933: PEX SHA-256 {scripts['TIF__000D7933']['pex_sha256']}, 999 bytes. Fragment_0 grants the captured reward items and sets its owning quest to stage 10.
- TIF__000E0D47: PEX SHA-256 {scripts['TIF__000E0D47']['pex_sha256']}, 888 bytes. Fragment_0 grants DA03 meat and sets its owning quest to stage 10.
- TIF__0010F590: PEX SHA-256 {scripts['TIF__0010F590']['pex_sha256']}, 684 bytes. Fragment_0 sets its owning helper to stage 20 and does not call DA03.Start or DA03.SetStage.
- QF_DA03Start_000D7939: PEX SHA-256 {scripts['QF_DA03Start_000D7939']['pex_sha256']}, 1,676 bytes. Stage 10 maps to Fragment_27, which calls DA03.SetStage(5); stage 20 maps to Fragment_29, which gives 25 gold and sets helper stage 200; stage 200 maps to Fragment_31, which stops the helper. Stage 15 maps to Fragment_33, which only completes/displays objectives in the captured body.
- Raw PEX parses and exact BSA extraction offsets are in .local/alignment/transactions/TX-20261017-0008/EV-0323-da03-pex.json.

## Interpretation and limits

These bodies connect the level-gated Lod stage-10 topics to the helper-to-main-quest handoff and classify the unlevelled goodbye as a helper reward route. They do not prove INFO selection or level-one dialogue access. Extraction is limited to the tested base Misc BSA; no full profile order or runtime transition was observed.
""")

    # Fresh GOG query captures used for EV-0324.
    ghidra = ROOT / ".local/ghidra"
    stamps = [
        "20261017T215324Z", "20261017T215426Z", "20261017T215531Z",
        "20261017T215639Z", "20261017T215735Z", "20261017T220043Z",
        "20261017T220223Z", "20261017T220435Z", "20261017T220953Z",
    ]
    local324: dict[str, str] = {}
    metadata = []
    for stamp in stamps:
        for suffix in ("stdout.raw", "meta.json"):
            path = ghidra / f"gog-query-{stamp}.{suffix}"
            if not path.is_file():
                raise SystemExit(f"missing Ghidra capture {path}")
            local324[path.relative_to(ROOT).as_posix()] = sha(path)
        meta_path = ghidra / f"gog-query-{stamp}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f" or meta.get("exit_code") != 0 or checks.get("program_identity_matches_gog_binary") is not True or checks.get("script_no_error") is not True:
            raise SystemExit(f"Ghidra query identity or execution failed: {stamp}")
        required_checks = ("requested_displacement", "displacement_scan_complete", "visitor_symbol_scan_complete", "writer_analysis_complete", "visitor_callee_analysis_complete", "computed_writer_analysis_complete", "visitor_method_analysis_complete") if meta.get("query_mode") == "memory_displacement_search" else ("function_lookup", "requested_rva_lookup", "disassembly", "decompilation")
        if meta.get("requested_vtable_slot") is not None:
            required_checks += ("vtable_slot_lookup",)
        if meta.get("enumerate_call_edges"):
            required_checks += ("direct_call_edge_scan",)
        if any(checks.get(key) is not True for key in required_checks):
            raise SystemExit(f"Ghidra required query component failed: {stamp}")
        metadata.append(meta)
    for name in ("vtable_actor.json", "vtable_playercharacter.json"):
        path = ROOT / ".local/alignment/transactions/TX-20261016-0003" / name
        if not path.is_file():
            raise SystemExit(f"missing vtable record {path}")
        local324[path.relative_to(ROOT).as_posix()] = sha(path)

    note324 = TX9 / "EV-0324-note.md"
    write(note324, """# EV-0324 — Trap receiver route versus inline armor skill resolver

## Build identity and query method

The queried native target is GOG Skyrim AE 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f, with matching Address Library SHA-256 3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e. Ghidra queries used the existing project with -noanalysis -readOnly. No project import, auto-analysis, or binary write occurred. Installed Steam AE 1.6.1170.0 is separately identified in EV-0109; no GOG RVA is transferred.

Fresh vtable-slot queries identify Actor and PlayerCharacter slot 0xF7 / byte offset 0x7B8. The PlayerCharacter target is FUN_140739050, which calls the skill-progress routine FUN_14077d090. CommonLibSSE-NG header hashes used for slot and ActorValue naming:
- include/RE/A/Actor.h: 0b2c088d5735102f5c92b40ee9e91d223bb16e5e6ef6382bec5c8186d9178415.
- include/RE/P/PlayerCharacter.h: 7204646155a75158b9c7e3efcc59194b2d6aacde5f9a97f8152d9f38ad50f0a5.
- include/RE/H/HitData.h: ca028c22282a141ad7afabe814d4b257bf4ca3aefa7f618db18feea82e1f703b.
- include/RE/A/ActorValues.h: 5e9178fd064da0d4287be0aa47f538a428ce04c856ec52bff3fc17f8a3e87e8b.

All raw stdout and query metadata hashes are in EV-0324-capture-manifest.json. The whole-listing displacement scan completed all markers; its 0x7B8 matches include relevant calls in FUN_1406b9df0 and FUN_1406bcaa0. The vtable slot-query wrapper reports ok=false only because it has no direct code-call xref for the vtable data entry; executable identity, slot lookup, disassembly, decompilation, and script checks pass.

## Direct observations

1. EV-0293 maps Papyrus ObjectReference.ProcessTrapHit to the Actor/PlayerCharacter slot-0x58 implementation FUN_140679da0. The fresh query records four direct calls in FUN_140679da0: HitData initialization, builder FUN_1407dd110, receiver FUN_1406b9df0, and cleanup. There is no direct call to FUN_1406bcaa0.
2. EV-0261 identifies FUN_1407ddf50 as a shared HitData population/resistance path, including AV39 and PlayerCharacter armor-base-factor calculations that reduce totalDamage. The trap FUN_1407dd110 path reaches this construction before FUN_1406b9df0. This is a mitigation input path, not proof that a hit causes positive final damage or protection.
3. The known inline resolver FUN_1406bcaa0 contains a PlayerCharacter skill branch for positive HitData damage. Its unblocked branch scans worn positive-base Light/Heavy armor and selects AV12/AV11; its blocked branch selects Block AV9. It calls Actor::UseSkill through slot 0xF7, then calls FUN_1406b9df0. These branches and point sources are separately supported in EV-0217 through EV-0223.
4. The trap route reaches FUN_1406b9df0 from FUN_140679da0 after shared HitData construction, without a direct edge through FUN_1406bcaa0. In the handler, the one visible Actor::UseSkill slot-0xF7 call at GOG RVA 0x6BA19C passes AV15 Sneak; its two captured point inputs are positive constants 2.5 and 20.0 under a Sneak branch. It is not an AV11/AV12 call.
5. The fresh complete direct/indirect census of FUN_1406b9df0 records 89 direct-call edges and 28 indirect call sites. Earlier bounded EV-0293/EV-0295/EV-0315 traces classify selected damage, ActorValue, caster, and handle routes without finding a mapped AV11/AV12 sink. The 28 virtual sites and unresolved descendants prevent a global no-award conclusion.
6. PlayerCharacter slot 0xF7 resolves to FUN_140739050 and reaches FUN_14077d090, a skill-progress path. Heavy Armor, Light Armor, Block, and Sneak IDs use the matching ActorValues schema. This is GOG static evidence.

## Competing models and assessment

- H1, direct-wrapper bypass candidate: ProcessTrapHit retains the common HitData mitigation path and enters the shared receiver handler directly, omitting the known inline AV11/AV12 or AV9 skill branch. The direct call topology and visible AV15 handler call support this bounded model.
- H2, hidden award or ineffective mitigation: an unresolved virtual call or deeper callback may award AV11/AV12, or the trap path may not preserve positive damage/effective armor protection. This remains open.

The static evidence supports a vanilla physical-trap candidate for functional armor with suppressed hit-earned armor XP, but does not establish zero XP, positive final damage, effective protection, complete absence of indirect armor-skill awards, Steam behavior, active-profile winner, or vanilla reproduction. A matched Steam positive-damage/protection/raw-AVSK test remains the discriminator once the target profile and observer are verified.
""")
    local324[note324.relative_to(ROOT).as_posix()] = sha(note324)
    manifest324 = TX9 / "EV-0324-capture-manifest.json"
    write(manifest324, json.dumps({
        "evidence_id": "EV-0324",
        "captured_utc": "2026-10-17T22:10:37+00:00",
        "analysis_binary": {"product_version": "1.6.1179.0", "sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f", "distribution": "GOG"},
        "address_library_sha256": "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e",
        "query_metadata": [{
            "requested_rva": item.get("requested_rva"),
            "query_mode": item.get("query_mode"),
            "stdout_sha256": item.get("stdout_sha256"),
            "metadata_artifact": item.get("metadata_artifact"),
            "read_only": item.get("read_only"),
            "auto_analysis_disabled": item.get("auto_analysis_disabled"),
            "ok": item.get("ok"),
        } for item in metadata],
        "local_hashes": local324,
    }, indent=2, ensure_ascii=False))
    local324[manifest324.relative_to(ROOT).as_posix()] = sha(manifest324)

    common = {"captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE", "modified_state": False}
    add_evidence({
        **common, "id": "EV-0322", "kind": "record",
        "source": "Hash-verified five-official-master DA03Start DIAL/INFO join with QUST Lod alias and VMAD fragment mapping.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0008/EV-0322-note.md",
        "sha256": sha(note322),
        "runtime": "Installed Steam SkyrimSE.exe ProductVersion 1.6.1170.0 is separately identified in EV-0109. Fixed official source order only; no complete profile winner.",
        "lane": "mechanism_inference",
        "tools": ["tools/plugin_reader.py source-bound TES4 parser through strict dispatcher", "EXP-0062 GRUP-aware DIAL/INFO join", "schema-ordered QUST VMAD decoder"],
        "coverage": "All 15 logical DA03Start DIAL/INFO topic-child pairs in the five hash-verified official source files; fixed official-source copies, Lod alias, conditions, response fields, and fragment links. No profile-specific winner or runtime dialogue test.",
        "result": "The Lod stage-10 handoff topics require GetLevel >=10 and DA03Start stage <10. The unlevelled Lod stage-20 goodbye callback is a helper reward route, not a captured DA03 start. No level-one access/reproduction is established.",
        "related_evidence": ["EV-0321", "EV-0300", "EV-0260"],
        "local_hashes": {
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-analysis.json": sha(raw["EV-0322-da03-topic-analysis.json"]),
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topics.json": sha(raw["EV-0322-da03-topics.json"]),
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-topic-summary.json": sha(raw["EV-0322-da03-topic-summary.json"]),
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-da03-vmad.json": sha(raw["EV-0322-da03-vmad.json"]),
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-note.md": sha(note322),
        },
    })
    add_evidence({
        **common, "id": "EV-0323", "kind": "script",
        "source": "Classic PEX 3.2 bodies for DA03Start Lod stage-10 topics, Lod stage-20 goodbye callback, and DA03Start QF stage fragments.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0008/EV-0323-note.md",
        "sha256": sha(note323),
        "runtime": "Steam AE 1.6.1170.0 official scripts extracted from the tested base Skyrim - Misc.bsa; no runtime execution was observed.",
        "lane": "mechanism_inference",
        "tools": ["tools/archive_source_discovery.py base Misc BSA extraction", "tools/papyrus_pex.py PEX parser through strict dispatcher"],
        "coverage": "Four exact script streams with archive and PEX hashes/offsets retained. Base Misc BSA scope only; no global archive/loose-file negative.",
        "result": "Both level-gated stage-10 topic callbacks set DA03Start stage 10; QF Fragment_27 calls DA03.SetStage(5). The unlevelled goodbye only sets helper stage 20; stage 20 grants 25 gold and stage 200 stops the helper.",
        "related_evidence": ["EV-0322", "EV-0321"],
        "local_hashes": {
            ".local/alignment/transactions/TX-20261017-0008/EV-0323-da03-pex.json": sha(raw["EV-0323-da03-pex.json"]),
            ".local/alignment/transactions/TX-20261017-0008/EV-0323-note.md": sha(note323),
        },
    })
    add_evidence({
        **common, "id": "EV-0324", "kind": "native",
        "source": "Fresh identity-checked GOG ProcessTrapHit, HitData, inline armor resolver, UseSkill vtable-slot, and receiver call-edge queries.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0009/EV-0324-note.md",
        "sha256": sha(note324),
        "runtime": "GOG Skyrim AE 1.6.1179.0 static analysis, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Installed Steam AE 1.6.1170.0 is separate; no GOG RVA is transferred.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py existing GOG project through strict dispatcher with -noanalysis -readOnly", "tools/address_library_probe.py matching GOG vtable lookups", "CommonLibSSE-NG Actor, PlayerCharacter, HitData, and ActorValues schemas"],
        "coverage": "Direct ProcessTrapHit receiver route, common HitData construction, known inline armor/Block wrapper, visible UseSkill calls and one complete 89-direct-edge/28-indirect-site receiver census. Unresolved virtual descendants and live results remain outside scope.",
        "result": "The ProcessTrapHit PlayerCharacter route reaches common HitData construction then FUN_1406b9df0 without a direct call through the known FUN_1406bcaa0 AV11/AV12 or AV9 wrapper. The handler's visible UseSkill call is AV15 Sneak. This is only a candidate; no zero-XP, positive-final-damage, protection, Steam, profile-winner or vanilla-reproduction result is established.",
        "related_evidence": ["EV-0293", "EV-0261", "EV-0294", "EV-0295", "EV-0315", "EV-0217", "EV-0218", "EV-0222", "EV-0260"],
        "local_hashes": local324,
    })

    # Add the evidence-backed claim and mechanism summaries.
    append_after(ROOT / "research/CLAIMS.md", "| CL-L154 |", "CL-L155",
        "| CL-L155 | In the five hash-verified official Skyrim AE source files, Lod's DA03Start topics that hand off to helper stage 10 require GetLevel >= 10; QF stage 10 calls DA03.SetStage(5). The unlevelled Lod goodbye callback sets helper stage 20, whose captured stage-20/200 fragments grant a reward and stop the helper. | supported (bounded official-source DIAL/INFO/VMAD/PEX path) | [EV-0322], [EV-0323] | Fixed official order is not a full profile winner; runtime dialogue accessibility, level-one state/progression, other non-official routes, and vanilla reproduction remain unobserved. Function index 72 is unresolved; PEX scope is the tested base Misc BSA. |")
    append_tail(ROOT / "research/CLAIMS.md", "CL-L156",
        "| CL-L156 | In GOG AE 1.6.1179.0, the ProcessTrapHit PlayerCharacter route reaches common HitData construction and then FUN_1406b9df0 directly, without a direct call through the known FUN_1406bcaa0 wrapper containing AV11/AV12 or AV9 skill routing; the handler's visible UseSkill call carries AV15 Sneak. | supported (bounded build-attested GOG control-flow comparison; armor-XP bypass candidate) | [EV-0324], [EV-0293], [EV-0261], [EV-0294], [EV-0295], [EV-0217]–[EV-0223] | FUN_1406b9df0 retains 28 unresolved indirect call sites. No zero armor XP, positive final damage, effective protection, Steam equivalence, active-profile winner, or vanilla reproduction is established; the exact positive-damage/protection/raw-AVSK test remains open under EV-0260. |")
    append_tail(ROOT / "research/MECHANISMS.md", "## M-0052",
        """## M-0052 — Lod DA03Start level-gated handoff and unlevelled reward route (Q-0061)

The fixed-official-order DA03Start topic join identifies the Lod alias and maps the stage-10 helper handoffs to GetLevel >= 10. The helper's stage-10 fragment calls DA03.SetStage(5). The separately unlevelled stage-20 goodbye callback only advances DA03Start into a reward fragment; stage 20 grants 25 gold and stage 200 stops the helper [EV-0322], [EV-0323]. This closes the direct Lod callback candidate in source scope, not every profile/runtime route. No level-one access/reproduction or causal edge to OBJ-2 is established. Claim CL-L155 -> M-0052; Q-0061.

## M-0053 — Physical-trap direct receiver path past inline armor skill routing (Q-0062)

In GOG AE 1.6.1179.0, ProcessTrapHit's PlayerCharacter receiver reaches the shared HitData construction/resistance path and then calls FUN_1406b9df0 directly. The known FUN_1406bcaa0 wrapper contains the visible AV11/AV12 armor or AV9 Block skill call before it calls the same downstream handler. The trap handler's mapped UseSkill call is AV15 Sneak, making physical traps a vanilla candidate for functional armor with suppressed hit-earned armor XP [EV-0324], with route context in EV-0293, EV-0261, and EV-0217–EV-0223.

The candidate remains unverified: the handler has 28 unresolved indirect sites, and no positive final damage, effective protection, raw AVSK, Steam mapping, profile winner, or vanilla reproduction exists. No causal edge to OBJ-1 is supported. Claim CL-L156 -> M-0053; Q-0062.""")
    append_tail(ROOT / "research/KNOWLEDGE_GRAPH.md", "## Q-0061 — Lod direct start",
        """## Q-0061 — Lod DA03Start handoff and reward callback

Lod alias 6 -> level-10 DIAL/INFO response -> DA03Start stage 10 -> QF Fragment_27 -> DA03 stage 5 [EV-0322], [EV-0323]. The independent unlevelled goodbye callback -> helper stage 20 -> gold reward/helper stage 200 -> helper stop; no DA03 main-quest call appears in that captured callback. This supports a level-gated direct handoff and helper-only unlevelled reward route in the fixed official source view. Runtime accessibility, full profile order, and level-one progression remain unknown. No edge to OBJ-2 is supported. Claim CL-L155 -> M-0052.

## Q-0062 — ProcessTrapHit versus inline armor skill routing

Physical trap records/scripts -> Papyrus ObjectReference.ProcessTrapHit -> PlayerCharacter FUN_140679da0 -> shared HitData population/resistance (including AV39 and armor-base-factor work) -> FUN_1406b9df0 [EV-0261], [EV-0293], [EV-0324]. The separate known FUN_1406bcaa0 path performs AV11/AV12 armor or AV9 Block skill routing through Actor slot 0xF7 before calling FUN_1406b9df0 [EV-0217]–[EV-0223], [EV-0324]. The trap path therefore bypasses that direct wrapper and has one visible downstream AV15 Sneak skill call. This is a static functional-armor/zero-armor-XP candidate, not a measured no-award outcome: 28 indirect call sites, positive final damage, effective protection, exact Steam behavior, and raw AVSK remain unresolved [EV-0260], [EV-0295], [EV-0315].

The new edge is confined to OBJ-2's trap-to-hit-builder-to-receiver path. No shared call, state, ActorValue, quest record, ActiveEffect, or serialization dependency connects it to OBJ-1; no cross-objective causal edge is added. Claim CL-L156 -> M-0053; Q-0062.""")
    append_tail(ROOT / "research/CONTRADICTIONS.md", "C-OBJ2-TRAP-DIRECT-ROUTE",
        """## C-OBJ2-TRAP-DIRECT-ROUTE — Direct wrapper bypass versus hidden armor award

- **Model A:** ProcessTrapHit retains the common damage/armor calculation and routes to the receiver handler without traversing the known AV11/AV12 or AV9 skill-routing wrapper.
- **Model B:** an unresolved receiver virtual call or a deeper callback awards AV11/AV12, or the damage path fails to preserve positive damage and effective armor protection.
- **Evidence:** [EV-0324], [EV-0293], [EV-0261], [EV-0294], [EV-0295], [EV-0315], [EV-0217]–[EV-0223].
- **Current assessment:** Model A is supported as a bounded GOG 1.6.1179.0 path comparison; Model B remains unresolved because FUN_1406b9df0 has 28 indirect sites and no matched live Steam result.
- **Discriminant:** map descendants tied to FUN_1406b9df0 for AV11/AV12 sinks, then test the exact Steam 1.6.1170.0 profile/save for positive hit damage, effective protection, and raw Light/Heavy Armor AVSK before/after. No debug forcing validates a vanilla exploit.""")
    
    # Refine Q-0061 and add a ready OBJ-2 successor before closing its transaction.
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q61 = next(row for row in frontier["items"] if row["id"] == "Q-0061")
    next(h for h in q61["hypotheses"] if h["id"] == "Q61-H1").update({
        "model": "A Lod-owned direct topic starts DA03Start or DA03 below level 10 through an ungated callback.",
        "status": "falsified", "evidence": ["EV-0322", "EV-0323"],
    })
    next(h for h in q61["hypotheses"] if h["id"] == "Q61-H2").update({
        "model": "The known Lod stage-10 handoff is gated at level 10; the captured unlevelled callback only reaches the helper reward/stop route.",
        "status": "supported", "evidence": ["EV-0322", "EV-0323"],
    })
    q61["evidence"] = list(dict.fromkeys([*q61.get("evidence", []), "EV-0322", "EV-0323"]))
    q61["linked_claims"] = list(dict.fromkeys([*q61.get("linked_claims", []), "CL-L155"]))
    if not any(row.get("id") == "Q-0062" for row in frontier["items"]):
        frontier["items"].append({
            "id": "Q-0062", "objective": "OBJ-2", "kind": "mechanism", "status": "open",
            "question": "Does the ProcessTrapHit route deliver positive armor-mitigated damage to a player while bypassing armor-skill XP, or can an indirect receiver descendant reintroduce AV11/AV12 credit?",
            "hypotheses": [
                {
                    "id": "Q62-H1",
                    "model": "ProcessTrapHit preserves the shared HitData mitigation path and enters the receiver handler without traversing the known inline AV11/AV12/AV9 wrapper; no mapped downstream armor award is present.",
                    "predicted_discriminant": "Build-attested edges show FUN_140679da0 -> FUN_1407dd110 -> FUN_1406b9df0, no direct call through FUN_1406bcaa0, and the mapped handler UseSkill call uses AV15 rather than AV11/AV12.",
                    "status": "supported", "evidence": ["EV-0324", "EV-0293", "EV-0261"],
                },
                {
                    "id": "Q62-H2",
                    "model": "An unresolved indirect receiver descendant can still award AV11/AV12, or the trap path fails to preserve positive damage/effective armor protection.",
                    "predicted_discriminant": "Concrete PlayerCharacter targets for remaining relevant indirect sites reveal an AV11/AV12 skill sink or show that the exact damage route does not use the mapped armor-mitigation input.",
                    "status": "proposed", "evidence": ["EV-0295", "EV-0315", "EV-0260"],
                },
            ],
            "methods": [
                "Read EV-0324 and prior EV-0293/EV-0295/EV-0315 before querying; keep all GOG RVAs scoped to 1.6.1179.0.",
                "Resolve only remaining indirect sites and descendants in FUN_1406b9df0 that consume HitData, ActorValue, armor, or receiver state; prioritize any route to Actor::UseSkill slot 0xF7 or FUN_1406bcaa0.",
                "Compare selected call arguments with AV11 Heavy Armor, AV12 Light Armor, AV9 Block, and AV15 Sneak; preserve unresolved sites instead of claiming a global negative.",
                "Keep the exact Steam 1.6.1170.0 damage/protection/raw-AVSK test separate; profile order, disposable level-one save, and loaded observer remain unverified under EV-0260.",
            ],
            "blocked_by": [], "evidence": ["EV-0324", "EV-0293", "EV-0261", "EV-0295", "EV-0315", "EV-0260"],
            "priority": 1.0, "information_gain": 0.99,
            "next_action": "Map the highest-information unresolved virtual targets in FUN_1406b9df0 that could feed Actor::UseSkill slot 0xF7 or HitData-derived damage, beginning with PlayerCharacter targets and arguments adjacent to the 28 indirect sites. Do not claim zero XP while any relevant path or live AVSK delta remains unresolved.",
            "linked_claims": ["CL-L156"], "successors": [], "attempts": [],
            "cross_source_assessment": "This is an OBJ-2 trap/armor mechanism comparison. No shared call, quest state, ActorValue predicate, ActiveEffect, or serialization dependency connects this route to OBJ-1 level-gated access. No cross-objective edge is added.",
        })
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # Complete the source evidence documents for both experiments.
    write(ROOT / "experiments/EXP-0062-da03-lod-direct-start/results.md", """# Results

The hash-verified five-official-master join contains 15 logical DA03Start DIAL/INFO topic-child pairs. Lod's stage-10 handoff topics 000D7930 -> 000D7933 and 000E0D3F -> 000E0D47 require GetLevel >= 10 and helper stage below 10. Their PEX callbacks set helper stage 10; its QF fragment then calls DA03.SetStage(5) [EV-0322], [EV-0323].

The unlevelled Lod goodbye path 0010F58E -> 0010F590 sets only helper stage 20. The captured stage-20 fragment gives 25 gold and moves to stage 200, whose fragment stops the helper. No direct DA03 start/stage call appears in that callback [EV-0322], [EV-0323].

Q61-H1 is falsified and Q61-H2 supported within the fixed official source layer and tested base-Misc-BSA PEX scope. This closes the Lod direct-start candidate only. It establishes neither a profile winner nor runtime dialogue accessibility, level-one main quest state/progression, useful access, or vanilla reproduction. No cross-objective edge to OBJ-2 is justified.
""")
    write(ROOT / "experiments/EXP-0062-da03-lod-direct-start/implications.md", """# Implications

The known Lod handoff into DA03 runs through DA03Start stage 10, and both captured direct Lod responses that set this stage require level 10. The unlevelled goodbye response is a reward/helper-stop route rather than an alternate main-quest start [EV-0322], [EV-0323].

Do not generalize this to every profile or runtime entry path: the join is the fixed official source layer, the complete active order is not configured, and no exact Steam level-one dialogue/quest-state observation exists [EV-0260]. Function-index-72 semantics and the tested base-Misc-BSA extraction scope remain explicit boundaries.

No OBJ-1/OBJ-2 causal edge is supported. Continue P0 research with the independent ProcessTrapHit route candidate (Q-0062).
""")
    exp63 = ROOT / "experiments/EXP-0063-trap-direct-receiver-candidate"
    write(exp63 / "README.md", """# EXP-0063 — ProcessTrapHit direct receiver candidate

**Question:** Does ProcessTrapHit preserve the shared HitData armor-mitigation path while bypassing the known inline AV11/AV12 armor-skill route, and what unresolved calls could reintroduce armor XP?

**Transaction:** TX-20261017-0009 / Q-0062.

This is a GOG 1.6.1179.0 static candidate investigation. It does not claim zero armor XP or Steam equivalence. EV-0324 preserves identity, raw captures, call-edge counts, and limits.
""")
    write(exp63 / "hypothesis.md", """# Hypothesis

A physical trap hit may meet OBJ-2 if its PlayerCharacter route reaches the common HitData builder/resistance calculation and then reaches damage handling without traversing the known inline AV11/AV12 armor-award wrapper.

The strongest rival is that an unresolved receiver virtual call or deeper callback still awards AV11/AV12, or that the trap damage path does not preserve positive damage and effective armor protection. GOG source evidence can narrow the path; only a matched Steam 1.6.1170.0 hit with raw AVSK can validate the gameplay result.
""")
    write(exp63 / "predicted-outcomes.md", """# Predicted outcomes

- **H1, wrapper bypass candidate:** direct edges show FUN_140679da0 -> FUN_1407dd110 -> FUN_1406b9df0; known FUN_1406bcaa0 armor/Block skill routing is separate; the mapped handler UseSkill call is AV15. This supports a candidate only.
- **H2, hidden award or ineffective protection:** a concrete descendant from an unresolved virtual site reaches AV11/AV12 skill progress, or the trap path cannot deliver positive damage with functioning armor.
- A GOG-only result cannot establish installed Steam behavior. Vanilla reproduction requires positive damage with worn armor and unchanged raw Light/Heavy Armor AVSK on the exact verified Steam target and full active order.
""")
    write(exp63 / "protocol.md", """# Protocol

1. Verify GOG 1.6.1179.0 and matching Address Library identity for each Ghidra query; use the existing project in read-only/no-analysis mode.
2. Read EV-0324 and EV-0293/EV-0295/EV-0315 before querying. Resolve only indirect/descendant routes tied to HitData, ActorValue updates, player damage, armor, or slot 0x7B8.
3. Preserve unresolved virtual sites and distinguish direct edges, mapped vtable targets, inference, and live behavior.
4. Keep the Steam AE 1.6.1170.0 test separate. It requires a complete exact active order, disposable level-one save, raw AVSK before/after, positive damage, and effective protection; EV-0260 records the current readiness gap.
5. Do not use console forcing, injected scripts, or altered plugins as vanilla validation.
""")
    write(exp63 / "results.md", """# Results

EV-0324 confirms the bounded route comparison: ProcessTrapHit uses shared HitData construction/resistance then calls FUN_1406b9df0 directly. The known FUN_1406bcaa0 wrapper contains the visible AV11/AV12 armor or AV9 Block branch before reaching the same handler. One visible UseSkill call in the handler carries AV15 Sneak. The handler retains 28 unresolved indirect sites.

No zero armor XP, positive final damage, effective protection, Steam equivalence, profile winner, or vanilla reproduction is established. The next static discriminator is targeted mapping of unresolved descendants with potential AV11/AV12 or UseSkill routes.
""")
    write(exp63 / "implications.md", """# Implications

This is a vanilla physical-trap candidate based on control-flow separation after shared HitData construction. It is not yet a useful armor/no-XP exploit because indirect sites, effective protection, positive hit damage, and raw armor AVSK remain open.

There is no causal edge to OBJ-1 quest gates. Continue the bounded static call-path work and keep the exact Steam gameplay test ready when EV-0260 prerequisites become available.
""")

    # Preserve a compact capture manifest for the two Lod artifacts.
    source_hashes = {
        str(path.relative_to(ROOT).as_posix()): sha(path)
        for path in raw.values()
    }
    write(TX8 / "EV-0322-0323-capture-manifest.json", json.dumps({
        "transaction_id": "TX-20261017-0008",
        "official_master_hashes": {
            "Skyrim.esm": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
            "Update.esm": "c1795e0a1218da45dbfd523f064f1857b42805c49714c46091e75277e525aed9",
            "Dawnguard.esm": "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4",
            "HearthFires.esm": "ad4ca9f32c81e7ddd3e39ec95e03b07841f20712989e598778442ea69b6e6a97",
            "Dragonborn.esm": "5f44f343552688c04f73bf83de58b90f70c7376b133fbbcb56b6fe33acf8778b",
        },
        "local_hashes": source_hashes | {
            ".local/alignment/transactions/TX-20261017-0008/EV-0322-note.md": sha(note322),
            ".local/alignment/transactions/TX-20261017-0008/EV-0323-note.md": sha(note323),
        },
    }, indent=2, ensure_ascii=False))

    print(json.dumps({
        "registered": ["EV-0322", "EV-0323", "EV-0324"],
        "note_hashes": {"EV-0322": sha(note322), "EV-0323": sha(note323), "EV-0324": sha(note324)},
        "frontier_successor": "Q-0062",
        "ghidra_query_count": len(metadata),
    }, indent=2))


if __name__ == "__main__":
    main()
