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
    "20261018T123610Z": ("memory_displacement_search", "scan", "0xB8", [
        "OFFSET_INSTRUCTION_COUNT=5654579", "OFFSET_ACCESS_COUNT=2747",
        "OFFSET_ACCESS_OUTPUT_LIMIT=2048", "OFFSET_MATCHED_FUNCTION_COUNT=1759",
        "OFFSET_SCAN_COMPLETE=true", "OFFSET_WRITER_ANALYSIS_COMPLETE=true"]),
    "20261018T123901Z": ("direct_call_edge_census", "rva", "0xB3FA20", [
        "INDIRECT_CALL_SITE=140b3faaf CALL qword ptr [RAX + 0xb8]",
        "XREF_CALL_EDGE=140e85a8f -> 140b3fa20"]),
    "20261018T124037Z": ("direct_call_edge_census", "rva", "0xB99380", [
        "INDIRECT_CALL_SITE=140b9941b CALL qword ptr [RAX + 0xb8]",
        "INCOMING_CALLER_FUNCTION_COUNT=0"]),
}

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate append: " + marker)
    write(path, old.rstrip() + "\n\n" + body.strip())

def main() -> None:
    evidence_path = ROOT / "research" / "EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0377" for row in evidence["items"]):
        raise SystemExit("EV-0377 already exists")
    captures, hashes = [], {}
    displayed_b_calls = []
    for stamp, (mode, key, value, markers) in SPECS.items():
        mp = GH / f"gog-query-{stamp}.meta.json"
        meta = json.loads(mp.read_text(encoding="utf-8"))
        out = ROOT / meta["artifacts"]["stdout"]
        checks = meta.get("checks", {})
        expected_field = {
            "scan": "requested_search_displacement",
            "rva": "requested_rva",
        }[key]
        valid = (
            meta.get("operation") == "existing_gog_project_read_only_query"
            and meta.get("analysis_distribution") == "GOG"
            and meta.get("analysis_binary_product_version") == "1.6.1179"
            and meta.get("analysis_binary_sha256") == BIN
            and meta.get("program") == "SkyrimSE.exe"
            and meta.get("program_executable_path_matches_gog_binary") is True
            and meta.get("query_mode") == mode
            and meta.get(expected_field, "").upper() == value.upper()
            and meta.get("ok") is True and meta.get("exit_code") == 0
            and meta.get("read_only") is True and meta.get("auto_analysis_disabled") is True
            and meta.get("import_attempted") is False and meta.get("overwrite_attempted") is False
            and meta.get("project_created") is False
            and bool(checks) and all(checks.values())
            and out.is_file() and sha(out) == meta.get("stdout_sha256")
        )
        if not valid:
            raise SystemExit("capture identity/policy/completion/hash failed: " + stamp)
        raw = out.read_text(encoding="utf-8", errors="replace")
        if any(marker not in raw for marker in markers):
            raise SystemExit("capture marker missing: " + stamp)
        if key == "scan":
            access_rows = [line for line in raw.splitlines() if "OFFSET_ACCESS=" in line]
            displayed_calls = [line for line in access_rows if re.search(r"instruction:.*\bCALL\b", line, re.I)]
            displayed_b_calls = [line for line in displayed_calls if re.search(r"rva:0xB[0-9A-Fa-f]{5}", line)]
            if len(access_rows) != 2048 or len(displayed_b_calls) != 2:
                raise SystemExit("unexpected access cap or physics-range call count")
        captures.append({
            "stamp": stamp, "query_mode": mode, "requested": value,
            "checks": checks, "stdout_sha256": meta["stdout_sha256"],
            "read_only": True, "auto_analysis_disabled": True,
        })
        for path in (mp, out):
            hashes[path.relative_to(ROOT).as_posix()] = sha(path)
        for rel in meta.get("artifacts", {}).values():
            path = ROOT / rel
            if path.is_file():
                hashes[path.relative_to(ROOT).as_posix()] = sha(path)
    if not any("rva:0xB3FAAF" in line for line in displayed_b_calls):
        raise SystemExit("broadphase callsite absent from scan output")
    if not any("rva:0xB9941B" in line for line in displayed_b_calls):
        raise SystemExit("cyclic transition callsite absent from scan output")

    note = TX / "EV-0377-note.md"
    write(note, f"""# EV-0377 — Bounded +0xB8 callsite screen

## Build and competing models

Three fresh identity-checked GOG AE 1.6.1179.0 queries used the configured existing Ghidra project through the strict dispatcher in read-only/no-analysis mode. Analysis binary SHA-256: {BIN}. H1 predicts a +0xB8 callsite uses the constructor-attested hkpWorld slot 23 and passes the exact ProcessTrapHit manager to the listener add method. H2 predicts same-offset calls use other dynamic interfaces. A concrete receiver vtable and argument flow are required to distinguish them.

## Direct observations

- The full analyzed-displacement scan examined 5,654,579 instructions and reports 2,747 +0xB8 accesses across 1,759 functions. It marks the scan and writer analyses complete, but prints only the first 2,048 access rows. The displayed rows contain two CALL instructions in the 0xB00000 region: 0x140B3FAAF and 0x140B9941B. The omitted rows prevent a whole-program negative [capture 20261018T123610Z].
- FUN_140b3fa20 contains CALL [RAX+0xB8] on the object loaded from param_1+0x88 and one direct caller, FUN_140e85590. That caller passes a slot+0x138 result into FUN_140b3fa20. The concrete receiver vtable and any connection to the ProcessTrapHit manager are unresolved [capture 20261018T123901Z].
- FUN_140b99380 labels its activity TtBSCyclicBlendTransitionGenerator::generate and conditionally calls slot +0xB8 on an object at param_1+0xA0 when param_1+0xA8 equals 2. It has zero analyzed direct incoming callers; its concrete receiver table and any relation to the ProcessTrapHit manager are unresolved [capture 20261018T124037Z].
- Neither exact context identifies the hkpWorld vtable at slot 23 or the manager argument passed through FUN_140b43a20 [EV-0360].

## Result, limits and no-edge rationale

The displayed physics-range candidates do not establish the required owner/argument link, so no causal edge from FUN_140b66f40 or FUN_140b56a80 to the ProcessTrapHit listener array is added. The 2,048-row cap means unprinted access sites remain unknown; this is not proof that no matching indirect call exists. No AV11/AV12 sink or armor-XP negative is established. Dynamic object classes on the cleanup fields remain data-selected, and Steam hit/protection/raw-AVSK telemetry is still unverified [EV-0331, EV-0375].

## Exact next action

Resume Q-0064 when a supported inspector can identify the exact first-person NIF root or verified runtime class telemetry is available. Trace only producer-backed slot+0x8 descendants to the AV11/AV12 skill sink, then run the clean Steam hit/protection/raw-AVSK discriminator. Continue static P0 research on the independent Q-0065 family comparison while those inputs are unavailable.
""")

    docs = {
        "README.md": "# EXP-0115 — Q64 slot +0xB8 callsite screen\n\nCompare candidate GOG +0xB8 indirect calls with the constructor-attested world listener method and exact ProcessTrapHit manager argument.\n",
        "hypothesis.md": "# Competing models\n\n- H1: a +0xB8 callsite invokes the hkpWorld slot 23 listener registration method on the ProcessTrapHit manager.\n- H2: the observed same-offset calls belong to other dynamic interface classes.\n",
        "protocol.md": "# Protocol\n\nRun the strict whole-program +0xB8 displacement scan and retain its completion markers and output cap. Inspect candidate callsites only with exact receiver provenance and caller arguments. Do not infer a world listener target from an offset match.\n",
        "expected-discriminants.md": "# Expected discriminants\n\nA concrete hkpWorld vtable at the callsite and an exact ProcessTrapHit manager argument support H1. A different producer-backed class supports H2 for that site. Unprinted scan rows and unresolved vtables leave the global question open.\n",
        "results.md": "# Results\n\nThe complete scan reports 2,747 +0xB8 accesses but caps printed rows at 2,048. Two displayed 0xB00000-range callsites resolve to FUN_140b3fa20 and FUN_140b99380; neither query identifies the ProcessTrapHit manager or hkpWorld slot 23. See EV-0377.\n",
        "implications.md": "# Implications\n\nNo listener-owner or AV11/AV12 edge is added. Preserve the output cap and unresolved dynamic targets; continue on another P0 line while exact asset/runtime class evidence is unavailable.\n",
    }
    for name, content in docs.items():
        write(EXP / name, content)
    hashes[note.relative_to(ROOT).as_posix()] = sha(note)
    hashes[Path(__file__).relative_to(ROOT).as_posix()] = sha(Path(__file__))
    for name in docs:
        p = EXP / name
        hashes[p.relative_to(ROOT).as_posix()] = sha(p)
    manifest = TX / "EV-0377-capture-manifest.json"
    write(manifest, json.dumps({"evidence_id": "EV-0377",
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BIN, "captures": captures,
        "displayed_physics_range_call_sites": [
            {"address": "0x140B3FAAF", "function": "FUN_140b3fa20"},
            {"address": "0x140B9941B", "function": "FUN_140b99380"}],
        "registered_local_hashes": hashes}, indent=2, ensure_ascii=False))
    hashes[manifest.relative_to(ROOT).as_posix()] = sha(manifest)

    evidence["items"].append({
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "edition": "AE", "modified_state": False, "id": "EV-0377", "kind": "native",
        "source": "Identity-checked GOG Ghidra +0xB8 displacement scan and exact candidate callsite queries.",
        "artifact": "private-local:.local/alignment/transactions/TX-20261017-0011/EV-0377-note.md",
        "sha256": sha(note),
        "runtime": f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
        "lane": "mechanism_inference",
        "tools": ["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
        "coverage": "Complete +0xB8 displacement scan with 2,048 printed-row cap; exact caller/decompilation queries for FUN_140b3fa20 and FUN_140b99380.",
        "result": "Two displayed physics-range callsites do not establish the hkpWorld slot-23 or ProcessTrapHit manager link. The output cap and unresolved receiver tables prevent a global negative.",
        "related_evidence": ["EV-0331", "EV-0347", "EV-0360", "EV-0364", "EV-0375", "EV-0376"],
        "local_hashes": hashes})
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research" / "CLAIMS.md", "| CL-L217 |",
        "| CL-L217 | The GOG AE 1.6.1179.0 +0xB8 displacement scan reports 2,747 accesses but prints 2,048 rows; two displayed 0xB00000-range callsites resolve to FUN_140b3fa20 and FUN_140b99380, whose exact queried receivers do not identify hkpWorld slot 23 or the ProcessTrapHit manager. | supported for displayed rows and queried callers | [EV-0377], [EV-0360] | The output cap and unresolved receiver tables leave unprinted callsites and indirect targets open; no global negative follows. |")
    append_once(ROOT / "research" / "CONTRADICTIONS.md",
        "## C-OBJ2-Q64-SLOT-B8-CALLSITE",
        """## C-OBJ2-Q64-SLOT-B8-CALLSITE — world listener method target

- **Model A:** a +0xB8 callsite invokes the constructor-attested hkpWorld slot 23 listener-registration method on the ProcessTrapHit manager.
- **Model B:** same-offset callsites dispatch to unrelated dynamic interfaces.
- **Evidence:** the displayed physics-range callsites resolve to a broadphase-shift object path and a cyclic-blend transition generator; neither exact query identifies the world table or manager [EV-0377].
- **Assessment:** neither model is selected. The scan prints only 2,048 of 2,747 accesses, and exact receiver tables remain unknown.
- **Discriminant:** a producer-backed hkpWorld receiver and exact manager argument at a concrete callsite supports Model A.""")
    append_once(ROOT / "research" / "KNOWLEDGE_GRAPH.md",
        "Q64 slot +0xB8 callsite no-edge rationale (EV-0377)",
        """### Q64 slot +0xB8 callsite no-edge rationale (EV-0377)

No edge is added from FUN_140b66f40 to the ProcessTrapHit manager. The displayed candidate calls do not identify hkpWorld slot 23 or the manager argument; the +0xB8 scan's 2,048-row output cap leaves other callsites unknown [CL-L217].""")

    fp = ROOT / "research" / "FRONTIER.json"
    frontier = json.loads(fp.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0064")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0377"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L217"]))
    for h in item.get("hypotheses", []):
        h["evidence"] = list(dict.fromkeys([*h.get("evidence", []), "EV-0377"]))
    item.setdefault("methods", []).append("EV-0377 screens the displayed +0xB8 physics callsites; exact receiver/argument evidence does not identify the hkpWorld listener method, and the 2,048-row output cap prevents a global negative.")
    item["next_action"] = "Resume Q-0064 when a supported inspector can identify the exact first-person NIF root or verified runtime class telemetry is available. Trace only producer-backed slot+0x8 descendants to the AV11/AV12 skill sink, then run the clean Steam hit/protection/raw-AVSK discriminator."
    write(fp, json.dumps(frontier, indent=2, ensure_ascii=False))

    append_once(ROOT / "STATE.md", "Q-0064 / EV-0377",
        "- Q-0064 / EV-0377: the +0xB8 scan reports 2,747 hits but prints 2,048 rows; two shown physics-range calls do not identify the hkpWorld listener method or ProcessTrapHit manager. Resume with exact dynamic resource/runtime class evidence.")
    append_once(ROOT / "ROADMAP.md", "EV-0377 +0xB8 listener callsite screen",
        "EV-0377 leaves the ProcessTrapHit listener method unlinked: displayed +0xB8 callsites have untyped/different receivers, and the scan output is capped. Resume after exact resource/runtime class evidence becomes available [CL-L217].")
    append_once(ROOT / "experiments" / "README.md", "EXP-0115 / EV-0377",
        "EXP-0115 / EV-0377 records a capped +0xB8 callsite scan and exact receiver screening for two displayed physics-range candidates.")
    print("Registered EV-0377 and CL-L217; no listener-owner edge is added and the capped scan is preserved.")
if __name__ == "__main__":
    main()
