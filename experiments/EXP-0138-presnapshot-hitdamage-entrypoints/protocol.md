# EXP-0138 protocol

## Static source phase

1. Read CommonLibSSE commit `b93280e832f263dbef44e44cbe2936622a02f91a` for the exact EntryPoint selector names. Treat enum names as source labels, not runtime proof.
2. Parse the five official masters read-only and preserve their SHA-256 hashes. Count all PERK entry-point DATA rows before filtering to the nine selectors observed upstream of the HitData `+0x54` snapshot. Preserve `DATA[1]`, `EPFT`, `EPFD`, raw CTDAs, FormIDs, and plugin origin.
3. Scan exact little-endian FormID bytes for the four non-positive rows across source subrecords. Classify matches as candidate references only; do not infer semantic ownership from byte occurrences. Use native xEdit for Deft Movement field decoding.
4. Preserve the existing GOG evidence for selector-`0x24` call order, the `+0x50` to `+0x54` copy, and the PlayerCharacter positive-points guard. Do not transfer GOG addresses to Steam.
5. Preserve the local UESP page title, revision, timestamp, URL, and raw hash as secondary grounding. Do not use it as a substitute for records or runtime evidence.

## Rival models and decisions

- A zeroing pre-snapshot row should be visible in the complete selector screen and should lower the copied `+0x54` value before the Player UseSkill guard.
- If zero rows are only attached to non-player actors/effects, the Player route is narrowed; a raw FormID byte match alone cannot distinguish attachment.
- Even a Player-applicable zero row does not meet OBJ-2 unless the level-one sequence produces a qualifying hit, worn armor independently supplies measurable protection, and Heavy/Light skill progress remains unchanged across repeated trials.

## Runtime lane (not run)

EV-0260 remains the required exact-target/full-order, clean-save, read-only-observer discriminator. Any eventual test records exact skill/perk state, armor pieces and keywords, every hit, protection against a no-armor control, raw AVSK before/after, Block progress, and character-level preservation. Do not use console stage/level forcing, injected scripts, or altered plugins as vanilla validation.

## Scope

No plugin, archive, save, co-save, or game state was modified. Source scope is the five official masters; no profile-specific winner or Creation Club coverage is claimed. Raw outputs stay under ignored `.local/` and are hashed in the transaction manifest.
