from __future__ import annotations
import hashlib, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / '.local/ghidra'
CAPTURES = [
    ('gog-query-20261019T164912Z', '0x658660', 0),
    ('gog-query-20261019T165011Z', '0x65b800', 16),
    ('gog-query-20261019T165124Z', '0x659160', 8),
]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
loaded=[]
for stem, rva, incoming in CAPTURES:
    raw=GH/f'{stem}.stdout.raw'; stderr=GH/f'{stem}.stderr.raw'; meta_path=GH/f'{stem}.meta.json'
    meta=json.loads(meta_path.read_text())
    if (not meta.get('ok') or meta.get('requested_rva','').lower()!=rva
        or meta.get('follow_incoming_calls')!=incoming
        or meta.get('analysis_binary_product_version')!='1.6.1179'
        or meta.get('analysis_binary_sha256')!='9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f'):
        raise SystemExit(f'GOG query identity/check failed: {stem}')
    rh, sh, mh = sha(raw), sha(stderr), sha(meta_path)
    if rh!=meta.get('stdout_sha256') or sh!=meta.get('stderr_sha256'):
        raise SystemExit(f'raw capture hash mismatch: {stem}')
    loaded.append((stem,meta,raw,stderr,meta_path,rh,sh,mh))

def hashes(rows):
    out={}
    for _,_,raw,stderr,meta_path,rh,sh,mh in rows:
        out[f'.local/ghidra/{raw.name}']=rh
        out[f'.local/ghidra/{stderr.name}']=sh
        out[f'.local/ghidra/{meta_path.name}']=mh
    return out
base_runtime='GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only query, auto-analysis disabled, no import or overwrite.'
def item(eid, source, primary, tools, coverage, result, related, rows):
    meta=next(x[1] for x in rows if x[0]==primary)
    raw=next(x[2] for x in rows if x[0]==primary)
    return {'kind':'native','edition':'AE','runtime':base_runtime,'modified_state':False,
      'lane':'mechanism_inference','id':eid,'source':source,
      'artifact':f'private-local:.local/ghidra/{raw.name}','sha256':sha(raw),
      'captured_utc':meta['captured_utc'],'tools':['strict Python 3.12 dispatcher',*tools],
      'coverage':coverage,'result':result,'local_hashes':hashes(rows),'related_evidence':related}
rows573=[loaded[0]]
rows574=loaded[1:]
items=[
 item('EV-0573','Identity-checked read-only GOG query of worker caller 38/62 FUN_140658660 and its producer FUN_1406c1d40',CAPTURES[0][0],
   ['tools/ghidra_probe.py --rva 0x658660 --list-call-edges --timeout 600'],
   'FUN_140658660 has one direct edge to the generic worker dispatcher FUN_14065b800, zero indirect sites, and one incoming direct caller FUN_1406c1d40. It builds tag 0x34, retains its object argument through the +0x28 reference counter, and queues the payload. The producer body shows the shared FUN_1406d4110 gate: its clear branch directly updates a process-selected vector from the Actor position, while its set branch submits the same Actor under tag 0x34. The producer also has player-specific coordinate/presentation paths; its full ancestry and dynamic targets are not resolved.',
   'Tag 0x34 is a deferred continuation of an Actor/process update in the captured producer route. The matched clear-gate and queued branches support H69 for this bounded transformation path; the producer body shows no direct mapped HitData, AV11/AV12, UseSkill or quest-gate call. The parent source and dynamic callbacks remain open, so this is not a global combat or armor negative.',
   ['EV-0556','EV-0545','EV-0260'],rows573),
 item('EV-0574','Identity-checked read-only GOG trace of tag-0x34 worker dispatch into FUN_140659160 case 0x34',CAPTURES[1][0],
   ['tools/ghidra_probe.py --rva 0x65b800 --list-call-edges --follow-incoming-calls 16 --timeout 600',
    'tools/ghidra_probe.py --rva 0x659160 --list-call-edges --follow-incoming-calls 8 --timeout 600'],
   'Generic worker FUN_14065b800 has four direct calls, one unresolved virtual site, 95 call xrefs from 64 direct caller functions, and 16 requested caller bodies. If its virtual callback does not consume the event, it calls FUN_140659160. That fallback has one analyzed direct caller, 198 direct calls and 81 indirect sites. Case 0x34 reads the Actor pointer, obtains a process-selected nested object via FUN_140664b20, sends Actor position coordinates through virtual slot +0x18, sends a constant vector through slot +0x38, then clears two fields/bits on the nested object. These two virtual targets are unresolved. The exact FUN_140664b20 Actor/process selection shape is independently captured in EV-0556.',
   'The matched dispatcher case implements a deferred Actor/process vector and state update for tag 0x34. It has no direct call to mapped HitData, ActorValue, UseSkill, armor-protection, or quest-gate code inside that case. The surrounding generic fallback contains many unrelated event cases and must not be attributed to tag 0x34. The two case-local virtual calls and Steam/runtime execution remain open.',
   ['EV-0573','EV-0556','EV-0545','EV-0260'],rows574),
]
epath=ROOT/'research/EVIDENCE.json'; ed=json.loads(epath.read_text()); existing={x['id']:x for x in ed['items']}
for it in items:
    if it['id'] in existing:
        if existing[it['id']].get('sha256')!=it['sha256']: raise SystemExit(f"{it['id']} collision")
    else: ed['items'].append(it)
tmp=epath.with_suffix('.json.tmp'); tmp.write_text(json.dumps(ed,ensure_ascii=False,indent=2)+'\n'); tmp.replace(epath)
def append(path,marker,block):
    p=ROOT/path; s=p.read_text()
    if marker not in s: p.write_text(s.rstrip()+'\n\n'+block.rstrip()+'\n')
append('research/CLAIMS.md','CL-L384','| CL-L384 | In GOG AE 1.6.1179.0, worker caller FUN_140658660 builds tag 0x34 with an Actor object and queues it through FUN_14065b800 when its producer FUN_1406c1d40 sees the shared thread gate; the clear-gate branch performs a matching process-selected vector update. | supported for the exact captured caller/producer flow | [EV-0573], [EV-0574] | The broader producer ancestry and dynamic callback targets remain unresolved; this does not establish a HitData or armor-skill path. |')
append('research/CLAIMS.md','CL-L385','| CL-L385 | In GOG AE 1.6.1179.0, FUN_140659160 case 0x34 obtains an Actor-associated process object through FUN_140664b20, passes Actor coordinates to virtual slot +0x18, passes a constant vector to slot +0x38, and clears process-state fields. | supported for the captured dispatcher case | [EV-0574], [EV-0556] | The two case-local virtual targets and runtime behavior remain unresolved; no direct HitData, AV11/AV12, UseSkill, effective-protection, or quest-gate call occurs in the captured case. |')
append('research/MECHANISMS.md','## M-0135 — tag-0x34 deferred Actor/process vector update (EV-0573/0574)','''## M-0135 — tag-0x34 deferred Actor/process vector update (EV-0573/0574)

In GOG AE 1.6.1179.0, `FUN_140658660` builds tag `0x34` with an Actor pointer and submits it through the shared worker dispatcher. Its only captured direct producer, `FUN_1406c1d40`, uses `FUN_1406d4110`: the clear-gate branch updates an Actor-associated process vector directly; the set-gate branch queues the Actor pointer. Generic worker fallback `FUN_140659160` case `0x34` obtains the associated process-selected nested object using `FUN_140664b20`, passes Actor coordinates to virtual slot `+0x18`, passes a constant vector to slot `+0x38`, and clears object state [EV-0573], [EV-0574], [EV-0556]. This supports a deferred Actor/process vector/state continuation for the captured route. The two virtual targets, broader producer ancestry, and Steam/runtime behavior remain unresolved. No direct HitData, AV11/AV12, `UseSkill`, effective-protection, or quest-gate edge is established; no causal graph edge to the armor-XP or level-one objectives is added. Claims CL-L384–CL-L385.''')
append('experiments/EXP-0128-hit-worker-callers/results.md','### Caller 38/62: tag-0x34 producer and dispatcher (EV-0573/0574)','''### Caller 38/62: tag-0x34 producer and dispatcher (EV-0573/0574)

`FUN_140658660` has one direct edge to `FUN_14065b800`, no indirect sites, and one direct caller `FUN_1406c1d40`. It retains its Actor argument and queues tag `0x34`. The producer uses the shared `FUN_1406d4110` gate: when clear, it directly updates a process-selected vector from Actor coordinates; when set, it submits the same Actor in tag `0x34` [EV-0573]. Worker fallback `FUN_140659160` case `0x34` obtains the Actor-associated process object through `FUN_140664b20`, invokes virtual slots `+0x18` and `+0x38` with Actor coordinates and a constant vector, then clears process-state fields [EV-0574], with the selected nested-object shape independently mapped in EV-0556. The callback targets and broader source ancestry remain unresolved. The exact case has no direct HitData, AV11/AV12, UseSkill, effective-protection or quest-gate edge; unrelated dispatcher cases are not attributed to this path.''')
append('experiments/EXP-0128-hit-worker-callers/hypothesis.md','## Caller 38 competing models','''## Caller 38 competing models

- Q79-H69: tag 0x34 is a deferred Actor/process vector and state update. Prediction: the producer clear-gate path and case 0x34 use the same Actor position and process-selected receiver; supported for the captured route [EV-0573], [EV-0574], [EV-0556].
- Q79-H70: tag 0x34 carries a combat/armor-skill consequence through the case-local virtual calls or an upstream producer. Prediction: resolve a producer-backed virtual target or source path to mapped HitData, AV11/AV12, or UseSkill code. Proposed; no such edge is currently established, and the case-local targets remain unresolved [EV-0573], [EV-0574].''')
append('experiments/EXP-0128-hit-worker-callers/expected-discriminants.md','EV-0573/0574 caller 38 discriminant','''EV-0573/0574 caller 38 discriminant: trace case-0x34 virtual slots +0x18/+0x38 against the exact process-selected object class and compare the producer's clear-gate route. H69 predicts vector/state continuation; H70 requires a source-backed HitData/AV11/AV12/UseSkill edge. Do not infer from unrelated cases in FUN_140659160.''')
append('experiments/EXP-0128-hit-worker-callers/implications.md','Caller 38 bounded no-edge note','''Caller 38 bounded no-edge note: tag 0x34 is a producer/dispatcher pair for an Actor-associated process vector/state update. The handler sits in a generic event fallback that also contains combat-related cases, but those separate switch branches do not create a causal edge to tag 0x34. Preserve the two unresolved case-local virtual calls and avoid a global armor/HitData negative.''')
append('research/KNOWLEDGE_GRAPH.md','EV-0573/0574 adds tag-0x34 Actor/process route','''EV-0573/0574 adds the tag-0x34 Actor/process route: producer FUN_1406c1d40 queues Actor coordinates under the shared gate; fallback case 0x34 uses FUN_140664b20 and virtual slots +0x18/+0x38 to update the process-selected object and clear state. The case-local targets remain unresolved. No causal edge to M-0017 armor mitigation, M-0031 skill awards, or OBJ-1 quest gates is supported.''')
fp=ROOT/'research/FRONTIER.json'; f=json.loads(fp.read_text()); q=next(x for x in f['items'] if x.get('id')=='Q-0079')
q['evidence']=list(dict.fromkeys([*q.get('evidence',[]),'EV-0573','EV-0574']))
q['linked_claims']=list(dict.fromkeys([*q.get('linked_claims',[]),'CL-L384','CL-L385']))
for h in [
 {'id':'Q79-H69','model':'Tag 0x34 is a deferred Actor/process vector and state update.','predicted_discriminant':'The producer clear-gate branch and dispatcher case use Actor coordinates and the same Actor-associated process-selected receiver; case-local virtual slots are +0x18 and +0x38.','status':'supported','evidence':['EV-0573','EV-0574','EV-0556']},
 {'id':'Q79-H70','model':'Tag 0x34 may carry a combat/armor-skill consequence through its case-local virtual calls or upstream producer.','predicted_discriminant':'A producer-backed virtual target/source path reaches mapped HitData, AV11/AV12, or UseSkill code; absent such a path, retain this as unconfirmed rather than inferring it from neighboring switch cases.','status':'proposed','evidence':['EV-0573','EV-0574']},
]:
    by={x['id']:x for x in q['hypotheses']}
    if h['id'] not in by: q['hypotheses'].append(h)
    elif by[h['id']]!=h: raise SystemExit(f"{h['id']} conflict")
for m in ['Trace case-0x34 virtual slots +0x18/+0x38 against the process-selected object class and compare the producer clear-gate route.', 'Continue exact caller inventory at ordinal 39/62: query FUN_1406586a0, then its producer and matched dispatcher case.']:
    if m not in q['methods']: q['methods'].append(m)
assessment='EV-0573/0574 bounds caller 38 as an Actor-associated process vector/state continuation: tag 0x34 queues the same Actor passed to the clear-gate vector update, and case 0x34 writes coordinates/state through process virtual slots +0x18/+0x38. Those targets remain unresolved. No armor/HitData/quest causal edge is added; caller 39/62 FUN_1406586a0 is next.'
if assessment not in q.get('cross_source_assessment',''): q['cross_source_assessment']=q.get('cross_source_assessment','').rstrip()+' '+assessment
tmp=fp.with_suffix('.json.tmp'); tmp.write_text(json.dumps(f,ensure_ascii=False,indent=2)+'\n'); tmp.replace(fp)
print('registered EV-0573/EV-0574; added CL-L384/CL-L385 and Q79-H69/H70')
