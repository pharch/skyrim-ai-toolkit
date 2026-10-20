from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
IDENTITY = ("1.6.1179", "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f")
CAPTURES = [
    ("gog-query-20261019T172852Z", "0x658850"),
    ("gog-query-20261019T165124Z", "0x659160"),
    ("gog-query-20261019T170740Z", "0x9ed4a0"),
]
hashes: dict[str, str] = {}
metas: dict[str, dict] = {}
for stem, rva in CAPTURES:
    raw, stderr, meta_path = (GH / f"{stem}.stdout.raw", GH / f"{stem}.stderr.raw", GH / f"{stem}.meta.json")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != rva:
        raise SystemExit(f"query identity failed: {stem}")
    if (meta.get("analysis_binary_product_version"), meta.get("analysis_binary_sha256")) != IDENTITY:
        raise SystemExit(f"GOG binary identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed: {stem}")
    raw_hash, stderr_hash = hashlib.sha256(raw.read_bytes()).hexdigest(), hashlib.sha256(stderr.read_bytes()).hexdigest()
    if raw_hash != meta.get("stdout_sha256") or stderr_hash != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed: {stem}")
    hashes.update({
        f".local/ghidra/{raw.name}": raw_hash,
        f".local/ghidra/{stderr.name}": stderr_hash,
        f".local/ghidra/{meta_path.name}": hashlib.sha256(meta_path.read_bytes()).hexdigest(),
    })
    metas[stem] = meta

primary = GH / "gog-query-20261019T172852Z.stdout.raw"
item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0583",
    "source": "Identity-checked GOG worker caller 42/62, tag-0x5e dispatcher case, and Actor native registration",
    "artifact": f"private-local:.local/ghidra/{primary.name}",
    "sha256": hashlib.sha256(primary.read_bytes()).hexdigest(),
    "captured_utc": metas["gog-query-20261019T172852Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x658850 --list-call-edges --timeout 600",
        "tools/ghidra_probe.py --rva 0x659160 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x9ed4a0 --list-call-edges --follow-direct-calls 8 --follow-incoming-calls 12 --timeout 600",
    ],
    "coverage": "FUN_140658850 builds tag 0x5e with one copied 32-bit value and an 8-byte payload; its sole captured direct producer FUN_1409e9120 uses FUN_140178cf0 or DAT_1420f7d9c for the value and forwards param_4 [gog-query-20261019T172852Z]. The Actor native registrar binds FUN_1409e9120 to `DispelSpell` and identifies its native object as `BSScript::NativeFunction1<class_Actor,bool,class_SpellItem*>` [gog-query-20261019T170740Z]. Worker fallback case 0x5e resolves the handle and calls `FUN_1405c4800(resolved_actor + 0xa0, spell_argument, &DAT_1420f7d9c, 0)` before releasing the Actor reference [gog-query-20261019T165124Z]. The exact callee data structure/effects are not identified in this item.",
    "result": "Caller 42 is a deferred Papyrus Actor.DispelSpell route to FUN_1405c4800 on an Actor-associated +0xa0 member with a SpellItem argument. This is a concrete candidate for Actor spell/ActiveEffect state handling, but the helper body is not yet traced, so active-effect lifetime, hit mitigation, armor protection, skill XP, quest state, and Steam runtime behavior remain unknown. No OBJ-1/OBJ-2 causal edge is added pending the helper discriminator.",
    "local_hashes": hashes,
    "related_evidence": ["EV-0580", "EV-0581", "EV-0582", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0583" in existing and existing["EV-0583"] != item:
    raise SystemExit("EV-0583 collision")
if "EV-0583" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

append_once(
    "research/CLAIMS.md",
    "CL-L394",
    "| CL-L394 | In GOG AE 1.6.1179.0, Papyrus `Actor.DispelSpell` is registered to FUN_1409e9120 as `NativeFunction1<class_Actor,bool,class_SpellItem*>`; its tag-0x5e worker case resolves the Actor handle and calls FUN_1405c4800(Actor+0xa0, SpellItem, default, 0). | supported for the exact native registration and dispatch callsite | [EV-0583] | FUN_1405c4800's data structure and effects remain unresolved; no ActiveEffect lifetime, HitData/armor, AV11/AV12, quest-gate, or Steam result is established. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0139 — tag-0x5e Actor.DispelSpell dispatch (EV-0583)",
    """## M-0139 — tag-0x5e Actor.DispelSpell dispatch (EV-0583)

The GOG Actor native registrar binds `FUN_1409e9120` as `Actor.DispelSpell` with native type `NativeFunction1<class_Actor,bool,class_SpellItem*>`. The wrapper serializes its Actor handle and forwards the SpellItem argument under worker tag `0x5e`; the matched fallback case resolves that Actor and calls `FUN_1405c4800(Actor+0xa0, SpellItem, default, 0)` [EV-0583]. The helper's receiver type, collection semantics, ActiveEffect consequences, and runtime behavior remain unresolved. Do not add a causal edge to effective armor protection, HitData, AV11/AV12, armor XP, or level-gated quests until its exact dataflow is traced.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 42/62: tag-0x5e Actor.DispelSpell lead (EV-0583)",
    """### Caller 42/62: tag-0x5e Actor.DispelSpell lead (EV-0583)

`FUN_140658850` builds tag `0x5e`; its sole producer `FUN_1409e9120` is registered as Papyrus `Actor.DispelSpell` with `NativeFunction1<class_Actor,bool,class_SpellItem*>` [EV-0583]. The fallback case resolves the Actor handle and calls `FUN_1405c4800(Actor+0xa0, SpellItem, default, 0)`. Competing models for the next probe: Q79-H77 predicts the helper mutates an Actor-associated ActiveEffect/spell runtime collection; Q79-H78 predicts a generic spell/state helper without an ActiveEffect lifetime or damage/XP consequence. Query the exact helper's incoming/outgoing edges and producer-backed structure before classification. This is a cross-system spell-state lead, not evidence of functional armor with zero XP.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "## Caller 42 competing models",
    """## Caller 42 competing models

- Q79-H77: `FUN_1405c4800` mutates an Actor-associated ActiveEffect/runtime-spell collection. Prediction: its exact receiver/array consumers or producer-backed callers identify ActiveEffect records and lifetime/removal operations.
- Q79-H78: `FUN_1405c4800` performs a generic spell/state update without an ActiveEffect lifetime or damage/XP effect. Prediction: its receiver and payload use resolve to a spell registry or other Actor state with no direct ActiveEffect, HitData, AV11/AV12, or UseSkill sink. Both models are proposed pending direct callee evidence [EV-0583].""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0583 caller 42 helper discriminant",
    """EV-0583 caller 42 helper discriminant: query `FUN_1405c4800` from the tag-0x5e path. Q79-H77 requires source-backed ActiveEffect record/array or lifetime operations on the Actor+`0xa0` receiver; Q79-H78 predicts a generic spell/state update without those edges. Preserve all direct callers, virtual targets and argument fields; do not infer protection or XP from the native name `DispelSpell` alone.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0583"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L394"]))
for hyp in [
    {"id": "Q79-H77", "model": "FUN_1405c4800 mutates an Actor-associated ActiveEffect/runtime-spell collection.", "predicted_discriminant": "The helper's exact receiver/array consumers or producer-backed callers identify ActiveEffect records and lifetime/removal operations.", "status": "proposed", "evidence": ["EV-0583"]},
    {"id": "Q79-H78", "model": "FUN_1405c4800 performs a generic spell/state update without an ActiveEffect lifetime or damage/XP consequence.", "predicted_discriminant": "The helper receiver and payload resolve to a spell registry or other Actor state with no direct ActiveEffect, HitData, AV11/AV12, or UseSkill sink.", "status": "proposed", "evidence": ["EV-0583"]},
]:
    existing_hyp = next((h for h in q79.get("hypotheses", []) if h.get("id") == hyp["id"]), None)
    if existing_hyp is None:
        q79.setdefault("hypotheses", []).append(hyp)
    elif existing_hyp != hyp:
        raise SystemExit(f"hypothesis collision: {hyp['id']}")
assessment = "Caller 42/62 is registered as Actor.DispelSpell and tag 0x5e calls FUN_1405c4800 on Actor+0xa0 with a SpellItem argument [EV-0583]. This opens an ActiveEffect/runtime-spell versus generic state helper discriminator; the callee remains untraced, so no P0 armor/quest causal edge is claimed."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x5c4800 --list-call-edges --follow-incoming-calls 32 --follow-direct-calls 8 --timeout 600; inspect FUN_1405c4800 receiver/data structure and all captured direct callers, testing Q79-H77 ActiveEffect membership/lifetime against Q79-H78 generic spell/state hypotheses. Trace mapped HitData/AV11/AV12/UseSkill sinks only when producer-backed; preserve GOG/Steam boundaries."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 42/62 is Papyrus Actor.DispelSpell/tag 0x5e, whose worker case invokes FUN_1405c4800 on Actor+0xa0 with a SpellItem argument. Competing models are Actor ActiveEffect/runtime-spell collection mutation versus generic spell/state update; helper is the exact next query. 20 exact worker callers remain. This is a cross-system lead only; no armor/quest causal edge or Steam runtime result is established.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("registered EV-0583/CL-L394/M-0139 and caller-42 ActiveEffect discriminator")
