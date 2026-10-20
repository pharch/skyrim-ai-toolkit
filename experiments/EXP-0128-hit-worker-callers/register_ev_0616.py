from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T191026Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x7bbb90":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_1407bbb90 @ 1407bbb90",
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=11",
    "INDIRECT_CALL_SITE_COUNT=7",
    "XREF_CALL_COUNT=0",
    "OUTGOING_DIRECT_CALL_EDGE=1407bbd41 -> 140657c30",
    "INDIRECT_CALL_SITE=1407bbe5c CALL qword ptr [RAX + 0x1a8]",
    "XREF_ANY=1418bb248 -> 1407bbb90 type=DATA source=<none> data=<none>",
    "1418bb240:0x407C0E80,1418bb244:0x00000001,1418bb248:0x407BBB90,1418bb24c:0x00000001,1418bb250:0x41B3AD70,1418bb254:0x00000001,1418bb258:0x407C1A80",
    "FUN_140658b10(DAT_14319a7c0,param_2);",
    "FUN_140657c30(DAT_14319a7c0,lVar8,plVar6,uVar13);",
):
    if token not in out:
        raise SystemExit(f"required producer result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0616",
    "source": "Identity-checked GOG direct-call census, disassembly, decompilation and source-less data-xref words for FUN_1407bbb90",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x7bbb90 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_1407bbb90 has 11 direct edges, 7 unresolved indirect sites and no analyzed direct incoming code-call edges. It reads object/process-like fields, invokes virtual slots +0x40, +0x380, +0x10 and +0x1a8, iterates an object list through FUN_14054e3c0 and FUN_14054e340, and calls FUN_140657c30 after queueing tag 0x49. None of the direct edges is a mapped HitData/protection/AV11/AV12/UseSkill target. A source-less data xref at RVA 0x18bb248 lies in a neighborhood of qwords that decode as code pointers; the qword at RVA 0x18bb240 points to 0x1407c0e80 and the next points to this producer. This is a candidate RTTI-backed vtable location, not yet established. A separate xref matches the function's runtime-function metadata. Type identity, indirect targets, and runtime effects remain open.",
    "result": "Caller 50's producer is an object/list-conditioned update with an immediate virtual +0x1a8 branch or a queued tag-0x49/FUN_140657c30 branch. Direct calls do not resolve the hit/armor hypothesis; seven virtual sites remain open. The adjacent code-pointer data xref may identify a vtable; query RTTI at candidate base RVA 0x18bb240 before type interpretation.",
    "local_hashes": hashes, "related_evidence": ["EV-0615", "EV-0614", "EV-0608", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0616")
if old and old != item:
    raise SystemExit("EV-0616 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L429", "| CL-L429 | GOG FUN_1407bbb90 has 11 direct edges, seven unresolved virtual call sites and no analyzed direct caller; its direct call list contains no mapped HitData/protection/AV11/AV12/UseSkill target, while a data xref at RVA 0x18bb248 lies among code-pointer qwords and may be an RTTI-backed vtable. | supported for bounded direct graph; vtable identity tentative | [EV-0616] | Indirect targets, type identity, and runtime effects remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0169 — Caller 50 producer has unresolved immediate and queued object-update branches (EV-0616)", "## M-0169 — Caller 50 producer has unresolved immediate and queued object-update branches (EV-0616)\n\n`FUN_1407bbb90` directly traverses an object list through `FUN_14054e3c0`/`FUN_14054e340` and calls `FUN_140657c30` after queuing tag `0x49`; a branch instead invokes unresolved virtual slot `+0x1a8` [EV-0616]. It has 7 unresolved indirect sites and no analyzed direct caller. A source-less data xref lies among adjacent code-pointer qwords at candidate table RVA `0x18bb240`; RTTI identity is not yet known. No HitData/armor-skill causal edge is established. Claim CL-L429.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 producer graph and candidate vtable discriminator (EV-0616)", "### Caller 50/62 producer graph and candidate vtable discriminator (EV-0616)\n\n`FUN_1407bbb90` has 11 direct edges, 7 unresolved indirect sites, and no analyzed direct code caller. Its direct calls do not include mapped HitData/protection/AV11/AV12/UseSkill targets. An xref at RVA `0x18bb248` sits among consecutive qwords that decode as code addresses, with the producer at the second qword; treat RVA `0x18bb240` as a candidate vtable base only. Query its MSVC RTTI identity before assigning a class or reading virtual slots. The immediate `+0x1a8` call, list callbacks and `FUN_140657c30` continuation remain unresolved [EV-0616].")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0616 bounds caller 50's direct graph and identifies a candidate vtable", "EV-0616 bounds the caller-50 producer to an object/list-conditioned immediate-or-queued update with 7 unresolved virtual calls and no direct mapped hit/armor-skill sink. Its source-less xref at RVA `0x18bb248` lies among code-pointer qwords, suggesting candidate vtable base `0x18bb240`; RTTI identity is pending. No causal edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0616"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L429"]))
h = {"id": "Q79-H125", "model": "Caller 50's source-less data xref at RVA 0x18bb248 is a method slot in an RTTI-backed vtable whose base is likely RVA 0x18bb240.", "predicted_discriminant": "The code-pointer qwords around the reference and the candidate base's preceding Complete Object Locator resolve to a named type through the GOG RTTI query.", "status": "proposed", "evidence": ["EV-0616"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H125")
next_action = "Query GOG RTTI at candidate vtable base RVA 0x18bb240 for FUN_1407bbb90's adjacent code-pointer table; if the Complete Object Locator/type descriptor validates, map this producer's slot and then resolve FUN_140657c30 and callback helpers."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 producer direct graph has seven unresolved virtual sites; test candidate RTTI-backed vtable at RVA 0x18bb240 before type inference.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_next = "**Selected next line:** trace caller 50's sole producer `FUN_1407bbb90`, its direct callees and incoming callers; resolve list callbacks `FUN_14054e3c0`/`FUN_14054e340`, manager continuation `FUN_140657c30`, and immediate/deferred parity before classifying its tag-0x49 path [EV-0615]."
new_next = "**Selected next line:** test candidate RTTI-backed vtable base RVA `0x18bb240` found in caller 50 producer's adjacent code-pointer xref [EV-0616]; resolve its type before mapping `FUN_1407bbb90` virtual slots, then trace `FUN_140657c30` and list callbacks."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0616/CL-L429/M-0169; producer direct graph bounded; checkpointed candidate RTTI query")
