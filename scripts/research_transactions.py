"""Validated append-only lifecycle operations for frontier investigations."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import re
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.research_state import (
    read_json,
    ready_items,
    record_attempt,
    transition_item,
    utc_now,
)

TRANSACTION_ID = re.compile(r"TX-[A-Z0-9-]{4,}")
EVIDENCE_ID = re.compile(r"EV-\d{4,}")
BLOCK_STATUSES = {"blocked_tool", "blocked_environment"}
ACTIVE_RECOVERY = {"running", "interrupted"}
TRANSACTION_STATUSES = {
    "running", "interrupted", "completed", "blocked_tool", "blocked_environment",
}
OPERATIONS = {"begin", "update", "complete", "block", "recover", "resume"}
FRONTIER_TERMINAL = {"completed", "falsified"}
NO_READY_ACTION = (
    "No independent frontier item is ready; review blocked dependencies and "
    "frontier priorities before selecting further work."
)
CLAIM_ID = re.compile(r"\bCL-[A-Z0-9]+(?:-[A-Z0-9]+)*\b")
MECHANISM_ID = re.compile(r"\bM-\d{4,}\b")
EVIDENCE_REF = re.compile(r"\bEV-\d{4,}\b")


def _path(root: Path, relative: str) -> Path:
    return root / "research" / relative


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _read_ledger(root: Path) -> dict[str, Any]:
    path = _path(root, "TRANSACTIONS.json")
    if not path.exists():
        return {"schema_version": 1, "transactions": [], "events": []}
    ledger = read_json(path)
    if ledger.get("schema_version") != 1:
        raise ValueError("transaction ledger schema_version must be 1")
    if not isinstance(ledger.get("transactions"), list) or not isinstance(ledger.get("events"), list):
        raise ValueError("transaction ledger needs transactions and events arrays")
    return ledger


def _load(root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], set[str]]:
    frontier = read_json(_path(root, "FRONTIER.json"))
    evidence = read_json(_path(root, "EVIDENCE.json"))
    recovery = read_json(_path(root, "RECOVERY.json"))
    ledger = _read_ledger(root)
    evidence_ids = {
        row.get("id") for row in evidence.get("items", [])
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }
    return frontier, evidence, recovery, ledger, evidence_ids


def _save(root: Path, frontier: dict[str, Any], recovery: dict[str, Any], ledger: dict[str, Any]) -> None:
    write_json(_path(root, "FRONTIER.json"), frontier)
    write_json(_path(root, "RECOVERY.json"), recovery)
    write_json(_path(root, "TRANSACTIONS.json"), ledger)


def _portable_text(value: str, field: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} must not be empty")
    if re.search(r"(?:\b[A-Za-z]:[\\/]|/mnt/[a-z]/|/home/)", cleaned, re.IGNORECASE):
        raise ValueError(f"{field} must not contain an absolute machine path")
    return cleaned


def _validate_artifacts(root: Path, artifacts: list[str] | None) -> list[str]:
    result: list[str] = []
    for artifact in artifacts or []:
        value = _portable_text(str(artifact), "artifact")
        if value.startswith("private-local:"):
            if len(value) <= len("private-local:"):
                raise ValueError("private-local artifact needs a stable alias")
        else:
            path = Path(value)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("artifact must be a repository-relative path or private-local alias")
            if not (root / path).exists():
                raise ValueError(f"artifact does not exist: {value}")
        result.append(value)
    return list(dict.fromkeys(result))


def _validate_evidence(evidence_ids: list[str] | None, available: set[str]) -> list[str]:
    result = list(dict.fromkeys(evidence_ids or []))
    malformed = [value for value in result if not EVIDENCE_ID.fullmatch(value)]
    missing = [value for value in result if value not in available]
    if malformed:
        raise ValueError("invalid evidence IDs: " + ", ".join(malformed))
    if missing:
        raise ValueError("unknown evidence IDs: " + ", ".join(missing))
    return result


def _find_transaction(ledger: dict[str, Any], transaction_id: str) -> dict[str, Any]:
    transaction = next((row for row in ledger["transactions"] if row.get("id") == transaction_id), None)
    if transaction is None:
        raise ValueError(f"unknown transaction: {transaction_id}")
    return transaction


def _find_frontier_item(frontier: dict[str, Any], frontier_id: str) -> dict[str, Any]:
    item = next((row for row in frontier.get("items", []) if row.get("id") == frontier_id), None)
    if item is None:
        raise ValueError(f"unknown frontier item: {frontier_id}")
    return item


def _append_event(
    ledger: dict[str, Any],
    transaction: dict[str, Any],
    operation: str,
    **details: Any,
) -> dict[str, Any]:
    used = {
        int(match.group(1))
        for row in ledger["events"]
        if isinstance(row, dict)
        if isinstance(match := re.fullmatch(r"TE-(\d{6,})", str(row.get("id", ""))), re.Match)
    }
    event_number = max(used, default=0) + 1
    event_id = f"TE-{event_number:06d}"
    while event_id in used:
        event_number += 1
        event_id = f"TE-{event_number:06d}"
    event = {
        "id": event_id,
        "transaction_id": transaction["id"],
        "operation": operation,
        "recorded_utc": utc_now(),
        **details,
    }
    ledger["events"].append(event)
    transaction.setdefault("event_ids", []).append(event_id)
    transaction["updated_utc"] = event["recorded_utc"]
    return event


def _append_session(root: Path, transaction_id: str, operation: str, summary: str) -> None:
    line = f"- {utc_now()} transaction `{transaction_id}` {operation}: {_portable_text(summary, 'session summary')}\n"
    path = root / "research" / "SESSION_LOG.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(line)


def _active_transaction(recovery: dict[str, Any], ledger: dict[str, Any], transaction_id: str) -> dict[str, Any]:
    if recovery.get("status") != "running" or recovery.get("transaction_id") != transaction_id:
        raise ValueError("transaction is not the active running checkpoint; recover or begin the correct transaction")
    transaction = _find_transaction(ledger, transaction_id)
    if transaction.get("status") != "running":
        raise ValueError(f"transaction is not running: {transaction.get('status')}")
    return transaction


def select_next_item(
    frontier: dict[str, Any], *, exclude_ids: set[str] | None = None,
) -> dict[str, Any] | None:
    excluded = exclude_ids or set()
    return next((item for item in ready_items(frontier) if item.get("id") not in excluded), None)


def _close_recovery(
    recovery: dict[str, Any], transaction: dict[str, Any], next_item: dict[str, Any] | None,
) -> None:
    recovery.update({
        "status": "idle",
        "transaction_id": None,
        "frontier_id": None,
        "started_utc": None,
        "checkpoint_utc": utc_now(),
        "artifacts": [],
        "next_action": next_item["next_action"] if next_item else NO_READY_ACTION,
        "next_frontier_id": next_item["id"] if next_item else None,
        "last_transaction_id": transaction["id"],
    })


def _allocate_transaction_id(ledger: dict[str, Any]) -> str:
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    existing = {str(row.get("id")) for row in ledger.get("transactions", []) if isinstance(row, dict)}
    serial = 1
    while True:
        candidate = f"TX-{day}-{serial:04d}"
        if candidate not in existing:
            return candidate
        serial += 1


def begin_transaction(
    root: Path,
    frontier_id: str,
    next_action: str,
    *,
    transaction_id: str | None = None,
) -> dict[str, Any]:
    action = _portable_text(next_action, "next_action")
    frontier, _, recovery, ledger, _ = _load(root)
    transaction_id = transaction_id or _allocate_transaction_id(ledger)
    if not TRANSACTION_ID.fullmatch(transaction_id):
        raise ValueError("transaction ID must match TX-[A-Z0-9-]{4,}")
    if recovery.get("status") in ACTIVE_RECOVERY:
        raise ValueError("an active or interrupted transaction must be resumed or closed first")
    if any(row.get("id") == transaction_id for row in ledger["transactions"]):
        raise ValueError(f"transaction ID already exists: {transaction_id}")
    item = _find_frontier_item(frontier, frontier_id)
    if item.get("status") not in {"open", "in_progress"}:
        raise ValueError(f"frontier item is not actionable: {item.get('status')}")
    if not any(row.get("id") == frontier_id for row in ready_items(frontier)):
        raise ValueError(f"frontier item is not ready: {frontier_id}")
    if item.get("status") == "open":
        transition_item(frontier, frontier_id, "in_progress")
    now = utc_now()
    transaction = {
        "id": transaction_id,
        "frontier_id": frontier_id,
        "question": item["question"],
        "hypotheses": item["hypotheses"],
        "status": "running",
        "started_utc": now,
        "updated_utc": now,
        "next_action": action,
        "evidence": [],
        "artifacts": [],
        "event_ids": [],
    }
    ledger["transactions"].append(transaction)
    _append_event(ledger, transaction, "begin", frontier_id=frontier_id, next_action=action)
    recovery.update({
        "status": "running",
        "transaction_id": transaction_id,
        "frontier_id": frontier_id,
        "started_utc": now,
        "checkpoint_utc": now,
        "artifacts": [],
        "next_action": action,
        "next_frontier_id": None,
    })
    _save(root, frontier, recovery, ledger)
    _append_session(root, transaction_id, "begin", f"frontier {frontier_id}; next action: {action}")
    return transaction


def update_transaction(
    root: Path,
    transaction_id: str,
    *,
    action_key: str,
    outcome: str,
    next_action: str,
    evidence_ids: list[str] | None = None,
    artifacts: list[str] | None = None,
    new_discriminant: str = "",
) -> dict[str, Any]:
    key = _portable_text(action_key, "action_key")
    result = _portable_text(outcome, "outcome")
    action = _portable_text(next_action, "next_action")
    discrim = _portable_text(new_discriminant, "new_discriminant") if new_discriminant.strip() else ""
    frontier, _, recovery, ledger, known_evidence = _load(root)
    transaction = _active_transaction(recovery, ledger, transaction_id)
    item = _find_frontier_item(frontier, transaction["frontier_id"])
    selected_evidence = _validate_evidence(evidence_ids, known_evidence)
    selected_artifacts = _validate_artifacts(root, artifacts)
    has_previous_action = any(attempt.get("action_key") == key for attempt in item.get("attempts", []))
    if has_previous_action:
        record_attempt(item, key, result, evidence_ids=selected_evidence, new_discriminant=discrim)
    elif not selected_evidence and not discrim:
        raise ValueError("update requires evidence or a new predicted discriminant")
    else:
        record_attempt(item, key, result, evidence_ids=selected_evidence, new_discriminant=discrim)
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), *selected_evidence]))
    transaction["evidence"] = list(dict.fromkeys([*transaction["evidence"], *selected_evidence]))
    transaction["artifacts"] = list(dict.fromkeys([*transaction["artifacts"], *selected_artifacts]))
    transaction["next_action"] = action
    item["next_action"] = action
    frontier["session_next_action"] = action
    recovery["checkpoint_utc"] = utc_now()
    recovery["next_action"] = action
    recovery["artifacts"] = list(dict.fromkeys([*recovery.get("artifacts", []), *selected_artifacts]))
    _append_event(
        ledger, transaction, "update", action_key=key, outcome=result,
        evidence=selected_evidence, artifacts=selected_artifacts,
        new_discriminant=discrim or None, next_action=action,
    )
    _save(root, frontier, recovery, ledger)
    _append_session(root, transaction_id, "update", f"{key}: {result}; next action: {action}")
    return transaction


def complete_transaction(
    root: Path,
    transaction_id: str,
    *,
    summary: str,
    cross_domain_assessment: str,
    evidence_ids: list[str] | None = None,
    artifacts: list[str] | None = None,
    frontier_status: str = "completed",
    successor_ids: list[str] | None = None,
    synthesis_claim_ids: list[str] | None = None,
    synthesis_mechanism_ids: list[str] | None = None,
    knowledge_graph_action: str,
) -> dict[str, Any]:
    result = _portable_text(summary, "summary")
    synthesis = _portable_text(cross_domain_assessment, "cross_domain_assessment")
    graph_action = _portable_text(knowledge_graph_action, "knowledge_graph_action")
    if frontier_status not in FRONTIER_TERMINAL:
        raise ValueError("frontier_status must be completed or falsified")
    frontier, _, recovery, ledger, known_evidence = _load(root)
    transaction = _active_transaction(recovery, ledger, transaction_id)
    if not any(event.get("transaction_id") == transaction_id and event.get("operation") == "update" for event in ledger["events"]):
        raise ValueError("complete requires at least one validated update")
    selected_evidence = _validate_evidence(evidence_ids, known_evidence)
    if not selected_evidence and not transaction.get("evidence"):
        raise ValueError("complete requires evidence")
    selected_artifacts = _validate_artifacts(root, artifacts)
    selected_evidence = list(dict.fromkeys([*transaction["evidence"], *selected_evidence]))
    selected_claims = _validate_synthesis_links(
        root,
        selected_evidence,
        synthesis_claim_ids or [],
        synthesis_mechanism_ids or [],
    )
    selected_mechanisms = list(dict.fromkeys(synthesis_mechanism_ids or []))
    selected_successors = list(dict.fromkeys(successor_ids or []))
    transaction["evidence"] = selected_evidence
    transaction["artifacts"] = list(dict.fromkeys([*transaction["artifacts"], *selected_artifacts]))
    transaction["status"] = "completed"
    transaction["summary"] = result
    transaction["cross_domain_assessment"] = synthesis
    current_id = transaction["frontier_id"]
    item = _find_frontier_item(frontier, current_id)
    decision = {
        "summary": result,
        "cross_domain_assessment": synthesis,
        "successors": selected_successors,
    }
    transition_item(
        frontier, current_id, frontier_status,
        evidence_ids=selected_evidence,
        decision=decision,
        available_evidence=known_evidence,
    )
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), *selected_claims]))
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), *selected_evidence]))
    completed_utc = item["decision"]["closed_utc"]
    transaction["closure_scope"] = "frontier_resolved"
    transaction["frontier_resolution"] = {"status": frontier_status, "closed_utc": completed_utc}
    transaction["synthesis_claim_ids"] = selected_claims
    transaction["synthesis_mechanism_ids"] = selected_mechanisms
    transaction["knowledge_graph_action"] = graph_action
    transaction["completed_utc"] = completed_utc
    next_item = select_next_item(frontier, exclude_ids={current_id})
    transaction["next_frontier_id"] = next_item["id"] if next_item else None
    _append_event(
        ledger, transaction, "complete", summary=result,
        cross_domain_assessment=synthesis, frontier_status=frontier_status,
        successor_frontier_ids=selected_successors, evidence=selected_evidence,
        artifacts=selected_artifacts, next_frontier_id=next_item["id"] if next_item else None,
        synthesis_claim_ids=selected_claims,
        synthesis_mechanism_ids=selected_mechanisms,
        knowledge_graph_action=graph_action,
    )
    _close_recovery(recovery, transaction, next_item)
    frontier["session_next_action"] = next_item["next_action"] if next_item else NO_READY_ACTION
    _save(root, frontier, recovery, ledger)
    next_note = f"selected {next_item['id']} next" if next_item else "no independent frontier item is ready"
    _append_session(root, transaction_id, "complete", f"{result}; {next_note}")
    return {"transaction": transaction, "next_item": next_item}


def _validate_synthesis_links(
    root: Path,
    evidence_ids: list[str],
    claim_ids: list[str],
    mechanism_ids: list[str],
) -> list[str]:
    claims = list(dict.fromkeys(claim_ids))
    mechanisms = list(dict.fromkeys(mechanism_ids))
    invalid_claims = [value for value in claims if not CLAIM_ID.fullmatch(value)]
    invalid_mechanisms = [value for value in mechanisms if not MECHANISM_ID.fullmatch(value)]
    if invalid_claims:
        raise ValueError("invalid synthesis claim IDs: " + ", ".join(invalid_claims))
    if invalid_mechanisms:
        raise ValueError("invalid synthesis mechanism IDs: " + ", ".join(invalid_mechanisms))

    claims_text = (root / "research/CLAIMS.md").read_text(encoding="utf-8")
    mechanisms_text = (root / "research/MECHANISMS.md").read_text(encoding="utf-8")
    graph_text = (root / "research/KNOWLEDGE_GRAPH.md").read_text(encoding="utf-8")
    for claim_id in claims:
        if claim_id not in CLAIM_ID.findall(claims_text):
            raise ValueError(f"synthesis claim is missing from research/CLAIMS.md: {claim_id}")
        if claim_id not in CLAIM_ID.findall(graph_text):
            raise ValueError(f"synthesis claim is not linked in research/KNOWLEDGE_GRAPH.md: {claim_id}")
        rows = [line for line in claims_text.splitlines() if claim_id in line]
        linked_evidence = {ref for line in rows for ref in EVIDENCE_REF.findall(line)}
        if evidence_ids and not linked_evidence.intersection(evidence_ids):
            raise ValueError(f"synthesis claim {claim_id} does not cite this transaction's evidence")
    for mechanism_id in mechanisms:
        if mechanism_id not in MECHANISM_ID.findall(mechanisms_text):
            raise ValueError(f"synthesis mechanism is missing from research/MECHANISMS.md: {mechanism_id}")
        if mechanism_id not in MECHANISM_ID.findall(graph_text):
            raise ValueError(f"synthesis mechanism is not linked in research/KNOWLEDGE_GRAPH.md: {mechanism_id}")
    return claims


def block_transaction(
    root: Path,
    transaction_id: str,
    *,
    blocker: str,
    blocker_status: str,
    evidence_ids: list[str],
    artifacts: list[str] | None = None,
) -> dict[str, Any]:
    reason = _portable_text(blocker, "blocker")
    if blocker_status not in BLOCK_STATUSES:
        raise ValueError("blocker_status must be blocked_tool or blocked_environment")
    frontier, _, recovery, ledger, known_evidence = _load(root)
    transaction = _active_transaction(recovery, ledger, transaction_id)
    selected_evidence = _validate_evidence(evidence_ids, known_evidence)
    if not selected_evidence and not transaction.get("evidence"):
        raise ValueError("block requires evidence of the blocker")
    selected_artifacts = _validate_artifacts(root, artifacts)
    current_id = transaction["frontier_id"]
    item = _find_frontier_item(frontier, current_id)
    transition_item(frontier, current_id, blocker_status, evidence_ids=selected_evidence, available_evidence=known_evidence)
    transaction["evidence"] = list(dict.fromkeys([*transaction["evidence"], *selected_evidence]))
    transaction["artifacts"] = list(dict.fromkeys([*transaction["artifacts"], *selected_artifacts]))
    transaction["status"] = blocker_status
    transaction["blocker"] = reason
    transaction["blocked_utc"] = utc_now()
    transaction["closure_scope"] = "blocked_checkpoint"
    transaction["frontier_resolution"] = {"status": blocker_status, "blocked_utc": transaction["blocked_utc"]}
    next_item = select_next_item(frontier, exclude_ids={current_id})
    transaction["next_frontier_id"] = next_item["id"] if next_item else None
    _append_event(
        ledger, transaction, "block", blocker=reason, blocker_status=blocker_status,
        evidence=selected_evidence, artifacts=selected_artifacts,
        reselected_frontier_id=next_item["id"] if next_item else None,
        next_action=next_item["next_action"] if next_item else NO_READY_ACTION,
    )
    _close_recovery(recovery, transaction, next_item)
    frontier["session_next_action"] = next_item["next_action"] if next_item else NO_READY_ACTION
    _save(root, frontier, recovery, ledger)
    next_note = f"independently selected {next_item['id']}" if next_item else "no other frontier item is ready"
    _append_session(root, transaction_id, "block", f"{reason}; {next_note}")
    return {"transaction": transaction, "next_item": next_item}


def recover_transaction(root: Path) -> dict[str, Any]:
    frontier, _, recovery, ledger, _ = _load(root)
    if recovery.get("status") != "running":
        return recovery
    transaction_id = recovery.get("transaction_id")
    if not transaction_id:
        raise ValueError("running recovery state lacks transaction_id")
    transaction = _find_transaction(ledger, transaction_id)
    if transaction.get("status") != "running":
        raise ValueError("running recovery and transaction statuses disagree")
    action = _portable_text(recovery.get("next_action", ""), "next_action")
    recovery.update({
        "status": "interrupted",
        "interrupted_utc": utc_now(),
        "resume_action": "Inspect raw artifacts and durable changes, then explicitly resume before further work.",
    })
    transaction["status"] = "interrupted"
    transaction["interrupted_utc"] = recovery["interrupted_utc"]
    _append_event(ledger, transaction, "recover", next_action=action)
    _save(root, frontier, recovery, ledger)
    _append_session(root, transaction_id, "recover", f"marked interrupted; resume at: {action}")
    return recovery


def resume_transaction(root: Path, transaction_id: str | None = None) -> dict[str, Any]:
    frontier, _, recovery, ledger, _ = _load(root)
    active_id = recovery.get("transaction_id")
    transaction_id = transaction_id or active_id
    if recovery.get("status") != "interrupted" or not transaction_id or active_id != transaction_id:
        raise ValueError("resume requires the matching interrupted recovery checkpoint")
    transaction = _find_transaction(ledger, transaction_id)
    if transaction.get("status") != "interrupted":
        raise ValueError("interrupted recovery and transaction statuses disagree")
    action = _portable_text(recovery.get("next_action", ""), "next_action")
    now = utc_now()
    transaction["status"] = "running"
    transaction["resumed_utc"] = now
    recovery["status"] = "running"
    recovery["checkpoint_utc"] = now
    recovery.pop("interrupted_utc", None)
    recovery.pop("resume_action", None)
    _append_event(ledger, transaction, "resume", next_action=action)
    _save(root, frontier, recovery, ledger)
    _append_session(root, transaction_id, "resume", f"fresh-process continuation; next action: {action}")
    return transaction


def validate_transaction_ledger(
    ledger: dict[str, Any],
    recovery: dict[str, Any],
    evidence_ids: set[str],
    *,
    frontier: dict[str, Any] | None = None,
    root: Path | None = None,
) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema_version") != 1:
        return ["transaction ledger schema_version must be 1"]
    transactions = ledger.get("transactions")
    events = ledger.get("events")
    if not isinstance(transactions, list) or not isinstance(events, list):
        return ["transaction ledger needs transactions and events arrays"]
    tx_by_id: dict[str, dict[str, Any]] = {}
    for transaction in transactions:
        if not isinstance(transaction, dict):
            errors.append("transaction entries must be objects")
            continue
        txid = transaction.get("id")
        if not isinstance(txid, str) or not TRANSACTION_ID.fullmatch(txid):
            errors.append(f"invalid transaction ID: {txid!r}")
            continue
        if txid in tx_by_id:
            errors.append(f"duplicate transaction ID: {txid}")
        tx_by_id[txid] = transaction
        if transaction.get("status") not in TRANSACTION_STATUSES:
            errors.append(f"{txid}: invalid transaction status")
        if not transaction.get("next_action"):
            errors.append(f"{txid}: missing actionable next_action")
        for evidence_id in transaction.get("evidence", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{txid}: unknown evidence {evidence_id}")
    event_ids: set[str] = set()
    by_tx_events: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        if not isinstance(event, dict):
            errors.append("transaction events must be objects")
            continue
        event_id = event.get("id")
        txid = event.get("transaction_id")
        if not isinstance(event_id, str) or not re.fullmatch(r"TE-\d{6,}", event_id):
            errors.append(f"invalid transaction event ID: {event_id!r}")
        elif event_id in event_ids:
            errors.append(f"duplicate transaction event ID: {event_id}")
        event_ids.add(event_id)
        if event.get("operation") not in OPERATIONS:
            errors.append(f"{event_id}: invalid transaction operation")
        if txid not in tx_by_id:
            errors.append(f"{event_id}: unknown transaction {txid}")
        by_tx_events.setdefault(txid, []).append(event)
        for evidence_id in event.get("evidence", []):
            if evidence_id not in evidence_ids:
                errors.append(f"{event_id}: unknown evidence {evidence_id}")
    for txid, transaction in tx_by_id.items():
        ids = transaction.get("event_ids", [])
        if not isinstance(ids, list) or any(event_id not in event_ids for event_id in ids):
            errors.append(f"{txid}: event_ids contain missing events")
        tx_events = by_tx_events.get(txid, [])
        operations = [event.get("operation") for event in tx_events]
        if not operations or operations[0] != "begin":
            errors.append(f"{txid}: lifecycle must begin with a begin event")
            continue
        if operations.count("complete") + operations.count("block") > 1:
            errors.append(f"{txid}: lifecycle has multiple terminal events")
        status = transaction.get("status")
        last = operations[-1]
        expected_last = {
            "running": {"begin", "update", "resume"},
            "interrupted": {"recover"},
            "completed": {"complete"},
            "blocked_tool": {"block"},
            "blocked_environment": {"block"},
        }.get(status, set())
        if last not in expected_last:
            errors.append(f"{txid}: last event {last!r} disagrees with status {status!r}")
        if status == "completed" and "update" not in operations:
            errors.append(f"{txid}: completion requires an update event")
        if status in BLOCK_STATUSES and "block" not in operations:
            errors.append(f"{txid}: blocked status requires a block event")
        if not isinstance(ids, list) or set(ids) != {event.get("id") for event in tx_events}:
            errors.append(f"{txid}: event_ids do not match append-only event records")
        scope = transaction.get("closure_scope")
        resolution = transaction.get("frontier_resolution")
        if status == "completed":
            if scope == "bounded_checkpoint":
                if not isinstance(resolution, dict) or resolution.get("status") != "unresolved":
                    errors.append(f"{txid}: bounded checkpoint must explicitly leave its frontier unresolved")
                elif frontier is not None:
                    item = next((entry for entry in frontier.get("items", []) if entry.get("id") == transaction.get("frontier_id")), None)
                    if item is None or item.get("status") not in {"open", "in_progress"}:
                        later_resolution = False
                        if item is not None and item.get("status") in FRONTIER_TERMINAL:
                            later_resolution = any(
                                other.get("id") != txid
                                and other.get("frontier_id") == transaction.get("frontier_id")
                                and other.get("status") == "completed"
                                and other.get("closure_scope") == "frontier_resolved"
                                and isinstance(other.get("frontier_resolution"), dict)
                                and other["frontier_resolution"].get("status") == item.get("status")
                                and item.get("decision", {}).get("evidence") == other.get("evidence")
                                for other in transactions
                            )
                        if item is not None and item.get("status") in BLOCK_STATUSES:
                            item_evidence = set(item.get("evidence", []))
                            later_resolution = later_resolution or any(
                                other.get("id") != txid
                                and other.get("frontier_id") == transaction.get("frontier_id")
                                and other.get("status") == item.get("status")
                                and other.get("closure_scope") == "blocked_checkpoint"
                                and isinstance(other.get("frontier_resolution"), dict)
                                and other["frontier_resolution"].get("status") == item.get("status")
                                and set(other.get("evidence", [])).issubset(item_evidence)
                                for other in transactions
                            )
                        if not later_resolution:
                            errors.append(f"{txid}: unresolved checkpoint is absent from the active frontier")
            elif scope == "frontier_resolved":
                resolution_status = resolution.get("status") if isinstance(resolution, dict) else None
                if resolution_status not in FRONTIER_TERMINAL:
                    errors.append(f"{txid}: completed investigation lacks a terminal frontier resolution")
                if not isinstance(transaction.get("knowledge_graph_action"), str) or not transaction["knowledge_graph_action"].strip():
                    errors.append(f"{txid}: completed investigation lacks a graph update or no-edge rationale")
                for field in ("synthesis_claim_ids", "synthesis_mechanism_ids"):
                    if not isinstance(transaction.get(field), list):
                        errors.append(f"{txid}: completed investigation lacks {field}")
                if frontier is not None and resolution_status in FRONTIER_TERMINAL:
                    item = next((entry for entry in frontier.get("items", []) if entry.get("id") == transaction.get("frontier_id")), None)
                    if item is None or item.get("status") != resolution_status:
                        errors.append(f"{txid}: resolved investigation re-entered or disagrees with the frontier")
                    elif item.get("decision", {}).get("evidence") != transaction.get("evidence"):
                        errors.append(f"{txid}: frontier decision evidence disagrees with transaction evidence")
                if root is not None and isinstance(transaction.get("knowledge_graph_action"), str):
                    try:
                        _validate_synthesis_links(
                            root, transaction.get("evidence", []),
                            transaction.get("synthesis_claim_ids", []),
                            transaction.get("synthesis_mechanism_ids", []),
                        )
                    except (OSError, ValueError) as exc:
                        errors.append(f"{txid}: synthesis references are inconsistent: {exc}")
            else:
                errors.append(f"{txid}: completed transaction must resolve its frontier or declare a bounded checkpoint")
        elif status in BLOCK_STATUSES and scope == "blocked_checkpoint" and frontier is not None:
            resolution_status = resolution.get("status") if isinstance(resolution, dict) else None
            item = next((entry for entry in frontier.get("items", []) if entry.get("id") == transaction.get("frontier_id")), None)
            if resolution_status != status or item is None or item.get("status") != status:
                errors.append(f"{txid}: blocked checkpoint disagrees with its frontier item")
    active = [row for row in transactions if isinstance(row, dict) and row.get("status") in ACTIVE_RECOVERY]
    recovery_status = recovery.get("status")
    if recovery_status in ACTIVE_RECOVERY:
        txid = recovery.get("transaction_id")
        matches = [row for row in active if row.get("id") == txid]
        if len(matches) != 1:
            errors.append("active recovery must reference exactly one active transaction")
        elif recovery.get("frontier_id") != matches[0].get("frontier_id"):
            errors.append("active recovery frontier_id disagrees with transaction")
        elif frontier is not None:
            item = next((entry for entry in frontier.get("items", []) if entry.get("id") == recovery.get("frontier_id")), None)
            if item is None or item.get("status") != "in_progress":
                errors.append("active recovery must point to an in-progress frontier item")
    elif active:
        errors.append("closed recovery state has an active transaction")
    elif frontier is not None and recovery_status == "idle":
        next_id = recovery.get("next_frontier_id")
        candidates = ready_items(frontier)
        if next_id is None and candidates:
            errors.append("idle recovery omits a next frontier while ready items exist")
        elif next_id is not None and not any(item.get("id") == next_id for item in candidates):
            errors.append("idle recovery next_frontier_id is not a ready frontier item")
    return errors


def main(argv: list[str] | None = None) -> int:
    """Expose the validated lifecycle through the repository Python dispatcher."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="research checkout root (defaults to this repository)")
    sub = parser.add_subparsers(dest="operation", required=True)

    begin = sub.add_parser("begin", help="begin a frontier investigation")
    begin.add_argument("frontier_id")
    begin.add_argument("--transaction-id", help="optional stable ID; generated uniquely when omitted")
    begin.add_argument("--next-action", required=True)

    update = sub.add_parser("update", help="append a research result to a running investigation")
    update.add_argument("transaction_id")
    update.add_argument("--action-key", required=True)
    update.add_argument("--outcome", required=True)
    update.add_argument("--next-action", required=True)
    update.add_argument("--evidence", dest="evidence_ids", action="append", default=[])
    update.add_argument("--artifact", action="append", default=[])
    update.add_argument("--new-discriminant", default="")

    complete = sub.add_parser("complete", help="close a completed investigation and choose a successor")
    complete.add_argument("transaction_id")
    complete.add_argument("--summary", required=True)
    complete.add_argument("--cross-domain-assessment", required=True)
    complete.add_argument("--evidence", dest="evidence_ids", action="append", default=[])
    complete.add_argument("--artifact", action="append", default=[])
    complete.add_argument("--frontier-status", choices=sorted(FRONTIER_TERMINAL), default="completed")
    complete.add_argument("--successor", dest="successor_ids", action="append", default=[])
    complete.add_argument("--claim", dest="claim_ids", action="append", default=[])
    complete.add_argument("--mechanism", dest="mechanism_ids", action="append", default=[])
    complete.add_argument("--graph-action", required=True)

    block = sub.add_parser("block", help="close a line blocked by an external dependency")
    block.add_argument("transaction_id")
    block.add_argument("--blocker", required=True)
    block.add_argument("--blocker-status", choices=sorted(BLOCK_STATUSES), required=True)
    block.add_argument("--evidence", dest="evidence_ids", action="append", default=[])
    block.add_argument("--artifact", action="append", default=[])

    sub.add_parser("recover", help="mark an unfinished transaction interrupted")
    resume = sub.add_parser("resume", help="resume the matching interrupted transaction")
    resume.add_argument("transaction_id", nargs="?")
    sub.add_parser("validate", help="validate the append-only lifecycle ledger")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        if args.operation == "begin":
            result = begin_transaction(
                root, args.frontier_id, args.next_action,
                transaction_id=args.transaction_id,
            )
        elif args.operation == "update":
            result = update_transaction(
                root, args.transaction_id, action_key=args.action_key, outcome=args.outcome,
                next_action=args.next_action, evidence_ids=args.evidence_ids,
                artifacts=args.artifact, new_discriminant=args.new_discriminant,
            )
        elif args.operation == "complete":
            result = complete_transaction(
                root, args.transaction_id, summary=args.summary,
                cross_domain_assessment=args.cross_domain_assessment,
                evidence_ids=args.evidence_ids, artifacts=args.artifact,
                frontier_status=args.frontier_status,
                successor_ids=args.successor_ids,
                synthesis_claim_ids=args.claim_ids,
                synthesis_mechanism_ids=args.mechanism_ids,
                knowledge_graph_action=args.graph_action,
            )
        elif args.operation == "block":
            result = block_transaction(
                root, args.transaction_id, blocker=args.blocker,
                blocker_status=args.blocker_status, evidence_ids=args.evidence_ids,
                artifacts=args.artifact,
            )
        elif args.operation == "recover":
            result = recover_transaction(root)
        elif args.operation == "resume":
            result = resume_transaction(root, args.transaction_id)
        else:
            frontier, evidence, recovery, ledger, evidence_ids = _load(root)
            errors = validate_transaction_ledger(
                ledger, recovery, evidence_ids, frontier=frontier, root=root,
            )
            result = {"ok": not errors, "errors": errors,
                      "transaction_count": len(ledger["transactions"]),
                      "event_count": len(ledger["events"])}
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if not errors else 1
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": f"{type(exc).__name__}: {exc}"}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
