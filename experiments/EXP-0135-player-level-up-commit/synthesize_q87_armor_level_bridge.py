#!/usr/bin/env python3
"""Register the shared-progress-object bridge from armor skill awards to level writes."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "research/EVIDENCE.json"
LOCAL = ROOT / ".local"
SUMMARY = LOCAL / "alignment/transactions/TX-20261020-0006/q87-armor-level-field-bridge.json"
BUILD_SHA = "9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def verify_capture(stamp: str, required: tuple[str, ...]) -> dict:
    stdout = ROOT / f".local/ghidra/gog-query-{stamp}.stdout.raw"
    meta_path = ROOT / f".local/ghidra/gog-query-{stamp}.meta.json"
    meta = load(meta_path)
    if (meta.get("ok") is not True or meta.get("read_only") is not True or
            meta.get("auto_analysis_disabled") is not True or
            meta.get("analysis_binary_product_version") != "1.6.1179" or
            meta.get("analysis_binary_sha256") != BUILD_SHA or
            meta.get("stdout_sha256") != digest(stdout)):
        raise SystemExit(f"capture identity/read-only/hash check failed: {stamp}")
    content = stdout.read_text(encoding="utf-8", errors="replace")
    if not all(needle in content for needle in required):
        raise SystemExit(f"shared-progress discriminants missing from capture: {stamp}")
    return {
        "requested_rva": meta.get("requested_rva"),
        "stdout": f"private-local:{stdout.relative_to(ROOT).as_posix()}",
        "stdout_sha256": digest(stdout),
        "metadata_sha256": digest(meta_path),
    }


def main() -> None:
    captures = {
        "skill_progress_mutates_progress": verify_capture(
            "20261020T033913Z",
            ("FUN_14077d090", "*(float *)*param_1", "_DAT_1420069b0", "param_1 + 0x9b8"),
        ),
        "threshold_predicate": verify_capture(
            "20261020T041628Z",
            ("MOVSS XMM0, dword ptr [RAX + 0x4]", "COMISS XMM0, dword ptr [RAX]", "SETBE AL"),
        ),
        "statsmenu_uses_player_progress_object": verify_capture(
            "20261020T041105Z",
            ("DAT_143188918 + 0x9b8", "FUN_14077d630(uVar1)", "FUN_14077d650(uVar1)"),
        ),
    }
    q86 = load(LOCAL / "alignment/transactions/TX-20261020-0005/q86-source-summary.json")
    armor = load(LOCAL / "alignment/transactions/TX-20261020-0005/q86-armor-to-levelxp.json")
    writer = load(LOCAL / "alignment/transactions/TX-20261020-0006/q87-level-writer-trace.json")
    lifecycle = load(LOCAL / "alignment/transactions/TX-20261020-0006/q87-statsmenu-factory-lifecycle.json")
    if (BUILD_SHA not in q86.get("target_separation", {}).get("analysis_target", "") or
            armor.get("target", "").find(BUILD_SHA) < 0 or
            writer.get("build", {}).get("executable_sha256") != BUILD_SHA or
            lifecycle.get("gog_build", {}).get("sha256") != BUILD_SHA):
        raise SystemExit("cross-domain summaries do not share the verified GOG build identity")
    required_summary = (
        "PlayerCharacter slot 0xF7",
        "FUN_14077d090",
    )
    if not all(term in armor.get("bounded_observation", "") for term in required_summary):
        raise SystemExit("armor award summary no longer contains the verified Player UseSkill path")

    summary = {
        "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "transaction": "TX-20261020-0006",
        "gog_build": {"product_version": "1.6.1179.0", "sha256": BUILD_SHA, "rvas_transferred_to_steam": False},
        "source_summaries": {
            "EV-0689": {"artifact": "private-local:.local/alignment/transactions/TX-20261020-0005/q86-source-summary.json", "sha256": digest(LOCAL / "alignment/transactions/TX-20261020-0005/q86-source-summary.json")},
            "EV-0690": {"artifact": "private-local:.local/alignment/transactions/TX-20261020-0005/q86-armor-to-levelxp.json", "sha256": digest(LOCAL / "alignment/transactions/TX-20261020-0005/q86-armor-to-levelxp.json")},
            "EV-0691": {"artifact": "private-local:.local/alignment/transactions/TX-20261020-0006/q87-level-writer-trace.json", "sha256": digest(LOCAL / "alignment/transactions/TX-20261020-0006/q87-level-writer-trace.json")},
            "EV-0693": {"artifact": "private-local:.local/alignment/transactions/TX-20261020-0006/q87-statsmenu-factory-lifecycle.json", "sha256": digest(LOCAL / "alignment/transactions/TX-20261020-0006/q87-statsmenu-factory-lifecycle.json")},
        },
        "captures": captures,
        "discriminant": "FUN_140739050 passes PlayerCharacter+0x9B8 to FUN_14077d090 after positive points. That routine adds character-level progress to the float at *(float*)*param_1. The StatsMenu update handler independently loads the same PlayerCharacter+0x9B8 pointer and passes it to FUN_14077d630/FUN_14077d650. Those functions compare the same progress object's float pair as pfVar1[1] <= pfVar1[0], and the due branch writes Player GetLevel+1 through the verified TESActorBaseData setter. The shared Player+0x9B8 argument and shared inner progress pointer discriminate this from two unrelated XP stores.",
        "finding": "For the bounded GOG path, positive HitData-derived worn-armor skill points can increase the same Player level-progress object checked by the StatsMenu kUpdate threshold path; when its threshold is due and that handler runs, the field writer can advance the stored GetLevel value. The relationship is a static causal inference across EV-0689 through EV-0693, not a Steam runtime observation or a zero-armor-XP result.",
        "limits": "This does not quantify the XP per hit or threshold, establish how/when a natural Steam UI update occurs, show a level-one quest/encounter start, or demonstrate functional protection with zero armor XP. Positive points are required by the captured PlayerCharacter UseSkill slot target; the level-field writer remains a separate menu-update stage.",
    }
    SUMMARY.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ledger = load(EVIDENCE)
    if any(row.get("id") == "EV-0694" for row in ledger.get("items", [])):
        raise SystemExit("EV-0694 already exists; refusing duplicate registration")
    ledger["items"].append({
        "id": "EV-0694",
        "captured_utc": summary["captured_utc"],
        "kind": "native",
        "source": "Cross-capture pointer/dataflow synthesis of GOG HitData armor skill awards, Player skill progression, StatsMenu level threshold, and ActorBaseData level setter.",
        "artifact": f"private-local:{SUMMARY.relative_to(ROOT).as_posix()}",
        "sha256": digest(SUMMARY),
        "edition": "AE",
        "runtime": "Static GOG analysis build only: ProductVersion 1.6.1179.0, executable SHA-256 9b0fc7880c4b12d436bfb59bcae64868f176dbc04010adbd9bc2ecb64bc8ed3f. Steam 1.6.1170.0 is separate [EV-0109].",
        "modified_state": False,
        "lane": "mechanism_inference",
        "tools": [
            "python3 scripts/python_env.py run experiments/EXP-0135-player-level-up-commit/synthesize_q87_armor_level_bridge.py",
            "source captures EV-0689, EV-0690, EV-0691, and EV-0693; all summarized hashes and GOG identities checked",
        ],
        "coverage": "The PlayerCharacter+0x9B8 pointer passed from positive armor skill UseSkill into FUN_14077d090 is the same pointer loaded by StatsMenu::ProcessMessage(kUpdate) before checking the threshold. Skill progression mutates the shared object's accumulated-level-progress float, and the due threshold branch reaches the exact stored-level setter.",
        "result": "PASS for the bounded GOG static causal bridge from hit-earned worn-armor skill points to level-up progress and, after the threshold is due and StatsMenu kUpdate runs, to the stored GetLevel field. This is not zero-armor-XP, effective-protection, Steam, or natural level-one quest evidence.",
        "related_evidence": ["EV-0109", "EV-0221", "EV-0260", "EV-0670", "EV-0674", "EV-0689", "EV-0690", "EV-0691", "EV-0692", "EV-0693"],
    })
    EVIDENCE.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"registered": "EV-0694", "summary_sha256": digest(SUMMARY)}, indent=2))


if __name__ == "__main__":
    main()
