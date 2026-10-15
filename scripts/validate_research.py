#!/usr/bin/env python3
"""Validate durable Skyrim AE evidence records and research-state links."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from .research_state import validate_frontier
except ImportError:
    from research_state import validate_frontier

ROOT = Path(__file__).resolve().parents[1]
LANES = {
    "offline", "diagnostic_intervention", "vanilla_candidate",
    "vanilla_reproduction", "mechanism_inference",
}
EVIDENCE_KINDS = {"record", "native", "runtime", "save", "log", "wiki", "discord", "tool", "legacy"}
EVIDENCE_ID = re.compile(r"EV-\d{4,}")
CLAIM_ID = re.compile(r"CL-[A-Z0-9-]+")
LEDGER_SECTIONS = {
    "MECHANISMS.md": re.compile(r"^##\s+(M-\d{4,})\b.*$", re.M),
    "GLITCHES.md": re.compile(r"^##\s+(G-\d{4,})\b.*$", re.M),
    "CONTRADICTIONS.md": re.compile(r"^##\s+(C-LEG-\d{4,})\b.*$", re.M),
}


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _validate_evidence(register: dict[str, Any], root: Path) -> tuple[list[str], set[str]]:
    errors: list[str] = []
    items = register.get("items")
    if register.get("schema_version") != 1 or not isinstance(items, list):
        return ["evidence register must have schema_version 1 and an items array"], set()
    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            errors.append("evidence entries must be objects")
            continue
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not EVIDENCE_ID.fullmatch(evidence_id):
            errors.append(f"invalid evidence ID: {evidence_id!r}")
            continue
        if evidence_id in by_id:
            errors.append(f"duplicate evidence ID: {evidence_id}")
        by_id[evidence_id] = item
        fields = (
            "kind", "source", "artifact", "sha256", "captured_utc",
            "edition", "runtime", "modified_state", "lane", "tools",
            "coverage", "result",
        )
        for field in fields:
            if field not in item:
                errors.append(f"{evidence_id}: missing {field}")
        if item.get("kind") not in EVIDENCE_KINDS:
            errors.append(f"{evidence_id}: invalid evidence kind")
        if item.get("lane") not in LANES:
            errors.append(f"{evidence_id}: invalid evidence lane")
        if item.get("edition") not in {"AE", "unknown"}:
            errors.append(f"{evidence_id}: edition must be AE or explicit unknown")
        if not isinstance(item.get("runtime"), str) or not item["runtime"].strip():
            errors.append(f"{evidence_id}: runtime must be a version or explicit unknown")
        if not isinstance(item.get("modified_state"), bool):
            errors.append(f"{evidence_id}: modified_state must be boolean")
        if not isinstance(item.get("tools"), list) or not item["tools"] or any(not isinstance(tool, str) or not tool.strip() for tool in item["tools"]):
            errors.append(f"{evidence_id}: tools must be a non-empty list of names/versions")
        for field in ("source", "coverage", "result"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                errors.append(f"{evidence_id}: {field} must be non-empty text")
        try:
            timestamp = datetime.fromisoformat(str(item.get("captured_utc", "")).replace("Z", "+00:00"))
            if timestamp.tzinfo is None:
                errors.append(f"{evidence_id}: captured_utc must include a timezone")
        except ValueError:
            errors.append(f"{evidence_id}: captured_utc must be ISO-8601")
        artifact = item.get("artifact")
        if not isinstance(artifact, str) or not artifact:
            errors.append(f"{evidence_id}: artifact must be a path or private-local reference")
        elif artifact.startswith("private-local:"):
            if not artifact.removeprefix("private-local:").strip():
                errors.append(f"{evidence_id}: private-local artifact must name a local artifact")
        else:
            artifact_path = Path(artifact)
            if artifact_path.is_absolute() or ".." in artifact_path.parts:
                errors.append(f"{evidence_id}: artifact must be relative or private-local")
            else:
                source = root / artifact_path
                if not source.is_file():
                    errors.append(f"{evidence_id}: artifact does not exist: {artifact}")
                elif isinstance(item.get("sha256"), str):
                    actual = hashlib.sha256(source.read_bytes()).hexdigest()
                    if actual != item["sha256"]:
                        errors.append(f"{evidence_id}: artifact SHA-256 mismatch")
        digest = item.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"{evidence_id}: sha256 must be 64 lowercase hex characters")
    return errors, set(by_id)


def _evidence_references(text: str) -> set[str]:
    return set(EVIDENCE_ID.findall(text))


def _validate_references(label: str, text: str, known: set[str]) -> list[str]:
    return [f"{label}: unknown evidence ID {ident}" for ident in sorted(_evidence_references(text) - known)]


def _validate_markdown_entities(root: Path, evidence_ids: set[str]) -> list[str]:
    """Validate the documented Markdown record shapes and their evidence links."""
    errors: list[str] = []
    claims_path = root / "research/CLAIMS.md"
    try:
        claims = claims_path.read_text(encoding="utf-8")
    except OSError:
        return ["missing research/CLAIMS.md"]
    header = "| ID | Claim | Status | Evidence IDs | Scope and open limit |"
    if header not in claims:
        errors.append("CLAIMS.md: expected the five-column claim schema header")
    claim_ids: set[str] = set()
    for line_number, line in enumerate(claims.splitlines(), 1):
        if not re.match(r"^\|\s*CL-", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        label = f"CLAIMS.md:{line_number}"
        if len(cells) != 5:
            errors.append(f"{label}: claim row must have five cells")
            continue
        ident = cells[0]
        if not CLAIM_ID.fullmatch(ident):
            errors.append(f"{label}: invalid claim ID {ident!r}")
        elif ident in claim_ids:
            errors.append(f"{label}: duplicate claim ID {ident}")
        claim_ids.add(ident)
        if any(not value for value in cells[1:]):
            errors.append(f"{label}: claim, status, evidence, and scope must be non-empty")
        references = _evidence_references(cells[3])
        if not references:
            errors.append(f"{label}: claim must cite at least one evidence ID")
        errors.extend(_validate_references(label, cells[3], evidence_ids))
    if not claim_ids:
        errors.append("CLAIMS.md: no claim records found")

    for filename, pattern in LEDGER_SECTIONS.items():
        path = root / "research" / filename
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            errors.append(f"missing research/{filename}")
            continue
        matches = list(pattern.finditer(text))
        if not matches:
            errors.append(f"{filename}: no entity sections found")
            continue
        identifiers: set[str] = set()
        for index, match in enumerate(matches):
            ident = match.group(1)
            label = f"{filename}:{ident}"
            if ident in identifiers:
                errors.append(f"{label}: duplicate entity ID")
            identifiers.add(ident)
            end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
            section = text[match.end():end].strip()
            refs = _evidence_references(section)
            if not section:
                errors.append(f"{label}: section body is empty")
            if not refs:
                errors.append(f"{label}: section must cite at least one evidence ID")
            errors.extend(_validate_references(label, section, evidence_ids))
            if filename == "CONTRADICTIONS.md":
                for field in ("Model A:", "Model B:", "Source:", "Discriminant:"):
                    if field not in section:
                        errors.append(f"{label}: contradiction schema requires {field}")

    experiment_dirs = sorted((root / "experiments").glob("EXP-*"))
    if not experiment_dirs:
        errors.append("experiments/: no experiment records found")
    legacy_rows: dict[str, list[dict[str, str]]] = {}
    provenance = root / "research" / "LEGACY_SOURCE_PROVENANCE.tsv"
    if provenance.is_file():
        try:
            with provenance.open(encoding="utf-8", newline="") as stream:
                for row in csv.DictReader(stream, delimiter="\t"):
                    retained = row.get("retained_reference", "")
                    if retained.startswith("experiments/EXP-"):
                        directory_name = Path(retained).parts[1]
                        legacy_rows.setdefault(directory_name, []).append(row)
        except (OSError, csv.Error) as exc:
            errors.append(f"legacy experiment provenance is unreadable: {type(exc).__name__}")
    for directory in experiment_dirs:
        label = directory.name
        if label in legacy_rows:
            rows = legacy_rows[label]
            indexed = {row.get("retained_reference", ""): row for row in rows}
            for path in sorted(directory.glob("*.md")):
                relative = path.relative_to(root).as_posix()
                row = indexed.get(relative)
                if row is None:
                    errors.append(f"{label}: historical file lacks a provenance row: {path.name}")
                    continue
                expected_hash = row.get("retained_sha256", "")
                actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
                if not expected_hash or expected_hash != actual_hash:
                    errors.append(f"{label}: retained historical file hash mismatch: {path.name}")
            refs = {row.get("evidence_id", "") for row in rows} - {"", "—"}
            if not refs:
                errors.append(f"{label}: historical experiment provenance has no evidence ID")
            for evidence_id in refs:
                errors.extend(_validate_references(label, f"[{evidence_id}]", evidence_ids))
            continue
        paths = [directory / name for name in ("README.md", "hypothesis.md", "protocol.md", "expected-discriminants.md", "results.md")]
        missing = [path.name for path in paths if not path.is_file()]
        if missing:
            errors.append(f"{label}: missing experiment record files {', '.join(missing)}")
            continue
        contents = {path.name: path.read_text(encoding="utf-8") for path in paths}
        hypothesis = contents["hypothesis.md"]
        if not re.search(r"\bH1\b", hypothesis) or not re.search(r"\bH2\b", hypothesis):
            errors.append(f"{label}: hypothesis schema requires rival H1 and H2 models")
        combined = "\n".join(contents.values())
        refs = _evidence_references(combined)
        if not refs:
            errors.append(f"{label}: experiment bundle must cite at least one evidence ID")
        errors.extend(_validate_references(label, combined, evidence_ids))
    return errors


def validate(root: Path = ROOT) -> list[str]:
    try:
        frontier = _read(root / "research/FRONTIER.json")
        register = _read(root / "research/EVIDENCE.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot read frontier/evidence JSON: {exc}"]
    errors, evidence_ids = _validate_evidence(register, root)
    errors.extend(validate_frontier(frontier, evidence_ids))
    errors.extend(_validate_markdown_entities(root, evidence_ids))
    return errors


if __name__ == "__main__":
    problems = validate()
    print("RESEARCH DATA " + ("FAIL" if problems else "PASS"))
    for problem in problems:
        print(f" - {problem}")
    raise SystemExit(bool(problems))
