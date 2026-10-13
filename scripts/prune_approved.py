#!/usr/bin/env python3
"""Preview or execute exact reviewed git rm paths from migration/PRUNE_APPROVED.txt.
No patterns, wildcards or directory-wide implicit recursion. One tracked file per line.
"""
import argparse, pathlib, subprocess, shlex, sys
r=pathlib.Path(__file__).resolve().parents[1]
a=argparse.ArgumentParser(description=__doc__)
a.add_argument('--apply',action='store_true',help='Execute after all file paths were individually reviewed')
args=a.parse_args()
manifest=r/'references/upstream/SNAPSHOT_MANIFEST.json'
if not manifest.exists():raise SystemExit('First run python scripts/upstream_snapshot.py and review original snapshots.')
review=r/'migration'/'PRUNE_APPROVED.txt'
if not review.exists():raise SystemExit(f'Create {review} with one reviewed tracked file per line (no globs).')
tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=r).decode('utf-8','surrogateescape').split('\0'))
protected=('LICENSE','KNOWLEDGEBASE.md','AGENTS.md','NORTH_STAR.md','STATE.md','ROADMAP.md','.codex/config.toml')
paths=[]
for line in review.read_text(encoding='utf-8').splitlines():
    x=line.strip()
    if not x or x.startswith('#'):continue
    if x in protected or not x or x.startswith('/') or '..' in pathlib.PurePosixPath(x).parts or '*' in x or '?' in x:
        raise SystemExit(f'Unsafe/unapproved removal path: {x!r}')
    if x not in tracked:
        raise SystemExit(f'Not an exact tracked file path: {x!r}')
    paths.append(x)
if len(paths)!=len(set(paths)):raise SystemExit('Duplicate entries in approved list')
if not paths:raise SystemExit('No approved paths. First audit the generated migration/PRUNE_PLAN.md.')
branch=subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()
print('Branch:',branch,'Files:',len(paths))
for x in paths:print('git rm -- '+shlex.quote(x))
if not args.apply:
    print('DRY RUN: add --apply to perform the exact commands above.');sys.exit(0)
if branch in ('master','main',''):
    raise SystemExit('Refusing to prune on master/main or detached HEAD. Create a dedicated branch.')
for x in paths:
    subprocess.run(['git','rm','--',x],cwd=r,check=True)
print('Removed approved files from index/worktree; review git diff --cached before commit.')
