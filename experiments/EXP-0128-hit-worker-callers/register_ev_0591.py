from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
QUERY_SPECS = [
    ("gog-query-20261019T175439Z", "0x40e300", None),
    ("gog-query-20261019T180053Z", "0x357c70", None),
    ("gog-query-20261019T180245Z", None, "0x362ffb4"),
]
EXPECTED_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
metas = {}
local_hashes = {}
for stem, rva, address_rva in QUERY_SPECS:
    raw = GH / f"{stem}.stdout.raw"
    stderr = GH / f"{stem}.stderr.raw"
    meta_path = GH / f"{stem}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if not meta.get("ok"):
        raise SystemExit(f"query failed for {stem}")
    if rva is not None and str(meta.get("requested_rva", "")).lower() != rva:
        raise SystemExit(f"RVA identity failed for {stem}")
    if address_rva is not None and str(meta.get("requested_address_rva", "")).lower() != address_rva:
        raise SystemExit(f"address identity failed for {stem}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != EXPECTED_SHA:
        raise SystemExit(f"GOG binary identity failed for {stem}")
    if not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
        raise SystemExit(f"read-only gate failed for {stem}")
    if sha(raw) != meta.get("stdout_sha256") or sha(stderr) != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash failed for {stem}")
    metas[stem] = meta
    for artifact in (raw, stderr, meta_path):
        local_hashes[f".local/ghidra/{artifact.name}"] = sha(artifact)

item = {
    "kind": "native_and_primary_documentation_inference",
    "edition": "AE",
    "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only queries, auto-analysis disabled, no import or overwrite.",
    "modified_state": False,
    "lane": "mechanism_inference",
    "id": "EV-0591",
    "source": "GOG xref word-context comparison against Microsoft Learn x64 RUNTIME_FUNCTION layout (accessed 2026-10-19)",
    "artifact": "private-local:.local/ghidra/gog-query-20261019T180053Z.stdout.raw",
    "sha256": metas["gog-query-20261019T180053Z"]["stdout_sha256"],
    "captured_utc": metas["gog-query-20261019T180053Z"]["captured_utc"],
    "tools": [
        "strict Python 3.12 dispatcher",
        "tools/ghidra_probe.py --rva 0x357c70 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
        "tools/ghidra_probe.py --rva 0x40e300 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600",
        "tools/ghidra_probe.py --address-rva 0x362ffb4 --timeout 600",
        "Microsoft Learn, x64 exception handling, RUNTIME_FUNCTION layout: https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170",
    ],
    "coverage": "GOG XREF_ANY context at the sole data reference to FUN_140357c70 reports adjacent DWORD values 0x357c70, 0x357ce7, and 0x1c70fcc. These align with that function's GOG start RVA, end RVA, and an unwind-data RVA. A separate GOG XREF_ANY context for known handler FUN_14040e300 reports the corresponding triple 0x40e300, 0x40e3a5, 0x1c91ba8. Microsoft Learn specifies that x64 RUNTIME_FUNCTION entries are three image-relative ULONG values (function start, function end, unwind-info address) stored in sorted .pdata [primary URL above]. The address-context query finds no function, no code xrefs, and no instructions at the queried data location. This supports an inference that the producer's one data xref is exception/unwind metadata rather than an application descriptor; the exact containing PE section was not separately enumerated.",
    "result": "The apparent data-reference lead for a decoder descriptor is narrowed away: the exact three-DWORD neighborhoods for FUN_140357c70 and FUN_14040e300 match the documented x64 RUNTIME_FUNCTION layout. Therefore the sole XREF_ANY data reference at RVA 0x362ffb4 is likely compiler exception metadata, not gameplay registration. This does not reveal the wrapper's selected decoder descriptor or input provenance, and does not make any gameplay/HitData/armor conclusion. Q79-H85 is supported and H86 is falsified for this specific xref only; no OBJ-1/OBJ-2 causal edge is added.",
    "local_hashes": local_hashes,
    "related_evidence": ["EV-0588", "EV-0589", "EV-0590", "EV-0260"],
}

evidence_path = ROOT / "research/EVIDENCE.json"
evidence_doc = json.loads(evidence_path.read_text(encoding="utf-8"))
existing = {row["id"]: row for row in evidence_doc["items"]}
if "EV-0591" in existing and existing["EV-0591"] != item:
    raise SystemExit("EV-0591 collision")
if "EV-0591" not in existing:
    evidence_doc["items"].append(item)
evidence_path.write_text(json.dumps(evidence_doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def append_once(path: str, marker: str, value: str) -> None:
    p = ROOT / path
    contents = p.read_text(encoding="utf-8")
    if marker not in contents:
        p.write_text(contents.rstrip() + "\n\n" + value.rstrip() + "\n", encoding="utf-8")


append_once(
    "research/CLAIMS.md",
    "CL-L403",
    "| CL-L403 | GOG xref word neighborhoods for FUN_140357c70 and FUN_14040e300 each match the documented x64 RUNTIME_FUNCTION sequence (begin RVA, end RVA, unwind-info RVA), so FUN_140357c70's sole data xref is likely exception/unwind metadata rather than an application descriptor. | strongly supported inference for the matching records | [EV-0591]; Microsoft Learn, `x64 exception handling`, https://learn.microsoft.com/en-us/cpp/build/exception-handling-x64?view=msvc-170 (accessed 2026-10-19) | The exact containing PE section was not separately enumerated; no wrapper descriptor or gameplay semantics are inferred. |",
)

mechanism_path = ROOT / "research/MECHANISMS.md"
mechanisms = mechanism_path.read_text(encoding="utf-8")
old = "## M-0145 — Tag-0x40 producer has unresolved data-table registration (EV-0590)\n\n`FUN_140357c70` directly calls only the shared decoder and tag-0x40 builder, has no analyzed direct callers, and has one data xref at RVA `0x362ffb4` [EV-0590]. The nearby words are not enough to classify the containing object or selected decode descriptor. Treat this as a table-reference lead, not proof of a native command, event source, Actor type, or gameplay role. No OBJ-1/OBJ-2 causal edge is established. Claim CL-L402."
new = "## M-0145 — Tag-0x40 producer xref matches x64 unwind metadata (EV-0590/0591)\n\n`FUN_140357c70` directly calls only the shared decoder and tag-0x40 builder, has no analyzed direct callers, and has one data xref at RVA `0x362ffb4` [EV-0590]. EV-0591 shows that the neighboring words `0x357c70`, `0x357ce7`, and `0x1c70fcc` align with the documented x64 `RUNTIME_FUNCTION` start/end/unwind-info fields; the same pattern appears around known handler `FUN_14040e300` [EV-0588], [EV-0591]. The xref is therefore likely exception/unwind metadata, not application registration. The exact containing section, selected decode descriptor and gameplay input provenance remain unknown. No OBJ-1/OBJ-2 causal edge is established. Claims CL-L402/CL-L403."
if old not in mechanisms:
    raise SystemExit("M-0145 source text not found")
mechanism_path.write_text(mechanisms.replace(old, new, 1), encoding="utf-8")

append_once(
    "experiments/EXP-0128-hit-worker-callers/results.md",
    "### Caller 45/62 xref metadata comparison (EV-0591)",
    """### Caller 45/62 xref metadata comparison (EV-0591)

The apparent producer data-table reference is reclassified as likely Windows x64 exception metadata. Its adjacent values are `0x357c70`, `0x357ce7`, and `0x1c70fcc`; the same three-field pattern appears for known handler `FUN_14040e300` as `0x40e300`, `0x40e3a5`, and `0x1c91ba8` [EV-0588], [EV-0591]. Microsoft documents `RUNTIME_FUNCTION` as image-relative function start, function end, and unwind-info DWORDs stored in sorted `.pdata`. The address-only Ghidra query had no function or code xrefs there. This strongly supports unwind metadata, not a gameplay registration; the exact PE section was not separately enumerated. The producer's decoder descriptor remains unknown. H85 is supported and H86 falsified for this xref only; continue caller 46/62.""",
)
append_once(
    "experiments/EXP-0128-hit-worker-callers/hypothesis.md",
    "Caller 45 data-xref provenance models",
    """## Caller 45 data-xref provenance models

- Q79-H85: the sole data xref to `FUN_140357c70` is an x64 `RUNTIME_FUNCTION` record rather than gameplay registration. Prediction: neighboring DWORDs match the documented image-relative function-start, function-end, and unwind-info fields for this and another known function.
- Q79-H86: the sole data xref is an application descriptor/registration record that identifies the queued value's gameplay type. Prediction: its neighboring fields do not follow PE unwind-table layout and expose descriptor or owner data.

EV-0591 strongly supports H85 and falsifies H86 for this xref; the exact containing section was not separately enumerated, and the producer descriptor/input remain unknown.""",
)
append_once(
    "research/KNOWLEDGE_GRAPH.md",
    "EV-0591 reclassifies caller 45 data xref as unwind metadata",
    "EV-0591 compares GOG xref DWORDs for FUN_140357c70 and FUN_14040e300 with Microsoft's x64 RUNTIME_FUNCTION layout and finds matching start/end/unwind triples. The apparent table reference is likely exception metadata rather than gameplay registration; caller 45's selected decoder type and input remain unknown [EV-0588], [EV-0590], [EV-0591]. No OBJ-1/OBJ-2 causal edge is added.",
)
append_once(
    "research/ROADMAP.md",
    "## Q-0079 update — caller 45 xref is likely unwind metadata (EV-0591)",
    """## Q-0079 update — caller 45 xref is likely unwind metadata (EV-0591)

The only data reference to caller 45's producer matches the documented x64 `RUNTIME_FUNCTION` start/end/unwind-info triplet in two GOG examples, so it is likely `.pdata` exception metadata rather than an application descriptor [EV-0591]. The decoder's selected type and input remain unresolved. Resume the original caller inventory at `FUN_1406589f0` (caller 46/62); do not treat the xref as a gameplay-registration lead [CL-L403], [M-0145].""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
q79 = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
q79["evidence"] = list(dict.fromkeys([*q79.get("evidence", []), "EV-0591"]))
q79["linked_claims"] = list(dict.fromkeys([*q79.get("linked_claims", []), "CL-L403"]))
for candidate in (
    {
        "id": "Q79-H85",
        "model": "The sole data xref to FUN_140357c70 is a Windows x64 RUNTIME_FUNCTION record, not an application descriptor.",
        "predicted_discriminant": "The three neighboring DWORDs match image-relative function start, function end, and unwind-info fields for this and another known function.",
        "status": "supported",
        "evidence": ["EV-0591"],
    },
    {
        "id": "Q79-H86",
        "model": "The sole data xref to FUN_140357c70 is an application descriptor/registration identifying the queued gameplay type.",
        "predicted_discriminant": "The neighboring fields do not match PE unwind-table layout and expose descriptor/owner data.",
        "status": "falsified",
        "evidence": ["EV-0591"],
    },
):
    hypotheses = q79["hypotheses"]
    prior = next((row for row in hypotheses if row.get("id") == candidate["id"]), None)
    if prior is None:
        hypotheses.append(candidate)
    elif prior != candidate:
        raise SystemExit(f"hypothesis collision: {candidate['id']}")
assessment = "EV-0591 strongly supports reclassifying FUN_140357c70's sole data xref as an x64 RUNTIME_FUNCTION unwind record, not application registration; the exact PE section is not separately verified. Q79-H85/H86 resolve this one xref only. Caller 45's decoder descriptor/input remain unknown, and no OBJ-1/OBJ-2 edge is added."
if assessment not in q79.get("cross_source_assessment", ""):
    q79["cross_source_assessment"] = q79.get("cross_source_assessment", "").rstrip() + " " + assessment
next_action = "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6589f0 --list-call-edges --timeout 600; inspect caller 46/62 FUN_1406589f0 for payload/tag, exact producer provenance, and dispatcher route against Q79-H1/H2/H3. Preserve the exception-metadata correction, tag/event uncertainty, clean Steam matched-hit/protection/raw-AVSK requirement, and GOG/Steam boundary."
q79["next_action"] = next_action
frontier["session_next_action"] = next_action
frontier["next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": "Q-0079/TX-20261018-0013 remains active on OBJ-2: caller 45/62's tag-0x40 producer decodes an unknown typed value before submission; its sole data xref is likely PE unwind metadata, not gameplay registration. Seventeen original callers remain; caller 46 FUN_1406589f0 is next.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
frontier_path.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

state_path = ROOT / "STATE.md"
state = state_path.read_text(encoding="utf-8")
state = state.replace(
    "EV-0589 traces its producer through a shared typed-value decoder, with source/type provenance still unknown and no direct Actor/HitData read in the wrapper.",
    "EV-0589 traces its producer through a shared typed-value decoder, with source/type provenance still unknown and no direct Actor/HitData read in the wrapper. EV-0591 reclassifies its sole data xref as likely x64 unwind metadata, not gameplay registration.",
    1,
)
state = state.replace(
    "EV-0589 maps the producer through a shared typed-value decoder.",
    "EV-0589 maps the producer through a shared typed-value decoder; EV-0591 identifies its sole data xref as likely x64 unwind metadata.",
    1,
)
old_next = "**Selected next line:** inspect the unresolved producer data reference at RVA `0x362ffb4` once [EV-0590]; if the table remains untyped, continue caller 46/62. Keep input provenance, decoded RTTI, transitive behavior, and GOG/Steam boundaries unresolved."
new_next = "**Selected next line:** inspect caller 46/62 `FUN_1406589f0` for its payload, producer, worker tag, dispatcher route, and direct mapped HitData/AV11/AV12/UseSkill edges [EV-0591]. The caller-45 data xref matches likely x64 unwind metadata; keep tag-0x40 input provenance and decoded RTTI unresolved."
if old_next not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
state = state.replace(old_next, new_next, 1)
state_path.write_text(state, encoding="utf-8")

print("registered EV-0591/CL-L403/M-0145; supported Q79-H85, falsified H86; reclassified xref and selected caller 46/62")
