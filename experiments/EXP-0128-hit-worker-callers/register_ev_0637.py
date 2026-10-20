#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = '9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f'
NEXT = ('Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658cc0 '
        '--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; '
        'review worker caller 56/62 FUN_140658cc0 for its exact tag, payload, producer, '
        'and immediate/deferred behavior, then continue the bounded caller census.')
BASES = [
 '.local/ghidra/gog-query-20261019T205358Z',
 '.local/ghidra/gog-query-20261019T205501Z',
 '.local/ghidra/gog-query-20261019T205606Z',
 '.local/ghidra/gog-query-20261019T205800Z',
]
EXPECTED = {
 '.local/ghidra/gog-query-20261019T205358Z.stdout.raw': 'd0e2844d332f13166ca23cbe2ef1ef6a0b95b50b57dd39b484074e6ab5982989',
 '.local/ghidra/gog-query-20261019T205358Z.meta.json': 'adf51dd871e51f9557c89e1e9adb470e414cf30b8b4a57b636406f0e05d63920',
 '.local/ghidra/gog-query-20261019T205501Z.stdout.raw': 'd3a69e1cf345002a92be4fa51ddb753fc29e9623d47d7c31cee31c02c5c17074',
 '.local/ghidra/gog-query-20261019T205501Z.meta.json': '160cf521c903c80186e961da07d0aec322f4d2119403c34277619ac38c098492',
 '.local/ghidra/gog-query-20261019T205606Z.stdout.raw': '5c011045a572646e498f6ef86a6afc9735738703a72e0737f4ba66bc8a2d6ef4',
 '.local/ghidra/gog-query-20261019T205606Z.meta.json': '2dfdd02b546c7e0c1952b0543e2dd9f195fc17b18e62d16187743b6c3c60ab5c',
 '.local/ghidra/gog-query-20261019T205800Z.stdout.raw': 'f0cd915c1c463cd869e1f5f51bfdcdd8e6c2b5ae3b129d39e01be9aac4fa4c51',
 '.local/ghidra/gog-query-20261019T205800Z.meta.json': '3be397388a6773be9525390ec2b6bef2f5bf5d8ebc427396036baa45e7c0b689',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value): p.write_text(value.rstrip()+'\n', encoding='utf-8', newline='\n')
def append_once(p, marker, body):
    old=p.read_text(encoding='utf-8')
    if marker in old: raise SystemExit('duplicate marker in '+str(p)+': '+marker)
    write(p, old.rstrip()+'\n\n'+body.strip())

def main():
    for rel, expected in EXPECTED.items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=expected: raise SystemExit('capture/hash mismatch: '+rel)
    metas=[json.loads((ROOT/(b+'.meta.json')).read_text(encoding='utf-8')) for b in BASES]
    for m in metas:
        if not (m.get('ok') and m.get('read_only') and m.get('auto_analysis_disabled')
                and m.get('program_executable_path_matches_gog_binary')
                and m.get('analysis_binary_product_version')=='1.6.1179'
                and m.get('analysis_binary_sha256')==GOG_SHA):
            raise SystemExit('capture failed GOG identity/read-only gates')
    raws=[(ROOT/(b+'.stdout.raw')).read_text(encoding='utf-8',errors='replace') for b in BASES]
    caller, producer, dispatcher, registry = raws
    checks=[
      (caller,['OUTGOING_DIRECT_CALL_EDGE_COUNT=1','INDIRECT_CALL_SITE_COUNT=0','local_88[0] = 0x57;','local_80 = param_2;','FUN_14065b800(param_1,local_88);','caller=FUN_14075a430']),
      (producer,['OUTGOING_DIRECT_CALL_EDGE_COUNT=2','INDIRECT_CALL_SITE_COUNT=0','FUN_140658c90(DAT_14319a7c0,param_4);','FUN_140971910(param_4);','FUN_14074b720','FUN_14075a430(0x18,param_3,DAT_142008060,0xfc)','FUN_14075a430(0x19,param_3,DAT_142008078,0xfd)','FUN_14075a430(0x1a,param_3,DAT_142008090,0xfe)','param_2 < param_3']),
      (dispatcher,['case 0x57:','FUN_140971910(param_1[2]);']),
      (registry,['OUTGOING_DIRECT_CALL_EDGE_COUNT=6','INDIRECT_CALL_SITE_COUNT=0','DECOMPILATION_BEGIN=FUN_140971910','FUN_1409786e0(DAT_1420f9d58 + 0x180,1);','FUN_140971e00(&DAT_1431b0b78,local_res8);']),
    ]
    for raw,tokens in checks:
        for token in tokens:
            if token not in raw: raise SystemExit('capture proof missing: '+token)

    ep=ROOT/'research/EVIDENCE.json'
    evidence=json.loads(ep.read_text(encoding='utf-8'))
    ids={r.get('id') for r in evidence.get('items',[])}
    if 'EV-0637' in ids: raise SystemExit('EV-0637 already exists')
    for req in ['EV-0260','EV-0636']:
        if req not in ids: raise SystemExit('missing linked evidence: '+req)
    note=EXP/'EV-0637-caller55-tag57-numeric-threshold-registry-route.md'
    body="""# EV-0637 — Caller 55 tag-0x57 numeric threshold and registry route

## Competing models and discriminants

- H1, ordinary-hit/armor route: tag 0x57 or a descendant performs HitData, effective-protection, AV11/AV12 or UseSkill work. It predicts a producer-backed data/control edge to a mapped combat or skill sink.
- H2, gated numeric-state notification: the producer compares a supplied numeric value with a separate limit, uses per-category state bits, and sends a small code through tag 0x57 to registry handling. It predicts literal category/code pairs, a numeric predicate, a worker dispatcher case, and a registry helper.
- H3, specifically named ActorValue or quest semantics: the literal categories and codes correspond to named game concepts. It predicts corroborating record/source names or a verified consumer mapping; numeric literals alone are insufficient.

## Direct GOG evidence

All captures are from the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata verifies read-only queries, auto-analysis disabled, and matching executable identity. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- FUN_140658c90 writes worker tag 0x57 and copies its 32-bit argument into the following payload field, then calls FUN_14065b800. Its only analyzed direct producer is FUN_14075a430 [EV-0637].
- FUN_14075a430 has two direct calls and no indirect sites. Its predicate is (category != 0x18 or value > 0) and value < limit. When global DAT_1420f7e00+0x160 is nonzero it calls FUN_140971910(code) directly; otherwise it queues tag 0x57 with that code. It returns true on the qualifying route [EV-0637].
- The only analyzed caller of FUN_14075a430 is FUN_14074b720, which calls it for literal categories 0x18, 0x19 and 0x1a with threshold globals DAT_142008060, DAT_142008078 and DAT_142008090, and code values 0xfc, 0xfd and 0xfe. It tests and updates distinct bits 3, 4 and 5 in its receiver field +0xbe4. The captures do not establish the names of these categories or codes, and do not show a previous-value comparison; this is a bounded numeric predicate, not proof of a crossing event [EV-0637].
- Worker dispatcher case 0x57 passes payload field 2 to FUN_140971910 [EV-0637]. That helper has six direct calls and zero indirect sites. Its direct body binary-searches an integer list; when the code is absent and initialization gates pass, it invokes FUN_1409786e0 and inserts the code through FUN_140971e00. No mapped HitData, protection, AV11/AV12 or UseSkill call appears in this bounded helper body [EV-0637].
- The registry helper is also called from 16 other analyzed functions, so the route is a shared registry primitive. This code reuse does not show what named record or runtime object the codes represent [EV-0637].

## Result and limits

H2 is supported for the captured direct route: caller 55 is a gated numeric value/limit notification that carries one of codes 0xfc-0xfe through tag 0x57 to registry handling. H1 has no mapped direct sink in this bounded path. H3 remains unverified: do not label the categories as ActorValues, Health/Magicka/Stamina, quest stages, or achievement codes from these literals alone. The dispatcher has other unresolved cases and registry descendants are not fully traced, so no transitive no-hit, Steam, effective-protection, armor-XP, or bounty conclusion follows. No causal edge is added.

## Next action

Continue worker caller 56/62, FUN_140658cc0, with an exact tag/payload and producer trace.
"""
    write(note,body)
    note_rel=note.relative_to(ROOT).as_posix()
    local={rel:sha(ROOT/rel) for rel in EXPECTED}
    local[note_rel]=sha(note)
    latest=max(metas,key=lambda x:x.get('captured_utc',''))
    evidence['items'].append({
      'captured_utc':latest['captured_utc'],'edition':'AE','modified_state':False,'id':'EV-0637',
      'kind':'native','source':'Identity-checked read-only GOG trace of worker caller 55/tag 0x57, its sole producer, dispatcher case, and numeric registry helper.',
      'artifact':'private-local:'+BASES[0]+'.stdout.raw','sha256':EXPECTED[BASES[0]+'.stdout.raw'],
      'runtime':'GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 '+GOG_SHA+'; existing-project read-only queries, auto-analysis disabled, no import or overwrite. Separate from Steam AE 1.6.1170.0.',
      'lane':'mechanism_inference','tools':['strict Python 3.12 dispatcher','tools/ghidra_probe.py direct call-edge and decompilation queries'],
      'coverage':'Caller 55 builder and sole producer, numeric category/value/limit predicate and bit flags, tag-0x57 dispatcher case, and complete direct census of FUN_140971910.',
      'result':'Caller 55 is a gated numeric value/limit notification carrying codes 0xfc-0xfe through tag 0x57 to a registry helper with six direct calls and no indirect sites. Literal category/code names are unknown. No mapped direct HitData/protection/AV11/AV12/UseSkill sink or causal OBJ-2 edge is established.',
      'local_hashes':local,'related_evidence':['EV-0260','EV-0636'],
    })
    write(ep,json.dumps(evidence,indent=2,ensure_ascii=False))

    append_once(ROOT/'research/CLAIMS.md','| CL-L450 |',
      '| CL-L450 | In GOG AE 1.6.1179.0, worker caller 55 emits tag 0x57 with a numeric code from a value/limit predicate for literal categories 0x18–0x1A; dispatcher case 0x57 passes that code to FUN_140971910, whose six-call direct body performs numeric registry lookup/initialization. | supported for captured direct route | [EV-0637] | Category/code names and downstream effects are unverified; no mapped direct HitData/protection/AV11/AV12/UseSkill sink or OBJ-2 causal edge is established. |')
    append_once(ROOT/'research/MECHANISMS.md','## M-0190 —',
      """## M-0190 — Tag-0x57 gated numeric notification and registry helper (EV-0637)

Caller 55 builder FUN_140658c90 writes tag 0x57 with a supplied 32-bit value. Its sole analyzed producer FUN_14075a430 gates category/value/limit arguments, using distinct literal categories 0x18–0x1A, threshold globals, and codes 0xFC–0xFE; caller FUN_14074b720 updates separate bits at receiver +0xbe4 [EV-0637]. The captured comparisons do not establish a previous-value crossing or the names of these categories/codes.

Dispatcher case 0x57 passes the code to FUN_140971910. Its complete direct census has six calls and zero indirect sites; the bounded body searches an integer list and may initialize/insert the code through FUN_1409786e0 and FUN_140971e00 [EV-0637]. No mapped direct HitData, protection, AV11/AV12 or UseSkill target appears, and no quest/ActorValue interpretation is established. Shared registry code is not a causal edge. Claim CL-L450.""")
    append_once(ROOT/'research/CONTRADICTIONS.md','## C-OBJ2-Q79-TAG57-NUMERIC-REGISTRY-VS-COMBAT',
      """## C-OBJ2-Q79-TAG57-NUMERIC-REGISTRY-VS-COMBAT — value/limit notification versus hit/armor route

- Model A: tag 0x57 or its registry descendants affect HitData, effective protection, AV11/AV12 or UseSkill.
- Model B: caller 55 applies a numeric value/limit predicate and routes one of codes 0xFC–0xFE through a registry helper.
- Evidence: builder/sole producer, literal category and code arguments, per-category state bits, dispatcher case, and six-call/zero-indirect registry-helper census [EV-0637].
- Assessment: B is supported for the captured direct route. A has no mapped direct sink in that bounded path. Literal categories and codes have no verified names, and wider registry descendants remain open. No global no-hit, Steam, armor-XP or bounty conclusion follows.
- Discriminant: map the code's data/record provenance and resolve relevant registry consumers before assigning named quest, ActorValue, combat, or armor semantics.""")
    append_once(ROOT/'research/KNOWLEDGE_GRAPH.md','EV-0637 maps caller 55 tag-0x57 numeric registry route',
      """### EV-0637 maps caller 55 tag-0x57 numeric registry route

Caller 55's sole producer gates literal categories 0x18–0x1A against supplied values and limit globals, sets per-category bits, and submits codes 0xFC–0xFE as tag 0x57 [EV-0637]. Dispatcher case 0x57 reaches FUN_140971910, a six-direct-call, zero-indirect numeric lookup/initialization helper [EV-0637]. Category/code names and downstream meanings are unverified. The bounded direct route has no mapped HitData/protection/AV11/AV12/UseSkill sink. No causal edge is added; continue caller 56/62 FUN_140658cc0.""")
    append_once(EXP/'results.md','### Caller 55/62: gated numeric tag-0x57 registry notification (EV-0637)',
      """### Caller 55/62: gated numeric tag-0x57 registry notification (EV-0637)

Caller 55 FUN_140658c90 writes tag 0x57 with a supplied 32-bit code. Its sole producer FUN_14075a430 checks a category/value/limit predicate; caller FUN_14074b720 supplies categories 0x18–0x1A, threshold globals, codes 0xFC–0xFE, and separate state bits at +0xbe4 [EV-0637]. This does not prove a threshold crossing or identify the literal categories.

The dispatcher passes the code to FUN_140971910, whose complete direct census has six edges and no indirect sites; its bounded body performs numeric-list lookup and gated registry initialization [EV-0637]. No direct mapped combat/armor sink or causal OBJ-2 edge is established. Caller 55 is bounded; continue caller 56/62 FUN_140658cc0.""")

    fp=ROOT/'research/FRONTIER.json'
    frontier=json.loads(fp.read_text(encoding='utf-8'))
    item=next(x for x in frontier['items'] if x.get('id')=='Q-0079')
    hids={x.get('id') for x in item.get('hypotheses',[])}
    if {'Q79-H151','Q79-H152'} & hids: raise SystemExit('caller-55 hypotheses already exist')
    item['hypotheses'].extend([
      {'id':'Q79-H151','model':'Caller 55 is a gated numeric value/limit notification: literal categories 0x18–0x1A and codes 0xFC–0xFE feed tag 0x57, whose dispatcher case enters FUN_140971910 numeric registry lookup/initialization.','predicted_discriminant':'The builder, sole producer, dispatcher case and complete direct census show the bounded numeric predicate and registry path; literal categories, code meanings and wider consumers remain unnamed.','status':'supported','evidence':['EV-0637']},
      {'id':'Q79-H152','model':'Caller 55 literal categories/codes name ActorValues, quest/milestone conditions, combat notifications, or another specific game-facing concept that connects the registry update to bounty targets.','predicted_discriminant':'Resolve verified record/source names or producer-backed registry consumers linking categories/codes to a specific named system; numeric literals and shared registry code alone do not establish semantics or causality.','status':'proposed','evidence':['EV-0637','EV-0260']},
    ])
    item['evidence']=list(dict.fromkeys([*item.get('evidence',[]),'EV-0637']))
    item['linked_claims']=list(dict.fromkeys([*item.get('linked_claims',[]),'CL-L450']))
    item['next_action']=NEXT
    frontier['session_next_action']=NEXT
    frontier['next_action']=NEXT
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    frontier['session_checkpoint']={'timestamp_utc':now,'task':'Q-0079/TX-20261018-0013: caller 55/tag-0x57 is bounded as a gated numeric notification into a registry helper; continue caller 56.','next_action':NEXT}
    frontier['last_session_checkpoint']={'recorded_utc':now,'next_action':NEXT,'active_process':'TX-20261018-0013'}
    write(fp,json.dumps(frontier,indent=2,ensure_ascii=False))

    sp=ROOT/'STATE.md'
    state=sp.read_text(encoding='utf-8')
    old='Q-0079/TX-20261018-0013 remains active on OBJ-2: 55 of 62 initially uninspected worker callers are reviewed, with 7 remaining.'
    new='Q-0079/TX-20261018-0013 remains active on OBJ-2: 56 of 62 initially uninspected worker callers are reviewed, with 6 remaining.'
    if state.count(old)!=1: raise SystemExit('STATE active caller count mismatch')
    state=state.replace(old,new,1)
    oldev='EV-0636 bounds caller 54/tag 0x54 as a spatial/context Actor update with tag-0x32 immediate/deferred slot +0x328 convergence; 21 target virtual sites remain open, with no direct mapped HitData/armor sink.'
    if state.count(oldev)!=1: raise SystemExit('STATE caller-54 summary mismatch')
    state=state.replace(oldev,oldev+' EV-0637 bounds caller 55/tag 0x57 as a gated numeric value/limit notification into a six-call registry helper; literal category/code names remain unknown, with no direct mapped HitData/armor sink.',1)
    state=state.replace('Q-0079 has 55/62 initially uninspected worker callers reviewed; 7 remain.','Q-0079 has 56/62 initially uninspected worker callers reviewed; 6 remain.',1)
    tick=chr(96)
    oldnext=('**Selected next line:** run '+tick+'python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658c90 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600'+tick+'; review worker caller 55/62 '+tick+'FUN_140658c90'+tick+' for its exact tag/payload and producer, then continue the bounded caller census. Caller 54'+chr(39)+'s tag-0x54 target has 21 unresolved virtual sites and no direct mapped HitData/armor sink.')
    newnext=('**Selected next line:** run '+tick+'python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658cc0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600'+tick+'; review worker caller 56/62 '+tick+'FUN_140658cc0'+tick+' for its exact tag, payload, producer and immediate/deferred behavior, then continue the bounded caller census. Caller 55'+chr(39)+'s tag-0x57 route is a numeric registry notification with unnamed codes/categories and no direct mapped HitData/armor sink.')
    if state.count(oldnext)!=1: raise SystemExit('STATE selected-next line mismatch')
    state=state.replace(oldnext,newnext,1)
    write(sp,state)

    append_once(ROOT/'research/ROADMAP.md','## Cross-domain synthesis — Q-0079 caller 55 (EV-0637)',
      """## Cross-domain synthesis — Q-0079 caller 55 (EV-0637)

Caller 54's tag-0x54 branch is spatial/context Actor state work with nested-state and object-tree helper reuse [EV-0636]; caller 55 is a distinct numeric value/limit notification into tag-0x57 registry lookup [EV-0637]. These worker routes share dispatcher infrastructure but have different producer payloads and consumers. Caller-55 literals 0x18–0x1A and 0xFC–0xFE do not establish named ActorValues, quest conditions, or resource events. No causal edge to HitData/protection/AV11/AV12/UseSkill or the level-one quest objective is added. The clean Steam matched-hit/protection/raw-AVSK test remains outstanding [EV-0260]. Continue caller 56/62 FUN_140658cc0.""")
    print('Registered EV-0637/CL-L450/M-0190, added bounded numeric-registry hypotheses, and checkpointed caller 56.')

if __name__=='__main__': main()

