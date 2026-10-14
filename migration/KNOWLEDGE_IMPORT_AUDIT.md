# Knowledge import audit

This audit records the distinction between what a hashed legacy report says
and what has been reverified on the current target. The original source
checkout had no usable Git metadata; source identity uses
`LEGACY-20261014-A` and the per-file hashes in
[`legacy_markdown_manifest.tsv`](legacy_markdown_manifest.tsv).

## Canonical records

- [`research/EVIDENCE.json`](../research/EVIDENCE.json) contains individually
  hashed legacy source records. The associated path-to-ID mapping is
  [`legacy_evidence_ids.json`](legacy_evidence_ids.json).
- [`research/CLAIMS.md`](../research/CLAIMS.md) separates historical report
  conclusions from runtime observations and lists the source IDs and limits.
- [`research/MECHANISMS.md`](../research/MECHANISMS.md),
  [`research/GLITCHES.md`](../research/GLITCHES.md),
  [`research/CONTRADICTIONS.md`](../research/CONTRADICTIONS.md), and
  [`research/KNOWLEDGE_GRAPH.md`](../research/KNOWLEDGE_GRAPH.md) preserve the
  causal model, negative results, conflicts, and cross-domain links.
- [`legacy_disposition.tsv`](legacy_disposition.tsv) is the per-file review
  authority. A source row marked as imported or superseded does not imply its
  mechanic was reproduced.

## Review boundary

The source-root summaries and reports keep their stated GOG 1.6.1179 or
Steam 1.6.1170 assumptions; those executable identities were not revalidated
in this Linux session. The old runtime Markdown lacks its claimed raw logs in
the candidate inventory. The private conversation export and community
evidence summary are excluded from copying or paraphrase. All 242 candidate Markdown files have been reviewed and given a source-specific disposition; one generated third-party Markdown file is tracked separately as an exclusion. A completed EV entry still means only that its hashed source report was reviewed, not that its mechanic was reproduced.

The per-file table below is updated as topic reviews are integrated. Exact
formulae, record/form identifiers, scope counts, and negative branches are
retained only when the source report supplies them.

| Evidence IDs | Source review and canonical link | Claim-level boundary retained |
|---|---|---|
| EV-0056 | `out/findings.md` → CL-L020, M-0004, G-0002 | 50 PoisonResist MGEFs, 319 reverse references, and 148 candidate recipes are report counts; old probe only supports hostile-first classification. No exact recipe, resistance result, delivery, or XP test. |
| EV-0057 | `legacy/out/diagnostics/alchemy-peak-shift-cleanup-arithmetic.md` → CL-L021, M-0002, G-0003, C-LEG-0007 | Corrects cleanup: Recover subtracts the negated effective magnitude; `+0x94` records the observed slot delta. Residue arithmetic is modeled, not gameplay. |
| EV-0058–EV-0064 | Potion cleanup, Conjuration recipe, null-key AV148, VMAD writer inventory, self-poison delivery/transfer, and robe reachability diagnostics → CL-L022–CL-L024, CL-L031, CL-L036–CL-L037, M-0003–M-0004/M-0012–M-0013, G-0002, C-LEG-0008 | The 89.2167511 Conjuration value is a static cost-model prediction; AV148 and robe reachability are static record claims; ExtraPoison transfer does not establish a stable self-delivery route. |
| EV-0065–EV-0069 | Enchanting furniture/output/condition reports and Speech reports → CL-L025–CL-L028, CL-L039, M-0001/M-0007, G-0001/G-0006 | No accessible type-3 furniture was found; fixed COBJ outputs do not select arbitrary enchantments. The Speech success-without-XP report lacks save/form/timing/raw delta. |
| EV-0070–EV-0074 | Two historical runtime Markdown reports and skill-use/ActiveEffect audits → CL-L029–CL-L032, M-0006/M-0012 | Raw runtime logs and executable hash are absent; the reports do not establish current runtime. Scroll and ordinary spell skill-use differ; the MGEF scan is limited to its historical corpus. |
| EV-0075–EV-0079 | Direct spell/favorites, MGR21, finite cleanup, and transform lifecycle reports → CL-L031, CL-L033–CL-L034, M-0005/M-0012, G-0004, C-LEG-0003/C-LEG-0008 | Deadload time-freeze is a historical user report. Membership, hand-slot assignment, perk save/revert, and timer cleanup are separate mechanisms. |
| EV-0080–EV-0081 | Observer completeness and engine-to-player validation reports → CL-L035 | Source/protocol documentation only; older target and ABI are unverified and no native bridge handshake occurred. |
| EV-0082–EV-0086 | Scripted permanent effect, packaged Papyrus, enchanting craft callback/Staff Enchanter, and CC MGEF refresh reports → CL-L030, CL-L036, CL-L038–CL-L040, M-0003/M-0006/M-0007 | Blades is a fixed intended writer; literal BSA scan does not rule out dynamic strings. Enchanting routes remain static and inaccessible/unreproduced. |
| EV-0087–EV-0092 | Enchanting base cap, Karstaag cast-power list, disenchant row/instance handling, and legacy “confirmed” status labels → CL-L041–CL-L046, M-0014/M-0015, C-LEG-0009/C-LEG-0010 | Native list membership or stale UI state does not prove a usable extra cast or permanent effect. Old source status labels are contradicted by the missing recipe, delivery, or raw XP artifacts. |
| EV-0093–EV-0099 | Empty-keyword scan, Jarrin/classification boundary, CC duration scan, non-finite timer, ENIT flags, zero-duration ingredient, and deferred Dispel reports → CL-L047–CL-L053, M-0003/M-0004/M-0012, C-LEG-0008 | Historical static scans and edge-case reports; zero-duration still reaches cleanup, and no ordinary non-finite timer writer or alchemy Dispel caller was found in the examined scope. |
| EV-0100–EV-0105 | Direct spell writer inventory, self-poison/Blizzard, fixed poison gas/reflection, Shalidor scrolls, and deadload user brief → CL-L054–CL-L059, M-0005/M-0013/M-0015 | Static and user-report boundaries remain distinct; none establishes a useful extra cast, arbitrary self-poison route, or functional deadload payload. |
| EV-0106–EV-0108 | Hazard cause/owner analysis, poison-consumption and duration route, corrected quest-gate inventory → CL-L060–CL-L062, M-0008, Q-0001/Q-0006/Q-0013 | Player-created hazards retain their player cause in the static path; the Waterbreathing candidate is separate from Fortify Destruction; level conditions are gates to trace, not bypasses. |
| EV-0001–EV-0055 | Earlier root summaries, selected P0 diagnostics, experiment results, and source-context records; source mappings in `legacy_evidence_ids.json` | All remain historical evidence; the first-party claims and each report's build/source limits are described in the claim ledger. |
| EXP-0001–0005 and EXP-0007 | All 32 source Markdown files are preserved under [`legacy_experiments/`](legacy_experiments/README.md); six result files also have evidence IDs and 26 supporting/protocol files are archival source documents. | Historical protocols/results, not current test authorization. No EXP-0006 source document was found. |
| Private/path-bearing material | Four source rows are privacy-excluded or not copied; only relative source paths and hashes appear in the ledger. | No private conversation text, community quote, author, channel, message ID, or machine-specific absolute path is present in tracked research. |
| Generated/binary/raw tool assets | Kept in the read-only source checkout or ignored local data; selected artifacts may be hash-referenced. | File presence does not establish a current build/runtime result. |

The ledger resolves all 242 candidate rows with zero `review_pending` entries. Disposition counts are 108 imported legacy evidence, 44 migrated canonical, 35 archived source document, 24 historical-only, 11 duplicate-with-unique-details-merged, 7 exact duplicates, 9 retired instructions, and 4 privacy exclusions. The evidence mapping contains 108 unique source paths; final validation will recheck source hashes and internal links.

Final manifest/hash and internal-link checks are recorded in the current
`LOCAL_SETUP_CHECKLIST.md` and `LOCAL_SETUP_REPORT.md`. See
[`LEGACY_SOURCE_INDEX.md`](LEGACY_SOURCE_INDEX.md) for the grouped map and the
ledger for each source file's final disposition.
