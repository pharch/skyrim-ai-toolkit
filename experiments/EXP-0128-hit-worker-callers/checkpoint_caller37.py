from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
recovery_path = ROOT / "research/RECOVERY.json"
frontier_path = ROOT / "research/FRONTIER.json"
state_path = ROOT / "STATE.md"
recovery = json.loads(recovery_path.read_text(encoding="utf-8"))
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
if recovery.get("transaction_id") != "TX-20261018-0013" or recovery.get("frontier_id") != "Q-0079":
    raise SystemExit("active checkpoint identity changed")
action = recovery["next_action"]
now = recovery["checkpoint_utc"]
task = (
    "Q-0079/TX-20261018-0013 active on OBJ-2: 36/62 exact worker callers reviewed, 26 remain. "
    "EV-0562–EV-0566 map caller 36 as tag 0x2d with three producers; a separate FUN_1407ed990 path "
    "selects the coordinate event for masked code 0x0b, but the source type is unresolved and the upstream "
    "direct edge set has no mapped HitData/tag-0x0b/ProcessTrapHit target. Q79-H64/H65 remain competing; "
    "H62 and the clean Steam matched-hit/AVSK discriminator remain open."
)
frontier["session_next_action"] = action
frontier["next_action"] = action
frontier["session_checkpoint"] = {"timestamp_utc": now, "task": task, "next_action": action}
frontier["last_session_checkpoint"] = {
    "recorded_utc": now,
    "next_action": action,
    "active_process": None,
}
tmp = frontier_path.with_suffix(frontier_path.suffix + ".tmp")
tmp.write_text(json.dumps(frontier, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
tmp.replace(frontier_path)
line = (
    f"\n\nActive checkpoint {now} (TX-20261018-0013, Q-0079): 36/62 worker callers reviewed; 26 remain. "
    "EV-0562–EV-0566 map caller 36 as tag 0x2d with a separate masked-code producer; code 0x0b and its "
    "source type remain unresolved, and the bounded upstream direct-edge screen finds no mapped HitData/tag-0x0b/"
    "ProcessTrapHit target. H64/H65 remain competing; H62 and the Steam matched-hit/AVSK discriminator remain open. "
    f"Next action: {action}"
)
state = state_path.read_text(encoding="utf-8")
if f"Active checkpoint {now} (TX-20261018-0013, Q-0079)" not in state:
    state_path.write_text(state.rstrip() + line + "\n", encoding="utf-8")
print(f"checkpoint synced at {now}; caller 37/62 is next")
