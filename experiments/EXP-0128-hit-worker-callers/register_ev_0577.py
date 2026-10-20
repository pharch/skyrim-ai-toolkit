from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
IDENTITY = {
    "analysis_binary_product_version": "1.6.1179",
    "analysis_binary_sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
}
CAPTURES = [
    ("gog-query-20261019T170045Z", "0x6586f0", "requested_rva"),
    ("gog-query-20261019T170213Z", "0x9ec930", "requested_rva"),
    ("gog-query-20261019T170740Z", "0x9ed4a0", "requested_rva"),
    ("gog-query-20261019T165124Z", "0x659160", "requested_rva"),
    ("gog-query-20261019T170314Z", "0x6e4ba0", "requested_rva"),
    ("gog-query-20261019T170424Z", "0x71e250", "requested_rva"),
    ("gog-query-20261019T170523Z", "0x766520", "requested_rva"),
    ("gog-query-20261019T170620Z", "0x1ffda78", "requested_address_rva"),
    ("gog-query-20261019T170921Z", "0x9d8", "requested_search_displacement"),
    ("gog-query-20261019T171236Z", "0x765e30", "requested_rva"),
    ("gog-query-20261019T171400Z", "0x8062d0", "requested_rva"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


loaded: dict[str, dict] = {}
for stem, target, key in CAPTURES:
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    observed = meta.get(key)
    if not meta.get("ok") or str(observed).lower() != target:
        raise SystemExit(f"capture identity/request check failed for {stem}: {key}={observed!r}")
    if any(meta.get(k) != v for k, v in IDENTITY.items()):
        raise SystemExit(f"GOG binary identity check failed for {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only/analysis gate failed for {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"raw capture hash mismatch for {stem}")
    loaded[stem] = {
        "meta": meta,
        "raw": raw,
        "stderr": stderr,
        "meta_path": meta_path,
        "hashes": {
            f".local/ghidra/{raw.name}": sha(raw),
            f".local/ghidra/{stderr.name}": sha(stderr),
            f".local/ghidra/{meta_path.name}": sha(meta_path),
        },
    }


def evidence(eid: str, source: str, primary_stem: str, tools: list[str], coverage: str, result: str, related: list[str], stems: list[str]) -> dict:
    primary = loaded[primary_stem]
    hashes: dict[str, str] = {}
    for stem in stems:
        hashes.update(loaded[stem]["hashes"])
    return {
        "kind": "native",
        "edition": "AE",
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "id": eid,
        "source": source,
        "artifact": f"private-local:.local/ghidra/{primary['raw'].name}",
        "sha256": sha(primary["raw"]),
        "captured_utc": primary["meta"]["captured_utc"],
        "tools": ["strict Python 3.12 dispatcher", *tools],
        "coverage": coverage,
        "result": result,
        "local_hashes": hashes,
        "related_evidence": related,
    }


items = [
    evidence(
        "EV-0577",
        "Identity-checked read-only GOG analysis of worker caller 40/62 FUN_1406586f0, producer FUN_1409ec930, and Actor native registration",
        "gog-query-20261019T170045Z",
        [
            "tools/ghidra_probe.py --rva 0x6586f0 --list-call-edges --timeout 600",
            "tools/ghidra_probe.py --rva 0x9ec930 --list-call-edges --follow-direct-calls 4 --follow-incoming-calls 12 --timeout 600",
            "tools/ghidra_probe.py --rva 0x9ed4a0 --list-call-edges --follow-direct-calls 8 --timeout 600",
        ],
        "FUN_1406586f0 builds worker tag 0x2a after converting its two Actor arguments through FUN_1402ef8f0. Its captured producer FUN_1409ec930 is registered by FUN_1409ed4a0 as Papyrus native Actor.StartCombat. The wrapper rejects a null second Actor; its queueing branch requires the first Actor not be the player, both Actor virtual +0x4c8 predicates false, both process fields at Actor+0xf8 non-null, and no disallowed dialogue case. It then calls FUN_1406586f0 with the two Actors. These are preconditions on an existing-Actor combat request, not evidence of quest or encounter creation.",
        "The bounded producer confirms a Papyrus Actor.StartCombat route into a deferred tag-0x2a worker. It contains no direct GetLevel, quest-start, Story Manager, or encounter-spawn call. The API can request combat between already-present process-backed Actors; it does not establish access to level-gated content or an OBJ-1 exploit. GOG static evidence does not prove Steam runtime behavior.",
        ["EV-0315", "EV-0291", "EV-0260"],
        ["gog-query-20261019T170045Z", "gog-query-20261019T170213Z", "gog-query-20261019T170740Z"],
    ),
    evidence(
        "EV-0578",
        "Identity-checked read-only GOG trace of tag-0x2a worker fallback and player-target transition guard",
        "gog-query-20261019T170314Z",
        [
            "tools/ghidra_probe.py --rva 0x659160 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "tools/ghidra_probe.py --rva 0x6e4ba0 --list-call-edges --timeout 600",
            "tools/ghidra_probe.py --rva 0x71e250 --list-call-edges --timeout 600",
        ],
        "Fallback worker case 0x2a resolves two Actor handles and, after process/object predicates, calls FUN_1406e4ba0. That helper's bounded body calls FUN_14071e250. In FUN_14071e250, when one argument is the player global DAT_143188918, a branch compares DAT_141ffda78 with FUN_140766520(player) and may decline the transition. No direct quest-start, Story Manager, encounter-spawn, HitData, AV11/AV12, or UseSkill call is present in the bounded path. The compared global's meaning was not identified by this capture.",
        "Tag 0x2a defers an Actor combat transition. The player-target branch contains a threshold comparison, but its existence alone does not identify a level check. The exact field returned by FUN_140766520 and the global threshold require separate discrimination; no causal link to a level-gated quest or armor-XP path is established.",
        ["EV-0577", "EV-0260", "EV-0572"],
        ["gog-query-20261019T165124Z", "gog-query-20261019T170314Z", "gog-query-20261019T170424Z"],
    ),
    evidence(
        "EV-0579",
        "Identity-checked read-only GOG discrimination of Actor+0x9d8 component field provenance against the direct Actor.Level model",
        "gog-query-20261019T171400Z",
        [
            "tools/ghidra_probe.py --rva 0x766520 --list-call-edges --timeout 600",
            "tools/ghidra_probe.py --address-rva 0x1ffda78 --timeout 600",
            "tools/ghidra_probe.py --search-displacement 0x9d8 --timeout 600",
            "tools/ghidra_probe.py --rva 0x765e30 --list-call-edges --timeout 600",
            "tools/ghidra_probe.py --rva 0x8062d0 --list-call-edges --timeout 600",
        ],
        "FUN_140766520 returns the 32-bit field at offset +0x18 from the object at Actor+0x9d8, or zero when that object is absent. The only captured reader of DAT_141ffda78 is FUN_14071e250. FUN_140765e30 lazily creates the Actor+0x9d8 component and calls FUN_1408062d0 before FUN_140805c40; it is also called by FUN_1406bc400, whose prior bounded context is associated with an AV15/UseSkill-related route [EV-0572]. FUN_1408062d0 reads the component's +0x18 field as a loop bound while walking records from a buffer pointer at +0x8 in 0xa8-byte steps. FUN_140805c40 passes the +0x18 field address, current +0x10 value, and element size 0xa8 to an array-allocation helper before writing one record. This establishes an array bound/capacity-like use for the field, while its exact container semantics and the global threshold meaning remain unknown.",
        "The direct Actor.Level interpretation is falsified for this accessor: its source is an Actor-associated component's +0x18 array bound/capacity-like field, used to bound traversal of 0xa8-byte records. The player-target gate therefore cannot be labeled a player-level gate from these captures. The array's exact count/capacity contract, why this component is touched from the adjacent AV15-related caller, DAT_141ffda78's purpose, and Steam behavior remain unresolved. No causal edge to Actor.Level, quest initiation, effective armor protection, or AV11/AV12 is added.",
        ["EV-0577", "EV-0578", "EV-0572", "EV-0315", "EV-0260"],
        ["gog-query-20261019T170523Z", "gog-query-20261019T170620Z", "gog-query-20261019T170921Z", "gog-query-20261019T171236Z", "gog-query-20261019T171400Z"],
    ),
]

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
known = {row["id"]: row for row in evidence_doc["items"]}
for item in items:
    if item["id"] in known:
        if known[item["id"]] != item:
            raise SystemExit(f"evidence ID collision or changed capture: {item['id']}")
    else:
        evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, text: str) -> None:
    target = ROOT / path
    content = target.read_text(encoding="utf-8")
    if marker not in content:
        target.write_text(content.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L388",
    "| CL-L388 | In GOG AE 1.6.1179.0, Papyrus `Actor.StartCombat` is registered to FUN_1409ec930, which queues a tag-0x2a event for two existing Actor arguments only after process and Actor-state predicates pass. | supported for the captured binding and wrapper | [EV-0577] | The static wrapper does not establish quest/encounter creation, a level-gate bypass, or Steam runtime behavior. |",
)
append_once(
    "research/CLAIMS.md",
    "CL-L389",
    "| CL-L389 | In the captured GOG tag-0x2a route, fallback case 0x2a reaches FUN_1406e4ba0 and FUN_14071e250; the latter compares DAT_141ffda78 against FUN_140766520(player) on a player-target branch. | supported for the exact captured static path | [EV-0578] | Neither the global nor comparison is identified as a player-level condition; no quest, encounter, HitData, AV11/AV12, or UseSkill edge is established. |",
)
append_once(
    "research/CLAIMS.md",
    "CL-L390",
    "| CL-L390 | In GOG AE 1.6.1179.0, FUN_140766520 reads Actor-associated component offset +0x18, which FUN_1408062d0 uses as a bound while traversing 0xa8-byte records; FUN_140805c40 passes that field address and record size to an array helper. | supported as field provenance and bounded use | [EV-0579] | Exact count/capacity semantics and DAT_141ffda78 purpose remain unknown; this falsifies only the direct Actor.Level interpretation of the accessor. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0137 — tag-0x2a Papyrus Actor.StartCombat continuation (EV-0577/0578/0579)",
    """## M-0137 — tag-0x2a Papyrus Actor.StartCombat continuation (EV-0577/0578/0579)

GOG AE 1.6.1179.0 registers Papyrus `Actor.StartCombat` to `FUN_1409ec930`. The wrapper checks two existing Actor arguments and process/state predicates, then queues tag `0x2a` through `FUN_1406586f0`; fallback case `0x2a` resolves the Actor handles and calls `FUN_1406e4ba0`, which enters `FUN_14071e250` [EV-0577], [EV-0578]. A player-target branch compares `DAT_141ffda78` with `FUN_140766520(player)`, but neither the global threshold nor its purpose is identified [EV-0578]. The accessor reads Actor+`0x9d8` component offset `+0x18`; that field is used as a loop bound over `0xa8`-byte records and is passed with record-size `0xa8` to an array helper [EV-0579]. This falsifies the direct `Actor.Level` interpretation of this accessor, while exact container semantics and threshold meaning remain unresolved. This existing-Actor combat continuation does not establish a quest/encounter start or level-one bypass. No causal edge to OBJ-1 or armor mitigation/skill progression is supported. Claims CL-L388–CL-L390.""",
)
append_once(
    "research/CONTRADICTIONS.md",
    "Q79 StartCombat player-target threshold field identity (EV-0579)",
    """## Q79 StartCombat player-target threshold field identity (EV-0579)

An initial reading of `DAT_141ffda78 <= FUN_140766520(player)` in `FUN_14071e250` admits a player-level-gate interpretation [EV-0578]. Follow-up source tracing shows `FUN_140766520` returns Actor+`0x9d8` component offset `+0x18`, and this field bounds traversal of `0xa8`-byte records in `FUN_1408062d0`; `FUN_140805c40` passes the field address and `0xa8` stride to an array helper [EV-0579]. The direct `Actor.Level` model is falsified for the accessor. The field's exact count/capacity meaning, global threshold identity and gate purpose remain unresolved; no level-gate conclusion follows.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 40/62: tag-0x2a StartCombat and player-target discriminator (EV-0577/0578/0579)",
    """### Caller 40/62: tag-0x2a StartCombat and player-target discriminator (EV-0577/0578/0579)

Competing models before the field trace: (1) `FUN_140766520(player)` returns Actor.Level and the global comparison is a level threshold; (2) it returns another player-associated state value and the comparison is not a level gate. The discriminant was the exact getter dataflow plus the field's producer/consumer use.

The GOG Actor native registrar binds `Actor.StartCombat` to `FUN_1409ec930`. Its queueing branch requires two process-backed Actors and state predicates, then builds tag `0x2a` with two converted handles [EV-0577]. Worker fallback case `0x2a` resolves those handles and enters `FUN_1406e4ba0`/`FUN_14071e250`; the latter has a player-target threshold comparison [EV-0578]. `FUN_140766520` returns Actor+`0x9d8` component `+0x18`, which is used as a bound over a pointer-backed `0xa8`-byte record array and supplied as the array helper's capacity/bound field [EV-0579]. This falsifies the direct Actor.Level model for the getter but does not identify the global or comparison purpose. No quest-start, Story Manager, encounter creation, HitData, AV11/AV12, effective-protection or UseSkill edge is established in the bounded route. This does not validate an OBJ-1 bypass or a Steam-runtime result.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "## Caller 40 competing models",
    """## Caller 40 competing models

- Q79-H73: `FUN_140766520(player)` is a direct Actor.Level accessor and the player-target threshold is a level gate. **Falsified for this accessor**: it reads Actor+`0x9d8` component `+0x18`, which is used as an array bound over `0xa8`-byte records; the global threshold remains unknown [EV-0578], [EV-0579].
- Q79-H74: the player-target branch compares a non-level component-array bound/capacity-like field against an unknown global threshold. **Structurally supported, semantic purpose unresolved** [EV-0578], [EV-0579].
- OBJ-1 lead assessment: Papyrus `Actor.StartCombat` is a real native route for existing process-backed Actors, but the captured API and worker do not show quest/encounter creation or a level-gate bypass [EV-0577], [EV-0578]. No successor bounty candidate is opened without a target-specific gate and sequence.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0577/0578/0579 caller 40 discriminants",
    """EV-0577/0578/0579 caller 40 discriminants: the direct Actor.Level model predicts that `FUN_140766520` returns a known player-level field; the competing component-state model predicts a producer-backed array bound or other non-level value. The captured field is the Actor+`0x9d8` component's `+0x18`, consumed as a bound over `0xa8`-byte records. To identify the threshold semantics, resolve writers/readers of that exact component field and identify `DAT_141ffda78` from an identity-checked GOG query. Do not infer a DA quest start from `Actor.StartCombat`.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 40 bounded OBJ-1 / OBJ-2 no-edge note",
    """Caller 40 bounded cross-domain note: `Actor.StartCombat` is an existing-Actor process continuation whose player-target branch compares an unknown global with an Actor-component array bound. It is not evidence of quest/event initiation, a level gate, effective armor protection, or armor XP suppression. The component is also reached from the prior AV15-related context in EV-0572, but this adjacency does not identify its purpose or imply an AV11/AV12/armor edge. Keep this uncertainty separate from the current HitData worker-caller sweep and the queued clean Steam matched-hit/protection/raw-AVSK test.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0577–EV-0579 adds tag-0x2a StartCombat route",
    """EV-0577–EV-0579 adds tag-0x2a StartCombat route: Papyrus native `Actor.StartCombat` enters a process-backed Actor worker continuation; its player-target comparison reads Actor+`0x9d8` component `+0x18`, a bound used over `0xa8`-byte records. This falsifies a direct Actor.Level interpretation but leaves the global threshold's purpose unknown. The path does not establish quest/encounter initiation or armor-skill causality; no graph edge to OBJ-1, M-0017, or M-0031 is added.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(item for item in frontier["items"] if item.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0577", "EV-0578", "EV-0579"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L388", "CL-L389", "CL-L390"]))
new_hypotheses = [
    {
        "id": "Q79-H73",
        "model": "FUN_140766520(player) is a direct Actor.Level accessor and the player-target threshold in FUN_14071e250 is a level gate.",
        "predicted_discriminant": "The getter should read the Actor level field or a source-backed level provider; its value should not instead serve as an array bound/capacity-like field over component records.",
        "status": "falsified",
        "evidence": ["EV-0578", "EV-0579"],
    },
    {
        "id": "Q79-H74",
        "model": "The player-target comparison uses a non-level Actor-component array bound/capacity-like value; the threshold and gate purpose are otherwise unknown.",
        "predicted_discriminant": "The getter source and producer/consumer show the returned field participating in an Actor-associated array layout rather than an Actor.Level accessor; identity of the global threshold requires separate evidence.",
        "status": "supported",
        "evidence": ["EV-0578", "EV-0579"],
    },
]
known_hypotheses = {h["id"]: h for h in q79.get("hypotheses", [])}
for hypothesis in new_hypotheses:
    if hypothesis["id"] in known_hypotheses:
        if known_hypotheses[hypothesis["id"]] != hypothesis:
            raise SystemExit(f"hypothesis conflict: {hypothesis['id']}")
    else:
        q79.setdefault("hypotheses", []).append(hypothesis)
assessment = "Caller 40/62 maps Papyrus Actor.StartCombat to the tag-0x2a process-backed Actor transition [EV-0577], [EV-0578]. The apparent player threshold reads Actor+0x9d8 component +0x18, used as an array bound/capacity-like field over 0xa8-byte records; the direct Actor.Level interpretation is falsified, while the global threshold purpose remains unknown [EV-0579]. No OBJ-1 or armor-XP causal edge is added. Resume at caller 41/62 FUN_140658810."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658810 --list-call-edges --timeout 600; inspect worker caller 41/62 FUN_140658810 for payload/tag, exact producer provenance, matched dispatcher route, and any direct HitData/ActorValue/armor-skill edge. Compare the bounded result against Q79-H1/H2/H3; retain unresolved virtual targets and the clean Steam matched-hit/protection/raw-AVSK requirement."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
checkpoint = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 40/62 FUN_1406586f0 is mapped to Papyrus Actor.StartCombat/tag 0x2a; the player-target threshold reads an Actor+0x9d8 component field used as an array bound/capacity-like value, not a direct Actor.Level accessor. H73 is falsified for that accessor; H74 is structurally supported while global threshold semantics remain unknown. 22 exact worker callers remain after this checkpoint. OBJ-1 remains P0 and independent; this local result does not resolve the bounty.",
    "next_action": next_action,
}
frontier["session_checkpoint"] = checkpoint
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier["next_action"] = next_action
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("registered EV-0577/EV-0578/EV-0579, CL-L388–CL-L390, M-0137, Q79-H73/H74, and caller-41 checkpoint")
