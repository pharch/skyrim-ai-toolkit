from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
IDENTITY = ("1.6.1179", "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f")
CAPTURES = [
    ("gog-query-20261019T165124Z", "0x659160"),
    ("gog-query-20261019T172253Z", "0x6c36e0"),
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
    raw_hash = hashlib.sha256(raw.read_bytes()).hexdigest()
    stderr_hash = hashlib.sha256(stderr.read_bytes()).hexdigest()
    if raw_hash != meta.get("stdout_sha256") or stderr_hash != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed: {stem}")
    hashes.update({
        f".local/ghidra/{raw.name}": raw_hash,
        f".local/ghidra/{stderr.name}": stderr_hash,
        f".local/ghidra/{meta_path.name}": hashlib.sha256(meta_path.read_bytes()).hexdigest(),
    })
    metas[stem] = meta

primary = GH / "gog-query-20261019T172253Z.stdout.raw"
item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0581",
    "source": "Identity-checked read-only GOG trace of tag-0x5d fallback case and shared FUN_1406c36e0 helper",
    "artifact": f"private-local:.local/ghidra/{primary.name}",
    "sha256": hashlib.sha256(primary.read_bytes()).hexdigest(),
    "captured_utc": metas["gog-query-20261019T172253Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x659160 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x6c36e0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "Worker fallback case 0x5d resolves the 32-bit payload value to an object and calls FUN_1406c36e0(resolved_object, eight_byte_payload), then releases the retained reference [gog-query-20261019T165124Z]. FUN_1406c36e0 has 11 direct callees, three indirect sites, and five direct caller functions including the worker. Its bounded body tests the second object, accesses a pointer-backed collection at the first object's +0x33/+0x34 members, locates/removes the matching object, adjusts a linked-list member at +0x31, clears matching entries in four slots starting at +0x39, handles a current-object member at +0x3d, invokes state helpers, and releases/compacts the collection. Two virtual calls at receiver slots +0x298 and +0x2e0 remain dynamic; concrete owner/reference types and the 8-byte payload semantics are unknown.",
    "result": "The exact tag-0x5d route is structurally an object membership/collection update and supports the bounded generic state-continuation model. The helper is shared by four other direct callers with distinct contexts, and its dynamic calls/types remain unresolved. No direct mapped HitData, AV11/AV12, UseSkill, effective-protection, or quest-initiation edge appears in the bounded helper/case. This does not establish a global combat or armor negative.",
    "local_hashes": hashes,
    "related_evidence": ["EV-0580", "EV-0397", "EV-0579", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0581" in existing and existing["EV-0581"] != item:
    raise SystemExit("EV-0581 collision")
if "EV-0581" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

append_once(
    "research/CLAIMS.md",
    "CL-L392",
    "| CL-L392 | In GOG AE 1.6.1179.0, worker case 0x5d resolves its handle and calls FUN_1406c36e0, whose bounded body removes a matching object from a pointer-backed collection and related list/fixed slots while invoking dynamic helpers. | supported for the exact case/helper body | [EV-0581], [EV-0580] | Owner/reference types, payload meaning, dynamic targets, and broader call effects remain unresolved; no direct HitData/AV11/AV12/UseSkill/protection/quest-start edge is established. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0138 — tag-0x5d object-membership update (EV-0580/0581)",
    """## M-0138 — tag-0x5d object-membership update (EV-0580/0581)

In GOG AE 1.6.1179.0, `FUN_140658810` constructs tag `0x5d` with a converted 32-bit value and an 8-byte payload; its sole observed producer is `FUN_1409e90c0` [EV-0580]. Worker fallback case `0x5d` resolves the handle and calls `FUN_1406c36e0(resolved_object, payload)` [EV-0581]. The helper locates and removes the supplied object from a pointer-backed collection, updates related list/fixed-slot members, invokes state helpers, and releases/compacts the collection. It has three indirect call sites and four other direct callers; concrete types, payload meaning, and dynamic effects remain unresolved. The bounded route supports a generic object-membership/state update and has no direct mapped HitData, AV11/AV12, UseSkill, effective-protection, or quest-start edge. No causal edge to OBJ-1 or OBJ-2 is added. Claim CL-L392.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 41/62: tag-0x5d case and collection-state helper (EV-0581)",
    """### Caller 41/62: tag-0x5d case and collection-state helper (EV-0581)

Worker fallback case `0x5d` resolves the event's 32-bit handle and calls `FUN_1406c36e0(resolved_object, eight_byte_payload)` [EV-0581]. The helper searches the first object's pointer-backed collection for the second object, removes it, updates associated linked-list/fixed-slot/current-object members, invokes state helpers, and releases/compacts the collection. Five functions call the helper directly; two virtual calls remain unresolved. This supports Q79-H75 for the bounded route. Q79-H76 remains proposed because the helper has dynamic calls and shared callers, although no direct mapped HitData/AV11/AV12/UseSkill edge appears in this case/helper. Next identify the exact native registration and producer context of `FUN_1409e90c0`; preserve source/type uncertainty and do not infer a P0-A or armor-XP result.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Q79-H75 supported after EV-0581",
    """Q79-H75 supported for the bounded caller-41 route: case `0x5d` calls `FUN_1406c36e0` with a resolved object; the helper removes matching object membership from a pointer-backed collection and updates related list/fixed-slot state [EV-0581]. Q79-H76 remains proposed because three indirect sites and four other direct callers are not classified; no case-local direct HitData/AV11/AV12/UseSkill edge is present.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/implications.md",
    "Caller 41 collection update cross-domain no-edge note",
    """Caller 41 cross-domain no-edge note: tag `0x5d` removes a resolved object from a manager-owned collection and related slots in the captured GOG path. The helper is shared with four other callers, and dynamic targets remain unknown. This is an object-membership/state operation in the bounded route; no causal link to quest initiation, HitData damage, effective protection, AV11/AV12 or armor XP is supported. Resolve the exact native registration before assigning the producer's semantic name.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0580/0581 adds tag-0x5d collection route",
    """EV-0580/0581 adds the tag-0x5d route: one producer builds a 32-bit converted-value/8-byte-payload event; the worker resolves the value and calls `FUN_1406c36e0`, which removes an object from a pointer-backed collection and updates related slots. Dynamic calls and concrete types remain unresolved. No causal edge to OBJ-1, armor mitigation, or armor-skill progression is supported.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0581"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L392"]))
h75 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H75")
h75["status"] = "supported"
h75["evidence"] = list(dict.fromkeys([*h75.get("evidence", []), "EV-0581"]))
h76 = next(h for h in q79["hypotheses"] if h.get("id") == "Q79-H76")
h76["evidence"] = list(dict.fromkeys([*h76.get("evidence", []), "EV-0581"]))
assessment = "Caller 41/62: worker case 0x5d calls FUN_1406c36e0, which removes a resolved object from a pointer-backed collection and updates related list/fixed-slot members [EV-0581]. This supports Q79-H75 for the bounded state route; Q79-H76 remains open because three indirect sites and other callers are unresolved. The producer's native registration name is the next discriminant; no OBJ-1 or armor-skill causal edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x9e90c0 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600; inspect FUN_1409e90c0's native registration/source context and producer arguments to identify the tag-0x5d operation. Preserve exact registry string evidence, unresolved handle conversion, and GOG/Steam boundaries."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 41/62 tag 0x5d reaches a bounded object-membership/collection update in FUN_1406c36e0. Q79-H75 is supported for this static route; H76 remains proposed because dynamic sites and other callers remain unresolved. Next resolve FUN_1409e90c0's exact native registration. 21 exact worker callers remain; P0-A and clean Steam armor/protection/raw-AVSK evidence remain open.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("registered EV-0581/CL-L392/M-0138 and supported Q79-H75; checkpointed native binding query")
