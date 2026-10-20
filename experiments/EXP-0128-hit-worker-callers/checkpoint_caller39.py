from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TS='2026-10-19T16:54:09+00:00'
NEXT='Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6586a0 --list-call-edges --timeout 600; inspect exact caller 39/62 producer, tag payload, matched dispatcher case, and any direct HitData/ActorValue/armor-skill edges. Keep the clean Steam matched-hit/protection/raw AVSK requirement and GOG/Steam build boundary explicit.'
TASK='Q-0079/TX-20261018-0013 active on OBJ-2: caller 38/62 FUN_140658660 is bounded as a tag-0x34 deferred Actor/process vector and state update; 24 exact worker callers remain. EV-0573/0574 map the matching clear-gate producer and dispatcher case; case-local virtual slots +0x18/+0x38 and broader ancestry remain unresolved. No direct HitData/AV11/AV12/UseSkill edge is established. OBJ-1 remains P0 and independent; caller completion does not resolve the bounty.'
fp=ROOT/'research/FRONTIER.json'; data=json.loads(fp.read_text())
data['session_next_action']=NEXT; data['next_action']=NEXT
data['session_checkpoint']={'timestamp_utc':TS,'task':TASK,'next_action':NEXT}
data['last_session_checkpoint']={'recorded_utc':TS,'next_action':NEXT,'active_process':None}
tmp=fp.with_suffix('.json.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); tmp.replace(fp)
state=ROOT/'STATE.md'; body=state.read_text(); marker='Active checkpoint 2026-10-19T16:54:09+00:00'
block=f'{marker} (`TX-20261018-0013`, Q-0079): 38/62 exact worker callers reviewed; 24 remain. EV-0573/0574 map tag 0x34 as a deferred Actor/process vector and state update matching its clear-gate producer. Case-local virtual slots +0x18/+0x38 and broader ancestry remain open; no direct HitData/AV11/AV12/UseSkill edge is established. OBJ-1 remains P0 and separate; local caller completion does not resolve the bounty. Next action: {NEXT}\n'
if marker not in body: state.write_text(body.rstrip()+'\n\n'+block)
print('checkpointed caller 39 in FRONTIER.json and STATE.md')
