# Hypothesis

## H1 — Static armor-XP candidate

In GOG AE 1.6.1179.0, a physical-trap hit uses the shared AV39 and PlayerCharacter cached armor-factor path. The cache visitor accepts Light (BOD2 type 0) and Heavy (type 1), reads their runtime DNAM input, and scales it with actor values. The trap wrapper bypasses the normal resolver's known AV11/AV12 branch and no mapped downstream handler site awards either armor skill.

**Disconfirming observation:** the trap builder omits the cached armor factor, type 0/1 is rejected or contributes no rating, or a reachable trap callback awards AV11/AV12.

## H2 — Protection or award-path failure

The trap path either does not produce effective Light/Heavy protection or still reaches an indirect/derived award path for Heavy/Light Armor.

**Disconfirming observation:** an exact Steam level-one matched hit test shows lower incoming damage with positive landed trap hits and exactly unchanged Heavy/Light AVSK across repeated hits, while an ordinary unblocked positive-damage control advances the appropriate armor skill.

Current static evidence supports H1 as a candidate but does not resolve the Steam/runtime discriminant or all dynamic award descendants.
