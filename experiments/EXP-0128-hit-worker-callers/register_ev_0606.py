from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T184734Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x4a27f0":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "OUTGOING_DIRECT_CALL_EDGE=1404a2862 -> 1401fe280",
    "INDIRECT_CALL_SITE=1404a2850 CALL qword ptr [RAX + 0x8]",
    "XREF_CALL_EDGE=1401fa06e -> 1404a27f0",
    "XREF_CALL_EDGE=1401fd9b1 -> 1404a27f0",
    "XREF_CALL_EDGE=1401fe154 -> 1404a27f0",
    "BGSDecalNode::vftable",
    "FUN_1404a27f0(&local_res10,*(undefined4 *)(lVar4 + 0x28)",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")

hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0606",
    "source": "Identity-checked GOG direct-edge census/decompilation of tag-0x44 object factory FUN_1404a27f0 and its three callers",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x4a27f0 --list-call-edges --follow-incoming-calls 16 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1404a27f0 scans global pointer array DAT_1431461e8/count DAT_1431461f8 for an entry whose field +0x28 matches the supplied 32-bit key, returns a refcounted pointer, then removes that global array entry through FUN_1401fe280. It has one unresolved refcount-finalizer virtual site and three callers: tag-0x44 producer FUN_1401fa010 plus FUN_1401fd930 and FUN_1401fe0d0, both of which write the Ghidra-labeled BGSDecalNode vftable and invoke the same factory while cleaning child entries. One caller checks child vtable +0x10 against DAT_143146390 and clears child +0x170 before lookup. This associates the global registry with BGSDecalNode cleanup but does not establish the factory result's exact dynamic type or the meaning of the tag-0x44 key.",
    "result": "The tag-0x44 clear-gate factory uses a keyed global object registry also reached by two BGSDecalNode-labeled cleanup functions. This strongly favors generic scene/decal-object lifecycle work over HitData/armor-skill logic, but returned type and alternate factory FUN_1404a28a0 remain unresolved. No direct OBJ-1/OBJ-2 edge is added.",
    "local_hashes": hashes, "related_evidence": ["EV-0605", "EV-0604", "EV-0603", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0606")
if old and old != item:
    raise SystemExit("EV-0606 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L419", "| CL-L419 | In GOG AE 1.6.1179.0, FUN_1404a27f0 removes a keyed object from global array DAT_1431461e8 after retaining it; two of its three callers are Ghidra-labeled BGSDecalNode cleanup functions that call it with child +0x28. | supported as a registry association | [EV-0606] | Exact result type, key meaning, one unresolved finalizer, alternate factory FUN_1404a28a0, and gameplay effects remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0159 — Tag-0x44 object factory shares a keyed registry with BGSDecalNode cleanup (EV-0606)", "## M-0159 — Tag-0x44 object factory shares a keyed registry with BGSDecalNode cleanup (EV-0606)\n\n`FUN_1404a27f0` finds a global-array entry by its +0x28 key, retains it, then removes the entry through `FUN_1401fe280`. Two other callers are Ghidra-labeled BGSDecalNode cleanup routines that call the same factory on child +0x28 keys [EV-0606]. This associates the registry with scene/decal-object cleanup and further weakens a combat interpretation; it does not type the returned object or resolve the alternate factory and finalizer. No OBJ-1/OBJ-2 edge is added. Claim CL-L419.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 47/62: keyed factory shares a registry with BGSDecalNode cleanup (EV-0606)", "### Caller 47/62: keyed factory shares a registry with BGSDecalNode cleanup (EV-0606)\n\n`FUN_1404a27f0` looks up a global-array object by field +0x28, returns a retained reference, and removes the entry. Its other two callers are Ghidra-labeled BGSDecalNode cleanup bodies that perform the same keyed lookup on child entries [EV-0606]. This supports a scene/decal registry association for the tag-0x44 route, but exact result type and alternate factory remain open. Next inspect `FUN_1404a28a0`, then continue caller 48/62.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0606 associates tag-0x44 object factory with BGSDecalNode cleanup", "EV-0606 shows tag-0x44's FUN_1404a27f0 factory retrieving/removing global-array entries by +0x28 key; the same factory is used by two BGSDecalNode-labeled cleanup callers. This is a registry association, not exact returned RTTI or proof of game effect. It weakens a combat interpretation but does not close unresolved dispatch.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0606"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L419"]))
h = {"id": "Q79-H112", "model": "Caller-47 tag 0x44's key-based object factory uses a global registry also consumed by BGSDecalNode cleanup, favoring a scene/decal-object lifecycle route.", "predicted_discriminant": "FUN_1404a27f0 looks up and removes global-array entries by +0x28 key, and BGSDecalNode-labeled cleanup callers invoke it on child keys.", "status": "supported", "evidence": ["EV-0606"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H112")
q["hypotheses"] = [dict(x, evidence=list(dict.fromkeys([*x.get("evidence", []), "EV-0606"]))) if x.get("id") == "Q79-H109" else x for x in q["hypotheses"]]
assessment = "EV-0606 associates tag-0x44's keyed object factory with two Ghidra-labeled BGSDecalNode cleanup callers using the same global array/key. This further weakens a combat/armor interpretation while leaving the returned type, alternate factory, and virtual finalizer unresolved."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Query FUN_1404a28a0 with direct/incoming edges to compare the no-argument factory with the keyed global BGSDecalNode-associated registry route; then close caller 47 as a bounded generic object-cleanup result unless the alternate path yields a mapped combat/armor sink, and continue caller 48/62 FUN_140658a80."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: EV-0606 links caller 47's keyed global object factory to two BGSDecalNode-labeled cleanup callers; alternate factory FUN_1404a28a0 remains to compare.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** query caller-47 object factories `FUN_1404a27f0` and `FUN_1404a28a0` to identify the returned object family, then continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
new = "**Selected next line:** inspect alternate factory `FUN_1404a28a0` against the keyed registry association with BGSDecalNode cleanup [EV-0606]; then close caller 47 as bounded if no combat/armor sink appears and continue caller 48/62 `FUN_140658a80`. Keep manager vtable +0x1c8 and GOG/Steam boundaries open."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("registered EV-0606/CL-L419/M-0159; H112 supported; checkpointed FUN_1404a28a0")
