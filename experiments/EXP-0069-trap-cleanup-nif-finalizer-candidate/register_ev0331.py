#!/usr/bin/env python3
"""Register a conditional NiNode finalizer candidate for PlayerCharacter +0x8F8."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = ROOT / "experiments/EXP-0069-trap-cleanup-nif-finalizer-candidate"
BINARY_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
STAMPS = [
    "20261018T023046Z", "20261018T023142Z", "20261018T023239Z",
    "20261018T023503Z", "20261018T023558Z", "20261018T023657Z",
    "20261018T023819Z", "20261018T023913Z", "20261018T024014Z",
    "20261018T024137Z",
]
MARKERS = {
    "20261018T023046Z": ["TARGET_RVA=0x737210", "CALL qword ptr [RAX + 0x8]", "param_1[0x11f]"],
    "20261018T023142Z": ["TARGET_RVA=0x736BE0", "FUN_140e05900", "Actors_Character__1stPerson_Skel"],
    "20261018T023239Z": ["TARGET_RVA=0xE05620", "FUN_140e05620", "local_18[0] + 0x28"],
    "20261018T023503Z": ["STRING_MATCH=1419ac050", "string=NiNode", "140d432a0"],
    "20261018T023558Z": ["TARGET_RVA=0xD432A0", 'FUN_140d22590("NiNode",FUN_140d1e880)'],
    "20261018T023657Z": ["TARGET_RVA=0xD1E880", "NiNode::vftable", "0x1419ac3f0"],
    "20261018T023819Z": ["POINTER_TABLE_ENTRY=index:1", "value:0x140D28F40"],
    "20261018T023913Z": ["TARGET_RVA=0xD28F40", "(**(code **)*param_1)(param_1,1)"],
    "20261018T024014Z": ["TARGET_RVA=0xD20350", "NiNode::vftable", "FUN_140d1d8f0"],
    "20261018T024137Z": ["TARGET_RVA=0xD1D8F0", "INDIRECT_CALL_SITE_COUNT=3", "FUN_140d27be0"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0331" for row in evidence["items"]):
        raise SystemExit("EV-0331 already exists; refusing duplicate registration")

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
            "stamp": stamp, "query_mode": meta.get("query_mode"),
            "requested_rva": meta.get("requested_rva"),
            "requested_string": meta.get("requested_string"),
            "requested_address_rva": meta.get("requested_address_rva"),
            "requested_pointer_table_rva": meta.get("requested_pointer_table_rva"),
            "requested_pointer_count": meta.get("requested_pointer_count"),
            "metadata_checks": checks,
            "stdout_sha256": meta.get("stdout_sha256"),
            "stderr_sha256": meta.get("stderr_sha256"),
            "adapter_sha256": meta.get("adapter_sha256"),
            "query_script_sha256": meta.get("query_script_sha256"),
        })

    note = TX / "EV-0331-note.md"
    write(note, f"""# EV-0331 — Conditional NiNode finalizer candidate for PlayerCharacter +0x8F8

## Build identity and method

The existing GOG Skyrim AE 1.6.1179.0 project identifies SkyrimSE.exe by SHA-256 {BINARY_SHA}. Ten bounded Ghidra captures were run through the strict dispatcher with analysis disabled and read-only mode. Their metadata confirms matching program identity, successful query completion, no import, and no overwrite. Capture and metadata hashes are retained. These RVAs are not transferred to Steam AE 1.6.1170.0.

The tested archive helper in this checkout supports narrow PEX extraction from Skyrim - Misc.bsa and is not a general BSA/NIF extractor. No NIF data for the exact first-person skeleton resource was parsed in this line.

## Direct observations

- PlayerCharacter field +0x8F8 is loaded in FUN_140736be0 by calling FUN_140e05900 with resource name Actors\\\\Character\\\\1stPerson\\\\Skel; teardown FUN_140737210 clears the field and final-releases it through virtual slot +0x8 when its refcount reaches zero [EV-0328; new captures in this manifest].
- FUN_140e05900 delegates to generic resource loading through FUN_140e05620 and retrieves the loaded object from a handle field at +0x28. This generic path does not identify the parsed object class for this specific resource.
- The GOG NIF parser registry has a NiNode name entry mapping to FUN_140d1e880. That parser allocates and initializes an object, then writes NiNode::vftable at absolute 0x1419AC3F0 (GOG RVA 0x19AC3F0).
- In that candidate NiNode table, entry 1 (byte offset +0x8) is FUN_140d28f40. This deleting-destructor thunk dispatches the object's slot 0; the NiNode table's entry 0 is FUN_140d20350.
- FUN_140d20350 resets child parent/index fields, decrements each child refcount and final-releases children through their own slot +0x8, then calls FUN_140d1d8f0 for NiAVObject cleanup. That cleanup has three indirect sites, including an unresolved slot +0x128 dispatch on an object stored at parent offset +0x40, plus refcount-final slot +0x8 releases. The inspected NiNode/NiAVObject bodies contain no direct Actor::UseSkill or mapped AV11/AV12 skill-progress call.

## Assessment and limits

The parser registry and candidate destructor chain do not prove that the actual Actors\\\\Character\\\\1stPerson\\\\Skel resource has a NiNode root or that its subtree consists only of these classes. The child slot +0x8 finalizers and the NiAVObject slot +0x128 target remain dynamic. EV-0331 therefore narrows a plausible +0x8F8 release class but does not resolve its runtime target, decide Q64-H1/H2, or establish a no-award path. No OBJ-1 edge is supported. No Steam runtime, active-profile winner, effective protection, positive incoming damage, raw AVSK delta, or vanilla reproduction is established.

## Exact next discriminant

Obtain a supported read-only NIF extraction/inspection route or verified runtime object-class observation for this exact resource. Continue independent Q-0064 static work at PlayerCharacter +0x9D0 while that class evidence is unavailable.
""")
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    manifest = TX / "EV-0331-capture-manifest.json"
    write(manifest, json.dumps({
        "evidence_id": "EV-0331",
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "analysis_binary": {"distribution": "GOG", "product_version": "1.6.1179.0", "sha256": BINARY_SHA},
        "project_mode": {"existing_project": True, "read_only": True, "auto_analysis_disabled": True, "import_attempted": False, "overwrite_attempted": False},
        "captures": captures, "private_hashes": hashes,
        "limitations": [
            "The exact first-person skeleton NIF root and child tree were not read.",
            "NiNode registration and destructor mapping are conditional candidates for this resource, not runtime type observation.",
            "NiNode child finalizers and the NiAVObject slot+0x128 target remain dynamic.",
            "No Steam runtime, effective protection, raw AVSK delta, profile winner, or vanilla reproduction is established.",
        ],
    }, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    docs = {
        "README.md": """# EXP-0069 — First-person skeleton finalizer candidate

Q-0064 follow-up tracing PlayerCharacter +0x8F8 through the generic resource loader and the GOG NiNode parser registry. EV-0331 maps a conditional NiNode destructor chain but does not establish the actual skeleton asset's root type or child tree.
""",
        "hypothesis.md": """# Competing models

- **Q64-H1:** captured cleanup descendants do not award AV11/AV12.
- **Q64-H2:** at least one resolved cleanup descendant reaches skill progress with AV11/AV12.
- **Resource model A:** the loaded first-person skeleton root is a NiNode and follows the mapped NiNode finalizer.
- **Resource model B:** the actual parsed root or relevant subtree uses another class/finalizer.

The binary registers a NiNode parser and maps its candidate destructor, but the specific NIF file was not extracted. Resource models A/B remain unresolved; a candidate destructor without the asset type is inconclusive for Q64.
""",
        "protocol.md": """# Protocol

Use the existing GOG AE 1.6.1179.0 project through the strict dispatcher, in read-only mode with analysis disabled. Preserve all raw captures and identity metadata. Keep parser-registration evidence separate from claims about one NIF resource. Do not use untested BSA/NIF tools, transfer GOG RVAs to Steam AE 1.6.1170.0, or promote a diagnostic intervention to vanilla reproduction.
""",
        "predicted-outcomes.md": """# Predicted outcomes

- **Supports resource model A:** inspect the exact source NIF or a verified runtime type observation and find a NiNode root; then map its child tree and finalizers.
- **Supports resource model B:** the exact source NIF/runtime observation identifies another root class.
- **Supports Q64-H1:** resolve the exact object and all relevant child/property finalizers; none reaches AV11/AV12 skill progress.
- **Supports Q64-H2:** a resolved finalizer descendant reaches the mapped skill-progress sink with AV11 or AV12.
- **Inconclusive:** exact NIF class, child types, or dynamic finalizer targets remain unresolved.
""",
        "results.md": """# Results — conditional NiNode path

EV-0331 maps the NiNode parser registration and constructor vtable, then maps vtable slot +0x8 through FUN_140d28f40 to primary destructor FUN_140d20350. That destructor final-releases each child object through its virtual slot +0x8 and delegates to FUN_140d1d8f0. The NiAVObject cleanup includes an unresolved slot +0x128 call on an object at offset +0x40.

No direct Actor skill-progress call appears in the inspected bodies. However, the first-person skeleton resource's exact NIF root, subtree, child finalizers, and slot +0x128 target are unknown. This is a conditional class candidate only; it does not resolve Q64-H1/H2 [EV-0331], [EV-0328], [EV-0327], [EV-0324].
""",
        "implications.md": """# Implications

Continue Q-0064 independently at PlayerCharacter field +0x9D0. Inspect EV-0328's writer candidates, attribute one producer to the PlayerCharacter receiver, and map its exact object vtable and final slot +0x8 target. Keep EV-0331's NiNode chain conditional until the exact NIF payload or runtime class is available.
""",
    }
    for name, body in docs.items():
        p = EXP / name
        write(p, body)
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    script = EXP / "register_ev0331.py"
    hashes[script.relative_to(ROOT).as_posix()] = sha(script)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0331",
        "kind": "native",
        "source": "Identity-checked GOG Skyrim AE 1.6.1179.0 traces of the PlayerCharacter +0x8F8 resource path, generic loader, NiNode parser registry/constructor, NiNode vtable/destructor, and NiAVObject cleanup.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0331-note.md",
        "sha256": sha(note),
        "runtime": f"Existing GOG AE 1.6.1179.0 Ghidra project; analysis binary SHA-256 {BINARY_SHA}; exact asset root is unobserved.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through strict dispatcher with -noanalysis -readOnly"],
        "coverage": "Ten identity-checked bounded captures map the +0x8F8 load/release shape, generic resource handle, NiNode parser registration/vtable, NiNode finalizer and NiAVObject cleanup. Exact asset root, subtree, and dynamic finalizer targets remain unresolved.",
        "result": "A NiNode parser and candidate finalizer are mapped, but the exact first-person skeleton resource is not linked to that root type. The candidate destructor releases child objects dynamically and delegates to NiAVObject cleanup with an unresolved slot+0x128 target; no direct skill-progress call appears in inspected bodies. Q64-H1/H2 remain open.",
        "related_evidence": ["EV-0330", "EV-0329", "EV-0328", "EV-0327", "EV-0325", "EV-0319", "EV-0324", "EV-0260"],
        "local_hashes": hashes,
    })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")

    claims_path = ROOT / "research/CLAIMS.md"
    claims = claims_path.read_text(encoding="utf-8")
    if "| CL-L163 |" in claims:
        raise SystemExit("CL-L163 already exists; refusing duplicate claim")
    write(claims_path, claims.rstrip() + """
| CL-L163 | In GOG AE 1.6.1179.0, the NIF parser registry maps NiNode to FUN_140d1e880, which installs NiNode vtable RVA 0x19AC3F0. Its +0x8 deleting-destructor thunk dispatches to primary destructor FUN_140d20350, which releases child objects through their own +0x8 slots and delegates to FUN_140d1d8f0. | supported (bounded build-attested parser registration and vtable trace) | [EV-0331] | This is only a candidate for PlayerCharacter +0x8F8's first-person skeleton resource. The exact NIF root/tree, child finalizers, and NiAVObject slot+0x128 target are unresolved; no Q64-H1/H2 result or AV11/AV12 exclusion follows. No Steam runtime or vanilla reproduction is established. |
""")

    mechanisms_path = ROOT / "research/MECHANISMS.md"
    mechanisms = mechanisms_path.read_text(encoding="utf-8")
    if "## M-0060 —" in mechanisms:
        raise SystemExit("M-0060 already exists; refusing duplicate mechanism")
    write(mechanisms_path, mechanisms.rstrip() + """

## M-0060 — Conditional NiNode finalizer candidate for +0x8F8 (Q-0064)

The GOG NIF parser registry maps the serialized name NiNode to FUN_140d1e880, which installs vtable RVA 0x19AC3F0. Slot +0x8 reaches a deleting-destructor thunk and primary NiNode destructor that final-releases child objects and delegates to NiAVObject cleanup [EV-0331]. The exact first-person skeleton asset root/subtree is not observed, child finalizers and the slot+0x128 callback remain dynamic, and no AV11/AV12 sink result follows. No OBJ-1 edge is supported. Claim CL-L163 -> M-0060.
""")

    graph_path = ROOT / "research/KNOWLEDGE_GRAPH.md"
    write(graph_path, graph_path.read_text(encoding="utf-8").rstrip() + """

EV-0331 maps the GOG NiNode parser and a conditional NiNode finalizer chain for PlayerCharacter +0x8F8's resource path. The exact NIF root and subtree remain unobserved; child +0x8 finalizers and a NiAVObject slot+0x128 callback remain dynamic. No edge to AV11/AV12 skill progress or OBJ-1 is added. Claim CL-L163 -> M-0060 [EV-0331].
""")

    contra_path = ROOT / "research/CONTRADICTIONS.md"
    contra = contra_path.read_text(encoding="utf-8")
    head = "## C-OBJ2-TRAP-DIRECT-ROUTE"
    start = contra.find(head)
    end = contra.find("\n## ", start + len(head))
    if start < 0:
        raise SystemExit("missing C-OBJ2-TRAP-DIRECT-ROUTE")
    if end < 0:
        end = len(contra)
    section = contra[start:end]
    section = section.replace("- **Evidence:** [EV-0330]", "- **Evidence:** [EV-0331], [EV-0330]", 1)
    section = section.replace(
        "the camera cleanup retains other unresolved indirect resource calls.",
        "the camera cleanup retains other unresolved indirect resource calls. EV-0331 maps a conditional NiNode parser/destructor candidate for +0x8F8, but does not establish the actual asset root or child types.",
        1,
    )
    write(contra_path, contra[:start] + section + contra[end:])

    index_path = ROOT / "experiments/README.md"
    write(index_path, index_path.read_text(encoding="utf-8").rstrip() + "\n\nEXP-0069 / EV-0331 maps a conditional NiNode finalizer candidate for PlayerCharacter +0x8F8. The exact first-person skeleton NIF root and child tree remain unobserved; Q-0064 remains active.\n")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(x for x in frontier["items"] if x.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0331"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L163"]))
    for hyp in item.get("hypotheses", []):
        hyp["evidence"] = list(dict.fromkeys([*hyp.get("evidence", []), "EV-0331"]))
    method = "EV-0331 maps only a conditional NiNode class candidate for +0x8F8; exact NIF root/tree and nested finalizers remain unknown. Continue independently at PlayerCharacter +0x9D0 using EV-0328's writer scan."
    item["methods"] = list(dict.fromkeys([*item.get("methods", []), method]))
    item["next_action"] = "Inspect EV-0328's +0x9D0 displacement capture and its nine writer candidates; attribute a store path to the PlayerCharacter receiver, identify the stored object's concrete vtable and final slot+0x8 target, then screen resolved descendants for AV11/AV12 skill progress. Keep +0x8F8's NiNode path conditional and preserve unknown asset/child types."
    frontier["session_next_action"] = item["next_action"]
    frontier["next_action"] = item["next_action"]
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False) + "\n")

    log = ROOT / "research/SESSION_LOG.md"
    with log.open("a", encoding="utf-8") as f:
        f.write(f"\n- {datetime.now(timezone.utc).isoformat(timespec='seconds')} transaction TX-20261017-0011 update: EV-0331 maps the GOG NiNode parser and a conditional finalizer for the +0x8F8 resource path. The exact NIF root/tree and dynamic child/property finalizers remain unknown; Q64-H1/H2 stay open. Next action: attribute PlayerCharacter +0x9D0's producer and finalizer.\n")
    print("registered EV-0331, CL-L163, M-0060, experiment EXP-0069, and Q-0064 links")
    print(f"note sha256={sha(note)}; capture manifest sha256={sha(manifest)}")


if __name__ == "__main__":
    main()
