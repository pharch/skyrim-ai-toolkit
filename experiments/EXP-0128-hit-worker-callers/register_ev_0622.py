from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
STEM = "gog-query-20261019T192423Z"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
raw, err, mp = tuple(GH / f"{STEM}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
if not meta.get("ok") or str(meta.get("requested_rva", "")).lower() != "0x54e3c0":
    raise SystemExit("query identity failed")
if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
out = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_14054e3c0 @ 14054e3c0",
    "INDIRECT_CALL_SITE=14054e3d4 CALL qword ptr [RAX + 0x28]",
    "XREF_CALL_EDGE=1407bbca7 -> 14054e3c0 caller=FUN_1407bbb90",
    "XREF_CALL_EDGE=14071462f -> 14054e3c0 caller=FUN_140713d90",
    "XREF_CALL_COUNT=2",
    "*param_1 = 1;",
    "return 1;",
):
    if token not in out:
        raise SystemExit(f"callback result missing: {token}")
hashes = {f".local/ghidra/{p.name}": sha(p) for p in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0622",
    "source": "Identity-checked GOG decompilation and caller census for FUN_14054e3c0",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x54e3c0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_14054e3c0 has no direct callees, one unresolved element virtual call at vtable +0x28, and two direct callers: AddRagdollHandler producer FUN_1407bbb90 and FUN_140713d90. For each non-null list entry it invokes that slot with no explicit arguments, sets a one-byte context flag to 1, and returns 1. The caller loop therefore performs the slot callback for each non-null entry while recording that at least one entry was present. This differs from sibling FUN_14054e340's +0x10 any-match predicate [EV-0621]. The element type, +0x28 callback effect and downstream runtime result remain unresolved; no direct HitData/protection/AV11/AV12/UseSkill sink is identified.",
    "result": "The first AddRagdollHandler list pass is a per-non-null-entry virtual +0x28 side-effect callback plus a seen-entry flag; a second pass applies an any-match predicate through +0x10. This is a generic list-handler pattern shared with FUN_140713d90, without an established hit/armor causal edge.",
    "local_hashes": hashes, "related_evidence": ["EV-0615", "EV-0616", "EV-0621", "EV-0600", "EV-0602", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0622")
if old and old != item:
    raise SystemExit("EV-0622 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L435", "| CL-L435 | GOG FUN_14054e3c0 invokes each non-null list element's virtual slot +0x28 without explicit arguments and sets a context byte to 1; its two direct callers are AddRagdollHandler producer FUN_1407bbb90 and FUN_140713d90. | supported for captured helper structure | [EV-0622] | Element type, slot effect and runtime outcome remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0175 — FUN_14054e3c0 applies a per-entry virtual +0x28 callback and seen flag (EV-0622)", "## M-0175 — FUN_14054e3c0 applies a per-entry virtual +0x28 callback and seen flag (EV-0622)\n\nFor each non-null list entry, the helper calls its vtable `+0x28` with no explicit arguments, writes the context byte to 1, and returns success. It has two direct callers, `FUN_1407bbb90` and `FUN_140713d90` [EV-0622]. In caller 50 it precedes the separate +0x10 any-match list pass [EV-0621]. The element type and callback effect remain unresolved; no HitData/armor-skill edge is established.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 first list pass and sibling callback (EV-0622)", "### Caller 50/62 first list pass and sibling callback (EV-0622)\n\n`FUN_14054e3c0` invokes element virtual slot `+0x28` for each non-null entry, sets a seen-entry byte, and returns 1. Its two callers are the AddRagdollHandler producer and `FUN_140713d90`. Caller 50 runs this pass before its distinct +0x10 any-match pass [EV-0621–EV-0622]. Element type and callback effect remain unresolved. Next trace the returned object `FUN_1402b8b60` used as receiver for unresolved `+0x1a8`.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0622 bounds caller 50's first list pass as a +0x28 callback", "EV-0622 identifies caller 50's first list pass as per-entry virtual `+0x28` side-effect callback plus a seen-entry flag; the same helper is used by `FUN_140713d90`. The helper relationship is structural and does not identify HitData/armor behavior.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0622"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L435"]))
h = {"id": "Q79-H131", "model": "Caller 50's first list pass invokes each non-null element's virtual slot +0x28 and records whether any entry exists; this is separate from its +0x10 any-match predicate pass.", "predicted_discriminant": "FUN_14054e3c0 has one indirect +0x28 call, writes the context byte to 1, returns 1, and has caller 50 plus FUN_140713d90 as its two direct callers.", "status": "supported", "evidence": ["EV-0622", "EV-0621"]}
prior = next((x for x in q["hypotheses"] if x.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H131")
next_action = "Query FUN_1402b8b60 called by AddRagdollHandler slot 1 to identify the returned object's type/vtable used as receiver for +0x1a8; compare direct result with case-0x12 target arguments and continue the tag-0x49 route."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: caller 50 performs a per-entry +0x28 callback then +0x10 any-match pass; identify FUN_1402b8b60 return object next.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0621 maps its shared list callback as an any-match predicate also reused in FUN_140699500; no HitData/armor edge follows from that reuse.", "EV-0621 maps the shared +0x10 any-match predicate used in FUN_140699500; EV-0622 maps a prior per-entry +0x28 side-effect callback also used in FUN_140713d90. These shared primitives add no HitData/armor edge.", 1)
old_next = "**Selected next line:** query sibling list predicate `FUN_14054e3c0` after identifying `FUN_14054e340`'s any-match semantics and shared use in `FUN_140699500` [EV-0621]; then trace the returned object and unresolved `+0x1a8` target."
new_next = "**Selected next line:** query `FUN_1402b8b60`, whose returned object receives caller 50's unresolved virtual `+0x1a8` call after the two bounded list passes [EV-0621–EV-0622]; establish RTTI/type before slot interpretation."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0622/CL-L435/M-0175; bounded first list pass; checkpointed FUN_1402b8b60")
