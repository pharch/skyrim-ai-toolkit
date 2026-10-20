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
        "id": "EV-0562", "stem": "gog-query-20261019T162340Z", "rva": "0x658550",
        "source": "Identity-checked read-only GOG query of exact worker caller 36/62 FUN_140658550",
        "command": "tools/ghidra_probe.py --rva 0x658550 --list-call-edges --timeout 600",
        "related": ["EV-0559", "EV-0560", "EV-0561", "EV-0545", "EV-0260"],
        "coverage": (
            "Complete direct-call census of one exact remaining worker caller. FUN_140658550 has one direct edge to "
            "FUN_14065b800, zero indirect sites, and three direct producers: FUN_14051cdd0 at 0x14051cffc, "
            "FUN_14051d020 at 0x14051d1fb, and FUN_1407ed990 at 0x1407edd30. The builder writes tag 0x2d, "
            "a scalar, and three float coordinates."
        ),
        "result": (
            "Caller 36/62 is the tag-0x2d worker builder. Its first two producers are the caller35 water/effect "
            "route; the third producer is a distinct record-processing function analyzed separately in EV-0563. "
            "Dispatcher case 0x2d targets FUN_140525820 [EV-0545], whose bounded coordinate-buffer effects are "
            "in EV-0561. This caller alone does not establish water, hit, ActorValue, protection, armor-skill, or XP semantics."
        ),
    },
    {
        "id": "EV-0563", "stem": "gog-query-20261019T162445Z", "rva": "0x7ed990",
        "source": "Identity-checked read-only GOG direct-call analysis of the third tag-0x2d producer FUN_1407ed990",
        "command": "tools/ghidra_probe.py --rva 0x7ed990 --list-call-edges --follow-direct-calls 8 --timeout 600",
        "related": ["EV-0562", "EV-0559", "EV-0561", "EV-0545", "EV-0260"],
        "coverage": (
            "FUN_1407ed990 has 22 direct calls, four indirect call sites, and five direct callers. In the branch "
            "where param_1+0x1d4 bit 12 is clear, it copies (param_5+0x2c)&0x7f into a 0x50-byte record at +0x34, "
            "copies coordinate inputs, and checks for code 0x0b. That branch selects direct FUN_140525820 when "
            "FUN_1406d4110 is clear or queues FUN_140658550 when the gate is set. The input object's runtime type "
            "and the meaning of code 0x0b are unresolved."
        ),
        "result": (
            "A third, non-water-producer-specific source selects the same tag-0x2d coordinate route for masked "
            "input code 0x0b. This establishes a shared spatial event path from a second producer family, not the "
            "meaning of that code. The complete direct-call list contains no mapped HitData, ActorValue, protection, "
            "or armor-skill target; four indirect sites and deeper consumers remain unresolved."
        ),
    },
    {
        "id": "EV-0564", "stem": "gog-query-20261019T162628Z", "rva": "0x7ed850",
        "source": "Identity-checked read-only GOG query of the shared record eligibility predicate FUN_1407ed850",
        "command": "tools/ghidra_probe.py --rva 0x7ed850 --list-call-edges --timeout 600",
        "related": ["EV-0563", "EV-0260"],
        "coverage": (
            "Complete direct-call census and decompilation of FUN_1407ed850; six direct callers include "
            "FUN_1407e25b0 and the other record-processing wrappers. The body reads the same +0x2c masked code "
            "and checks additional record and receiver fields; runtime type identity remains unknown."
        ),
        "result": (
            "The +0x2c masked code participates in shared eligibility logic and cannot be named as a HitData flag "
            "from this query. The predicate contains no direct mapped HitData, ActorValue, or armor-skill sink."
        ),
    },
    {
        "id": "EV-0565", "stem": "gog-query-20261019T162827Z", "rva": "0x7e25b0",
        "source": "Identity-checked read-only GOG query of FUN_1407e25b0 and its direct producer context",
        "command": "tools/ghidra_probe.py --rva 0x7e25b0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
        "related": ["EV-0563", "EV-0564", "EV-0260"],
        "coverage": (
            "Complete direct-call census of FUN_1407e25b0 and its analyzed incoming direct-call set. It has one "
            "incoming direct caller, FUN_1407cb9d0 at 0x1407cba20, and gates its call to FUN_1407ed990 on "
            "object/state predicates plus the shared FUN_1407ed850 eligibility helper."
        ),
        "result": (
            "The third tag-0x2d producer is reached through a single observed direct wrapper, FUN_1407cb9d0. "
            "That wrapper identity does not establish an ordinary hit, collision, or water source."
        ),
    },
    {
        "id": "EV-0566", "stem": "gog-query-20261019T162938Z", "rva": "0x7cb9d0",
        "source": "Identity-checked read-only GOG direct-call census of the upstream wrapper FUN_1407cb9d0",
        "command": "tools/ghidra_probe.py --rva 0x7cb9d0 --list-call-edges --timeout 600",
        "related": ["EV-0565", "EV-0563", "EV-0291", "EV-0260"],
        "coverage": (
            "Complete direct-call edge scan of FUN_1407cb9d0: 17 direct calls, three indirect sites, and zero "
            "analyzed incoming direct callers. The body calls FUN_1407e25b0; the remaining indirect targets and "
            "runtime owner are unresolved. No direct edge to mapped FUN_1406b9df0, FUN_1406bb690, or FUN_1406bcaa0 appears."
        ),
        "result": (
            "The bounded upstream wrapper does not directly call the mapped HitData handler, tag-0x0b handler, or "
            "ProcessTrapHit entry. This is a direct-edge negative only; its three indirect sites and runtime "
            "registration remain open, and no ordinary-hit or armor-XP conclusion follows."
        ),
    },
]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def append_block(path: Path, marker: str, block: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        return
    path.write_text(old.rstrip() + "\n\n" + block.rstrip() + "\n", encoding="utf-8")


evidence_path = ROOT / "research/EVIDENCE.json"
evidence = load_json(evidence_path)
existing = {item["id"]: item for item in evidence["items"]}
for spec in CAPTURES:
    raw = GHIDRA / f"{spec['stem']}.stdout.raw"
    stderr = GHIDRA / f"{spec['stem']}.stderr.raw"
    meta_path = GHIDRA / f"{spec['stem']}.meta.json"
    meta = load_json(meta_path)
    if not meta.get("ok") or meta.get("requested_rva", "").lower() != spec["rva"].lower():
        raise SystemExit(f"capture identity/check failed for {spec['id']}: {meta_path}")
    if meta.get("analysis_binary_product_version") != "1.6.1179" or not meta.get("program_executable_path_matches_gog_binary"):
        raise SystemExit(f"GOG build identity failed for {spec['id']}: {meta_path}")
    raw_hash, stderr_hash, meta_hash = sha(raw), sha(stderr), sha(meta_path)
    if raw_hash != meta.get("stdout_sha256") or stderr_hash != meta.get("stderr_sha256"):
        raise SystemExit(f"raw artifact hash mismatch for {spec['id']}")
    item = {
        "kind": "native",
        "edition": "AE",
        "runtime": RUNTIME,
        "modified_state": False,
        "lane": "mechanism_inference",
        "id": spec["id"],
        "source": spec["source"],
        "artifact": f"private-local:.local/ghidra/{raw.name}",
        "sha256": raw_hash,
        "captured_utc": meta["captured_utc"],
        "tools": ["strict Python 3.12 dispatcher", spec["command"]],
        "coverage": spec["coverage"],
        "result": spec["result"],
        "local_hashes": {
            f".local/ghidra/{raw.name}": raw_hash,
            f".local/ghidra/{stderr.name}": stderr_hash,
            f".local/ghidra/{meta_path.name}": meta_hash,
        },
        "related_evidence": spec["related"],
    }
    if spec["id"] in existing:
        if existing[spec["id"]].get("sha256") != raw_hash:
            raise SystemExit(f"evidence ID collision for {spec['id']}")
    else:
        evidence["items"].append(item)
        existing[spec["id"]] = item
save_json(evidence_path, evidence)

claims = ROOT / "research/CLAIMS.md"
for line in [
    "| CL-L376 | In GOG AE 1.6.1179.0, exact worker caller 36/62 FUN_140658550 builds tag 0x2d with a scalar and three-coordinate payload; its three direct producers are FUN_14051cdd0, FUN_14051d020, and FUN_1407ed990. | supported for the exact builder and direct-producer census | [EV-0562], [EV-0563] | The third producer's event meaning and the coordinate-buffer consumers remain unresolved; no ordinary-hit, armor-protection, ActorValue, armor-skill, or XP result follows. |",
    "| CL-L377 | In GOG AE 1.6.1179.0, FUN_1407ed990 copies `(param_5+0x2c)&0x7f` into a record field and, when its enclosing state bit is clear and that value is 0x0b, selects direct FUN_140525820 or queued tag-0x2d builder FUN_140658550 according to FUN_1406d4110. | supported for captured static control/data flow | [EV-0563], [EV-0564] | The input object type and code 0x0b semantics are unknown; four indirect sites and downstream consumers remain unresolved. |",
    "| CL-L378 | FUN_1407e25b0 has one analyzed direct caller, FUN_1407cb9d0; the bounded upstream wrapper has 17 direct calls and three unresolved indirect sites, with no direct edge to the mapped HitData/tag-0x0b/ProcessTrapHit routines. | supported for the captured GOG direct-edge census | [EV-0565], [EV-0566], [EV-0291] | This bounded direct-edge negative does not resolve indirect dispatch, runtime registration, ordinary-hit coverage, effective protection, or armor XP. |",
]:
    append_block(claims, line.split(" | ")[0], line)

mechanism = ROOT / "research/MECHANISMS.md"
append_block(
    mechanism,
    "## M-0133 — Additional tag-0x2d source through masked record code (Q-0079)",
    """## M-0133 — Additional tag-0x2d source through masked record code (Q-0079)

The exact tag-0x2d worker builder FUN_140658550 has three direct producers: water/effect functions FUN_14051cdd0 and FUN_14051d020, plus FUN_1407ed990 [EV-0562]. In FUN_1407ed990's state-bit-clear branch, `(param_5+0x2c)&0x7f` is copied into a record field; code 0x0b selects the same direct FUN_140525820 target or queued FUN_140658550 builder according to the shared FUN_1406d4110 gate [EV-0563], [EV-0564]. FUN_1407e25b0 has one analyzed direct caller, FUN_1407cb9d0; that wrapper's complete direct-edge set has no call to the mapped HitData/tag-0x0b/ProcessTrapHit functions, while three indirect sites remain unresolved [EV-0565], [EV-0566].

This widens the source set of the bounded spatial coordinate path beyond the two captured water/effect producers. The code's semantic type, water relation, runtime owner, four indirect sites in FUN_1407ed990, and buffer consumers are unresolved. No causal edge to HitData, ActorValue, effective protection, AV11/AV12, armor skill/XP, or OBJ-1 is supported. Claims CL-L376–CL-L378.""",
)

results = ROOT / "experiments/EXP-0128-hit-worker-callers/results.md"
append_block(
    results,
    "## Caller 36/62 — tag-0x2d with a separate masked-code producer",
    """## Caller 36/62 — tag-0x2d with a separate masked-code producer

EV-0562 maps FUN_140658550: one outgoing edge to FUN_14065b800, zero indirect sites, and three direct producers. FUN_14051cdd0 and FUN_14051d020 are the caller35 water/effect producers; FUN_1407ed990 is a third source. The builder stores tag 0x2d, a scalar, and three float coordinates. Dispatcher case 0x2d returns to FUN_140525820 [EV-0545], whose distance-gated coordinate-buffer writes are bounded in EV-0561.

EV-0563 shows FUN_1407ed990 copying `(param_5+0x2c)&0x7f` into a pooled record and, when `param_1+0x1d4` bit 12 is clear, branching on value 0x0b. The clear thread gate calls FUN_140525820 directly; the set gate calls FUN_140658550. The source object and code meaning are not identified. EV-0564 confirms the shared eligibility predicate also reads the masked code but does not type it as HitData. FUN_1407e25b0 is reached from one analyzed direct caller, FUN_1407cb9d0 [EV-0565]. Its complete 17-edge direct-call census has three indirect sites but no direct call to FUN_1406b9df0, FUN_1406bb690, or FUN_1406bcaa0 [EV-0566].

This supports a second producer family for the same bounded spatial/coordinate event. It does not show that code 0x0b is a HitData flag, an ordinary incoming hit, or a water category. Competing Q79-H64/H65 remain proposed until the input object's type and producer are resolved. H63 remains supported only for the caller35 water/effect source; H1/H2/H3 and H62 do not change. No HitData/ActorValue/effective-protection/armor-skill edge or OBJ-1 edge is added. The inventory now covers 36/62 callers, with 26 remaining. Next inspect caller 37/62 FUN_1406585a0.

Raw .local/ghidra/gog-query-20261019T162340Z.stdout.raw SHA-256 c921059e7db16dbff5aa3d2609d9c0439074952d7c4337b3d34af3e3fa.
Raw .local/ghidra/gog-query-20261019T162445Z.stdout.raw SHA-256 3e3e3b48e90039c1f482e5f2e498ea1afc210498516b50f4ddd3672346ec2d0c.
Raw .local/ghidra/gog-query-20261019T162628Z.stdout.raw SHA-256 4789a20278fe2f44dee3e8a3c0ccb30f46631b2fcfd3f3b5c167dff891ba93ac.
Raw .local/ghidra/gog-query-20261019T162827Z.stdout.raw SHA-256 2140983ec9476bfe12528882ab8bc1a7b88bde4f481a5a375eb9a3917c649b86.
Raw .local/ghidra/gog-query-20261019T162938Z.stdout.raw SHA-256 e7652da40717f502286ff8a00eba3533768d2314189141da7fd9124640d7854d.""",
)

hypothesis = ROOT / "experiments/EXP-0128-hit-worker-callers/hypothesis.md"
append_block(
    hypothesis,
    "## Caller 36 competing source models",
    """## Caller 36 competing source models

- Q79-H64: The `0x0b` masked code supplied to FUN_1407ed990 is a hit/collision-related source category, and tag 0x2d is accompanying spatial feedback. Prediction: tracing the source object and its +0x2c writer reaches a mapped hit/collision structure or hit-event producer. This remains proposed; no skill award follows from the spatial event itself [EV-0562]–[EV-0566].
- Q79-H65: The same masked code is a non-hit event category sharing the coordinate-buffer callback; its proximity to water/effect work does not make it a combat event. Prediction: producer-backed source/type resolution remains outside the mapped HitData/tag-0x0b/ProcessTrapHit routes. This remains proposed because FUN_1407ed990 has four indirect sites and its source type is unknown [EV-0563]–[EV-0566].""",
)

expected = ROOT / "experiments/EXP-0128-hit-worker-callers/expected-discriminants.md"
append_block(
    expected,
    "EV-0562–EV-0566 discriminant",
    """EV-0562–EV-0566 discriminant: resolve the runtime type and producer of the object field `(param_5+0x2c)&0x7f` copied by FUN_1407ed990. A writer or caller that identifies a HitData/collision source supports Q79-H64 for a hit-adjacent spatial effect; a non-hit source supports Q79-H65. Neither outcome establishes armor skill XP. The upstream wrapper's three indirect targets, FUN_1407ed990's four indirect targets, the coordinate-buffer consumers, and clean Steam matched-hit/AVSK telemetry remain separate open checks.""",
)

implications = ROOT / "experiments/EXP-0128-hit-worker-callers/implications.md"
append_block(
    implications,
    "Caller 36 cross-system note",
    """Caller 36 cross-system note: the worker gate continues to serialize unrelated actor/update, registry, water/effect, and this masked-code spatial route. The shared worker and coordinate handler are engine scheduling/dataflow edges; no shared ActorValue, armor-protection, AVSK, quest-state, or Story Manager dependency has been mapped. Keep the water-specific interpretation scoped to the caller35 producer and keep OBJ-1 independent.""",
)

graph = ROOT / "research/KNOWLEDGE_GRAPH.md"
append_block(
    graph,
    "EV-0562–EV-0566 widen the tag-0x2d source set",
    """EV-0562–EV-0566 widen the tag-0x2d source set: FUN_1407ed990 copies a masked input code into its event record and, for code 0x0b on a gated branch, converges on FUN_140525820 directly or through worker tag 0x2d. FUN_1407cb9d0 is the only analyzed direct caller of FUN_1407e25b0; its direct-edge census does not reach mapped HitData/tag-0x0b/ProcessTrapHit routines. Add these producer and worker edges, but keep source-type semantics, indirect sites, coordinate-buffer consumers and runtime owner unresolved. No causal edge to protection, ActorValue, armor XP or OBJ-1 is supported.""",
)

frontier_path = ROOT / "research/FRONTIER.json"
frontier = load_json(frontier_path)
q = next(item for item in frontier["items"] if item.get("id") == "Q-0079")
new_hypotheses = [
    {
        "id": "Q79-H61",
        "model": "Tag 0x21 is a deferred re-entry into the same primary Actor base method through a generation-managed handle.",
        "predicted_discriminant": "The builder stores a generation handle for the source object; dispatcher case 0x21 resolves it and invokes Actor slot +0x6c8, which maps to the producer FUN_14067e960. Dynamic overrides and runtime gate state remain open.",
        "status": "supported",
        "evidence": ["EV-0545", "EV-0553", "EV-0554", "EV-0555", "EV-0557"],
    },
    {
        "id": "Q79-H62",
        "model": "The tag-0x21 scalar continuation reaches an ActorValue, effective-protection, or armor-skill sink.",
        "predicted_discriminant": "Resolve the nested Actor/process receiver at +0x190/vtable slot +0x8 and bounded descendants to a mapped ActorValue/HitData/UseSkill sink; otherwise preserve this as an open downstream possibility.",
        "status": "proposed",
        "evidence": ["EV-0553", "EV-0556", "EV-0558", "EV-0260"],
    },
    {
        "id": "Q79-H63",
        "model": "Caller 35's tag-0x2c and paired tag-0x2d route is spatial water/effect work.",
        "predicted_discriminant": "The exact handlers show water-splash resources and bounded coordinate-buffer updates. This model is scoped to the captured caller35 water/effect source; additional tag-0x2d sources may exist.",
        "status": "supported",
        "evidence": ["EV-0545", "EV-0559", "EV-0560", "EV-0561"],
    },
    {
        "id": "Q79-H64",
        "model": "The masked source code 0x0b in FUN_1407ed990 is a hit/collision-related category, with tag 0x2d acting as accompanying spatial feedback.",
        "predicted_discriminant": "A producer-backed source/type trace identifies the input object or +0x2c writer as a hit/collision record or a hit-event producer. This does not predict an armor-skill award from the spatial callback.",
        "status": "proposed",
        "evidence": ["EV-0562", "EV-0563", "EV-0564", "EV-0565", "EV-0566"],
    },
    {
        "id": "Q79-H65",
        "model": "The masked source code 0x0b is a non-hit event category sharing the coordinate-buffer callback; its proximity to the water/effect route does not make it a combat event.",
        "predicted_discriminant": "Resolve the source object/type outside mapped HitData/tag-0x0b/ProcessTrapHit paths. The unresolved indirect sites prevent this from becoming a global no-hit conclusion.",
        "status": "proposed",
        "evidence": ["EV-0563", "EV-0564", "EV-0565", "EV-0566"],
    },
]
by_hypothesis = {h["id"]: h for h in q.get("hypotheses", [])}
for item in new_hypotheses:
    current = by_hypothesis.get(item["id"])
    if current is None:
        q["hypotheses"].append(item)
    elif current != item:
        raise SystemExit(f"frontier hypothesis conflict: {item['id']}")
bad_ids = {f"EV-{i}" for i in range(562, 567)}
q["evidence"] = list(dict.fromkeys([*[x for x in q.get("evidence", []) if x not in bad_ids], *[f"EV-{i:04d}" for i in range(562, 567)]]))
q["linked_claims"] = list(dict.fromkeys([*q.get("linked_claims", []), "CL-L376", "CL-L377", "CL-L378"]))
new_method = "Trace the producer-backed source/type that supplies `(param_5+0x2c)&0x7f` to FUN_1407ed990; distinguish Q79-H64 from H65 without treating code 0x0b or tag 0x2d as HitData semantics."
if new_method not in q["methods"]:
    q["methods"].append(new_method)
assessment = (
    "Caller 36 adds a second producer family for the tag-0x2d coordinate path: FUN_1407ed990 selects it from "
    "masked code 0x0b, while the caller35 water/effect producers remain separately supported. The input type and "
    "water/hit relationship are unresolved under Q79-H64/H65. Direct edges do not reach mapped HitData/tag-0x0b/"
    "ProcessTrapHit functions; indirect sites, buffer consumers, clean Steam protection/AVSK evidence, and OBJ-1 "
    "level-one access remain open."
)
if assessment not in q.get("cross_source_assessment", ""):
    q["cross_source_assessment"] = q.get("cross_source_assessment", "").rstrip() + " " + assessment
save_json(frontier_path, frontier)

print("registered EV-0562–EV-0566; added CL-L376–CL-L378 and M-0133; synced Q79-H61–H65")
