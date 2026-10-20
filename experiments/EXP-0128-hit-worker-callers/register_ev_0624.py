from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T193014Z"
raw, err, mp = tuple(GH / f"{stem}.{ext}" for ext in ("stdout.raw", "stderr.raw", "meta.json"))
meta = json.loads(mp.read_text(encoding="utf-8"))
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
expected_sha = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != expected_sha:
    raise SystemExit("GOG identity failed")
if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
    raise SystemExit("read-only/hash gate failed")
text = raw.read_text(encoding="utf-8", errors="replace")
for token in (
    "FUNCTION_LOOKUP=FUN_140179080 @ 140179080",
    "OUTGOING_DIRECT_CALL_EDGE_COUNT=4",
    "OUTGOING_DIRECT_CALL_EDGE=1401790b8 -> 140ccab80",
    "OUTGOING_DIRECT_CALL_EDGE=1401791ca -> 140ccae40",
    "XREF_CALL_COUNT=700",
    "INCOMING_CALLER_FUNCTION_COUNT=64",
    "uVar8 = param_2 >> 3 & 0x1fffffff",
    "(**(code **)(*plVar3 + 8))(plVar3)",
    "for (plVar3 = *(longlong **)(param_1 + 8);",
    "*(longlong **)(lVar2 + (ulonglong)uVar6 * 8 + 0x20) = plVar3",
):
    if token not in text:
        raise SystemExit(f"registry lookup result missing: {token}")

hashes = {f".local/ghidra/{path.name}": sha(path) for path in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0624",
    "source": "Identity-checked GOG function graph, disassembly and decompilation for FUN_140179080",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x179080 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "FUN_140179080 acquires a lock associated with param+0x18, checks the bit for numeric key param2 in a bitmap at param+0x10, consults a thread-local cache keyed by holder and numeric key, and on a miss scans the linked list at param+8 comparing each entry's virtual slot +0x8 result to param2. A matching entry is cached and returned; the lock is released before return. The helper has 700 analyzed direct call edges across 64 caller functions and calls two synchronization helpers plus memset. The optional-object accessor FUN_1401699e0 calls this helper with key 1, reads the matched entry's +0x10 object pointer and performs reference-count adjustments. This is generic registry/holder behavior; it does not identify the concrete receiver type or caller 50 slot +0x1a8 target, and no direct HitData/protection/AV11/AV12/UseSkill sink is established.",
    "result": "FUN_140179080 is a synchronized, bitmap-gated, thread-local-cached numeric-key lookup over holder entries whose virtual slot +0x8 supplies each entry's key. For caller 50's optional branch, FUN_1401699e0 requests key 1 and extracts the matched entry's +0x10 object. The helper's broad reuse is generic infrastructure and does not add an armor or hit causal edge.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0617", "EV-0619", "EV-0620"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0624")
if old and old != item:
    raise SystemExit("EV-0624 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    file = ROOT / path
    current = file.read_text(encoding="utf-8")
    if marker not in current:
        file.write_text(current.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L437", "| CL-L437 | GOG FUN_140179080 performs a bitmap-gated, thread-local-cached numeric-key lookup over holder entries, comparing the requested key against each entry's virtual slot +0x8 result; FUN_1401699e0 requests key 1 and extracts the matched entry's +0x10 object. | supported for captured GOG implementation | [EV-0623], [EV-0624] | Concrete object type and caller-50 slot +0x1a8 target remain unknown; no HitData/armor causal edge is established. |")
append_once("research/MECHANISMS.md", "## M-0177 — FUN_140179080 resolves a bitmap-gated numeric key through a cached holder list (EV-0624)", "## M-0177 — FUN_140179080 resolves a bitmap-gated numeric key through a cached holder list (EV-0624)\n\nThe helper locks the holder, checks a bitmap bit for the requested numeric key, then consults a thread-local cache keyed by holder and key. On a miss it scans the holder's linked entries, compares the key against each entry's virtual slot `+0x8` result, caches a match, releases the lock, and returns the entry [EV-0624]. `FUN_1401699e0` requests key `1` and extracts the matched entry's object at `+0x10` [EV-0623], [EV-0624]. This identifies generic keyed-holder infrastructure only; concrete type, slot `+0x1a8` target, and gameplay effect remain unknown. Claim CL-L437.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 optional-object holder lookup (EV-0624)", "### Caller 50/62 optional-object holder lookup (EV-0624)\n\n`FUN_140179080(holder,key)` uses a bitmap gate, a thread-local holder/key cache, and a linked-list scan comparing each entry's virtual `+0x8` result with the requested key. A match returns the entry; `FUN_1401699e0` requests key 1 and extracts its `+0x10` object with reference-count handling [EV-0623–EV-0624]. This is shared keyed-holder infrastructure; it does not identify caller 50's concrete receiver or virtual `+0x1a8` target. Inspect the global fallback `DAT_1420f9d28` next.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0624 maps FUN_140179080 as a generic numeric-key holder lookup", "EV-0624 maps `FUN_140179080` as a bitmap-gated, thread-local-cached numeric-key lookup over holder entries. Caller 50's optional branch requests key 1 and obtains the entry's `+0x10` object through `FUN_1401699e0` [EV-0623–EV-0624]. Concrete type and `+0x1a8` target remain unresolved; no HitData/armor edge is added.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0624"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L437"]))
h = {
    "id": "Q79-H133",
    "model": "Caller 50's optional receiver branch retrieves numeric key 1 from a bitmap-gated synchronized holder; each holder entry supplies its key through virtual slot +0x8 and its object through +0x10.",
    "predicted_discriminant": "FUN_140179080 checks the requested key's bitmap bit, checks a holder/key thread-local cache, and on miss scans linked entries comparing virtual +0x8 results; FUN_1401699e0 requests key 1 and extracts entry +0x10.",
    "status": "supported", "evidence": ["EV-0623", "EV-0624"]
}
prior = next((row for row in q["hypotheses"] if row.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H133")
next_action = "Inspect global fallback DAT_1420f9d28 by querying its stored pointer and nearby vtable/RTTI; compare with the optional key-1 holder object before interpreting caller 50 slot +0x1a8."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: optional branch is generic key-1 holder lookup; inspect caller 50 global fallback identity.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_top = "EV-0623 maps caller 50's +0x1a8 receiver to an optional-object/global fallback. These routes add no HitData/armor edge."
new_top = "EV-0623 maps caller 50's +0x1a8 receiver to an optional-object/global fallback; EV-0624 maps the optional branch to a generic key-1 holder lookup. These routes add no HitData/armor edge."
if old_top in state:
    state = state.replace(old_top, new_top, 1)
old_next = "**Selected next line:** trace optional-object accessor `FUN_1401699e0` and global fallback `DAT_1420f9d28` returned through `FUN_1402b8b60` [EV-0623]; identify the selected receiver's type before interpreting virtual `+0x1a8`."
new_next = "**Selected next line:** inspect global fallback `DAT_1420f9d28` selected through `FUN_1402b8b60` [EV-0623–EV-0624]; identify its stored pointer/vtable before interpreting virtual `+0x1a8`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0624/CL-L437/M-0177; generic key-1 holder semantics bounded; checkpointed global fallback identity")
