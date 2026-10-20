# Competing models

- **Q68-H1:** `GetLevel >= LevelGateTrollCave` is a necessary WE13 start gate, so its script-triggered quest and required aliases cannot run below level 12.
- **Q68-H2:** the predicate gates only one scheduling or alias branch; an independent ordinary location, quest, or encounter path can expose the same content below level 12.
- **Q68-H3:** WE13 is a script-triggered wilderness encounter, but the QUST condition alone does not identify the transition or prove that the player lacks physical access to a cave.

The discriminating evidence is the QUST field placement, Story Manager parent/child path, script owner/call sites, alias-fill source, and any independently reachable encounter/location path. Keep static dispatch evidence separate from clean level-one gameplay.
