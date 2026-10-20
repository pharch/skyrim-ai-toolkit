from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T172013Z"
EXPECTED_RVA = "0x658810"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != EXPECTED_RVA:
    raise SystemExit("caller-41 request identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f":
    raise SystemExit("caller-41 GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("caller-41 read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("caller-41 raw hash check failed")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0580",
    "source": "Identity-checked read-only GOG query of exact worker caller 41/62 FUN_140658810 and its sole direct producer",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": sha(raw),
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658810 --list-call-edges --timeout 600"],
    "coverage": "FUN_140658810 writes tag 0x5d, copies one 32-bit value from its second argument, copies its third argument as an 8-byte payload, and calls FUN_14065b800. One direct caller, FUN_1409e90c0, derives the 32-bit value through FUN_140178cf0(param_3) or uses DAT_1420f7d9c, then passes param_4 as the 8-byte payload. The API/source semantics and worker case target are not identified by this capture.",
    "result": "Caller 41 is a one-producer tag-0x5d value/handle continuation with an unresolved payload meaning. Its builder has no direct HitData, ActorValue, UseSkill, protection, or quest-start edge. Competing models remain: a generic Actor-associated/state update versus a continuation into combat/skill processing; trace the matched case target before classification.",
    "local_hashes": {
        f".local/ghidra/{raw.name}": sha(raw),
        f".local/ghidra/{stderr.name}": sha(stderr),
        f".local/ghidra/{meta_path.name}": sha(meta_path),
    },
    "related_evidence": ["EV-0579", "EV-0397", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in doc["items"]}
if "EV-0580" in existing and existing["EV-0580"] != item:
    raise SystemExit("EV-0580 collision")
if "EV-0580" not in existing:
    doc["items"].append(item)
evidence_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, text: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + text.rstrip() + "\n", encoding="utf-8")

append_once(
    "research/CLAIMS.md",
    "CL-L391",
    "| CL-L391 | In GOG AE 1.6.1179.0, worker caller FUN_140658810 builds tag 0x5d with one copied 32-bit value and one 8-byte payload; its sole captured direct producer FUN_1409e90c0 derives the first through FUN_140178cf0 or a default global. | supported for the exact builder/producer flow | [EV-0580] | Source/API meaning and matched worker-case semantics are unresolved; no HitData/ActorValue/UseSkill/protection/quest-start edge is established. |",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 41/62: tag-0x5d builder and one producer (EV-0580)",
    """### Caller 41/62: tag-0x5d builder and one producer (EV-0580)

`FUN_140658810` builds tag `0x5d` with a copied 32-bit value and an 8-byte payload, then calls the generic worker. Its only captured producer is `FUN_1409e90c0`, which obtains the 32-bit value through `FUN_140178cf0(param_3)` or a default global and forwards `param_4` [EV-0580]. The API and argument meanings remain unknown. Competing models for the next probe: a generic Actor-associated/state update predicts a bounded helper without a mapped HitData/AV11/AV12/UseSkill sink; a combat/skill continuation predicts a producer-backed path to one of those mapped sinks. Query the exact tag-0x5d dispatcher target `FUN_1406c36e0` before classifying this caller. No P0-A or P0-B edge is established.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "## Caller 41 competing models",
    """## Caller 41 competing models

- Q79-H75: tag 0x5d is a generic Actor-associated/state continuation. Prediction: matched case `0x5d` and `FUN_1406c36e0` perform bounded state/property work without a producer-backed mapped HitData, AV11/AV12, or UseSkill sink. Proposed [EV-0580].
- Q79-H76: tag 0x5d carries a combat or skill-processing continuation. Prediction: the matched dispatcher/helper or its exact producer-backed descendants reach mapped HitData/AV11/AV12/UseSkill processing with the payload consumed in that route. Proposed [EV-0580].""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md",
    "EV-0580 caller 41 discriminants",
    """EV-0580 caller 41 discriminants: follow worker case `0x5d` to `FUN_1406c36e0` and trace the payload plus the sole producer `FUN_1409e90c0`. A state/property path supports Q79-H75; a producer-backed edge into mapped HitData, AV11/AV12, or UseSkill supports Q79-H76. Keep the native registration name and the 32-bit converter's semantics unknown until their exact registry/source evidence is captured.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0580"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L391"]))
for hyp in [
    {"id": "Q79-H75", "model": "Tag 0x5d is a generic Actor-associated/state continuation.", "predicted_discriminant": "The exact case 0x5d target and producer-backed callee path perform bounded state/property work without reaching mapped HitData, AV11/AV12, or UseSkill sinks.", "status": "proposed", "evidence": ["EV-0580"]},
    {"id": "Q79-H76", "model": "Tag 0x5d carries a combat or skill-processing continuation.", "predicted_discriminant": "The matched case/helper or its exact producer-backed descendants reach mapped HitData, AV11/AV12, or UseSkill processing, with the tag payload consumed on that route.", "status": "proposed", "evidence": ["EV-0580"]},
]:
    existing_hyp = next((h for h in q79.get("hypotheses", []) if h.get("id") == hyp["id"]), None)
    if existing_hyp is None:
        q79.setdefault("hypotheses", []).append(hyp)
    elif existing_hyp != hyp:
        raise SystemExit(f"hypothesis collision: {hyp['id']}")
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6c36e0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; resolve worker case 0x5d's FUN_1406c36e0 target and test Q79-H75 state/property versus Q79-H76 combat/skill predictions. Preserve exact payload provenance, dynamic calls, and GOG/Steam boundaries."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 active on OBJ-2: caller 41/62 FUN_140658810 is a one-producer tag-0x5d payload builder. Its source/API and semantics remain unknown; H75 generic Actor-state continuation and H76 combat/skill continuation are explicit rivals. 21 exact worker callers remain after this caller. P0-A and clean Steam armor/protection/raw-AVSK evidence remain open.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("registered EV-0580/CL-L391 and caller-41 discriminants; checkpointed FUN_1406c36e0")
