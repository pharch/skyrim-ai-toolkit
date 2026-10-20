#!/usr/bin/env python3
"""Refresh the human-readable Q82 checkpoint from its active transaction."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
frontier_path = ROOT / "research" / "FRONTIER.json"
recovery_path = ROOT / "research" / "RECOVERY.json"
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
recovery = json.loads(recovery_path.read_text(encoding="utf-8"))

if recovery.get("status") != "running" or recovery.get("frontier_id") != "Q-0082":
    raise SystemExit("Q82 is not the active running checkpoint")
transaction_id = recovery.get("transaction_id")
if transaction_id != "TX-20261020-0001":
    raise SystemExit(f"unexpected active Q82 transaction: {transaction_id!r}")
item = next((row for row in frontier.get("items", []) if row.get("id") == "Q-0082"), None)
if item is None or item.get("status") != "in_progress":
    raise SystemExit("Q82 frontier item is not in_progress")

now = datetime.now(timezone.utc).isoformat(timespec="seconds")
next_action = recovery["next_action"]
frontier["session_checkpoint"] = {
    "timestamp_utc": now,
    "task": f"Q-0082/{transaction_id}: trace mitigation through the actual AV11/AV12 receiver and classify the separate HandleHealthDamage route.",
    "next_action": next_action,
}
frontier["last_session_checkpoint"] = {
    "recorded_utc": now,
    "next_action": next_action,
    "active_process": transaction_id,
}
frontier["next_action"] = next_action
frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"checkpointed {transaction_id}: {next_action}")
