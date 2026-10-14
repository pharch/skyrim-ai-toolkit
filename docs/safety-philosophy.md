# Research safety

This repository is an offline-first research checkout. It is not placed in the
Skyrim installation, does not install mods, and does not grant permission to
inspect or mutate a live game.

## Protected state

- Preserve original game executables, plugins, archives, saves, and co-saves.
- Use copies for analysis and new scratch directories for archive extraction.
- Keep private paths, API keys, saves, co-saves, Discord exports, and raw game
  files outside Git.
- Do not mutate plugins, archives, saves, or game settings as part of research.
- Keep `diagnostic_intervention` separate from vanilla candidate and
  reproduction lanes.

## Evidence safety

Verify the exact Skyrim AE executable and active profile before record or live
work. Keep raw output, input hashes, tool versions, exit status, denominators,
and negative results. An empty parse or missing tool is unknown coverage. Do
not claim that a fixture test establishes Windows xEdit, MO2, DevBench, or
in-game compatibility.

## Interactive operation

Use an interactive Codex session as the research interface. Persist the
checkpoint, frontier, and session log before a context boundary; inspect partial
outputs before resuming. Keep live mutation tools out of unattended runs. Stop
on identity mismatch, data corruption, crash loops, or a missing baseline, then
continue with offline work.

These rules are operational guidance, not an OS-level sandbox. Keep Codex
approval and sandbox settings conservative; never rely on prompts or an
instruction file as the only boundary around the game installation.
