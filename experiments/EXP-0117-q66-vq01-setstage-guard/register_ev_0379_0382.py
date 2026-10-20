#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
TX = ROOT / ".local/alignment/transactions/TX-20261018-0002"
BIN_HASH = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"
SOURCE_HASH = "1bda804009a21228acf6b30aa6aa7a692b247ff8a0313fe9aa69b3617ed4a6c4"

CAPTURES = [
    ".local/alignment/xedit-bridge/20261018T125120.279526Z/stdout.raw",
    ".local/alignment/xedit-bridge/20261018T125527.760139Z/stdout.raw",
    ".local/xedit-authoritative-copy/out/xedit/20261018T125608.468789Z/native-records.tsv",
    ".local/xedit-authoritative-copy/out/xedit/20261018T125608.468789Z/native-result.json",
    ".local/ghidra/gog-query-20261018T125229Z.stdout.raw",
    ".local/ghidra/gog-query-20261018T130029Z.stdout.raw",
    ".local/ghidra/gog-query-20261018T130243Z.stdout.raw",
    ".local/ghidra/gog-query-20261018T125229Z.meta.json",
    ".local/ghidra/gog-query-20261018T130029Z.meta.json",
    ".local/ghidra/gog-query-20261018T130243Z.meta.json",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, data: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data.rstrip() + "\n", encoding="utf-8")


def append_once(path: Path, marker: str, data: str) -> None:
    old = path.read_text(encoding="utf-8")
    if marker in old:
        raise SystemExit("duplicate append: " + marker)
    write(path, old.rstrip() + "\n\n" + data.strip())


def main() -> None:
    evidence_path = ROOT / "research/EVIDENCE.json"
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    existing = {item["id"] for item in evidence["items"]}
    wanted = {"EV-0379", "EV-0380", "EV-0381", "EV-0382"}
    if existing & wanted:
        raise SystemExit("Q66 evidence already registered: " + ", ".join(sorted(existing & wanted)))
    for rel in CAPTURES:
        if not (ROOT / rel).is_file():
            raise SystemExit("missing preserved capture: " + rel)
    TX.mkdir(parents=True, exist_ok=True)

    results = """# Results — Q-0066 VQ01 SetStage startup guard

## Rival models and discriminant

- **H1:** Fort Dawnguard's mapped dialogue callback calls `DLC1VQ01.SetStage(10)`. In the GOG AE 1.6.1179.0 callback, an accepted `Quest.SetStage` request can call `TESQuest::EnsureQuestStarted` in start-now mode before the requested stage is written. VQ01's source fields and constructor state satisfy the initial event/ready-state predicates, with no level comparison in the bounded callback.
- **H2:** a startup eligibility or required-alias/reference preflight can still reject the stopped quest, leaving stage 10 un-applied or a start incomplete.
- The static discriminator is the exact QUST source data against the callback and helper predicates. A natural, clean level-one run must separately show the quest running state, stage, required aliases, and useful crypt access; a journal/map marker alone is insufficient.

## Source-linked findings

The five-official-master source export identifies Dawnguard.esm `DLC1VQ01` as form `0200352A`, Run Once, and not Start Game Enabled [EV-0326, EV-0379]. Its direct TES4 parser capture has no `ENAM` subrecord. The VQ01 export contains 14 aliases: six required, including DimhollowCrypt, Tolan, Adalvald, Serana, Book, and DimhollowEntrance; the alias export has no alias-node CTDA/function rows. Serana is an external alias to the start-enabled `DLC1NPCMentalModel` alias `ResponsiveNPC`, whose source fill is the forced `DLC1SeranaRef` in DimhollowCrypt02 [EV-0379]. These are source fill definitions, not proof of live alias initialization.

The mapped Fort Dawnguard route in the fixed official-master source scope runs through the VQ00 Durak dialogue helper and requests `DLC1VQ01.SetStage(10)`; the separate level-10 Story Manager helper is not on that mapped callback chain [EV-0326]. The GOG callback candidate `FUN_14034de90` checks `(quest + 0xDC bit 0) OR (quest + 0xE0 == -1)`, and its accepted path calls `FUN_1403c9d30` (`TESQuest::EnsureQuestStarted`) with mode 1 before stage application [EV-0313, EV-0380].

The GOG `TESQuest` constructor candidate initializes `+0xE0` to `0xFFFFFFFF`, sets bit `0x100` in `+0xDC`, and zeros `+0x22A`. With the VQ01 record's absent `ENAM`, these constructor defaults satisfy the observed initial SetStage predicate and the helper's inner `(bit 0x100 clear) OR (+0x22A == 0)` check in this GOG model [EV-0381]. The GOG helper then performs further state/readiness and alias/reference work before `BeginStartUpQuest`; it is not an unconditional start [EV-0380, EV-0382].

The alias/reference processor `FUN_1403d0c10` includes data-driven fill/condition paths, five unresolved indirect call sites in the bounded query, and paths that return zero. Its caller treats a failed nonoptional entry as a failed preflight [EV-0382]. No direct `GetLevel` comparison appears in the bounded SetStage callback/helper code examined, but that does not prove all source-driven or deferred startup behavior is level-independent.

## Decision and limits

H1 is supported as a **conditional GOG/source candidate**: the callback can request startup before stage 10, and the exact VQ01 source/constructor inputs pass the initial callback predicates. H2 remains live because required-alias/reference preflight and actual startup completion are dynamic. The evidence does not establish a Steam AE 1.6.1170.0 result, a level-one reproduction, quest-running state, alias fill, or functional crypt access. Stage 10's objective/map-marker change is not itself proof that the content can be entered or progressed [EV-0326].

No causal edge to OBJ-2 is supported. The next discriminating test is a clean level-one Steam run using only the natural Fort dialogue sequence, with a no-dialogue control and read-only capture of player level, VQ01 running/stage state, each required alias, and actual Dimhollow entrance/progression. No console stage/start command, script injection, modified plugin, or altered save may be part of the candidate run; current live prerequisites remain unavailable [EV-0260].
"""
    hypothesis = """# Competing models

- **Q66-H1:** the mapped Fort dialogue callback's `Quest.SetStage(10)` conditionally starts stopped VQ01 before applying stage 10. Exact VQ01 source fields and the GOG constructor defaults satisfy the initial guards; a level-one natural path remains a candidate.
- **Q66-H2:** a remaining EnsureQuestStarted state check or required alias/reference preflight rejects VQ01 or prevents useful startup.

The static SetStage entry and constructor checks discriminate the initial guard. Only the exact runtime state transition plus required-alias/access observation can discriminate the full models for Steam AE.
"""
    protocol = """# Protocol

1. Reuse and read EV-0313/EV-0314 and EV-0326; preserve the fixed five-official-master and GOG build scopes.
2. Compare the exact Dawnguard.esm QUST/alias source fields with the existing identity-attested GOG SetStage callback, `EnsureQuestStarted`, constructor, and alias/reference helper paths.
3. Keep source fill data separate from proof that runtime aliases fill, and keep stage 10/journal/map state separate from functional crypt progression.
4. Record GOG predicates as a static candidate only. The independent Steam discriminator is a natural level-one Durak dialogue run, no-trigger control, live required-alias/quest-stage inspection, actual entrance/progression, and level-preservation check.
5. Add no causal edge to armor XP without an exact shared engine call/state or controlled dependency.
"""
    expected = """# Expected discriminants

- **H1 supported at the callback boundary:** exact VQ01 ENAM/flags and GOG constructor values satisfy the initial guards; the mapped dialogue path reaches SetStage(10), which calls startup before applying the stage.
- **H2 supported at a guard:** exact record inputs fail a preflight, or a natural level-one run leaves VQ01 stopped/required aliases unfilled after the mapped dialogue.
- **Both remain open:** dynamic required aliases or deferred startup cannot be resolved from bounded static evidence, or runtime prerequisites are absent.

A Start Game Enabled flag alone is not the discriminant: the traced native callback can invoke a separate start path. A stage value, journal entry, objective, or map marker alone is not a successful-access result.
"""
    implications = """# Implications

VQ01's Start Game Enabled=0 field does not by itself rule out the Fort dialogue route: the GOG SetStage callback has a conditional startup path that precedes stage application. Exact constructor state passes the initial guard for the no-ENAM VQ01 source record. Required alias/reference preflight remains data-driven and can reject startup, so this is not yet a working level-one bypass. Keep Dawnguard/Steam runtime proof open and continue an independent OBJ-1 case. No OBJ-2 edge is added.
"""
    docs = {
        "README.md": "# EXP-0117 — Q-0066 VQ01 SetStage startup guard\n\nTest whether the Fort Dawnguard `DLC1VQ01.SetStage(10)` callback can start the stopped quest before applying the stage. Compare exact source record inputs and the build-attested GOG native guards; preserve required-alias and Steam runtime uncertainty.\n",
        "hypothesis.md": hypothesis,
        "protocol.md": protocol,
        "expected-discriminants.md": expected,
        "results.md": results,
        "implications.md": implications,
    }
    for name, content in docs.items():
        write(EXP / name, content)

    note = TX / "EV-0379-0382-note.md"
    write(note, """# EV-0379–EV-0382 — Q-0066 VQ01 SetStage and startup preflight

## Source scope and build identity

The record evidence is limited to the fixed five official masters and Dawnguard.esm SHA-256 {source_hash}; it is not an active-profile winner. The native query for the external alias provider used the same official-master scope. GOG native traces are tied to AE 1.6.1179.0 SkyrimSE.exe SHA-256 {binary_hash}; the installed Steam AE 1.6.1170.0 identity is separately recorded as EV-0109. Do not transfer a GOG RVA or runtime conclusion to Steam.

## EV-0379 — direct QUST and alias source evidence

Direct read-only TES4 parsing of `DLC1VQ01` form `0200352A` found no `ENAM` subrecord. Native xEdit five-master export (EV-0326) identifies Start Game Enabled=0 and Run Once=1. A parser of that export reports 14 aliases and no alias-node CTDA/function rows. Six aliases are required: DimhollowCrypt (location), Tolan and Adalvald (unique actors), Serana (external alias), Book (forced REFR 0200D072), and DimhollowEntrance (forced REFR 02002F71). The provider `DLC1NPCMentalModel` (QUST 02002B6E) is Start Game Enabled=1 and defines `ResponsiveNPC` as forced `DLC1SeranaRef` (ACHR 02002B74) in DimhollowCrypt02. Source fill definitions do not prove runtime fill or that EnsureQuestStarted accepts all required refs.

## EV-0380 — EnsureQuestStarted call boundary

Existing GOG project read-only query at RVA 0x3C9D30 (function `FUN_1403c9d30`) succeeded against ProductVersion 1.6.1179.0 and the hash above. Five direct outgoing call edges and no enumerated indirect sites were reported; incoming caller evidence identifies the SetStage candidate. The helper calls `FUN_1403ccd90` for state/ref/alias readiness and calls `FUN_140532e60` (BeginStartUpQuest) only when that preflight accepts. Existing EV-0313 maps the callback argument as start-now mode 1. This is static GOG evidence.

## EV-0381 — GOG TESQuest constructor inputs

Existing GOG project read-only query at RVA 0x3C6FF0 (function `FUN_1403c6ff0`) succeeded. The bounded constructor writes `+0xE0 = 0xFFFFFFFF`, ORs `0x0100` into `+0xDC`, zeros `+0x228`, nulls `+0x240`, and zeros `+0x22A`. Given the VQ01 record's absent ENAM, the observed constructor values satisfy the initial SetStage alternative `( +0xDC bit 0 set ) OR ( +0xE0 == -1 )`. The helper's observed inner check `( +0xDC bit 0x100 clear ) OR ( +0x22A == 0 )` also accepts this constructor state. This is a GOG structure interpretation, not Steam object telemetry.

## EV-0382 — alias/reference preflight boundary

Existing GOG project read-only query at RVA 0x3D0C10 succeeded and covered 33 direct call edges plus five unresolved indirect call sites in the bounded helper. `FUN_1403ccd90` invokes `FUN_1403d0c10` while processing quest reference/alias entries. The helper's type-specific paths can return zero for missing references or failed condition/fill work; the caller marks a failed nonoptional entry as preflight failure. The source export has six required aliases and no alias-node conditions, but external aliases, forced refs, dynamic runtime presence, provider state, and unresolved indirect calls remain. No direct GetLevel check appears in this bounded body; data-driven condition execution and deferred startup are not ruled out.

## Result, uncertainty and next test

The mapped Fort dialogue route reaches `DLC1VQ01.SetStage(10)` and is outside the separate level-10 helper chain in the five-master source scope [EV-0326]. GOG SetStage can call startup before stage application when its predicates accept [EV-0313, EV-0380]. The exact VQ01 source and constructor inputs satisfy the initial guards [EV-0379, EV-0381]. Thus the callback is a conditional level-one candidate, not proof that required aliases fill or that the quest starts and provides functional crypt access. H2 remains possible at the data-driven preflight [EV-0382]. No clean Steam level-one run is presently available [EV-0260].

The next discriminator requires a clean level-one Steam save and complete selected order, a natural Durak dialogue path/no-dialogue control, and read-only capture of level, VQ01 running/stage state, all six required aliases, and actual entrance/progression. No diagnostic state forcing may enter the candidate run.
""".format(source_hash=SOURCE_HASH, binary_hash=BIN_HASH))

    capture_hashes = {rel: sha(ROOT / rel) for rel in CAPTURES}
    source_manifest = {
        "transaction_id": "TX-20261018-0002",
        "evidence_ids": ["EV-0379", "EV-0380", "EV-0381", "EV-0382"],
        "analysis_binary_product_version": "1.6.1179.0",
        "analysis_binary_sha256": BIN_HASH,
        "dawnguard_esm_sha256": SOURCE_HASH,
        "record_scope": "fixed five official masters; not a profile-specific winner",
        "capture_sha256": capture_hashes,
    }
    manifest_path = TX / "EV-0379-0382-capture-manifest.json"
    write(manifest_path, json.dumps(source_manifest, indent=2, ensure_ascii=False))
    doc_hashes = {f"experiments/EXP-0117-q66-vq01-setstage-guard/{n}": sha(EXP / n) for n in docs}
    doc_hashes["experiments/EXP-0117-q66-vq01-setstage-guard/register_ev_0379_0382.py"] = sha(Path(__file__).resolve())
    doc_hashes[f"{note.relative_to(ROOT).as_posix()}"] = sha(note)
    doc_hashes[f"{manifest_path.relative_to(ROOT).as_posix()}"] = sha(manifest_path)
    doc_hashes.update(capture_hashes)

    metadata = [
        ("EV-0379", "record", "Direct read-only TES4 parser capture of Dawnguard.esm DLC1VQ01 plus native xEdit five-official-master exports for VQ01 and DLC1NPCMentalModel; parser-generated alias summary.", ".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-note.md", "Fixed five-official-master Dawnguard.esm source scope; Dawnguard.esm SHA-256 " + SOURCE_HASH + "; not a profile winner or runtime result.", ["strict-dispatcher tools/xedit_bridge.py file-records", "native xEdit five-official-master query (read-only)", "EXP-0117 source-export parser"], "Exact VQ01 form 0200352A has no ENAM in the direct parser capture; xEdit source marks it not Start Game Enabled and Run Once. Six of 14 aliases are required, with no alias-node CTDA/function rows. Its external Serana alias points to the start-enabled provider quest's forced ResponsiveNPC reference. Alias source definitions do not establish runtime fill.", ["EV-0326"]),
        ("EV-0380", "native", "Existing GOG project read-only call-edge query of TESQuest::EnsureQuestStarted candidate FUN_1403c9d30 and bounded direct callers/callees.", ".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-note.md", "Offline GOG AE 1.6.1179.0 SHA-256 " + BIN_HASH + "; no RVA or behavior transfer to Steam AE 1.6.1170.0.", ["tools/ghidra_probe.py through strict dispatcher against configured existing GOG project, no analysis/import"], "The helper performs quest state/reference/alias preflight and calls BeginStartUpQuest only on acceptance. The SetStage callback is an incoming caller and invokes start-now mode per EV-0313.", ["EV-0313", "EV-0381", "EV-0382"]),
        ("EV-0381", "native", "Existing GOG project read-only constructor query of TESQuest constructor candidate FUN_1403c6ff0.", ".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-note.md", "Offline GOG AE 1.6.1179.0 SHA-256 " + BIN_HASH + "; structure interpretation remains GOG-build scoped.", ["tools/ghidra_probe.py through strict dispatcher against configured existing GOG project, no analysis/import"], "The bounded constructor initializes +0xE0 to -1, sets +0xDC bit 0x100, and zeros +0x22A. Together with VQ01's absent ENAM, these inputs pass the observed initial SetStage and inner EnsureQuestStarted predicates; later eligibility remains unresolved.", ["EV-0313", "EV-0314", "EV-0379", "EV-0380"]),
        ("EV-0382", "native", "Existing GOG project read-only query of quest alias/reference preflight helper FUN_1403d0c10 and caller FUN_1403ccd90.", ".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-note.md", "Offline GOG AE 1.6.1179.0 SHA-256 " + BIN_HASH + "; bounded helper query, not runtime alias telemetry.", ["tools/ghidra_probe.py through strict dispatcher against configured existing GOG project, no analysis/import"], "Data-driven alias/reference processing can reject missing or failed required entries; five indirect sites and runtime fill remain unresolved. The bounded code has no direct GetLevel comparison, which does not rule out data-driven/deferred behavior.", ["EV-0313", "EV-0326", "EV-0379", "EV-0380"]),
    ]
    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for eid, kind, source, artifact, runtime, tools, result, related in metadata:
        evidence["items"].append({
            "id": eid, "kind": kind, "source": source, "artifact": "private-local:" + artifact,
            "sha256": sha(note), "captured_utc": captured, "edition": "AE",
            "runtime": runtime, "modified_state": False, "lane": "mechanism_inference",
            "tools": tools,
            "coverage": "See the evidence-specific section in EV-0379-0382-note.md and the private capture manifest; raw outputs are hashed and remain under ignored .local/.",
            "result": result, "related_evidence": related, "local_hashes": doc_hashes,
        })
    write(evidence_path, json.dumps(evidence, indent=2, ensure_ascii=False))

    append_once(ROOT / "research/CLAIMS.md", "| CL-L219 |", "| CL-L219 | In the mapped five-master Fort Dawnguard route, the VQ00 dialogue callback requests DLC1VQ01.SetStage(10); the GOG AE 1.6.1179.0 Quest.SetStage candidate can call EnsureQuestStarted in start-now mode before applying the stage, and VQ01's no-ENAM source plus constructor defaults satisfy the observed initial guard. This is a conditional static candidate, not a demonstrated level-one or Steam start. | supported as a bounded GOG/source candidate | [EV-0326], [EV-0379], [EV-0380], [EV-0381] | Alias/reference preflight, completed startup, Steam AE 1.6.1170.0 behavior, actual crypt access, and a clean level-one reproduction remain unobserved. |")
    append_once(ROOT / "research/CLAIMS.md", "| CL-L220 |", "| CL-L220 | VQ01 has six required source aliases and an external Serana alias whose provider defines a forced reference, while the GOG startup helper processes quest reference/alias entries through a data-driven preflight that can reject missing or failed required entries. | supported for source definitions and bounded GOG helper | [EV-0379], [EV-0380], [EV-0382] | Source fill records do not prove runtime alias fill; five indirect sites and dynamic/ref state remain unresolved, and no Steam runtime result follows. |")

    mechanisms = ROOT / "research/MECHANISMS.md"
    old = mechanisms.read_text(encoding="utf-8")
    wrong = "## M-0077 — Q-0065 class-family comparison boundary"
    right = "## M-0091 — Q-0065 class-family comparison boundary"
    if old.count(wrong) != 1:
        raise SystemExit("expected one Q65 duplicate mechanism heading")
    old = old.replace(wrong, right).replace("Claim CL-L218 -> M-0077; Q-0065.", "Claim CL-L218 -> M-0091; Q-0065.")
    write(mechanisms, old)

    append_once(ROOT / "research/MECHANISMS.md", "## M-0090 — VQ01 conditional SetStage startup candidate (Q-0066)", """## M-0090 — VQ01 conditional SetStage startup candidate (Q-0066)

The fixed five-master Fort Dawnguard route requests `DLC1VQ01.SetStage(10)` outside the separate level-10 Story Manager helper [EV-0326]. In the identity-checked GOG AE 1.6.1179.0 trace, the registered SetStage candidate can call `TESQuest::EnsureQuestStarted` in start-now mode before stage application [EV-0313], [EV-0380]. VQ01 has no serialized ENAM in the direct parser capture, while the GOG constructor defaults set +0xE0 to -1 and +0xDC bit 0x100; those values pass the observed initial SetStage and helper predicates [EV-0379], [EV-0381]. The helper still runs dynamic reference/alias preflight and may reject missing or failed required entries [EV-0382]. Thus the route is a conditional static candidate, not proof of Steam startup, alias fill, level-one reproduction, or usable Dimhollow access. No causal edge to armor XP is identified. Claims CL-L219/CL-L220 -> M-0090; Q-0066.""")

    append_once(ROOT / "research/CONTRADICTIONS.md", "## C-OBJ1-Q66-SETSTAGE-START", """## C-OBJ1-Q66-SETSTAGE-START — VQ01 Fort SetStage startup

- **Model A:** the mapped Fort dialogue's SetStage(10) request conditionally starts stopped VQ01 before setting the stage.
- **Model B:** an event/state/readiness or required alias/reference preflight rejects the start or leaves it incomplete.
- **Evidence:** the fixed five-master route reaches VQ01.SetStage(10) outside the separate level-10 helper [EV-0326]; the GOG callback calls EnsureQuestStarted before stage application [EV-0313, EV-0380]; VQ01's source/constructor inputs satisfy the initial observed predicates [EV-0379, EV-0381]; the dynamic data-driven alias/reference preflight can fail required entries [EV-0382].
- **Assessment:** Model A is supported at the bounded callback/initial-guard level. Model B remains possible at helper preflight and runtime completion. Neither establishes a Steam AE level-one start or functional access.
- **Discriminant:** clean level-one Steam test with no-trigger control; read-only verification of quest running state, stage, all required aliases, and actual Dimhollow access while preserving numeric level 1.
""")

    append_once(ROOT / "research/KNOWLEDGE_GRAPH.md", "### Q-0066 VQ01 conditional startup (EV-0379–EV-0382)", """### Q-0066 VQ01 conditional startup (EV-0379–EV-0382)

Source route: Fort Dawnguard VQ00 dialogue helper -> VQ01.SetStage(10) [EV-0326]. GOG static route: SetStage callback -> EnsureQuestStarted(start-now) -> state/ref/alias preflight -> BeginStartUpQuest only when accepted -> requested stage processing [EV-0313, EV-0380, EV-0382]. VQ01's no-ENAM record and constructor defaults pass the observed initial guard [EV-0379, EV-0381]. Keep the preflight-to-successful-start and startup-to-functional-access edges unresolved; no level-one Steam runtime capture exists. No causal edge to OBJ-2 is supported [CL-L219, CL-L220].
""")
    append_once(ROOT / "experiments/README.md", "EXP-0117 / EV-0379", "EXP-0117 / EV-0379–EV-0382 traces VQ01's Fort SetStage request through the GOG startup and required-alias preflight guards. Static conditional candidate; runtime and functional access remain open.")

    frontier_path = ROOT / "research/FRONTIER.json"
    frontier = json.loads(frontier_path.read_text(encoding="utf-8"))
    q66 = next(item for item in frontier["items"] if item["id"] == "Q-0066")
    if q66.get("status") != "in_progress":
        raise SystemExit("Q-0066 is not in progress")
    q66["hypotheses"][0]["status"] = "supported"
    q66["hypotheses"][0]["evidence"] = ["EV-0326", "EV-0379", "EV-0380", "EV-0381"]
    q66["hypotheses"][1]["status"] = "proposed"
    q66["hypotheses"][1]["evidence"] = ["EV-0379", "EV-0380", "EV-0382", "EV-0260"]
    q66["evidence"] = list(dict.fromkeys(q66.get("evidence", []) + ["EV-0379", "EV-0380", "EV-0381", "EV-0382"]))
    q66["linked_claims"] = list(dict.fromkeys(q66.get("linked_claims", []) + ["CL-L219", "CL-L220"]))
    q66["next_action"] = "Record Q-0066 as blocked_environment for the exact Steam clean level-one running-state/alias/access discriminator; preserve the conditional GOG source candidate and select independent Q-0067 DA05 gate-layer census."
    q66["successors"] = list(dict.fromkeys(q66.get("successors", []) + ["Q-0067"]))
    q66["cross_source_assessment"] = "The bounded Dawnguard start candidate has no supported shared call or state edge to OBJ-2 armor-skill progress; retain separate P0 branches."
    q67 = {
        "id": "Q-0067", "objective": "OBJ-1", "kind": "mechanism", "status": "open",
        "question": "For DA05 A Night to Remember, where is the actual above-level-one initiation gate evaluated: Sam Guevenne's placement/story event, the quest start predicate, the dialogue conditions, or more than one layer? Does any source-supported player-accessible tavern interaction remain available below the ordinary gate?",
        "hypotheses": [
            {"id": "Q67-H1", "model": "The level gate is limited to the ordinary Sam Guevenne story/placement event; a separately available actor/dialogue path can initiate DA05 below the gate.", "predicted_discriminant": "Official records show a level predicate only on the story/placement event, while the quest/dialogue start path accepts a lower-level player and has a source-backed player-accessible actor route.", "status": "proposed", "evidence": []},
            {"id": "Q67-H2", "model": "DA05's own start or required dialogue path also checks the above-one level condition, so tavern presence alone cannot start the quest below it.", "predicted_discriminant": "The exact QUST, DIAL/INFO, VMAD, or native start predicates contain a necessary level check on the player-usable route.", "status": "proposed", "evidence": []},
            {"id": "Q67-H3", "model": "The assumed level requirement is not enforced by the source records on the actual initiation route; it describes ordinary discovery/spawn behavior rather than a hard quest gate.", "predicted_discriminant": "Source-backed quest and dialogue startup checks have no necessary level predicate, and the purported threshold appears only in external guidance or unrelated encounter selection.", "status": "proposed", "evidence": []},
        ],
        "methods": [
            "Ground the DA05 level premise against local UESP and direct official records; preserve exact edition/content scope.",
            "Inspect DA05 QUST start flags, Story Manager event/helper records, Sam Guevenne placement, linked dialogue and VMAD/PEX callbacks using only tested read-only routes.",
            "Trace every path from actor availability to quest start and distinguish a story event from an independently callable player dialogue route.",
            "Keep a level-one natural tavern observation and no-contact control separate from static candidate evidence; do not use console, injected scripts or altered records.",
        ],
        "blocked_by": [], "evidence": [], "priority": 0.99, "information_gain": 0.96,
        "next_action": "Verify whether local UESP has an attributed DA05 level threshold, then identify exact Skyrim.esm QUST/CLOC/DIAL records and their tested read-only export route before evaluating any bypass.",
        "linked_claims": [], "successors": [], "attempts": [],
        "cross_source_assessment": "Keep DA05 quest initiation independent from the Dawnguard VQ01 candidate and armor/HitData mechanisms unless an exact shared call or state is identified.",
    }
    if any(item["id"] == "Q-0067" for item in frontier["items"]):
        raise SystemExit("Q-0067 already exists")
    frontier["items"].append(q67)
    write(frontier_path, json.dumps(frontier, indent=2, ensure_ascii=False))

    local = {
        f"experiments/EXP-0117-q66-vq01-setstage-guard/{name}": sha(EXP / name)
        for name in [*docs.keys(), "register_ev_0379_0382.py", "inspect_vq01_record.py", "inspect_vq01_aliases.py", "inspect_npc_mental_model.py", "q66-vq01-alias-summary.json"]
    }
    local[".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-note.md"] = sha(note)
    local[".local/alignment/transactions/TX-20261018-0002/EV-0379-0382-capture-manifest.json"] = sha(manifest_path)
    local.update(capture_hashes)
    updated = json.loads(evidence_path.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in updated["items"]}
    for eid in wanted:
        by_id[eid]["local_hashes"] = local
    write(evidence_path, json.dumps(updated, indent=2, ensure_ascii=False))
    print("registered EV-0379–EV-0382, CL-L219/220, M-0090/M-0091; opened Q-0067")


if __name__ == "__main__":
    main()
