# Final alignment resume and research handoff

The final local alignment is complete when
[`FINAL_ALIGNMENT_REPORT.md`](FINAL_ALIGNMENT_REPORT.md) and
[`FINAL_ALIGNMENT_CHECKLIST.md`](FINAL_ALIGNMENT_CHECKLIST.md) show terminal
statuses and the report's validators pass. If interrupted before then, first
read `STATE.md`, `research/FRONTIER.json`, `research/RECOVERY.json`, and the
last section of `research/SESSION_LOG.md`, then continue from the exact
`next_action` recorded there. Do not begin glitch research while an alignment
criterion remains `PENDING`.

Current disposition: all 52 criteria are terminal (50 PASS, 2
BLOCKED_EXTERNAL, zero pending). The gates are `STATIC_RESEARCH_READY=READY`,
`NATIVE_RESEARCH_READY=PARTIAL`, and
`INSTRUMENTED_AUTONOMOUS_RESEARCH_READY=NOT_VERIFIED`. SSEView opened and
completed an isolated five-official-master load (EV-0184/0185/0189), but its
accessible UI tree exposed no safe record selector and the full MO2 profile is
unknown. The Observer build and 7/7 analyzer tests passed, but it remains
staged only with no deployment or live handshake (EV-0186/0187/0188).

For the first deep research session, start at the repository root and run:

```text
python3 scripts/python_env.py run scripts/research_state.py validate
```

Then read [`FINAL_ALIGNMENT_REPORT.md`](FINAL_ALIGNMENT_REPORT.md) and start a
new interactive Codex session using the complete prompt in
[`docs/RESEARCH_START_PROMPT.md`](../docs/RESEARCH_START_PROMPT.md). It begins
with P0 OBJ-1 / Q-0001 unless frontier scoring documents a higher-information
P0 item. It requires rival models, predicted discriminants, checkpoint
recovery, cross-domain synthesis, and continued frontier selection.

External unblocks before a native winner or live test:

1. In ignored `config/local.env`, set `MO2_PROFILE_DIR` to the selected MO2
   profile and `PLUGINS_TXT` to that profile's explicit `plugins.txt`. The
   configured SSEEdit 4.1.5.0 binary still matches its recorded hash. Restore
   a working WSL PowerShell bridge (current error: `UtilBindVsockAnyPort`) or
   run preflight from the supported Windows host, then run
   `python3 scripts/python_env.py run tools/ae_preflight.py`. Do not run a
   winning-record query unless this validates the complete order.
2. Set `RESEARCH_TEST_SAVE` only to a designated disposable copy. The current
   fallback environment lacks `lz4`; verify the named environment with
   `python3 scripts/python_env.py check` before using
   `python3 scripts/python_env.py run scripts/read-save.py <copy.ess>` or
   `python3 scripts/python_env.py run tools/cosave-info.py <copy.skse>`.
   ReSaver remains unavailable until its existing local executable and a safe
   copy are identified.
3. A user-controlled disposable AE test profile and a running compatible game
   are required before deploying the already-built Observer and attempting a
   read-only handshake/capture. Do not use an original save or change the
   installed game as part of startup.

The isolated recovery rehearsal passed in EV-0175. It verified the local
transaction/recovery tool across processes; it does not claim continuous Codex
execution or a game result.
