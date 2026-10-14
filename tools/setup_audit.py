#!/usr/bin/env python3
"""Maintain the evidence-backed local setup audit checklist.

The prompt's checkboxes are parsed once into a JSON source of truth. Markdown
is rendered from that file so status summaries cannot drift from the ledger.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPT = ROOT / "session-brief" / "LOCAL_CODEX_FINAL_AUDIT_PROMPT.md"
JSON_PATH = ROOT / "migration" / "local_setup_checklist.json"
MD_PATH = ROOT / "migration" / "LOCAL_SETUP_CHECKLIST.md"
STATUSES = {
    "TODO",
    "IN_PROGRESS",
    "PASS",
    "FAIL",
    "BLOCKED_EXTERNAL",
    "NOT_APPLICABLE",
}
CRITERION = re.compile(r"^- \[ \] ([A-G]\d{2}) (.+)$")


def parse_prompt() -> list[dict[str, object]]:
    if not PROMPT.is_file():
        raise FileNotFoundError(f"audit prompt missing: {PROMPT.relative_to(ROOT)}")
    result = []
    for line in PROMPT.read_text(encoding="utf-8").splitlines():
        match = CRITERION.match(line)
        if match:
            result.append(
                {
                    "id": match.group(1),
                    "criterion": match.group(2).strip(),
                    "status": "TODO",
                    "evidence": "Not yet audited.",
                    "last_verified": None,
                }
            )
    ids = [entry["id"] for entry in result]
    if len(ids) != 86 or len(ids) != len(set(ids)):
        raise ValueError(f"expected 86 unique criteria; parsed {len(ids)}")
    return result


def load() -> dict[str, object]:
    return json.loads(JSON_PATH.read_text(encoding="utf-8"))


def save(data: dict[str, object]) -> None:
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def render(data: dict[str, object]) -> None:
    rows = data["criteria"]
    counts = {status: 0 for status in sorted(STATUSES)}
    for item in rows:
        counts[item["status"]] += 1
    lines = [
        "# Local Setup Checklist",
        "",
        f"Canonical machine-readable source: [`local_setup_checklist.json`](local_setup_checklist.json). Last rendered: {date.today().isoformat()}.",
        "",
        "Statuses require criterion-specific evidence. `PASS` requires a concrete test/result or source location; `BLOCKED_EXTERNAL` requires a diagnosed external prerequisite.",
        "",
        "## Summary",
        "",
        " | ".join(f"{key}: {value}" for key, value in counts.items()),
        "",
        "## Criteria",
        "",
        "| ID | Status | Criterion | Evidence | Verified |",
        "|---|---|---|---|---|",
    ]
    for item in rows:
        text = str(item["criterion"]).replace("|", "\\|")
        evidence = str(item["evidence"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {item['id']} | `{item['status']}` | {text} | {evidence} | {item['last_verified'] or '—'} |"
        )
    MD_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate(data: dict[str, object]) -> list[str]:
    errors = []
    rows = data.get("criteria")
    if not isinstance(rows, list) or len(rows) != 86:
        return ["criteria must be a list containing exactly 86 entries"]
    seen = set()
    for item in rows:
        if not isinstance(item, dict):
            errors.append("criterion entry must be an object")
            continue
        ident = item.get("id")
        if not isinstance(ident, str) or not re.fullmatch(r"[A-G]\d{2}", ident):
            errors.append(f"invalid criterion id: {ident!r}")
        elif ident in seen:
            errors.append(f"duplicate criterion id: {ident}")
        seen.add(ident)
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{ident}: invalid status {status!r}")
        evidence = item.get("evidence")
        if status in {"PASS", "FAIL", "BLOCKED_EXTERNAL", "NOT_APPLICABLE"} and (
            not isinstance(evidence, str) or not evidence.strip() or evidence == "Not yet audited."
        ):
            errors.append(f"{ident}: {status} requires criterion-specific evidence/reason")
        if item.get("last_verified") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(item["last_verified"])):
            errors.append(f"{ident}: last_verified must be YYYY-MM-DD")
    expected = {f"{letter}{n:02d}" for letter, nmax in zip("ABCDEFG", (10, 10, 16, 12, 12, 14, 12)) for n in range(1, nmax + 1)}
    if seen != expected:
        errors.append("criterion IDs do not match A01–G12 section counts")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    subs.add_parser("init", help="create the 86-item checklist from the audit prompt")
    subs.add_parser("render", help="render Markdown from the JSON source of truth")
    subs.add_parser("validate", help="validate IDs, statuses, evidence and dates")
    update = subs.add_parser("set", help="set one criterion status and evidence")
    update.add_argument("id")
    update.add_argument("status", choices=sorted(STATUSES))
    update.add_argument("evidence")
    update.add_argument("--verified", default=date.today().isoformat())
    args = parser.parse_args()

    if args.command == "init":
        if JSON_PATH.exists():
            parser.error(f"refusing to overwrite existing {JSON_PATH.relative_to(ROOT)}")
        data = {
            "schema_version": 1,
            "mission_prompt": "session-brief/LOCAL_CODEX_FINAL_AUDIT_PROMPT.md",
            "last_updated": date.today().isoformat(),
            "criteria": parse_prompt(),
        }
        save(data)
        render(data)
        print(f"initialized {len(data['criteria'])} criteria")
        return 0

    if not JSON_PATH.is_file():
        parser.error("checklist is not initialized; run init")
    data = load()
    if args.command == "set":
        matches = [item for item in data["criteria"] if item["id"] == args.id]
        if len(matches) != 1:
            parser.error(f"unknown criterion id: {args.id}")
        matches[0].update(status=args.status, evidence=args.evidence, last_verified=args.verified)
        data["last_updated"] = date.today().isoformat()
        save(data)
        render(data)
        print(f"updated {args.id} to {args.status}")
        return 0
    if args.command == "render":
        render(data)
        print(f"rendered {len(data['criteria'])} criteria")
        return 0
    errors = validate(data)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"valid: {len(data['criteria'])} unique criteria")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
