#!/usr/bin/env python3
"""Checkpoint the active Q-0064 transaction in the compact state files."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    recovery = json.loads((ROOT / "research/RECOVERY.json").read_text(encoding="utf-8"))
    if recovery.get("status") != "running" or recovery.get("frontier_id") != "Q-0064":
        raise SystemExit("recovery does not identify the active Q-0064 transaction")
    action = recovery.get("next_action", "")
    if not action:
        raise SystemExit("active Q-0064 transaction has no next action")
    active_item = next(item for item in frontier["items"] if item["id"] == "Q-0064")
    active_item["next_action"] = action
    frontier["session_next_action"] = action
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0063/EV-0326 is closed as a bounded Dawnguard source candidate. Q-0064 remains active on the ProcessTrapHit cleanup descendants for the OBJ-2 physical-trap route.",
        "next_action": action,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now,
        "next_action": action,
        "active_process": f"{recovery['transaction_id']} running on Q-0064; trace whether the exact selected entity enters hkpSimulationIsland EntityPtrs and whether its exact constraint enters ConMstPtr; then follow producer-backed callbacks/members to AV11/AV12.",
    }
    frontier["next_action"] = action
    frontier.setdefault("target", {})["next_action"] = action
    frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    state = f"""# Current research state — 2026-10-18

## Active bounty

Keep OBJ-1 level-one access to gated content and OBJ-2 functional armor with zero hit-earned Heavy/Light Armor XP at P0. A bounded source candidate does not resolve the bounty.

## Latest bounded findings

- Q-0063 / EV-0326 maps a Fort Dawnguard dialogue and helper callback chain from start-enabled VQ00 to `DLC1VQ01.SetStage(10)` without a serialized level-10 condition on that mapped route. This is a strong level-one source candidate, not a Steam runtime bypass. VQ01 startup, natural level-one dialogue access, aliases, useful Dimhollow progress, and profile winner remain unknown.
- Q-0062 / EV-0324–EV-0325 maps the GOG AE 1.6.1179.0 ProcessTrapHit path around the known armor/Block XP wrapper. The PlayerCharacter cleanup body has 108 direct edges and eight indirect sites; the trap remains unverified for positive final damage, effective protection, and zero raw AVSK change.
- Q-0064 / EV-0347 ties PlayerCharacter+0x8F8 to `Actors\\Character\\1stPerson\\Skel` through the generic mesh loader. The exact NIF root class and slot +0x8 descendants remain unresolved; the +0x730 scan adds no concrete class.
- Q-0064 / EV-0348 maps the +0x9D0 fallback to descriptor key-2/key-1 values, with the concrete object class still data-dependent. The next path is the +0x9A0/+0x9A8 model resource.
- Q-0064 / EV-0349 maps the +0x9A0/+0x9A8 candidate through a two-slot adapter and sorted-name lookup. Its concrete root/finalizer remains data-selected; the lookup contract differs from +0x8F8 without deciding class identity.
- Q-0064 / EV-0350 maps the mode-selected +0x9A8/+0x9A0 setter and model-resource caller, but the incoming class/finalizer remain unresolved. The next source branch is +0x730.
- Q-0064 / EV-0351 confirms the +0x730 helper returns a data-selected value at cell+0x130+8; class and non-null writer remain unknown. The next branch is the PlayerCamera global cleanup.
- Q-0064 / EV-0352 maps the PlayerCamera global table and slot-0 destructor; five owned-object calls remain dynamic and the broad +0x28 scan finds no object-specific non-null writer. The next branch is +0x128.
- Q-0064 / EV-0353 resolves PlayerCamera+0x128 to bhkRigidBody and its slot+8 destructor to FUN_140e92c60; that body's +0x28 child array still dispatches unresolved slot+8 targets. The next branch traces those child producers.
- Q-0064 / EV-0354 proves the rigid body's +0x28 pointer and +0x38 count start zero, so its first slot+0x150 loop skips; later vector population is still unknown. The next query is FUN_140ebf0b0 and post-constructor writers.
- Q-0064 / EV-0355 ties FUN_1406b9df0 to a flagged scene traversal that can append fixed/malleable physics constraints to rigid-body child vectors; mapped callbacks manipulate physics state, but FUN_140b3a830 descendants and remaining indirect sites stay open.
- Q-0064 / EV-0356 maps the factory-created child payload as hkpConstraintInstance; its slot +0x30 returns zero, bypassing one conditional list-removal branch. CL-L194 records no supported causal edge between the EV-0326 Fort stage-request route and this OBJ-2 physics path; a shared call/state dependency would falsify it.
- Q-0064 / EV-0357 resolves the factory-created hkpConstraintInstance slot-0 finalizer to callback/member ownership cleanup and TLS allocation; callback +0x18 targets and member classes remain unresolved.
- Q-0064 / EV-0358 maps the hkpConstraintInstance callback-array consumer and its two direct caller functions; constructor starts empty and broad +0x40/+0x48 scans identify no exact callback producer.
- Q-0064 / EV-0359 separates a chain-instance cleanup override from potential island/entity and post-collision command carriers; exact factory-object membership remains unresolved.
- Q-0064 / EV-0360 links the exact ProcessTrapHit-created hkpConstraintInstance to its entity +0x100/+0x108 constraint record and +0x60 back-pointer; attach callback dispatch follows but listener writers/classes remain unresolved.
- Q-0064 / EV-0361 maps the exact add/remove callback consumer slots and two add-wrapper caller functions; the hkpConstraintListener string has no analyzed references and no producer/class is identified.
- Q-0064 / EV-0362 corrects the owner name to hkpSimulationIsland and maps its EntityPtrs-to-constraint serializer; exact factory-object membership remains unresolved.
- Q-0064 / EV-0363 withdraws the EV-0362 +0x60/+0x68 writer negative: both broad scans printed only the first 2,048 accesses and stopped before 0x140b.

## Active transaction

`{recovery['transaction_id']}` / Q-0064 tests whether any of the eight indirect calls in the ProcessTrapHit PlayerCharacter teardown chain can reach AV11/AV12 skill progress. Next action: {action} Resolve targets only through the existing GOG AE 1.6.1179.0 project in read-only mode. Keep GOG and Steam AE 1.6.1170.0 addresses separate.

## Target and evidence boundary

Steam AE `SkyrimSE.exe` ProductVersion 1.6.1170.0 is identified by EV-0109. The complete active order, clean level-one save, and read-only live Observer are unavailable (EV-0260). Use the fixed five official masters only for bounded source questions; they do not establish a profile winner. Keep raw captures in ignored `.local/`; preserve source hashes and uncertainty in the evidence ledgers.
"""
    (ROOT / "STATE.md").write_text(state, encoding="utf-8")
    print("STATE.md and frontier checkpoints now point to TX-20261017-0011 / Q-0064")


if __name__ == "__main__":
    main()
