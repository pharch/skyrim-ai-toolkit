#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GH = ROOT / ".local/ghidra"
TX = ROOT / ".local/alignment/transactions/TX-20261017-0011"
EXP = Path(__file__).resolve().parent
BIN = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
 "20261018T101842Z": {"requested_string":"TtconDeletedCb"},
 "20261018T102003Z": {"requested_search_displacement":"0x48"},
 "20261018T102256Z": {"requested_rva":"0xB48A20"},
 "20261018T102400Z": {"requested_rva":"0xB675F0"},
 "20261018T102513Z": {"requested_rva":"0xB67750"},
 "20261018T102621Z": {"requested_rva":"0xB5B160"},
 "20261018T102900Z": {"requested_rva":"0xB5B430"},
 "20261018T103022Z": {"requested_pointer_table_rva":"0x19771E0","requested_pointer_count":16},
 "20261018T103135Z": {"requested_rva":"0xB5D450"},
 "20261018T103253Z": {"requested_pointer_table_rva":"0x19753A0","requested_pointer_count":16},
 "20261018T103413Z": {"requested_pointer_table_rva":"0x1975320","requested_pointer_count":16},
 "20261018T103523Z": {"requested_pointer_table_rva":"0x19771E0","requested_pointer_count":24},
 "20261018T103632Z": {"requested_pointer_table_rva":"0x19771E0","requested_pointer_count":64},
 "20261018T103944Z": {"requested_rva":"0x19EB9C0","requested_vtable_slot":"0x31"},
 "20261018T104110Z": {"requested_rva":"0x19F50A8","requested_vtable_slot":"0x31"},
 "20261018T104229Z": {"requested_rva":"0xECD680"},
 "20261018T104350Z": {"requested_rva":"0xECE1A0"},
 "20261018T104650Z": {"requested_rva":"0xA89E60"},
 "20261018T104909Z": {"requested_rva":"0xEBE4A0"},
 "20261018T105044Z": {"requested_rva":"0xA89DA0"},
}
MARKERS = {
 "20261018T101842Z":["TtconDeletedCb"],
 "20261018T102256Z":["FUN_140b48a20","0x80000000"],
 "20261018T102400Z":["FUN_140b675f0"],
 "20261018T102513Z":["FUN_140b67750"],
 "20261018T102621Z":["FUN_140b5b160"],
 "20261018T102900Z":["FUN_140b5b430"],
 "20261018T103022Z":["POINTER_TABLE_BASE_RVA=0x19771E0"],
 "20261018T103135Z":["FUN_140b5d450"],
 "20261018T103253Z":["POINTER_TABLE_BASE_RVA=0x19753A0"],
 "20261018T103413Z":["POINTER_TABLE_BASE_RVA=0x1975320"],
 "20261018T104229Z":["void FUN_140ecd680","FUN_140ebe4a0(param_1,param_2);"],
 "20261018T104350Z":["void FUN_140ece1a0","FUN_140ebe4f0();"],
 "20261018T104650Z":["void FUN_140a89e60","(**(code **)*param_1)(param_1,1);"],
 "20261018T104909Z":["void FUN_140ebe4a0","param_1[2] = param_2;"],
 "20261018T105044Z":["void FUN_140a89da0","*(short *)(param_1 + 10) = *(short *)(param_1 + 10) + 1;"],
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(s.rstrip()+"\n", encoding="utf-8")
def append_once(p, marker, body):
    s=p.read_text(encoding="utf-8")
    if marker in s: raise SystemExit("duplicate append: "+marker)
    write(p,s.rstrip()+"\n\n"+body.strip())

def main():
    caps=[]
    for stamp, expected in CAPTURES.items():
        mp=GH/f"gog-query-{stamp}.meta.json"
        if not mp.is_file(): raise SystemExit(f"missing metadata {stamp}")
        m=json.loads(mp.read_text(encoding="utf-8"))
        checks=m.get("checks",{})
        out=ROOT/m.get("artifacts",{}).get("stdout","")
        ok=(m.get("operation")=="existing_gog_project_read_only_query"
            and m.get("analysis_distribution")=="GOG"
            and m.get("analysis_binary_product_version")=="1.6.1179"
            and m.get("analysis_binary_sha256")==BIN and m.get("program")=="SkyrimSE.exe"
            and m.get("program_executable_path_matches_gog_binary") is True
            and m.get("exit_code")==0 and m.get("ok") is True
            and m.get("read_only") is True and m.get("auto_analysis_disabled") is True
            and m.get("import_attempted") is False and m.get("overwrite_attempted") is False
            and m.get("project_created") is False and bool(checks) and all(checks.values())
            and out.is_file() and sha(out)==m.get("stdout_sha256")
            and all(m.get(k)==v for k,v in expected.items()))
        if not ok: raise SystemExit(f"capture validation failed {stamp}")
        raw=out.read_text(encoding="utf-8",errors="replace")
        missing=[x for x in MARKERS.get(stamp,[]) if x not in raw]
        if missing: raise SystemExit(f"capture markers missing {stamp}: {missing}")
        caps.append((stamp,m,mp,out))

    ep=ROOT/"research/EVIDENCE.json"
    evidence=json.loads(ep.read_text(encoding="utf-8"))
    if any(x.get("id")=="EV-0368" for x in evidence["items"]): raise SystemExit("EV-0368 exists")
    claimp=ROOT/"research/CLAIMS.md"
    note=TX/"EV-0368-note.md"
    write(note,f"""# EV-0368 — ProcessTrapHit constraint-wrapper lifetime boundary

## Build and method

Twenty identity-checked captures query the existing GOG AE 1.6.1179.0 Ghidra project in read-only, no-analysis mode. Analysis binary SHA-256: {BIN}. All recorded checks pass and captured stdout hashes match metadata. Factory and constructor context from EV-0365 and EV-0366 is reused.

## Competing models

- H1: FUN_140ecdfc0's immediate release reaches terminal count and dispatches hkpConstraintInstance slot 0.
- H2: wrapper association first retains the instance, so the factory release only balances its temporary reference.
- The discriminant is constructor count plus exact wrapper slot +0x130, reference helper and factory call order. This does not decide later detach/destruction.

## Direct observations

- FUN_140b48720 initializes the packed word at +0x08 to 0x1ffff, so the short count at +0x0a starts at 1. It initializes callback pointer +0x40 to null and encoded count +0x48 to 0x80000000, with low count bits zero [EV-0365; capture 20261018T090112Z].
- Fixed and malleable wrapper vtables map +0x128 to FUN_140ecd680 and +0x130 to FUN_140ece1a0 [EV-0366]. FUN_140ebe4a0 notifies +0x130 with mode 0, swaps wrapper +0x10, then notifies with mode 1 [captures 20261018T104909Z, 20261018T104229Z].
- FUN_140ece1a0 writes the associated instance's +0x58 backlink to wrapper/null, then calls FUN_140ebe4f0 [capture 20261018T104350Z]. That helper selects FUN_140a89da0 to enable and FUN_140a89e60 to disable [EV-0366].
- FUN_140a89da0 increments the short count at +0x0a when the +0x08 header is nonzero [capture 20261018T105044Z]. FUN_140a89e60 decrements the count and invokes receiver slot 0 with delete flag 1 only when the prior count was 1 [capture 20261018T104650Z].
- FUN_140ecdfc0 constructs the instance, calls wrapper +0x128 with it, and then releases the temporary construction reference [capture 20261018T070646Z; EV-0365, EV-0366]. Count therefore advances 1 -> 2 on association, then returns 2 -> 1 on this release. It does not call slot 0.
- The exact deletion consumer FUN_140b674a0 walks non-null entries at +0x40/+0x48 and invokes entry slot +0x18 only during finalization [EV-0367]. The mapped creation handoff cannot by itself dispatch that consumer.
- The +0x188 fixed/malleable finalizer route releases a separate wrapper +0x18 object and does not write the hkp callback fields [EV-0366].
- The string and table screens, same-offset chain-data candidates and capped displacement scan do not identify an exact callback-array writer. The chain-data receiver is not the exact hkpConstraintInstance type, and capped output is not a complete writer exclusion [EV-0366; captures 20261018T101842Z, 20261018T102003Z, 20261018T102900Z, 20261018T103022Z through 20261018T103632Z].

## Result and uncertainty

H2 is supported for this exact creation handoff. Callback dispatch requires a later terminal release or another route. Exact callback-array producer, entry class and entry slot +0x18 target remain unknown. Neither Q64 hypothesis is selected globally; no AV11/AV12 causal edge, live Steam outcome or zero-armor-XP claim follows.

## Exact next action

Inspect exact receiver and callsite context for hkp-region +0x40/+0x48 writer candidates FUN_140b57860 and FUN_140b58550. Establish whether either writes the exact hkpConstraintInstance callback array; then resolve any entry class, slot +0x18 target and argument flow to Actor::UseSkill AV11/AV12. Preserve the independent Steam discriminator: verified target, full profile order, positive final damage, effective protection and repeated raw AVSK deltas.
""")
    docs={
      "README.md":"# EXP-0106 — ProcessTrapHit constraint-wrapper lifetime boundary\n\nTrace constructor count, wrapper association, temporary release and terminal callback dispatch. Result is bounded to the mapped creation handoff.\n",
      "hypothesis.md":"# Competing models\n\n- H1: the factory release reaches terminal count and dispatches slot 0.\n- H2: wrapper association retains the instance and the factory release balances its temporary reference.\n\nLater releases are separate.\n",
      "protocol.md":"# Protocol\n\nUse identity-checked read-only GOG queries. Reconstruct constructor state, wrapper slot targets, enable/disable association, reference helper behavior and exact call order. Treat same-offset receivers as candidates only.\n",
      "expected-discriminants.md":"# Expected discriminants\n\nH1 predicts the factory decrement begins at count 1 and calls slot 0. H2 predicts constructor 1, association 2, factory decrement 1, with no slot-0 call. Later world releases need their own receiver and count trace.\n",
      "results.md":"# Results\n\nThe mapped factory creates at count 1, wrapper association increments to 2, and the immediate temporary release returns to 1 without slot 0. Later releases and callback producers remain unresolved. See EV-0368.\n",
      "implications.md":"# Implications\n\nThe creation handoff does not dispatch the hkp deletion callback consumer. This does not resolve the remaining teardown calls, exclude later callback dispatch, establish AV11/AV12 absence, or prove zero armor XP. No edge to OBJ-1 is supported.\n",
    }
    for n,s in docs.items(): write(EXP/n,s)
    mf=TX/"EV-0368-capture-manifest.json"
    hashes={}
    summaries=[]
    for stamp,m,mp,out in caps:
        hashes[mp.relative_to(ROOT).as_posix()]=sha(mp)
        for a in m.get("artifacts",{}).values():
            p=ROOT/a
            if p.is_file(): hashes[p.relative_to(ROOT).as_posix()]=sha(p)
        summaries.append({k:m.get(k) for k in ("captured_utc","query_mode","requested_rva","requested_string","requested_search_displacement","requested_pointer_table_rva","requested_pointer_count","requested_vtable_slot","checks","stdout_sha256","read_only","auto_analysis_disabled")}|{"stamp":stamp})
    hashes[note.relative_to(ROOT).as_posix()]=sha(note)
    hashes[Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    for n in docs: hashes[(EXP/n).relative_to(ROOT).as_posix()]=sha(EXP/n)
    write(mf,json.dumps({"evidence_id":"EV-0368","analysis_binary_product_version":"1.6.1179.0","analysis_binary_sha256":BIN,"captures":summaries,"registered_local_hashes":hashes},indent=2,ensure_ascii=False))
    hashes[mf.relative_to(ROOT).as_posix()]=sha(mf)
    evidence["items"].append({
      "captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"edition":"AE","modified_state":False,
      "id":"EV-0368","kind":"native","source":"Identity-checked read-only GOG Ghidra ProcessTrapHit hkpConstraintInstance wrapper reference-lifetime trace.",
      "artifact":"private-local:.local/alignment/transactions/TX-20261017-0011/EV-0368-note.md","sha256":sha(note),
      "runtime":f"GOG AE 1.6.1179.0 static outputs; analysis binary SHA-256 {BIN}; no Steam runtime observation.",
      "lane":"mechanism_inference","tools":["tools/ghidra_probe.py through scripts/python_env.py in -noanalysis -readOnly mode"],
      "coverage":"Constructor count, fixed/malleable wrapper association, add/release helpers and factory call order; broad writer search remains incomplete.",
      "result":"Constructor count 1; wrapper association increments to 2; factory temporary release returns to 1 and does not dispatch slot 0 or the deletion-callback consumer. Later terminal release, callback-array producer, entry type and slot +0x18 behavior remain unresolved.",
      "related_evidence":["EV-0355","EV-0358","EV-0365","EV-0366","EV-0367"],"local_hashes":hashes})
    write(ep,json.dumps(evidence,indent=2,ensure_ascii=False))

    append_once(claimp,"| CL-L208 |","| CL-L208 | In GOG AE 1.6.1179.0, the mapped ProcessTrapHit hkpConstraintInstance factory starts at reference count 1, fixed/malleable wrapper association increments it to 2, and the immediate release returns it to 1 without dispatching slot 0 or the deletion-callback consumer. | supported for this mapped handoff | [EV-0368], [EV-0365], [EV-0366], [EV-0367] | Later releases and callback writers remain unresolved; no AV11/AV12 or zero-armor-XP result follows. |")
    append_once(ROOT/"research/MECHANISMS.md","## M-0087 — ProcessTrapHit hkpConstraintInstance creation-time reference balance","""## M-0087 — ProcessTrapHit hkpConstraintInstance creation-time reference balance

The constructor initializes count 1 and the callback array empty. Wrapper association retains the instance to 2; FUN_140ecdfc0 drops its temporary reference to 1, so the immediate release does not invoke slot 0 or FUN_140b674a0. A later terminal release remains necessary for deletion callbacks. Claim CL-L208 -> M-0087 [EV-0368].""")
    append_once(ROOT/"research/CONTRADICTIONS.md","## C-OBJ2-Q64-TRAP-INSTANCE-LIFETIME","""## C-OBJ2-Q64-TRAP-INSTANCE-LIFETIME — factory release and deletion callback timing

- **Model A:** FUN_140ecdfc0's immediate release reaches terminal count and dispatches slot 0.
- **Model B:** wrapper association increments the new instance, so the immediate release only balances the temporary reference.
- **Evidence:** constructor count 1, wrapper enable reaches FUN_140a89da0, then factory calls FUN_140a89e60 [EV-0365, EV-0366, EV-0368].
- **Assessment:** Model B is supported for this handoff; later release routes remain unresolved.
- **Discriminant:** trace later world releases with exact receiver and count to test reachability of FUN_140b674a0.""")
    append_once(ROOT/"research/KNOWLEDGE_GRAPH.md","EV-0368 adds a bounded lifetime edge","EV-0368 adds a bounded lifetime edge: constructor count 1 -> wrapper retain to 2 -> factory temporary release to 1, with no slot-0 deletion callback on that handoff. Later terminal release and callback producers remain unresolved. No edge to AV11/AV12 or the OBJ-1 Story Manager gate is supported [CL-L208], [M-0087].")

    fp=ROOT/"research/FRONTIER.json"
    frontier=json.loads(fp.read_text(encoding="utf-8"))
    q=next(x for x in frontier["items"] if x.get("id")=="Q-0064")
    if q.get("status")!="in_progress": raise SystemExit("Q-0064 no longer active")
    q.setdefault("evidence",[])
    if "EV-0368" not in q["evidence"]: q["evidence"].append("EV-0368")
    for h in q.get("hypotheses",[]):
        h.setdefault("evidence",[])
        if "EV-0368" not in h["evidence"]: h["evidence"].append("EV-0368")
    q.setdefault("linked_claims",[])
    if "CL-L208" not in q["linked_claims"]: q["linked_claims"].append("CL-L208")
    nxt="Inspect exact receiver and callsite context for hkp-region +0x40/+0x48 writer candidates FUN_140b57860 and FUN_140b58550. Establish whether either writes the exact hkpConstraintInstance callback array; then resolve concrete entry class, slot +0x18 target and argument flow to Actor::UseSkill AV11/AV12. Preserve the independent Steam discriminator: verified target, full profile order, positive final damage, effective protection and repeated raw AVSK deltas."
    q["next_action"]=nxt
    q.setdefault("methods",[]).append("EV-0368 bounds callback timing: the ProcessTrapHit creation-time retain/release pair does not dispatch deletion callbacks; resolve later terminal releases and exact callback-array writers.")
    write(fp,json.dumps(frontier,indent=2,ensure_ascii=False))
    append_once(ROOT/"STATE.md","Q-0064 / EV-0368","- Q-0064 / EV-0368 narrows callback timing: constructor count 1, wrapper retain to 2, factory release to 1 without slot-0 finalization. Callback writers and later terminal releases remain unresolved. Next inspect exact receivers for FUN_140b57860 and FUN_140b58550, then resolve any entry target and AV11/AV12 flow.")
    append_once(ROOT/"ROADMAP.md","EV-0368 confirms the ProcessTrapHit creation-time reference balance","EV-0368 confirms the ProcessTrapHit creation-time reference balance: hkp instance count 1 -> wrapper retain 2 -> temporary release 1 without callback dispatch. Later releases and exact writers remain open. Claim CL-L208 -> M-0087.")
    append_once(ROOT/"experiments/README.md","EXP-0106 / EV-0368","EXP-0106 / EV-0368 maps the ProcessTrapHit hkpConstraintInstance creation-time wrapper retain/release balance; later callback writers and terminal releases remain open.")
    print("Registered EV-0368 and CL-L208/M-0087; Q-0064 remains active on exact callback-array writers and later terminal releases.")

if __name__=="__main__": main()

