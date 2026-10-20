from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
QUERY_SPECS = [
    ("gog-query-20261019T174727Z", "0x6588e0"),
    ("gog-query-20261019T174845Z", "0x5d3680"),
    ("gog-query-20261019T175042Z", "0x5d4bf0"),
]
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
metas = {}
local_hashes = {}
for stem, rva in QUERY_SPECS:
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != rva:
        raise SystemExit(f"query identity failed for {stem}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG binary identity failed for {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed for {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed for {stem}")
    metas[stem] = meta
    local_hashes[f".local/ghidra/{raw.name}"] = sha(raw)
    local_hashes[f".local/ghidra/{stderr.name}"] = sha(stderr)
    local_hashes[f".local/ghidra/{meta_path.name}"] = sha(meta_path)

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only queries, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0587",
    "source": "Identity-checked read-only GOG tag-0x3f builder, fallback wrapper and shared immediate/deferred handler trace",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T175042Z.stdout.raw",
    "sha256": metas["gog-query-20261019T175042Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T175042Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x6588e0 --list-call-edges --timeout 600",
        "tools/ghidra_probe.py --rva 0x5d3680 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x5d4bf0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_1406588e0 builds tag 0x3f from a producer object: payload fields are the low dword at source+0x38, qwords at source+0x110 and +0x108, and a retained object returned by source vslot +0x1e0. Its only direct producer is FUN_1405d3900. When the shared gate is clear, that producer calls FUN_1405d4bf0 with the corresponding source fields; when set, it calls the builder and clears source+0x110 before related arrays/resources are drained. Worker fallback case 0x3f calls FUN_1405d3680 and releases its retained object [EV-0574]. FUN_1405d3680 copies the four payload values into FUN_1405d4bf0 in the same argument order. FUN_1405d4bf0 has three direct callees and four indirect call sites, with two direct incoming caller functions (FUN_1405d3680 and FUN_1405d3900). It uses form/global checks, a form-to-object resolver, virtual object slots +0x378/+0x380, and FUN_140266e40, which recursively inspects a child/object collection and may call FUN_140267bd0 on a matching nested entry. No direct mapped HitData, effective armor, AV11/AV12, or UseSkill target appears in the exact shared helper; the virtual targets and descendants remain unresolved.",
    "result": "The deferred tag-0x3f route and the producer's immediate branch converge on FUN_1405d4bf0 with the same four values. This supports a single form/context-gated state-cleanup operation behind the shared worker gate and falsifies the divergent-handler alternative for the captured path. The exact object type and dynamic slots remain unknown. The bounded helper contains no direct mapped HitData/protection/ActorValue/UseSkill sink; no OBJ-2 causal edge is added. Q79-H1/H2 remain open with 18 original callers left.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0586", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0587" in existing and existing["EV-0587"] != item:
    raise SystemExit("EV-0587 collision")
if "EV-0587" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L399",
    "| CL-L399 | In GOG AE 1.6.1179.0, tag 0x3f's deferred worker case copies four payload values through FUN_1405d3680 into the same FUN_1405d4bf0 helper called by the producer's immediate branch. The shared helper has three direct callees and four indirect sites, including unresolved object slots +0x378/+0x380; no direct mapped HitData, effective-armor, AV11/AV12, or UseSkill target appears. | supported for the exact bounded queue/direct route | [EV-0587], [EV-0574] | Nested object type, virtual targets and downstream effects remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0142 — Tag-0x3f immediate/deferred state-cleanup convergence (EV-0574/0587)",
    """## M-0142 — Tag-0x3f immediate/deferred state-cleanup convergence (EV-0574/0587)

`FUN_1405d3900` selects an immediate call to `FUN_1405d4bf0` when the shared gate is clear, or serializes tag `0x3f` and clears source field `+0x110` when queued [EV-0587]. Worker case `0x3f` calls `FUN_1405d3680`; the wrapper copies the same four source values into the same `FUN_1405d4bf0` parameter order [EV-0574], [EV-0587]. The shared helper performs form/global checks and uses unresolved object virtual slots `+0x378`/`+0x380`, `FUN_140179420`, and `FUN_140266e40`; the latter traverses child/object entries and may call `FUN_140267bd0` on a matching entry [EV-0587]. This supports queue/direct convergence for the bounded route. Exact object RTTI, virtual meanings and downstream effects remain unknown; no direct HitData/effective-armor/AV11/AV12/UseSkill or OBJ-1 edge is established. Claim CL-L399.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 44/62: FUN_1406588e0 tag-0x3f queue/direct convergence (EV-0587)",
    """### Caller 44/62: FUN_1406588e0 tag-0x3f queue/direct convergence (EV-0587)

Caller `FUN_1406588e0` builds tag `0x3f` with four values derived from its sole producer `FUN_1405d3900`; the producer calls `FUN_1405d4bf0` directly when the shared gate is clear and queues the matching fields when set [EV-0587]. Worker fallback case 0x3f calls `FUN_1405d3680`, which forwards those four values to the same `FUN_1405d4bf0` helper in the same order [EV-0574], [EV-0587]. The shared helper has three direct callees plus four indirect sites, including unresolved slots `+0x378` and `+0x380`; its bounded body performs form/global checks and nested object traversal/update work. No direct mapped HitData/effective-armor/AV11/AV12/UseSkill sink appears. H81 is supported and H82 is falsified for the captured direct/deferred alternatives; nested type and virtual behavior remain open. Eighteen original callers remain; continue at caller 45/62 `FUN_140658950`.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 44 competing queue/direct models",
    """## Caller 44 competing queue/direct models

- Q79-H81: the tag-0x3f deferred route reconstructs the same four values and converges on the producer's immediate helper `FUN_1405d4bf0`. Prediction: producer fields, worker wrapper payload, and direct/deferred call arguments match.
- Q79-H82: the deferred route performs a different state operation or loses a value relative to the immediate branch. Prediction: the tag-0x3f worker case targets another helper or changes field/argument order.

EV-0587 supports H81 and falsifies H82 for the captured branches. The shared helper still contains unresolved object slots and its nested type/effects remain unknown; no armor or HitData edge follows.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0587 caller-44 result and frontier",
    "EV-0587 establishes that tag 0x3f's queued wrapper and the producer's immediate branch converge on FUN_1405d4bf0 with the same four fields. Its direct body uses unresolved object virtuals and nested cleanup/state helpers, with no mapped HitData/protection/AV11/AV12/UseSkill sink. Resume caller 45/62 FUN_140658950 and keep Q79-H1/H2 open.",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Callers 42–44 cross-system synthesis: shared worker, distinct state mechanisms",
    """Callers 42–44 cross-system synthesis: shared worker, distinct state mechanisms

The generic worker is only a serialization/re-entry primitive across these bounded examples. Caller 42 is a Papyrus `Actor.DispelSpell` route that marks a SpellItem-linked record for shared status handling; caller 43 is an indexed object-state route with an `iMagicEquipped` property cue; caller 44 is a gate-controlled form/context cleanup whose immediate and deferred branches converge on the same helper [EV-0583]–[EV-0587]. These distinct payloads do not establish a shared ActiveEffect class, effective-armor path, HitData relation, AV11/AV12 award or armor XP consequence. Keep the causal graph separated until a producer-backed common sink appears.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0587 resolves tag-0x3f queue/direct convergence",
    "EV-0587 shows that tag 0x3f's producer immediate branch and deferred worker case converge on FUN_1405d4bf0 with the same four payload values. The helper uses unresolved object slots and nested state traversal; it has no direct mapped HitData/protection/AV11/AV12/UseSkill sink, and no OBJ-1/OBJ-2 edge is added [EV-0574], [EV-0587]. Callers 42–44 share the generic worker but retain distinct payload semantics.",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 44 tag-0x3f immediate/deferred convergence (EV-0587)",
    """## Q-0079 update — caller 44 tag-0x3f immediate/deferred convergence (EV-0587)

Caller 44's producer chooses an immediate `FUN_1405d4bf0` call or submits the same four values through tag `0x3f`; the worker wrapper reaches the same helper in the same argument order [EV-0574], [EV-0587]. The helper's object virtuals remain unresolved and it has no direct mapped HitData/protection/AV11/AV12/UseSkill sink. Eighteen original callers remain; resume at `FUN_140658950` [CL-L399], [M-0142].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0587"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L399"]))
h81 = {
    "id": "Q79-H81",
    "model": "Tag 0x3f's deferred worker route reconstructs the same four values and converges on FUN_1405d4bf0, matching the producer's immediate branch.",
    "predicted_discriminant": "Producer fields, worker wrapper payload and direct/deferred helper arguments match in value and order.",
    "status": "supported",
    "evidence": ["EV-0587", "EV-0574"],
}
h82 = {
    "id": "Q79-H82",
    "model": "Tag 0x3f's deferred worker route performs a different state operation or loses a value relative to the immediate branch.",
    "predicted_discriminant": "The tag-0x3f worker case targets a different helper or changes the payload fields/argument order relative to the direct producer call.",
    "status": "falsified",
    "evidence": ["EV-0587", "EV-0574"],
}
hypotheses = q79["hypotheses"]
for candidate in (h81, h82):
    found = next((h for h in hypotheses if h.get("id") == candidate["id"]), None)
    if found is None:
        hypotheses.append(candidate)
    elif found != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0587 resolves caller 44's tag-0x3f immediate/deferred split: both branches pass the same four values into FUN_1405d4bf0. The helper uses unresolved object virtual slots and nested state traversal but exposes no direct mapped HitData/protection/AV11/AV12/UseSkill edge. Together with callers 42–43, this shows separate spell-record, indexed object-state, and form/context cleanup payloads behind one generic worker; no common armor or quest causal edge is supported."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658950 --list-call-edges --timeout 600; inspect worker caller 45/62 FUN_140658950 for payload/tag, producer provenance, dispatcher route, and any direct mapped HitData/AV11/AV12/UseSkill edge. Compare against Q79-H1/H2/H3, preserve tag/source uncertainty and the unavailable clean Steam matched-hit/protection/raw-AVSK discriminator, then continue caller 46/62."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 44/62 is tag 0x3f; the immediate producer and deferred worker path converge on FUN_1405d4bf0 with the same four payload values. The helper uses unresolved object virtual slots and nested state traversal, with no direct mapped HitData/protection/AV11/AV12/UseSkill edge. Eighteen original callers remain; caller 45 is next.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace("43 of 62 initially uninspected worker callers are reviewed, with 19 remaining.", "44 of 62 initially uninspected worker callers are reviewed, with 18 remaining.", 1)
state = state.replace(
    "EV-0586 maps caller 43/tag 0x3d to indexed object-state updates with unresolved virtual selectors and no direct mapped hit/armor-skill sink. No armor-XP bypass is established; Q79-H1/H2/H3 and clean Steam protection/raw-AVSK remain open.",
    "EV-0586 maps caller 43/tag 0x3d to indexed object-state updates with unresolved virtual selectors and no direct mapped hit/armor-skill sink. EV-0587 maps caller 44/tag 0x3f to the same helper from immediate and deferred paths with identical four-field payloads. No armor-XP bypass is established; Q79-H1/H2/H3 and clean Steam protection/raw-AVSK remain open.",
    1,
)
state = state.replace("Q-0079 has 43/62 exact worker callers reviewed; 19 remain.", "Q-0079 has 44/62 exact worker callers reviewed; 18 remain.", 1)
state = state.replace(
    "EV-0586 maps tag 0x3d into indexed object-state updates with unresolved virtual selectors.",
    "EV-0586 maps tag 0x3d into indexed object-state updates with unresolved virtual selectors; EV-0587 maps tag 0x3f immediate/deferred branches to the same four-field helper.",
    1,
)
old_next = "**Selected next line:** inspect caller 44/62 `FUN_1406588e0` for its producer payload, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0586]. Keep caller 43's dynamic object type and virtual selectors unresolved; no armor causal edge is established."
new_next = "**Selected next line:** inspect caller 45/62 `FUN_140658950` for its payload, producer, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0587]. Keep tag-0x3f nested object identity and virtual behavior unresolved; no armor causal edge is established."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0587/CL-L399/M-0142; supported Q79-H81, falsified H82, checkpointed caller 45/62")
