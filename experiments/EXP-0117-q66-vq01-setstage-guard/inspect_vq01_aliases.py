#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TSV = ROOT / ".local/xedit-authoritative-copy/out/xedit/20261017T224439.768640Z/native-records.tsv"
rows = list(csv.reader(TSV.open(encoding="utf-8"), delimiter="\t"))
aliases = {}
functions = []
for row in rows:
    if len(row) < 7 or row[1] != "0200352A" or row[2] != "DLC1VQ01" or row[3] != "QUST":
        continue
    path, value = row[5], row[6]
    match = re.search(r"\\10:Aliases\\(\d+):Alias", path)
    if not match:
        if "\\10:Aliases" in path and path.endswith(":Function"):
            functions.append(value)
        continue
    index = int(match.group(1))
    entry = aliases.setdefault(index, {"index": index, "name": None, "optional": False, "fill_sources": []})
    if "ALID - Alias Name" in path:
        entry["name"] = value
    elif "Flags\\0:Optional" in path:
        entry["optional"] = (value == "1")
    elif any(field in path for field in ("ALFR - Forced Reference", "ALFL - Specific Location", "ALUA - Unique Actor", "ALRA - Reference Alias", "ALST - Location Alias ID", "ALEQ - Quest", "ALEA - Alias")):
        entry["fill_sources"].append({"field": path.rsplit("\\", 1)[-1], "value": value})
result = {
    "source": "preserved native xEdit five-official-master QUST export for Dawnguard.esm DLC1VQ01 0200352A (EV-0326)",
    "native_records_tsv_sha256": hashlib.sha256(TSV.read_bytes()).hexdigest(),
    "alias_count": len(aliases),
    "alias_condition_function_count": len(functions),
    "alias_condition_functions": functions,
    "aliases": [aliases[index] for index in sorted(aliases)],
}
out = ROOT / "experiments/EXP-0117-q66-vq01-setstage-guard/q66-vq01-alias-summary.json"
out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps(result, indent=2, ensure_ascii=False))
