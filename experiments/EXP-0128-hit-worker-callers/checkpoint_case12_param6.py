from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
fp=ROOT/"research/FRONTIER.json";fr=json.loads(fp.read_text(encoding="utf-8"));q=next(r for r in fr["items"] if r.get("id")=="Q-0079")
h={"id":"Q79-H141","model":"Deferred tag-0x12 case supplies param6=0 to bhkWorldM slot +0x1a8 because its sixth argument is the low byte of an in-stack word ANDed with 0xffffffffffffff00.","predicted_discriminant":"Instruction-level code at GOG RVA 0x659c92 shows the source word, low-byte clear, and final stack argument; if the callee sees zero, its object-state eligibility check is enforced just as on the immediate path.","status":"proposed","evidence":["EV-0619","EV-0630"]}
prior=next((r for r in q["hypotheses"] if r.get("id")==h["id"]),None)
if prior is None:q["hypotheses"].append(h)
elif prior!=h:raise SystemExit("hypothesis collision: Q79-H141")
next_action="Run address-only Ghidra query at RVA 0x659c92, the case-0x12 bhkWorldM +0x1a8 call; capture exact instructions forming the fifth and sixth arguments and discriminate the low-byte-cleared-zero model from inherited nonzero param6."
q["next_action"]=next_action;fr["next_action"]=next_action;fr["session_next_action"]=next_action
now=datetime.now(timezone.utc).isoformat(timespec="seconds")
fr["session_checkpoint"]={"timestamp_utc":now,"task":"Q-0079/TX-20261018-0013: test competing deferred param6 bypass/no-bypass models at exact case-0x12 callsite.","next_action":next_action}
fr["last_session_checkpoint"]={"recorded_utc":now,"next_action":next_action,"active_process":"TX-20261018-0013"}
fp.write_text(json.dumps(fr,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
sp=ROOT/"STATE.md";s=sp.read_text(encoding="utf-8")
old="**Selected next line:** compare `FUN_140e884d0`'s immediate and tag-0x12 deferred call setup, focusing on the sixth argument that gates its object-state validation [EV-0619], [EV-0620], [EV-0630]."
new="**Selected next line:** query address RVA `0x659c92` for exact case-0x12 slot `+0x1a8` call instructions; test whether the in-stack sixth argument is low-byte-cleared to zero or inherited nonzero [EV-0619], [EV-0630]."
if old not in s:raise SystemExit("STATE next action not found")
sp.write_text(s.replace(old,new,1),encoding="utf-8")
print("checkpointed exact case-0x12 param6 address query and competing bypass/no-bypass models")
