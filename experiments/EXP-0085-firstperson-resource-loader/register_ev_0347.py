#!/usr/bin/env python3
"""Register the PlayerCharacter first-person skeleton resource trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0085-firstperson-resource-loader"
BINARY = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = [
    {"stamp": "20261018T053039Z", "kind": "memory", "markers": [
        "OFFSET_QUERY=0x8F8", "OFFSET_SCAN_COMPLETE=true",
        "OFFSET_WRITER_CANDIDATE=FUN_140736be0",
        "FUN_140e05900(PTR_s_Actors_Character__1stPerson_Skel_141ffe048,&local_68,&local_48)",
        "param_1[0x11f] = (longlong)local_68",
        "(**(code **)(*plVar17 + 0x150))(plVar17,lVar13 + 8)",
        "OFFSET_WRITER_ANALYSIS_COMPLETE=true"]},
    {"stamp": "20261018T053237Z", "kind": "calls", "markers": [
        "TARGET_RVA=0xE05900", "DECOMPILATION_BEGIN=FUN_140e05900",
        "FUN_140e05620(param_1,local_18)", "local_18[0] + 0x28",
        "DECOMPILATION_END=FUN_140e05900"]},
    {"stamp": "20261018T053336Z", "kind": "calls", "markers": [
        "TARGET_RVA=0xE05620", "DECOMPILATION_BEGIN=FUN_140e05620",
        "FUN_140d0af10", "FUN_140205f50", "FUN_140207000",
        "DECOMPILATION_END=FUN_140e05620"]},
    {"stamp": "20261018T053510Z", "kind": "memory", "markers": [
        "OFFSET_QUERY=0x730", "OFFSET_ACCESS_COUNT=67",
        "OFFSET_MATCHED_FUNCTION_COUNT=47", "OFFSET_WRITER_CANDIDATE=FUN_1407373e0",
        "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true"]},
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def put(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value.rstrip() + "\n", encoding="utf-8")


def validate_capture(spec: dict) -> tuple[dict, dict[str, str]]:
    stamp = spec["stamp"]
    metadata_path = GH / f"gog-query-{stamp}.meta.json"
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    checks = meta.get("checks", {})
    if (meta.get("analysis_distribution") != "GOG"
        or meta.get("analysis_binary_product_version") != "1.6.1179"
        or meta.get("analysis_binary_sha256") != BINARY
        or meta.get("program_executable_path_matches_gog_binary") is not True
        or meta.get("exit_code") != 0 or meta.get("ok") is not True
        or meta.get("read_only") is not True or meta.get("auto_analysis_disabled") is not True
        or meta.get("import_attempted") is not False or meta.get("overwrite_attempted") is not False
        or checks.get("program_identity_matches_gog_binary") is not True
        or checks.get("script_no_error") is not True):
        raise SystemExit(f"identity/read-only/completion validation failed: {stamp}")
    if spec["kind"] == "memory":
        if (meta.get("query_mode") != "memory_displacement_search"
            or checks.get("displacement_scan_complete") is not True
            or checks.get("writer_analysis_complete") is not True):
            raise SystemExit(f"memory scan completion validation failed: {stamp}")
    else:
        if (meta.get("query_mode") != "direct_call_edge_census"
            or checks.get("function_lookup") is not True
            or checks.get("requested_rva_lookup") is not True
            or checks.get("decompilation") is not True):
            raise SystemExit(f"function query completion validation failed: {stamp}")
    stdout = ROOT / meta["artifacts"]["stdout"]
    raw = stdout.read_text(encoding="utf-8", errors="replace")
    if digest(stdout) != meta.get("stdout_sha256") or any(marker not in raw for marker in spec["markers"]):
        missing = [marker for marker in spec["markers"] if marker not in raw]
        raise SystemExit(f"stdout hash/marker validation failed: {stamp}: {missing}")
    files = [metadata_path] + [ROOT / relative for relative in meta["artifacts"].values()]
    if any(not path.is_file() for path in files):
        raise SystemExit(f"capture artifact missing: {stamp}")
    hashes = {path.relative_to(ROOT).as_posix(): digest(path) for path in files}
    row = {
        "stamp": stamp, "query_kind": spec["kind"], "query_mode": meta.get("query_mode"),
        "requested_rva": meta.get("requested_rva"),
        "requested_search_displacement": meta.get("requested_search_displacement"),
        "checks": checks, "overall_ok": meta.get("ok"),
        "stdout_sha256": meta.get("stdout_sha256"),
        "stderr_sha256": meta.get("stderr_sha256"),
        "query_script_sha256": meta.get("query_script_sha256"),
    }
    return row, hashes


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0347" for row in evidence.get("items", [])):
        raise SystemExit("EV-0347 already registered")
    rows: list[dict] = []
    local_hashes: dict[str, str] = {}
    for spec in CAPTURES:
        row, hashes = validate_capture(spec)
        rows.append(row)
        local_hashes.update(hashes)

    note = TX / "EV-0347-note.md"
    put(note, f"""# EV-0347 — First-person skeleton resource stored at PlayerCharacter +0x8F8

## Build and method

Four bounded queries used the existing GOG Skyrim AE 1.6.1179.0 Ghidra project, analysis binary SHA-256 {BINARY}, through the strict dispatcher in read-only/no-analysis mode. Two complete memory-displacement scans examined PlayerCharacter-related offsets +0x8F8 and +0x730; two function queries traced the loader at FUN_140e05900 and its lower-level mesh-resource path FUN_140e05620. All identities and query completion markers passed. No GOG RVA is transferred to Steam AE 1.6.1170.0.

## Direct observations

- The complete +0x8F8 displacement scan identifies FUN_140736be0 as a writer and FUN_14072fd60 as the teardown reader. FUN_140736be0 passes the global string symbol `Actors\\Character\\1stPerson\\Skel` to FUN_140e05900, which writes the loaded object into a local retained pointer. On replacement, the function increments the new pointer's refcount at +0x8, stores it at PlayerCharacter+0x8F8, and decrements/releases the old object through its slot +0x8 when the old count reaches one [capture 20261018T053039Z; compare EV-0346].
- FUN_140e05900 calls FUN_140e05620 with that name, then reads the returned resource object's member at +0x28 and transfers it to the caller with refcount management [capture 20261018T053237Z].
- FUN_140e05620 prepends `meshes\\` to the supplied name and uses the engine resource-cache/load paths, including FUN_140205f50 and FUN_140207000 [capture 20261018T053336Z]. This supports a first-person mesh/NIF resource interpretation of the field's source path; it does not identify the parsed resource root's concrete class.
- After loading, FUN_140736be0 invokes the object through virtual slots +0x28 and +0x150 and passes named markers into the latter. These uses are consistent with scene-object operations but do not by themselves prove a NiNode or NiAVObject vtable.
- The complete +0x730 displacement scan found 67 object-base accesses across 47 functions and identified FUN_1407373e0, the PlayerCharacter constructor, and FUN_14072fd60 among the writer/context candidates. It adds no new exact class or finalizer for +0x730; EV-0334 remains the bounded cell-transition/scene-child analysis [capture 20261018T053510Z].

## Causal assessment

This resolves the source path and field role of PlayerCharacter+0x8F8 more tightly than the generic resource-loader evidence in EV-0331. It corroborates that NiNode is a plausible candidate for the first-person skeleton, but the loaded NIF root and all descendants remain data-selected and unobserved. The +0x8 release shape and scene-like virtual calls do not resolve the deleting-destructor target or its descendant chain. No AV11/AV12 sink reachability or exclusion follows; Q64-H1/H2 and Q65-H1/H2 remain proposed. No OBJ-1 edge is added.

## Exact next discriminant

Trace the +0x9D0 producer through its type-selected metadata/resource return and determine whether a concrete vtable can be recovered. If that remains data-dependent, trace the independent +0x9A0/+0x9A8 model-resource producer. Preserve the first-person root class as unresolved unless an exact supported NIF inspection or runtime class observation becomes available.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = digest(note)
    manifest = TX / "EV-0347-capture-manifest.json"
    put(manifest, json.dumps({"evidence_id": "EV-0347", "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BINARY, "captures": rows}, indent=2, ensure_ascii=False))
    local_hashes[manifest.relative_to(ROOT).as_posix()] = digest(manifest)

    docs = {
        "README.md": "# EXP-0085 — First-person skeleton resource path\n\nTrace the PlayerCharacter+0x8F8 producer from its named first-person skeleton resource through the generic mesh loader, and keep source-path evidence separate from the unresolved NIF root class.\n",
        "hypothesis.md": "# Competing models\n\n- Q64-H1: the +0x8F8 resource object's concrete finalizer descendants do not reach AV11/AV12 skill progress.\n- Q64-H2: at least one +0x8F8 finalizer descendant can route AV11/AV12 into skill progress.\n\nThe named mesh path and generic slot +0x8 release do not discriminate the models.\n",
        "protocol.md": "# Protocol\n\nUse only identity-checked queries against the existing GOG 1.6.1179.0 project through the strict dispatcher with analysis disabled and read-only mode. Confirm the +0x8F8 writer, path argument, loader handoff, retained result, and cleanup shape. Do not assign the loaded NIF root class from the path or method names. Keep GOG and Steam addresses separate.\n",
        "results.md": "# Results\n\nFUN_140736be0 loads the named resource `Actors\\\\Character\\\\1stPerson\\\\Skel` through FUN_140e05900; the generic loader prepends `meshes\\\\` and obtains a reference-counted object from a resource handle member at +0x28. FUN_140736be0 stores the object at PlayerCharacter+0x8F8 and uses virtual slots +0x28 and +0x150. The NIF root class and exact slot +0x8 target remain unknown [EV-0347].\n",
        "predicted-outcomes.md": "# Predicted outcomes\n\n- A concrete +0x8F8 root/finalizer path reaching Actor::UseSkill with AV11/AV12 supports Q64-H2 for that branch.\n- A resolved chain that avoids the mapped sink narrows Q64-H1 to that branch only.\n- The generic resource handle, a NiNode parser candidate, or slot +0x8 alone is inconclusive.\n",
        "implications.md": "# Implications\n\nThe first-person resource source is now tied to PlayerCharacter+0x8F8. The evidence is stronger than a generic loader candidate but remains short of exact asset parsing or a concrete destructor chain. The +0x730 field retains its separate cell-transition candidate analysis.\n",
        "expected-discriminants.md": "# Expected discriminants\n\n1. Identify the exact root class for Actors\\\\Character\\\\1stPerson\\\\Skel through a supported read-only asset or runtime observation.\n2. Map its concrete vtable slot +0x8 and descendants.\n3. Screen the full release chain for Actor::UseSkill AV11/AV12.\n4. Trace +0x9D0 and +0x9A0/+0x9A8 independently while the NIF class remains unresolved.\n",
    }
    for name, content in docs.items():
        put(EXP / name, content)
    for path in EXP.iterdir():
        if path.is_file():
            local_hashes[path.relative_to(ROOT).as_posix()] = digest(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0347", "kind": "native",
        "source": "Read-only GOG Ghidra displacement scans and resource-loader traces for PlayerCharacter+0x8F8 and +0x730.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0347-note.md",
        "sha256": digest(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY}; static only.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Complete memory displacement scans for offsets +0x8F8 and +0x730 plus function decompilations for the +0x8F8 resource loader. The exact first-person NIF root class, all dynamic finalizers, and AV11/AV12 reachability remain unresolved.",
        "result": "FUN_140736be0 loads Actors\\\\Character\\\\1stPerson\\\\Skel through the generic mesh loader, retains the returned resource object at PlayerCharacter+0x8F8, and uses virtual slots +0x28/+0x150. The loader prepends meshes\\\\ and reads a reference-counted object from a resource handle at +0x28. This identifies the resource path, not the parsed root class or finalizer. The +0x730 scan adds no concrete class. No Q64/Q65 resolution or AV11/AV12 exclusion follows.",
        "related_evidence": ["EV-0328", "EV-0331", "EV-0334", "EV-0346", "EV-0217", "EV-0220", "EV-0221"],
        "local_hashes": local_hashes,
    })
    put(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L185 |" in claims:
        raise SystemExit("CL-L185 already exists")
    put(claims_path, claims.rstrip() + "\n| CL-L185 | In GOG AE 1.6.1179.0, FUN_140736be0 loads `Actors\\\\Character\\\\1stPerson\\\\Skel` through the generic mesh-resource path and retains the returned object at PlayerCharacter+0x8F8; the object is used through virtual slots +0x28/+0x150. | supported for source path and field flow; resource-root interpretation is bounded inference | [EV-0347], [EV-0331] | The parsed NIF root class, exact slot +0x8 target, descendants, and AV11/AV12 reachability remain unknown. |")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    put(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip()
        + "\n\n## M-0067 — First-person skeleton resource lifetime at PlayerCharacter+0x8F8 (Q-0064)\n\nFUN_140736be0 passes the named first-person skeleton path `Actors\\\\Character\\\\1stPerson\\\\Skel` to FUN_140e05900; the generic mesh loader prepends `meshes\\\\`, returns a refcounted resource object through handle member +0x28, and the caller retains it at PlayerCharacter+0x8F8 [EV-0347]. The caller uses slots +0x28 and +0x150, while teardown final-releases the field through dynamic slot +0x8 [EV-0346]. This supports a scene-resource role but does not prove the exact NIF root class, concrete finalizer, or any AV11/AV12 descendant. Claim CL-L185 -> M-0067; no causal sink edge is resolved.\n")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    put(graph_path, graph_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEV-0347 ties PlayerCharacter+0x8F8 to the named first-person skeleton resource and generic mesh loader; this strengthens the source-path side of EV-0331's conditional NiNode candidate but does not establish a concrete NIF root or destructor table. The exact +0x8 finalizer descendants remain untyped, so no edge to Actor::UseSkill AV11/AV12 is added or excluded. The separate +0x730 cell-scene branch remains mapped only to a cell-transition child candidate [EV-0334], while +0x9D0 and +0x9A0/+0x9A8 retain data-selected producer gaps [EV-0332], [EV-0333]. Claim CL-L185 -> M-0067; Q64-H1/H2 and Q65-H1/H2 remain unresolved.\n")

    index_path = ROOT / "experiments/README.md"
    put(index_path, index_path.read_text(encoding="utf-8").rstrip()
        + "\n\nEXP-0085 / EV-0347 traces the PlayerCharacter+0x8F8 first-person skeleton resource path through the generic mesh loader; the exact NIF root class and finalizer remain unresolved.\n")
    roadmap_path = ROOT / "research/ROADMAP.md"
    put(roadmap_path, roadmap_path.read_text(encoding="utf-8").rstrip()
        + "EV-0347 ties PlayerCharacter+0x8F8 to `Actors\\\\Character\\\\1stPerson\\\\Skel` and the generic mesh-resource path, but does not resolve the NIF root class or slot +0x8 descendants. The +0x730 displacement scan reconfirms the cell-transition writer without adding a concrete type. Next, inspect the +0x9D0 type-selected metadata/resource producer and compare its exact return/finalizer path; then continue the independent +0x9A0/+0x9A8 model path. Claim CL-L185 -> M-0067.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q64 = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    q65 = next(row for row in frontier["items"] if row.get("id") == "Q-0065")
    for row in (q64, q65):
        if "EV-0347" not in row.setdefault("evidence", []):
            row["evidence"].append("EV-0347")
        for hypothesis in row.get("hypotheses", []):
            if "EV-0347" not in hypothesis.setdefault("evidence", []):
                hypothesis["evidence"].append("EV-0347")
    for row in (q64, q65):
        if "CL-L185" not in row.setdefault("linked_claims", []):
            row["linked_claims"].append("CL-L185")
    q64["next_action"] = (
        "Trace the +0x9D0 producer through its type-selected metadata/resource return and determine whether a concrete "
        "vtable and slot +0x8 finalizer can be recovered. Start with FUN_140766540/FUN_1401a19c0/FUN_1402b8cf0 and "
        "the descriptor type branches; keep the type-0x11 cell branch conditional. If the returned class remains "
        "data-dependent, follow the independent +0x9A0/+0x9A8 model-resource producer. Screen resolved descendants "
        "for Actor::UseSkill AV11/AV12 and leave the +0x8F8 NIF root unresolved without exact asset evidence."
    )
    q65["next_action"] = (
        "Compare producer-backed concrete tables for +0x8F8, +0x730, +0x9D0, +0x9A0/+0x9A8, and ThirdPersonState+0xA0. "
        "EV-0347 identifies the +0x8F8 resource path but not its root class; do not count a shared slot +0x8 ABI as a "
        "shared NiNode finalizer family."
    )
    if not any(a.get("action_key") == "q65-firstperson-resource-path-registered" for a in q65.get("attempts", [])):
        q65.setdefault("attempts", []).append({
            "action_key": "q65-firstperson-resource-path-registered",
            "outcome": "EV-0347 identifies +0x8F8 as the retained object loaded from the first-person skeleton mesh path, but does not identify its concrete NIF root or slot +0x8 target. It therefore neither supports nor falsifies the shared NiNode-family model.",
            "evidence": ["EV-0347"],
            "new_discriminant": "A concrete producer-backed vtable for the loaded first-person root must match another field's exact vtable/finalizer before Q65-H1 is supported.",
            "next_action": q65["next_action"],
        })
    put(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    checkpoint_path = ROOT / "experiments/EXP-0064-dawnguard-alternate-entry-source/checkpoint_q64_begin.py"
    checkpoint = checkpoint_path.read_text(encoding="utf-8")
    old_task = "Q-0064 is active to trace unresolved PlayerCharacter cleanup dispatches on the OBJ-2 physical-trap route."
    new_task = "Q-0064 remains active on PlayerCharacter cleanup dispatches for the OBJ-2 physical-trap route."
    old_process = "enumerate and classify the eight indirect cleanup sites before a bounded target query."
    new_process = "resolve producer-backed cleanup object classes and screen their descendants for AV11/AV12."
    if old_task not in checkpoint or old_process not in checkpoint:
        raise SystemExit("checkpoint task/process wording not found")
    checkpoint = checkpoint.replace(old_task, new_task).replace(old_process, new_process)
    needle = "- Q-0062 / EV-0324–EV-0325 maps the GOG AE 1.6.1179.0 ProcessTrapHit path around the known armor/Block XP wrapper. The PlayerCharacter cleanup body has 108 direct edges and eight indirect sites; the trap remains unverified for positive final damage, effective protection, and zero raw AVSK change.\n"
    addition = needle + "- Q-0064 / EV-0347 ties PlayerCharacter+0x8F8 to `Actors\\\\Character\\\\1stPerson\\\\Skel` through the generic mesh loader. The exact NIF root class and slot +0x8 descendants remain unresolved; the +0x730 scan adds no concrete class.\n"
    if needle not in checkpoint:
        raise SystemExit("checkpoint insertion point not found")
    checkpoint = checkpoint.replace(needle, addition)
    put(checkpoint_path, checkpoint)

    print("registered EV-0347 / CL-L185 / M-0067; Q-0064 continues on the +0x9D0 metadata producer")


if __name__ == "__main__":
    main()
