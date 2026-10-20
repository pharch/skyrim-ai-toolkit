from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
QUERY_SPECS = [
    ("gog-query-20261019T175258Z", "0x658950"),
    ("gog-query-20261019T175752Z", "0x33e470"),
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
    for artifact in (raw, stderr, meta_path):
        local_hashes[f".local/ghidra/{artifact.name}"] = sha(artifact)

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only queries, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0589",
    "source": "Identity-checked GOG tag-0x40 producer and shared typed-value decoder call trace",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T175752Z.stdout.raw",
    "sha256": metas["gog-query-20261019T175752Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T175752Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x33e470 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x658950 --list-call-edges --timeout 600",
    ],
    "coverage": "The sole tag-0x40 producer FUN_140357c70 initializes two output locals, calls FUN_14033e470 with descriptor/input/cursor context plus output pointers, returns 0 on a failed decode, and otherwise submits the decoded object and a boolean derived from the second output to FUN_140658950 [EV-0587, query artifact 20261019T175258Z]. FUN_14033e470 walks typed descriptor entries against a compact byte stream and has 613 call xrefs across 64 caller functions in the current analysis; its complete call-edge scan shows nine direct callsites and four indirect sites. Selected conversion cases validate Form values with RTTI casts to SpellItem, MagicItem, or EffectSetting. The capture does not establish the exact selected descriptor/type for FUN_140357c70, who supplies its input stream, or whether decoded values originate from gameplay state. No direct mapped HitData/effective-protection/AV11/AV12/UseSkill sink is shown in the wrapper or decoder; indirect decoder callbacks and downstream behavior remain unresolved.",
    "result": "This narrows caller 45's immediate construction path to a typed-value decoder followed by object/boolean worker submission; FUN_140357c70 does not directly read Actor or HitData fields in its decompiled body. The decoder is shared across hundreds of call xrefs and supports several SpellItem/MagicItem/EffectSetting conversions, but the wrapper's descriptor and source provenance are unknown. This does not prove that the queued object is unrelated to gameplay, and it does not identify a level-one gate or armor-skill bypass. Q79-H1/H2/H3 remain unchanged; no causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0587", "EV-0588", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0589" in existing and existing["EV-0589"] != item:
    raise SystemExit("EV-0589 collision")
if "EV-0589" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L401",
    "| CL-L401 | In GOG AE 1.6.1179.0, tag-0x40 producer FUN_140357c70 obtains its submitted object and boolean from outputs of shared typed-value decoder FUN_14033e470, then forwards them to the worker builder. The wrapper body does not directly read Actor/HitData fields; the exact descriptor and input provenance are unknown. | supported for the captured construction path | [EV-0589], [EV-0587] | The decoded object may still encode gameplay state; decoder indirect callbacks, descriptor selection, producer registration and runtime effects remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0144 — Typed-value decode before tag-0x40 submission (EV-0589)",
    """## M-0144 — Typed-value decode before tag-0x40 submission (EV-0589)

`FUN_140357c70` initializes object/flag outputs, calls shared decoder `FUN_14033e470` with descriptor and byte-stream context, and submits the outputs to tag-0x40 builder `FUN_140658950` only if decoding succeeds [EV-0587], [EV-0589]. The decoder walks typed entries and includes RTTI-checked `TESForm` conversions for `SpellItem`, `MagicItem`, and `EffectSetting`; it has hundreds of call xrefs and four indirect sites [EV-0589]. The exact descriptor selected by this wrapper, its input producer, decoded object type, and any indirect callback behavior remain unknown. This narrows the direct source path but does not establish that the payload is unrelated to gameplay, HitData, or armor. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L401.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 45/62 producer decode path (EV-0589)",
    """### Caller 45/62 producer decode path (EV-0589)

The tag-0x40 producer `FUN_140357c70` initializes output locals, invokes shared typed-value decoder `FUN_14033e470`, returns false if decoding fails, and otherwise passes the returned object plus a nonzero test of the second output into `FUN_140658950` [EV-0587], [EV-0589]. The decoder walks descriptor-selected values from a byte stream and has RTTI-checked conversions to `SpellItem`, `MagicItem`, and `EffectSetting`; it has 613 call xrefs across 64 caller functions and four unresolved indirect sites [EV-0589]. The exact type selector, stream source and output object's RTTI remain unknown. The wrapper body contains no direct Actor/HitData field read, but this does not rule out gameplay data in its input. No mapped direct HitData/protection/AV11/AV12/UseSkill edge is added; caller 46/62 is next.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 45 producer-source models",
    """## Caller 45 producer-source models

- Q79-H83: tag-0x40's sole producer obtains the queued object and boolean through typed-value decoding before submitting them. Prediction: the producer initializes output slots, the shared decoder walks a descriptor/input stream, and the outputs are then passed to the tag-0x40 builder.
- Q79-H84: the producer directly constructs the tag-0x40 object/flag from Actor or HitData state. Prediction: its body reads gameplay object/HitData fields or calls a mapped combat/protection/armor-skill helper before submission.

EV-0589 supports H83 and falsifies H84 for the producer's direct body. Input provenance, decoder descriptor selection and indirect callbacks remain open, so neither an unrelated-event classification nor a transitive/runtime negative follows.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0589 narrows tag-0x40 producer construction",
    "EV-0589 shows that tag 0x40's producer forwards outputs of a shared typed-value decoder into the worker builder; the producer body itself does not directly read Actor/HitData state. Input provenance and decoded type remain unknown, and no OBJ-1/OBJ-2 causal edge is added [EV-0587], [EV-0588], [EV-0589].",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 45 typed-value producer path (EV-0589)",
    """## Q-0079 update — caller 45 typed-value producer path (EV-0589)

Caller 45's sole producer decodes descriptor-selected values through shared `FUN_14033e470` and forwards an object/boolean to the tag-0x40 worker only on success [EV-0589]. The wrapper body does not directly read Actor/HitData fields; input provenance and decoded type remain unresolved. Continue to caller 46/62 without treating the generic decoder as evidence of a hit or armor route [CL-L401], [M-0144].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0589"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L401"]))
for candidate in (
    {
        "id": "Q79-H83",
        "model": "Tag-0x40's sole producer obtains the queued object and boolean from a shared typed-value decoder before submission.",
        "predicted_discriminant": "The producer initializes output slots, calls the descriptor/input decoder, and submits those outputs only on decode success.",
        "status": "supported",
        "evidence": ["EV-0589", "EV-0587"],
    },
    {
        "id": "Q79-H84",
        "model": "Tag-0x40's producer directly constructs its object/flag from Actor or HitData state before submission.",
        "predicted_discriminant": "The producer body reads Actor/HitData fields or calls mapped combat/protection/armor-skill logic before building the worker event.",
        "status": "falsified",
        "evidence": ["EV-0589"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0589 supports a typed-decoder-to-worker construction for tag 0x40 and falsifies direct Actor/HitData field construction in the producer body. The decoder's input source and selected output RTTI remain unknown, so no unrelated-event or transitive negative is claimed. No OBJ-1/OBJ-2 causal edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x357c70 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; inspect FUN_140357c70's exact incoming/code and data references for a descriptor-registration context that identifies its selected typed value. If the static registration remains opaque, preserve that boundary and continue worker caller 46/62 from the baseline inventory."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 45/62 tag 0x40 is sourced through shared typed-value decoding, then passed as object/boolean; direct producer body contains no Actor/HitData field reads. Seventeen original callers remain; check producer registration context before caller 46.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0588 bounds caller 45/tag 0x40 as object/scalar state work with a TESImageSpace-related helper branch and no direct mapped combat/armor-skill sink.",
    "EV-0588 bounds caller 45/tag 0x40 as object/scalar state work with a TESImageSpace-related helper branch; EV-0589 traces its producer through a shared typed-value decoder, with source/type provenance still unknown and no direct Actor/HitData read in the wrapper.",
    1,
)
state = state.replace(
    "EV-0588 bounds tag 0x40 as a scalar/state update without a direct mapped combat/armor-skill sink.",
    "EV-0588 bounds tag 0x40 as a scalar/state update without a direct mapped combat/armor-skill sink; EV-0589 maps the producer through a shared typed-value decoder.",
    1,
)
old_next = "**Selected next line:** trace caller 45's producer `FUN_140357c70` through `FUN_14033e470` for the source/role of its object and boolean outputs [EV-0588]. Keep payload RTTI, TESImageSpace form provenance, transitive behavior, and the GOG/Steam boundary unresolved; then continue caller 46/62."
new_next = "**Selected next line:** inspect `FUN_140357c70` code/data references for its typed-value descriptor registration after EV-0589; if static registration remains opaque, continue caller 46/62. Keep input provenance, decoded RTTI, transitive behavior, and GOG/Steam boundaries unresolved."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0589/CL-L401/M-0144; supported Q79-H83, falsified H84; checkpointed wrapper registration context")
