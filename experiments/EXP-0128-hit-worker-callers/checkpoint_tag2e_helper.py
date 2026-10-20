from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
rp=ROOT/'research/RECOVERY.json'; fp=ROOT/'research/FRONTIER.json'; sp=ROOT/'STATE.md'
r=json.loads(rp.read_text(encoding='utf-8')); f=json.loads(fp.read_text(encoding='utf-8'))
if r.get('transaction_id')!='TX-20261018-0013' or r.get('frontier_id')!='Q-0079': raise SystemExit('active transaction changed')
now=r['checkpoint_utc']; action=r['next_action']
task=('Q-0079/TX-20261018-0013 active on OBJ-2: caller 37/62 FUN_1406585a0 is bounded as tag 0x2e Actor/process re-entry; 25 callers remain. EV-0567–EV-0571 map its process dword and adjacent shared Health AV0x18 helper. No direct armor-skill route is shown; H66 is supported for the continuation and H67 remains proposed for its parent context.')
f['session_next_action']=action; f['next_action']=action
f['session_checkpoint']={'timestamp_utc':now,'task':task,'next_action':action}
f['last_session_checkpoint']={'recorded_utc':now,'next_action':action,'active_process':None}
t=fp.with_suffix(fp.suffix+'.tmp'); t.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); t.replace(fp)
line=(f'\n\nActive checkpoint {now} (TX-20261018-0013, Q-0079): caller 37/62 is bounded as a tag-0x2e Actor/process continuation; 25 callers remain. EV-0567–EV-0571 map its unnamed process dword and an adjacent Health AV0x18 helper shared with HitData handlers. No direct tag-0x2e armor-skill route is shown; H66 is supported and H67 remains proposed. Next action: {action}')
s=sp.read_text(encoding='utf-8')
if f'Active checkpoint {now} (TX-20261018-0013, Q-0079)' not in s: sp.write_text(s.rstrip()+line+'\n',encoding='utf-8')
print(f'checkpoint synced at {now}; focused helper query is next')
