from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
stem = "gog-query-20261019T193444Z"
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
    "FUNCTION_LOOKUP=FUN_1402c65b0 @ 1402c65b0",
    "XREF_CALL_COUNT=1",
    "XREF_CALL_EDGE=1402217a7 -> 1402c65b0 caller=FUN_140221790",
    "FUN_1402c6810(&local_30,0)",
    "DAT_1420f9d28 = plVar5;",
    "*plVar5 = lVar4;",
    "local_30 = DAT_1432740d8;",
    "local_2c = DAT_1432740dc;",
    "local_28 = DAT_1432740e0;",
    "if (param_2 != '\\0')",
):
    if token not in text:
        raise SystemExit(f"global setter provenance missing: {token}")

hashes = {f".local/ghidra/{path.name}": sha(path) for path in (raw, err, mp)}
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {expected_sha}; existing-project read-only capture, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0626",
    "source": "Identity-checked GOG setter FUN_1402c65b0 and sole analyzed direct caller FUN_140221790",
    "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": meta["stdout_sha256"], "captured_utc": meta["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x2c65b0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600"],
    "coverage": "The sole analyzed direct caller FUN_140221790 invokes FUN_1402c65b0 when its second argument is nonzero. The setter obtains an 8-byte wrapper/holder via FUN_140cc5b80, builds a local three-dword value from DAT_1432740d8, DAT_1432740dc and DAT_1432740e0, calls FUN_1402c6810(&local_30,0), stores the holder address in DAT_1420f9d28 and stores the returned pointer at *holder, incrementing its reference count when nonnull. The pointer resolver FUN_1402b8b60 returns *DAT_1420f9d28 on its fallback branch [EV-0623]. The helper's return type, RTTI, vtable and gameplay purpose remain unresolved; no HitData/protection/AV11/AV12/UseSkill edge is established.",
    "result": "Caller 50's global fallback cell is backed by an allocated/located holder whose first qword is populated with FUN_1402c6810's result from a three-dword global input. FUN_1402c65b0 is called by FUN_140221790 only when the caller's second argument is nonzero. This bounds pointer construction/provenance but does not identify the returned object's type or virtual +0x1a8 behavior.",
    "local_hashes": hashes, "related_evidence": ["EV-0623", "EV-0625", "EV-0624"]
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0626")
if old and old != item:
    raise SystemExit("EV-0626 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    file = ROOT / path
    current = file.read_text(encoding="utf-8")
    if marker not in current:
        file.write_text(current.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L439", "| CL-L439 | FUN_1402c65b0 stores a holder in DAT_1420f9d28 and places FUN_1402c6810(&three adjacent global dwords,0)'s result in the holder's first qword; its sole analyzed direct caller FUN_140221790 invokes the setter when its second argument is nonzero. | supported for captured GOG construction and direct-caller graph | [EV-0623], [EV-0626] | Factory result type, caller condition meaning and caller-50 virtual +0x1a8 behavior remain unknown. |")
append_once("research/MECHANISMS.md", "## M-0179 — FUN_1402c65b0 populates caller 50's global fallback holder (EV-0626)", "## M-0179 — FUN_1402c65b0 populates caller 50's global fallback holder (EV-0626)\n\n`FUN_1402c65b0` obtains an 8-byte holder, calls `FUN_1402c6810` with a local three-dword value copied from `DAT_1432740d8..0xe0`, stores the holder in `DAT_1420f9d28` and stores the returned pointer at `*holder`, retaining it when nonnull [EV-0626]. The sole analyzed direct caller `FUN_140221790` invokes the setter only when its second argument is nonzero. `FUN_1402b8b60` later returns `*DAT_1420f9d28` on the fallback branch [EV-0623]. The factory result's type and gameplay meaning remain unresolved. Claim CL-L439.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 global fallback setter provenance (EV-0626)", "### Caller 50/62 global fallback setter provenance (EV-0626)\n\n`FUN_1402c65b0` obtains an 8-byte holder, constructs a local three-dword input from `DAT_1432740d8`, `+4` and `+8`, passes it to `FUN_1402c6810`, stores the holder in global `DAT_1420f9d28`, then places the helper result in `*holder` and retains it when nonnull. Its sole analyzed direct caller `FUN_140221790` calls the setter when its second argument is nonzero [EV-0626]. Trace `FUN_1402c6810` and the zeroing path to identify the fallback object; the global resolver returns the holder's first qword [EV-0623].")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0626 maps caller 50's fallback holder construction", "EV-0626 connects the global fallback setter to `FUN_1402c6810`: it uses a three-dword global input, stores the result inside the holder placed in `DAT_1420f9d28`, and its sole analyzed direct caller has a nonzero-argument gate. This narrows construction provenance, but type and `+0x1a8` target remain unresolved [EV-0623], [EV-0625–EV-0626].")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0626"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L439"]))
h = {
    "id": "Q79-H135",
    "model": "Caller 50's global fallback object comes from FUN_1402c6810 applied to a local three-dword value copied from adjacent globals, then stored in the holder at DAT_1420f9d28 by FUN_1402c65b0.",
    "predicted_discriminant": "A direct query of FUN_1402c6810 should identify allocation, vtable/RTTI or returned-object operations; the caller 50 global path returns the holder's first qword.",
    "status": "supported", "evidence": ["EV-0623", "EV-0626"]
}
prior = next((row for row in q["hypotheses"] if row.get("id") == h["id"]), None)
if prior is None:
    q["hypotheses"].append(h)
elif prior != h:
    raise SystemExit("hypothesis collision: Q79-H135")
next_action = "Trace FUN_1402c6810, the helper that supplies the fallback object's first qword from a three-dword input; identify its return type and vtable before interpreting caller 50 slot +0x1a8. Then map FUN_1402c6720's clear path."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: global fallback holder is populated from FUN_1402c6810; trace returned object's type.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old_top = "EV-0625 shows the global fallback cell is zero in the static image, with an RDI setter and zeroing path. These routes add no HitData/armor edge."
new_top = "EV-0625 shows the global fallback cell is zero in the static image, with an RDI setter and zeroing path; EV-0626 traces the setter to a holder populated by FUN_1402c6810 from three adjacent global dwords. These routes add no HitData/armor edge."
if old_top in state:
    state = state.replace(old_top, new_top, 1)
old_next = "**Selected next line:** trace `FUN_1402c65b0` and `FUN_1402c6720` writing global fallback `DAT_1420f9d28` [EV-0625]; resolve the assigned receiver's provenance and type before interpreting virtual `+0x1a8`."
new_next = "**Selected next line:** trace `FUN_1402c6810`, which supplies the object stored in the global fallback holder [EV-0626], to identify its returned type before interpreting virtual `+0x1a8`; then map the clear path."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0626/CL-L439/M-0179; global fallback construction narrowed to FUN_1402c6810; checkpointed returned-type trace")
