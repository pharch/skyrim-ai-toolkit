#!/usr/bin/env python3
"""Generate a read-only, Git-aware prune plan. Does NOT delete anything."""
from pathlib import Path
import subprocess, shlex

root=Path(__file__).resolve().parents[1]
p=subprocess.run(['git','ls-files','-z'],cwd=root,stdout=subprocess.PIPE,check=True)
paths=[x.decode('utf-8','surrogateescape') for x in p.stdout.split(b'\0') if x]
# Remove only when upstream instructions have been snapshotted and adapted.
retire_root={'CLAUDE.md','SETUP_PROMPT.txt','setup.sh'}
asset_tokens={'skyrim-nif','skyrim-audio','skyrim-vfx','skyrim-mesh','skyrim-texture','skyrim-animation','skyrim-vr','nif','pynifly','pyffi','render','blender','nifskope','texture','audio','fomod','vfx','vr-input','mcm'}
retire=[]; examine=[]; keep=[]
for path in paths:
    lp=path.lower()
    if path in retire_root or lp.startswith('.claude/hooks/') or lp.startswith('.claude/settings'):
        retire.append(path)
    elif lp.startswith('.claude/skills/') and any(tok in lp for tok in asset_tokens):
        examine.append((path,'ASSET-SKILL: preserve unique engine/protocol facts first'))
    elif any(tok in lp for tok in asset_tokens) and not lp.startswith('references/upstream/'):
        examine.append((path,'ASSET-PATH: inspect consumers and references; do not auto-delete'))
    elif lp.startswith('.claude/'):
        examine.append((path,'CLAUDE-SPECIFIC: migrate useful skill first'))
    else:
        keep.append(path)

report=root/'migration'/'PRUNE_PLAN.md'
report.parent.mkdir(exist_ok=True)
with report.open('w',encoding='utf-8') as f:
    f.write('# Generated pruning plan\n\nRegenerate after upstream updates. No files have been deleted by this script.\n\n')
    f.write(f'Inventory: {len(paths)} tracked files; {len(retire)} retire candidates; {len(examine)} manual-review candidates; {len(keep)} initially retained.\n\n')
    f.write('## Remove after snapshots + Codex port\n\n')
    for x in retire:f.write(f'- `{x}`\n')
    f.write('\n### Exact Git removal commands (review each command first)\n\n```bash\n')
    for x in retire:f.write('git rm -- '+shlex.quote(x)+'\n')
    f.write('```\n\n## Manual audit before asset pruning\n\n')
    for x,why in examine:f.write(f'- `{x}` — {why}\n')
    f.write('\n## Retain by default\n\n')
    for x in keep:f.write(f'- `{x}`\n')
print(f'{report}: {len(retire)} proposed retirements, {len(examine)} review items. NO DELETION performed.')
