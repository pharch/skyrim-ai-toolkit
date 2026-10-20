#!/usr/bin/env python3
"""Register the Q-0064 refcounted-field producer and receiver trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = [
    ("20261017T234928Z", {"query_mode": "function_query", "requested_rva": "0x18ACD70", "requested_vtable_slot": "0x6C"}, [
        "VTABLE_SLOT_TARGET_RVA=0x737210",
        "CALLER_DECOMPILATION_BEGIN=FUN_14072fd60",
        "param_1[0x134]",
        "param_1[0x135]",
    ]),
    ("20261017T235241Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x7445D0"}, [
        "XREF_CALL_COUNT=2",
        "FUN_140215af0",
        "FUN_140215660",
        "param_1 + 0x9a8",
        "param_1 + 0x9a0",
    ]),
    ("20261017T235427Z", {"query_mode": "address_context_query", "requested_address_rva": "0x3188918"}, [
        "ADDRESS_TARGET=143188918",
        "ADDRESS_TARGET_XREF_COUNT=2835",
    ]),
    ("20261017T235530Z", {"query_mode": "pointer_table_query", "requested_pointer_table_rva": "0x3188918", "requested_pointer_count": 1}, [
        "POINTER_TABLE_ENTRY=index:0 address:143188918 value:0x0",
    ]),
    ("20261017T235735Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x744180"}, [
        "XREF_CALL_COUNT=2",
        "FUN_140738380",
        "FUN_140215660",
        "param_1[0x134]",
        "param_1[0x135]",
    ]),
    ("20261017T235834Z", {"query_mode": "pointer_table_query", "requested_pointer_table_rva": "0x18ACD70", "requested_pointer_count": 128}, [
        "POINTER_TABLE_ENTRY=index:111",
        "value:0x1407371F0",
        "POINTER_TABLE_ENTRY=index:126",
        "value:0x140738340",
    ]),
    ("20261017T235928Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x738380"}, [
        "XREF_CALL_COUNT=14",
        "FUN_14073dc50",
        "FUN_140744180",
    ]),
    ("20261018T000127Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x7371F0"}, [
        "param_1 + 0x8f8",
    ]),
    ("20261018T000234Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x738340"}, [
        "param_1 + 0x8f0",
    ]),
    ("20261018T000406Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0x216B40"}, [
        "FUN_140e05620",
        "FUN_140d19980",
        "INDIRECT_CALL_SITE_COUNT=11",
    ]),
    ("20261018T000509Z", {"query_mode": "direct_call_edge_census", "requested_rva": "0xD19980"}, [
        "param_1 + 0xb8",
        "param_1 + 0xe8",
    ]),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0329" for row in evidence["items"]):
        raise SystemExit("EV-0329 already exists; refusing duplicate registration")

    records: list[dict] = []
    hashes: dict[str, str] = {}
    for stamp, expected, markers in CAPTURES:
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if (
            meta.get("analysis_distribution") != "GOG"
            or meta.get("analysis_binary_product_version") != "1.6.1179"
            or meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("exit_code") != 0
            or meta.get("ok") is not True
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("import_attempted") is not False
            or meta.get("overwrite_attempted") is not False
            or any(meta.get(key) != value for key, value in expected.items())
            or checks.get("program_identity_matches_gog_binary") is not True
            or checks.get("script_no_error") is not True
        ):
            raise SystemExit(f"identity, mode, or completion checks failed: {stamp}")
        stdout = ROOT / meta["artifacts"]["stdout"]
        raw = stdout.read_text(encoding="utf-8", errors="replace")
        if sha(stdout) != meta.get("stdout_sha256"):
            raise SystemExit(f"stdout hash mismatch: {stamp}")
        for marker in markers:
            if marker not in raw:
                raise SystemExit(f"required marker missing for {stamp}: {marker}")
        files = {"metadata": meta_path}
        for kind, relative in meta.get("artifacts", {}).items():
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing {kind} artifact for {stamp}")
            files[kind] = path
        hashes.update({path.relative_to(ROOT).as_posix(): sha(path) for path in files.values()})
        records.append({
            "stamp": stamp,
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_pointer_count": meta.get("requested_pointer_count"),
            "requested_vtable_slot": meta.get("requested_vtable_slot"),
            "metadata_checks": checks,
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        })

    note = TX / "EV-0329-note.md"
    write(note, f"""# EV-0329 — PlayerCharacter refcounted-field producer trace

## Build identity and method

The existing GOG Skyrim AE 1.6.1179.0 project identifies SkyrimSE.exe by SHA-256 {BINARY_SHA}. Eleven bounded queries used the strict adapter with analysis disabled and read-only mode. Every capture reports the matching GOG binary identity, no script error, and no import or overwrite. The private capture manifest retains stdout, stderr, log, script-log, metadata hashes, requested addresses, and completion checks. These addresses belong only to the GOG 1.6.1179.0 analysis build.

## Direct observations

- The PlayerCharacter destructor FUN_14072fd60 releases pointer fields at byte offsets +0x9A0 and +0x9A8 (param_1[0x134] and param_1[0x135]). Each path decrements the reference count and calls the object's vtable slot +0x8 only when the old count is one (capture included in this evidence manifest).
- FUN_1407445d0 stores a non-null or null param_2 in either receiver+0x9A0 or receiver+0x9A8 according to param_3, increments the new reference, and final-releases the replaced value through slot +0x8. Its two direct callers are FUN_140215af0 and FUN_140215660; both pass the global DAT_143188918 as the receiver. The queried global is zero in the binary image and has broad read references, so its runtime class is not independently established by the global-data query.
- FUN_140744180 is called directly from FUN_140738380 and FUN_140215660. It dispatches through receiver vtable offsets +0x378 and +0x3F0. In the primary PlayerCharacter vtable, those slots contain FUN_1407371f0 and FUN_140738340. The first returns receiver+0x8F8 when its flag is set; the second returns receiver+0x8F0. This is strong static evidence that the FUN_140738380 -> FUN_140744180 path expects the PlayerCharacter layout; it is not a runtime observation of the global pointer.
- In FUN_140215660, a value returned by FUN_140216b40 is passed to FUN_1407445d0. FUN_140216b40 gets a resource name through an input object's virtual slot +0x20, calls the generic resource routine FUN_140e05620, and calls FUN_140d19980 on the loaded object. FUN_140d19980 itself calls dynamic virtual slots +0xB8 and +0xE8 and returns the first result. The stored value's concrete class, vtable, and final slot +0x8 target remain unresolved.

## Assessment and limits

EV-0329 maps the PlayerCharacter +0x9A0/+0x9A8 cleanup callback shape and a non-null producer candidate. It does not resolve that callback to a concrete destructor, show a descendant reaching Actor::UseSkill with AV11/AV12, decide Q-0064 H1/H2, or prove zero armor XP. The identity of DAT_143188918 at runtime and the loaded resource object's type remain unknown. No Steam runtime, exact profile, effective protection, positive incoming damage, raw AVSK delta, or vanilla reproduction is established. No causal edge to OBJ-1 is supported.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0329-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0329",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"distribution": "GOG", "product_version": "1.6.1179.0", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "captures": records,
        "private_hashes": hashes,
        "limitations": [
            "DAT_143188918 is zero in the image; no runtime class or initializer is mapped.",
            "Primary PlayerCharacter slot compatibility supports static receiver inference but is not live object telemetry.",
            "The object returned by FUN_140216b40 has unresolved dynamic vtable and final slot +0x8 target.",
            "No AV11/AV12 skill-progress descendant, Steam runtime result, effective protection, raw AVSK delta, or vanilla reproduction is established.",
        ],
    }, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    exp = ROOT / "experiments/EXP-0067-trap-cleanup-ref-object-origin"
    write(exp / "README.md", """# EXP-0067 — Trap cleanup refcounted-field producer

This Q-0064 follow-up maps the PlayerCharacter +0x9A0/+0x9A8 final-release fields, the shared setter/accessor cluster, and a non-null object producer candidate. EV-0329 preserves the GOG build identity, exact vtable mappings, caller contexts, and raw capture hashes. The dynamic object class and finalizer remain open.
""")
    write(exp / "hypothesis.md", """# Competing models

- **Q64-H1:** final-release callbacks on the captured ProcessTrapHit cleanup route do not dispatch AV11/AV12 armor-skill progress.
- **Q64-H2:** at least one such callback or descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **Receiver model A:** FUN_140744180 and likely FUN_1407445d0 operate on the PlayerCharacter layout.
- **Receiver model B:** the setter's global receiver has another runtime type with coincident offsets.

The PlayerCharacter vtable accessors and teardown accesses support model A for the FUN_140738380 helper path. DAT_143188918 remains zero in the image, so the setter's runtime receiver is not directly typed. An unknown callback is inconclusive under Q64-H1/H2.
""")
    write(exp / "protocol.md", """# Protocol

Use the existing identity-checked GOG AE 1.6.1179.0 project through the strict dispatcher, with analysis disabled and read-only mode. Preserve stdout, stderr, logs, script logs, and metadata hashes. Attribute same-offset fields only with receiver or exact vtable evidence. Follow the value producer to an exact object vtable and final slot +0x8 callback. Do not transfer GOG RVAs to Steam AE 1.6.1170.0. Do not infer a vanilla exploit from a diagnostic intervention.
""")
    write(exp / "predicted-outcomes.md", """# Predicted outcomes

- **Supports Q64-H1:** resolve the stored object's finalizer and descendants; they do not reach Actor::UseSkill or the mapped skill-progress sink with AV11/AV12, with no relevant indirect target left open.
- **Supports Q64-H2:** a resolved finalizer descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **Inconclusive:** the resource object's vtable or final slot +0x8 target remains dynamic, or an indirect descendant remains unresolved.
""")
    write(exp / "results.md", """# Results — refcounted-field producer and receiver

EV-0329 confirms PlayerCharacter teardown releases +0x9A0 and +0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 stores into those offsets and releases replaced values through the same slot. Its two direct callers pass DAT_143188918; the global is zero in the binary image and its runtime class is unresolved.

The FUN_140744180 path from FUN_140738380 dispatches through primary PlayerCharacter slots +0x378 and +0x3F0, mapped to accessors for +0x8F8 and +0x8F0. This supports PlayerCharacter receiver attribution for that path. FUN_140215660 passes a value from FUN_140216b40 to the setter; that producer uses a generic resource routine and dynamic +0xB8/+0xE8 calls on the loaded object. The resulting object's concrete class and final +0x8 callback are still unknown.

Q64-H1/H2 remain proposed. No mapped descendant reaches AV11/AV12 skill progress in this evidence, but unresolved dynamic targets preclude a negative conclusion [EV-0329], [EV-0328], [EV-0327], [EV-0325], [EV-0319], [EV-0324], [EV-0260].
""")
    write(exp / "implications.md", """# Implications

Continue by resolving the loaded resource object's exact vtable and the return from its +0xB8 call, then map the object's final vtable slot +0x8 target and descendants. Screen resolved descendants for Actor::UseSkill slot 0xF7 or the mapped skill-progress sink with AV11/AV12. Keep the PlayerCharacter singleton identity of DAT_143188918 labeled as a candidate until its runtime initialization/type is mapped. A live Steam test still needs positive incoming damage, maintained effective protection, and raw Light/Heavy Armor AVSK before and after a verified hit.
""")
    for path in exp.iterdir():
        if path.is_file():
            hashes[path.relative_to(ROOT).as_posix()] = sha(path)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0329",
        "kind": "native",
        "source": "Identity-checked GOG SkyrimSE.exe 1.6.1179.0 read-only traces of PlayerCharacter +0x9A0/+0x9A8 teardown, their shared setter/helper, primary vtable accessors, and the non-null resource-derived value producer.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0329-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY_SHA}. Steam AE 1.6.1170.0 is separate.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Eleven bounded queries with identity and read-only checks; maps primary PlayerCharacter vtable accessors, field setter callers, final-release shape, and generic resource-derived producer path.",
        "result": "PlayerCharacter teardown releases fields +0x9A0/+0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 writes the same offsets; its callers pass DAT_143188918, whose runtime class remains unresolved. FUN_140744180 uses PlayerCharacter vtable accessors on a related helper path. FUN_140216b40 passes a generic resource-derived value to the setter; the returned object's concrete class and finalizer target remain unresolved. This does not decide Q-0064 H1/H2 or establish zero armor XP.",
        "related_evidence": ["EV-0328", "EV-0327", "EV-0325", "EV-0319", "EV-0324", "EV-0261", "EV-0260"],
        "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L161 |" in claims:
        raise SystemExit("CL-L161 already exists; refusing duplicate claim")
    write(claims_path, claims.rstrip() + """
| CL-L161 | In GOG AE 1.6.1179.0, PlayerCharacter teardown releases pointer fields +0x9A0 and +0x9A8 through refcount-final vtable slot +0x8. FUN_1407445d0 stores values at the same offsets; its direct callers pass DAT_143188918, whose runtime class is not identified. FUN_140744180 is called from FUN_140738380 and uses primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0 on that helper path. | supported (bounded build-attested GOG decompilation and vtable mapping) | [EV-0329] | The setter global and stored resource-derived object remain dynamically untyped; no finalizer descendant or AV11/AV12 skill award is mapped. This does not establish zero armor XP, Steam behavior, or vanilla reproduction. No OBJ-1 edge is supported. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    if "## M-0058 —" in mechanisms_path.read_text(encoding="utf-8"):
        raise SystemExit("M-0058 already exists; refusing duplicate mechanism")
    write(mechanisms_path, mechanisms_path.read_text(encoding="utf-8").rstrip() + """

## M-0058 — PlayerCharacter +0x9A0/+0x9A8 refcount-final callback fields (Q-0064)

PlayerCharacter teardown FUN_14072fd60 decrements the references stored at +0x9A0/+0x9A8 and calls each object's vtable slot +0x8 when the old count is one. FUN_1407445d0 stores a candidate value into those offsets and uses the same final-release shape for replaced values. Its direct callers pass DAT_143188918, whose runtime class is not identified. A related FUN_140744180 path uses primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. FUN_140216b40 produces a resource-derived value via generic loading and dynamic object calls, but its class and finalizer target remain unresolved [EV-0329]. Claim CL-L161 -> M-0058. No ActorValue/skill sink edge is supported or excluded; no OBJ-1 edge is supported.
""")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0329 maps PlayerCharacter teardown fields +0x9A0/+0x9A8 to refcount-final virtual slot +0x8 calls and traces a shared setter plus a resource-derived non-null value producer. The related FUN_140744180 helper path uses exact primary PlayerCharacter vtable accessors for +0x8F8/+0x8F0. The setter's global receiver and stored object's dynamic class/finalizer remain unresolved, so no edge to Actor::UseSkill or AV11/AV12 skill progress is added or excluded. Claim CL-L161 -> M-0058; Q-0064 remains active. No edge to OBJ-1 is supported [EV-0329].
""")

    contradictions_path = ROOT / "research/CONTRADICTIONS.md"
    contradictions = contradictions_path.read_text(encoding="utf-8")
    heading = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contradictions.find(heading)
    end = contradictions.find("\n## ", start + len(heading))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contradictions)
    section = contradictions[start:end]
    section = section.replace(
        "**Evidence:** [EV-0328], [EV-0327]",
        "**Evidence:** [EV-0329], [EV-0328], [EV-0327]",
        1,
    )
    old_assessment = "Model A is supported as a bounded GOG 1.6.1179.0 path comparison. EV-0327 resolves the PlayerCharacter global callback to PlayerCamera cleanup, which retains five indirect calls; the primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown. Model B remains unresolved because the main receiver has 28 indirect sites and teardown descendants remain open. EV-0328 ties PC+0x8F8 to a resource loaded from the first-person skeleton path but leaves its runtime class/destructor and other release fields unresolved; no matched live Steam result exists."
    new_assessment = "Model A is supported as a bounded GOG 1.6.1179.0 path comparison. EV-0327 resolves the PlayerCharacter global callback to PlayerCamera cleanup, which retains five indirect calls; the primary PlayerCharacter slot 0x98 also reads/clears +0x730, whose producer and dynamic type remain unknown. EV-0329 maps PlayerCharacter +0x9A0/+0x9A8 teardown to refcount-final virtual slot +0x8 and traces a resource-derived setter value, but the stored object's class/finalizer and AV11/AV12 descendants remain unresolved. Model B remains unresolved because the main receiver has 28 indirect sites and teardown descendants remain open; no matched live Steam result exists."
    if old_assessment not in section:
        raise SystemExit("contradiction assessment changed; inspect before updating")
    section = section.replace(old_assessment, new_assessment, 1)
    write(contradictions_path, contradictions[:start] + section + contradictions[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0067 / EV-0329 maps PlayerCharacter +0x9A0/+0x9A8 refcount-final releases and traces the shared setter to a generic resource-derived value. The stored object's class, finalizer, and skill-progress descendants remain unresolved; Q-0064 stays active.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0329"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L161"]))
    method = "Trace FUN_140216b40 and FUN_140d19980 from EV-0329 to the loaded object's concrete vtable and final slot +0x8 target; screen resolved descendants for AV11/AV12 skill progress."
    item["methods"] = list(dict.fromkeys([*item.get("methods", []), method]))
    item["next_action"] = "Trace FUN_140216b40 return values through FUN_140e05620 and FUN_140d19980 virtual targets; determine the concrete object vtable or finalizer used for PlayerCharacter +0x9A0/+0x9A8, then screen that destructor chain for Actor::UseSkill or the mapped skill-progress sink with AV11/AV12. Keep the global receiver typed only as a PlayerCharacter candidate until its runtime identity is mapped."
    frontier["session_next_action"] = item["next_action"]
    frontier["next_action"] = item["next_action"]
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    log_path = ROOT / "research/SESSION_LOG.md"
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n- {datetime.now(timezone.utc).isoformat(timespec='seconds')} transaction TX-20261017-0011 update: EV-0329 registers the PlayerCharacter +0x9A0/+0x9A8 final-release trace and a generic resource-derived setter value. The exact stored-object class/finalizer and AV11/AV12 descendants remain unresolved; Q64-H1/H2 stay proposed. Next action: map FUN_140216b40/FUN_140d19980 to an exact vtable and finalizer, then screen descendants for the mapped skill-progress sink.\n"
        )
    print("registered EV-0329 and refreshed the Q-0064 evidence, claim, mechanism, contradiction, graph, experiment index, and frontier links")
    print(f"note sha256={sha(note)}; capture manifest sha256={sha(manifest)}")


if __name__ == "__main__":
    main()

