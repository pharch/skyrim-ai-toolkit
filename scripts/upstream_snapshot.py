#!/usr/bin/env python3
"""Capture original guidance, Claude hooks, and skills from git HEAD before pruning."""
from pathlib import Path
import subprocess
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'references' / 'upstream'
FILES = [
    'AGENTS.md',
    'CLAUDE.md',
    'README.md',
    'SETUP_PROMPT.txt',
    'setup.sh',
    'KNOWLEDGEBASE.md',
    'KNOWLEDGEBASE.local.md',
    '.claude/settings.json',
    '.claude/settings.local.json.example',
    '.claude/skyrim-paths.env.example',
    '.claude/hooks/backup-before-edit.sh',
    '.claude/hooks/protect-bash.sh',
    '.claude/hooks/protect-files.sh',
    '.claude/hooks/session-kb-guard.sh',
    '.claude/hooks/snapshot-before-tool.sh',
    '.claude/skills/create-mod/SKILL.md',
    '.claude/skills/inspect-esp/SKILL.md',
    '.claude/skills/port-to-vr/SKILL.md',
    '.claude/skills/skyrim-audio/SKILL.md',
    '.claude/skills/skyrim-bsa/SKILL.md',
    '.claude/skills/skyrim-context/SKILL.md',
    '.claude/skills/skyrim-mcm/SKILL.md',
    '.claude/skills/skyrim-nif/SKILL.md',
    '.claude/skills/skyrim-save/SKILL.md',
]
OUT.mkdir(parents=True, exist_ok=True)
manifest=[]
for name in FILES:
    p=subprocess.run(['git','show',f'HEAD:{name}'],cwd=ROOT,capture_output=True)
    if p.returncode:
        # User-owned local KB may not be tracked. Keep original untouched.
        if name == 'KNOWLEDGEBASE.local.md' and (ROOT/name).exists():
            data=(ROOT/name).read_bytes()
            private=ROOT/'research'/'data-private'/'KNOWLEDGEBASE.local.md'
            private.parent.mkdir(parents=True,exist_ok=True)
            if private.exists() and private.read_bytes()!=data:
                raise SystemExit(f'Refusing to overwrite different private knowledge snapshot: {private}')
            private.write_bytes(data)
            print(f'Preserved UNTRACKED user knowledge privately at {private}; DO NOT git add')
        continue
    else:
        data=p.stdout
        source=f'git HEAD:{name}'
    dest=OUT/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() and dest.read_bytes()!=data:
        raise SystemExit(f'Refusing to overwrite different snapshot: {dest}')
    dest.write_bytes(data)
    manifest.append({'source':source,'snapshot':str(dest.relative_to(ROOT)), 'sha256':hashlib.sha256(data).hexdigest()})
(OUT/'SNAPSHOT_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(f'Snapshotted {len(manifest)} originals into {OUT}')
