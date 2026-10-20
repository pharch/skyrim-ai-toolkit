#!/usr/bin/env python3
"""Register the GOG-only HitData-to-skill-progress cross-domain capture for Q86."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STAMP = "20261020T040343Z"
TX = "TX-20261020-0005"
GHIDRA = ROOT / ".local/ghidra"
META = GHIDRA / f"gog-query-{STAMP}.meta.json"
STDOUT = GHIDRA / f"gog-query-{STAMP}.stdout.raw"
EVIDENCE = ROOT / "research/EVIDENCE.json"
RECOVERY = ROOT / "research/RECOVERY.json"
SUMMARY = ROOT / ".local/alignment/transactions" / TX / "q86-armor-to-levelxp.json"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    if (recovery.get("status"), recovery.get("transaction_id"), recovery.get("frontier_id")) != ("running", TX, "Q-0086"):
        raise SystemExit("Q86 is not the active transaction")
    meta = json.loads(META.read_text(encoding="utf-8"))
    if (meta.get("ok") is not True or meta.get("read_only") is not True or
        meta.get("auto_analysis_disabled") is not True or
        meta.get("analysis_binary_product_version") != "1.6.1179" or
        meta.get("analysis_binary_sha256") != "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f" or
        str(meta.get("requested_rva", "")).lower() != "0x6bcaa0" or
        meta.get("stdout_sha256") != sha(STDOUT)):
        raise SystemExit("GOG identity, mode, requested RVA, or raw hash check failed")
    raw = STDOUT.read_text(encoding="utf-8", errors="replace")
    for marker in ("FUN_1406bcaa0", "param_2 != DAT_143138a98", "*param_2 + 0x7b8", "iVar3,local_94,lVar7,0"):
        if marker not in raw:
            raise SystemExit(f"expected receiver-side skill call is missing: {marker}")

    summary = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": TX,
        "target": "GOG SkyrimSE.exe 1.6.1179.0; SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f",
        "address_library_sha256": "3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e",
        "rvas_transferred_to_steam": False,
        "query": {
            "requested_rva": meta["requested_rva"],
            "metadata": f"private-local:{META.relative_to(ROOT).as_posix()}",
            "metadata_sha256": sha(META),
            "stdout": f"private-local:{STDOUT.relative_to(ROOT).as_posix()}",
            "stdout_sha256": sha(STDOUT),
            "function": "FUN_1406bcaa0",
        },
        "bounded_observation": "In the Player receiver branch, FUN_1406bcaa0 routes the unblocked worn-armor skill selection through vtable byte offset +0x7b8. This is slot 0xF7 (0x7b8 / 8). The visible selector values are 0xB/0xC (ActorValue indices 11/12 in the previously screened path); the call passes its calculated point value. Prior identity-checked captures map PlayerCharacter slot 0xF7 to FUN_140739050 (EV-0674, EV-0221), whose positive-points branch calls FUN_14077d090; EV-0689 maps that progress routine to per-skill progress plus a separate cumulative character-level XP accumulator. The shared native path is a GOG-only causal connection from the captured armor-skill award route into the general skill-progress/character-XP routine. It does not establish ordinary-hit runtime coverage, effective protection, a zero-XP exploit, Steam behavior, or when GetLevel changes.",
        "scope": "Static GOG analysis only; no original game state was modified. Player identity is inferred from the compared global in the captured branch. Selector values and slot resolution are cross-checked against the separately cited captured paths.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    ledger = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    if any(row.get("id") == "EV-0690" for row in ledger.get("items", [])):
        raise SystemExit("EV-0690 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0690",
        "captured_utc": summary["captured_utc"],
        "kind": "native",
        "source": "Read-only, build-identity-checked GOG AE 1.6.1179.0 Ghidra decompilation of the Player receiver path in FUN_1406bcaa0, correlated with previously captured PlayerCharacter UseSkill slot and skill-progress targets.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": sha(SUMMARY),
        "edition": "AE",
        "runtime": "GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f; matching Address Library SHA-256 3ee46b2f3a8a24b9cda1f2aa63b0f0f47dea347e52701a6739327e5ea1b5838e. Steam 1.6.1170.0 is separate [EV-0109]; no RVA transfer.",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run tools/ghidra_probe.py --rva 0x6bcaa0 --timeout 600",
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/register_q86_armor_level_bridge.py",
        ],
        "coverage": "The captured FUN_1406bcaa0 Player receiver branch reaches vtable byte offset +0x7b8 for the unblocked worn-armor skill call. Division by the 8-byte pointer size gives slot 0xF7. The exact slot target and skill-progress helper are cross-checked with EV-0674/EV-0221 and EV-0689. This is the direct GOG call-path bridge; it does not show an ordinary live hit, positive measured protection, Steam-equivalent code, or the timing of the Player level field update.",
        "result": "PASS for a bounded GOG source-code connection: the captured worn-armor AV11/AV12 skill route enters the same PlayerCharacter UseSkill/progress path that accumulates separate character-level XP. This creates a causal cross-domain edge between hit-earned armor skill points and level-progress accumulation, but does not resolve pending-versus-accepted GetLevel timing or establish an OBJ-2 result.",
        "local_hashes": {
            "query_stdout_sha256": sha(STDOUT),
            "query_metadata_sha256": sha(META),
        },
        "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0670", "EV-0674", "EV-0689"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0690", "summary_sha256": sha(SUMMARY), "query_stdout_sha256": sha(STDOUT)}, indent=2))


if __name__ == "__main__":
    main()
