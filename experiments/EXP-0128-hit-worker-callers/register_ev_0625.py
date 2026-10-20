from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T193247Z"
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
    "POINTER_TABLE_BASE_RVA=0x20F9D28",
    "POINTER_TABLE_XREF_SCAN_COMPLETE=true",
    "POINTER_TABLE_XREF_COUNT=143",
    "POINTER_TABLE_ENTRY=index:0 address:1420f9d28 value:0x0 target:00000000 function:<no-function>",
    "from:1402c66c1 type:WRITE function:FUN_1402c65b0",
    "MOV qword ptr [0x1420f9d28],RDI",
    "from:1402c67d2 type:WRITE function:FUN_1402c6720",
    "MOV qword ptr [0x1420f9d28],0x0",
):
    if token not in text:
        raise SystemExit(f"global fallback result missing: {token}")

hashes = {f".local/ghidra/{path.name}": sha(path) for path in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0625",
    "source": "Identity-checked GOG pointer-table and reference census for global DAT_1420f9d28",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --pointer-table-rva 0x20f9d28 --pointer-count 4 --timeout 600"],
    "coverage": "The four-qword scan starting at global DAT_1420f9d28 reports all four current image values as zero and 143 direct read/write references across those four addresses. For the first cell DAT_1420f9d28 specifically, the scan reports 49 references: 47 reads and two writes. FUN_1402c65b0 stores RDI to the cell at instruction RVA 0x2c66c1; FUN_1402c6720 writes zero at RVA 0x2c67d2. This establishes that the image snapshot does not identify the runtime fallback object and exposes candidate set/clear code for tracing. It does not identify the assigned object's type or caller-50 slot +0x1a8 target.",
    "result": "The static GOG image has a zero value at DAT_1420f9d28. Its exact cell has 47 direct read references, an RDI assignment in FUN_1402c65b0, and a zeroing write in FUN_1402c6720. Treat the active fallback receiver as runtime-populated and unresolved until the setter's input, control flow and type are traced; do not infer a zero receiver from the file snapshot.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0624", "EV-0617"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0625")
if old and old != item:
    raise SystemExit("EV-0625 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    file = ROOT / path
    current = file.read_text(encoding="utf-8")
    if marker not in current:
        file.write_text(current.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L438", "| CL-L438 | GOG DAT_1420f9d28 is zero in the static image and has 47 direct read references plus two writes: FUN_1402c65b0 stores RDI and FUN_1402c6720 stores zero. | supported for captured static image and reference census | [EV-0625] | The runtime assigned object, its type and caller-50 slot +0x1a8 target remain unresolved. |")
append_once("research/MECHANISMS.md", "## M-0178 — DAT_1420f9d28 is a runtime-populated global receiver cell (EV-0625)", "## M-0178 — DAT_1420f9d28 is a runtime-populated global receiver cell (EV-0625)\n\nThe static GOG image stores zero at `DAT_1420f9d28`, but analyzed code reads the cell widely. A reference census finds 47 reads and two writes to the exact cell: `FUN_1402c65b0` assigns `RDI`, while `FUN_1402c6720` stores zero [EV-0625]. Therefore the captured file value does not identify the active runtime receiver. Trace the assignment's RDI provenance and type and the clearing path before reading caller 50 slot `+0x1a8`. Claim CL-L438.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 global fallback storage (EV-0625)", "### Caller 50/62 global fallback storage (EV-0625)\n\nAt static image load, `DAT_1420f9d28` and the next three qwords are zero. The exact fallback cell has 47 direct reads and two writes in analyzed code: `FUN_1402c65b0` stores `RDI`; `FUN_1402c6720` stores zero [EV-0625]. The fallback is runtime-populated, but its assigned object class and caller-50 slot `+0x1a8` target remain unresolved. Trace both writer functions and their incoming callers to recover RDI provenance and the set/clear lifecycle.")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0625 maps the static fallback cell and its setter/clearer", "EV-0625 shows `DAT_1420f9d28` is zero in the static image, with 47 direct reads, an `RDI` assignment from `FUN_1402c65b0`, and a zeroing write from `FUN_1402c6720`. This identifies runtime-populated storage but not the receiver type or virtual `+0x1a8` target; trace assignment provenance before adding a class or gameplay edge.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0625"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L438"]))
h = {
    "id": "Q79-H134",
    "model": "Caller 50's global fallback DAT_1420f9d28 is zero in the static image but is assigned from RDI by FUN_1402c65b0 and cleared by FUN_1402c6720, so the receiver is runtime-populated.",
    "predicted_discriminant": "The cell's GOG pointer census shows zero in the image, an RDI store from FUN_1402c65b0 and a zero store from FUN_1402c6720; tracing both writer bodies and callers identifies the runtime object lifecycle and type.",
    "status": "supported", "evidence": ["EV-0625", "EV-0623"]
}
prior = next((row for row in q["hypotheses"] if row.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H134")
next_action = "Query FUN_1402c65b0 and FUN_1402c6720 with call-edge/decompilation context; establish the RDI source, callers and object type for DAT_1420f9d28 before interpreting caller 50 slot +0x1a8."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: global fallback is zero in the static image with an RDI setter and zeroing path; trace set/clear functions.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_top = "EV-0623 maps caller 50's +0x1a8 receiver to an optional-object/global fallback; EV-0624 maps the optional branch to a generic key-1 holder lookup. These routes add no HitData/armor edge."
new_top = "EV-0623 maps caller 50's +0x1a8 receiver to an optional-object/global fallback; EV-0624 maps the optional branch to a generic key-1 holder lookup; EV-0625 shows the global fallback cell is zero in the static image, with an RDI setter and zeroing path. These routes add no HitData/armor edge."
if old_top in state:
    state = state.replace(old_top, new_top, 1)
old_next = "**Selected next line:** inspect global fallback `DAT_1420f9d28` selected through `FUN_1402b8b60` [EV-0623–EV-0624]; identify its stored pointer/vtable before interpreting virtual `+0x1a8`."
new_next = "**Selected next line:** trace `FUN_1402c65b0` and `FUN_1402c6720` writing global fallback `DAT_1420f9d28` [EV-0625]; resolve the assigned receiver's provenance and type before interpreting virtual `+0x1a8`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0625/CL-L438/M-0178; global cell distinguished from static image zero; checkpointed set/clear tracing")
