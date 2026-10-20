from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
captures = []
for stem in ("gog-query-20261019T191026Z", "gog-query-20261019T191237Z"):
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"read-only/hash gate failed: {stem}")
    captures.append((raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace")))

graph_raw, _, _, graph_meta, graph = captures[0]
if "XREF_ANY=1418bb248 -> 1407bbb90 type=DATA source=<none> data=<none>" not in graph or "1418bb248:0x407BBB90" not in graph:
    raise SystemExit("candidate table pointer missing")
rtti_raw, _, _, rtti_meta, rtti = captures[1]
for token in ("VTABLE_RTTI_TABLE_RVA=0x18BB240", "VTABLE_RTTI_SUBOBJECT_OFFSET=0/0x0", "VTABLE_RTTI_TYPE_DESCRIPTOR_RVA=0x206F2A8", "VTABLE_RTTI_TYPE_NAME=.?AVAddRagdollHandler@@", "VTABLE_RTTI_CENSUS_COMPLETE=true"):
    if token not in rtti:
        raise SystemExit(f"RTTI identity missing: {token}")
hashes = {}
for raw, err, mp, _, _ in captures:
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0617",
    "source": "GOG RTTI census paired with the identity-checked producer's source-less code-pointer xref",
    "artifact": f"private-local:.local/ghidra/{rtti_raw.name}", "sha256": rtti_meta["stdout_sha256"], "captured_utc": rtti_meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --vtable-rtti-rvas 0x18bb240 --timeout 600", "paired with EV-0616 GOG producer xref words"],
    "coverage": "The table at RVA 0x18bb240 has an MSVC Complete Object Locator with signature 1, subobject offset 0, type descriptor RVA 0x206f2a8 and demangled name AddRagdollHandler. EV-0616 shows the qword at table RVA 0x18bb248 (zero-based slot 1) points to FUN_1407bbb90. Together these identify FUN_1407bbb90 as slot 1 of the GOG AddRagdollHandler primary vtable. This does not identify the method name, its second argument's concrete type, its triggering gameplay event, or an armor/HitData/skill effect.",
    "result": "Candidate vtable identity is confirmed: FUN_1407bbb90 is zero-based virtual slot 1 in RTTI-identified AddRagdollHandler at RVA 0x18bb240. The class name narrows the producer to a ragdoll-handler class route, but does not establish hit-trigger provenance or OBJ-2 relevance.",
    "local_hashes": hashes, "related_evidence": ["EV-0616", "EV-0615", "EV-0614", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0617")
if old and old != item:
    raise SystemExit("EV-0617 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L430", "| CL-L430 | GOG FUN_1407bbb90 is zero-based slot 1 in the RTTI-identified AddRagdollHandler primary vtable at RVA 0x18bb240. | supported for captured GOG RTTI and pointer-table identity | [EV-0616], [EV-0617] | Method name, argument type, gameplay trigger and armor/HitData/skill effect remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0170 — Caller 50 producer is AddRagdollHandler vtable slot 1 (EV-0617)", "## M-0170 — Caller 50 producer is AddRagdollHandler vtable slot 1 (EV-0617)\n\nRTTI identifies the table at RVA `0x18bb240` as primary `AddRagdollHandler` (subobject offset 0). The table's slot 1 points to `FUN_1407bbb90` [EV-0616], [EV-0617]. This identifies class membership only; method name, argument type, triggering event and gameplay effect remain unknown. No armor/HitData causal edge is established. Claim CL-L430.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 producer RTTI identity (EV-0617)", "### Caller 50/62 producer RTTI identity (EV-0617)\n\nThe candidate table base RVA `0x18bb240` validates with an MSVC Complete Object Locator and type descriptor `.?AVAddRagdollHandler@@`, subobject offset zero. EV-0616's qword at `0x18bb248` is the function pointer to `FUN_1407bbb90`, making it zero-based slot 1 in the primary vtable [EV-0617]. This identifies class membership, not the producer's method name, argument type, trigger or armor/HitData/skill effect. Next trace the queued continuation `FUN_140657c30`.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0617 identifies caller 50 producer as AddRagdollHandler slot 1", "EV-0617 joins caller 50's slot-1 function pointer to RTTI-identified primary vtable `AddRagdollHandler`. This is a static type identity edge only; trigger and gameplay-effect edges remain unsupported.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0617"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L430"]))
for hid, model, pred in (
    ("Q79-H125", "Caller 50's data xref at RVA 0x18bb248 is slot 1 in an RTTI-backed AddRagdollHandler vtable based at RVA 0x18bb240.", "The table's Complete Object Locator names AddRagdollHandler and the qword at base+8 points to FUN_1407bbb90."),
    ("Q79-H126", "Caller 50 producer FUN_1407bbb90 is a method in AddRagdollHandler, but its exact method purpose and gameplay trigger remain unresolved.", "The RTTI-identified AddRagdollHandler table contains FUN_1407bbb90 at zero-based slot 1; additional method/runtime evidence is needed for purpose and trigger."),
):
    h = {"id": hid, "model": model, "predicted_discriminant": pred, "status": "supported", "evidence": ["EV-0616", "EV-0617"]}
    prior = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if prior is None:
        q["hypotheses"].append(h)
    elif hid == "Q79-H125" and "likely RVA 0x18bb240" in prior.get("model", ""):
        prior.update(h)
    elif prior != h:
        raise SystemExit(f"hypothesis collision: {hid}")
next_action = "Trace FUN_140657c30 from the AddRagdollHandler slot-1 tag-0x49 producer with direct/incoming edges; determine whether the queued continuation shares the immediate vtable +0x1a8 operation, then resolve the shared FUN_14054e340 list callback."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 producer is RTTI-identified AddRagdollHandler slot 1; trace queued continuation FUN_140657c30.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_next = "**Selected next line:** test candidate RTTI-backed vtable base RVA `0x18bb240` found in caller 50 producer's adjacent code-pointer xref [EV-0616]; resolve its type before mapping `FUN_1407bbb90` virtual slots, then trace `FUN_140657c30` and list callbacks."
new_next = "**Selected next line:** trace queued continuation `FUN_140657c30` from RTTI-identified AddRagdollHandler slot 1's tag-0x49 producer [EV-0616–EV-0617]; compare it with the immediate `+0x1a8` call, then resolve shared list callback `FUN_14054e340`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0617/CL-L430/M-0170; identified AddRagdollHandler slot 1; checkpointed FUN_140657c30")
