from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GHIDRA = ROOT / ".local/ghidra"
RUNTIME = (
    "GOG SkyrimSE.exe ProductVersion 1.6.1179.0, SHA-256 "
    "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; "
    "existing-project read-only query, auto-analysis disabled, no import or overwrite."
)
CAPTURES = [
    {
        "id": "EV-0567", "stem": "gog-query-20261019T163514Z", "rva": "0x6585a0",
        "source": "Identity-checked read-only GOG query of exact worker caller 37/62 FUN_1406585a0",
        "command": "tools/ghidra_probe.py --rva 0x6585a0 --list-call-edges --timeout 600",
        "related": ["EV-0545", "EV-0260"],
        "coverage": (
            "Complete direct-call census of one exact remaining worker caller. FUN_1406585a0 has one outgoing "
            "edge to FUN_14065b800, zero indirect sites, and one direct producer FUN_14068b3a0 at 0x14068b434. "
            "It stores tag 0x2e, a retained object pointer at +0x28, and two byte arguments."
        ),
        "result": (
            "Caller 37/62 is a small tag-0x2e builder. Its one producer is FUN_14068b3a0; dispatcher case 0x2e "
            "returns the Actor pointer and both bytes to that same routine [EV-0545]. No hit, armor, ActorValue, "
            "or XP meaning follows from the builder alone."
        ),
    },
    {
        "id": "EV-0568", "stem": "gog-query-20261019T163636Z", "rva": "0x6f1c00",
        "source": "Identity-checked read-only GOG query of process-field getter FUN_1406f1c00",
        "command": "tools/ghidra_probe.py --rva 0x6f1c00 --list-call-edges --timeout 600",
        "related": ["EV-0570", "EV-0260"],
        "coverage": (
            "Complete edge and caller census of FUN_1406f1c00: zero direct calls, zero indirect sites, one direct "
            "caller FUN_14068b3a0. If its +0x10 pointer is nonnull, it returns the dword at that object +0x328."
        ),
        "result": (
            "The getter reads one process-associated numeric field and has no deeper call path. Its runtime field "
            "name/type is not identified; it is not mapped as an ActorValue or armor parameter."
        ),
    },
    {
        "id": "EV-0569", "stem": "gog-query-20261019T163729Z", "rva": "0x6f1be0",
        "source": "Identity-checked read-only GOG query of process-field setter FUN_1406f1be0",
        "command": "tools/ghidra_probe.py --rva 0x6f1be0 --list-call-edges --timeout 600",
        "related": ["EV-0568", "EV-0570", "EV-0260"],
        "coverage": (
            "Complete edge and caller census of FUN_1406f1be0: zero direct calls, zero indirect sites, one direct "
            "caller FUN_14068b3a0. If its +0x10 pointer is nonnull, it stores the supplied dword at that object +0x328."
        ),
        "result": (
            "The paired setter writes the same process-associated numeric field read by FUN_1406f1c00. No ActorValue, "
            "HitData, protection, or skill award is invoked by either helper."
        ),
    },
    {
        "id": "EV-0570", "stem": "gog-query-20261019T163845Z", "rva": "0x68b3a0",
        "source": "Identity-checked read-only GOG direct/incoming-call analysis of tag-0x2e handler FUN_14068b3a0",
        "command": "tools/ghidra_probe.py --rva 0x68b3a0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "related": ["EV-0567", "EV-0568", "EV-0569", "EV-0545", "EV-0291", "EV-0260"],
        "coverage": (
            "FUN_14068b3a0 has nine direct calls, one indirect slot +0x4c8 site, and five callsites from four "
            "direct callers: FUN_140669f70 (two), FUN_1406a1830, FUN_1406c4830, and dispatcher FUN_140659160. "
            "Its clear-gate branch reads process+0x10+0x328 and compares it with Actor+0x260 before conditionally "
            "writing Actor+0x260 plus a constant. A player-only branch can resolve a TESImageSpaceModifier and "
            "call FUN_14029def0; another byte-gated branch calls FUN_1408044e0."
        ),
        "result": (
            "Caller/dispatcher evidence supports deferred re-entry into an Actor/process numeric-state routine. "
            "FUN_1406a1830's caller body follows FSTLandHardHeavy/Light selection and a positive computed value; "
            "FUN_140669f70 contains an NPCHumanDrowning string branch and a separate call path that invokes "
            "FUN_140668f50 before FUN_14068b3a0. The main routine has no direct mapped HitData, AV11/AV12, "
            "protection, armor-skill, or XP target. The +0x4c8 dynamic site, FUN_1408044e0, other producer "
            "semantics, and Steam behavior remain unresolved."
        ),
    },
    {
        "id": "EV-0571", "stem": "gog-query-20261019T164008Z", "rva": "0x668f50",
        "source": "Identity-checked read-only GOG direct/caller analysis of shared health-update helper FUN_140668f50",
        "command": "tools/ghidra_probe.py --rva 0x668f50 --list-call-edges --follow-direct-calls 8 --timeout 600",
        "related": ["EV-0570", "EV-0294", "EV-0291", "EV-0260"],
        "coverage": (
            "FUN_140668f50 has nine direct calls, two indirect sites, eight direct-call sites across seven caller "
            "functions. The body conditionally calls FUN_1406b49d0 with operation 2, ActorValue code 0x18, and a "
            "scaled float, then selects direct FUN_1402da2b0 or queued tag-0x1e FUN_140656de0 according to "
            "FUN_1406d4110. Direct callers include FUN_1406b9df0, FUN_1406bcaa0, FUN_1406a1830, "
            "FUN_140669f70, and dispatcher FUN_140659160."
        ),
        "result": (
            "Existing GOG mapping identifies the 0x18 ActorValue branch in FUN_1406b49d0 as Health [EV-0294, "
            "CL-L128]. The shared helper is used by the HitData/armor-related handlers as well as the hard-landing "
            "and Actor-update callers. This makes those parent paths adjacent to a generic Health update, but does "
            "not show that tag 0x2e itself calls Health damage or awards armor skill. Two indirect sites and the "
            "runtime sign/result remain unresolved."
        ),
    },
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_block(path: Path, marker: str, block: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker not in old:
        path.write_text(old.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


EVIDENCE_PATH = ROOT / "research/EVIDENCE.json"
evidence = read_json(EVIDENCE_PATH)
known = {item["id"]: item for item in evidence["items"]}
for spec in CAPTURES:
    raw = GHIDRA / f"{spec['stem']}.stdout.raw"
    stderr = GHIDRA / f"{spec['stem']}.stderr.raw"
    meta_path = GHIDRA / f"{spec['stem']}.meta.json"
    meta = read_json(meta_path)
    if not meta.get("ok") or meta.get("requested_rva", "").lower() != spec["rva"].lower():
        raise SystemExit(f"capture identity/check failed for {spec['id']}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or not meta.get("program_executable_path_matches_gog_binary"):
        raise SystemExit(f"GOG build identity failed for {spec['id']}")
    raw_hash, stderr_hash, meta_hash = sha(raw), sha(stderr), sha(meta_path)
    if raw_hash != meta.get("stdout_sha256") or stderr_hash != meta.get("stderr_sha256"):
        raise SystemExit(f"capture hash mismatch for {spec['id']}")
    item = {
        "kind": "native", "edition": "AE", "runtime": RUNTIME, "modified_state": False,
        "lane": "mechanism_inference", "id": spec["id"], "source": spec["source"],
        "artifact": f"private-local:.local/ghidra/{raw.name}", "sha256": raw_hash,
        "captured_utc": meta["captured_utc"],
        "tools": ["strict Python 3.12 dispatcher", spec["command"]],
        "coverage": spec["coverage"], "result": spec["result"],
        "local_hashes": {
            f".local/ghidra/{raw.name}": raw_hash,
            f".local/ghidra/{stderr.name}": stderr_hash,
            f".local/ghidra/{meta_path.name}": meta_hash,
        },
        "related_evidence": spec["related"],
    }
    if spec["id"] in known:
        if known[spec["id"]].get("sha256") != raw_hash:
            raise SystemExit(f"evidence ID collision for {spec['id']}")
    else:
        evidence["items"].append(item)
        known[spec["id"]] = item
write_json(EVIDENCE_PATH, evidence)

claims = ROOT / "research/CLAIMS.md"
claim_lines = [
    "| CL-L379 | In GOG AE 1.6.1179.0, exact worker caller 37/62 FUN_1406585a0 builds tag 0x2e with a retained object pointer and two bytes; its captured producer FUN_14068b3a0 calls it when FUN_1406d4110 is set, and dispatcher case 0x2e calls FUN_14068b3a0 with those fields. | supported for the exact static builder/dispatcher continuation | [EV-0567], [EV-0570], [EV-0545] | The event is a deferred Actor/process continuation; runtime scheduling and the bytes' meanings remain unknown. |",
    "| CL-L380 | In GOG AE 1.6.1179.0, FUN_14068b3a0's clear-gate path reads process+0x10+0x328, compares it with Actor+0x260, and can write Actor+0x260 plus a constant; a player-only branch resolves a TESImageSpaceModifier and invokes visual/sound helpers. | supported for the captured body and call graph | [EV-0570], [EV-0568], [EV-0569] | The process field is unnamed; the +0x4c8 dynamic target and FUN_1408044e0 remain unresolved. No direct HitData, AV11/AV12, protection, armor-skill, or XP target appears. |",
    "| CL-L381 | FUN_1406f1c00 and FUN_1406f1be0 are no-call helpers with one observed caller, FUN_14068b3a0; together they read and write the same dword at *(process+0x10)+0x328. | supported for the exact GOG helper bodies | [EV-0568], [EV-0569] | The field's runtime semantic name and relation to any ActorValue are unresolved. |",
    "| CL-L382 | FUN_140668f50 conditionally sends ActorValue code 0x18 through FUN_1406b49d0 and is shared by mapped HitData handlers and Actor/landing update callers; existing evidence maps the selected code as Health. | supported for the bounded static call/data flow | [EV-0571], [EV-0294], [CL-L128] | The selected operation's runtime result/sign and any AV11/AV12 award remain conditional; its adjacency to tag 0x2e does not make the tag a damage or skill event. |",
]
for line in claim_lines:
    append_block(claims, line.split(" | ")[0], line)

mechanism = ROOT / "research/MECHANISMS.md"
append_block(
    mechanism,
    "## M-0134 — Tag-0x2e Actor process continuation beside a shared Health update (Q-0079)",
    """## M-0134 — Tag-0x2e Actor process continuation beside a shared Health update (Q-0079)

FUN_1406585a0 builds tag 0x2e with an Actor pointer and two bytes; its captured caller FUN_14068b3a0 queues this record when the shared thread gate is set, and dispatcher case 0x2e returns the fields to FUN_14068b3a0 [EV-0567], [EV-0570], [EV-0545]. On the gate-clear path, the handler checks the primary Actor slot +0x4c8 predicate, reads process field `*( *(process+0x10) + 0x328 )`, compares it with Actor+0x260, and conditionally writes a value based on Actor+0x260. The paired process helpers are exact no-call getter/setter bodies with one observed caller [EV-0568], [EV-0569]. Player-only branches can resolve a TESImageSpaceModifier and call visual/sound helpers. One captured parent caller contains FSTLandHardLight/Heavy selection; another contains an NPCHumanDrowning string branch [EV-0570].

A separate shared helper, FUN_140668f50, can pass ActorValue code 0x18 through FUN_1406b49d0; prior mapping identifies that code as Health. The helper is also called by the mapped HitData handlers FUN_1406b9df0/FUN_1406bcaa0 and by landing/Actor-update paths [EV-0571], [EV-0294], [CL-L128]. Some parent paths call this Health helper and FUN_14068b3a0 in the same routine, but the tag-0x2e body itself has no direct HitData, AV11/AV12, protection, armor-skill, or XP target. Do not equate the shared Health helper or thread gate with an armor-XP route. The dynamic +0x4c8 override, FUN_1408044e0 descendants, other producer meaning, Steam behavior, and exact field identity remain open. Claims CL-L379–CL-L382.""",
)

results = ROOT / "experiments/EXP-0128-hit-worker-callers/results.md"
append_block(
    results,
    "## Caller 37/62 — tag-0x2e Actor/process continuation",
    """## Caller 37/62 — tag-0x2e Actor/process continuation

EV-0567 maps FUN_1406585a0: one outgoing edge to FUN_14065b800, zero indirect sites, and one producer FUN_14068b3a0. It retains the object pointer and stores two bytes with tag 0x2e. Dispatcher case 0x2e calls FUN_14068b3a0 with those fields [EV-0545], supporting deferred same-method re-entry.

EV-0570 gives FUN_14068b3a0 nine direct calls, one indirect +0x4c8 site, and five callsites from four callers including dispatcher FUN_140659160. When the shared gate is clear, it reads process+0x10+0x328 through FUN_1406f1c00, compares that value with Actor+0x260, and may write Actor+0x260 plus a constant through FUN_1406f1be0. EV-0568/0569 show these paired helpers have no direct calls/sites and one observed caller each; they read/write the same unnamed process dword. A player-only branch may resolve TESImageSpaceModifier and reach image-space/sound helpers. The +0x4c8 base Actor slot is the previously mapped masked state predicate FUN_140677100 [EV-0291], but runtime overrides remain unknown.

The captured direct callers include FUN_1406a1830, whose body selects FSTLandHardHeavy/Light and calls the update after a positive computed value, and FUN_140669f70, which contains an NPCHumanDrowning string branch plus a separate path invoking FUN_140668f50 before FUN_14068b3a0 [EV-0570]. EV-0571 shows FUN_140668f50 conditionally sends ActorValue code 0x18 through FUN_1406b49d0; prior GOG mapping identifies Health and shows this helper is also called by the HitData/armor-related handlers [EV-0294], [CL-L128]. Thus some parent contexts are adjacent to Health updates, but this does not turn tag 0x2e into HitData or an armor-skill event. The tag-0x2e routine has no direct mapped HitData/AV11/AV12/protection/armor-skill target. Its +0x4c8 dynamic override, FUN_1408044e0 descendants, untyped process field, and clean Steam behavior remain open. Caller37 adds no tag-0x0b builder; H1/H2/H3 and H64/H65 do not change. The inventory covers 37/62 callers, with 25 remaining. Next inspect caller 38/62 FUN_140658660 after the focused FUN_1408044e0 check.

Raw .local/ghidra/gog-query-20261019T163514Z.stdout.raw SHA-256 042b9277d9375b3a117f6351d73bd85f940dcafe6bc7e53aa5888f28015048f5.
Raw .local/ghidra/gog-query-20261019T163636Z.stdout.raw SHA-256 c7302b2d9e1b8575beee015bd60239d086aa4f6f860ae86f7bd261508a5cd1ea.
Raw .local/ghidra/gog-query-20261019T163729Z.stdout.raw SHA-256 0c1891fe750194e2cf8803433230db097502c662850e77939e93fb7b64f8d2ce.
Raw .local/ghidra/gog-query-20261019T163845Z.stdout.raw SHA-256 a89325db82c8905d365240dc1cb21e2c11ae2af9883561fb8c07ee041b164477.
Raw .local/ghidra/gog-query-20261019T164008Z.stdout.raw SHA-256 6f02698b18392bb15531756ecfda147a2e0ecdc0e1f04b265d2844dcf807e8c9.""",
)

hypothesis = ROOT / "experiments/EXP-0128-hit-worker-callers/hypothesis.md"
append_block(
    hypothesis,
    "## Caller 37 competing models",
    """## Caller 37 competing models

- Q79-H66: Tag 0x2e is a deferred Actor/process numeric-state and presentation continuation. Prediction: the builder and dispatcher return to FUN_14068b3a0, whose clear-gate branch reads/writes one process dword and may apply player image-space/sound effects. Supported for the captured route; dynamic +0x4c8 and FUN_1408044e0 descendants remain open [EV-0545], [EV-0567]–[EV-0570].
- Q79-H67: A tag-0x2e parent path may be hit-adjacent because FUN_140669f70 calls the shared Health update FUN_140668f50 before FUN_14068b3a0, and FUN_140668f50 is also called by the mapped HitData handlers. Prediction: exact source-type and descendant mapping reveals a hit event or a relevant AV11/AV12/UseSkill target; the current evidence instead includes hard-landing and drowning contexts and does not support this outcome. Proposed, unresolved [EV-0570], [EV-0571], [EV-0294], [CL-L128].""",
)

expected = ROOT / "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md"
append_block(
    expected,
    "EV-0567–EV-0571 discriminant",
    """EV-0567–EV-0571 discriminant: follow FUN_1408044e0, the remaining direct helper selected by a tag-0x2e byte, and resolve the process field at *( *(process+0x10)+0x328 ) only from producer-backed type evidence. A mapped HitData/AV11/AV12/UseSkill descendant supports Q79-H67; a bounded Actor/process or visual target supports H66 for this route. Preserve the hard-landing/drowning contexts, dynamic +0x4c8 override, and the clean Steam positive-hit/protection/raw-AVSK requirement.""",
)

implications = ROOT / "experiments/EXP-0128-hit-worker-callers/implications.md"
append_block(
    implications,
    "Caller 37 cross-system note",
    """Caller 37 cross-system note: FUN_140668f50 is a shared Health ActorValue helper used by HitData/armor-related handlers and by hard-landing/Actor-update callers, while tag 0x2e's own body updates an unnamed process field and presentation state. This is a shared downstream Health primitive, not evidence that the tag-0x2e worker itself awards armor XP. The shared worker gate also appears in water/effect and Actor-state routes; its use is scheduling, not proof of a combat or quest-state dependency. OBJ-1 remains independent.""",
)

graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
append_block(
    graph,
    "EV-0567–EV-0571 add tag-0x2e and shared Health context",
    """EV-0567–EV-0571 add tag-0x2e Actor/process edges: FUN_14068b3a0 -> worker tag-0x2e -> dispatcher case 0x2e -> FUN_14068b3a0; the clear-gate branch reads/writes `*( *(process+0x10)+0x328 )` against Actor+0x260 and can invoke player image-space/sound helpers. In two parent contexts the routine is adjacent to FUN_140668f50's Health ActorValue update, a helper also used by mapped HitData handlers. Keep the Health-to-process adjacency separate from the tag-0x2e body: no direct AV11/AV12/UseSkill, armor-protection, or XP edge is added. FUN_1408044e0, dynamic +0x4c8, process-field identity, and clean Steam behavior remain unresolved.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = read_json(frontier_path)
q = next(item for item in frontier["items"] if item.get("id") == "Q-0079")
new_hypotheses = [
    {
        "id": "Q79-H66",
        "model": "Tag 0x2e is a deferred Actor/process numeric-state and presentation continuation.",
        "predicted_discriminant": "The builder and dispatcher return to FUN_14068b3a0; its clear-gate path reads/writes the process dword at *( *(process+0x10)+0x328 ) and may apply player image-space/sound effects. Dynamic +0x4c8 and FUN_1408044e0 descendants remain open.",
        "status": "supported",
        "evidence": ["EV-0545", "EV-0567", "EV-0568", "EV-0569", "EV-0570"],
    },
    {
        "id": "Q79-H67",
        "model": "At least one tag-0x2e parent path is hit-adjacent because FUN_140669f70 calls shared Health helper FUN_140668f50 before FUN_14068b3a0, and the helper is also called by mapped HitData handlers.",
        "predicted_discriminant": "Resolve the exact source/event type and remaining descendant calls. A mapped incoming-hit/AV11/AV12/UseSkill route supports H67; only hard-landing/drowning or other process-state sources with no skill sink narrows it to H66 for those paths.",
        "status": "proposed",
        "evidence": ["EV-0570", "EV-0571", "EV-0294", "EV-0260"],
    },
]
by_id = {h["id"]: h for h in q.get("hypotheses", [])}
for h in new_hypotheses:
    current = by_id.get(h["id"])
    if current is None:
        q["hypotheses"].append(h)
    elif current != h:
        raise SystemExit(f"frontier hypothesis conflict: {h['id']}")
q["evidence"] = list(dict.fromkeys([*q.get("evidence", []), *[f"EV-{i:04d}" for i in range(567, 572)]]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L379", "CL-L380", "CL-L381", "CL-L382"]))
assessment = (
    "Caller 37/62 adds a tag-0x2e deferred Actor/process update. Its direct body writes an unnamed process dword and "
    "may apply player presentation effects; some parent contexts are adjacent to the shared Health helper "
    "FUN_140668f50, which is also used by mapped HitData handlers. This does not map a causal tag-0x2e-to-armor-skill "
    "edge. H66 is supported for the bounded continuation; H67 remains proposed pending the source type and "
    "FUN_1408044e0 descendants."
)
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
write_json(frontier_path, frontier)
print("registered EV-0567–EV-0571; added CL-L379–CL-L382, M-0134, and Q79-H66/H67")
