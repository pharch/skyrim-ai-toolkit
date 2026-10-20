from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TS='2026-10-19T17:00:17+00:00'
NEXT='Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6586f0 --list-call-edges --timeout 600; inspect exact caller 40/62 producer, tag payload, matched dispatcher case, and any direct HitData/ActorValue/armor-skill edges. Keep the clean Steam matched-hit/protection/raw AVSK requirement and GOG/Steam build boundary explicit.'
TASK='Q-0079/TX-20261018-0013 active on OBJ-2: caller 39/62 FUN_1406586a0 is bounded as a reference-managed tag-0x35 Actor/process object update with two producers and an optional object; 23 exact worker callers remain. EV-0575/0576 map gate-selected direct/queued FUN_140ea04c0 flows. Its nested/receiver virtual targets and object type remain unresolved. H71 is supported for the bounded update; H72 remains proposed for possible dynamic combat/skill descendants. OBJ-1 remains P0 and independent; caller completion does not resolve the bounty.'
fp=ROOT/'research/FRONTIER.json'; data=json.loads(fp.read_text())
data['session_next_action']=NEXT; data['next_action']=NEXT
data['session_checkpoint']={'timestamp_utc':TS,'task':TASK,'next_action':NEXT}
data['last_session_checkpoint']={'recorded_utc':TS,'next_action':NEXT,'active_process':None}
tmp=fp.with_suffix('.json.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); tmp.replace(fp)
state=ROOT/'STATE.md'; body=state.read_text(); marker='Active checkpoint 2026-10-19T17:00:17+00:00'
block=f'{marker} (`TX-20261018-0013`, Q-0079): 39/62 exact worker callers reviewed; 23 remain. EV-0575/0576 map tag 0x35 as a reference-managed Actor/process object update with two producers and an optional object. FUN_140ea04c0 compares/replaces object pointers through unresolved virtual slots +0x78/+0x148/+0x150/+0x70; H71 is supported for the bounded route and H72 remains proposed. OBJ-1 remains P0 and separate; local caller completion does not resolve the bounty. Next action: {NEXT}\n'
if marker not in body: state.write_text(body.rstrip()+'\n\n'+block)
print('checkpointed caller 40 in FRONTIER.json and STATE.md')
