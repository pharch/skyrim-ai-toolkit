from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; GH=ROOT/'.local/ghidra'
CAPTURES=[
 ('gog-query-20261019T165450Z','0x6586a0',0,0),
 ('gog-query-20261019T165644Z','0x7bc1f0',0,8),
 ('gog-query-20261019T165742Z','0xea04c0',8,12),
 ('gog-query-20261019T165011Z','0x65b800',0,16),
 ('gog-query-20261019T165124Z','0x659160',0,8),
]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for stem,rva,direct,incoming in CAPTURES:
 raw=GH/f'{stem}.stdout.raw'; stderr=GH/f'{stem}.stderr.raw'; mp=GH/f'{stem}.meta.json'; meta=json.loads(mp.read_text())
 if (not meta.get('ok') or meta.get('requested_rva','').lower()!=rva or meta.get('follow_direct_calls')!=direct or meta.get('follow_incoming_calls')!=incoming or meta.get('analysis_binary_product_version')!='1.6.1179' or meta.get('analysis_binary_sha256')!='9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f'):
  raise SystemExit(f'identity/query check failed: {stem}')
 rh,sh,mh=sha(raw),sha(stderr),sha(mp)
 if rh!=meta.get('stdout_sha256') or sh!=meta.get('stderr_sha256'): raise SystemExit(f'raw hash mismatch: {stem}')
 rows.append((stem,meta,raw,stderr,mp,rh,sh,mh))
def local_hashes(selected):
 d={}
 for _,_,raw,stderr,mp,rh,sh,mh in selected:
  d[f'.local/ghidra/{raw.name}']=rh; d[f'.local/ghidra/{stderr.name}']=sh; d[f'.local/ghidra/{mp.name}']=mh
 return d
runtime='GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.'
def mk(eid,source,primary,tools,coverage,result,related,selected):
 row=next(x for x in selected if x[0]==primary); meta=row[1]; raw=row[2]
 return {'kind':'native','edition':'AE','runtime':runtime,'modified_state':False,'lane':'mechanism_inference','id':eid,'source':source,'artifact':f'private-local:.local/ghidra/{raw.name}','sha256':row[5],'captured_utc':meta['captured_utc'],'tools':['strict Python 3.12 dispatcher',*tools],'coverage':coverage,'result':result,'local_hashes':local_hashes(selected),'related_evidence':['EV-0556','EV-0545','EV-0574','EV-0260']}
items=[
 mk('EV-0575','Identity-checked read-only GOG analysis of worker caller 39/62 FUN_1406586a0 and both producer bodies',CAPTURES[0][0],
  ['tools/ghidra_probe.py --rva 0x6586a0 --list-call-edges --timeout 600','tools/ghidra_probe.py --rva 0x7bc1f0 --list-call-edges --follow-incoming-calls 8 --timeout 600'],
  'FUN_1406586a0 has one outgoing direct call to FUN_14065b800, zero indirect sites, and two observed direct producer functions FUN_1407bc060/FUN_1407bc1f0. It retains the first object via its +0x28 counter, optionally retains the second at +0x8, writes tag 0x35, and queues both pointers. FUN_1407bc060 uses the shared FUN_1406d4110 gate and queues a null second pointer or directly calls FUN_140ea04c0(FUN_140664b20(Actor),0). FUN_1407bc1f0 conditionally obtains a second pointer with FUN_1402b8b60, updates process-associated position/state, then queues the Actor and optional pointer or directly calls FUN_140ea04c0 with the same values. Its full body has 9 direct calls, 3 indirect sites, and no analyzed incoming direct caller.',
  'Caller 39 is a gated Actor/process object-update builder with two producer families and an optional payload object. The producers show coordinate/process-state work around the event, but the optional object type and virtual targets are not resolved. No direct mapped HitData/AV11/AV12/UseSkill sink appears in the builder/producer bodies; no global combat negative follows.',
  ['EV-0556','EV-0545','EV-0260'],rows[:2]),
 mk('EV-0576','Identity-checked read-only GOG analysis of tag-0x35 dispatcher case and shared FUN_140ea04c0 target',CAPTURES[2][0],
  ['tools/ghidra_probe.py --rva 0x659160 --list-call-edges --follow-incoming-calls 8 --timeout 600','tools/ghidra_probe.py --rva 0xea04c0 --list-call-edges --follow-direct-calls 8 --follow-incoming-calls 12 --timeout 600'],
  'Fallback dispatcher FUN_140659160 case 0x35 obtains the Actor-associated nested object through FUN_140664b20, invokes FUN_140ea04c0 with the optional second payload, and releases retained references. FUN_140ea04c0 has no direct calls, three unresolved indirect sites, and nine callsites from eight caller functions. It asks the receiver virtual slot +0x78 for a current object; when that differs from the supplied object, it conditionally calls nested slots +0x150 (old object) and +0x148 (new object), then tail-dispatches receiver slot +0x70 with the supplied object. The receiver/nested object types and all four dynamic targets remain unresolved. Case 0x37 and other callers share FUN_140ea04c0 but have distinct surrounding contexts.',
  'The bounded tag-0x35 route is a gated process-associated object replacement/update with reference management and a final virtual continuation, not a demonstrated HitData or armor-skill path. Common helper identity across tags/callers does not assign the optional object a combat meaning. No direct HitData, ActorValue, UseSkill, effective-protection, or quest-gate edge is established inside this case/helper body; the dynamic callbacks remain open.',
  ['EV-0575','EV-0556','EV-0545','EV-0260'],[rows[2],rows[3],rows[4]])
]
ep=ROOT/'research/EVIDENCE.json'; data=json.loads(ep.read_text()); old={x['id']:x for x in data['items']}
for it in items:
 if it['id'] in old:
  if old[it['id']].get('sha256')!=it['sha256']: raise SystemExit(f"{it['id']} collision")
 else: data['items'].append(it)
tmp=ep.with_suffix('.json.tmp'); tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n'); tmp.replace(ep)
def append(rel,marker,block):
 p=ROOT/rel; s=p.read_text()
 if marker not in s: p.write_text(s.rstrip()+'\n\n'+block.rstrip()+'\n')
append('research/CLAIMS.md','CL-L386','| CL-L386 | In GOG AE 1.6.1179.0, worker caller FUN_1406586a0 builds tag 0x35 with two reference-counted pointers and has two observed producers, FUN_1407bc060 and FUN_1407bc1f0; both use the shared gate to choose queued versus direct FUN_140ea04c0 execution on an Actor-associated process object. | supported for the captured builder/producer flows | [EV-0575], [EV-0576] | The optional pointer’s concrete type and the three target helper virtuals remain unresolved; no combat or armor-skill consequence is established. |')
append('research/CLAIMS.md','CL-L387','| CL-L387 | In GOG AE 1.6.1179.0, FUN_140ea04c0 compares the receiver’s current virtual-slot-0x78 object with its argument, conditionally calls nested virtual slots +0x150/+0x148 to process differing old/new objects, then tail-dispatches receiver slot +0x70; tag-0x35 supplies the Actor-associated process object and optional payload. | supported for the exact captured helper/callsite flow | [EV-0576], [EV-0575] | All targets are dynamic; other callers include distinct contexts, so shared helper identity does not imply tag-0x35 combat, armor, or quest semantics. |')
append('research/MECHANISMS.md','## M-0136 — tag-0x35 process-associated object update (EV-0575/0576)','''## M-0136 — tag-0x35 process-associated object update (EV-0575/0576)

In GOG AE 1.6.1179.0, `FUN_1406586a0` creates a reference-managed tag-`0x35` payload containing an Actor-associated object and an optional second pointer. Its two captured producers, `FUN_1407bc060` and `FUN_1407bc1f0`, use `FUN_1406d4110` to choose queued tag delivery or direct execution of `FUN_140ea04c0` against the object selected by `FUN_140664b20` [EV-0575], [EV-0556]. Dispatcher case `0x35` returns the optional pointer to that helper and releases retained references [EV-0576]. The helper compares a receiver's current object through virtual slot `+0x78`, conditionally invokes nested-object slots `+0x150`/`+0x148` for differing old/new objects, and tail-dispatches receiver slot `+0x70`; targets and concrete object types are unresolved. Another dispatcher case and other callers use the same helper in different contexts, so no common combat semantics follow. No direct HitData, ActorValue, `UseSkill`, protection, or quest-gate edge is established. Keep Q79-H71 supported only as a bounded object-update model and H72 proposed for the unresolved dynamic path; add no causal graph edge to M-0017 or OBJ-1. Claims CL-L386–CL-L387.''')
append('experiments/EXP-0128-hit-worker-callers/results.md','### Caller 39/62: tag-0x35 producer and process object update (EV-0575/0576)','''### Caller 39/62: tag-0x35 producer and process object update (EV-0575/0576)

`FUN_1406586a0` retains an Actor-associated pointer and optional object, writes tag `0x35`, and queues both. Producers `FUN_1407bc060` and `FUN_1407bc1f0` use the shared thread gate; clear branches call `FUN_140ea04c0(FUN_140664b20(Actor),payload)`, while set branches queue the same pointer tuple [EV-0575]. The second producer builds Actor/process position/state and conditionally supplies an optional pointer. Dispatcher case `0x35` calls the same helper with the two payload values and releases references [EV-0576]. `FUN_140ea04c0` compares the receiver's current object through virtual slot `+0x78`, may dispatch nested old/new object slots `+0x150`/`+0x148`, then tail-calls receiver slot `+0x70`; it has three indirect sites and no direct calls. Concrete types and dynamic targets remain unknown. No direct HitData/AV11/AV12/UseSkill/protection/quest-gate edge is established in this case/helper; unrelated callers and neighboring event cases are not attributed to tag 0x35.''')
append('experiments/EXP-0128-hit-worker-callers/hypothesis.md','## Caller 39 competing models','''## Caller 39 competing models

- Q79-H71: tag 0x35 is a deferred Actor-associated process object update/replacement. Prediction: producer gate branches converge on FUN_140ea04c0 with the same process-selected receiver and optional pointer; the helper compares, releases/replaces, and forwards the object. Supported for the captured static route; object type and dynamic callbacks remain unresolved [EV-0575], [EV-0576], [EV-0556].
- Q79-H72: the optional object or final virtual callback carries a combat/armor-skill consequence. Prediction: a producer-backed dynamic target reaches mapped HitData, AV11/AV12, or UseSkill code. Proposed; no such edge is presently established [EV-0575], [EV-0576].''')
append('experiments/EXP-0128-hit-worker-callers/expected-discriminants.md','EV-0575/0576 caller 39 discriminant','''EV-0575/0576 caller 39 discriminant: resolve the type and target for FUN_140ea04c0 receiver slots +0x78/+0x70 and nested slots +0x148/+0x150 from the object returned by FUN_140664b20. H71 predicts a process object update/replacement; H72 requires a source-backed HitData/AV11/AV12/UseSkill edge. Keep case 0x37 and other shared-helper callers separate.''')
append('experiments/EXP-0128-hit-worker-callers/implications.md','Caller 39 shared-helper note','''Caller 39 shared-helper note: FUN_140ea04c0 is shared across tag 0x35, tag 0x37, and other callers, but the captured contexts and payloads differ. Its three indirect sites carry the remaining type/behavior uncertainty. Treat the common helper as an object-update primitive only for the bounded flow; do not infer HitData, armor XP, or level-gate behavior from function identity.''')
append('research/KNOWLEDGE_GRAPH.md','EV-0575/0576 adds tag-0x35 object-update route','''EV-0575/0576 adds tag-0x35 object-update route: two producers choose queued or direct FUN_140ea04c0 execution on the FUN_140664b20 Actor-associated object; the helper compares the current optional object and conditionally invokes dynamic old/new-object methods before a final virtual continuation. Concrete types and targets remain unresolved. No causal edge to M-0017 armor mitigation, M-0031 skill awards, or OBJ-1 quest gates is supported.''')
fp=ROOT/'research/FRONTIER.json'; f=json.loads(fp.read_text()); q=next(x for x in f['items'] if x.get('id')=='Q-0079')
q['evidence']=list(dict.fromkeys([*q.get('evidence',[]),'EV-0575','EV-0576']))
q['linked_claims']=list(dict.fromkeys([*q.get('linked_claims',[]),'CL-L386','CL-L387']))
for h in [
 {'id':'Q79-H71','model':'Tag 0x35 is a deferred Actor-associated process object update/replacement.','predicted_discriminant':'Both producer gate branches converge on FUN_140ea04c0 with the Actor-associated object and optional pointer; the helper compares current/new objects and forwards via dynamic virtual slots.','status':'supported','evidence':['EV-0575','EV-0576','EV-0556']},
 {'id':'Q79-H72','model':'The optional object or final virtual callback may carry a combat/armor-skill consequence.','predicted_discriminant':'A producer-backed target for FUN_140ea04c0 slots +0x78/+0x70 or nested slots +0x148/+0x150 resolves to mapped HitData, AV11/AV12, or UseSkill code.','status':'proposed','evidence':['EV-0575','EV-0576']},
]:
 by={x['id']:x for x in q['hypotheses']}
 if h['id'] not in by: q['hypotheses'].append(h)
 elif by[h['id']]!=h: raise SystemExit(f"{h['id']} conflict")
for m in ['Resolve FUN_140ea04c0 receiver virtual slots +0x78/+0x70 and nested slots +0x148/+0x150 from the process-selected receiver type.','Continue exact caller inventory at ordinal 40/62: query FUN_1406586f0, then its producer and matched dispatcher case.']:
 if m not in q['methods']: q['methods'].append(m)
assessment='EV-0575/0576 map caller 39 as tag-0x35 Actor-associated object replacement/update: its two producers select queued/direct FUN_140ea04c0 paths and case 0x35 returns the optional pointer to the helper. The helper has three unresolved dynamic sites and is shared by distinct callers. No armor/HitData/quest causal edge is established; caller 40/62 FUN_1406586f0 is next.'
if assessment not in q.get('cross_source_assessment',''): q['cross_source_assessment']=q.get('cross_source_assessment','').rstrip()+' '+assessment
tmp=fp.with_suffix('.json.tmp'); tmp.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n'); tmp.replace(fp)
print('registered EV-0575/EV-0576; added CL-L386/CL-L387 and Q79-H71/H72')
