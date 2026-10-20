from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T181210Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x717d10":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")

local_hashes = {
    f".local/ghidra/{raw.name}": sha(raw),
    f".local/ghidra/{stderr.name}": sha(stderr),
    f".local/ghidra/{meta_path.name}": sha(meta_path),
}
item = {
    "kind": "native",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0594",
    "source": "Identity-checked GOG trace of tag-0x43 state helper descendant FUN_140717d10",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x717d10 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_140717d10 has one unique direct callee (FUN_1406671b0), zero indirect sites, and two analyzed direct callers (FUN_1406bbff0 and FUN_1406bc100). It compares a supplied byte with a nested object's +0x332 byte, clears nested +0x2f8 and +0x332 state fields, and calls FUN_1406671b0 when the prior count exceeds one. FUN_1406671b0 may derive a value, store it at the caller object's +0x108, and call worker builder FUN_140657870. The inspected bodies expose no mapped HitData/effective-protection/AV11/AV12/UseSkill target. FUN_140657870's tag/payload and descendants remain to be identified; no object RTTI or runtime interpretation is claimed.",
    "result": "The direct descendant from the tag-0x43 helper is another conditional nested-state reset/update. When a nested count exceeds one, it routes through FUN_1406671b0 and may submit a separate worker builder event FUN_140657870; that builder is the next discriminant. This bounded path has no direct mapped HitData/armor-skill target, but the builder tag and descendants remain unresolved. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0592", "EV-0593", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0594" in existing and existing["EV-0594"] != item:
    raise SystemExit("EV-0594 collision")
if "EV-0594" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L406",
    "| CL-L406 | In GOG AE 1.6.1179.0, FUN_140717d10 compares and clears nested state fields at +0x332/+0x2f8 and may call FUN_1406671b0; the inspected direct bodies show no mapped HitData/protection/AV11/AV12/UseSkill target. | supported for the bounded direct path | [EV-0594] | FUN_140657870's event tag, descendants, runtime object type, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0147 — Nested-state reset may emit a separate worker update (EV-0594)",
    """## M-0147 — Nested-state reset may emit a separate worker update (EV-0594)

`FUN_140717d10` checks a supplied byte against nested field `+0x332`, clears nested fields `+0x2f8`/`+0x332`, and conditionally calls `FUN_1406671b0` [EV-0594]. That helper may derive and store a value at the parent `+0x108`, then call worker builder `FUN_140657870`. The builder's tag and downstream behavior remain unknown; the bounded inspected route shows no mapped HitData/protection/AV11/AV12/UseSkill target. No OBJ-1/OBJ-2 edge is established. Claim CL-L406.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 46/62 descendant check: FUN_140717d10 (EV-0594)",
    """### Caller 46/62 descendant check: FUN_140717d10 (EV-0594)

The descendant `FUN_140717d10` has one direct callee and no indirect sites. It checks a byte against nested `+0x332`, clears `+0x2f8` and `+0x332`, and conditionally calls `FUN_1406671b0`; that helper may update parent `+0x108` and submit builder `FUN_140657870` [EV-0594]. No mapped HitData/effective-protection/AV11/AV12/UseSkill target appears in these inspected bodies. Identify the secondary builder's tag once, then continue caller 47/62; object types and runtime effects remain unknown.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0594 adds a nested-state update under tag-0x43 helper",
    "EV-0594 shows that FUN_140717d10 conditionally resets nested state and may route through FUN_1406671b0 to worker builder FUN_140657870. The bounded bodies expose no mapped HitData/protection/AV11/AV12/UseSkill target, but the secondary event tag remains unknown [EV-0593], [EV-0594]. No OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0594"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L406"]))
for candidate in (
    {
        "id": "Q79-H93",
        "model": "FUN_140717d10 is a conditional nested-state reset/update that can forward a secondary state event through FUN_1406671b0 to FUN_140657870.",
        "predicted_discriminant": "The body compares and clears nested state fields and its conditional helper submits a worker-builder event without a mapped HitData/armor-skill target.",
        "status": "supported",
        "evidence": ["EV-0594"],
    },
    {
        "id": "Q79-H94",
        "model": "FUN_140717d10 directly resolves HitData, effective protection, or AV11/AV12/UseSkill effects.",
        "predicted_discriminant": "Its direct body or sole direct callee calls a mapped HitData/armor-skill target.",
        "status": "falsified",
        "evidence": ["EV-0594"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0594 extends caller 46's state route through conditional nested-field reset and a possible secondary builder FUN_140657870. That builder's tag remains unknown; the inspected direct bodies still expose no mapped hit/armor-skill target. Keep this bounded and do not infer whole-path/runtime behavior."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x657870 --list-call-edges --timeout 600; identify the secondary worker event built by FUN_1406671b0 and screen its direct target against mapped HitData/protection/AV11/AV12/UseSkill functions. Then continue original worker caller 47/62 FUN_140658a30 regardless of local resolution."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 46/62's tag-0x43 helper has seven queue/direct-equivalent producers and conditional nested-state descendants. FUN_140717d10 can route to secondary worker builder FUN_140657870; its tag is next. Sixteen original callers remain.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "The helper updates a three-bit state and has no direct mapped hit/armor-skill sink, though three virtual callbacks and FUN_140717d10 remain open.",
    "The helper updates a three-bit state and has no direct mapped hit/armor-skill sink; EV-0594 maps FUN_140717d10 to conditional nested-state reset and secondary worker builder FUN_140657870, whose tag remains unknown.",
    1,
)
old_next = "**Selected next line:** inspect descendant `FUN_140717d10` reached through `FUN_1406bc100` [EV-0593]; if it remains state work, continue caller 47/62 `FUN_140658a30`. Keep virtual callback types, event meaning, runtime object type, and GOG/Steam boundaries open."
new_next = "**Selected next line:** identify the secondary worker event built by `FUN_140657870` [EV-0594], then continue caller 47/62 `FUN_140658a30`. Keep virtual callback types, event meaning, runtime object type, and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0594/CL-L406/M-0147; supported H93, falsified H94; checkpointed secondary builder FUN_140657870")
