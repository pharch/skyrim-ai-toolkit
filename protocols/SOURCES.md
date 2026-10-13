# Evidence Sources, UESP, Discord and Conflicts

## Reference priority depends on the question

For what is in **this** game build: direct runtime observation + appropriate load-order resolution + vanilla records are strongest. For what a function does: reproducible native tracing is strongest. For known quest prerequisites and community observations: UESP is a helpful starting point; Apocrypha logs suggest experiments and show anecdotal reproductions. External claims must be dated and attributed. A single erroneous UESP or Discord statement never overrides a repeatable instrumented result.

## Fact-check triggers

Before assuming a quest has a level requirement, an item has a magic effect, an encounter uses a leveled list, a perk affects a formula, or a console command has no side effects: query UESP, review the corresponding active record/script, and check existing Apocrypha messages. Revisit the source if an observation contradicts it. Record page URL, revision ID / last-edited time and game build; for Discord record export ID, channel, message ID, timestamp and author pseudonym.

## UESP access

`scripts/uesp_lookup.py` is a deliberately small **on-demand** MediaWiki client (search and fetch), not a full mirror. Its endpoint `https://en.uesp.net/w/api.php` must be tested locally; our preliminary remote check was blocked (HTTP 403), so availability is NOT established. If blocked, do not evade access controls or run a mass crawl; ask UESP for a permitted API/offline dump or use authorized public page lookups and metadata-only caching. Review UESP copyright/license, rate limits, and robots restrictions before bulk use. Retain URL and revision attribution. Never assume the entire wiki may be redistributed in a fork.

If a license-compliant complete UESP article export is available, `scripts/index_uesp_dump.py` streams its MediaWiki XML into a local SQLite FTS index, and `scripts/search_uesp_dump.py` queries the resulting article text with revision provenance. These scripts neither retrieve an export nor grant redistribution rights. Use an offline index across approved data only if access/licensing permit it. For comprehensive search, prefer UESP search API with fallback to human-mediated retrieval. Fandom is **not** in the default ingestion path; only inspect a specific Fandom claim when testing a contradiction, never silently merge.

## Apocrypha Discord export

Ingest local authorized exports through `scripts/index_apocrypha.py`. Keep raw exports in a user-controlled untracked location. Search the resulting local SQLite FTS index; messages are hypotheses or observations, not direct game evidence unless they contain a reproducible protocol. Do not upload private chat content to public services or commit it. Preserve exact message provenance and quote sparingly. Respect community sharing/retention expectations.

## Conflicts

When sources disagree, write both claims to `research/CONTRADICTIONS.md`; identify potentially different versions, DLC, mods, save-state, dates or interpretive definitions, then propose a discriminating test. Never pick UESP or Fandom automatically by a simple absolute ranking.
