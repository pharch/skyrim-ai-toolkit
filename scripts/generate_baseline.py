#!/usr/bin/env python3
"""Report that the former game-install baseline generator is retired."""
import json
import sys

print(json.dumps({
    "ok": False,
    "status": "retired",
    "reason": "game-directory baseline generation is outside this read-only AE research harness",
    "safe_alternative": "scripts/research_safety.py snapshot",
}))
raise SystemExit(2)
