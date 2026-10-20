from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T175439Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw = GH / f"{STEM}.stdout.raw"
stderr = GH / f"{STEM}.stderr.raw"
meta_path = GH / f"{STEM}.meta.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x40e300":
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
    "id": "EV-0588",
    "source": "Identity-checked GOG read-only call-edge census and decompilation of tag-0x40 handler FUN_14040e300",
    "artifact": f"private-local:.local/ghidra/{raw.name}",
    "sha256": meta["stdout_sha256"],
    "captured_utc": meta["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x40e300 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
    ],
    "coverage": "FUN_14040e300 has three direct callees, zero indirect call sites, and three incoming direct callsites in GOG 1.6.1179.0. The worker caller FUN_140659160 is among the incoming callers. The handler clears/sets fields on its first object, conditionally retains or clears the supplied object based on a byte flag, invokes FUN_14040e420, resets a shared global field, obtains one scalar through FUN_140635730 and writes it to two state offsets, then updates a bitfield. FUN_14040e420 contains a runtime type cast from a form lookup to TESImageSpace for form ID 0x167 and a separate scalar-threshold/update branch. FUN_140635730 reads a scalar from a global-owned object or returns a default. Exact payload RTTI and form provenance are not resolved. No direct mapped HitData, effective-protection, AV11/AV12, or UseSkill target appears in FUN_14040e300; transitive behavior beyond the inspected callees is not claimed.",
    "result": "The bounded tag-0x40 target is a state-reset/scalar-update routine with a TESImageSpace-related branch in its direct update helper, not a direct HitData or armor-skill handler. The exact object and scalar roles remain unknown, and the producer FUN_140357c70 still requires tracing through FUN_14033e470. This result does not identify the caller as an ordinary hit and does not change Q79-H1/H2/H3; no OBJ-1 or OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0574", "EV-0587", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0588" in existing and existing["EV-0588"] != item:
    raise SystemExit("EV-0588 collision")
if "EV-0588" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L400",
    "| CL-L400 | In GOG AE 1.6.1179.0, the tag-0x40 target FUN_14040e300 has three direct callees and no indirect sites; its direct update helper includes a TESImageSpace form-cast branch, and the target has no direct mapped HitData/effective-protection/AV11/AV12/UseSkill edge. | supported for the bounded handler body | [EV-0588], [EV-0574] | Payload type, TESImageSpace form provenance, transitive descendants, runtime semantics, and Steam equivalence remain unresolved. |",
)
append_once(
    "research/MECHANISMS.md",
    "## M-0143 — Tag-0x40 scalar/state update handler (EV-0588)",
    """## M-0143 — Tag-0x40 scalar/state update handler (EV-0588)

Worker case 0x40 reaches `FUN_14040e300` with an object and byte flag [EV-0574]. The exact handler resets/sets state fields, conditionally retains the supplied object, calls `FUN_14040e420`, reads a shared scalar through `FUN_140635730`, and updates two scalar fields plus a bitfield [EV-0588]. The direct update helper includes a form lookup and RTTI cast to `TESImageSpace` for form ID `0x167`; the submitted payload's RTTI and that form's plugin provenance are unknown. The handler has three direct callees, zero indirect call sites, and no direct mapped HitData/effective-protection/AV11/AV12/UseSkill edge. This is a bounded negative, not a transitive or gameplay negative. Producer `FUN_140357c70` and its `FUN_14033e470` result remain to be traced. Claim CL-L400.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 45/62 target: tag-0x40 scalar/state update (EV-0588)",
    """### Caller 45/62 target: tag-0x40 scalar/state update (EV-0588)

The worker's tag-0x40 case reaches `FUN_14040e300(object, payload, flag)` [EV-0574]. Its GOG 1.6.1179.0 call-edge census finds three direct callees and no indirect sites. The handler clears/reinitializes state, stores or clears the payload according to the flag, calls `FUN_14040e420`, reads a shared scalar using `FUN_140635730`, updates two scalar fields and a bitfield, and has a direct helper path that casts form ID `0x167` to `TESImageSpace` [EV-0588]. No direct mapped HitData/effective-protection/AV11/AV12/UseSkill sink appears. Payload RTTI, form provenance, descendant behavior and runtime role remain unknown. Q79-H1/H2/H3 are unchanged; caller 46/62 remains next.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0588 bounds the tag-0x40 handler",
    "EV-0588 bounds tag 0x40's FUN_14040e300 handler as a scalar/state update with a TESImageSpace-related direct helper branch and no direct mapped HitData/protection/AV11/AV12/UseSkill edge. Payload type, form provenance and transitive behavior remain unknown; no OBJ-1/OBJ-2 causal edge is added [EV-0574], [EV-0588].",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 45 tag-0x40 handler bounded (EV-0588)",
    """## Q-0079 update — caller 45 tag-0x40 handler bounded (EV-0588)

The tag-0x40 worker target `FUN_14040e300` has three direct callees and no indirect sites. It updates object/scalar state and invokes a helper with a `TESImageSpace` form-cast branch; no direct mapped HitData/effective-protection/AV11/AV12/UseSkill target appears [EV-0588]. Payload identity, form provenance and transitive behavior remain unknown; inspect producer `FUN_140357c70` through `FUN_14033e470` next [CL-L400], [M-0143].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0588"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L400"]))
assessment = "EV-0588 bounds caller 45's tag-0x40 handler as object/scalar state work with a TESImageSpace-related direct helper branch and no direct mapped HitData/protection/AV11/AV12/UseSkill target. This is not a transitive/runtime negative and does not classify the payload or alter Q79-H1/H2/H3. No OBJ-1/OBJ-2 causal edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x33e470 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; trace the sole tag-0x40 producer FUN_140357c70 through FUN_14033e470 to identify the source and role of its object/boolean outputs, testing whether the route approaches any mapped HitData/AV11/AV12/UseSkill target. Keep payload RTTI and GOG/Steam boundary unresolved unless the evidence resolves them; then continue caller 46/62."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 45/62 tag 0x40 reaches a scalar/state update handler with a TESImageSpace-related helper branch and no direct mapped HitData/protection/AV11/AV12/UseSkill sink. Eighteen original callers remain; trace producer FUN_140357c70 through FUN_14033e470 before caller 46.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace("44 of 62 initially uninspected worker callers are reviewed, with 18 remaining.", "45 of 62 initially uninspected worker callers are reviewed, with 17 remaining.", 1)
state = state.replace(
    "EV-0587 maps caller 44/tag 0x3f to the same helper from immediate and deferred paths with identical four-field payloads.",
    "EV-0587 maps caller 44/tag 0x3f to the same helper from immediate and deferred paths with identical four-field payloads. EV-0588 bounds caller 45/tag 0x40 as object/scalar state work with a TESImageSpace-related helper branch and no direct mapped combat/armor-skill sink.",
    1,
)
state = state.replace("Q-0079 has 44/62 exact worker callers reviewed; 18 remain.", "Q-0079 has 45/62 exact worker callers reviewed; 17 remain.", 1)
state = state.replace(
    "EV-0587 maps tag 0x3f immediate/deferred branches to the same four-field helper.",
    "EV-0587 maps tag 0x3f immediate/deferred branches to the same four-field helper; EV-0588 bounds tag 0x40 as a scalar/state update without a direct mapped combat/armor-skill sink.",
    1,
)
old_next = "**Selected next line:** inspect caller 45/62 `FUN_140658950` for its payload, producer, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0587]. Keep tag-0x3f nested object identity and virtual behavior unresolved; no armor causal edge is established."
new_next = "**Selected next line:** trace caller 45's producer `FUN_140357c70` through `FUN_14033e470` for the source/role of its object and boolean outputs [EV-0588]. Keep payload RTTI, TESImageSpace form provenance, transitive behavior, and the GOG/Steam boundary unresolved; then continue caller 46/62."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0588/CL-L400/M-0143; caller 45/62 bounded; checkpointed producer FUN_14033e470")
