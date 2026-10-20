#!/usr/bin/env python3
"""Register caller 57/tag 0x5F as a bounded perk-rank update route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
BASES = {
    ".local/ghidra/gog-query-20261019T212906Z": "24b5477fb46a5861fc7e5de26eea7ef14a33cf15dbe41637fd2423b27a7cfb8b",
    ".local/ghidra/gog-query-20261019T213011Z": "1de49998b7145ad9c7113b0bedac786056a123106e72132628d7c6c7c13357c7",
    ".local/ghidra/gog-query-20261019T213114Z": "bda69619351509e3d476ceb9ff42cfcb2176bce1ceafdf46c20ec14b91d27676",
    ".local/ghidra/gog-query-20261019T213218Z": "2d519c130df9b783b54a8d653cbacf4c026affba6fc49b362ae31c57c5b79fa1",
    ".local/ghidra/gog-query-20261019T213410Z": "a470053265d267a096b849decafaa64f27eaf7eb4943b80e1c96d9d850136b66",
    ".local/ghidra/gog-query-20261019T213514Z": "2e9c5414dc73bec6ffaea0d5c1ba7a058551eb893a11f57c707c824d92bcbc5c",
    ".local/ghidra/gog-query-20261019T213632Z": "26cac2173fe34dc9e2ddedadf7293a3b170ffd4bbb5981c71f20a1be89d45779",
    ".local/ghidra/gog-query-20261019T213855Z": "8781ad80220fb73a19783107275f39edfec20a2db5a17b4f06d69d21b75a1d1b",
}
META_HASHES = {
    ".local/ghidra/gog-query-20261019T212906Z.meta.json": "b0f9bb5c3a3bf01aaec531d6dc72e7b39fe503f4d225bf62fce5cba353cf1909",
    ".local/ghidra/gog-query-20261019T213011Z.meta.json": "c41bcb0c89ebfc8ae27182b3a13a88f9468cd54166599c63a4df45f6d279150e",
    ".local/ghidra/gog-query-20261019T213114Z.meta.json": "d239efec0a7cd26d8faf8311a83d581ad74d4e751f4a0169949cc8b199c168ec",
    ".local/ghidra/gog-query-20261019T213218Z.meta.json": "92c527fb6b36413a8b11d944baa7963d028e774796de27967637cb251c7df514",
    ".local/ghidra/gog-query-20261019T213410Z.meta.json": "63e92707555cac2a539c7a847852dc907da373b92de20320faaae2e200ee6999",
    ".local/ghidra/gog-query-20261019T213514Z.meta.json": "808aeb010ceeb34ef4c48e5aa319c499b26053b6b33deb34b6e9bd86d45b272e",
    ".local/ghidra/gog-query-20261019T213632Z.meta.json": "c5e067e4fd3f0a75e73fd0a0ccb180b87c496d608b19529a0b77474bad1961f2",
    ".local/ghidra/gog-query-20261019T213855Z.meta.json": "221bd50283c0d805e46df262babb100a566f16024b148195437d344ef3f581aa",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate marker: " + marker)
    write(path, old.rstrip() + "\n\n" + body.strip())


def main() -> None:
    raws: dict[str, str] = {}
    local_hashes: dict[str, str] = {}
    metas = []
    for base, expected in BASES.items():
        rel = base + ".stdout.raw"
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("capture/hash mismatch: " + rel)
        raws[base] = path.read_text(encoding="utf-8", errors="replace")
        local_hashes[rel] = expected
    for rel, expected in META_HASHES.items():
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
    proof_sets = [
        (".local/ghidra/gog-query-20261019T213218Z", [
            "TARGET_RVA=0x750D80", "caller=FUN_14074b150", "caller=FUN_14074b220",
            "BGSPerk::AddPerkVisitor::vftable", "*(byte *)(param_2 + 0x52) < param_3",
            "FUN_140658d00(DAT_14319a7c0,param_1,param_2,0,param_3);",
            "FUN_140658d00(undefined8 param_1,longlong param_2,longlong param_3,byte param_4,byte param_5)",
            "local_88[0] = 0x5f;", "FUN_14065b800(param_1,local_88);",
        ]),
        (".local/ghidra/gog-query-20261019T212906Z", [
            "DECOMPILATION_BEGIN=FUN_1403906c0", "INDIRECT_CALL_SITE_COUNT=2",
            "(**(code **)(*plVar2 + 0x58))(plVar2,param_2);",
            "(**(code **)(*plVar2 + 0x50))(plVar2,param_2);",
        ]),
        (".local/ghidra/gog-query-20261019T213011Z", [
            "DECOMPILATION_BEGIN=FUN_14068f020", "FUN_1407177b0(*(longlong *)(param_1 + 0xf8),param_1,param_2);",
        ]),
        (".local/ghidra/gog-query-20261019T213114Z", [
            "DECOMPILATION_BEGIN=FUN_1407177b0", "BGSPerk::FindPerkInRanksVisitor::vftable",
            "(**(code **)(*param_2 + 2000))(param_2,&local_28);",
        ]),
        (".local/ghidra/gog-query-20261019T213410Z", [
            "INCOMING_CALLER_FUNCTION_COUNT=0", "FUN_140750d80();", "CALL 0x140750d80",
        ]),
        (".local/ghidra/gog-query-20261019T213514Z", [
            "INCOMING_CALLER_FUNCTION_COUNT=0",
            "FUN_140750d80(param_1,param_2,CONCAT71((int7)(uVar6 >> 8),1));",
        ]),
        (".local/ghidra/gog-query-20261019T213632Z", [
            "VTABLE_RTTI_SIGNATURE=0x83485740", "VTABLE_RTTI_CENSUS_COMPLETE=true",
        ]),
        (".local/ghidra/gog-query-20261019T213855Z", [
            "POINTER_TABLE_BASE_RVA=0x18AD540", "POINTER_TABLE_XREF_COUNT=0",
            "POINTER_TABLE_READ_COUNT=6", "value:0x14074B150", "value:0x14074B220",
            "POINTER_TABLE_SCAN_COMPLETE=true",
        ]),
    ]
    for base, tokens in proof_sets:
        for token in tokens:
            if token not in raws[base]:
                raise SystemExit("proof token missing: " + token)

    note = EXP / "EV-0639-caller57-tag5f-perk-rank-add.md"
    write(note, """# EV-0639 — Caller 57 tag-0x5F perk-rank addition and callbacks

## Competing models and discriminants

- H1, rank-list update: the event reports a perk rank insertion/update. It predicts the AddPerkVisitor, rank-count bound, PlayerCharacter rank-list mutation, and old/new-rank callback routing.
- H2, level-one perk-gate bypass: this route can place a perk on a level-one PlayerCharacter despite a level requirement. It predicts an ordinary caller path into the add routine without a level predicate and a verified level-gated perk whose rank becomes available at level one. A rank-count bound alone is insufficient.
- H3, combat/armor-skill route: the event or a rank callback reaches HitData, effective protection, AV11/AV12, or UseSkill. It predicts a producer-backed data/control edge to a mapped sink; unresolved per-rank virtual calls do not establish one.

## Direct GOG evidence

All captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Their metadata verifies read-only execution, disabled auto-analysis, and executable identity. These RVAs do not transfer to Steam AE 1.6.1170.0.

- FUN_140658d00 writes tag 0x5F, derives a dword with FUN_1402ef8f0, stores another object pointer and two byte values, then queues through FUN_14065b800. Worker case 0x5F resolves a handle and calls FUN_1403906c0 with the object and both payload bytes [EV-0637], [EV-0639].
- The sole analyzed event producer is FUN_140750d80, called from FUN_14074b150 and FUN_14074b220. It rejects a null perk. If requested rank is zero, it reads the current matching rank through FUN_14068f020/FUN_1407177b0 and increments it. It returns when the request exceeds the byte at perk+0x52, scans PlayerCharacter+0x4b8 with a Ghidra-labeled BGSPerk::AddPerkVisitor, stores a perk-rank pair, and emits tag 0x5F with old rank 0 and the requested new rank [EV-0639].
- FUN_14068f020 calls FUN_1407177b0 through a nonnull nested pointer at +0xF8. FUN_1407177b0 uses the BGSPerk::FindPerkInRanksVisitor label, dispatches through PlayerCharacter slot +0x7D0, and returns a matched rank byte or zero. This is a current-rank lookup, not a Player-level read [EV-0639].
- FUN_1403906c0 scans a collection at +0x60/count +0x70. It calls each entry's virtual slot +0x58 when stored-rank+1 matches the old byte, or slot +0x50 when it matches the new byte; then it invokes FUN_1403918a0 and FUN_140391660. Two indirect sites remain, so callback effects are unresolved [EV-0639].
- FUN_14074b220 requires a nonnull object, updates a reference-counted collection at +0x4E8/+0x4F8, and may call FUN_140750d80 with rank 1 after checking a separate list at +0x4D0/+0x4E0. FUN_14074b150's decompilation omits displayed call arguments, but its captured instructions preserve incoming RCX/RDX/R8 across the call to FUN_140750d80. Neither wrapper has an analyzed incoming direct caller [EV-0639].
- A six-entry function-pointer region at RVA 0x18AD540 contains FUN_14074b150 and FUN_14074b220, but its bounded scan reports zero references to the table base. The RTTI check returns signature 0x83485740, not a validated MSVC vtable. The owner and runtime invokers remain unknown [EV-0639].

## Result and limits

H1 is supported for the captured static rank-list route and tag-0x5F event. The visible requested-rank limit is the perk's rank-count byte; this bounded path does not read Player level or establish perk eligibility. H2 remains proposed because wrapper invokers, perk records, and a natural level-one call are not established. H3 has no mapped direct sink, but the per-rank virtual callbacks remain unresolved. This is not a validated vanilla exploit, level-one access result, armor-XP bypass, Steam result, or bounty resolution. No causal edge is added to OBJ-1 quest gates, HitData, protection, AV11/AV12, or UseSkill.

## Next action

Continue the exact worker-caller census at caller 58/62, FUN_140658dd0; preserve the unknown owner of the rank-list wrappers as a later level-one access discriminator.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    ids = {row.get("id") for row in evidence.get("items", [])}
    if "EV-0639" in ids or not {"EV-0344", "EV-0637"} <= ids:
        raise SystemExit("evidence ID conflict or missing context")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    evidence["items"].append({
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0639", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 57/tag 0x5F, AddPerkVisitor producer, current-rank visitor, dispatcher fanout, wrapper contexts, and bounded function-pointer/RTTI checks.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T213218Z.stdout.raw",
        "sha256": BASES[".local/ghidra/gog-query-20261019T213218Z"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries, auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge, pointer-table, and RTTI queries"],
        "coverage": "Tag-0x5F builder/dispatcher; AddPerkVisitor rank path; current-rank visitor; per-rank callbacks; both wrappers; argument-register correction; six-entry pointer table and invalid RTTI result.",
        "result": "Caller 57 emits tag 0x5F on a perk-rank list addition/update path. Requested rank zero defaults to current rank+1 and the visible bound is perk+0x52; no Player-level gate is shown. Wrapper invokers and per-rank dynamic callbacks remain unresolved. No level-one access, mapped HitData/protection/armor-skill edge, vanilla reproduction, or bounty result is established.",
        "local_hashes": local_hashes, "related_evidence": ["EV-0344", "EV-0637"],
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L452 |",
        "| CL-L452 | In GOG AE 1.6.1179.0, caller 57 tag 0x5F reports a perk-rank list addition/update; the bounded AddPerkVisitor path defaults rank zero to current rank+1 and limits the request by perk byte +0x52. | supported for captured static route | [EV-0637], [EV-0639] | Wrapper invokers, perk eligibility records, Player-level gating, runtime rank callbacks, and Steam behavior remain unresolved; no level-one access or OBJ-2 result follows. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0192 —",
        """## M-0192 — Tag-0x5F perk-rank addition and per-rank callback fanout (EV-0639)

Caller 57 FUN_140658d00 writes tag 0x5F with an object-derived dword, another object pointer, and two rank bytes; worker case 0x5F resolves a handle and calls FUN_1403906c0 [EV-0637], [EV-0639]. The sole analyzed producer FUN_140750d80 uses a Ghidra-labeled AddPerkVisitor to scan PlayerCharacter+0x4b8, adds or updates a perk-rank pair, and emits old rank 0/new requested rank. Rank 0 defaults to current matching rank+1, and the explicit bound is the byte at perk+0x52 [EV-0639].

The current-rank lookup uses FUN_14068f020/FUN_1407177b0 and a FindPerkInRanksVisitor label, returning a matched rank byte through PlayerCharacter slot +0x7D0. FUN_1403906c0 fans old/new ranks to per-entry slots +0x58/+0x50; both remain unresolved. Wrapper FUN_14074b150 and FUN_14074b220 have no analyzed incoming direct callers; their candidate six-entry pointer region has no identified table-base references and fails the RTTI check. No Player-level eligibility check, verified level-one caller, HitData, protection, AV11/AV12, UseSkill, armor XP, or quest-start edge is established. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L452.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ1-Q79-PERK-RANK-ADD-VS-LEVEL-GATE",
        """## C-OBJ1-Q79-PERK-RANK-ADD-VS-LEVEL-GATE — rank-list API versus level-one perk access

- Model A: caller 57's AddPerkVisitor route can set a perk rank without evaluating a Player-level requirement, so a natural caller might expose a level-gated perk at level one.
- Model B: the observed native path mutates a rank list under a rank-count bound; a separate caller, record condition, or runtime path may enforce eligibility, and wrapper invokers are not identified.
- Evidence: tag-0x5F builder/dispatcher, AddPerkVisitor rank path, current-rank lookup, two wrappers, and bounded function-table/RTTI screen [EV-0637], [EV-0639].
- Assessment: Model B is the conservative result. The captured path checks perk+0x52 but does not read Player level; the wrappers have no analyzed incoming direct callers and the candidate table is not RTTI-validated. This does not prove a bypass, level-one perk access, quest gate change, or ordinary vanilla invocation. No OBJ-1 causal edge is added.
- Discriminant: identify runtime wrapper callers, trace a verified level-gated perk record into this route, and observe rank membership and gate state on a clean level-one path. Preserve callback uncertainty and the GOG/Steam boundary.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0639 maps caller 57 tag-0x5F perk-rank addition",
        """### EV-0639 maps caller 57 tag-0x5F perk-rank addition

The AddPerkVisitor route and caller 56's FindPerkInRanksVisitor cleanup both use PlayerCharacter rank-list field +0x4b8 [EV-0638], [EV-0639]. Caller 57 adds or updates a rank entry under a perk rank-count bound and dispatches old/new rank bytes to unresolved callbacks; caller 56 conditionally removes a matched entry. This is a shared list lifecycle, not proof of a level-one perk grant or shared quest/combat cause. No causal edge is added to OBJ-1, HitData, effective protection, AV11/AV12, UseSkill, or armor XP. Claim mapping: CL-L451/CL-L452 -> M-0191/M-0192.""")
    append_once(EXP / "results.md", "### Caller 57/62: tag-0x5F perk-rank addition (EV-0639)",
        """### Caller 57/62: tag-0x5F perk-rank addition (EV-0639)

Caller 57 writes tag 0x5F with an object-derived dword, another object pointer, and two bytes. Its sole analyzed producer FUN_140750d80 scans PlayerCharacter+0x4b8 with a Ghidra-labeled AddPerkVisitor, defaults rank 0 to current rank+1, bounds the request by perk+0x52, stores the rank pair, and emits the worker event [EV-0639]. Dispatcher case 0x5F resolves a handle and calls FUN_1403906c0 with both rank bytes [EV-0637], [EV-0639].

FUN_1403906c0 invokes per-rank slots +0x58/+0x50 and has two unresolved indirect sites. Wrapper FUN_14074b150/FUN_14074b220 have no analyzed incoming direct callers; the six-entry pointer region at RVA 0x18AD540 has no identified table-base references and invalid RTTI. The bounded path shows a perk rank-count bound, not a Player-level gate. It does not establish level-one access or a vanilla bypass, and no mapped HitData/protection/AV11/AV12/UseSkill sink appears. Continue caller 58/62 FUN_140658dd0.""")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    existing_hypotheses = {row.get("id") for row in item.get("hypotheses", [])}
    if {"Q79-H155", "Q79-H156"} & existing_hypotheses:
        raise SystemExit("caller-57 hypotheses already exist")
    next_action = ("Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658dd0 "
                   "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
                   "review worker caller 58/62 FUN_140658dd0 for its exact tag, payload, producer, and "
                   "dispatcher route, then continue the bounded caller census.")
    item["hypotheses"].extend([
        {"id": "Q79-H155",
         "model": "Caller 57 tag 0x5F reports a perk-rank list addition/update; rank 0 defaults to current rank+1 and the request is bounded by perk+0x52.",
         "predicted_discriminant": "Builder, sole producer, current-rank visitor, PlayerCharacter list field, rank-count comparison, and dispatcher callback fanout establish the captured route; per-rank callbacks remain unresolved.",
         "status": "supported", "evidence": ["EV-0637", "EV-0639"]},
        {"id": "Q79-H156",
         "model": "A natural wrapper caller can invoke caller 57's rank-add route at level one to satisfy a perk or level-gated content requirement, or a per-rank callback connects the event to HitData/armor skill.",
         "predicted_discriminant": "Resolve wrapper owner/callers, identify a verified level-gated perk and level-one invocation, or show a producer-backed callback edge to mapped HitData/protection/AV11/AV12/UseSkill. The rank-count bound and invalid RTTI candidate table prove neither outcome.",
         "status": "proposed", "evidence": ["EV-0639", "EV-0260"]},
    ])
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0639"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L452"]))
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 57/tag-0x5F is bounded as perk-rank addition with unresolved wrapper callers and callbacks; continue caller 58.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    old = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 57 of 62 initially uninspected worker callers are reviewed, with 5 remaining."
    new = "Q-0079/TX-20261018-0013 remains active on OBJ-2: 58 of 62 initially uninspected worker callers are reviewed, with 4 remaining."
    if state.count(old) != 1:
        raise SystemExit("STATE active caller-count mismatch")
    state = state.replace(old, new, 1)
    old_summary = "EV-0638 maps caller 56/tag 0x58 to PlayerCharacter collection removal and conditional RTTI-verified perk-rank cleanup; one runtime PlayerCharacter vtable slot remains unresolved, with no mapped direct HitData/armor sink."
    new_summary = old_summary + " EV-0639 maps caller 57/tag 0x5F to perk-rank addition under a perk rank-count bound; wrapper callers and per-rank virtual effects remain unresolved, with no level-one bypass or mapped HitData/armor sink."
    if state.count(old_summary) != 1:
        raise SystemExit("STATE caller-56 summary mismatch")
    state = state.replace(old_summary, new_summary, 1)
    count_old = "Q-0079 has 57/62 initially uninspected worker callers reviewed; 5 remain."
    count_new = "Q-0079 has 58/62 initially uninspected worker callers reviewed; 4 remain."
    if count_old in state:
        state = state.replace(count_old, count_new, 1)
    b = chr(96)
    old_next = ("**Selected next line:** run " + b + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658d00 "
                "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600" + b +
                "; review worker caller 57/62 " + b + "FUN_140658d00" + b +
                " for its exact tag, payload and producer, then continue the bounded caller census. Caller 56 tag 0x58 "
                "is a PlayerCharacter perk-rank cleanup route; the runtime vtable slot +0x650 remains unresolved.")
    new_next = ("**Selected next line:** run " + b + "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658dd0 "
                "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600" + b +
                "; review worker caller 58/62 " + b + "FUN_140658dd0" + b +
                " for its exact tag, payload, producer and dispatcher route, then continue the bounded caller census. "
                "Caller 57 tag 0x5F is a perk-rank addition path; wrapper invokers and per-rank callbacks remain unresolved.")
    if state.count(old_next) != 1:
        raise SystemExit("STATE selected-next line mismatch")
    state = state.replace(old_next, new_next, 1)
    write(state_path, state)

    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 callers 56–57 (EV-0639)",
        """## Cross-domain synthesis — Q-0079 callers 56–57 (EV-0639)

Callers 56 and 57 expose opposite operations over the same PlayerCharacter rank-list field +0x4b8: caller 56's RTTI-verified FindPerkInRanksVisitor locates/removes a matching entry, while caller 57's AddPerkVisitor path inserts or updates a perk-rank pair [EV-0638], [EV-0639]. Caller 57 defaults rank zero to current rank+1 and enforces only the captured perk rank-count byte +0x52. The two callers support a shared list-lifecycle model; they do not identify a level-one caller or prove perk level requirements are bypassed. Old/new rank callbacks remain unresolved. No edge is added to OBJ-1 quest gates or OBJ-2 HitData/protection/armor XP. Continue caller 58/62 FUN_140658dd0 and preserve wrapper-table ownership for a later level-one discriminator.""")
    print("Registered EV-0639/CL-L452/M-0192 and checkpointed caller 58.")


if __name__ == "__main__":
    main()
