#!/usr/bin/env python3
"""Register Q87's exact GOG ActorBaseData level-writer and caller-path captures."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

TX = "TX-20261020-0006"
GHIDRA = ROOT / ".local/ghidra"
RECOVERY = ROOT / "research/RECOVERY.json"
EVIDENCE = ROOT / "research/EVIDENCE.json"
SUMMARY = ROOT / ".local/alignment/transactions" / TX / "q87-level-writer-trace.json"
CAPTURES = {
    "exact_setter": ("20261020T040808Z", "0x1D7BA0"),
    "unclassified_player_increment": ("20261020T041000Z", "0x355210"),
    "threshold_writer": ("20261020T041105Z", "0x77D650"),
    "generic_actor_update_writer": ("20261020T041238Z", "0x77D580"),
    "pending_ui_path": ("20261020T041350Z", "0x9611E0"),
    "candidate_ui_table_rtti_probe": ("20261020T041516Z", None),
    "pending_progress_predicate": ("20261020T041628Z", "0x77D630"),
    "threshold_writer_loop": ("20261020T041731Z", "0x356A10"),
    "post_write_ui_event": ("20261020T041854Z", "0x9366D0"),
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> None:
    recovery = load(RECOVERY)
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != ("running", TX, "Q-0087"):
        raise SystemExit("Q87 is not the active transaction")
    manifest = {}
    for name, (stamp, expected_rva) in CAPTURES.items():
        stdout = GHIDRA / f"gog-query-{stamp}.stdout.raw"
        meta_path = GHIDRA / f"gog-query-{stamp}.meta.json"
        meta = load(meta_path)
        if (meta.get("ok") is not True or meta.get("read_only") is not True or
            meta.get("auto_analysis_disabled") is not True or
            meta.get("analysis_binary_product_version") != "1.6.1179" or
            meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f" or
            meta.get("stdout_sha256") != sha(stdout)):
            raise SystemExit(f"identity/read-only/raw hash check failed: {name}")
        if expected_rva and str(meta.get("requested_rva", "")).lower() != expected_rva.lower():
            raise SystemExit(f"requested RVA mismatch: {name}")
        text = stdout.read_text(encoding="utf-8", errors="replace")
        manifest[name] = {
            "metadata": f"private-local:{meta_path.relative_to(ROOT).as_posix()}",
            "metadata_sha256": sha(meta_path),
            "stdout": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
            "stdout_sha256": sha(stdout),
            "requested_rva": meta.get("requested_rva"),
            "query_mode": meta.get("query_mode"),
        }

    setter_text = (GHIDRA / "gog-query-20261020T040808Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
    writer_text = (GHIDRA / "gog-query-20261020T041105Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
    ui_text = (GHIDRA / "gog-query-20261020T041350Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
    predicate_text = (GHIDRA / "gog-query-20261020T041628Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
    post_text = (GHIDRA / "gog-query-20261020T041854Z.stdout.raw").read_text(encoding="utf-8", errors="replace")
    for marker in ("MOV word ptr [RCX + 0x10], DX", "ADD RCX, -0x30", "XREF_CALL_COUNT=6"):
        if marker not in setter_text:
            raise SystemExit(f"exact setter evidence is missing: {marker}")
    for marker in ('"UILevelUp"', "FUN_140668f30(DAT_143188918)", "FUN_1401d7ba0"):
        if marker not in writer_text:
            raise SystemExit(f"threshold writer evidence is missing: {marker}")
    for marker in ("FUN_14077d630", "FUN_14077d650", "FUN_1409366d0"):
        if marker not in ui_text:
            raise SystemExit(f"pending UI call-order evidence is missing: {marker}")
    if "pfVar1[1] < *pfVar1 || pfVar1[1] == *pfVar1" not in predicate_text:
        raise SystemExit("pending progress predicate is not captured")
    if "*puVar2 = 0x46" not in post_text or "FUN_1401af090" not in post_text:
        raise SystemExit("post-write UI event scope is not captured")

    captured = datetime.now(timezone.utc).isoformat(timespec="seconds")
    summary = {
        "captured_utc": captured,
        "transaction": TX,
        "build": {
            "product_version": "GOG SkyrimSE.exe 1.6.1179.0",
            "executable_sha256": "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
            "address_library_sha256": "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e",
            "steam_1_6_1170_rvas_used": False,
        },
        "captures": manifest,
        "field": "FUN_1401d7b20 loads the 16-bit value from TESActorBaseData+0x10; CommonLib ACTOR_BASE_DATA.level is +0x08 within actorData, whose containing TESActorBaseData member is +0x08, agreeing with +0x10.",
        "setter": "FUN_1401d7ba0 stores DX to [RCX+0x10], subtracts 0x30 to recover the enclosing actor base form, then calls its vtable slot +0x50 with selector 2. The exact setter has six direct caller functions in the analyzed GOG project.",
        "threshold_ui_path": "FUN_14077d630 returns true when its pointed-to float pair satisfies pfVar1[1] <= pfVar1[0]. FUN_14077d650 uses the same pair condition, emits the UILevelUp message, obtains current Player GetLevel+1, and calls FUN_1401d7ba0 with that new value. Direct callers include FUN_140356a10 and FUN_1409611e0. FUN_140356a10 loops while the predicate remains true, calls FUN_14077d650 then FUN_14077d700, and logs a Player Level advanced message; it has no analyzed direct callers and two data xrefs. FUN_1409611e0's bounded UI branch checks FUN_14077d630, calls FUN_14077d650, then calls FUN_1409366d0; that post-write helper sets thread-local value 0x46 around FUN_1401af090. The latter path therefore writes the level field before this post-write UI event dispatch.",
        "other_writers": "FUN_140355210 independently increments the Player's current GetLevel by one through FUN_1401d7ba0; it has no analyzed direct callers and three data xrefs whose registration/dispatch meaning is unresolved. FUN_14077d580 writes an explicit supplied level but its only observed caller FUN_140358000 is a generic TESObjectREFR-to-Actor record/update route; when its Actor equals the global Player, it delegates to FUN_14077d580. Two other setter callers are not classified in this bounded pass.",
        "negative_and_limit": "The captured ConfirmLevelUpAttributeCallback FUN_140936740 applies the chosen ActorValue and calls FUN_14077d700, with no direct call to FUN_1401d7ba0 in its resolved body [EV-0689]. A candidate data table at RVA 0x19026c0 did not yield a valid RTTI identity (signature 0xCC0000C2 / offset 0xCCCCCCCC), so FUN_1409611e0's owning UI class and exact input/state meaning remain unknown. Static GOG code supports a threshold-gated UI notification writer outside the resolved attribute-confirm callback, but does not decide whether entering that UI path itself is the player's acceptance action. No Steam result follows.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = load(EVIDENCE)
    if any(row.get("id") == "EV-0691" for row in ledger.get("items", [])):
        raise SystemExit("EV-0691 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0691",
        "captured_utc": captured,
        "kind": "native",
        "source": "Identity-checked, read-only GOG AE 1.6.1179.0 Ghidra exact field setter, complete direct caller census, threshold predicate, Player UI/update caller paths, and post-write UI event helper; correlated with EV-0689 CommonLib/GetLevel/LevelUpMenu mapping.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": sha(SUMMARY),
        "edition": "AE",
        "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; Address Library SHA-256 3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e. Steam 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x1d7ba0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x77d650 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x77d630 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x9611e0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x9366d0 --list-call-edges --follow-incoming-calls 8 --timeout 600",
            "python3 scripts/python_env.py run tools/ghidra_probe.py --vtable-rtti-rvas 0x19026c0 --timeout 600",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q87_writer_evidence.py",
        ],
        "coverage": "The exact GOG setter writes the same TESActorBaseData+0x10 halfword read by GetLevel and has six analyzed direct callers. One Player-specific caller increments current GetLevel after the progress pair satisfies a threshold predicate, emits UILevelUp, and writes before a subsequent UI event dispatch. A second loop processes pending predicate states. Generic actor record-update, an uncalled Player increment wrapper with untyped data refs, two unclassified setter callers, an unidentified UI class/input gate, and two ambiguous direct caller registrations remain open.",
        "result": "PASS for locating the GOG field writer and a threshold-gated UI/notification route. H2 is supported for this bounded source path: the field write is not confined to the resolved ConfirmLevelUpAttributeCallback body. Whether the pending UI call requires an explicit player acceptance action, what the UI callback registration means, and whether Steam 1.6.1170.0 behaves the same remain unresolved; no natural level-one gate result is established.",
        "local_hashes": {name: item["stdout_sha256"] for name, item in manifest.items()},
        "related_evidence": ["EV-0109", "EV-0260", "EV-0688", "EV-0689", "EV-0690"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0691", "summary_sha256": sha(SUMMARY), "captures": list(manifest)}, indent=2))


if __name__ == "__main__":
    main()
