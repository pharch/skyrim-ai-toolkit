#!/usr/bin/env python3
"""Validate and update durable Skyrim research transactions and checkpoints."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
STATUSES = {
    "open",
    "in_progress",
    "awaiting_user_test",
    "blocked_tool",
    "blocked_environment",
    "completed",
    "falsified",
    "superseded",
}
TERMINAL = {"completed", "falsified", "superseded"}
TRANSITIONS = {
    "open": {"in_progress", "awaiting_user_test", "blocked_tool", "blocked_environment"},
    "in_progress": {
        "open", "awaiting_user_test", "blocked_tool", "blocked_environment",
        "completed", "falsified",
    },
    "awaiting_user_test": {"open", "in_progress", "blocked_environment"},
    "blocked_tool": {"open", "in_progress", "blocked_environment"},
    "blocked_environment": {"open", "in_progress", "awaiting_user_test"},
    "completed": {"superseded"},
    "falsified": {"superseded"},
    "superseded": set(),
}
HYPOTHESIS_STATES = {"proposed", "supported", "falsified", "superseded"}
ID_PATTERN = re.compile(r"[A-Z]+-\d{4,}")
EVIDENCE_PATTERN = re.compile(r"EV-\d{4,}")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate_frontier(frontier: dict[str, Any], evidence_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if frontier.get("schema_version") != 3:
        errors.append("frontier schema_version must be 3")
    target = frontier.get("target")
    if not isinstance(target, dict) or target.get("edition") != "AE":
        errors.append("frontier target edition must be AE")
    items = frontier.get("items")
    if not isinstance(items, list) or not items:
        return errors + ["frontier must contain at least one research item"]

    by_id: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            errors.append("frontier entries must be objects")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not ID_PATTERN.fullmatch(item_id):
            errors.append(f"invalid frontier ID: {item_id!r}")
            continue
        if item_id in by_id:
            errors.append(f"duplicate frontier ID: {item_id}")
        by_id[item_id] = item
        for field in (
            "objective", "kind", "status", "question", "hypotheses", "methods",
            "blocked_by", "evidence", "priority", "information_gain",
            "next_action", "linked_claims", "successors", "attempts",
        ):
            if field not in item:
                errors.append(f"{item_id}: missing {field}")
        status = item.get("status")
        if status not in STATUSES:
            errors.append(f"{item_id}: invalid status {status!r}")
        for score in ("priority", "information_gain"):
            value = item.get(score)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
                errors.append(f"{item_id}: {score} must be a number from 0 to 1")
        if not isinstance(item.get("next_action"), str) or not item["next_action"].strip():
            errors.append(f"{item_id}: next_action must be actionable text")
        for field in ("methods", "blocked_by", "evidence", "linked_claims", "successors", "attempts"):
            if not isinstance(item.get(field), list):
                errors.append(f"{item_id}: {field} must be an array")
        hypotheses = item.get("hypotheses")
        if not isinstance(hypotheses, list) or len(hypotheses) < 2:
            errors.append(f"{item_id}: at least two competing hypotheses are required")
        else:
            hypothesis_ids: set[str] = set()
            for hypothesis in hypotheses:
                if not isinstance(hypothesis, dict):
                    errors.append(f"{item_id}: hypotheses must be objects")
                    continue
                hid = hypothesis.get("id")
                if not isinstance(hid, str) or not hid.strip() or hid in hypothesis_ids:
                    errors.append(f"{item_id}: hypothesis IDs must be non-empty and unique")
                else:
                    hypothesis_ids.add(hid)
                for field in ("model", "predicted_discriminant", "status"):
                    if not isinstance(hypothesis.get(field), str) or not hypothesis[field].strip():
                        errors.append(f"{item_id}: hypothesis {hid!r} needs {field}")
                if hypothesis.get("status") not in HYPOTHESIS_STATES:
                    errors.append(f"{item_id}: hypothesis {hid!r} has invalid status")
                if hypothesis.get("status") in {"supported", "falsified", "superseded"}:
                    linked = hypothesis.get("evidence", [])
                    if not isinstance(linked, list) or not linked:
                        errors.append(f"{item_id}: resolved hypothesis {hid!r} needs evidence")
                    else:
                        for evidence_id in linked:
                            if evidence_id not in evidence_ids:
                                errors.append(f"{item_id}: hypothesis {hid!r} cites unknown evidence {evidence_id}")
        for evidence_id in item.get("evidence", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{item_id}: unknown evidence ID {evidence_id}")
        if status in TERMINAL:
            decision = item.get("decision")
            if not isinstance(decision, dict):
                errors.append(f"{item_id}: terminal investigation requires a decision record")
            else:
                for field in ("summary", "cross_domain_assessment"):
                    if not isinstance(decision.get(field), str) or not decision[field].strip():
                        errors.append(f"{item_id}: decision requires {field}")
                if not decision.get("evidence"):
                    errors.append(f"{item_id}: terminal decision requires evidence")
                for evidence_id in decision.get("evidence", []):
                    if evidence_id not in evidence_ids:
                        errors.append(f"{item_id}: decision cites unknown evidence {evidence_id}")
                if not decision.get("successors"):
                    errors.append(f"{item_id}: terminal decision must generate or link successor questions")

    for item_id, item in by_id.items():
        for field, label in (("blocked_by", "dependency"), ("successors", "successor")):
            for linked_id in item.get(field, []):
                if linked_id not in by_id:
                    errors.append(f"{item_id}: unknown {label} ID {linked_id}")
                    if label == "dependency":
                        errors.append(f"{item_id}: unknown dependency {linked_id}")
        for claim_id in item.get("linked_claims", []):
            if not isinstance(claim_id, str) or not claim_id.strip():
                errors.append(f"{item_id}: linked_claims contains an invalid claim ID")
        attempts = item.get("attempts", [])
        if isinstance(attempts, list):
            seen_actions: dict[str, dict[str, Any]] = {}
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    errors.append(f"{item_id}: attempts must contain objects")
                    continue
                action = attempt.get("action_key")
                if not isinstance(action, str) or not action.strip():
                    errors.append(f"{item_id}: attempt requires action_key")
                    continue
                previous = seen_actions.get(action)
                if previous and not attempt.get("new_discriminant"):
                    errors.append(f"{item_id}: repeated action {action!r} lacks a new discriminant")
                seen_actions[action] = attempt

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item_id: str) -> None:
        if item_id in visiting:
            errors.append(f"cyclic frontier dependency at {item_id}")
            return
        if item_id in visited:
            return
        visiting.add(item_id)
        for dependency in by_id[item_id].get("blocked_by", []):
            if dependency in by_id:
                visit(dependency)
        visiting.remove(item_id)
        visited.add(item_id)

    for item_id in by_id:
        visit(item_id)
    return errors


def transition_item(
    frontier: dict[str, Any],
    item_id: str,
    new_status: str,
    *,
    evidence_ids: list[str] | None = None,
    decision: dict[str, Any] | None = None,
    available_evidence: set[str] | None = None,
) -> None:
    items = frontier.get("items", [])
    item = next((entry for entry in items if entry.get("id") == item_id), None)
    if item is None:
        raise ValueError(f"unknown frontier item: {item_id}")
    old_status = item.get("status")
    if new_status not in TRANSITIONS.get(old_status, set()):
        raise ValueError(f"invalid status transition: {old_status} -> {new_status}")
    evidence_ids = evidence_ids or []
    known = available_evidence or set()
    missing = [evidence_id for evidence_id in evidence_ids if evidence_id not in known]
    if missing:
        raise ValueError(f"unknown evidence IDs: {', '.join(missing)}")
    if new_status in TERMINAL:
        if not decision:
            raise ValueError(f"{new_status} requires a decision record")
        required = ("summary", "cross_domain_assessment", "successors")
        if any(not decision.get(field) for field in required):
            raise ValueError(f"{new_status} requires summary, cross_domain_assessment and successors")
        if not evidence_ids:
            raise ValueError(f"{new_status} requires at least one evidence ID")
        successor_ids = {entry.get("id") for entry in items}
        if any(successor not in successor_ids for successor in decision["successors"]):
            raise ValueError("decision contains an unknown successor frontier ID")
        item["decision"] = {**decision, "evidence": list(evidence_ids), "closed_utc": utc_now()}
        item["successors"] = list(decision["successors"])
    if evidence_ids:
        item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), *evidence_ids]))
    item["status"] = new_status


def ready_items(frontier: dict[str, Any]) -> list[dict[str, Any]]:
    items = frontier.get("items", [])
    by_id = {item.get("id"): item for item in items}
    ready = []
    for item in items:
        if item.get("status") not in {"open", "in_progress"}:
            continue
        dependencies = item.get("blocked_by", [])
        if all(by_id.get(dep, {}).get("status") in TERMINAL for dep in dependencies):
            ready.append(item)
    return sorted(
        ready,
        key=lambda item: (
            item.get("priority", 0),
            item.get("information_gain", 0),
            item.get("id", ""),
        ),
        reverse=True,
    )


def record_attempt(
    item: dict[str, Any],
    action_key: str,
    outcome: str,
    *,
    evidence_ids: list[str] | None = None,
    new_discriminant: str = "",
) -> None:
    attempts = item.setdefault("attempts", [])
    previous = [attempt for attempt in attempts if attempt.get("action_key") == action_key]
    known_evidence = {
        evidence_id
        for attempt in previous
        for evidence_id in attempt.get("evidence", [])
    }
    has_new_evidence = bool(set(evidence_ids or []) - known_evidence)
    if previous and not new_discriminant.strip() and not has_new_evidence:
        raise ValueError("repeating an action requires new evidence or a new predicted discriminant")
    attempts.append({
        "action_key": action_key,
        "outcome": outcome,
        "evidence": list(evidence_ids or []),
        "new_discriminant": new_discriminant.strip() or None,
        "recorded_utc": utc_now(),
    })


def recover_checkpoint(recovery: dict[str, Any]) -> dict[str, Any]:
    if recovery.get("status") != "running":
        return recovery
    next_action = recovery.get("next_action")
    if not isinstance(next_action, str) or not next_action.strip():
        raise ValueError("running checkpoint lacks an actionable next_action")
    return {
        **recovery,
        "status": "interrupted",
        "interrupted_utc": utc_now(),
        "resume_action": (
            "Inspect the recorded raw artifacts and durable-state diff; do not "
            "infer completion from interruption. Resume from next_action."
        ),
    }


def validate_repository(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    try:
        frontier = read_json(root / "research/FRONTIER.json")
        evidence = read_json(root / "research/EVIDENCE.json")
        recovery = read_json(root / "research/RECOVERY.json")
        transactions = read_json(root / "research/TRANSACTIONS.json")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [f"cannot read research state: {exc}"]
    evidence_ids = {
        entry.get("id") for entry in evidence.get("items", [])
        if isinstance(entry, dict) and isinstance(entry.get("id"), str)
    }
    errors.extend(validate_frontier(frontier, evidence_ids))
    from scripts.research_transactions import validate_transaction_ledger

    errors.extend(validate_transaction_ledger(transactions, recovery, evidence_ids))
    if recovery.get("schema_version") != 2:
        errors.append("recovery schema_version must be 2")
    if recovery.get("status") not in {"idle", "running", "interrupted", "resumable"}:
        errors.append("recovery status is invalid")
    if not isinstance(recovery.get("next_action"), str) or not recovery["next_action"].strip():
        errors.append("recovery next_action must be actionable")
    if not isinstance(recovery.get("artifacts"), list):
        errors.append("recovery artifacts must be an array")
    template = root / "experiments/TRANSACTION_TEMPLATE.md"
    if not template.is_file():
        errors.append("missing experiments/TRANSACTION_TEMPLATE.md")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    validate = subcommands.add_parser("validate", help="validate frontier, evidence links, transactions, and recovery state")
    validate.add_argument("--root", type=Path, default=ROOT)
    recover = subcommands.add_parser("recover", help="mark a running transaction interrupted")
    recover.add_argument("--root", type=Path, default=ROOT)
    begin = subcommands.add_parser("begin", help="begin a validated frontier transaction")
    begin.add_argument("--root", type=Path, default=ROOT)
    begin.add_argument("--transaction-id", required=True)
    begin.add_argument("--frontier-id", required=True)
    begin.add_argument("--next-action", required=True)
    update = subcommands.add_parser("update", help="append a transaction observation and checkpoint")
    update.add_argument("--root", type=Path, default=ROOT)
    update.add_argument("--transaction-id", required=True)
    update.add_argument("--action-key", required=True)
    update.add_argument("--outcome", required=True)
    update.add_argument("--next-action", required=True)
    update.add_argument("--evidence", action="append", default=[])
    update.add_argument("--artifact", action="append", default=[])
    update.add_argument("--new-discriminant", default="")
    complete = subcommands.add_parser("complete", help="complete one transaction and select the next ready item")
    complete.add_argument("--root", type=Path, default=ROOT)
    complete.add_argument("--transaction-id", required=True)
    complete.add_argument("--summary", required=True)
    complete.add_argument("--cross-domain-assessment", required=True)
    complete.add_argument("--evidence", action="append", default=[])
    complete.add_argument("--artifact", action="append", default=[])
    block = subcommands.add_parser("block", help="block one line and automatically select an independent item")
    block.add_argument("--root", type=Path, default=ROOT)
    block.add_argument("--transaction-id", required=True)
    block.add_argument("--blocker", required=True)
    block.add_argument("--blocker-status", choices=("blocked_tool", "blocked_environment"), required=True)
    block.add_argument("--evidence", action="append", required=True)
    block.add_argument("--artifact", action="append", default=[])
    resume = subcommands.add_parser("resume", help="resume an interrupted transaction in a new process")
    resume.add_argument("--root", type=Path, default=ROOT)
    resume.add_argument("--transaction-id", required=True)
    args = parser.parse_args(argv)
    if args.command == "validate":
        errors = validate_repository(args.root)
        for error in errors:
            print(f"FAIL {error}")
        if not errors:
            print("PASS research frontier, evidence links, and recovery state")
        return 1 if errors else 0
    from scripts.research_transactions import (
        begin_transaction,
        block_transaction,
        complete_transaction,
        recover_transaction,
        resume_transaction,
        update_transaction,
    )

    try:
        if args.command == "recover":
            recovery = recover_transaction(args.root)
            print(f"{recovery['status']}: {recovery.get('resume_action', 'checkpoint unchanged')}")
        elif args.command == "begin":
            transaction = begin_transaction(args.root, args.transaction_id, args.frontier_id, args.next_action)
            print(f"running: {transaction['id']} on {transaction['frontier_id']}")
        elif args.command == "update":
            transaction = update_transaction(
                args.root, args.transaction_id, action_key=args.action_key,
                outcome=args.outcome, next_action=args.next_action,
                evidence_ids=args.evidence, artifacts=args.artifact,
                new_discriminant=args.new_discriminant,
            )
            print(f"updated: {transaction['id']}; next action: {transaction['next_action']}")
        elif args.command == "complete":
            result = complete_transaction(
                args.root, args.transaction_id, summary=args.summary,
                cross_domain_assessment=args.cross_domain_assessment,
                evidence_ids=args.evidence, artifacts=args.artifact,
            )
            print(f"completed: {args.transaction_id}; next frontier {result['next_item']['id']}: {result['next_item']['next_action']}")
        elif args.command == "block":
            result = block_transaction(
                args.root, args.transaction_id, blocker=args.blocker,
                blocker_status=args.blocker_status, evidence_ids=args.evidence,
                artifacts=args.artifact,
            )
            print(f"{args.blocker_status}: {args.transaction_id}; independently selected {result['next_item']['id']}: {result['next_item']['next_action']}")
        elif args.command == "resume":
            transaction = resume_transaction(args.root, args.transaction_id)
            print(f"running: resumed {transaction['id']}; next action: {transaction['next_action']}")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR {exc}", file=__import__("sys").stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
