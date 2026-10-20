from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T184125Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0xd1ed80":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=140d1ee4c -> 140d20780",
    "INDIRECT_CALL_SITE=140d1edc0 CALL qword ptr [RAX + 0x1c8]",
    "XREF_CALL_EDGE=1401fdc2d -> 140d1ed80",
    "XREF_CALL_EDGE=140d2a89a -> 140d1ed80",
    "XREF_CALL_EDGE=140e2bb18 -> 140d1ed80",
    "XREF_CALL_EDGE=1401fdd2e -> 140d1ed80",
    "plVar2[6] = 0",
    "FUN_140d20780(param_1 + 0x22",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0605",
    "source": "Identity-checked GOG direct-edge census/decompilation of FUN_140d1ed80 and four callers",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0xd1ed80 --list-call-edges --follow-incoming-calls 8 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_140d1ed80 has one direct callee FUN_140d20780, six unresolved indirect calls including manager vtable +0x1c8, and four direct callers: FUN_1401fdb80, sibling FUN_1401fdc70, FUN_140d2a7f0 and FUN_140e2bad0. For a key whose field at object +0x38 is -1, it scans the manager array at param_1[0x23] by pointer identity; on a match it clears object fields +0x30/+0x38 and removes that array entry through FUN_140d20780. The direct callee removes a refcounted array slot and updates its count. Other key cases dispatch through unresolved manager vtable +0x1c8. No direct HitData/protection/AV11/AV12/UseSkill sink occurs in the captured bodies; the virtual route and full transitive callers remain unresolved.",
    "result": "The tag-0x44 helper's fallback is another refcounted manager-array removal/lookup path with an object-key special case, shared by three other callers. This supports a generic object-registry/state interpretation but leaves manager vtable +0x1c8 and transitive behavior open, so the combat-effect hypothesis is narrowed rather than falsified. No OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": hashes, "related_evidence": ["EV-0604", "EV-0603", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0605")
if old and old != item:
    raise SystemExit("EV-0605 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L417", "| CL-L417 | In GOG AE 1.6.1179.0, FUN_140d1ed80 performs object-identity removal from a manager-owned refcounted array when an object key field is -1, otherwise using unresolved manager vtable +0x1c8; it has four observed callers including FUN_1401fdb80. | supported for captured static branches | [EV-0605] | Virtual branch meaning, runtime object types, downstream effects and Steam equivalence remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0157 — Tag-0x44 keyed fallback manipulates a manager-owned object array (EV-0605)", "## M-0157 — Tag-0x44 keyed fallback manipulates a manager-owned object array (EV-0605)\n\n`FUN_140d1ed80` scans a manager-owned refcounted array by pointer identity when the object key at `+0x38` is `-1`, clears object state and removes the array slot through `FUN_140d20780`; other key values dispatch through unresolved manager vtable `+0x1c8` [EV-0605]. Four callers share the helper, including sibling collection code. The direct branch is object-registry state work without a mapped HitData/armor-skill sink; virtual and transitive effects remain open. No OBJ-1/OBJ-2 edge is added. Claim CL-L417.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 47/62: manager-array fallback bounds tag-0x44 state route (EV-0605)", "### Caller 47/62: manager-array fallback bounds tag-0x44 state route (EV-0605)\n\n`FUN_140d1ed80` has four callers and one direct array-removal helper. For object key `-1`, it searches a manager-owned refcounted array by pointer identity, clears fields `+0x30/+0x38`, and removes the slot through `FUN_140d20780`; other keys use unresolved manager vtable `+0x1c8` [EV-0605]. This supports a generic registry/state path but leaves the virtual branch and downstream effects open. Next inspect tag-0x44 object factories and their producer callers, then continue caller 48/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0605 traces tag-0x44 fallback into manager-owned array removal", "EV-0605 traces FUN_140d1ed80 to manager-array removal for object-key -1 and unresolved manager vtable +0x1c8 for other keys. Four callers share the helper; its generic data structure does not establish gameplay effect. No OBJ-1/OBJ-2 causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0605"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L417"]))
h = {"id": "Q79-H111", "model": "The clear-gate tag-0x44 fallback removes objects from a manager-owned refcounted array when the object key is -1; other key values use a manager virtual dispatch.", "predicted_discriminant": "The direct body scans manager array by object identity and removes a matching slot through FUN_140d20780, while the non-minus-one branch dispatches vtable +0x1c8.", "status": "supported", "evidence": ["EV-0605"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H111")
q["hypotheses"] = [dict(x, evidence=list(dict.fromkeys([*x.get("evidence", []), "EV-0605"]))) if x.get("id") == "Q79-H109" else x for x in q["hypotheses"]]
assessment = "EV-0605 traces the tag-0x44 helper's keyed fallback to manager-owned refcounted-array removal for the -1 object-key case; other keys use unresolved vtable +0x1c8. The shared generic structure further narrows the caller-specific combat model without resolving the virtual route."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query tag-0x44 object acquisition helpers FUN_1404a27f0 and FUN_1404a28a0 with direct/incoming call edges to identify their returned object family and any producer-specific virtual target. Then continue original worker caller 48/62 FUN_140658a80; preserve the unresolved manager vtable +0x1c8 route."
q["next_action"] = next_action
fr["next_action"] = next_action
fr["session_next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: EV-0605 bounds the tag-0x44 key -1 route as manager-owned refcounted-array removal; other keys use unresolved manager virtual +0x1c8. Four callers share this generic helper.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("Q-0079/TX-20261018-0013 remains active on OBJ-2: 46 of 62 initially uninspected worker callers are reviewed, with 16 remaining.", "Q-0079/TX-20261018-0013 remains active on OBJ-2: 47 of 62 initially uninspected worker callers are reviewed, with 15 remaining. EV-0603–EV-0605 bound caller 47's tag-0x44 immediate route to generic manager-array cleanup with unresolved virtual effects.", 1)
state = state.replace("**OBJ-2:** Q-0079 has 46/62 exact worker callers reviewed; 16 remain.", "**OBJ-2:** Q-0079 has 47/62 exact worker callers reviewed; 15 remain. EV-0603–EV-0605 map caller 47/tag 0x44 through a gated object producer into manager-array membership cleanup; unresolved virtual effects and the clean Steam protection/raw-AVSK test remain open.", 1)
old_next = "**Selected next line:** inspect keyed fallback `FUN_140d1ed80` and caller-47 object acquisition helpers after EV-0604 bounds `FUN_1401fdb80` as pointer-array cleanup; then continue caller 48/62 `FUN_140658a80`. Keep unresolved virtual effects and GOG/Steam boundaries open."
new_next = "**Selected next line:** query caller-47 object factories `FUN_1404a27f0` and `FUN_1404a28a0` to identify the returned object family, then continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old_next, new_next, 1), encoding="utf-8")
print("registered EV-0605/CL-L417/M-0157; H111 supported; caller 47/62 checkpointed")
