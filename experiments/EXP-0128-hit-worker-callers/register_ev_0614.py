from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
stems = ("gog-query-20261019T190025Z", "gog-query-20261019T190518Z")
captures = []
for stem in stems:
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG query identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture integrity/read-only gate failed: {stem}")
    captures.append((raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace")))

builder_raw, _, _, builder_meta, builder = captures[0]
for token in (
    "FUNCTION_LOOKUP=FUN_140658ac0 @ 140658ac0",
    "XREF_ANY=143657848 -> 140658ac0 type=DATA source=<none> data=<none>",
    "143657848:0x00658AC0,14365784c:0x00658AFE,143657850:0x01D4F8F0",
):
    if token not in builder:
        raise SystemExit(f"builder xref word pattern missing: {token}")
address_raw, _, _, address_meta, address = captures[1]
for token in (
    "ADDRESS_RVA=0x3657848",
    "ADDRESS_FUNCTION_LOOKUP=<no-function>",
    "ADDRESS_TARGET_XREF_COUNT=0",
    "ADDRESS_CONTEXT_INSTRUCTION_COUNT=0",
    "ADDRESS_CONTEXT_COMPLETE=true",
):
    if token not in address:
        raise SystemExit(f"address-context result missing: {token}")

hashes = {}
for raw, err, mp, _, _ in captures:
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0614",
    "source": "GOG FUN_140658ac0 data-xref word neighborhood and address-only context, compared with the prior documented x64 RUNTIME_FUNCTION discriminator",
    "artifact": f"private-local:.local/ghidra/{builder_raw.name}", "sha256": builder_meta["stdout_sha256"], "captured_utc": builder_meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x658af0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "tools/ghidra_probe.py --address-rva 0x3657848 --timeout 600", "Microsoft Learn x64 exception handling layout as previously captured in EV-0591"],
    "coverage": "The caller-49 query reports a source-less DATA xref from RVA 0x3657848 to FUN_140658ac0. Its local DWORDs at +0x848/+0x84c/+0x850 are 0x658ac0, 0x658afe, 0x1d4f8f0: the first is the Ghidra-verified function start, and the three-value sequence matches the x64 RUNTIME_FUNCTION (begin RVA, end RVA, unwind-info RVA) shape documented and independently matched against a known handler in EV-0591. The address-only query finds no function, code xrefs or instructions at the data address. This strongly supports unwind metadata rather than application registration; the exact containing PE section was not separately enumerated.",
    "result": "Caller 49's sole source-less data xref is strongly supported as an x64 RUNTIME_FUNCTION unwind record, not a gameplay registration lead. This classifies the data reference only; it adds no OBJ-1/OBJ-2 causal edge and does not identify the tag-0x48 callback implementation.",
    "local_hashes": hashes, "related_evidence": ["EV-0612", "EV-0613", "EV-0591", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0614")
if old and old != item:
    raise SystemExit("EV-0614 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L427", "| CL-L427 | Caller 49's only source-less DATA xref at RVA 0x3657848 has neighboring DWORDs 0x658ac0, 0x658afe, 0x1d4f8f0 matching the x64 RUNTIME_FUNCTION begin/end/unwind-info layout, so the reference is strongly supported as unwind metadata rather than gameplay registration. | strongly supported inference for this record | [EV-0614], [EV-0591]; Microsoft Learn x64 exception-handling layout | Exact containing PE section was not separately verified; no gameplay causal edge is inferred. |")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 49/62 data-xref classification and bounded closure (EV-0614)", "### Caller 49/62 data-xref classification and bounded closure (EV-0614)\n\nThe sole source-less DATA xref at RVA `0x3657848` points to `FUN_140658ac0`. Its neighboring DWORDs `0x658ac0`, `0x658afe`, and `0x1d4f8f0` match the x64 `RUNTIME_FUNCTION` begin/end/unwind-info layout, as documented and independently matched against a known GOG handler in EV-0591. The address-only query found no function or instructions there. This strongly supports compiler unwind metadata rather than application registration; the exact PE section remains unverified [EV-0614]. Caller 49 is closed as a bounded generic tag-0x48 list-callback route [EV-0612–EV-0614]. No OBJ-1/OBJ-2 causal edge or global negative is added. Continue caller 50/62 `FUN_140658b10`.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0614 reclassifies caller 49's data xref as likely unwind metadata", "EV-0614's three neighboring DWORDs at caller 49's sole data xref match the x64 `RUNTIME_FUNCTION` begin/end/unwind-info layout previously tested in EV-0591. The reference is likely unwind metadata rather than gameplay registration; its exact PE section is unverified. No OBJ-1/OBJ-2 causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0614"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L427"]))
for h in (
    {"id": "Q79-H121", "model": "Caller 49's source-less data xref at RVA 0x3657848 is an x64 RUNTIME_FUNCTION unwind record, not an application descriptor.", "predicted_discriminant": "The xref neighborhood contains the function-start, function-end and unwind-info DWORDs in the documented order and no instruction/function body at the metadata address.", "status": "supported", "evidence": ["EV-0614", "EV-0591"]},
    {"id": "Q79-H122", "model": "Caller 49's source-less data xref is a gameplay or application registration descriptor.", "predicted_discriminant": "The referenced word neighborhood resolves as a registration structure rather than the documented x64 RUNTIME_FUNCTION triple.", "status": "falsified", "evidence": ["EV-0614"]},
):
    prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
    if prior is None:
        q["hypotheses"].append(h)
    elif prior != h:
        raise SystemExit(f"hypothesis collision: {h['id']}")
assessment = "EV-0614 strongly supports caller 49's sole data xref as an x64 RUNTIME_FUNCTION record, not application registration; exact section remains unverified."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Inspect caller 50/62 FUN_140658b10: identify its tag and payload, producer and immediate/deferred paths; compare its dispatcher case and direct call edges with mapped HitData/protection/AV11/AV12/UseSkill sinks."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 49 is bounded as tag-0x48 generic list callback with likely unwind-metadata xref; continue caller 50/62.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0612–EV-0613 bound caller 49's tag-0x48 list route to a generic vtable callback; its data xref remains unresolved.", "EV-0612–EV-0614 bound caller 49's tag-0x48 list route to a generic vtable callback and classified its sole data xref as likely unwind metadata.", 1)
old_next = "**Selected next line:** classify caller 49's sole source-less data xref RVA `0x3657848` after tracing its generic tag-0x48 list helper [EV-0612–EV-0613]; then continue caller 50/62."
new_next = "**Selected next line:** inspect caller 50/62 `FUN_140658b10` for its tag/payload, producer and direct route to mapped HitData/protection/AV11/AV12/UseSkill sinks after closing caller 49's bounded list route and likely unwind-metadata xref [EV-0612–EV-0614]."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0614/CL-L427; caller 49 xref strongly matches unwind metadata; checkpointed caller 50/62")
