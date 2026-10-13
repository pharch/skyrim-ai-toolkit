# Finalization checklist — blocked on authoritative specification

**Status: NOT COMPLETE.** The user specified 82 acceptance criteria in
`migration/FINAL_SETUP_BRIEF.md`, but that file is not present in this checkout
or in the available repository history. The exact criteria and their wording
cannot be reconstructed from the count alone.

No acceptance criteria have been invented or marked complete. Consequently,
this is a blocker record, **not** the requested 82-item evidence checklist, and
the repository readiness validator must continue to fail. Once the authoritative
brief is restored, transcribe its 82 criteria verbatim here, assign stable
`AC-01` through `AC-82` identifiers, and record concrete evidence and status for
each before claiming completion.

## Evidence recorded for this blocker

- Required source: `migration/FINAL_SETUP_BRIEF.md`.
- Observed state: file absent from the working tree and available Git history;
  search and recovery attempts are recorded in `migration/UNRESOLVED.md`.
- User-provided scope count: 82 acceptance criteria; their actual text is not
  available.
- Verification: `python scripts/validate_overlay.py` must report the missing
  authoritative brief and reject this blocker record as a completed checklist.
