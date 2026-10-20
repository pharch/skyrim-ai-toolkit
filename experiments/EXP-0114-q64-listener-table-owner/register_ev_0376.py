#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local" / "ghidra"
TX = ROOT / ".local" / "alignment" / "transactions" / "TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BIN = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
SPECS = {
    "20261018T122319Z": ("direct_call_edge_census", "rva", "0xB56A80", None,
        ["INCOMING_CALLER_FUNCTION_COUNT=0",
         "OUTGOING_DIRECT_CALL_EDGE=140b56ad9 -> 140b3db50", "XREF_ANY_COUNT=2",
         "XREF_ANY=141973f20 -> 140b56a80 type=DATA",
         "XREF_ANY=1436999d4 -> 140b56a80 type=DATA"]),
    "20261018T122442Z": ("pointer_table_query", "table", "0x1973F18", 12,
        ["POINTER_TABLE_XREF_SCAN_COMPLETE=true",
         "POINTER_TABLE_ENTRY=index:1 address:141973f20 value:0x140B56A80"]),
    "20261018T122659Z": ("address_context_query", "address", "0x1973F18", None,
        ["ADDRESS_TARGET_XREF_COUNT=0", "ADDRESS_FUNCTION_LOOKUP=<no-function>",
         "ADDRESS_CONTEXT_INSTRUCTION_COUNT=0"]),
    "20261018T122811Z": ("address_context_query", "address", "0x36999D4", None,
        ["ADDRESS_TARGET_XREF_COUNT=0", "ADDRESS_FUNCTION_LOOKUP=<no-function>",
         "ADDRESS_CONTEXT_INSTRUCTION_COUNT=0"]),
}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p: Path, content: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.rstrip() + "\n", encoding="utf-8")

def append_once(p: Path, marker: str, body: str) -> None:
    old = p.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate append: " + marker)
    write(p, old.rstrip() + "\n\n" + body.strip())

def main() -> None:
    evidence_path = ROOT / "research" / "EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0376" for row in evidence["items"]):
        raise SystemExit("EV-0376 already exists")
    captures, hashes = [], {}
    found_indices = None
    for stamp, (mode, key, value, count, markers) in SPECS.items():
        mp = GH / f"gog-query-{stamp}.meta.json"
        meta = json.loads(mp.read_text(encoding="utf-8"))
        out = ROOT / meta["artifacts"]["stdout"]
        checks = meta.get("checks", {})
        identity = (
            meta.get("operation") == "existing_gog_project_read_only_query"
            and meta.get("analysis_distribution") == "GOG"
            and meta.get("analysis_binary_product_version") == "1.6.1179"
            and meta.get("analysis_binary_sha256") == BIN
            and meta.get("program") == "SkyrimSE.exe"
            and meta.get("program_executable_path_matches_gog_binary") is True
            and meta.get("query_mode") == mode and meta.get("ok") is True
            and meta.get("exit_code") == 0 and meta.get("read_only") is True
            and meta.get("auto_analysis_disabled") is True
            and meta.get("import_attempted") is False
            and meta.get("overwrite_attempted") is False
            and meta.get("project_created") is False
            and bool(checks) and all(checks.values())
            and out.is_file() and sha(out) == meta.get("stdout_sha256")
        )
        if key == "rva":
            identity = identity and meta.get("requested_rva", "").upper() == value.upper()
        elif key == "table":
            identity = identity and meta.get("requested_pointer_table_rva", "").upper() == value.upper()
            identity = identity and meta.get("requested_pointer_count") == count
        else:
            identity = identity and meta.get("requested_address_rva", "").upper() == value.upper()
        if not identity:
            raise SystemExit("capture identity, policy, completion or hash failed: " + stamp)
        raw = out.read_text(encoding="utf-8", errors="replace")
        if any(marker not in raw for marker in markers):
            raise SystemExit("capture marker missing: " + stamp)
        row = {"stamp": stamp, "query_mode": mode, "checks": checks,
               "stdout_sha256": meta["stdout_sha256"], "read_only": True,
               "auto_analysis_disabled": True}
        row["requested_" + key] = value
        if count is not None:
            row["requested_pointer_count"] = count
            indices = sorted({int(m.group(1)) for m in re.finditer(
                r"POINTER_TABLE_XREF=entry_index:(\d+)", raw)})
            found_indices = indices
            row["referenced_entry_indices"] = indices
        captures.append(row)
        for p in (mp, out):
            hashes[p.relative_to(ROOT).as_posix()] = sha(p)
        for rel in meta.get("artifacts", {}).values():
            p = ROOT / rel
            if p.is_file():
                hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    if found_indices != [3, 6, 11]:
        raise SystemExit("unexpected table entry reference indices: " + str(found_indices))

    note = TX / "EV-0376-note.md"
    write(note, f"""# EV-0376 — Listener add helper data references remain unowned

## Build and method

Four identity-checked queries used the configured existing GOG Skyrim AE 1.6.1179.0 Ghidra project through the strict dispatcher in read-only/no-analysis mode. Analysis binary SHA-256: {BIN}. Queries covered FUN_140b56a80's direct-call census, a bounded 12-qword window at RVA 0x1973F18, and address context at that window base and the reported metadata cell. All identity, completion, read-only and no-analysis checks passed. GOG addresses do not transfer to installed Steam AE 1.6.1170.0.

## Competing models and predictions

- H1: FUN_140b56a80 registers a listener on the ProcessTrapHit manager path. A producer-backed table owner or resolved callsite must pass the same manager used by FUN_140b43a20 as param_2.
- H2: the references are data-only or belong to another registration family. No ProcessTrapHit link follows without a concrete caller and matching argument.
- A function-pointer value or data reference is not an invocation; an unresolved indirect call remains unknown.

## Direct observations

- FUN_140b56a80 has one outgoing direct call to FUN_140b3db50 and zero analyzed incoming direct-call edges/caller functions. It checks param_1+0x60 in param_2's +0x1D8/+0x1E0 array and appends only if absent [capture 20261018T122319Z].
- The bounded qword window at RVA 0x1973F18 contains FUN_140b56a80 at 0x141973F20. Its reference scan reports entries 3, 6 and 11, not entry 1. The exact window base at 0x141973F18 has zero analyzed references and no function boundary [captures 20261018T122442Z, 20261018T122659Z].
- The function census reports two DATA references to FUN_140b56a80: 0x141973F20 and a source-less metadata word at 0x1436999D4. Address context for RVA 0x36999D4 has no incoming analyzed reference or function boundary. Neither reference identifies an executable callsite or table owner [captures 20261018T122319Z, 20261018T122811Z].
- The ProcessTrapHit trace separately shows FUN_140b43a20 passing its manager argument through the world-listener dispatcher; this candidate's param_2 is not linked to that exact value [EV-0360].

## Result and limits

These queries do not establish a ProcessTrapHit call to FUN_140b56a80. They narrow this branch to two raw DATA references without an analyzed direct caller or identified owner. This does not prove the function is unreachable; dynamic or untyped indirect use remains possible. No AV11/AV12 sink, global armor-XP negative, or OBJ-1 edge is established. The exact first-person NIF root is not available through the local PEX-only archive helper [EV-0331]; continue with another producer-backed static branch.

## Exact next action

Run the complete analyzed-displacement scan for +0xB8, the constructor-attested hkpWorld candidate vtable slot 23 containing FUN_140b66f40. Inspect only callsites whose receiver provenance identifies the same manager passed through FUN_140b43a20. A matching receiver and argument would establish the owner link; otherwise retain this listener route as unlinked and return to the remaining cleanup sources.
""")

    docs = {
        "README.md": "# EXP-0114 — Listener table owner and callsite\n\nTest whether the unowned FUN_140b56a80 data references identify an active ProcessTrapHit registration route.\n",
        "hypothesis.md": "# Competing models\n\n- H1: FUN_140b56a80 is active on the ProcessTrapHit manager route.\n- H2: its function-pointer values are data references without a demonstrated owner or callsite on that route.\n",
        "protocol.md": "# Protocol\n\nUse the identity-checked GOG project in read-only/no-analysis mode. Census direct incoming and outgoing edges, inspect only the bounded pointer window containing the function value, and query the exact reported data-cell addresses. Require a concrete owner/callsite and the exact manager argument before linking this helper to ProcessTrapHit.\n",
        "expected-discriminants.md": "# Expected discriminants\n\nA concrete callsite using the ProcessTrapHit manager as the helper array owner supports H1. Data-only references with no owner or callsite leave H1 unconfirmed and support no causal edge; they do not prove unreachability.\n",
        "results.md": "# Results\n\nFUN_140b56a80 has one direct outgoing call and no analyzed direct incoming caller. Two DATA references point to it, but the candidate qword-window base and metadata cell have no analyzed incoming references, and no owner/callsite is identified. This narrows the table branch without resolving possible indirect use. See EV-0376.\n",
        "implications.md": "# Implications\n\nNo ProcessTrapHit registration or AV11/AV12 edge is added. Continue at the constructor-attested vtable slot +0xB8 callsite census, then preserve unknown indirect targets and the separate Steam hit/protection/raw-AVSK test.\n",
    }
    for name, content in docs.items():
        write(EXP / name, content)
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    for name in docs:
        p = EXP / name
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    manifest = TX / "EV-0376-capture-manifest.json"
    write(manifest, json.dumps({"evidence_id": "EV-0376",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BIN, "captures": captures,
        "registered_local_hashes": hashes}, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0376", "kind": "native",
        "source": "Identity-checked GOG Ghidra direct-call and data-reference queries for candidate listener add helper FUN_140b56a80.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0376-note.md",
        "sha256": sha(note),
        "runtime": f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "FUN_140b56a80 direct-call census; qword window at RVA 0x1973F18; address-context queries at 0x1973F18 and 0x36999D4.",
        "result": "No analyzed direct caller or table owner links FUN_140b56a80 to the ProcessTrapHit manager. Two DATA references remain untyped; indirect execution is not excluded.",
        "related_evidence": ["EV-0331", "EV-0347", "EV-0360", "EV-0364", "EV-0375"],
        "local_hashes": hashes})
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research" / "CLAIMS.md", "| CL-L216 |",
        "| CL-L216 | In the captured GOG AE 1.6.1179.0 analyzed listing, FUN_140b56a80 has one outgoing direct call to FUN_140b3db50 and zero analyzed incoming direct-call edges; two raw DATA references point to it, but neither is resolved to an executable callsite or ProcessTrapHit manager owner. | supported for the captured static query scope | [EV-0376], [EV-0360] | Dynamic or untyped indirect invocation remains possible; no global reachability negative follows. |")
    append_once(ROOT / "research" / "CONTRADICTIONS.md",
        "## C-OBJ2-Q64-IDEMPOTENT-LISTENER-OWNER",
        """## C-OBJ2-Q64-IDEMPOTENT-LISTENER-OWNER — candidate add helper callsite

- **Model A:** FUN_140b56a80 registers a listener on the ProcessTrapHit-selected manager.
- **Model B:** its data references are unrelated to the captured ProcessTrapHit route.
- **Evidence:** the direct-call census finds zero analyzed direct callers; the qword and metadata references lack an identified code consumer or owner [EV-0376]. The ProcessTrapHit dispatcher path is separately mapped [EV-0360].
- **Assessment:** neither model is selected. No exact manager argument or executable callsite is established; indirect use remains possible.
- **Discriminant:** a producer-backed callsite must pass the same manager argument used by FUN_140b43a20 to support Model A.""")
    append_once(ROOT / "research" / "KNOWLEDGE_GRAPH.md",
        "Q64 listener add helper no-edge rationale (EV-0376)",
        """### Q64 listener add helper no-edge rationale (EV-0376)

No causal edge is added from FUN_140b56a80 to the ProcessTrapHit manager or the AV11/AV12 skill-progress sink: the bounded direct-call census has no incoming caller, and its two raw DATA references identify no executable consumer. This is a bounded absence of an identified edge, not proof that dynamic invocation is impossible [CL-L216].""")

    fp = ROOT / "research" / "FRONTIER.json"
    frontier = json.loads(fp.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0376"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L216"]))
    for h in item.get("hypotheses", []):
        h["evidence"] = list(dict.fromkeys([*h.get("evidence", []), "EV-0376"]))
    item.setdefault("methods", []).append("EV-0376 narrows the candidate idempotent listener add helper to unowned DATA references; no ProcessTrapHit callsite is established.")
    item["next_action"] = "Run the complete analyzed-displacement scan for +0xB8, the constructor-attested hkpWorld candidate vtable slot 23 containing FUN_140b66f40. Inspect only callsites whose receiver provenance identifies the same manager passed through FUN_140b43a20. A matching receiver and argument would establish the owner link; otherwise retain this listener route as unlinked and return to the remaining cleanup sources."
    write(fp, json.dumps(frontier, indent=2, ensure_ascii=False))

    append_once(ROOT / "STATE.md", "Q-0064 / EV-0376",
        "- Q-0064 / EV-0376 records two unowned DATA references to FUN_140b56a80 and no analyzed direct caller or ProcessTrapHit manager link. Continue with the +0xB8 listener registration callsite census; unresolved indirect use remains open.")
    append_once(ROOT / "ROADMAP.md", "EV-0376 candidate listener add helper",
        "EV-0376 leaves the candidate idempotent listener helper unowned: no analyzed direct caller or ProcessTrapHit manager link is identified. Continue with the constructor-attested +0xB8 vtable slot census [CL-L216].")
    append_once(ROOT / "experiments" / "README.md", "EXP-0114 / EV-0376",
        "EXP-0114 / EV-0376 bounds the unowned FUN_140b56a80 data references and selects an exact +0xB8 callsite census.")
    print("Registered EV-0376 and CL-L216; preserved the no-edge rationale and selected the +0xB8 callsite census.")

if __name__ == "__main__":
    main()
