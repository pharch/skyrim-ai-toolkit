from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
artifact = ROOT / ".local/alignment/transactions/TX-20261018-0013/address-library-vtable-actor.json"
raw = json.loads(artifact.read_text(encoding="utf-8"))
artifact_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
expected_binary = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
expected_library = "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e"
if not raw.get("ok") or raw.get("symbol") != "VTABLE::Actor" or raw.get("address_library_rva", "").lower() != "0x189ec20":
    raise SystemExit("Actor vtable symbol/RVA check failed")
if raw.get("analysis_binary_product_version") != "1.6.1179.0" or raw.get("analysis_binary_sha256") != expected_binary:
    raise SystemExit("GOG analysis-binary identity failed")
if raw.get("address_library_internal_version") != "1.6.1179.0" or raw.get("address_library_sha256") != expected_library:
    raise SystemExit("GOG Address Library identity failed")
if not raw.get("read_only"):
    raise SystemExit("read-only gate failed")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_binary}; matching GOG Address Library 1.6.1179.0 SHA-256 {expected_library}.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0597",
    "source": "Configured matching GOG Address Library VTABLE::Actor symbol resolution",
    "artifact": "private-local:.local/alignment/transactions/TX-20261018-0013/address-library-vtable-actor.json",
    "sha256": artifact_sha,
    "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "tools": ["strict Python 3.12 dispatcher", "tools/address_library_probe.py --symbol VTABLE::Actor"],
    "coverage": "The configured Address Library returns VTABLE::Actor array entry index 0, AE ID 207511, RVA 0x189EC20 for exact GOG SkyrimSE.exe 1.6.1179.0, with matching binary and Address Library hashes and read_only=true. The deprecated legacy symbol map has no runtime provenance and is explicitly not accepted. This supplies a GOG vtable base for a bounded read-only slot query only; it establishes no class behavior and no Steam RVA.",
    "result": "Matching GOG Address Library evidence locates primary VTABLE::Actor at RVA 0x189EC20. Query slot index 0x10e (byte offset +0x870) in the identity-checked existing GOG Ghidra project; do not transfer this RVA to Steam. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": {".local/alignment/transactions/TX-20261018-0013/address-library-vtable-actor.json": artifact_sha},
    "related_evidence": ["EV-0596", "EV-0291"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0597" in existing and existing["EV-0597"] != item:
    raise SystemExit("EV-0597 collision")
if "EV-0597" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L409",
    "| CL-L409 | The configured GOG Address Library matching SkyrimSE.exe 1.6.1179.0 maps primary VTABLE::Actor to RVA 0x189EC20 (AE ID 207511, array entry 0). | supported for the exact GOG build/library pair | [EV-0597] | The RVA is not a Steam address and the slot target/behavior is not yet resolved. |",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Matching GOG Actor vtable base for tag-0x0A slot resolution (EV-0597)",
    """### Matching GOG Actor vtable base for tag-0x0A slot resolution (EV-0597)

The matching GOG 1.6.1179.0 Address Library maps `VTABLE::Actor` array entry 0 (AE ID 207511) to RVA `0x189EC20` [EV-0597]. The deprecated legacy map lacks runtime provenance and is not used. Next read slot index `0x10e` (byte offset `+0x870`) from this exact GOG vtable and screen the target/callees; do not transfer this RVA to Steam.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0597 pins primary GOG Actor vtable base for slot query",
    "EV-0597 resolves primary GOG VTABLE::Actor to RVA 0x189EC20 for the exact GOG 1.6.1179.0 binary/Address Library pair. This supports the pending slot 0x10e target query only and creates no gameplay causal edge.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0597"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L409"]))
assessment = "EV-0597 resolves primary VTABLE::Actor to GOG RVA 0x189EC20 from the Address Library matching the exact GOG binary. This makes the recipient slot 0x10e query concrete; no Steam mapping or behavioral claim follows."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x189EC20 --vtable-slot 0x10e --timeout 600; record the exact slot target and screen its direct callees against mapped HitData/protection/AV11/AV12/UseSkill functions. Then continue original worker caller 47/62 FUN_140658a30 regardless of local resolution."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: the tag-0x0A event has an Actor-vtable-compatible producer route. EV-0597 pins the matching GOG Actor vtable at RVA 0x189EC20; query slot index 0x10e (+0x870) next, then continue caller 47/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0594–0596 map FUN_140717d10 to a secondary tag-0x0A handle/vector worker update. One producer is Actor-vtable-compatible through +0x4c8/slot 0x99, but dispatcher slot +0x870 and transitive effects remain open.",
    "EV-0594–0597 map FUN_140717d10 to a secondary tag-0x0A handle/vector worker update. One producer is Actor-vtable-compatible; matching GOG VTABLE::Actor is at RVA 0x189EC20, and slot 0x10e (+0x870) is next.",
    1,
)
old_next = "**Selected next line:** resolve primary GOG `VTABLE::Actor` slot `0x10e` (byte offset `+0x870`) [EV-0596], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, exact runtime type, event meaning, and GOG/Steam boundaries open."
new_next = "**Selected next line:** query GOG vtable RVA `0x189EC20`, slot `0x10e` (+`0x870`) [EV-0597], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback type, exact runtime type, event meaning, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0597/CL-L409; checkpointed GOG Actor slot query at 0x189EC20+0x10e")
