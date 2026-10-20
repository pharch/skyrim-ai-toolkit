from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
GH=ROOT/'.local/ghidra'; stem='gog-query-20261019T164548Z'
raw=GH/f'{stem}.stdout.raw'; stderr=GH/f'{stem}.stderr.raw'; meta_path=GH/f'{stem}.meta.json'
meta=json.loads(meta_path.read_text());
if not meta.get('ok') or meta.get('requested_rva','').lower()!='0x8044e0' or meta.get('follow_incoming_calls')!=12 or meta.get('analysis_binary_product_version')!='1.6.1179': raise SystemExit('GOG query identity/check failed')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rh,sh,mh=sha(raw),sha(stderr),sha(meta_path)
if rh!=meta['stdout_sha256'] or sh!=meta['stderr_sha256']: raise SystemExit('raw capture hash mismatch')
item={
 'kind':'native','edition':'AE','runtime':'GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.',
 'modified_state':False,'lane':'mechanism_inference','id':'EV-0572',
 'source':'Identity-checked read-only GOG direct/incoming-call analysis of shared helper FUN_1408044e0',
 'artifact':f'private-local:.local/ghidra/{raw.name}','sha256':rh,'captured_utc':meta['captured_utc'],
 'tools':['strict Python 3.12 dispatcher','tools/ghidra_probe.py --rva 0x8044e0 --list-call-edges --follow-incoming-calls 12 --timeout 600'],
 'coverage':'FUN_1408044e0 has 22 outgoing direct calls, three indirect sites, and 13 direct callsites from 12 caller functions; all 12 caller bodies were requested. Direct callers include tag-0x2e handler FUN_14068b3a0, HitData handler FUN_1406b9df0 (two sites), and FUN_1406bc400. The tag-0x2e call uses (source-data=0, mode=3, code=0x1d, flag=0, extra=0); FUN_1406b9df0 uses code 0x1d with nonnull source data, flag 1, and a nonnull final pointer at one site, plus a separate code-0x23 call. Three dynamic sites and descendants remain unresolved.',
 'result':'The shared helper identity does not establish shared HitData payload semantics. The captured tag-0x2e call passes no source data and a clear flag; the HitData code-0x1d call passes a data pointer and sets the flag. FUN_1408044e0 has no direct edge to mapped ActorValue/UseSkill/armor-skill sinks, but its three virtual sites remain open.',
 'local_hashes':{f'.local/ghidra/{raw.name}':rh,f'.local/ghidra/{stderr.name}':sh,f'.local/ghidra/{meta_path.name}':mh},
 'related_evidence':['EV-0570','EV-0571','EV-0294','EV-0260']}

epath=ROOT/'research/EVIDENCE.json'; ed=json.loads(epath.read_text()); old={x['id']:x for x in ed['items']}
if 'EV-0572' in old:
 if old['EV-0572'].get('sha256')!=rh: raise SystemExit('EV-0572 collision')
else: ed['items'].append(item)
tmp=epath.with_suffix('.json.tmp'); tmp.write_text(json.dumps(ed,ensure_ascii=False,indent=2)+'\n'); tmp.replace(epath)
def append(path,marker,block):
 p=ROOT/path; s=p.read_text()
 if marker not in s: p.write_text(s.rstrip()+'\n\n'+block.rstrip()+'\n')
append('research/CLAIMS.md','CL-L383','| CL-L383 | In GOG AE 1.6.1179.0, tag-0x2e handler FUN_14068b3a0 calls shared FUN_1408044e0 with event code 0x1d but null source-data/final pointers and flag 0; FUN_1406b9df0 calls the same code with nonnull data/final pointer and flag 1, plus a separate code-0x23 call. | supported for exact captured callsites and differing arguments | [EV-0572], [EV-0570] | FUN_1408044e0 has three unresolved dynamic sites; common helper identity does not establish HitData semantics or an armor-skill effect. |')
append('research/MECHANISMS.md','## M-0134 addendum — shared effect helper parameter distinction (EV-0572)','''## M-0134 addendum — shared effect helper parameter distinction (EV-0572)

FUN_14068b3a0 selects FUN_1408044e0 with mode 3/code 0x1d, but passes zero for both source-data and final-pointer arguments and flag 0. The mapped HitData handler FUN_1406b9df0 calls the same helper with code 0x1d plus a nonnull source-data pointer, flag 1, and a nonnull final pointer at one captured site; it also calls code 0x23 separately [EV-0572]. FUN_1408044e0 has 22 direct calls and three unresolved dynamic sites. This is a shared helper with different argument paths, not proof that the tag-0x2e event carries HitData or invokes armor skill. Keep H67 proposed only for its broader upstream source context; no direct tag-0x2e-to-AV11/AV12/UseSkill edge is added. Claim CL-L383.''')
append('experiments/EXP-0128-hit-worker-callers/results.md','### Shared code-0x1d helper argument comparison (EV-0572)','''### Shared code-0x1d helper argument comparison (EV-0572)

`FUN_1408044e0` has 22 direct calls, three indirect sites, and 12 distinct direct callers. Its tag-0x2e call from `FUN_14068b3a0` uses mode 3/code 0x1d with null source-data and final-pointer arguments and flag 0. The HitData handler `FUN_1406b9df0` calls the same code with a nonnull source-data pointer, flag 1 and a nonnull final pointer at a separate site; it also calls code 0x23 [EV-0572]. Thus the shared helper is a real cross-system edge, while the captured payload forms differ. This narrows but does not eliminate the possibility that one upstream parent of tag 0x2e is hit-adjacent. The helper's dynamic sites and descendants remain open; no direct armor-skill consequence is shown.''')
append('experiments/EXP-0128-hit-worker-callers/hypothesis.md','- Q79-H68: tag-0x2e reuses FUN_1408044e0 with null source data','''- Q79-H68: tag-0x2e reuses shared FUN_1408044e0 code 0x1d as a generic state/effect operation, not as a HitData payload. Prediction: its null source-data/final-pointer arguments and clear flag distinguish it from the FUN_1406b9df0 code-0x1d call, which supplies data and flag 1. Supported for captured callsites; three dynamic sites remain open [EV-0572].''')
append('experiments/EXP-0128-hit-worker-callers/expected-discriminants.md','EV-0572 discriminant','''EV-0572 discriminant: tag 0x2e and HitData both call FUN_1408044e0 with code 0x1d, but their source-data/final-pointer arguments and flag differ. Resolve the three dynamic sites only if producer-backed evidence can show the tag-0x2e null-data path reaches a HitData/AV11/AV12/UseSkill sink; otherwise retain H66 for the bounded state/effect route and H67 only as an upstream-source possibility.''')
append('experiments/EXP-0128-hit-worker-callers/implications.md','Caller 37 helper-sharing note','''Caller 37 helper-sharing note: FUN_1408044e0 joins tag-0x2e process state with HitData and ActorValue-related callers, but tag 0x2e supplies null source data and a clear flag where the mapped HitData caller supplies data and sets the flag. Common function identity is not enough for a shared combat mechanism; preserve this argument distinction in future synthesis.''')
append('research/KNOWLEDGE_GRAPH.md','EV-0572 refines shared FUN_1408044e0 edges','''EV-0572 refines shared FUN_1408044e0 edges: tag-0x2e FUN_14068b3a0 and HitData FUN_1406b9df0 both call the helper with code 0x1d, but the former supplies null source-data/final-pointer arguments and flag 0 while the latter supplies event data/final pointer and flag 1. Retain the shared function edge and distinct argument edges; do not collapse them into a HitData or armor-skill causal edge. Three dynamic sites remain unresolved.''')
fp=ROOT/'research/FRONTIER.json'; f=json.loads(fp.read_text()); q=next(x for x in f['items'] if x.get('id')=='Q-0079')
q['evidence']=list(dict.fromkeys([*q.get('evidence',[]),'EV-0572']))
q['linked_claims']=list(dict.fromkeys([*q.get('linked_claims',[]),'CL-L383']))
h={'id':'Q79-H68','model':'Tag 0x2e reuses shared FUN_1408044e0 code 0x1d as a generic state/effect operation with no HitData payload.',
   'predicted_discriminant':'The tag-0x2e caller supplies null source-data/final-pointer arguments and flag 0, whereas the FUN_1406b9df0 HitData call supplies event data/final pointer and flag 1. Dynamic descendants remain open.',
   'status':'supported','evidence':['EV-0572','EV-0570']}
by={x['id']:x for x in q['hypotheses']}
if 'Q79-H68' not in by:q['hypotheses'].append(h)
elif by['Q79-H68']!=h:raise SystemExit('Q79-H68 conflict')
method='Compare producer-backed argument tuples for the shared FUN_1408044e0 event code 0x1d; preserve null source-data versus HitData pointer and flag differences.'
if method not in q['methods']:q['methods'].append(method)
assessment='EV-0572 shows tag 0x2e and HitData share FUN_1408044e0 code 0x1d only at function identity: tag 0x2e passes null data/final pointers and flag 0, while FUN_1406b9df0 passes data and flag 1. The three dynamic sites remain open, but no direct HitData/armor-skill edge follows.'
if assessment not in q.get('cross_source_assessment',''):q['cross_source_assessment']=q.get('cross_source_assessment','').rstrip()+' '+assessment
tmp=fp.with_suffix('.json.tmp');tmp.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n');tmp.replace(fp)
print('registered EV-0572; added CL-L383 and Q79-H68 argument distinction')
