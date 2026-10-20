from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
next_action = "Run the RTTI-only query for GOG vtable RVA 0x19e9078, then run a separate slot-only query at the same RVA for zero-based slot 0x35 (+0x1a8); the adapter does not combine RTTI with other query modes."
fp = ROOT / "research/FRONTIER.json"
fr = json.loads(fp.read_text(encoding="utf-8"))
q = next(row for row in fr["items"] if row.get("id") == "Q-0079")
q["next_action"] = next_action
fr["next_action"] = next_action
fr["session_next_action"] = next_action
now = datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"] = {"timestamp_utc": now, "task": "Q-0079/TX-20261018-0013: validate bhkWorldM RTTI and +0x1a8 target through separate Ghidra modes.", "next_action": next_action}
fr["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
fp.write_text(json.dumps(fr, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
sp = ROOT / "STATE.md"
state = sp.read_text(encoding="utf-8")
old = "**Selected next line:** validate RTTI and read zero-based slot `0x35` (+`0x1a8`) at GOG vtable RVA `0x19e9078` [EV-0628], then trace the target for a HitData/armor-skill connection."
new = "**Selected next line:** query RTTI separately for the GOG vtable at RVA `0x19e9078`, then read slot `0x35` (+`0x1a8`) in a second query [EV-0628]; the Ghidra adapter does not combine those modes."
if old not in state:
    raise SystemExit("STATE selected-next checkpoint not found")
sp.write_text(state.replace(old, new, 1), encoding="utf-8")
print("checkpointed separate RTTI then slot query in STATE and frontier")
