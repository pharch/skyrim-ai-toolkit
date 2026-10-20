from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T190325Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x54e390":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
    raise SystemExit("read-only gate failed")
if sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("capture hash failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_14054e390 @ 14054e390",
    "INDIRECT_CALL_SITE=14054e3a7 CALL qword ptr [RAX + 0x20]",
    "XREF_CALL_EDGE=14065ad10 -> 14054e390 caller=FUN_140659160",
    "XREF_CALL_COUNT=4",
    "*(undefined1 *)(param_1 + 1) = 1;",
    "return 1;",
):
    if token not in out:
        raise SystemExit(f"required result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0613",
    "source": "Identity-checked GOG decompilation and direct caller census for FUN_14054e390",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x54e390 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_14054e390 has no direct callees, one unresolved indirect call through the first argument object's vtable slot +0x20, and four analyzed direct callers. Its body loads the object pointer from the second argument, invokes that slot with the first argument pointer, writes byte 1 at first-argument offset +8, and returns 1. One direct caller is FUN_140659160 at the tag-0x48 list-iteration site; three others also use it in list traversals. Exact interface and callback semantics are unresolved. No direct HitData/protection/AV11/AV12/UseSkill function edge is identified.",
    "result": "The tag-0x48 list helper is a generic virtual callback/visitor primitive at the observed level: per list entry it dispatches object vtable slot +0x20, sets a result flag and reports success. This narrows caller 49 away from a direct armor-skill mechanism but does not identify the callback implementation or prove a global negative.",
    "local_hashes": hashes, "related_evidence": ["EV-0612", "EV-0608", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0613")
if old and old != item:
    raise SystemExit("EV-0613 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L426", "| CL-L426 | In GOG AE 1.6.1179.0, FUN_14054e390 loads each non-null list entry's vtable slot +0x20, invokes it with the caller's first argument, sets that argument's byte at +8, and returns 1; it has four direct callers including FUN_140659160's tag-0x48 case. | supported for captured function structure | [EV-0613] | Callback interface and implementation remain unresolved; no direct armor-skill sink follows from this generic helper. |")
append_once("research/MECHANISMS.md", "## M-0166 — FUN_14054e390 is a generic virtual list callback primitive (EV-0613)", "## M-0166 — FUN_14054e390 is a generic virtual list callback primitive (EV-0613)\n\nThe helper loads a non-null entry object, calls its vtable slot `+0x20` with the supplied context, sets context byte `+8`, and returns 1. Four direct callers include the tag-0x48 case in `FUN_140659160`; the concrete interface and callback effects remain unknown. This is a structural operation, not evidence of armor-skill behavior. Claim CL-L426.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Tag-0x48 list helper FUN_14054e390 (EV-0613)", "### Tag-0x48 list helper FUN_14054e390 (EV-0613)\n\nThe helper invokes each non-null entry object's virtual slot `+0x20` with a context pointer, sets context byte `+8`, and returns 1. It has four callers, including `FUN_140659160`'s tag-0x48 list loop. The exact callback contract is unresolved; no direct mapped armor-skill sink appears. Inspect caller 49's data xref RVA `0x3657848` next [EV-0613].")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0613 identifies FUN_14054e390 as a generic virtual list callback", "EV-0613 identifies `FUN_14054e390` as a generic list-entry virtual callback primitive shared by four callers, including dispatcher case 0x48. This is structural evidence only; no armor-skill or quest-gate causal edge is established.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0613"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L426"]))
hid = "Q79-H120"
h = {"id": hid, "model": "Caller 49's tag-0x48 list route reaches a generic virtual callback primitive, not a directly mapped armor-skill sink.", "predicted_discriminant": "FUN_14054e390's four direct callers and body show list-entry vtable slot +0x20 dispatch, a context completion byte, and no direct HitData/protection/AV11/AV12/UseSkill call.", "status": "supported", "evidence": ["EV-0613"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H120")
assessment = "EV-0613 shows FUN_14054e390 is a generic entry vtable callback with four direct callers, including tag 0x48; callback implementation remains unresolved and no direct armor-skill sink is established."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Inspect source-less data xref RVA 0x3657848 from caller 49's FUN_140658ac0 and classify its surrounding bytes/references before closing caller 49; then continue caller 50 of 62."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 49's tag-0x48 list helper is a generic virtual callback; classify its sole source-less data xref next.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0612 begins caller 49's tag-0x48 list route.", "EV-0612–EV-0613 bound caller 49's tag-0x48 list route to a generic vtable callback; its data xref remains unresolved.", 1)
state = state.replace("**Selected next line:** trace tag-0x48 list helper `FUN_14054e390` and then classify caller 49's sole data xref RVA `0x3657848` [EV-0612]; continue to caller 50 after the bounded list-path result.", "**Selected next line:** classify caller 49's sole source-less data xref RVA `0x3657848` after tracing its generic tag-0x48 list helper [EV-0612–EV-0613]; then continue caller 50/62.", 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0613/CL-L426/M-0166; bounded tag-0x48 helper; checkpointed xref RVA 0x3657848")
