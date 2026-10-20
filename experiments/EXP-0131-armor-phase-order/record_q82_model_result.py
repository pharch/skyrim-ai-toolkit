#!/usr/bin/env python3
"""Record the scoped Q82 hypothesis result before closing its transaction."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
frontier_path = ROOT / "research" / "FRONTIER.json"
recovery = json.loads((ROOT / "research" / "RECOVERY.json").read_text(encoding="utf-8"))
frontier = json.loads(frontier_path.read_text(encoding="utf-8"))

if recovery.get("status") != "running" or recovery.get("transaction_id") != "TX-20261020-0001" or recovery.get("frontier_id") != "Q-0082":
    raise SystemExit("refusing to update Q82 models outside its active transaction")
item = next((row for row in frontier.get("items", []) if row.get("id") == "Q-0082"), None)
if item is None or item.get("status") != "in_progress":
    raise SystemExit("Q82 is not the active in-progress frontier item")

models = {row["id"]: row for row in item["hypotheses"]}
h1, h2, h3 = models["Q82-H1"], models["Q82-H2"], models["Q82-H3"]
h1["model"] = "Within the captured GOG 1.6.1179.0 HitData path and matching official five-master selector rows, a synchronous callback or player-accessible equipment transition occurs after mitigation but before the worn-ARMO scan, allowing that same hit to avoid AV11/AV12."
h1["status"] = "falsified"
h1["evidence"] = list(dict.fromkeys([*h1.get("evidence", []), "EV-0670", "EV-0671", "EV-0672", "EV-0675", "EV-0676"]))
h2["model"] = "Within the captured GOG 1.6.1179.0 path and matching official five-master selector rows, mitigation, synchronous numeric entrypoint callbacks, worn-ARMO scan, and UseSkill routing execute in the same resolver pass; no player-input or yield point is identified."
h2["status"] = "supported"
h2["evidence"] = list(dict.fromkeys([*h2.get("evidence", []), "EV-0670", "EV-0671", "EV-0672", "EV-0675", "EV-0676"]))
h3["status"] = "supported"
h3["evidence"] = list(dict.fromkeys([*h3.get("evidence", []), "EV-0670", "EV-0673"]))
item["cross_source_assessment"] = (
    "The exact GOG 1.6.1179.0 builder/resolver trace places AV39/armor-factor mitigation before the unblocked receiver's worn-ARMO AV11/AV12 scan in FUN_1406bcaa0; FUN_1406b9df0 is a later separate health/trap continuation [EV-0670], [EV-0673]. "
    "Selectors 0x25/0x27 traverse entrypoint data synchronously [EV-0671]. Across the five official masters, the matching selector DATA rows use EPFT IDs 1/2 [EV-0675], whose captured GOG handlers write/add numeric results [EV-0672]; their typed function-data virtual predicates at +8 remain unresolved. "
    "Thus H1 is falsified only for the captured static scope and H2 is supported there. H3's AV9 blocked routing is a code-branch result, not evidence of positive armor protection or a bounty-qualified zero-XP hit. No Steam equivalence, active-profile winner, live protection/AVSK result, or OBJ-1 causal edge is established; preserve EV-0260."
)
frontier_path.write_text(json.dumps(frontier, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("recorded scoped Q82-H1/H2/H3 result and remaining limits")
