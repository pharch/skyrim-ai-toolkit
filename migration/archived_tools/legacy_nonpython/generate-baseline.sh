#!/usr/bin/env bash
set -euo pipefail
cat >&2 <<'NOTICE'
This game-install baseline script is retired and performs no file access.
Its former version wrote checksums under a game-directory .claude folder and
included Skyrim VR paths, which are outside this AE research harness.
Use scripts/research_safety.py snapshot only with checkout-relative text files.
NOTICE
exit 2
