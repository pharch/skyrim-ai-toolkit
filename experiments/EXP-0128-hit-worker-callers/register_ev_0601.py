from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T183142Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x189ec20" or str(meta.get("requested_vtable_slot", "")).lower() != "0xa":
    raise SystemExit("query identity/slot failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG binary identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
stdout = raw.read_text(encoding="utf-8", errors="replace")
for token in ("VTABLE_SLOT_INDEX=0xA", "VTABLE_SLOT_TARGET_RVA=0x1DFDC0", "VTABLE_RTTI_TYPE_NAME=.?AVActor@@", "FUN_140606580"):
    if token not in stdout:
        raise SystemExit(f"required slot result missing: {token}")

item = {
    "kind": "native",
    "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only query, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0601",
    "source": "Identity-checked GOG primary Actor vtable slot 0xA query",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x189EC20 --vtable-slot 0xA --timeout 600"],
    "coverage": "Primary GOG Actor vtable slot index 0xA (byte offset +0x50) resolves under RTTI .?AVActor@@ to FUN_1401dfdc0 at RVA 0x1DFDC0. The target returns a value; when global DAT_14317bfc0 is nonzero it directly delegates to FUN_140606580(global,param_1,param_2,0), otherwise it returns a zero-extended false-like result. One analyzed direct caller is FUN_1403a94e0. The query establishes slot identity and bounded body only; FUN_140606580 and runtime effects are unresolved.",
    "result": "The Actor callback invoked after FUN_1406be430 at byte offset +0x50 maps to FUN_1401dfdc0, which conditionally forwards Actor and selector arguments to global manager/helper FUN_140606580. This looks like a gated state/manager dispatch, but the target's effect remains unknown. No direct HitData, protection, AV11/AV12 or UseSkill edge is established, and no OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": {f".local/ghidra/{raw.name}": sha(raw), f".local/ghidra/{stderr.name}": sha(stderr), f".local/ghidra/{meta_path.name}": sha(meta_path)},
    "related_evidence": ["EV-0600", "EV-0598", "EV-0597"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0601" in existing and existing["EV-0601"] != item:
    raise SystemExit("EV-0601 collision")
if "EV-0601" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    target = ROOT / path
    contents = target.read_text(encoding="utf-8")
    if marker not in contents:
        target.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L413",
    "| CL-L413 | In GOG AE 1.6.1179.0, primary Actor vtable slot 0xA (+0x50) resolves to FUN_1401dfdc0, which conditionally delegates Actor and selector arguments to FUN_140606580 through global DAT_14317bfc0. | supported for the exact GOG slot/body | [EV-0601] | FUN_140606580 behavior, runtime recipient, transitive combat/skill effects, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0153 — Actor slot +0x50 forwards to a global state manager (EV-0601)",
    """## M-0153 — Actor slot `+0x50` forwards to a global state manager (EV-0601)

Primary GOG `VTABLE::Actor` slot `0xA` resolves to `FUN_1401dfdc0`. If global `DAT_14317bfc0` is nonzero, this method calls `FUN_140606580(global, Actor, selector, 0)`; otherwise it returns a false-like result [EV-0601]. The manager target is not yet traced. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L413.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Actor slot +0x50 manager dispatch following tag-0x0A vector helper (EV-0601)",
    """### Actor slot +0x50 manager dispatch following tag-0x0A vector helper (EV-0601)

The follow-up Actor slot `0xA` / byte offset `+0x50` maps to `FUN_1401dfdc0`; if global `DAT_14317bfc0` exists it delegates Actor and selector arguments to `FUN_140606580` [EV-0601]. Resolve that bounded manager/helper before closing caller 46; no P0 sink is established yet.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0601 extends tag-0x0A vector route into global manager helper",
    "EV-0601 maps the Actor +0x50 call after FUN_1406be430 to FUN_1401dfdc0, which conditionally forwards to FUN_140606580 through a global manager pointer. The recipient/helper behavior is unresolved; no OBJ-1/OBJ-2 causal edge is added.",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0601"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L413"]))
for candidate in (
    {
        "id": "Q79-H104",
        "model": "The Actor slot +0x50 called by tag-0x0A Actor method FUN_140699500 resolves to FUN_1401dfdc0 and conditionally delegates to FUN_140606580 via a global manager pointer.",
        "predicted_discriminant": "The identity-checked primary Actor vtable slot query returns RVA 0x1DFDC0; its body reads DAT_14317bfc0 and calls FUN_140606580 only on the nonzero branch.",
        "status": "supported",
        "evidence": ["EV-0601"],
    },
    {
        "id": "Q79-H105",
        "model": "The tag-0x0A follow-up manager call FUN_140606580 reaches HitData/protection/AV11/AV12/UseSkill behavior.",
        "predicted_discriminant": "The bounded manager target or its mapped direct descendants resolve to combat/protection/skill award sinks.",
        "status": "proposed",
        "evidence": ["EV-0601"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0601 resolves the Actor +0x50 call after the shared vector helper to FUN_1401dfdc0, which conditionally forwards into global helper FUN_140606580. The slot body is now bounded, but the manager target is the last direct discriminator before local caller 46 closure."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x606580 --list-call-edges --follow-direct-calls 8 --timeout 600; screen FUN_140606580's direct targets against mapped HitData/protection/AV11/AV12/UseSkill functions. Then close caller 46 as a bounded Actor/process vector/state event and continue original caller 47/62 FUN_140658a30."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013: caller 46 tag-0x0A Actor path reaches a vector helper and then Actor slot +0x50, which conditionally delegates to global helper FUN_140606580. Resolve this target's direct behavior before bounded closure, then continue caller 47/62.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "Resolve Actor slot 0xA (+0x50) called after the tag-0x0A vector helper [EV-0600], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open.",
    "Actor slot 0xA (+0x50) after the tag-0x0A vector helper resolves to FUN_1401dfdc0 and conditional global helper FUN_140606580 [EV-0601]; trace that manager target, then close caller 46 and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open.",
    1,
)
old_next = "**Selected next line:** resolve Actor vtable slot `0xA` / byte offset `+0x50` called after the tag-0x0A vector helper [EV-0600], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open."
new_next = "**Selected next line:** inspect `FUN_140606580` reached by the Actor slot `+0x50` transition [EV-0601], then close caller 46 as bounded and continue caller 47/62 `FUN_140658a30`. Keep the 45 remaining indirect sites and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0601/CL-L413/M-0153; supported H104, proposed H105; checkpointed FUN_140606580")
