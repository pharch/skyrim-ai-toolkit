#!/usr/bin/env python3
"""Register the bounded PlayerCharacter +0x9D0 producer trace."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0070-trap-cleanup-cell-resource-producer"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T024610Z", "20261018T024829Z", "20261018T024954Z",
    "20261018T025055Z", "20261018T025200Z", "20261018T025258Z",
    "20261018T025412Z", "20261018T025618Z", "20261018T025828Z",
    "20261018T025943Z", "20261018T030052Z", "20261018T030207Z",
    "20261018T030335Z", "20261018T030435Z",
]
MARKERS = {
    "20261018T024610Z": ["TARGET_RVA=0x1A19C0", "FUN_1402b8cf0(lVar3,param_2)", "FUN_140766540"],
    "20261018T024829Z": ["TARGET_RVA=0x2E8580", "DECOMPILATION_BEGIN=FUN_1402e8580"],
    "20261018T024954Z": ["TARGET_RVA=0xE84A70", "param_1 + 0x80"],
    "20261018T025055Z": ["TARGET_RVA=0xE84AD0", "FUN_140e83f10", "FUN_140e84220"],
    "20261018T025200Z": ["ADDRESS_TARGET=1431886f0", "ADDRESS_TARGET_XREF_COUNT=688"],
    "20261018T025258Z": ["TARGET_RVA=0x644E30", "DAT_1431886f0 = uVar8", "TES::vftable"],
    "20261018T025412Z": ["OFFSET_QUERY=0x130", "OFFSET_COMPUTED_WRITER_ANALYSIS_COMPLETE=true"],
    "20261018T025618Z": ["TARGET_RVA=0x1A0F80", "DAT_1431886f0 + 0x137"],
    "20261018T025828Z": ["TARGET_RVA=0x1920B0", "FUN_1401972e0(DAT_1420f7730 + 0xd0)"],
    "20261018T025943Z": ["TARGET_RVA=0x2B1EA0", "TESObjectCELL::vftable", "param_1[0x26] = 0"],
    "20261018T030052Z": ["TARGET_RVA=0x2B8CF0", "hkpClosestRayHitCollector::vftable", "FUN_1408552f0"],
    "20261018T030207Z": ["TARGET_RVA=0x764C30", "FUN_140766540(param_1,fVar24,1)", "DAT_143188918"],
    "20261018T030335Z": ["TARGET_RVA=0xE83F10", "param_2 + 0xc0"],
    "20261018T030435Z": ["TARGET_RVA=0xE84220", "param_1 + 0x10"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + chr(10), encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0332" for row in evidence["items"]):
        raise SystemExit("EV-0332 already exists; refusing duplicate registration")

    hashes: dict[str, str] = {}
    captures: list[dict] = []
    for stamp in STAMPS:
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        checks = meta.get("checks", {})
        if (
            meta.get("analysis_distribution") != "GOG"
            or meta.get("analysis_binary_product_version") != "1.6.1179"
            or meta.get("analysis_binary_sha256") != BINARY_SHA
            or meta.get("exit_code") != 0 or meta.get("ok") is not True
            or meta.get("read_only") is not True
            or meta.get("auto_analysis_disabled") is not True
            or meta.get("import_attempted") is not False
            or meta.get("overwrite_attempted") is not False
            or checks.get("program_identity_matches_gog_binary") is not True
            or checks.get("script_no_error") is not True
        ):
            raise SystemExit(f"identity, read-only, or completion checks failed: {stamp}")
        stdout = ROOT / meta["artifacts"]["stdout"]
        raw = stdout.read_text(encoding="utf-8", errors="replace")
        if sha(stdout) != meta.get("stdout_sha256"):
            raise SystemExit(f"stdout hash mismatch: {stamp}")
        for marker in MARKERS.get(stamp, []):
            if marker not in raw:
                raise SystemExit(f"required marker missing for {stamp}: {marker}")
        files = {"metadata": meta_path}
        for kind, relative in meta.get("artifacts", {}).items():
            path = ROOT / relative
            if not path.is_file():
                raise SystemExit(f"missing {kind} artifact for {stamp}")
            files[kind] = path
        hashes.update({p.relative_to(ROOT).as_posix(): sha(p) for p in files.values()})
        captures.append({
            "stamp": stamp,
            "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_search_displacement": meta.get("requested_search_displacement"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "metadata_checks": checks,
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
            "interpretive_role": (
                "supporting capture" if stamp not in {"20261018T025200Z", "20261018T025618Z", "20261018T025828Z"}
                else "context or collision-control capture; not a class attribution by itself"
            ),
        })

    note = TX / "EV-0332-note.md"
    write(note, f"""# EV-0332 — Candidate PlayerCharacter +0x9D0 producer through cell/resource query

## Build identity and method

The existing GOG Skyrim AE 1.6.1179.0 project identifies SkyrimSE.exe by SHA-256 {BINARY_SHA}. Fourteen read-only, no-analysis Ghidra queries were run through the strict dispatcher. Metadata confirms the matching program identity and successful completion with no import or overwrite. Full output, metadata, and auxiliary hashes are retained in the capture manifest. These are GOG-only addresses; no RVA is transferred to the installed Steam AE 1.6.1170.0 runtime.

## Direct observations

- EV-0328 identified FUN_140766540 as a candidate +0x9D0 writer. Its body obtains plVar10 from FUN_1401a19c0(DAT_1431886f0, &local_268), increments the new pointer's reference count at +0x8, stores it at param_1[0x13a] (+0x9D0), and final-releases the replaced pointer through virtual slot +0x8. FUN_140764c30 calls this writer with its receiver; a direct caller passes DAT_143188918 into FUN_140764c30. Prior PlayerCharacter lifecycle evidence ties the populated global to the PlayerCharacter setup path [EV-0325], [EV-0329]. Receiver attribution remains a bounded path inference, not a recovered source-level type declaration.
- FUN_1401a19c0 reads a pointer from its first argument at +0xC0; if null it obtains one from +0x78, then calls FUN_1402b8cf0 with that nested object and the descriptor. The first argument is the global DAT_1431886f0 initialized by FUN_140644e30 through FUN_140199810, which installs TES::vftable.
- FUN_1402b8cf0 checks a byte at receiver+0x40 and uses receiver+0x48 in a context lookup. A separate caller, FUN_1408552f0, builds hkpClosestRayHitCollector or hkpClosestCdPointCollector and passes a pointer from its +0x60 field to this helper. The constructor FUN_1402b1ea0 installs TESObjectCELL::vftable, initializes the corresponding +0x40 field, constructs BaseExtraList at +0x48, and clears its +0x130 pointer. This layout/call-context match supports a cell-like receiver inference; the exact dynamic receiver for every call is not established.
- If the receiver's +0x130 pointer exists and the descriptor metadata carries low-seven-bit type 0x11, FUN_1402b8cf0 returns the pointer stored eight bytes into that member. Otherwise it calls FUN_140e84ad0. The latter checks metadata at descriptor+0x80, looks for entry type 2 through FUN_140e83f10, and returns entry+0x10; if absent, FUN_140e84220 looks up entry type 1. These helpers return data-derived pointers without exposing a concrete class or vtable.
- The whole-binary +0x130 scan is collision-heavy. FUN_1401920b0's apparent +0x130 access is on a queue rooted at DAT_1420f7730+0xD0, not the TESObjectCELL candidate. The scan did not identify a non-null writer attributable to the relevant receiver. FUN_1402e8580, also called in FUN_140766540, computes a separate ancestry-derived value retained in a local; that return is not the pointer stored at +0x9D0.

## Assessment and limits

This traces a candidate +0x9D0 store through a TES-owned lookup into a cell-like query context and its type-selected resource metadata fallback. It does not recover the returned object's dynamic vtable, final slot+0x8 implementation, or any descendant. The type-0x11 branch is not shown active; the +0x130 field is null-initialized in the TESObjectCELL constructor and no matching non-null writer was identified by the bounded displacement screen. No direct AV11/AV12 award inference follows from this producer trace, and Q64-H1/H2 remain proposed. The line does not establish zero armor XP, effective armor protection, positive incoming damage, an active-profile winner, Steam runtime behavior, vanilla reproduction, or a causal edge to OBJ-1.

## Exact next discriminant

Resolve the returned metadata object's concrete class and vtable on the exact producer path, then map its slot+0x8 release target and descendants to the AV11/AV12 sink. If that remains data-dependent, continue on the independent +0x9A0/+0x9A8 producer path from EV-0329.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0332-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0332",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"distribution": "GOG", "product_version": "1.6.1179.0", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "captures": captures,
        "private_hashes": hashes,
        "limitations": [
            "The +0x9D0 writer remains a candidate receiver path; no source-level type declaration was recovered.",
            "The cell-like TESObjectCELL receiver is a class/layout inference; runtime receiver identity is not observed.",
            "The type-0x11 branch and non-null member at receiver+0x130 were not shown active.",
            "The resource metadata return class, concrete vtable, final slot+0x8 callback, and descendants remain unresolved.",
            "No Steam runtime, active profile, raw AVSK delta, effective armor measurement, or vanilla reproduction is established.",
        ],
    }, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    docs = {
        "README.md": """# EXP-0070 — PlayerCharacter +0x9D0 cell/resource producer

Q-0064 follow-up tracing the EV-0328 candidate +0x9D0 writer through a TES-owned lookup, a cell-like collision query, and resource metadata fallback. EV-0332 narrows the producer but leaves the stored object's class, finalizer, and AV11/AV12 descendants unresolved.
""",
        "hypothesis.md": """# Competing models

- **Q64-H1:** cleanup descendants on the captured ProcessTrapHit route do not dispatch armor skill progress for AV11/AV12.
- **Q64-H2:** at least one teardown callback or descendant reaches skill progress with AV11/AV12.
- **Producer model A:** the type-0x11 cell-context branch returns a nested object whose finalizer can reach the skill sink.
- **Producer model B:** the metadata fallback returns an object whose finalizer does not reach the skill sink.

EV-0332 maps both producer shapes but does not identify which branch is live or either returned class. It therefore distinguishes neither Q64 model.
""",
        "protocol.md": """# Protocol

Use only the existing GOG 1.6.1179.0 project through the strict dispatcher, with analysis disabled and read-only mode. Preserve capture hashes and distinguish direct observations from receiver/class inferences. Do not transfer GOG RVAs to Steam, infer a live branch from static code, or classify an unresolved slot as a negative.
""",
        "predicted-outcomes.md": """# Predicted outcomes

- **Supports producer model A:** identify a concrete object behind cell-context+0x130 on the observed type-0x11 branch, then resolve slot+0x8 and find an AV11/AV12 skill sink.
- **Supports producer model B:** identify the type-2 or type-1 metadata return object's concrete vtable and resolve its finalizer without an AV11/AV12 sink.
- **Supports Q64-H1:** resolve every relevant cleanup descendant and show none reaches skill progress with AV11/AV12.
- **Supports Q64-H2:** a resolved cleanup descendant reaches Actor::UseSkill or the mapped skill-progress sink with an AV11/AV12 argument.
- **Inconclusive:** receiver class, selected metadata branch, returned object's vtable, or finalizer descendants remain dynamic.
""",
        "results.md": """# Results — bounded +0x9D0 producer trace

EV-0332 follows the candidate writer FUN_140766540 through FUN_1401a19c0 and FUN_1402b8cf0. The helper receives a nested object from a TES global at +0xC0 or +0x78. Its layout and ray-query use are consistent with TESObjectCELL, whose constructor clears +0x130. The helper has a type-0x11 branch that reads a nested pointer at +0x130; otherwise it returns a type-2 or type-1 resource metadata pointer.

Neither branch exposes the returned object's concrete vtable or final +0x8 implementation. FUN_1402e8580 in the setter computes a different ancestry-derived local and does not supply the value stored at +0x9D0. Q64-H1/H2 remain open [EV-0332], [EV-0328], [EV-0325], [EV-0329].
""",
        "implications.md": """# Implications

Continue Q-0064 on the independent EV-0329 +0x9A0/+0x9A8 producer path. Resolve FUN_140d19980's dynamic slots +0xB8/+0xE8 and trace the stored object's exact final slot+0x8 target. Return to +0x9D0 if a concrete resource parser or receiver vtable is found.
""",
    }
    for name, body in docs.items():
        path = EXP / name
        write(path, body)
        hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    script = EXP / "register_ev0332.py"
    hashes[script.relative_to(ROOT).as_posix()] = sha(script)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0332",
        "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 traces of the candidate PlayerCharacter +0x9D0 setter, TES-owned lookup, cell-like query, metadata extraction and nested class-layout candidates.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0332-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY_SHA}; no runtime branch selection observed.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Fourteen identity-checked captures map the candidate +0x9D0 store, manager selection, TES initialization, a cell-like query receiver, type-selected metadata fallback, collision controls and separate ancestry helper.",
        "result": "FUN_140766540 stores a FUN_1401a19c0 result at receiver+0x9D0 and final-releases its replacement through slot+0x8. FUN_1401a19c0 passes a nested TES-owned object into FUN_1402b8cf0. The type-0x11 branch and type-2/type-1 metadata fallbacks return opaque pointers; receiver layout is consistent with TESObjectCELL but not a runtime class observation. The stored object's vtable and finalizer remain unresolved, so Q64-H1/H2 are unchanged.",
        "related_evidence": ["EV-0328", "EV-0329", "EV-0325", "EV-0331", "EV-0260"],
        "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False) + chr(10))

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L164 |" in claims:
        raise SystemExit("CL-L164 already exists; refusing duplicate claim")
    write(claims_path, claims.rstrip() + """
| CL-L164 | In GOG AE 1.6.1179.0, candidate writer FUN_140766540 stores the result of FUN_1401a19c0 at receiver+0x9D0 and final-releases a replaced value through vtable slot +0x8. The lookup passes a nested TES-owned object into FUN_1402b8cf0, whose type-0x11 and resource-metadata branches return opaque pointers. | supported (bounded build-attested producer trace) | [EV-0332], [EV-0328] | The receiver's PlayerCharacter attribution is a lifecycle-path inference; the cell-like receiver layout is not a runtime class observation. Neither returned pointer has a mapped concrete vtable or finalizer. Q64-H1/H2 remain unresolved; no AV11/AV12 negative, zero-XP result, Steam behavior, or vanilla reproduction follows. No OBJ-1 edge is supported. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "## M-0061 —" in mechanisms:
        raise SystemExit("M-0061 already exists; refusing duplicate mechanism")
    write(mechanisms_path, mechanisms.rstrip() + """

## M-0061 — Cell/resource metadata producer candidate for +0x9D0 (Q-0064)

Candidate writer FUN_140766540 stores a FUN_1401a19c0 result at receiver+0x9D0 and releases a replaced value through slot+0x8. The lookup chooses a nested TES-owned object and calls FUN_1402b8cf0; its receiver layout and Havok ray-query caller are consistent with TESObjectCELL, whose constructor clears +0x130. The type-0x11 branch and type-2/type-1 resource metadata fallback expose no concrete result vtable or finalizer [EV-0332]. FUN_1402e8580 in the writer derives a separate local and is not the stored pointer. No AV11/AV12 edge or OBJ-1 edge is supported; Q64-H1/H2 remain open. Claim CL-L164 -> M-0061.
""")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0332 narrows a candidate PlayerCharacter +0x9D0 store to a TES-owned cell/resource query and metadata fallback. The exact stored-object vtable and finalizer remain unknown; no edge to AV11/AV12 skill progress or OBJ-1 is added. Claim CL-L164 -> M-0061 [EV-0332].
""")

    contra_path = ROOT / "research/CONTRADICTIONS.md"
    contra = contra_path.read_text(encoding="utf-8")
    head = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contra.find(head)
    end = contra.find(chr(10) + "## ", start + len(head))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contra)
    section = contra[start:end]
    section = section.replace("- **Evidence:** [EV-0331]", "- **Evidence:** [EV-0332], [EV-0331]", 1)
    section = section.replace(
        "the stored object's class/finalizer and AV11/AV12 descendants remain unresolved.",
        "the stored object's class/finalizer and AV11/AV12 descendants remain unresolved. EV-0332 traces a candidate +0x9D0 producer through a TES-owned cell/resource query; both returned-object branches remain dynamically untyped.",
        1,
    )
    write(contra_path, contra[:start] + section + contra[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + chr(10) + chr(10) + "EXP-0070 / EV-0332 traces a candidate PlayerCharacter +0x9D0 producer through a TES-owned cell/resource query; the stored object's class and finalizer remain unresolved. Q-0064 stays open." + chr(10))

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(x for x in frontier["items"] if x.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0332"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L164"]))
    for hyp in item.get("hypotheses", []):
        hyp["evidence"] = list(dict.fromkeys([*hyp.get("evidence", []), "EV-0332"]))
    method = "EV-0332 narrows the +0x9D0 producer to a TES-owned cell/resource query, but the type-selected output class and finalizer remain unresolved."
    item["methods"] = list(dict.fromkeys([*item.get("methods", []), method]))
    next_action = "Continue the independent EV-0329 +0x9A0/+0x9A8 producer path: inspect FUN_140d19980 and its exact callers to resolve dynamic slots +0xB8/+0xE8 and the stored object's final slot+0x8 target. Screen resolved descendants for AV11/AV12 skill progress; return to +0x9D0 only if a concrete resource parser or receiver vtable becomes available."
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False) + chr(10))

    log = ROOT / "research/SESSION_LOG.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(chr(10) + "- " + datetime.now(timezone.utc).isoformat(timespec="seconds") + " transaction TX-20261017-0011 update: EV-0332 traces a candidate +0x9D0 store through a TES-owned cell/resource query; the type-selected metadata returns remain untyped and the finalizer is unresolved. Q64-H1/H2 stay open. Next action: inspect EV-0329's FUN_140d19980 +0xB8/+0xE8 callbacks and resolve the +0x9A0/+0x9A8 stored object's slot+0x8 finalizer." + chr(10))
    print("registered EV-0332, CL-L164, M-0061, experiment EXP-0070, and Q-0064 links")
    print(f"note sha256={sha(note)}; capture manifest sha256={sha(manifest)}")


if __name__ == "__main__":
    main()
