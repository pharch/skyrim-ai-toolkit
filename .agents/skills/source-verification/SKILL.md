---
name: skyrim-source-verification
description: Fact-check Skyrim quest prerequisites, perks, formulas, items and game behavior before relying on assumptions, using UESP, local game data and Apocrypha Discord evidence.
---

# Source verification procedure

Use when a basic factual premise influences a hypothesis or test plan.

1. State the exact falsifiable premise and applicable game build.
2. Run `python scripts/uesp_lookup.py search '<keywords>'`, then targeted `page '<title>'` if the UESP API is accessible and permitted. Record page URL + revision. Do not retry aggressively after a 403.
3. Run `python scripts/search_apocrypha.py '<FTS terms>'` if a local authorized index exists, preserving channel/message IDs and timestamps.
4. Verify the underlying active game record/script using xelib or equivalent where possible. Beware MO2 virtual load order.
5. Separate source quote, interpretation, and your actual test observation. Record disagreement in `research/CONTRADICTIONS.md` and define a discriminant.
6. Update the claim ledger. Do not present wiki/forum conclusions as code-confirmed facts.
