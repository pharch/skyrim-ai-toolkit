from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
captures = {
    "gog-query-20261019T181514Z": "0x657870",
    "gog-query-20261019T113125Z": "0xE89260",
}
hashes: dict[str, str] = {}
metas: dict[str, dict] = {}
for stem, requested_rva in captures.items():
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != requested_rva.lower():
        raise SystemExit(f"query identity failed: {stem}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG binary identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed: {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed: {stem}")
    hashes.update({f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)})
    metas[stem] = meta

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only queries, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0595",
    "source": "Identity-checked GOG trace of secondary worker builder FUN_140657870 and existing FUN_140659160 fallback dispatcher case 10",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T181514Z.stdout.raw",
    "sha256": metas["gog-query-20261019T181514Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T181514Z"]["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x657870 --list-call-edges --timeout 600", "identity-checked dispatcher capture at 0xE89260"],
    "coverage": "FUN_140657870 has six direct calls, zero indirect sites, and three captured incoming callers (FUN_1406671b0, FUN_1406694e0, FUN_140665950). Under its nonnull-object and FUN_140667430-clear branch, it writes decimal 10 (tag 0x0A), obtains a handle-like value through FUN_1402ef8f0, copies a scalar, a float, a pointer-sized value, two bytes, and possibly three coordinates obtained from FUN_1406ee850/FUN_1406ee8c0, changes an object state through FUN_140667460, then submits the payload to FUN_14065b800. Existing dispatcher decompilation shows case 10 resolving the payload handle via FUN_14018a7e0; it conditionally applies a vector through FUN_1406ee880/FUN_1406ee8e0, changes the resolved object's state through FUN_140667460, resolves a second handle, and invokes unresolved recipient vtable slot +0x870 with that handle, a payload scalar, and two bytes. No recipient RTTI or virtual target is identified, and the bounded bodies contain no direct mapped HitData/effective-protection/AV11/AV12/UseSkill target.",
    "result": "The secondary builder is a tag-0x0A handle/scalar/vector/byte update route. Its fallback case reaches a dynamic method at vtable byte offset +0x870 after resolving the handle; the concrete recipient type and virtual target remain unresolved. The direct bodies expose no mapped hit/armor-skill sink, which does not rule out the unresolved virtual call or transitive effects. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": hashes,
    "related_evidence": ["EV-0594", "EV-0397", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0595" in existing and existing["EV-0595"] != item:
    raise SystemExit("EV-0595 collision")
if "EV-0595" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L407",
    "| CL-L407 | In GOG AE 1.6.1179.0, FUN_140657870 emits worker tag 0x0A with handle/scalar/vector/byte data; fallback case 10 resolves a handle and calls an unresolved recipient vtable slot +0x870, with no mapped HitData/protection/AV11/AV12/UseSkill direct target in the inspected bodies. | supported for the bounded static path | [EV-0595] | Recipient RTTI, virtual target, transitive effects, runtime behavior, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0148 — Tag-0x0A worker event performs a handle/vector update before a virtual callback (EV-0595)",
    """## M-0148 — Tag-0x0A worker event performs a handle/vector update before a virtual callback (EV-0595)

`FUN_140657870` builds tag `0x0A` with handle-like, scalar, float/vector, pointer-sized and byte payload fields before submitting to `FUN_14065b800`. Dispatcher case 10 resolves the handle, conditionally applies vector state, changes an object state, resolves a second handle, and calls recipient vtable byte offset `+0x870` [EV-0595]. The receiver RTTI and virtual target remain unknown. No direct HitData/armor-skill edge is established; no OBJ-1/OBJ-2 causal edge is added. Claim CL-L407.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 46 secondary event: tag 0x0A builder FUN_140657870 (EV-0595)",
    """### Caller 46 secondary event: tag 0x0A builder FUN_140657870 (EV-0595)

The builder `FUN_140657870` writes tag `0x0A` with a handle-like value and scalar/vector/byte payload, then submits it to the generic worker. Existing dispatcher case 10 resolves the handle, may apply a vector update, changes object state, resolves a second handle, and calls an unresolved recipient vtable slot `+0x870` [EV-0595]. No direct mapped HitData/protection/AV11/AV12/UseSkill call appears in the bounded bodies. The receiver RTTI and virtual target remain open; continue caller 47/62 after resolving the strongest available type/slot discriminator.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0595 adds a tag-0x0A handle/vector worker route",
    "EV-0595 links the secondary builder from EV-0594 to dispatcher case 10: handle resolution, conditional vector state, a second handle, then an unresolved virtual callback at recipient vtable byte offset +0x870. Its type/target remain unknown, so no OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0595"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L407"]))
for candidate in (
    {
        "id": "Q79-H95",
        "model": "FUN_140657870 emits tag 0x0A with a handle/scalar/vector/byte payload; dispatcher case 10 resolves handles and performs a vector/state update before unresolved recipient vtable slot +0x870.",
        "predicted_discriminant": "The builder writes tag 10 and case 10 reaches a dynamic recipient call after handle and optional vector processing, with no direct mapped HitData/armor-skill call in the inspected bodies.",
        "status": "supported",
        "evidence": ["EV-0595"],
    },
    {
        "id": "Q79-H96",
        "model": "The bounded tag-0x0A builder and dispatcher bodies directly call mapped HitData, effective-protection, AV11/AV12, or UseSkill targets.",
        "predicted_discriminant": "A direct edge in either inspected body resolves to one of the mapped combat/protection/skill targets.",
        "status": "falsified",
        "evidence": ["EV-0595"],
    },
    {
        "id": "Q79-H97",
        "model": "The tag-0x0A recipient is an Actor and the virtual slot +0x870 affects damage/protection or armor skill XP.",
        "predicted_discriminant": "Concrete recipient RTTI and the vtable target at byte offset +0x870 resolve to an Actor method with a path into mapped HitData/protection/AV11/AV12/UseSkill behavior.",
        "status": "proposed",
        "evidence": ["EV-0595"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")

assessment = "EV-0595 identifies caller 46's secondary event as tag 0x0A with a handle/scalar/vector/byte payload and a dispatcher-side virtual callback at recipient vtable byte offset +0x870. The direct path has no mapped hit/armor-skill target, but the unresolved receiver and virtual call prevent a transitive negative. Resolve a concrete producer/recipient type and the slot target, then continue caller 47."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_140657870's three direct callers and the relevant handle conversion/type path to identify the concrete recipient family; then resolve that family's vtable slot +0x870 and screen the target against mapped HitData/protection/AV11/AV12/UseSkill functions. Continue original worker caller 47/62 FUN_140658a30 after this bounded discriminator."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 continues caller 46/62: EV-0595 identifies a secondary tag-0x0A handle/vector worker event. Dispatcher case 10 reaches unresolved recipient vtable byte offset +0x870; direct mapped HitData/armor-skill calls were not found, but virtual type/effects remain open. Sixteen original callers remain.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0594 maps FUN_140717d10 to conditional nested-state reset and secondary worker builder FUN_140657870, whose tag remains unknown.",
    "EV-0594/0595 map FUN_140717d10 to a secondary tag-0x0A handle/vector worker update; its fallback calls unresolved recipient vtable slot +0x870, so receiver type and transitive effects remain open.",
    1,
)
old_next = "**Selected next line:** identify the secondary worker event built by `FUN_140657870` [EV-0594], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback types, event meaning, runtime object type, and GOG/Steam boundaries open."
new_next = "**Selected next line:** query the three direct callers of `FUN_140657870` and resolve the recipient type/vtable slot `+0x870` [EV-0595], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, event meaning, runtime object type, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0595/CL-L407/M-0148; supported H95, falsified H96, proposed H97; checkpointed vtable/type discriminator")
