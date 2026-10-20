#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/EXP-0128-hit-worker-callers"
RAW_CASE12 = ROOT / ".local/ghidra/gog-query-20261019T194800Z.stdout.raw"
META_CASE12 = ROOT / ".local/ghidra/gog-query-20261019T194800Z.meta.json"
RAW_CASE4 = ROOT / ".local/ghidra/gog-query-20261019T195220Z.stdout.raw"
META_CASE4 = ROOT / ".local/ghidra/gog-query-20261019T195220Z.meta.json"
RAW_PRODUCER = ROOT / ".local/ghidra/gog-query-20261019T191026Z.stdout.raw"
RAW_BUILDER = ROOT / ".local/ghidra/gog-query-20261019T191458Z.stdout.raw"
RAW_DISPATCH = ROOT / ".local/ghidra/gog-query-20261019T191713Z.stdout.raw"
NEXT_ACTION = (
    "Run python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658b50 "
    "--list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600; "
    "map caller 51/62's event tag, payload, producer and matching dispatcher case, then screen "
    "the bounded route against mapped HitData, protection, AV11/AV12 and UseSkill targets."
)
EXPECTED = {
    ".local/ghidra/gog-query-20261019T194800Z.stdout.raw": "be58aa580a02191f22b78d81f3c2b5a3d208c10e5163f4e042d044d52e7d91f7",
    ".local/ghidra/gog-query-20261019T194800Z.meta.json": "6e6dac18cd1b6d1ee4c6116a1ab76995d464c2a79b979b25c8e1eacfe4efcd8a",
    ".local/ghidra/gog-query-20261019T195220Z.stdout.raw": "92b10396fdf10ec789f88b01e96c8b69b647edd6ed6fb08dd28ed15aa87ff730",
    ".local/ghidra/gog-query-20261019T195220Z.meta.json": "0f81c26978e3c808ebf904bb34a1a4d9068c7dc45fa162948c58ecceff54df92",
    ".local/ghidra/gog-query-20261019T191026Z.stdout.raw": "ab84cea3a79dab8c1b1cecda5cfb8a4f534ec4711b86b0105df1dd8499691f7a",
    ".local/ghidra/gog-query-20261019T191458Z.stdout.raw": "bcc47473375929604a7d26dfbeb845f586d28e21e1c5763a16aea355770c2fee",
    ".local/ghidra/gog-query-20261019T191713Z.stdout.raw": "cec53c18db470c99d49337b6087a6ba72934d25ceae1f19c4dfc18554fb3b489",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, content: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit(f"duplicate marker in {path}: {marker}")
    write(path, old.rstrip() + "\n\n" + content.strip())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected one {label}, found {count}")
    return text.replace(old, new, 1)


def replace_section(text: str, heading: str, new_section: str) -> str:
    start = text.index(heading)
    end = text.find("\n## ", start + len(heading))
    if end < 0:
        end = len(text)
    return text[:start] + new_section.strip() + "\n\n" + text[end:].lstrip("\n")


def main() -> None:
    for rel, expected in EXPECTED.items():
        p = ROOT / rel
        if not p.exists() or sha(p) != expected:
            raise SystemExit(f"raw artifact missing or hash changed: {rel}")

    case12 = RAW_CASE12.read_text(encoding="utf-8", errors="replace")
    case4 = RAW_CASE4.read_text(encoding="utf-8", errors="replace")
    producer = RAW_PRODUCER.read_text(encoding="utf-8", errors="replace")
    builder = RAW_BUILDER.read_text(encoding="utf-8", errors="replace")
    dispatcher = RAW_DISPATCH.read_text(encoding="utf-8", errors="replace")
    for token in [
        "ADDRESS_RVA=0x659C92",
        "ADDRESS_CONTEXT_BEFORE=140659c79 MOV MOV byte ptr [RSP + 0x28],0x0",
        "ADDRESS_CONTEXT_BEFORE=140659c7e MOV MOV EAX,dword ptr [RDI + 0x18]",
        "ADDRESS_CONTEXT_BEFORE=140659c81 MOV MOV dword ptr [RSP + 0x20],EAX",
        "ADDRESS_CONTEXT_BEFORE=140659c85 MOV MOV R9B,0x1",
        "ADDRESS_CONTEXT_BEFORE=140659c88 MOVZX MOVZX R8D,R9B",
        "ADDRESS_CONTEXT_BEFORE=140659c8c MOV MOV RDX,R15",
        "ADDRESS_CONTEXT_BEFORE=140659c8f MOV MOV RCX,R14",
        "ADDRESS_CONTEXT_INSTRUCTION=140659c92 CALL CALL qword ptr [R10 + 0x1a8]",
    ]:
        if token not in case12:
            raise SystemExit("case-0x12 argument proof missing: " + token)
    if "ADDRESS_TARGET=14065939c" not in case4 or "ADDRESS_CONTEXT_INSTRUCTION=14065939c CALL CALL qword ptr [RAX + 0x1a8]" not in case4:
        raise SystemExit("prior callsite address proof missing")
    if "case 4:" not in dispatcher or "case 0x12:" not in dispatcher:
        raise SystemExit("dispatcher switch case decompilation missing")
    if "case 0x12:" not in dispatcher or "in_stack_fffffffffffffd60 & 0xffffffffffffff00);" not in dispatcher:
        raise SystemExit("case-0x12 decompiler argument expression missing")
    if "(**(code **)(*plVar6 + 0x1a8))(plVar6,lVar8,1,1,uVar13,0);" not in producer:
        raise SystemExit("immediate producer argument sequence missing")
    if "FUN_140657c30(DAT_14319a7c0,lVar8,plVar6,uVar13);" not in producer:
        raise SystemExit("tag-0x12 builder call missing")
    for token in ["local_88[0] = 0x12;", "local_80 = param_2;", "local_78 = param_3;", "local_70 = param_4;"]:
        if token not in builder:
            raise SystemExit("tag-0x12 payload layout proof missing: " + token)

    meta12 = json.loads(META_CASE12.read_text(encoding="utf-8"))
    meta4 = json.loads(META_CASE4.read_text(encoding="utf-8"))
    for meta, requested in [(meta12, "0x659C92"), (meta4, "0x65939C")]:
        if not meta.get("ok") or not meta.get("read_only") or not meta.get("auto_analysis_disabled"):
            raise SystemExit("Ghidra query was not a successful read-only, analysis-disabled capture")
        if meta.get("analysis_binary_product_version") != "1.6.1179" or meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f":
            raise SystemExit("Ghidra query binary identity mismatch")
        if meta.get("requested_address_rva") != requested:
            raise SystemExit("Ghidra query requested a different address")

    ep = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(ep.read_text(encoding="utf-8"))
    by_id = {row.get("id"): row for row in evidence.get("items", [])}
    if "EV-0631" in by_id:
        raise SystemExit("EV-0631 already exists")
    for required in ["EV-0615", "EV-0616", "EV-0618", "EV-0619", "EV-0620", "EV-0630"]:
        if required not in by_id:
            raise SystemExit("missing source evidence: " + required)

    note = EXP / "EV-0631-case12-corrected-argument-parity.md"
    note_text = """# EV-0631 — Correct tag-0x12 callsite and exact argument parity

## Scope and source identity

This is static GOG AE 1.6.1179.0 disassembly/decompilation from the existing read-only Ghidra project. The verified analysis binary SHA-256 is `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`; auto-analysis was disabled and no binary/project import or overwrite was attempted. These GOG RVAs are not transferred to Steam AE 1.6.1170.0.

## Competing models and discriminants

- H1: tag-0x12 deferred dispatch exactly matches the immediate AddRagdollHandler slot `+0x1a8` call, including argument five and a zero sixth argument. It predicts that the case-0x12 callsite stores zero at `[RSP+0x28]`, forms `[RSP+0x20]` from the payload dword, and sets `R8=1`, `R9=1`.
- H2: the deferred route inherits a different/nonzero sixth argument or takes argument values from the previously attributed callsite at RVA `0x65939c`. It predicts a nonzero byte at the actual case-0x12 call or a callsite that belongs to that case.

The exact discriminant is the dispatcher switch case paired with the instructions at the actual tag-0x12 virtual call, checked against the producer call and builder payload offsets.

## Direct evidence

- The caller-50 producer invokes `(*plVar6 + 0x1a8)(plVar6,lVar8,1,1,uVar13,0)` in the immediate route. Its deferred route calls `FUN_140657c30(...,lVar8,plVar6,uVar13)` [EV-0615], [EV-0616], raw `.local/ghidra/gog-query-20261019T191026Z.stdout.raw`.
- `FUN_140657c30` writes tag `0x12` at payload `+0`, its second parameter at `+8`, third at `+0x10`, and fourth dword at `+0x18` [EV-0618], raw `.local/ghidra/gog-query-20261019T191458Z.stdout.raw`.
- Dispatcher case `0x12` reads those payload fields and invokes the same vtable slot. The exact call is RVA `0x659c92`, not `0x65939c`. At `0x659c92`, instructions set `[RSP+0x28]=0`, load EAX from `[RDI+0x18]`, store it at `[RSP+0x20]`, set `R9B=1`, derive `R8D=1`, and set `RDX=R15`, `RCX=R14` [EV-0631], raw `.local/ghidra/gog-query-20261019T194800Z.stdout.raw`.
- The later address-only query confirms that the previously attributed `0x65939c` is a different virtual-call site in dispatcher case `0x4`; its byte-valued `R8` setup belongs to that case [EV-0631], raw `.local/ghidra/gog-query-20261019T195220Z.stdout.raw`. EV-0619's instruction reading was real, but its case attribution was wrong.
- The decompiler's case-0x12 sixth-argument expression masks off the low byte; the direct instruction query independently shows the sixth stack-argument byte is explicitly zero. The deferred call therefore does not use a nonzero inherited `param6` to skip `FUN_140e884d0`'s bit-1 eligibility check [EV-0630], [EV-0631].

## Result and limits

H1 is supported for the captured GOG call path; H2 is falsified for this callsite. The immediate producer and deferred case construct `(receiver, object, 1, 1, selector, 0)` in the same six argument positions. `FUN_14065b800` still forwards only the event pointer to the dispatcher, which reads the event fields and constructs the downstream call arguments. Thus the worker wrapper's limited call signature alone did not establish a mismatch.

This establishes static argument parity, not identical dynamic receiver state, callback execution, gameplay outcome, effective protection, armor-skill XP, Steam equivalence, or a vanilla exploit. No direct HitData/AV11/AV12/UseSkill edge is added. Caller 50 is bounded as a caller review; continue with caller 51/62.
"""
    write(note, note_text)

    note_rel = note.relative_to(ROOT).as_posix()
    hashes = {rel: sha(ROOT / rel) for rel in EXPECTED}
    hashes[note_rel] = sha(note)
    raw_primary_rel = ".local/ghidra/gog-query-20261019T194800Z.stdout.raw"
    evidence["items"].append({
        "captured_utc": meta12["captured_utc"],
        "edition": "AE",
        "modified_state": False,
        "id": "EV-0631",
        "kind": "native",
        "source": "Identity-checked GOG disassembly at the actual tag-0x12 dispatcher call RVA 0x659c92, paired with the AddRagdollHandler producer/builder and a correction query for RVA 0x65939c.",
        "artifact": "private-local:" + raw_primary_rel,
        "sha256": sha(RAW_CASE12),
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; existing-project read-only captures, auto-analysis disabled, no import or overwrite. GOG RVAs are not transferred to the separately verified Steam AE 1.6.1170.0 target.",
        "lane": "mechanism_inference",
        "tools": [
            "strict Python 3.12 dispatcher",
            "tools/ghidra_probe.py --address-rva 0x659c92 --timeout 600",
            "tools/ghidra_probe.py --address-rva 0x65939c --timeout 600",
            "captured producer, builder and dispatcher query outputs from EV-0615 through EV-0620"
        ],
        "coverage": "The actual case-0x12 virtual call at RVA 0x659c92 builds RCX=R14, RDX=R15, R8D=1, R9B=1, stack argument five from dword payload+0x18, and stack argument six as zero at [RSP+0x28]. Builder FUN_140657c30 maps its fourth parameter uVar13 to payload+0x18; the immediate producer supplies (receiver, object, 1, 1, uVar13, 0). A separate address query and the captured switch decompilation identify RVA 0x65939c as a case-0x4 call, correcting EV-0619's case attribution. The worker wrapper still directly passes only the event pointer; the dispatcher constructs downstream arguments from payload fields.",
        "result": "Tag-0x12 deferred and immediate AddRagdollHandler slot +0x1a8 calls have exact six-position argument parity in the captured GOG build: receiver, object, 1, 1, selector dword and zero sixth argument. The sixth-argument bypass model is falsified for this path. This is static control-flow/argument evidence only and establishes no runtime armor, skill-XP or vanilla-exploit outcome.",
        "local_hashes": hashes,
        "related_evidence": ["EV-0615", "EV-0616", "EV-0618", "EV-0619", "EV-0620", "EV-0630"]
    })
    write(ep, json.dumps(evidence, indent=2, ensure_ascii=False))

    claims = ROOT / "research/CLAIMS.md"
    ctext = claims.read_text(encoding="utf-8")
    ctext = replace_once(
        ctext,
        "| CL-L432 | In GOG, AddRagdollHandler slot-1 immediate and tag-0x12 deferred calls share vtable +0x1a8 and receiver/object roles, but the immediate call sets R8D=1, R9B=1 and two stack arguments, whereas the dispatcher loads R8D from the event selector byte and does not set matching R9/stack values in its block. | supported disassembly result; exact callee contract remains open | [EV-0619] | Worker-wrapper inherited register/stack context remains unexamined; no semantic or runtime equivalence is inferred. |",
        "| CL-L432 | **Retracted/superseded:** the earlier interpretation attributed dispatcher call RVA 0x65939c to case 0x12 and inferred mismatched argument setup. That call is in case 0x4; the actual case-0x12 call at RVA 0x659c92 matches the immediate six-argument setup [EV-0631]. | retracted by EV-0631; see CL-L444 | [EV-0619], [EV-0631] | Preserve the original disassembly as provenance; its switch-case attribution was incorrect. |",
        "CL-L432")
    ctext = replace_once(
        ctext,
        "| CL-L433 | GOG worker wrapper FUN_14065b800 calls FUN_140659160 with only the event pointer explicitly moved into RCX; it does not set RDX/R8/R9/stack arguments at the callsite, so those values are not proven payload fields for case 0x12. | supported disassembly result | [EV-0620] | The dispatcher's downstream virtual-call signature and inherited volatile-register values remain unknown. |",
        "| CL-L433 | GOG worker wrapper FUN_14065b800 calls FUN_140659160 with only the event pointer explicitly moved into RCX; it does not set RDX/R8/R9/stack arguments at that callsite. The dispatcher then reads its event payload and constructs the case-0x12 virtual-call arguments [EV-0631]. | supported, limited to the wrapper callsite | [EV-0620], [EV-0631] | The wrapper's register setup alone does not determine downstream argument parity or gameplay effect. |",
        "CL-L433")
    ctext = replace_once(
        ctext,
        "| CL-L443 | GOG bhkWorldM vtable slot 0x35 (+0x1a8) resolves to FUN_140e884d0; when its sixth argument is zero it requires FUN_140e0f510(object) and bit 1 of result+0x18, while a nonzero value skips this check before setting receiver+0xc5f8 and issuing optional callbacks. | supported for captured GOG target structure | [EV-0619], [EV-0620], [EV-0629], [EV-0630] | Deferred-call param6, callback targets and runtime effect remain unresolved; no direct armor/HitData/skill sink is established. |",
        "| CL-L443 | GOG bhkWorldM vtable slot 0x35 (+0x1a8) resolves to FUN_140e884d0; when its sixth argument is zero it requires FUN_140e0f510(object) and bit 1 of result+0x18, while a nonzero value skips this check before setting receiver+0xc5f8 and issuing optional callbacks. | supported for captured GOG target structure | [EV-0619], [EV-0620], [EV-0629], [EV-0630], [EV-0631] | The deferred case-0x12 call's sixth argument is now confirmed zero; callback targets, runtime effect and Steam behavior remain unresolved. No direct armor/HitData/skill sink is established. |",
        "CL-L443")
    if "| CL-L444 |" in ctext:
        raise SystemExit("CL-L444 already exists")
    ctext = ctext.rstrip() + "\n\n" + "| CL-L444 | In GOG AE 1.6.1179.0, AddRagdollHandler's immediate and tag-0x12 deferred routes call vtable slot +0x1a8 with the same six argument positions: receiver, object, 1, 1, selector dword and zero sixth argument. EV-0619's RVA 0x65939c instructions belong to case 0x4, not case 0x12. | supported for captured GOG static argument setup | [EV-0615], [EV-0616], [EV-0618], [EV-0631] | Dynamic receiver state, callback execution, runtime result, Steam equivalence and any armor-skill effect remain unobserved. |\n"
    write(claims, ctext)

    mechanisms = ROOT / "research/MECHANISMS.md"
    mtext = mechanisms.read_text(encoding="utf-8")
    mtext = replace_section(
        mtext,
        "## M-0172 — Immediate and tag-0x12 calls share slot +0x1a8 but not visible arguments (EV-0619)",
        """## M-0172 — Earlier case-0x12 mismatch attribution (superseded by M-0184)

EV-0619 correctly captured the instructions at RVA `0x65939c`, but those instructions belong to dispatcher case `0x4`, not case `0x12`. Applying them to tag `0x12` created a false mismatch model. The actual case-0x12 call is at RVA `0x659c92`; EV-0631 records its exact arguments and the correction. Preserve EV-0619 as provenance for the misattributed case; use M-0184 for the corrected route. Claim CL-L432 is retracted."""
    )
    mtext = replace_section(
        mtext,
        "## M-0173 — Worker wrapper forwards only the event pointer to FUN_140659160 (EV-0620)",
        """## M-0173 — Worker wrapper passes the event pointer; dispatcher builds call arguments (EV-0620, EV-0631)

At the sole direct call to `FUN_140659160`, `FUN_14065b800` explicitly loads only `RCX` with the event pointer [EV-0620]. The dispatcher reads case-0x12 values from that event and constructs the downstream virtual call arguments itself: receiver/object pointers, `1,1`, the selector dword and a zero sixth argument [EV-0631]. The wrapper's callsite therefore does not establish a mismatch or preclude parity. This remains static argument construction, not semantic, runtime or armor-XP equivalence. Claim CL-L433."""
    )
    mtext = replace_once(
        mtext,
        "RTTI-verified bhkWorldM slot `0x35` targets `FUN_140e884d0`. With sixth argument zero, it requires nonnull `FUN_140e0f510(object)` and bit `1` in the returned record's `+0x18`; nonzero skips this eligibility test. Passing the guard sets receiver byte `+0xc5f8` and emits optional callback records through `FUN_140e898f0` [EV-0630]. AddRagdollHandler's immediate call supplies zero; tag-0x12 deferred case setup does not locally establish the same stack/register arguments [EV-0619], [EV-0620]. Whether inherited `param6` is nonzero in a vanilla deferred call and whether this yields a reproducing exploit are open. No direct HitData/armor-skill sink is present. Claim CL-L443.",
        "RTTI-verified bhkWorldM slot `0x35` targets `FUN_140e884d0`. With sixth argument zero, it requires nonnull `FUN_140e0f510(object)` and bit `1` in the returned record's `+0x18`; nonzero skips this eligibility test. Passing the guard sets receiver byte `+0xc5f8` and emits optional callback records through `FUN_140e898f0` [EV-0630]. Both the immediate producer and deferred case-0x12 call pass zero in argument six [EV-0615], [EV-0631], so the proposed nonzero-argument eligibility bypass is falsified for this captured static path. Callback execution, runtime effect and Steam behavior remain open. No direct HitData/armor-skill sink is present. Claim CL-L443.",
        "M-0183")
    mtext = mtext.rstrip() + "\n\n" + "## M-0184 — Tag-0x12 deferred call exactly matches immediate slot +0x1a8 arguments (EV-0631)\n\nThe immediate AddRagdollHandler branch calls slot `+0x1a8` as `(receiver, object, 1, 1, uVar13, 0)`. Its deferred builder stores tag `0x12`, the same object and receiver pointers, and `uVar13` at event `+0x18`. The correct dispatcher case is at RVA `0x659c92`: it sets `RCX=R14`, `RDX=R15`, `R8D=1`, `R9B=1`, copies event `+0x18` to stack argument five, and explicitly stores zero at stack argument six. The formerly cited `0x65939c` site is a different case (`0x4`) [EV-0631]. This establishes exact static argument parity and falsifies the proposed `param6 != 0` check bypass, while leaving dynamic object state, callback outcome, runtime behavior and armor/skill causality untested. Claims CL-L432 (retracted), CL-L433, CL-L443 and CL-L444." + "\n"
    write(mechanisms, mtext)

    contradiction = ROOT / "research/CONTRADICTIONS.md"
    append_once(
        contradiction,
        "## C-OBJ2-Q79-TAG12-CALL-PARITY",
        """## C-OBJ2-Q79-TAG12-CALL-PARITY — immediate/deferred slot +0x1a8 arguments

- **Model A (earlier):** the deferred case uses a selector in R8 and lacks matching R9/stack arguments, so it differs from the immediate AddRagdollHandler call [EV-0619], [EV-0620].
- **Model B (corrected):** the cited `0x65939c` instruction belongs to case `0x4`; tag `0x12` calls slot `+0x1a8` at `0x659c92` with `(receiver, object, 1, 1, selector, 0)`, matching the immediate call [EV-0631].
- **Discriminant and assessment:** address-only GOG captures at both RVAs, the dispatcher case decompilation, producer call and tag-0x12 builder offsets support Model B. Model A is falsified for this static call path; CL-L432 is retracted and corrected by CL-L444.
- **Implication:** the zero sixth argument enforces the `FUN_140e884d0` object-state check on both immediate and deferred routes. This removes the proposed nonzero-`param6` bypass mechanism, but it does not establish dynamic callback results, Steam behavior, protection, armor XP or a vanilla reproduction. No OBJ-2 causal edge is added."""
    )

    graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
    append_once(
        graph,
        "EV-0631 corrects AddRagdollHandler tag-0x12 argument setup",
        """### EV-0631 corrects AddRagdollHandler tag-0x12 argument setup

The earlier parity mismatch came from assigning the `0x65939c` call (case `0x4`) to case `0x12`. The actual case-0x12 call at `0x659c92` constructs the same six argument positions as the immediate AddRagdollHandler call, including argument six equal to zero [EV-0631], [CL-L444], [M-0184]. This corrects a native control-flow/argument edge and falsifies the proposed eligibility-bypass mechanism. It adds no causal edge from AddRagdollHandler to HitData, protection or armor skill; callback/runtime outcomes remain open."""
    )

    results = EXP / "results.md"
    append_once(
        results,
        "### Caller 50/62 correction: case-0x12 argument parity (EV-0631)",
        """### Caller 50/62 correction: case-0x12 argument parity (EV-0631)

The earlier disassembly at RVA `0x65939c` was a valid virtual call, but the full dispatcher and a new address-only query identify it as case `0x4`, not case `0x12`. The actual tag-0x12 virtual call is at `0x659c92` [EV-0631].

The immediate producer passes `(receiver, object, 1, 1, uVar13, 0)`. The tag-0x12 builder stores the same receiver/object roles and `uVar13` at payload `+0x18`. Case 0x12 sets `R8D=1`, `R9B=1`, copies payload `+0x18` to stack argument five, and writes zero to stack argument six. Thus all six argument positions match. `FUN_14065b800` still forwards only the event pointer; the dispatcher consumes the event payload and forms the virtual call itself [EV-0615], [EV-0616], [EV-0618], [EV-0620], [EV-0631].

This falsifies the proposed nonzero-`param6` bypass of the `FUN_140e884d0` object-state gate for this static GOG path [EV-0630], [EV-0631]. The exact runtime receiver, optional callback execution, hit/protection effects and armor-skill XP remain unobserved; no OBJ-2 causal edge is added. Caller 50 is bounded for the worker-caller census. Continue with caller 51/62 `FUN_140658b50`."""
    )

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    hs = {row["id"]: row for row in item["hypotheses"]}
    updates = {
        "Q79-H127": {
            "model": "AddRagdollHandler slot-1's tag-0x12 deferred path exactly reproduces all six immediate slot +0x1a8 argument values.",
            "predicted_discriminant": "At the correct case-0x12 callsite RVA 0x659c92, RCX/RDX are the same receiver/object payload pointers, R8D=1, R9B=1, stack argument five comes from event +0x18, and stack argument six is zero; compare with the immediate producer and builder field mapping.",
            "status": "supported",
        },
        "Q79-H128": {
            "model": "The earlier apparent mismatch came from attributing dispatcher call RVA 0x65939c (case 0x4) to tag 0x12; the actual tag-0x12 call at RVA 0x659c92 matches the immediate six-argument setup.",
            "predicted_discriminant": "The switch case and instruction context distinguish case 0x4 at 0x65939c from case 0x12 at 0x659c92; only the latter is used to compare deferred AddRagdollHandler arguments.",
            "status": "falsified",
        },
        "Q79-H129": {
            "model": "The worker wrapper FUN_14065b800 passes only the event pointer to FUN_140659160; the dispatcher reads the event payload and constructs case-specific virtual-call arguments itself.",
            "predicted_discriminant": "At the wrapper call RCX is the only explicit argument; case 0x12 then reads its stored receiver/object/selector fields and sets the downstream vcall registers and stack arguments, so wrapper setup alone cannot establish a parity mismatch.",
            "status": "supported",
        },
        "Q79-H139": {
            "model": "The bhkWorldM +0x1a8 target FUN_140e884d0 uses param6==0 to enforce FUN_140e0f510(object) result+0x18 bit 1; nonzero skips that eligibility check. Both immediate and deferred case-0x12 calls pass param6=0.",
            "predicted_discriminant": "The target body gates on argument six, and exact producer/dispatcher call setup shows zero for both routes; this is a static GOG result, not a runtime behavior claim.",
            "status": "supported",
        },
        "Q79-H140": {
            "model": "The deferred tag-0x12 call may pass a nonzero inherited sixth argument and bypass the bhkWorldM +0x1a8 object-state check.",
            "predicted_discriminant": "The correct case-0x12 call at RVA 0x659c92 explicitly stores zero at [RSP+0x28], falsifying the nonzero inherited-param6 model for this GOG path. Runtime callback and Steam behavior remain separate unknowns.",
            "status": "falsified",
        },
        "Q79-H141": {
            "model": "Deferred tag-0x12 case supplies param6=0 to bhkWorldM slot +0x1a8: it explicitly stores zero in the sixth-argument byte while copying the selector dword to argument five.",
            "predicted_discriminant": "At case-0x12 callsite RVA 0x659c92, [RSP+0x28]=0 and [RSP+0x20] receives payload dword +0x18; the producer immediate call and builder mapping show exact six-position parity.",
            "status": "supported",
        },
    }
    for hid, values in updates.items():
        if hid not in hs:
            raise SystemExit("frontier hypothesis missing: " + hid)
        hs[hid].update(values)
        if "EV-0631" not in hs[hid].setdefault("evidence", []):
            hs[hid]["evidence"].append("EV-0631")
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0631"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L444"]))
    item["next_action"] = NEXT_ACTION
    frontier["session_next_action"] = NEXT_ACTION
    frontier["next_action"] = NEXT_ACTION
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: corrected caller-50 tag-0x12 parity and bounded the route; resume the exact worker caller census.",
        "next_action": NEXT_ACTION,
    }
    frontier["last_session_checkpoint"] = {
        "recorded_utc": now,
        "next_action": NEXT_ACTION,
        "active_process": "TX-20261018-0013",
    }
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state = state.replace("50 of 62 initially uninspected worker callers are reviewed, with 12 remaining", "51 of 62 initially uninspected worker callers are reviewed, with 11 remaining")
    state = replace_once(
        state,
        "EV-0615–EV-0620 map caller 50 tag 0x49 to RTTI-identified AddRagdollHandler slot 1; its immediate and deferred tag-0x12 routes share virtual +0x1a8 and pointer roles but not visible argument setup, and the worker wrapper forwards only the event pointer.",
        "EV-0615–EV-0618 map caller 50 tag 0x49 to RTTI-identified AddRagdollHandler slot 1. EV-0619's callsite attribution is corrected by EV-0631: RVA 0x65939c is case 0x4, while actual case 0x12 at 0x659c92 matches the immediate `(receiver, object,1,1,selector,0)` argument setup. The worker wrapper forwards the event pointer; the dispatcher builds arguments from its payload.",
        "STATE caller-50 parity summary")
    state = state.replace(
        "EV-0628 locates its GOG vtable at RVA 0x19E9078. Resolve slot +0x1a8 next; no HitData/armor edge is added yet. Dynamic callbacks and the exact live armor result remain open.",
        "EV-0628 locates its GOG vtable at RVA 0x19E9078; EV-0630 resolves slot +0x1a8, and EV-0631 confirms zero sixth argument on both immediate/deferred calls. Caller 50 is bounded with no direct HitData/armor edge. Dynamic callbacks and the exact live armor result remain open.")
    state = replace_once(
        state,
        "**Selected next line:** query address RVA `0x659c92` for exact case-0x12 slot `+0x1a8` call instructions; test whether the in-stack sixth argument is low-byte-cleared to zero or inherited nonzero [EV-0619], [EV-0630].",
        "**Selected next line:** run `python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x658b50 --list-call-edges --follow-incoming-calls 24 --follow-direct-calls 8 --timeout 600`; map caller 51/62 `FUN_140658b50`'s tag, payload, producer and dispatcher case, then screen the bounded route against mapped HitData/protection/AV11/AV12/UseSkill sinks. Caller 50's exact tag-0x12 argument parity and zero sixth argument are recorded in EV-0631; GOG runtime/callback behavior and Steam equivalence remain open.",
        "STATE exact next action")
    write(state_path, state)

    print("Registered EV-0631, CL-L444 and M-0184; corrected the caller-50 case attribution, updated the causal model/frontier, and checkpointed caller 51/62.")


if __name__ == "__main__":
    main()
