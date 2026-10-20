# EXP-0016 protocol

## Competing hypotheses and predicted discriminants

- **H3 — official award-side skill-use modifier:** an official PERK entry point can modify skill-use credit independently from HitData mitigation. Prediction: schema-backed EP22 rows identify the function, amount type, and `EPMagic_IsAdvanceSkill` conditions; this establishes a record-layer award route, not a suppression candidate unless the amount is non-positive and a reachable owner is traced.
- **H4 — no direct skill-advance suppressor in the screened signatures:** the complete five-master MGEF primary-ActorValue and PERK EP22 screens contain no AV117/119/120 MGEF target and no non-positive EP22 multiplier conditioned on AV9/11/12. Prediction: decoded MGEF matches and all EP22 rows show no such suppressor. This does not rule out other MGEF fields/archetypes, other PERK entry points, scripts, native paths, profile overrides, or runtime state.

Primary Q-0004 models remain: H1 predicts protection and armor XP suppression share an inseparable prerequisite; H2 predicts a vanilla-reachable separable condition. EV-0261 supports only GOG source order, where AV39/armor-base-factor mitigation precedes blocked/unblocked receiver routing; it does not establish a candidate or gameplay outcome.

## Target and source scope

- Installed Steam target identity previously verified as AE 1.6.1170.0 (EV-0109). This experiment reads only the five official-master source files and makes no profile-winner claim.
- Exact plugin filenames, SHA-256 values, parser identity, record counts, and raw result hashes must be preserved in the ignored capture referenced by the result evidence entry.
- ActorValue numeric mapping: Block AV9, Heavy Armor AV11, Light Armor AV12, BlockSkillAdvance AV117, HeavyArmorSkillAdvance AV119, LightArmorSkillAdvance AV120. The local CommonLib source declaration and commit must be cited with the scan.

## Read-only procedure

1. Run `python3 scripts/python_env.py run tools/plugin_reader.py doctor` and preserve its output.
2. Use a strict-dispatcher helper to read all MGEF and PERK records from each of the five official masters through `tools.plugin_reader.read_plugin`; capture file SHA-256 and record counts. Keep raw plugin bytes outside the checkout.
3. Decode MGEF primary ActorValue fields only with the preserved CommonLib EffectSetting declaration and versioned mapping already documented in the repository. List exact candidate FormIDs, EditorIDs, file origin and override rows; do not interpret names as runtime behavior.
4. For candidate PERKs, preserve raw effect/condition subrecords and decode only fields with a cited TES5Edit schema or native xEdit export. If no schema-backed direct award writer can be established, report the raw screen as inconclusive for that record field.
5. For every EP22 row conditioned on AV9/11/12, decode the modifier direction and all conditions. If a non-positive candidate appears, trace its exact owner records, conditions, stage/level gates, cleanup and player reachability before proposing runtime work.

## Controls and decision rules

- No plugin, game, save, or profile is modified. No console command, injected effect, altered plugin, or live mutator is used.
- Static screen requires no test save or rollback. Any later live test requires a clean disposable save, complete verified active order for the exact executable, loaded read-only Observer, an unarmored control, qualifying armor control, and raw AVSK/HitData measurements as specified in EXP-0013.
- Support H3 only for an exact schema-decoded entry point, function, amount type, and condition. A positive amount is not a suppression candidate, and no player reachability is inferred without tracing the owner.
- Support H4 only for the explicitly enumerated signatures/fields and verified five official files. No absence claim extends beyond that scope.
- Record any parser errors, missing schemas, unresolved owner routes, and incomplete samples as coverage limitations.
