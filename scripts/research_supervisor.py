#!/usr/bin/env python3
"""Opt-in local Codex session supervisor for sustained, bounded research.

Requires installed/authenticated Codex CLI. Does NOT auto-start in background.
Each iteration is a fresh Codex exec reading repository state; this is deliberate,
not a promise that a Codex session itself lasts a week. Invoke only after auditing
file/game permissions and all enabled MCP endpoints.
"""
import argparse, datetime as dt, json, os, pathlib, shutil, subprocess, sys, time
r=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--hours',type=float,default=168)
p.add_argument('--round-minutes',type=int,default=45)
p.add_argument('--max-failures',type=int,default=3)
p.add_argument('--execute',action='store_true')
a=p.parse_args()
if a.hours <= 0 or a.round_minutes < 5 or a.max_failures < 1: p.error('invalid bounds')
if not a.execute and not shutil.which('codex'):
    print('WARNING: Codex executable is not on PATH; dry run only.')
if a.execute and not shutil.which('codex'): raise SystemExit('Codex executable is not on PATH')
if not (r/'AGENTS.md').exists():raise SystemExit('wrong repository root')
logdir=r/'research'/'supervisor-logs';logdir.mkdir(exist_ok=True,parents=True)
command=['codex','exec','--sandbox','workspace-write','--ask-for-approval','never','--json','-']
prompt='''Continue the Skyrim level-1 exploit research program documented in AGENTS.md.
Read NORTH_STAR.md, STATE.md, ROADMAP.md and research/FRONTIER.json.
Choose and execute a high-information-gain, nonblocked research item; prioritize
OBJ-1 or OBJ-2; do not re-perform last session's work without a new reason.
Fact-check source assumptions; capture provenance; update state, frontier and
research/SESSION_LOG.md. Include a succinct precise handoff checkpoint.
Never invoke game mutations without independent approved safeguards and a test
save; prefer offline research until vetted live instrumentation exists.
If one branch is stale, synthesize and move to another. Do not invent evidence.
'''
if not a.execute:
    print('DRY RUN ONLY. Would run:', ' '.join(command))
    print('CWD:',r)
    print('For live bounded run: python scripts/research_supervisor.py --execute --hours 168')
    sys.exit(0)
stop=r/'.stop-research'
lock=r/'.research-supervisor.lock'
try:
    fd=os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
except FileExistsError:
    raise SystemExit(f'Lock exists ({lock}); stop existing supervisor or inspect/remove stale lock manually')
with os.fdopen(fd,'w') as f:f.write(str(os.getpid()))
start=time.monotonic();deadline=start+a.hours*3600
failure_streak=0;run=0
try:
    while time.monotonic()<deadline and not stop.exists():
        run+=1
        ts=dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        base=logdir/f'{ts}-run{run:04d}'
        meta={'utc':ts,'run':run,'command':command,'timeout_minutes':a.round_minutes}
        (pathlib.Path(str(base)+'.meta.json')).write_text(json.dumps(meta,indent=2))
        print(f'[{ts}] Starting research cycle {run}',flush=True)
        timeout=min(a.round_minutes*60,max(1,int(deadline-time.monotonic())))
        with open(str(base)+'.out.jsonl','w',encoding='utf-8') as out,open(str(base)+'.err.log','w',encoding='utf-8') as err:
            proc=subprocess.Popen(command,cwd=r,stdin=subprocess.PIPE,stdout=out,stderr=err,text=True)
            try:
                proc.communicate(input=prompt,timeout=timeout)
                rc=proc.returncode
            except subprocess.TimeoutExpired:
                proc.kill();proc.communicate();rc=124
        meta['exit_code']=rc
        meta['ended_at']=dt.datetime.now(dt.timezone.utc).isoformat()
        pathlib.Path(str(base)+'.meta.json').write_text(json.dumps(meta,indent=2))
        if rc:
            failure_streak+=1
            print(f'Cycle {run} exited {rc}; consecutive failures: {failure_streak}',flush=True)
            if failure_streak>=a.max_failures:break
            time.sleep(10)
        else:
            failure_streak=0
        # Explicitly opt-out if user creates a local .stop-research sentinel.
        # No attempts to repair errors by changing permissions or mutating the game.
finally:
    lock.unlink(missing_ok=True)
print(f'Supervisor ended; cycles={run}. Inspect STATE.md, SESSION_LOG and logs.',flush=True)
