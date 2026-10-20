#!/usr/bin/env python3
"""Register caller 62/tag 0x62 and reconcile its bounded shared-handler route."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
GOG_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
CAPTURES = {
    ".local/ghidra/gog-query-20261019T220951Z.stdout.raw": "d04a32244861d50a9f8c7b3faece6ea1c85ca8c4c94b0fc1869089dc026f72fe",
    ".local/ghidra/gog-query-20261019T221102Z.stdout.raw": "9d35bf0b04893f9d6b946ee2c7d2b8a6e98facbf98b9351408e8b3eee34c03ad",
    ".local/ghidra/gog-query-20261019T221219Z.stdout.raw": "1ef51d8a7034ae8926f1f000917c710fbf9e2be35f4338885e0e91f9cdfc194c",
    ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": "adf7fe696c42d26eede69497ec1ec5d1745908d4d31c206915f07e2a921492ff",
}
METAS = {
    ".local/ghidra/gog-query-20261019T220951Z.meta.json": "7c9189256c1436df3f2b399f4611476408301ce1b0d3a6d2d9a66257826b19db",
    ".local/ghidra/gog-query-20261019T221102Z.meta.json": "3d27529e6c7f7b1ff5a4dd67d7ceff052a05afba8a7fb48e4a161cf9622c6b00",
    ".local/ghidra/gog-query-20261019T221219Z.meta.json": "cf13e69483715d76dee148c9b271b045ab1b55c022d3b93b3c86a2f5d15ec402",
    ".local/ghidra/gog-query-20261019T215421Z.meta.json": "b2091e46fbe7de2af95b156f394076a0dafbb1ce9ae9b18353458ff06a50d1be",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: str) -> None:
    path.write_text(value.rstrip() + "\n", encoding="utf-8", newline="\n")


def append_once(path: Path, marker: str, body: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker not in old:
        write(path, old.rstrip() + "\n\n" + body.strip())


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return text.replace(old, new, 1)


def main() -> None:
    raws: dict[str, str] = {}
    local_hashes: dict[str, str] = {}
    metas = []
    for rel, expected in CAPTURES.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("capture/hash mismatch: " + rel)
        raws[rel] = path.read_text(encoding="utf-8", errors="replace")
        local_hashes[rel] = expected
    for rel, expected in METAS.items():
        path = ROOT / rel
        if not path.is_file() or sha(path) != expected:
            raise SystemExit("metadata/hash mismatch: " + rel)
        meta = json.loads(path.read_text(encoding="utf-8"))
        if not (meta.get("ok") and meta.get("read_only") and meta.get("auto_analysis_disabled")
                and meta.get("program_executable_path_matches_gog_binary")
                and meta.get("analysis_binary_product_version") == "1.6.1179"
                and meta.get("analysis_binary_sha256") == GOG_SHA):
            raise SystemExit("failed GOG identity/read-only gate: " + rel)
        metas.append(meta)
        local_hashes[rel] = expected

    proof_sets = {
        ".local/ghidra/gog-query-20261019T220951Z.stdout.raw": [
            "TARGET_RVA=0x658FB0", "local_88[0] = 0x62;", "FUN_14065b800(param_1,local_88);",
            "CALLER_DECOMPILATION_BEGIN=FUN_1406c72d0", "FUN_140658fb0(DAT_14319a7c0,lVar2,*param_2,param_2[2]",
        ],
        ".local/ghidra/gog-query-20261019T221102Z.stdout.raw": [
            "TARGET_RVA=0x6BC400", "OUTGOING_DIRECT_CALL_EDGE_COUNT=39", "INDIRECT_CALL_SITE_COUNT=13",
            "FUN_1406b9df0 @ 1406b9df0", "FUN_1405bab90 @ 1405bab90", "FUN_140672640(param_1,param_2",
        ],
        ".local/ghidra/gog-query-20261019T221219Z.stdout.raw": [
            "TARGET_RVA=0x672640", "OUTGOING_DIRECT_CALL_EDGE_COUNT=55", "INDIRECT_CALL_SITE_COUNT=5",
            "DECOMPILATION_BEGIN=FUN_140672640", "FUN_14066d830(param_1,3,local_a8,local_e0",
        ],
        ".local/ghidra/gog-query-20261019T215421Z.stdout.raw": [
            "case 0x62:", "FUN_1406bc400(lVar15,lVar23,uVar21,uVar25);",
        ],
    }
    for rel, tokens in proof_sets.items():
        for token in tokens:
            if token not in raws[rel]:
                raise SystemExit(f"proof token missing from {rel}: {token}")

    note = EXP / "EV-0644-caller62-tag62-shared-actor-reaction-route.md"
    write(note, """# EV-0644 — Caller 62/tag-0x62 shared Actor reaction route

## Competing models and discriminants

- H1, a distinct serialized event reuses an Actor handler also reached from HitData: caller 62 writes tag 0x62, its sole analyzed producer is `FUN_1406c72d0`, and dispatcher case 0x62 calls `FUN_1406bc400`; the exact target also has a direct caller in mapped HitData handler `FUN_1406b9df0`. This predicts the producer, tag, dispatcher edge, shared target, and a bounded Actor/process response body.
- H2, tag 0x62 is itself an ordinary incoming HitData/AV11/AV12 continuation: this predicts that its producer or dispatcher forwards the mapped HitData context/resolver arguments or that the bounded target reaches the mapped armor-skill sink. A shared callee alone does not meet that prediction.
- H3, tag 0x62 changes level eligibility or effective armor protection: this predicts a mapped level/quest predicate or protection calculation in the producer/dispatcher/target path.

## Direct GOG evidence

The identity-checked read-only captures use GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 `9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f`, with auto-analysis disabled. This project is separate from Steam AE 1.6.1170.0; no RVA transfers to Steam.

- Caller 62 `FUN_140658fb0` writes payload tag `0x62`, retains its two object arguments, stores the remaining scalar/pointer payload, and queues through `FUN_14065b800`. Its one analyzed producer is `FUN_1406c72d0`; the captured branch submits the tag after process/event filters and passes an object pair plus a value resolved from the producer context [EV-0644].
- Dispatcher case 0x62 resolves the queued payload fields and calls `FUN_1406bc400`. The builder tag is `0x62`, not `0x0B` [EV-0644].
- `FUN_1406bc400` has 39 direct outgoing calls and 13 unresolved indirect sites. Its three direct callers include dispatcher case 0x62, `FUN_1405bab90`, and mapped HitData handler `FUN_1406b9df0`. It calls `FUN_140672640` on several Actor/process-conditioned branches [EV-0644]. This establishes exact code reuse, not identity of caller arguments or event cause.
- `FUN_140672640` has 55 direct outgoing calls and five unresolved indirect sites. Its captured body checks receiver/target state, PlayerCharacter identity and Actor flags, traverses related Actor entries, and submits event code `0x2A` through a direct helper. Exact helper semantics and dynamic virtual effects remain unresolved [EV-0644].
- The bounded tag-0x62 producer/dispatcher/target bodies contain no explicit level or quest-start gate and no mapped effective-protection or AV11/AV12/UseSkill sink. The 13 and five unresolved virtual sites, deeper descendants, ordinary-hit coverage, and Steam runtime effects remain outside this evidence [EV-0644], [EV-0260].
- The underlying caller inventory is 95 unique direct callers into `FUN_14065b800`; 33 were decompiled in the earlier sample and the exact remaining partition contains 62 bodies. This is the final body in that remaining partition; the full 62-body/tag review still does not resolve the clean Steam matched-hit test [EV-0397], [EV-0423], [EV-0644].

## Result and limits

H1 is supported for the captured static call route: a distinct tag-0x62 producer reaches an Actor reaction handler that is also called from mapped HitData code. H2 is not established: caller 62 does not construct tag 0x0B, and the shared handler does not identify the same runtime event, HitData fields, or armor-skill side effect. H3 is unsupported by the bounded bodies. No level-one access, effective-protection result, armor-XP bypass, ordinary-hit result, Steam result, or bounty resolution follows. Record the within-event producer/dispatcher/handler relationship; add no OBJ-1/OBJ-2 causal edge.

## Next action

Verify the exact 95-function caller set and its 62-body remaining partition against the preserved identity-checked census, close Q-0079 as a bounded static caller review, and begin the highest-priority ready P0 line Q-0080. The live Steam matched-hit/protection/raw-AVSK test remains open under EV-0260.
""")
    local_hashes[note.relative_to(ROOT).as_posix()] = sha(note)

    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    items = evidence.get("items", [])
    ids = {row.get("id") for row in items}
    if not {"EV-0397", "EV-0423", "EV-0295", "EV-0296", "EV-0260"} <= ids:
        raise SystemExit("missing contextual evidence")
    latest = max(metas, key=lambda row: row.get("captured_utc", ""))
    record = {
        "captured_utc": latest["captured_utc"], "edition": "AE", "modified_state": False,
        "id": "EV-0644", "kind": "native",
        "source": "Identity-checked read-only GOG trace of caller 62/tag 0x62, its producer, dispatcher, shared Actor handler and direct action helper.",
        "artifact": "private-local:.local/ghidra/gog-query-20261019T220951Z.stdout.raw",
        "sha256": CAPTURES[".local/ghidra/gog-query-20261019T220951Z.stdout.raw"],
        "runtime": "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 " + GOG_SHA + "; existing-project read-only queries with auto-analysis disabled. Separate from Steam AE 1.6.1170.0.",
        "lane": "mechanism_inference",
        "tools": ["strict Python 3.12 dispatcher", "tools/ghidra_probe.py read-only call-edge queries"],
        "coverage": "Caller 62/tag 0x62 builder and sole analyzed producer FUN_1406c72d0; dispatcher case 0x62; FUN_1406bc400 39-direct/13-indirect census and its mapped HitData direct caller; FUN_140672640 55-direct/5-indirect body; final body in the 62-function remaining caller partition.",
        "result": "Caller 62/tag 0x62 is a distinct producer/dispatcher path into FUN_1406bc400, an Actor/process response helper also directly called by mapped HitData handler FUN_1406b9df0. This proves shared code identity, not event or argument identity. Bounded bodies show no explicit level/quest gate or mapped effective-protection/AV11/AV12/UseSkill sink; dynamic sites and live Steam behavior remain unresolved.",
        "local_hashes": local_hashes,
        "related_evidence": ["EV-0397", "EV-0423", "EV-0295", "EV-0296", "EV-0260"],
    }
    if "EV-0644" not in ids:
        items.append(record)
        write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L457 |",
        "| CL-L457 | In GOG AE 1.6.1179.0, caller 62/tag 0x62 is produced by FUN_1406c72d0 and dispatches to FUN_1406bc400, which is also a direct callee of mapped HitData handler FUN_1406b9df0; the captured target calls Actor/process helper FUN_140672640. | supported for the captured producer/dispatch/shared-handler route | [EV-0644], [EV-0295], [EV-0296] | Shared callee identity does not establish ordinary-hit or argument identity; 13 target and five helper indirect sites, protection, AV11/AV12/UseSkill, runtime and Steam behavior remain unresolved. No OBJ-1/OBJ-2 causal edge follows. |")
    append_once(ROOT / "research/MECHANISMS.md", "## M-0197 —",
        """## M-0197 — Tag-0x62 serialized Actor/process response route (EV-0644)

Caller 62 builds tag 0x62 from producer `FUN_1406c72d0`; dispatcher case 0x62 resolves its retained object/value payload and calls `FUN_1406bc400` [EV-0644]. That function also has a direct caller in mapped HitData handler `FUN_1406b9df0`, and it conditionally calls `FUN_140672640`, whose captured body processes Actor/PlayerCharacter state and related Actor entries [EV-0644]. The exact shared callee is supported; runtime event/argument identity is not. `FUN_1406bc400` has 13 unresolved indirect sites and `FUN_140672640` has five. No explicit level/quest gate or mapped effective-protection, AV11/AV12, or UseSkill sink is established in this bounded path. No OBJ-1/OBJ-2 causal edge is added. Claim CL-L457.""")
    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ2-Q79-TAG62-SHARED-ACTOR-HANDLER-VS-ARMOR-XP",
        """## C-OBJ2-Q79-TAG62-SHARED-ACTOR-HANDLER-VS-ARMOR-XP — shared HitData-reached helper versus same hit/skill event

- Model A: caller 62/tag 0x62 is a distinct event that reuses `FUN_1406bc400`, an Actor/process handler also called by the mapped HitData handler.
- Model B: tag 0x62 itself represents the ordinary incoming HitData continuation and reaches the AV11/AV12 award path.
- Model C: tag 0x62 changes level-one eligibility or effective armor protection.
- Evidence: caller builder/sole producer, tag-0x62 dispatcher case, exact target direct-call census, mapped HitData caller, and direct helper census [EV-0644], [EV-0295], [EV-0296].
- Assessment: A is supported as call-graph reuse. B is not established: the caller is a different producer, the builder writes tag 0x62, and no same-event arguments or mapped armor-skill sink are shown. C has no direct gate/protection evidence. Unresolved indirect descendants and runtime effects remain open; no OBJ-1/OBJ-2 edge is added.
- Discriminant: reopen B only with producer-backed argument identity/ordinary-hit coverage or a clean Steam event trace; reopen C only with a mapped level/protection path or controlled effective-protection observation.""")
    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### EV-0644 maps caller 62 tag-0x62 shared Actor handler",
        """### EV-0644 maps caller 62 tag-0x62 shared Actor handler

Caller 62's tag-0x62 producer `FUN_1406c72d0` routes through the worker dispatcher to `FUN_1406bc400`; the exact target is also called by mapped HitData handler `FUN_1406b9df0` [EV-0644], [EV-0295], [EV-0296]. This is a supported code-reuse edge, not proof of equal runtime events or arguments. The target's Actor/process action helper and bounded direct call body add no mapped level gate, protection, AV11/AV12 or UseSkill relationship [EV-0644]. Preserve a no-edge rationale from this route to OBJ-1/OBJ-2; the clean Steam matched-hit observation remains decisive [EV-0260]. Claim mapping: CL-L457 -> M-0197.""")
    append_once(EXP / "results.md", "### Caller 62/62: tag-0x62 shared Actor handler (EV-0644)",
        """### Caller 62/62: tag-0x62 shared Actor handler (EV-0644)

Caller 62 `FUN_140658fb0` writes tag 0x62; its sole analyzed producer is `FUN_1406c72d0`, and dispatcher case 0x62 calls `FUN_1406bc400`. That target's three direct callers include the mapped HitData handler `FUN_1406b9df0`; it conditionally calls `FUN_140672640`, whose captured body checks Actor/PlayerCharacter state and related Actor entries. These facts establish shared code identity, not matching event origin or arguments [EV-0644], [EV-0295], [EV-0296]. The bounded bodies show no explicit level/quest gate or mapped effective-protection/AV11/AV12/UseSkill sink; 13 and five indirect sites and runtime behavior remain open. No OBJ-1/OBJ-2 causal edge is added. The 95-function census contains an exact partition of 33 previously decompiled plus 62 remaining bodies; caller 62 is the final body. Verify the preserved partition, close Q-0079, then begin Q-0080; Steam matched-hit/protection/raw-AVSK evidence remains required [EV-0397], [EV-0423], [EV-0260].""")
    append_once(ROOT / "research/ROADMAP.md", "## Cross-domain synthesis — Q-0079 caller 62 (EV-0644)",
        """## Cross-domain synthesis — Q-0079 caller 62 (EV-0644)

The last worker caller adds a second HitData-adjacent code reuse observation: caller 60/tag 0x5C was directly produced inside the mapped HitData handler and rejoined a vector/physics helper [EV-0642], while caller 62/tag 0x62 comes from `FUN_1406c72d0` and reaches `FUN_1406bc400`, another helper called by mapped HitData code [EV-0644]. The payloads and target helpers differ, so the worker's shared transport and reused Actor helpers do not establish one causal event or an armor XP/protection mechanism. Caller 61 remains a separate eye-texture update [EV-0643]. No OBJ-1/OBJ-2 causal edge is added. Reconcile the 95-caller exact partition, then select Q-0080; preserve the live Steam matched-hit test as open [EV-0260].""")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    item = next(row for row in frontier["items"] if row.get("id") == "Q-0079")
    known = {row.get("id") for row in item.get("hypotheses", [])}
    if "Q79-H165" not in known:
        item["hypotheses"].append({
            "id": "Q79-H165",
            "model": "Caller 62/tag 0x62 is a distinct producer/dispatcher route into FUN_1406bc400, a code identity also called by mapped HitData handler FUN_1406b9df0; it establishes shared Actor response code, not same event origin.",
            "predicted_discriminant": "Producer and dispatcher calls identify tag 0x62 and the exact shared target; ordinary-hit identity would additionally require argument/source equivalence or runtime observation.",
            "status": "supported", "evidence": ["EV-0644", "EV-0295", "EV-0296"],
        })
    if "Q79-H166" not in known:
        item["hypotheses"].append({
            "id": "Q79-H166",
            "model": "Caller 62/tag 0x62 is itself the ordinary incoming HitData continuation that preserves effective protection and awards AV11/AV12 armor skill.",
            "predicted_discriminant": "The producer-backed route should preserve mapped HitData arguments or reach a mapped protection/AV11/AV12/UseSkill sink; shared helper identity alone is insufficient.",
            "status": "proposed", "evidence": ["EV-0644", "EV-0260"],
        })
    item["evidence"] = list(dict.fromkeys([*item.get("evidence", []), "EV-0644"]))
    item["linked_claims"] = list(dict.fromkeys([*item.get("linked_claims", []), "CL-L457"]))
    next_action = ("python3 scripts/python_env.py run experiments/EXP-0128-hit-worker-callers/verify_worker_caller_sets.py "
                   "--original-raw .local/ghidra/gog-query-20261018T155745Z.stdout.raw "
                   "--fresh-raw .local/ghidra/gog-query-20261018T202505Z.stdout.raw "
                   "--fresh-meta .local/ghidra/gog-query-20261018T202505Z.meta.json "
                   "--inventory .local/alignment/transactions/TX-20261018-0013/remaining-worker-callers.json "
                   "--query-source tools/ghidra_scripts/ReadOnlyTargetedQuery.java "
                   "--output .local/alignment/transactions/TX-20261018-0013/worker-caller-set-verification.final.json; "
                   "confirm 95/95 unique callers and exact 33+62 partition, close Q-0079, then begin ready P0 frontier Q-0080.")
    item["next_action"] = next_action
    frontier["session_next_action"] = next_action
    frontier["next_action"] = next_action
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    frontier["session_checkpoint"] = {
        "timestamp_utc": now,
        "task": "Q-0079/TX-20261018-0013: caller 62/tag 0x62 is bounded as a shared Actor handler route; all 62 remaining caller bodies are reviewed.",
        "next_action": next_action,
    }
    frontier["last_session_checkpoint"] = {"recorded_utc": now, "next_action": next_action, "active_process": "TX-20261018-0013"}
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    state_path = ROOT / "STATE.md"
    state = state_path.read_text(encoding="utf-8")
    state = replace_once(state, "61 of 62 initially uninspected worker callers are reviewed, with 1 remaining.",
                         "62 of 62 initially uninspected worker callers are reviewed; the exact remaining-caller inventory is ready for final reconciliation.", "STATE main count")
    state = replace_once(state, "Q-0079 has 61/62 initially uninspected worker callers reviewed; 1 remains.",
                         "Q-0079 has 62/62 initially uninspected worker callers reviewed; final exact-partition reconciliation remains.", "STATE OBJ-2 count")
    old_summary = "EV-0643 maps caller 61/tag 0x61 to an eye-headpart texture update through a guarded nested pointer replacement; caller 62 remains to be inspected before closing the exact census."
    new_summary = old_summary.replace("caller 62 remains to be inspected before closing the exact census.",
        "EV-0644 maps final caller 62/tag 0x62 from FUN_1406c72d0 through dispatch to FUN_1406bc400, an Actor/process handler also called by mapped HitData code; shared code does not establish event identity or armor XP. All 62 remaining bodies are reviewed; exact caller-set reconciliation and clean Steam matched-hit/protection/raw-AVSK evidence remain open.")
    state = replace_once(state, old_summary, new_summary, "STATE caller-61 summary")
    old_next_line = next((line for line in state.splitlines() if line.startswith("**Selected next line:**")), None)
    if old_next_line is None or "caller 62/62 `FUN_140658fb0`" not in old_next_line:
        raise SystemExit("STATE selected-next checkpoint mismatch")
    state = state.replace(old_next_line, "**Selected next line:** verify the preserved identity-checked 95-function worker caller set against its exact 33+62 partition using `verify_worker_caller_sets.py`; then close Q-0079 as a bounded static review and begin ready P0 line Q-0080. Caller 62/tag 0x62 shares `FUN_1406bc400` with mapped HitData code but does not establish the same hit or armor-skill event.", 1)
    checkpoint = ("\n\nActive checkpoint " + now + " (`TX-20261018-0013`, Q-0079): all 62/62 initially uninspected worker caller bodies are reviewed. "
                  "EV-0644 maps caller 62/tag 0x62 through FUN_1406bc400, which is also called by mapped HitData handler FUN_1406b9df0; no event identity or OBJ-1/OBJ-2 causal edge follows. "
                  "Next action: " + next_action)
    state += checkpoint
    write(state_path, state)
    print("Registered EV-0644/CL-L457/M-0197 and checkpointed exact 62-caller reconciliation.")


if __name__ == "__main__":
    main()
