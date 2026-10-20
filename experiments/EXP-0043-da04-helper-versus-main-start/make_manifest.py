#!/usr/bin/env python3
"""Create the private TX-20261016-0036 capture manifest."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


TX_ID = "TX-20261016-0036"
TX_DIR = Path(".local/alignment/transactions") / TX_ID
MANIFEST = TX_DIR / "capture-manifest.json"
EXP_DIR = Path("experiments/EXP-0043-da04-helper-versus-main-start")
SCHEMA_URL = "https://raw.githubusercontent.com/TES5Edit/TES5Edit/dev-4.1.6/Core/wbDefinitionsTES5.pas"
UESP_REVISION = 3564369


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


files = {
    path.name: sha256(path)
    for path in sorted(TX_DIR.iterdir())
    if path.is_file() and path != MANIFEST
}
research_scripts = {
    path.name: sha256(path)
    for path in sorted(EXP_DIR.glob("*.py"))
}
manifest = {
    "transaction_id": TX_ID,
    "captured_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    "scope": {
        "edition": "Skyrim AE",
        "runtime_identity": "Steam 1.6.1170.0 verified separately by EV-0109",
        "source_plugin": "Skyrim.esm prepared official-master copy",
        "source_plugin_sha256": "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107",
        "profile_order": "not verified; no winner claim",
        "route": "direct read-only TES4 parser; not native xEdit",
    },
    "tools": {
        "research_dispatcher": "python3 scripts/python_env.py run",
        "records": "tools/xedit_bridge.py file-records",
        "pex": "tools/papyrus_pex.py extract/disassemble",
        "vmad_decoder": "experiments/EXP-0043-da04-helper-versus-main-start/decode_qust_vmad.py",
        "vmad_schema_url": SCHEMA_URL,
        "vmad_schema_revision_label": "TES5Edit dev-4.1.6; source page is a branch URL",
        "quest_setstage_docs": "https://papyrus.bellcube.dev/skyrimse/script/quest/function/setstage/",
        "quest_setstage_docs_scope": "Papyrus Index transcription/references of CK Wiki; CK Wiki URL returned HTTP 403",
    },
    "archive": {
        "name": "Skyrim - Misc.bsa",
        "sha256": "ddb19908dcd5c135b8bba240e8dfcdb95395b569852f715d330396e9c1390b9d",
        "route": "tested read-only archive extraction",
    },
    "secondary_source": {
        "name": "local UESP Skyrim:Daedric Quests page",
        "revision": UESP_REVISION,
        "scope": "secondary route lead only",
    },
    "native_xedit_retry": {
        "command": "native-query --signature QUST --plugin Skyrim.esm --editor-id DA04",
        "status": "failed before process enumeration; no native record fields",
        "error": "PowerShell step processes-before exited 1: WSL UtilBindVsockAnyPort:307: socket failed 1",
    },
    "files": files,
    "research_scripts": research_scripts,
}
MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {MANIFEST} with {len(files)} hashed files")
