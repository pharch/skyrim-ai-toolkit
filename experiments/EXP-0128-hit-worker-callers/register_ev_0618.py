from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
stems = ("gog-query-20261019T191026Z", "gog-query-20261019T185131Z", "gog-query-20261019T191458Z")
captures = []
for stem in stems:
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash/read-only gate failed: {stem}")
    captures.append((raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace")))
producer = captures[0][4]
dispatcher = captures[1][4]
queue = captures[2][4]
for token in ("INDIRECT_CALL_SITE=1407bbe5c CALL qword ptr [RAX + 0x1a8]", "FUN_140657c30(DAT_14319a7c0,lVar8,plVar6,uVar13);"):
    if token not in producer:
        raise SystemExit(f"producer immediate/deferred route missing: {token}")
for token in ("case 0x12:", "(**(code **)(*plVar14 + 0x1a8))", "case 0x49:"):
    if token not in dispatcher:
        raise SystemExit(f"dispatcher route missing: {token}")
for token in ("FUNCTION_LOOKUP=FUN_140657c30 @ 140657c30", "local_88[0] = 0x12;", "local_80 = param_2;", "local_78 = param_3;", "local_70 = param_4;", "FUN_14065b800(param_1,local_88)", "XREF_CALL_COUNT=7"):
    if token not in queue:
        raise SystemExit(f"tag-0x12 builder missing: {token}")
hashes = {}
for raw, err, mp, _, _ in captures:
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0618",
    "source": "GOG producer/case comparison of AddRagdollHandler slot 1, tag-0x12 builder and FUN_140659160 dispatcher",
    "artifact": f"private-local:.local/ghidra/{captures[2][0].name}", "sha256": captures[2][3]["stdout_sha256"], "captured_utc": captures[2][3]["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x657c30 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600", "matched producer and case from EV-0616 / EV-0608 captures"],
    "coverage": "FUN_140657c30 builds tag 0x12 with retained object pointers param_2/param_3 and dword param_4, then queues it; it has seven direct callers. In AddRagdollHandler slot-1 producer FUN_1407bbb90, the immediate branch calls object vtable +0x1a8 with (object, lVar8, 1, 1, uVar13, 0), while the queued branch submits tag 0x49 then tag 0x12 carrying (lVar8, plVar6, uVar13). Dispatcher case 0x12 calls vtable +0x1a8 with the payload's plVar6 receiver, lVar8 object, constants 1/1 and selector uVar13 in the corresponding positions. The decompiled final argument is an unresolved in-stack expression; exact ABI-level equality remains unverified until instruction inspection. No target implementation or armor/HitData/skill effect is identified.",
    "result": "Static decompilation strongly suggests the AddRagdollHandler producer's immediate vtable +0x1a8 route and deferred tag-0x12 case converge on the same receiver, object, flags and selector. The final argument requires disassembly confirmation. The separate tag-0x49 queued list event remains a companion route.",
    "local_hashes": hashes, "related_evidence": ["EV-0615", "EV-0616", "EV-0617", "EV-0608", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0618")
if old and old != item:
    raise SystemExit("EV-0618 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L431", "| CL-L431 | AddRagdollHandler slot-1 producer's immediate branch and deferred tag-0x12 dispatcher both call vtable slot +0x1a8 with corresponding receiver/object/1/1/selector values; decompiled final argument remains unresolved pending disassembly. | strongly supported partial parity | [EV-0615]–[EV-0618] | Virtual target, exact last argument, and gameplay/armor effect remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0171 — AddRagdollHandler queues tag 0x12 for its slot +0x1a8 operation (EV-0618)", "## M-0171 — AddRagdollHandler queues tag 0x12 for its slot +0x1a8 operation (EV-0618)\n\nThe direct branch in `FUN_1407bbb90` invokes receiver slot `+0x1a8` with object `lVar8`, constants `1,1`, selector `uVar13`, and final argument 0. The queued branch builds tag `0x12` with the corresponding receiver/object/selector fields through `FUN_140657c30`; case 0x12 invokes the same slot with matching visible arguments [EV-0615]–[EV-0618]. Exact final-argument equality remains pending disassembly; slot target and effect remain unresolved. No armor-XP edge is established.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 immediate and deferred slot +0x1a8 comparison (EV-0618)", "### Caller 50/62 immediate and deferred slot +0x1a8 comparison (EV-0618)\n\nThe AddRagdollHandler slot-1 method invokes vtable `+0x1a8` directly when the gate is clear. When set, it queues tag `0x49` and builds a tag-`0x12` object-pair/dword event with `FUN_140657c30`; dispatcher case 0x12 invokes the same receiver slot with matching visible object, constants and selector fields. The decompiled last argument is ambiguous, so inspect its machine instructions before claiming exact parity. The virtual target remains unknown [EV-0618].")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0618 links caller 50's queued tag 0x12 to the immediate virtual operation", "EV-0618 links AddRagdollHandler slot-1's immediate `+0x1a8` virtual operation to its queued tag-0x12 dispatcher route by matching receiver/object/flags/selector; the final argument still needs disassembly. This is a control-flow convergence edge only, with target/effect unresolved.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0618"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L431"]))
for hid, model, pred in (
    ("Q79-H127", "AddRagdollHandler slot-1's immediate and deferred tag-0x12 paths converge on the same vtable +0x1a8 receiver, object, flags and selector.", "The queued tag-0x12 case dispatches the same receiver slot with matching first five argument positions as the immediate producer call; inspect machine instructions for the final argument."),
    ("Q79-H128", "AddRagdollHandler's deferred tag-0x12 route differs materially from its immediate vtable +0x1a8 operation.", "The dispatcher receiver/object/flags/selector or final call argument differs from the immediate producer path."),
):
    h = {"id": hid, "model": model, "predicted_discriminant": pred, "status": "proposed", "evidence": ["EV-0618"]}
    prior = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if prior is None:
        q["hypotheses"].append(h)
    elif prior != h:
        raise SystemExit(f"hypothesis collision: {hid}")
next_action = "Inspect FUN_140659160 machine instructions around dispatcher case 0x12's indirect vtable +0x1a8 call to resolve its sixth argument and compare against the producer's immediate zero; then query FUN_14054e340 as the shared tag-0x49 list callback."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: AddRagdollHandler immediate/deferred routes visibly converge on vtable +0x1a8; inspect case-0x12 instructions to test final-argument parity.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("EV-0615 begins caller 50's tag-0x49 retained-object route.", "EV-0615–EV-0618 map caller 50 tag 0x49 to RTTI-identified AddRagdollHandler slot 1; its immediate and queued tag-0x12 routes converge on virtual +0x1a8 subject to final-argument disassembly.", 1)
old_next = "**Selected next line:** trace queued continuation `FUN_140657c30` from RTTI-identified AddRagdollHandler slot 1's tag-0x49 producer [EV-0616–EV-0617]; compare it with the immediate `+0x1a8` call, then resolve shared list callback `FUN_14054e340`."
new_next = "**Selected next line:** inspect `FUN_140659160` instructions for tag-0x12's indirect `+0x1a8` call to resolve the final argument against AddRagdollHandler's immediate branch [EV-0618]; then trace shared tag-0x49 list callback `FUN_14054e340`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0618/CL-L431/M-0171; linked tag-0x12 dispatch to AddRagdollHandler +0x1a8; checkpointed instruction parity query")
