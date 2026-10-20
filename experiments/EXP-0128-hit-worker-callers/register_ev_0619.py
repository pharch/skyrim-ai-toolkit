from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
stems = ("gog-query-20261019T191026Z", "gog-query-20261019T191713Z", "gog-query-20261019T191458Z")
captures = []
for stem in stems:
    raw, err, mp = tuple(GH / f"{stem}.{x}" for x in ("stdout.raw", "stderr.raw", "meta.json"))
    meta = json.loads(mp.read_text(encoding="utf-8"))
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not meta.get("ok") or meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG identity failed: {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled") or sha(raw) != meta.get("stdout_sha256") or sha(err) != meta.get("stderr_sha256"):
        raise SystemExit(f"read-only/hash gate failed: {stem}")
    captures.append((raw, err, mp, meta, raw.read_text(encoding="utf-8", errors="replace")))
producer, dispatcher, queue = captures[0][4], captures[1][4], captures[2][4]
for token in (
    "DISASM=1407bbe45 MOV byte ptr [RSP + 0x28], 0x0",
    "DISASM=1407bbe4a MOV dword ptr [RSP + 0x20], R15D",
    "DISASM=1407bbe4f MOV R9B, 0x1",
    "DISASM=1407bbe52 MOVZX R8D, R9B",
    "DISASM=1407bbe56 MOV RDX, R13",
    "DISASM=1407bbe59 MOV RCX, R14",
    "DISASM=1407bbe5c CALL qword ptr [RAX + 0x1a8]",
):
    if token not in producer:
        raise SystemExit(f"immediate argument setup missing: {token}")
for token in (
    "DISASM=140659386 MOV RBX, qword ptr [RDI + 0x8]",
    "DISASM=14065938a MOV R15, qword ptr [RDI + 0x10]",
    "DISASM=140659391 MOVZX R8D, byte ptr [RDI + 0x18]",
    "DISASM=140659396 MOV RDX, RBX",
    "DISASM=140659399 MOV RCX, R15",
    "DISASM=14065939c CALL qword ptr [RAX + 0x1a8]",
    "XREF_CALL_EDGE=14065b915 -> 140659160 caller=FUN_14065b800",
):
    if token not in dispatcher:
        raise SystemExit(f"deferred argument setup missing: {token}")
if "local_70 = param_4;" not in queue or "local_88[0] = 0x12;" not in queue:
    raise SystemExit("tag-0x12 payload layout missing")
hashes = {}
for raw, err, mp, _, _ in captures:
    for p in (raw, err, mp):
        hashes[f".local/ghidra/{p.name}"] = hashlib.sha256(p.read_bytes()).hexdigest()
item = {
    "kind": "native", "edition": "AE",
    "runtime": f"GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 {EXPECTED_SHA}; existing-project read-only captures, auto-analysis disabled, no import or overwrite.",
    "modified_state": False, "lane": "mechanism_inference", "id": "EV-0619",
    "source": "GOG machine-instruction comparison of AddRagdollHandler immediate slot call and tag-0x12 dispatcher case",
    "artifact": f"private-local:.local/ghidra/{captures[1][0].name}", "sha256": captures[1][3]["stdout_sha256"], "captured_utc": captures[1][3]["captured_utc"],
    "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py --rva 0x659160 --list-call-edges --timeout 600", "paired with EV-0616 and EV-0618 captures"],
    "coverage": "The immediate AddRagdollHandler slot-1 call at 0x1407bbe5c explicitly sets RCX=receiver, RDX=object, R8D=1, R9B=1, stack dword [RSP+0x20]=selector and stack byte [RSP+0x28]=0 before virtual slot +0x1a8. The tag-0x12 dispatcher case at 0x14065939c sets RCX=payload second pointer, RDX=payload first pointer and R8D=byte[payload+0x18], then calls the same slot; this call block does not set matching R9 or stack arguments. Its visible third argument is an event selector byte rather than the immediate constant 1, so exact argument parity is falsified. The dispatcher has one direct caller, FUN_14065b800; its outgoing callsite context must be checked to bound inherited register/stack state. Same slot and pointer roles do not by themselves establish equivalent behavior.",
    "result": "The initial decompiler-based parity model is corrected: immediate and deferred paths share receiver/object roles and slot +0x1a8, but their visible argument setup differs. The deferred case forwards a selector byte in R8 where the immediate call passes 1, and does not locally set matching R9/stack values. Worker-wrapper context and callee signature remain unresolved; no global negative or armor conclusion follows.",
    "local_hashes": hashes, "related_evidence": ["EV-0618", "EV-0617", "EV-0616", "EV-0608", "EV-0397"],
}
ep = ROOT / "research/EVIDENCE.json"
ed = json.loads(ep.read_text(encoding="utf-8"))
old = {row["id"]: row for row in ed["items"]}.get("EV-0619")
if old and old != item:
    raise SystemExit("EV-0619 collision")
if not old:
    ed["items"].append(item)
ep.write_text(json.dumps(ed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    s = p.read_text(encoding="utf-8")
    if marker not in s:
        p.write_text(s.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")

append_once("research/CLAIMS.md", "CL-L432", "| CL-L432 | In GOG, AddRagdollHandler slot-1 immediate and tag-0x12 deferred calls share vtable +0x1a8 and receiver/object roles, but the immediate call sets R8D=1, R9B=1 and two stack arguments, whereas the dispatcher loads R8D from the event selector byte and does not set matching R9/stack values in its block. | supported disassembly result; exact callee contract remains open | [EV-0619] | Worker-wrapper inherited register/stack context remains unexamined; no semantic or runtime equivalence is inferred. |")
append_once("research/MECHANISMS.md", "## M-0172 — Immediate and tag-0x12 calls share slot +0x1a8 but not visible arguments (EV-0619)", "## M-0172 — Immediate and tag-0x12 calls share slot +0x1a8 but not visible arguments (EV-0619)\n\nMachine code corrects provisional parity in M-0171: both call slot `+0x1a8` with the same receiver/object roles, but the direct AddRagdollHandler path sets `R8D=1`, `R9B=1`, selector on the stack and a zero stack byte; case 0x12 loads `R8D` from the payload selector byte and does not set matching R9/stack values locally [EV-0619]. The event-dispatch wrapper's inherited context and callee signature remain open. This is not exact argument parity and does not establish different terminal behavior. Claim CL-L432.")
append_once("experiments/EXP-0128-hit-worker-callers/results.md", "### Caller 50/62 disassembly corrects immediate/deferred argument parity (EV-0619)", "### Caller 50/62 disassembly corrects immediate/deferred argument parity (EV-0619)\n\nThe immediate AddRagdollHandler call sets `R8D=1`, `R9B=1`, selector in stack dword `[RSP+0x20]`, and zero in stack byte `[RSP+0x28]`. Case 0x12 instead loads `R8D` from the event selector byte at payload+0x18 and does not set matching R9/stack arguments in its block. Both use the same receiver/object pointer roles and vtable slot `+0x1a8`, but exact argument parity is falsified. `FUN_14065b800` is the sole direct caller of the dispatcher; inspect its callsite to bound inherited context before interpreting the mismatch [EV-0619].")
append_once("research/KNOWLEDGE_GRAPH.md", "EV-0619 corrects the proposed AddRagdollHandler argument-parity edge", "EV-0619 refines EV-0618: immediate and tag-0x12 paths use the same slot and pointer roles but have different visible argument setup. Exact call parity is falsified; inherited worker context and target semantics remain unknown.")

fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), "EV-0619"]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L432"]))
for hid, model, status in (
    ("Q79-H127", "AddRagdollHandler slot-1's tag-0x12 deferred path exactly reproduces the immediate slot +0x1a8 argument values.", "falsified"),
    ("Q79-H128", "The deferred tag-0x12 case shares slot +0x1a8 and pointer roles but forwards a selector byte in R8 and lacks locally matching R9/stack setup; worker context remains unresolved.", "supported"),
):
    prior = next((x for x in q["hypotheses"] if x.get("id") == hid), None)
    if prior is None:
        model_record = {"id": hid, "model": model, "predicted_discriminant": "Machine instructions at both callsites identify receiver, object, register and stack arguments; worker callsite resolves any inherited values.", "status": status, "evidence": ["EV-0619"]}
        q["hypotheses"].append(model_record)
    else:
        prior["model"] = model
        prior["status"] = status
        prior["evidence"] = list(dict.fromkeys([*prior.get("evidence", []), "EV-0619"]))
assessment = "EV-0619 falsifies exact visible argument parity for the immediate and tag-0x12 slot +0x1a8 calls; worker-wrapper context and callee signature remain unknown."
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Inspect FUN_14065b800 instructions around its sole call at RVA 0x65b915 to FUN_140659160 and identify all register/stack arguments, then resolve FUN_14054e340's tag-0x49 list callback."
q["next_action"] = next_action
fr["session_next_action"] = next_action
fr["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: exact immediate/deferred +0x1a8 argument parity is falsified; inspect worker wrapper's callsite context next.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
state = state.replace("its immediate and queued tag-0x12 routes converge on virtual +0x1a8 subject to final-argument disassembly.", "its immediate and deferred tag-0x12 routes share virtual +0x1a8 and pointer roles but have different visible argument setup.", 1)
old_next = "**Selected next line:** inspect `FUN_140659160` instructions for tag-0x12's indirect `+0x1a8` call to resolve the final argument against AddRagdollHandler's immediate branch [EV-0618]; then trace shared tag-0x49 list callback `FUN_14054e340`."
new_next = "**Selected next line:** inspect `FUN_14065b800` callsite RVA `0x65b915` for register/stack context inherited by case 0x12, after disassembly falsified exact visible argument parity [EV-0619]; then trace shared tag-0x49 list callback `FUN_14054e340`."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
sp.write_text(state, encoding="utf-8")
print("registered EV-0619/CL-L432/M-0172; falsified exact visible argument parity; checkpointed worker callsite")
