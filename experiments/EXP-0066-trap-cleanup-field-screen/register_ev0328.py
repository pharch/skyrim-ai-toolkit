#!/usr/bin/env python3
"""Register four complete GOG displacement screens for Q-0064."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
SCANS = [("233509", "0x9D0", 21, 9), ("233739", "0x9A8", 24, 7), ("233939", "0x9A0", 22, 5), ("234144", "0x8F8", 32, 8)]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    ev_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(ev_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0328" for row in evidence["items"]):
        raise SystemExit("EV-0328 already exists; refusing duplicate registration")

    records: list[dict] = []
    hashes: dict[str, str] = {}
    for stamp, displacement, access_count, writer_count in SCANS:
        meta_path = GHIDRA / f"gog-query-20261017T{stamp}Z.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        required = ["program_identity_matches_gog_binary", "requested_displacement", "displacement_scan_complete", "writer_analysis_complete", "computed_writer_analysis_complete", "script_no_error"]
        if (
            meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("analysis_distribution") != "GOG"
            or meta.get("query_mode") != "memory_displacement_search"
            or meta.get("requested_search_displacement") != displacement
            or meta.get("exit_code") != 0
            or meta.get("ok") is not True
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("import_attempted") is not False
            or meta.get("overwrite_attempted") is not False
            or any(checks.get(name) is not True for name in required)
        ):
            raise SystemExit(f"query identity or complete-scan checks failed: {stamp}")
        stdout = ROOT / meta["artifacts"]["stdout"]
        if not stdout.is_file():
            raise SystemExit(f"missing scan output: {stdout}")
        raw = stdout.read_text(encoding="utf-8", errors="replace")
        if f"OFFSET_ACCESS_COUNT={access_count}" not in raw:
            raise SystemExit(f"access count changed for {displacement}")
        marker = "OFFSET_WRITER_CANDIDATE_FUNCTION_COUNT="
        if marker + str(writer_count) not in raw:
            raise SystemExit(f"writer-candidate count changed for {displacement}")
        files = {"metadata": meta_path}
        for kind, relative in meta.get("artifacts", {}).items():
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing {kind} artifact for {stamp}")
            files[kind] = path
        hashes.update({path.relative_to(ROOT).as_posix(): sha(path) for path in files.values()})
        records.append({
            "stamp": stamp, "displacement": displacement, "access_count": access_count,
            "writer_candidate_count": writer_count,
            "computed_writer_candidate_count": 0,
            "metadata_checks": checks,
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        })

    note = TX / "EV-0328-note.md"
    write(note, f"""# EV-0328 — PlayerCharacter final-release-field displacement screens

## Build identity and method

The existing GOG Skyrim AE 1.6.1179.0 project identifies `SkyrimSE.exe` by SHA-256 `{BINARY_SHA}`. Four whole-program memory-operand scans were run through the strict adapter in `-noanalysis -readOnly` mode. All report the matching binary identity, requested displacement, complete scan, writer analysis, computed-writer analysis, no script error, and no import/overwrite. Stdout, stderr, logs, script logs, and metadata hashes are in the capture manifest. These are GOG-only addresses; no Steam RVA is inferred.

## Direct observations

| PlayerCharacter candidate field | Operand hits | Writer candidates | Computed writers | Capture |
|---|---:|---:|---:|---|
| `+0x9D0` | 21 | 9 | 0 | `20261017T233509Z` |
| `+0x9A8` | 24 | 7 | 0 | `20261017T233739Z` |
| `+0x9A0` | 22 | 5 | 0 | `20261017T233939Z` |
| `+0x8F8` | 32 | 8 | 0 | `20261017T234144Z` |

The first three scans include PlayerCharacter setup `FUN_14072ed70` and teardown `FUN_14072fd60` accesses; same-displacement hits elsewhere are not attributed without receiver evidence. The `+0x9A8` and `+0x9A0` scans also share accesses in several `FUN_140744xxx` functions, a candidate related lifecycle cluster whose object receiver remains untyped.

For `+0x8F8`, the scan's decompilation of `FUN_140736be0` calls `FUN_140e05900` with the literal resource path `Actors\\Character\\1stPerson\\Skel`, then stores its returned local object in `param_1[0x11f]` (byte offset `+0x8F8`). Cleanup `FUN_140737210` is directly called from PlayerCharacter teardown; on its cleanup branch it clears the same field and decrements/releases the referenced object through its vtable slot `+0x8`. The actual runtime class, loaded vtable, destructor implementation, and downstream skill reachability are not mapped.

## Assessment and limits

EV-0328 identifies a resource-path-linked producer and cleanup method for one PlayerCharacter release field, and supplies complete whole-program screens for the other three fields. It does not resolve any of the four cleanup targets to a concrete final destructor, prove a no-skill-award path, or decide Q-0064 H1/H2. The `FUN_140744xxx` cluster and the `+0x9D0` candidate writers need receiver- and callsite-level follow-up. The next discriminant is to map the `+0x8F8` producer and cleanup virtual slots, then follow the object returned by `FUN_140e05900` to any resolved vtable and descendant.

This is an OBJ-2 static result only; no causal edge to OBJ-1 is supported. Steam runtime, effective armor protection, positive incoming damage, raw AVSK deltas, profile winner, and vanilla reproduction remain unobserved.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0328-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0328",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"distribution": "GOG", "product_version": "1.6.1179.0", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "scans": records,
        "private_hashes": hashes,
        "limitations": ["Offset identity alone does not prove structure or receiver.", "FUN_140e05900 return class and +0x8 destructor target are unresolved.", "No GOG RVA is transferred to Steam.", "No Q-0064 hypothesis is decided."],
    }, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    exp = ROOT / "experiments/EXP-0066-trap-cleanup-field-screen"
    write(exp / "README.md", """# EXP-0066 — Trap cleanup final-release field screen

This static follow-up to Q-0064 screens the four PlayerCharacter fields used by the remaining final-release calls. EV-0328 preserves the complete GOG displacement scans and the `+0x8F8` resource-path producer/cleanup observation. Same-offset hits are not assigned to PlayerCharacter without receiver provenance; no Steam addresses or gameplay outcome are claimed.
""")
    write(exp / "hypothesis.md", """# Competing models

- **Q64-H1:** the teardown descendants do not award AV11/AV12 skill progress. Resolved object targets and arguments stay away from the skill-progress sink.
- **Q64-H2:** at least one cleanup callback routes AV11/AV12 into skill progress. A concrete descendant reaches the mapped sink with one of those ActorValues.

An unresolved dynamic object or indirect call is inconclusive. EV-0328 is intended to identify candidate producer/cleanup pairs, not decide H1/H2.
""")
    write(exp / "protocol.md", """# Protocol

Use the existing identity-checked GOG project via `tools/ghidra_probe.py` and the strict dispatcher with `-noanalysis -readOnly`. Require complete displacement and writer-analysis markers; retain stdout, stderr, logs, and metadata hashes. Attribute offset hits only after receiver evidence. Follow exact function and virtual table targets from the captures. Do not transfer GOG RVAs to Steam AE 1.6.1170.0 or use game mutators.
""")
    write(exp / "predicted-outcomes.md", """# Predicted outcomes

- **Supports H1:** resolved cleanup targets and descendants avoid AV11/AV12 skill sinks, with no relevant indirect calls left open.
- **Supports H2:** a concrete cleanup descendant invokes the mapped skill sink with AV11/AV12.
- **Inconclusive:** producer/type or virtual target remains unresolved. EV-0328 is inconclusive overall, though it identifies the `+0x8F8` resource path.
""")
    write(exp / "results.md", """# Results — final-release-field scans

EV-0328 records four complete GOG whole-program displacement scans: `+0x9D0` (21 operand hits, 9 writer candidates), `+0x9A8` (24, 7), `+0x9A0` (22, 5), and `+0x8F8` (32, 8). All four report zero computed writer candidates. PlayerCharacter setup and teardown access the first three offsets; same-offset matches elsewhere remain untyped. `+0x9A8` and `+0x9A0` share a `FUN_140744xxx` access cluster that warrants receiver tracing.

For `+0x8F8`, `FUN_140736be0` calls the resource routine with `Actors\\Character\\1stPerson\\Skel` and stores the returned object in PlayerCharacter `param_1[0x11f]`. Cleanup method `FUN_140737210`, called by PlayerCharacter teardown, clears and final-releases that field through vtable slot `+0x8`. The actual class/vtable target remains unknown.

Q-0064 H1/H2 remain unresolved; no complete no-award result or Steam runtime comparison exists [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0260].
""")
    write(exp / "implications.md", """# Implications

Trace the `+0x8F8` field producer and cleanup method through their PlayerCharacter vtable slots and identify the observed returned-object vtable before following descendants. Then inspect the shared `FUN_140744xxx` cluster only after its receiver is established. Keep Q64-H1/H2 proposed until relevant indirect targets and skill arguments are resolved; preserve Steam damage/protection/raw-AVSK testing as a separate requirement under EV-0260.
""")
    for path in exp.iterdir():
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = sha(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "edition": "AE", "modified_state": False,
        "id": "EV-0328", "kind": "native",
        "source": "Four complete whole-program GOG SkyrimSE.exe v1.6.1179.0 displacement scans for PlayerCharacter candidate final-release fields +0x9D0, +0x9A8, +0x9A0, and +0x8F8.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0328-note.md", "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY_SHA}. Steam AE 1.6.1170.0 is separate.",
        "lane": "mechanism_inference", "tools": ["tools/ghidra_probe.py through strict dispatcher with --search-displacement and -noanalysis -readOnly"],
        "coverage": "Four complete scans with identity/read-only/writer markers; +0x8F8 writer `FUN_140736be0` and cleanup `FUN_140737210` decompilation show resource path `Actors\\Character\\1stPerson\\Skel` and refcount-final release. Dynamic class and target unresolved.",
        "result": "The four scans have 21/24/22/32 operand hits and 9/7/5/8 candidate writer functions respectively; no computed writers were identified. +0x8F8 is assigned from a resource load using the first-person skeleton path and is cleared/released in a PlayerCharacter teardown helper. This does not identify the actual object class/destructor or decide whether cleanup can reach AV11/AV12 skill progress.",
        "related_evidence": ["EV-0327", "EV-0325", "EV-0319", "EV-0324", "EV-0261", "EV-0260"], "local_hashes": hashes,
    })
    write(ev_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L160 |" in claims:
        raise SystemExit("CL-L160 already exists; refusing duplicate claim")
    write(claims_path, claims.rstrip() + """
| CL-L160 | In GOG AE 1.6.1179.0, PlayerCharacter `+0x8F8` is assigned in `FUN_140736be0` from a resource object returned by `FUN_140e05900` using path `Actors\\Character\\1stPerson\\Skel`; teardown helper `FUN_140737210` clears the field and conditionally final-releases the object through vtable slot `+0x8`. | supported (bounded build-attested displacement scan and producer/cleanup decompilation) | [EV-0328] | The returned object's runtime class, exact destructor implementation, and skill-progress reachability remain unresolved; this does not establish zero armor XP, Steam behavior, or vanilla reproduction. No OBJ-1 causal edge is supported. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    write(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip() + """

## M-0057 — PlayerCharacter `+0x8F8` resource-backed release field (Q-0064)

The complete GOG displacement scan ties PlayerCharacter `+0x8F8` to `FUN_140736be0`, which calls `FUN_140e05900` with `Actors\\Character\\1stPerson\\Skel` and stores the returned object; teardown helper `FUN_140737210` clears the field and conditionally invokes refcount-final vtable slot `+0x8` [EV-0328]. The actual object class, destructor target, and descendant skill behavior remain unknown. The other screened fields remain untyped or only partially attributed. No OBJ-1 edge is supported. Claim CL-L160 -> M-0057.
""")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0328 screens PlayerCharacter final-release candidate fields `+0x9D0`, `+0x9A8`, `+0x9A0`, and `+0x8F8` with complete direct/computed writer scans. The `+0x8F8` producer loads through path `Actors\\Character\\1stPerson\\Skel` and teardown helper `FUN_140737210` clears/releases it; the object's runtime type and destructor target remain unresolved. Other same-offset hits and the shared `FUN_140744xxx` cluster need receiver provenance. This narrows, but does not decide, Q-0064. Claim CL-L160 -> M-0057. No edge to OBJ-1 is supported [EV-0328].
""")

    contradiction_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradiction_path.read_text(encoding="utf-8")
    heading = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contradictions.find(heading)
    end = contradictions.find("\n## ", start + len(heading))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contradictions)
    section = contradictions[start:end]
    if "[EV-0328]" not in section:
        section = section.replace("[EV-0327], [EV-0325]", "[EV-0328], [EV-0327], [EV-0325]", 1)
        section = section.replace(
            "the main receiver has 28 indirect sites, teardown descendants remain open, and no matched live Steam result exists.",
            "the main receiver has 28 indirect sites and teardown descendants remain open. EV-0328 ties PC+0x8F8 to a resource loaded from the first-person skeleton path but leaves its runtime class/destructor and other release fields unresolved; no matched live Steam result exists."
        )
        write(contradiction_path, contradictions[:start] + section + contradictions[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\n`EXP-0066` / EV-0328 screens the four PlayerCharacter final-release fields; `+0x8F8` is set from a resource path ending in `1stPerson\\Skel` and released by a teardown helper, but its class and destructor target remain unknown. Q-0064 remains unresolved.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0328"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L160"]))
    item["methods"].append("Use EV-0328's `+0x8F8` producer/cleanup trace to map the exact PlayerCharacter virtual slots and returned-object vtable; inspect the shared `FUN_140744xxx` cluster only after receiver provenance is established.")
    item["next_action"] = "Query the exact GOG FUN_140736be0 and FUN_140737210 caller/edge contexts plus resource-loading function FUN_140e05900; determine the PlayerCharacter virtual slots and whether the +0x8F8 field's loaded object type or destructor target can be mapped to skill-progress code."
    frontier["session_next_action"] = item["next_action"]
    frontier["next_action"] = item["next_action"]
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    print("registered EV-0328 from four complete read-only GOG field scans")
    print(f"note sha256={sha(note)}; manifest sha256={sha(manifest)}")


if __name__ == "__main__":
    main()
