#!/usr/bin/env python3
"""Register callback caller and listener-name search boundaries for Q-0064."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
FRESH = {
    "20261018T081726Z": [
        "FUNCTION_LOOKUP=FUN_140b439a0",
        "XREF_CALL_COUNT=2",
        "XREF_CALL_EDGE=140f604c0 -> 140b439a0",
        "XREF_CALL_EDGE=140b60df8 -> 140b439a0",
        "CALLER_DECOMPILATION_BEGIN=FUN_140f604b0",
        "INCOMING_CALLER_DECOMPILATION_BEGIN=FUN_140b60df0",
        "INDIRECT_CALL_SITE_COUNT=0",
    ],
    "20261018T081836Z": [
        "STRING_MATCH=1420bcb04 RVA=0x20BCB04",
        "STRING_REFERENCE_COUNT=0",
        "STRING_REFERENCE_SCAN_COMPLETE=true",
    ],
}
REUSED = {
    "20261018T074001Z": [
        "CALLEE_DECOMPILATION_BEGIN=FUN_140b67350",
        "(**(code **)(*plVar2 + 0x10))(plVar2,param_1)",
        "TtconRemCb",
    ],
    "20261018T081252Z": [
        "DECOMPILATION_BEGIN=FUN_140b67200",
        "(**(code **)(*plVar2 + 8))(plVar2,param_1)",
        "TtconAddCb",
    ],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def checked(stamp: str, markers: list[str]):
    meta_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    stdout_path = ROOT / meta["artifacts"]["stdout"]
    checks = meta.get("checks", {})
    valid = (
        meta.get("analysis_distribution") == "GOG"
        and meta.get("analysis_binary_product_version") == "1.6.1179"
        and meta.get("analysis_binary_sha256") == BINARY
        and meta.get("program_executable_path_matches_gog_binary") is True
        and meta.get("exit_code") == 0
        and meta.get("ok") is True
        and meta.get("read_only") is True
        and meta.get("auto_analysis_disabled") is True
        and meta.get("import_attempted") is False
        and meta.get("overwrite_attempted") is False
        and checks.get("program_identity_matches_gog_binary") is True
        and checks.get("script_no_error") is True
        and all(checks.values())
        and sha(stdout_path) == meta.get("stdout_sha256")
    )
    if not valid:
        raise SystemExit(f"capture identity/completion check failed: {stamp}")
    raw = stdout_path.read_text(errors="replace")
    missing = [marker for marker in markers if marker not in raw]
    if missing:
        raise SystemExit(f"capture marker missing: {stamp}: {missing}")
    return meta, meta_path, stdout_path


def main() -> None:
    fresh = {stamp: checked(stamp, markers) for stamp, markers in FRESH.items()}
    reused = {stamp: checked(stamp, markers) for stamp, markers in REUSED.items()}
    note = TX / "EV-0361-note.md"
    manifest = TX / "EV-0361-capture-manifest.json"

    write(note, f"""# EV-0361 — callback consumer caller boundary

## Build and method

Two fresh identity-checked GOG AE 1.6.1179.0 queries used the configured existing project through the strict dispatcher in read-only/no-analysis mode. Two earlier callback-consumer captures are reused from this transaction. Analysis binary SHA-256: {BINARY}. GOG addresses do not transfer to Steam AE 1.6.1170.0.

## Direct observations

- The add-and-notify wrapper FUN_140b439a0 has two analyzed direct caller functions: FUN_140f604b0 and FUN_140b60df0. The first calls it from a post-collision type-0 command handler; the second obtains a nested pointer from `param_2+0x28`, then `+0x10`, and passes that pointer to the wrapper [fresh capture 20261018T081726Z; caller ancestry EV-0359].
- FUN_140b439a0 itself performs the entity constraint-record insertion through FUN_140b678a0, dispatches world callbacks through FUN_140b4fa40, then tail-jumps to the exact hkp add-callback consumer FUN_140b67200. It has no indirect call sites of its own [capture 20261018T081726Z; consumer details EV-0358/EV-0360].
- The removal consumer FUN_140b67350 dispatches each populated entry through its virtual slot +0x10; the add consumer FUN_140b67200 uses slot +0x8. Their trace labels are TtconRemCb and TtconAddCb respectively [reused captures 20261018T074001Z, 20261018T081252Z; EV-0358].
- The exact ASCII string `hkpConstraintListener` exists at GOG address 0x1420bcb04, but the analyzed program reports zero references to it [fresh capture 20261018T081836Z]. This does not identify the concrete callback type or show the callback array is empty.
- These caller and string results identify no producer-backed callback entry and no Actor::UseSkill/AV11/AV12 descendant. They do not settle either Q64 model.

## Competing models and result

- Q64-H1 predicts producer-backed callbacks and members on this route do not dispatch AV11/AV12 progress.
- Q64-H2 predicts a concrete callback or member descendant reaches Actor::UseSkill or the mapped skill-progress sink with AV11/AV12.

The exact add wrapper's two direct callers are now mapped to island/entity and post-collision routes, but no entry writer or listener class is identified. Q64-H1 and Q64-H2 remain proposed.

## Scope and next action

This is static GOG caller/name evidence only. It does not establish Steam behavior, live callback population, effective armor protection, positive final damage, or raw AVSK. Continue with producer-backed membership of the exact ProcessTrapHit instance and the callback/member targets; preserve the runtime discriminator before any armor-XP conclusion.
""")

    docs = {
        "README.md": "# EXP-0099 — callback caller boundary\n\nMap exact add/remove callback consumers to their direct caller routes and record whether retained listener-name metadata identifies concrete entries.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: producer-backed callback/member descendants on the ProcessTrapHit route stay outside AV11/AV12 progress.\n- Q64-H2: a concrete callback/member descendant reaches Actor::UseSkill or mapped progress with AV11/AV12.\n\nConsumer caller identity or an unreferenced type-name string alone does not discriminate the models.\n",
        "protocol.md": "# Protocol\n\nValidate the exact GOG capture metadata and hashes; census direct callers of FUN_140b439a0; compare add/remove virtual dispatch slots; search initialized memory for the listener type name; retain all caller and type boundaries.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. A concrete writer must target the exact hkpConstraintInstance +0x40/+0x48 array/count.\n2. Its entry object must be tied to a concrete class and slot +0x8/+0x10 targets.\n3. Follow that object and target to Actor::UseSkill or the mapped skill-progress sink with an AV11/AV12 argument.\n4. A missing symbol reference, generic caller, or unrelated offset match is inconclusive.\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- Producer-backed non-skill targets strengthen Q64-H1 only for the resolved route.\n- A producer-backed target reaching AV11/AV12 progress supports Q64-H2.\n- An unresolved callback class or object membership leaves both models open.\n",
        "results.md": "# Results\n\nThe exact add-and-notify wrapper has two direct caller functions, mapped to island/entity and post-collision command routes. The binary contains an unreferenced `hkpConstraintListener` string. No callback producer, concrete listener class, or AV11/AV12 descendant is identified; Q64-H1/H2 remain open [EV-0361].\n",
        "implications.md": "# Implications\n\nCaller census narrows the routes that invoke add notification, but it does not reveal who populated the callback array. The next useful discriminator remains producer-backed exact-instance and listener-object lineage.\n",
    }
    for name, content in docs.items():
        write(EXP / name, content)

    capture_rows = {}
    hashes = {}
    for stamp, (meta, meta_path, stdout_path) in {**fresh, **reused}.items():
        capture_rows[stamp] = {
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_string": meta.get("requested_string"),
            "checks": meta.get("checks"),
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
            "reused": stamp in reused,
        }
        for artifact in (meta_path, stdout_path, *(ROOT / p for p in meta["artifacts"].values())):
            if artifact.is_file():
                hashes[artifact.relative_to(ROOT).as_posix()] = sha(artifact)
    for artifact in (note, *EXP.iterdir(), Path(__file__)):
        if artifact.is_file():
            hashes[artifact.relative_to(ROOT).as_posix()] = sha(artifact)
    hashes.pop(manifest.relative_to(ROOT).as_posix(), None)
    write(manifest, json.dumps({
        "evidence_id": "EV-0361",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY,
        "captures": capture_rows,
        "registered_local_hashes": hashes,
    }, indent=2))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(item.get("id") == "EV-0361" for item in evidence["items"]):
        raise SystemExit("EV-0361 already registered")
    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0361",
        "kind": "native",
        "source": "Identity-checked read-only GOG Ghidra caller census and initialized-memory literal search, with reused exact callback-consumer captures.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0361-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "Direct caller functions of the exact hkp add-callback wrapper, add/remove callback virtual dispatch, and retained hkpConstraintListener literal references.",
        "result": "Two direct caller functions invoke the add-and-notify wrapper; the listener-name literal has no analyzed references. Callback writers, entry classes, and AV11/AV12 descendants remain unresolved.",
        "related_evidence": ["EV-0358", "EV-0359", "EV-0360", "EV-0357"],
        "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L200 |" in claims:
        raise SystemExit("CL-L200 already registered")
    write(claims_path, claims.rstrip() + "\n| CL-L200 | In GOG AE 1.6.1179.0, the exact hkp add-callback wrapper FUN_140b439a0 has two analyzed direct caller functions, and the literal `hkpConstraintListener` has no analyzed references. | supported for this static caller/string scope | [EV-0361], [EV-0358] | Callback-array producers, concrete entry classes, skill descendants, and Steam runtime behavior remain unresolved. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    write(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip() + "\n\n## M-0081 — hkp callback dispatch caller boundary (Q-0064)\n\nThe exact add-and-notify wrapper FUN_140b439a0 has two analyzed direct caller functions, one in a post-collision type-0 handler and one island/entity thunk. It inserts the entity constraint record, sends world callbacks, then invokes hkp add callbacks. Those callbacks use entry slot +0x8; removal uses +0x10. The retained `hkpConstraintListener` string has no analyzed references, so no concrete entry class or producer is established. No AV11/AV12 result follows [EV-0361]. Claim CL-L200 -> M-0081.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0361 adds direct caller and callback-slot context for the hkp add/remove dispatch path. It does not establish a producer-backed listener or any causal edge to Actor::UseSkill AV11/AV12 [CL-L200].\n")

    roadmap_path = ROOT / "research/ROADMAP.md"
    write(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip() + "\n\nEV-0361 narrows the exact hkp add-callback dispatch callers to island/entity and post-collision routes; the retained listener-name string has no analyzed references. Continue with exact-instance member/callback producer lineage and preserve the Steam positive-damage, effective-protection, raw-AVSK discriminator.\n")

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0099 / EV-0361 maps direct callers and virtual slots for the exact hkp add/remove callback consumers; no producer or callback class is identified.\n")

    action = "Trace producer-backed membership of the exact ProcessTrapHit hkpConstraintInstance through the island/entity and type-1 command routes, then resolve its callback/member targets to AV11/AV12; preserve the Steam positive-damage, effective-protection, and raw-AVSK discriminator."
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    question = next(item for item in frontier["items"] if item.get("id") == "Q-0064")
    for bucket in [question.setdefault("evidence", []), *(hyp.setdefault("evidence", []) for hyp in question.get("hypotheses", []))]:
        if "EV-0361" not in bucket:
            bucket.append("EV-0361")
    if "CL-L200" not in question.setdefault("linked_claims", []):
        question["linked_claims"].append("CL-L200")
    question["next_action"] = action
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checkpoint_path = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    checkpoint = checkpoint_path.read_text(encoding="utf-8")
    needle = "- Q-0064 / EV-0360 links the exact ProcessTrapHit-created hkpConstraintInstance to its entity +0x100/+0x108 constraint record and +0x60 back-pointer; attach callback dispatch follows but listener writers/classes remain unresolved.\n"
    addition = "- Q-0064 / EV-0361 maps the exact add/remove callback consumer slots and two add-wrapper caller functions; the hkpConstraintListener string has no analyzed references and no producer/class is identified.\n"
    if needle not in checkpoint:
        raise SystemExit("checkpoint helper lacks EV-0360 summary line")
    checkpoint = checkpoint.replace(needle, needle + addition)
    checkpoint = checkpoint.replace(
        "resolve exact +0x40/+0x48 callback writers/classes and follow attach/remove callback and member descendants against AV11/AV12.",
        "trace exact-instance membership through island/entity and type-1 command routes, then resolve producer-backed callback/member descendants against AV11/AV12.",
    )
    checkpoint_path.write_text(checkpoint, encoding="utf-8")
    print("registered EV-0361 / CL-L200 / M-0081; Q-0064 remains active")


if __name__ == "__main__":
    main()
