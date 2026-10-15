# Start the first deep research session

Use [`bounties/BOUNTY-0001-LEVEL1-P0.md`](../bounties/BOUNTY-0001-LEVEL1-P0.md) as the active target. The bounty selects the question and proof criteria; `AGENTS.md`, the skills and `protocols/TOOL_ROUTING.md` define the research method. Do not reset the existing frontier or claim that a lead is confirmed.

Before beginning, read `AGENTS.md`, `NORTH_STAR.md`, `STATE.md`, `ROADMAP.md`, `research/FRONTIER.json`, `research/RECOVERY.json`, the bounty, and only sources relevant to the chosen question. Bootstrap or reuse Python and run the strict check and `research_state.py validate` as documented in `LOCAL_RUNTIME_CONTRACT.md`. Validate the tool mode needed for the chosen source. After those checks pass, proceed with research; do not turn the session into ongoing setup work.

Recovery is idle after `TX-0004`; `Q-0001` / `OBJ-1` is the next frontier item. From the repository root, start its transaction after reviewing its competing models and current evidence:

```sh
python3 scripts/python_env.py run scripts/research_state.py begin \
  --transaction-id TX-0005 \
  --frontier-id Q-0001 \
  --next-action "Identify candidate vanilla quest/event level gates and state H1/H2 discriminants before source inspection."
```

On Windows PowerShell, use `py -3.12` instead of `python3`. Then investigate the chosen gate against the active bounty's proof criteria. If a record or runtime capability is unavailable, preserve the exact limit, queue a test protocol where useful, and continue with an independent tractable frontier item. Keep the level-one quest and armor-XP objectives at P0.
