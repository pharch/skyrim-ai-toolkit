#!/usr/bin/env python3
"""Extract zeroing PERK/MGEF records and raw official-master reference candidates."""
from __future__ import annotations
import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin
PLUGINS=("Skyrim.esm","Update.esm","Dawnguard.esm","HearthFires.esm","Dragonborn.esm")
TARGETS={
 "00109639":{"kind":"PERK","plugin":"Skyrim.esm","editor_id":"DragonhideSpellPerk"},
 "0201ED99":{"kind":"PERK","plugin":"Dragonborn.esm","editor_id":"dlc2BBDrunkenMaster"},
 "0201DF9E":{"kind":"PERK","plugin":"Dragonborn.esm","editor_id":"DLC2StandingStoneEarthPerk"},
 "000CDB75":{"kind":"MGEF","plugin":"Skyrim.esm","editor_id":"ArmorFFSelf100"},
 "0201DFA0":{"kind":"MGEF","plugin":"Dragonborn.esm","editor_id":"DLC2StandingStonesEarthEffect"},
}
def sha(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def main():
 cfg=read_local_config(ROOT); raw=cfg.get("SKYRIM_DATA","").strip()
 if not raw: raise SystemExit("SKYRIM_DATA is not bound")
 data=_native_path(raw); needles={fid:bytes.fromhex(fid)[::-1] for fid in TARGETS}
 hashes={};coverage={};matches=[];records={fid:[] for fid in TARGETS}
 for name in PLUGINS:
  path=data/name
  if not path.is_file(): raise SystemExit(f"official master missing: {name}")
  hashes[name]=sha(path);nr=0;ns=0
  for row in read_plugin(path,include_subrecords=True):
   nr+=1;fid=row["file_form_id"].upper()
   if fid in records and name==TARGETS[fid]["plugin"] and row["signature"]==TARGETS[fid]["kind"]:
    records[fid].append({k:row.get(k) for k in ("plugin","origin_plugin","file_form_id","local_form_id","editor_id","flags","offset","subrecords")})
   for sub in row.get("subrecords",[]):
    ns+=1;blob=bytes.fromhex(sub["value_hex"])
    found=[key for key,value in needles.items() if value in blob]
    if found:
     matches.append({"source_plugin":name,"record_signature":row["signature"],"record_form_id":fid,"record_editor_id":row["editor_id"],"subrecord_signature":sub["signature"],"matching_form_ids":found,"subrecord_hex":sub["value_hex"]})
  coverage[name]={"record_count":nr,"subrecord_count":ns}
 missing={fid:len(rows) for fid,rows in records.items() if len(rows)!=1}
 if missing: raise SystemExit(f"exact target record count mismatch: {missing}")
 out={"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"source":"Configured official five masters, read-only direct TES4 parser; exact records plus raw FormID-byte candidates, not semantic reverse references or profile winners","plugin_sha256":hashes,"coverage":coverage,"targets":TARGETS,"records":records,"matching_subrecord_count":len(matches),"matches":matches}
 out_path=ROOT/".local"/"alignment"/"transactions"/"TX-20261020-0008"/"q89"/"zeroing-perk-effect-chain.json"
 out_path.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"artifact":str(out_path.relative_to(ROOT)),"sha256":sha(out_path),"plugin_sha256":hashes,"coverage":coverage,"records":{fid:{"plugin":TARGETS[fid]["plugin"],"signature":TARGETS[fid]["kind"],"editor_id":rows[0]["editor_id"]} for fid,rows in records.items()},"matching_subrecord_count":len(matches),"matches":[{k:v for k,v in row.items() if k!="subrecord_hex"} for row in matches]},indent=2))
 return 0
if __name__=="__main__": raise SystemExit(main())
