from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
IDENTITY = ("1.6.1179", "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f")
CAPTURES = [
    ("gog-query-20261019T170740Z", "0x9ed4a0"),
    ("gog-query-20261019T172546Z", "0x9e90c0"),
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

primary = GH / "gog-query-20261019T170740Z.stdout.raw"
item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0582",
    "source": "Identity-checked GOG Actor native registrar row and exact tag-0x5d producer xref",
    "artifact": f"private-local:.local/ghidra/{primary.name}",
    "sha256": hashlib.sha256(primary.read_bytes()).hexdigest(),
    "captured_utc": metas["gog-query-20261019T170740Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x9ed4a0 --list-call-edges --follow-direct-calls 8 --follow-incoming-calls 12 --timeout 600",
        "tools/ghidra_probe.py --rva 0x9e90c0 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "The exact native registration row is FUN_1409f5510(..., \"RemoveSpell\", \"Actor\", FUN_1409e90c0, ...), binding the captured wrapper to Papyrus Actor.RemoveSpell [gog-query-20261019T170740Z]. The wrapper has no direct incoming call xrefs; its code address is referenced as data by the registrar. It calls FUN_140178cf0 to convert its param_3 object when the handle is valid, otherwise copies DAT_1420f7d9c, then invokes FUN_140658810 with that value and param_4 [gog-query-20261019T172546Z]. The exact API argument types and dynamic behavior after worker dispatch remain outside this registration row.",
    "result": "Caller 41's tag-0x5d event is the deferred GOG Papyrus Actor.RemoveSpell route. The worker resolves the converted object and invokes the bounded membership-removal helper FUN_1406c36e0 [EV-0580], [EV-0581]. This identifies a spell-list/state mutation, not a demonstrated HitData, AV11/AV12, armor-XP, quest-start, or level-gate route. GOG static binding does not establish Steam runtime behavior.",
    "local_hashes": hashes,
    "related_evidence": ["EV-0580", "EV-0581", "EV-0577", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0582" in existing and existing["EV-0582"] != item:
    raise SystemExit("EV-0582 collision")
if "EV-0582" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

append_once(
    "research/CLAIMS.md",
    "CL-L393",
    "| CL-L393 | In GOG AE 1.6.1179.0, Actor native registration binds Papyrus `Actor.RemoveSpell` to FUN_1409e90c0, which converts one object to a handle/default value and submits it with a second argument through worker tag 0x5d. | supported for the exact native registration and wrapper | [EV-0582], [EV-0580] | Argument type details, dynamic effects, Steam equivalence, and any HitData/AV11/AV12/armor-XP consequence remain unestablished. |",
)
append_once(
    "research/MECHANISMS.md",
    "### Native-name refinement: Actor.RemoveSpell (EV-0582)",
    """### Native-name refinement: Actor.RemoveSpell (EV-0582)

The Actor native registrar binds `FUN_1409e90c0` to Papyrus `Actor.RemoveSpell`; the wrapper converts one object to a handle/default value and queues tag `0x5d` with its second argument [EV-0582], [EV-0580]. The matched worker case resolves the object and reaches the bounded collection-membership update helper [EV-0581]. Keep the exact native name as registration evidence; do not infer dynamic callback semantics, spell-effect lifetime, armor XP, or Steam behavior from the binding alone.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 41/62: native registration resolves tag 0x5d (EV-0582)",
    """### Caller 41/62: native registration resolves tag 0x5d (EV-0582)

The GOG Actor native registrar binds `FUN_1409e90c0` to Papyrus `Actor.RemoveSpell`; its wrapper converts one object through `FUN_140178cf0` or a default global, then queues the converted value and second argument under tag `0x5d` [EV-0582], [EV-0580]. The matched case resolves the handle and invokes `FUN_1406c36e0`, whose bounded body removes object membership and updates related slots [EV-0581]. This identifies the bounded operation as the Actor.RemoveSpell native route. It does not establish how unresolved dynamic callbacks alter spell effects, armor protection, AV11/AV12, HitData, or quest state; it also does not establish Steam runtime equivalence.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 41 cross-domain synthesis: spell mutation boundary",
    """Caller 41 cross-domain synthesis: spell mutation boundary

The `Actor.RemoveSpell` native route links Papyrus dispatch, generational handle conversion, worker serialization, and object-membership mutation [EV-0580]–[EV-0582]. This is a concrete cross-system serialization/state transition, but no captured edge links its helper to ActiveEffect expiration, HitData mitigation, AV11/AV12/UseSkill, equipment rating, or the OBJ-1 quest-start gates. Retain it as a spell-state mechanism and do not promote it to an armor-XP or level-one candidate without a producer-backed edge.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0582 identifies caller 41 as Actor.RemoveSpell",
    """EV-0582 identifies caller 41's native binding as Papyrus `Actor.RemoveSpell`: its wrapper converts an object handle and submits tag `0x5d`, whose matched handler removes object membership through FUN_1406c36e0 [EV-0580], [EV-0581]. This connects native dispatch, handle serialization, and Actor spell-state mutation. No causal edge to OBJ-1, HitData mitigation, or armor skill progression is supported.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0582"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L393"]))
h75 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H75")
h75["model"] = "Tag 0x5d is the deferred Papyrus Actor.RemoveSpell native route, with bounded object-membership/state updates in its matched worker helper."
h75["predicted_discriminant"] = "The Actor native registrar names FUN_1409e90c0 as RemoveSpell; its wrapper queues tag 0x5d, whose matched case invokes the collection-membership helper."
h75["status"] = "supported"
h75["evidence"] = list(dict.fromkeys([*h75.get("evidence", []), "EV-0582"]))
assessment = "EV-0582 confirms the tag-0x5d producer FUN_1409e90c0 is registered as Papyrus Actor.RemoveSpell [EV-0582]. Combined with the handle conversion and collection-membership helper [EV-0580], [EV-0581], caller 41 is a native spell-state removal route. No ActiveEffect, HitData/armor, quest-gate, or Steam-runtime causal result follows from this registration."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658850 --list-call-edges --timeout 600; inspect worker caller 42/62 FUN_140658850 for payload/tag, exact producer provenance, matched dispatcher route, and any direct HitData/ActorValue/armor-skill edge. Compare against Q79-H1/H2/H3 and retain the clean Steam matched-hit/protection/raw-AVSK requirement."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 41/62 tag 0x5d is confirmed by the GOG Actor native registrar as Papyrus Actor.RemoveSpell. Its wrapper serializes a handle through the worker and the bounded helper performs collection membership updates. Q79-H75 is supported; no direct HitData/AV11/AV12/UseSkill/protection edge is established. 21 callers remain; next caller is 42/62 FUN_140658850. OBJ-1 and clean Steam hit/protection/raw-AVSK evidence remain open.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("registered EV-0582/CL-L393; identified Actor.RemoveSpell and checkpointed caller 42")
