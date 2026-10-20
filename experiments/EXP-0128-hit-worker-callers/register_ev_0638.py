#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
EXP=Path(__file__).resolve().parent
GOG_SHA='9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f'
NEXT=('Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658d00 '
      '--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; '
      'review worker caller 57/62 FUN_140658d00 for its exact tag, payload and producer, '
      'then continue the bounded caller census.')
BASES=[
 '.local/ghidra/gog-query-20261019T210749Z',
 '.local/ghidra/gog-query-20261019T210855Z',
 '.local/ghidra/gog-query-20261019T211008Z',
 '.local/ghidra/gog-query-20261019T211120Z',
 '.local/ghidra/gog-query-20261019T211230Z',
 '.local/ghidra/gog-query-20261019T211346Z',
 '.local/ghidra/gog-query-20261019T211445Z',
 '.local/ghidra/gog-query-20261019T211542Z',
 '.local/ghidra/gog-query-20261019T211653Z',
 '.local/ghidra/gog-query-20261019T211754Z',
 '.local/ghidra/gog-query-20261019T211852Z',
 '.local/ghidra/gog-query-20261019T212000Z',
]
EXPECTED={
 '.local/ghidra/gog-query-20261019T210749Z.stdout.raw':'bb50ac8bd3cd6317cb2215d27ba8391ef6fb1beb997ad4e7558c7e30cec93fa8',
 '.local/ghidra/gog-query-20261019T210749Z.meta.json':'406d9e03740c0536be7ee4787f9645a2790936a3d98182f1b59a78b1084a5333',
 '.local/ghidra/gog-query-20261019T210855Z.stdout.raw':'ad8ec816232a9211ef2b59142f81225de2eaff58dcb00916bbfd3e5a2aeed973',
 '.local/ghidra/gog-query-20261019T210855Z.meta.json':'7e22f9506e0450841a72e94c1aa8c78967e211f072c273a441900f53ed92e540',
 '.local/ghidra/gog-query-20261019T211008Z.stdout.raw':'6a77ede58c772cced22ff316a546f6636e662e81a70f40553cdd13539ff41672',
 '.local/ghidra/gog-query-20261019T211008Z.meta.json':'a53583324dbcbc340c0fc0be13efcf7ee111bff7a0f2d847a947dae912833308',
 '.local/ghidra/gog-query-20261019T211120Z.stdout.raw':'bd34aead1073b1fc1197f9497faab51bdf78c17195e8bf0d4181c7f5eb625756',
 '.local/ghidra/gog-query-20261019T211120Z.meta.json':'c8ae8397ef94f43f501137632152022cec209d8a1a8cfeaaad9239c5c3806810',
 '.local/ghidra/gog-query-20261019T211230Z.stdout.raw':'47842314e422e5a95d97d9b4bf48e939c7f62e0da230e85e15ed676e53c46cab',
 '.local/ghidra/gog-query-20261019T211230Z.meta.json':'8fdf5c528068420e4b404e788860490aeb1283b6da6557f896c541d6f6cc84c2',
 '.local/ghidra/gog-query-20261019T211346Z.stdout.raw':'259714b76dca5d2028c1f16de4309cc7df3093846bd1fb2415ad2403f3eb8eb5',
 '.local/ghidra/gog-query-20261019T211346Z.meta.json':'fe378bf7f20949adfc631139015ed64c3af4cc2ed9d2123281100e8592212b38',
 '.local/ghidra/gog-query-20261019T211445Z.stdout.raw':'a5d3ea043476d79a5c2e8072c00ee9d98f62f4dc19c126227b1a8291b1b9ced1',
 '.local/ghidra/gog-query-20261019T211445Z.meta.json':'43936b4ea84fd6d0307313174005ab4f56ebddc718d104a0d1b9bf2c1a7bcbcf',
 '.local/ghidra/gog-query-20261019T211542Z.stdout.raw':'0394855010e1a32fdc9555a6747cf22976619284cabcf2b5146ba2a5cfb16b61',
 '.local/ghidra/gog-query-20261019T211542Z.meta.json':'ee1c73f4b63dd4cd58fc574ed39eba29696e73cbbda33f92b9a14c59c7b1c55f',
 '.local/ghidra/gog-query-20261019T211653Z.stdout.raw':'fad55a6d0ada60da8d7df45ac661ae1aef7208615e3e92e09dbda856d93827aa',
 '.local/ghidra/gog-query-20261019T211653Z.meta.json':'fe25d3c9cba943b16176c1b795d12e5113faac262af87f63553e8cc1619ae943',
 '.local/ghidra/gog-query-20261019T211754Z.stdout.raw':'e590be2c819569acf9f2a98799e34165ea07cb000548a4413fdb9ca3d5df39e0',
 '.local/ghidra/gog-query-20261019T211754Z.meta.json':'7b79ba1e1ebffe0b88790fe2a284f7289e8b3b722c7471ced3f16f149b169d54',
 '.local/ghidra/gog-query-20261019T211852Z.stdout.raw':'cd87b2bf87111dc2e14b51f4b99f4bafa1c584fa6527b7e6f118603607c50490',
 '.local/ghidra/gog-query-20261019T211852Z.meta.json':'ca912f672c04eb551bb2d196cac3d1d0b0c196bb93395ffe102c6815fffa634c',
 '.local/ghidra/gog-query-20261019T212000Z.stdout.raw':'1d3cb9014cf06b56e2afcc9ad4d53527520548cf8a9fd591ac0c79e7a087f78a',
 '.local/ghidra/gog-query-20261019T212000Z.meta.json':'47cba9626f4c0c9f444afb4fdb3e2098c51ae9a89b06308d353c5b869aa1dda4',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,s): p.write_text(s.rstrip()+'\n',encoding='utf-8',newline='\n')
def append_once(p,marker,body):
    old=p.read_text(encoding='utf-8')
    if marker in old: raise SystemExit('duplicate marker '+marker)
    write(p,old.rstrip()+'\n\n'+body.strip())

def main():
    for rel,want in EXPECTED.items():
        p=ROOT/rel
        if not p.is_file() or sha(p)!=want: raise SystemExit('capture/hash mismatch '+rel)
    metas=[json.loads((ROOT/(b+'.meta.json')).read_text(encoding='utf-8')) for b in BASES]
    for m in metas:
        if not (m.get('ok') and m.get('read_only') and m.get('auto_analysis_disabled')
                and m.get('program_executable_path_matches_gog_binary')
                and m.get('analysis_binary_product_version')=='1.6.1179'
                and m.get('analysis_binary_sha256')==GOG_SHA):
            raise SystemExit('capture failed GOG identity/read-only gates')
    raws=[(ROOT/(b+'.stdout.raw')).read_text(encoding='utf-8',errors='replace') for b in BASES]
    caller,handler,cleanup,selector,reset,actor_slot,actor_rtti,slot_fn,visitor_rtti,visitor_ptr,visitor_method,equality=raws
    proofs=[
      (caller,['OUTGOING_DIRECT_CALL_EDGE_COUNT=1','INDIRECT_CALL_SITE_COUNT=0','local_88[0] = 0x58;','local_80 = param_2;','local_78 = param_3;','FUN_14065b800(param_1,local_88);','caller=FUN_14074b200','caller=FUN_14074b330','FUN_140658cc0(DAT_14319a7c0,param_2,0);','FUN_140658cc0(DAT_14319a7c0,param_2,1);']),
      (handler,['OUTGOING_DIRECT_CALL_EDGE_COUNT=5','INDIRECT_CALL_SITE_COUNT=0','DECOMPILATION_BEGIN=FUN_14074b350','FUN_1407540f0','FUN_140750f70','FUN_140cc82b0']),
      (cleanup,['OUTGOING_DIRECT_CALL_EDGE_COUNT=5','INDIRECT_CALL_SITE_COUNT=1','BGSPerk::FindPerkInRanksVisitor::vftable','FUN_140390a80','(**(code **)(*DAT_143188918 + 0x650))()','FUN_140225820(DAT_143188918)']),
      (selector,['FUN_140225820','FUN_140238a60','DAT_143188918']),
      (reset,['DECOMPILATION_BEGIN=FUN_140238a60','*(undefined4 *)(param_1 + 0x10) = 0xbf800000;']),
      (actor_slot,['POINTER_TABLE_BASE_RVA=0x189F270','POINTER_TABLE_ENTRY=index:0 address:14189f270 value:0x1406B21D0']),
      (actor_rtti,['VTABLE_RTTI_TYPE_NAME=.?AVActor@@','VTABLE_RTTI_CENSUS_ENTRY=index:1 requested_rva:0x189F270','VTABLE_RTTI_SIGNATURE=0x28EC8348']),
      (slot_fn,['FUNCTION_LOOKUP=FUN_1406b21d0','OUTGOING_DIRECT_CALL_EDGE_COUNT=0','void FUN_1406b21d0(void)']),
      (visitor_rtti,['VTABLE_RTTI_TABLE_RVA=0x18A5EF8','VTABLE_RTTI_TYPE_NAME=.?AVFindPerkInRanksVisitor@BGSPerk@@']),
      (visitor_ptr,['POINTER_TABLE_BASE_RVA=0x18A5EF8','POINTER_TABLE_ENTRY=index:0 address:1418a5ef8 value:0x140390A80']),
      (visitor_method,['OUTGOING_DIRECT_CALL_EDGE_COUNT=0','DECOMPILATION_BEGIN=FUN_140390a80','*param_2 == *(longlong *)(param_1 + 8)']),
      (equality,['OUTGOING_DIRECT_CALL_EDGE_COUNT=0','DECOMPILATION_BEGIN=FUN_1407540f0','return *param_1 == param_2;']),
    ]
    for raw,tokens in proofs:
        for token in tokens:
            if token not in raw: raise SystemExit('proof token missing: '+token)

    ep=ROOT/'research/EVIDENCE.json'
    ev=json.loads(ep.read_text(encoding='utf-8'))
    ids={r.get('id') for r in ev.get('items',[])}
    if 'EV-0638' in ids: raise SystemExit('EV-0638 already exists')
    for required in ['EV-0344','EV-0400','EV-0637']:
        if required not in ids: raise SystemExit('missing contextual evidence '+required)
    note=EXP/'EV-0638-caller56-tag58-playercharacter-perk-rank-cleanup.md'
    body="""# EV-0638 — Caller 56 tag-0x58 PlayerCharacter collection and perk-rank cleanup

## Competing models and discriminants

- H1, perk-rank/collection cleanup: tag 0x58 supplies an object and a mode byte to PlayerCharacter collection-removal code, with a FindPerkInRanksVisitor lookup when the object is no longer present in the relevant collection. It predicts the observed object-list scans, reference/list removal, RTTI-verified visitor, and pointer-match method.
- H2, HitData/effective-armor/armor-skill route: the object or a descendant reaches hit/protection/AV11/AV12/UseSkill processing. It predicts a producer-backed edge to a mapped combat/skill sink, including through dynamic callbacks.
- H3, level-gated perk access change: this cleanup changes perk eligibility or grants access to a gated perk. It predicts a rank/eligibility mutation or a positive perk-add/level condition; a removal and list cleanup alone do not support it.

## Direct GOG evidence

Captures use the existing GOG SkyrimSE.exe Ghidra project, ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Metadata verifies read-only queries, auto-analysis disabled, and matching executable identity. GOG addresses are not transferred to Steam AE 1.6.1170.0.

- FUN_140658cc0 writes tag 0x58, copies its object pointer and one mode byte, then submits the record through FUN_14065b800. Its two direct producers FUN_14074b200 and FUN_14074b330 each require a nonnull object and pass mode 0 or 1 respectively [EV-0638].
- Dispatcher case 0x58 passes the PlayerCharacter singleton DAT_143188918, the queued object, and the mode byte to FUN_14074b350 [EV-0637], [EV-0638]. PlayerCharacter identity is independently verified [EV-0344].
- FUN_14074b350 has five direct calls and no indirect sites. It checks/removes the object across collection fields +0x4e8/+0x4f8 and +0x4d0/+0x4e0; one mode decrements a paired reference count before compacting. Its equality helper FUN_1407540f0 is a direct pointer comparison. Under the captured conditions it calls FUN_140750f70 for further cleanup [EV-0638].
- FUN_140750f70 scans a PlayerCharacter list at +0x4b8 with a stack visitor whose RTTI is verified as BGSPerk::FindPerkInRanksVisitor at RVA 0x18a5ef8 [EV-0638]. The visitor method FUN_140390a80 returns a match when the candidate pointer equals its stored object pointer and saves the matched rank entry [EV-0638].
- On a visitor match, FUN_140750f70 removes the rank entry, invokes PlayerCharacter vtable slot +0x650, then calls FUN_140225820 and conditionally FUN_140238a60. The latter resets two float fields to -1.0. A pointer read at primary Actor table base RVA 0x189ec20 plus 0x650 resolves to FUN_1406b21d0, which is empty in this GOG image; however, DAT_143188918's runtime PlayerCharacter vtable/override at that slot is not identified, so the actual virtual target remains open [EV-0400], [EV-0344], [EV-0638].
- FUN_140750f70 has five direct calls and one unresolved dynamic PlayerCharacter slot +0x650 call. The visitor comparison itself is resolved to FUN_140390a80. No mapped direct HitData, protection, AV11/AV12 or UseSkill sink appears in the bounded route [EV-0638].

## Result and limits

H1 is supported for the captured static path as conditional PlayerCharacter collection and perk-rank cleanup. H2 has no mapped direct sink in the bounded path, but the runtime PlayerCharacter virtual override at +0x650 remains unresolved. H3 is not supported: the captured route removes a matched rank entry and shows no perk-grant, eligibility-level comparison, or level-gate bypass. No armor-XP bypass or bounty outcome follows, and no causal edge is added to HitData, protection, AV11/AV12, UseSkill, or level-one quest access.

## Next action

Continue worker caller 57/62, FUN_140658d00, with an exact tag, payload, and producer trace.
"""
    write(note,body)
    note_rel=note.relative_to(ROOT).as_posix()
    local={k:sha(ROOT/k) for k in EXPECTED}
    local[note_rel]=sha(note)
    latest=max(metas,key=lambda x:x.get('captured_utc',''))
    ev['items'].append({
      'captured_utc':latest['captured_utc'],'edition':'AE','modified_state':False,'id':'EV-0638',
      'kind':'native','source':'Identity-checked read-only GOG trace of caller 56/tag 0x58, both producers, PlayerCharacter list-removal handler, RTTI-verified perk-rank visitor, its pointer comparator, and bounded cleanup targets.',
      'artifact':'private-local:'+BASES[1]+'.stdout.raw','sha256':EXPECTED[BASES[1]+'.stdout.raw'],
      'runtime':'GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 '+GOG_SHA+'; existing-project read-only queries, auto-analysis disabled, no import or overwrite. Separate from Steam AE 1.6.1170.0.',
      'lane':'mechanism_inference','tools':['strict Python 3.12 dispatcher','tools/ghidra_probe.py read-only call-edge, RTTI, and pointer-table queries'],
      'coverage':'Caller 56 builder/two producers, dispatcher case 0x58 cross-linked to EV-0637, PlayerCharacter handler and direct census, shared cleanup helper, FindPerkInRanksVisitor RTTI and method, Actor base slot +0x650, and timing-field cleanup helper.',
      'result':'Caller 56 is a queued PlayerCharacter collection-removal route with a conditional RTTI-verified perk-rank lookup/removal. The visitor method is a pointer match. FUN_140750f70 has one unresolved dynamic PlayerCharacter slot +0x650; the base Actor table entry is a no-op but does not identify the runtime override. No mapped direct HitData/protection/AV11/AV12/UseSkill edge or perk grant/eligibility-level gate is established.',
      'local_hashes':local,'related_evidence':['EV-0344','EV-0400','EV-0637'],
    })
    write(ep,json.dumps(ev,indent=2,ensure_ascii=False))

    append_once(ROOT/'research/CLAIMS.md','| CL-L451 |',
      '| CL-L451 | In GOG AE 1.6.1179.0, caller 56 tag 0x58 dispatches a nonnull object/mode payload to PlayerCharacter collection cleanup; the conditional +0x4b8 list path uses RTTI-verified BGSPerk::FindPerkInRanksVisitor to locate and remove a matching rank entry. | supported for captured static route | [EV-0344], [EV-0637], [EV-0638] | The runtime PlayerCharacter virtual override at +0x650 remains unresolved; no perk grant, level-gate bypass, HitData/protection/armor-skill edge, or bounty result follows. |')
    append_once(ROOT/'research/MECHANISMS.md','## M-0191 —',
      """## M-0191 — Tag-0x58 PlayerCharacter collection and perk-rank cleanup (EV-0638)

Caller 56 FUN_140658cc0 writes tag 0x58 with an object pointer and mode byte; two nonnull-gated producers pass modes 0 and 1 [EV-0638]. Dispatcher case 0x58 supplies PlayerCharacter DAT_143188918 to FUN_14074b350 [EV-0344], [EV-0637], [EV-0638]. The handler scans/removes from object collections at +0x4e8/+0x4f8 and +0x4d0/+0x4e0, with a paired reference-count branch, and conditionally enters FUN_140750f70 [EV-0638].

FUN_140750f70 uses an RTTI-verified BGSPerk::FindPerkInRanksVisitor to compare object pointers and may remove a matching entry from the PlayerCharacter list at +0x4b8 [EV-0638]. Its dynamic PlayerCharacter slot +0x650 remains unresolved; the primary Actor base slot is a no-op but is not proof of the derived runtime target. The bounded path shows cleanup, not perk granting, level eligibility, HitData, protection, AV11/AV12, UseSkill, or armor XP. No causal OBJ-1/OBJ-2 edge is added. Claim CL-L451.""")
    append_once(ROOT/'research/CONTRADICTIONS.md','## C-OBJ2-Q79-TAG58-PERK-CLEANUP-VS-COMBAT',
      """## C-OBJ2-Q79-TAG58-PERK-CLEANUP-VS-COMBAT — PlayerCharacter rank-list cleanup versus hit/armor route

- Model A: tag 0x58 or a dynamic descendant performs HitData/effective-protection/AV11/AV12/UseSkill work.
- Model B: tag 0x58 removes a PlayerCharacter collection object and conditionally removes its matching entry through BGSPerk::FindPerkInRanksVisitor.
- Evidence: two builder producers and modes, dispatcher case, collection-removal handler, visitor RTTI/method, and bounded cleanup helper chain [EV-0344], [EV-0637], [EV-0638].
- Assessment: B is supported for the captured static path. A has no mapped direct sink; one runtime PlayerCharacter virtual override at +0x650 remains unresolved. The captured path does not show perk granting or eligibility-level mutation. No global no-hit, Steam, armor-XP, or bounty conclusion follows.
- Discriminant: identify the runtime PlayerCharacter vtable target for +0x650 and trace any producer-backed continuation before changing the no-edge assessment.""")
    append_once(ROOT/'research/KNOWLEDGE_GRAPH.md','EV-0638 maps caller 56 tag-0x58 PlayerCharacter perk-rank cleanup',
      """### EV-0638 maps caller 56 tag-0x58 PlayerCharacter perk-rank cleanup

Caller 56 tag 0x58 reaches PlayerCharacter collection removal; the conditional +0x4b8 path uses RTTI-verified BGSPerk::FindPerkInRanksVisitor and a direct pointer-match method to locate/remove a matching rank entry [EV-0344], [EV-0637], [EV-0638]. The runtime PlayerCharacter virtual override at +0x650 remains unresolved. **No causal edge is added** to perk eligibility/granting, HitData, protection, AV11/AV12, UseSkill, armor XP, or quest gates. Continue caller 57/62 FUN_140658d00.""")
    append_once(EXP/'results.md','### Caller 56/62: PlayerCharacter tag-0x58 perk-rank cleanup (EV-0638)',
      """### Caller 56/62: PlayerCharacter tag-0x58 perk-rank cleanup (EV-0638)

Caller 56 FUN_140658cc0 writes tag 0x58 with an object and mode byte. Its two nonnull-gated producers pass modes 0 and 1; dispatcher case 0x58 supplies the PlayerCharacter singleton to FUN_14074b350 [EV-0344], [EV-0637], [EV-0638]. The handler edits two object collections and conditionally calls FUN_140750f70.

The cleanup helper's stack visitor has verified RTTI BGSPerk::FindPerkInRanksVisitor, and its method matches a candidate by pointer before removing the associated rank entry [EV-0638]. PlayerCharacter slot +0x650 remains dynamic; the base Actor entry is empty but does not establish the runtime override. The bounded route shows no direct HitData/protection/AV11/AV12/UseSkill sink, no perk grant or level-gate change, and no causal OBJ-1/OBJ-2 edge. Continue caller 57/62 FUN_140658d00.""")
    fp=ROOT/'research/FRONTIER.json'
    frontier=json.loads(fp.read_text(encoding='utf-8'))
    item=next(x for x in frontier['items'] if x.get('id')=='Q-0079')
    hids={x.get('id') for x in item.get('hypotheses',[])}
    if {'Q79-H153','Q79-H154'} & hids: raise SystemExit('caller-56 hypotheses already exist')
    item['hypotheses'].extend([
      {'id':'Q79-H153','model':'Caller 56 tag 0x58 is a PlayerCharacter collection-removal route with a conditional RTTI-verified BGSPerk::FindPerkInRanksVisitor pointer match/removal from the +0x4b8 rank list.','predicted_discriminant':'The two producer modes, tag-0x58 dispatcher, collection fields, verified visitor RTTI, pointer comparator, and rank-entry removal establish the captured static cleanup path; runtime slot +0x650 remains open.','status':'supported','evidence':['EV-0344','EV-0637','EV-0638']},
      {'id':'Q79-H154','model':'The unresolved runtime PlayerCharacter slot +0x650 or another descendant of caller 56 cleanup changes perk eligibility, reaches HitData/effective protection/AV11/AV12/UseSkill, or alters level-one quest access.','predicted_discriminant':'Resolve the runtime PlayerCharacter vtable override and show a concrete producer-backed rank grant/eligibility/level gate or data/control edge into a mapped combat, armor-skill, or quest-start sink. The empty Actor base slot does not identify the derived target.','status':'proposed','evidence':['EV-0344','EV-0638','EV-0260']},
    ])
    item['evidence']=list(dict.fromkeys([*item.get('evidence',[]),'EV-0638']))
    item['linked_claims']=list(dict.fromkeys([*item.get('linked_claims',[]),'CL-L451']))
    item['next_action']=NEXT
    frontier['session_next_action']=NEXT
    frontier['next_action']=NEXT
    now=datetime.now(timezone.utc).isoformat(timespec='seconds')
    frontier['session_checkpoint']={'timestamp_utc':now,'task':'Q-0079/TX-20261018-0013: caller 56/tag-0x58 is bounded as PlayerCharacter collection/perk-rank cleanup; continue caller 57.','next_action':NEXT}
    frontier['last_session_checkpoint']={'recorded_utc':now,'next_action':NEXT,'active_process':'TX-20261018-0013'}
    write(fp,json.dumps(frontier,indent=2,ensure_ascii=False))

    sp=ROOT/'STATE.md'
    state=sp.read_text(encoding='utf-8')
    old='Q-0079/TX-20261018-0013 remains active on OBJ-2: 56 of 62 initially uninspected worker callers are reviewed, with 6 remaining.'
    new='Q-0079/TX-20261018-0013 remains active on OBJ-2: 57 of 62 initially uninspected worker callers are reviewed, with 5 remaining.'
    if state.count(old)!=1: raise SystemExit('STATE active caller count mismatch')
    state=state.replace(old,new,1)
    oldev='EV-0637 bounds caller 55/tag 0x57 as a gated numeric value/limit notification into a six-call registry helper; literal category/code names remain unknown, with no direct mapped HitData/armor sink.'
    if state.count(oldev)!=1: raise SystemExit('STATE caller-55 summary mismatch')
    state=state.replace(oldev,oldev+' EV-0638 maps caller 56/tag 0x58 to PlayerCharacter collection removal and conditional RTTI-verified perk-rank cleanup; one runtime PlayerCharacter vtable slot remains unresolved, with no mapped direct HitData/armor sink.',1)
    state=state.replace('Q-0079 has 56/62 initially uninspected worker callers reviewed; 6 remain.','Q-0079 has 57/62 initially uninspected worker callers reviewed; 5 remain.',1)
    tick=chr(96)
    oldnext=('**Selected next line:** run '+tick+'python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658cc0 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600'+tick+'; review worker caller 56/62 '+tick+'FUN_140658cc0'+tick+' for its exact tag, payload, producer and immediate/deferred behavior, then continue the bounded caller census. Caller 55'+chr(39)+'s tag-0x57 route is a numeric registry notification with unnamed codes/categories and no direct mapped HitData/armor sink.')
    newnext=('**Selected next line:** run '+tick+'python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658d00 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600'+tick+'; review worker caller 57/62 '+tick+'FUN_140658d00'+tick+' for its exact tag, payload and producer, then continue the bounded caller census. Caller 56 tag 0x58 is a PlayerCharacter perk-rank cleanup route; the runtime vtable slot +0x650 remains unresolved.')
    if state.count(oldnext)!=1: raise SystemExit('STATE selected-next line mismatch')
    state=state.replace(oldnext,newnext,1)
    write(sp,state)

    append_once(ROOT/'research/ROADMAP.md','## Cross-domain synthesis — Q-0079 caller 56 (EV-0638)',
      """## Cross-domain synthesis — Q-0079 caller 56 (EV-0638)

Caller 54 maps spatial/context Actor updates and shared nested-object helpers; caller 55 maps a numeric value/limit registry notification; caller 56 maps PlayerCharacter collection cleanup with an RTTI-verified perk-rank visitor [EV-0636]–[EV-0638]. Their common worker dispatcher does not establish a shared causal mechanic. The caller-56 route removes a rank-list entry under captured conditions; it does not demonstrate a perk grant, level eligibility check, HitData event, effective protection change, AV11/AV12 award, or armor XP effect. One runtime PlayerCharacter virtual override remains unresolved. Keep this as a separate state-cleanup mechanism with no OBJ-1/OBJ-2 edge. The clean Steam protection/raw-AVSK test remains outstanding [EV-0260]. Continue caller 57/62 FUN_140658d00.""")
    print('Registered EV-0638/CL-L451/M-0191 and checkpointed caller 57.')
if __name__=='__main__': main()

