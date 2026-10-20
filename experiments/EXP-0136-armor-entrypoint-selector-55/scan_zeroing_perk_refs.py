#!/usr/bin/env python3
"""Screen official five-master raw subrecords for the three zero-valued ModArmorRating perks."""
from __future__ import annotations
import hashlib,json,sys
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))
from scripts.local_config import read_local_config
from tools.ae_target import _native_path
from tools.plugin_reader import read_plugin
PLUGINS=("Skyrim.esm","Update.esm","Dawnguard.esm","HearthFires.esm","Dragonborn.esm")
TARGETS={"00109639":"DragonhideSpellPerk","0201ED99":"dlc2BBDrunkenMaster","0201DF9E":"DLC2StandingStoneEarthPerk"}
def digest(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
 return h.hexdigest()
def main():
 cfg=read_local_config(ROOT)
 raw=cfg.get("SKYRIM_DATA","").strip()
 if not raw: raise SystemExit("SKYRIM_DATA is not bound")
 data=_native_path(raw)
 needles={fid:bytes.fromhex(fid)[::-1] for fid in TARGETS}
 hashes={}; coverage={}; matches=[]
 for name in PLUGINS:
  plugin=data/name
  if not plugin.is_file(): raise SystemExit(f"official master missing: {name}")
  hashes[name]=digest(plugin); records=0; subs=0
  for record in read_plugin(plugin,include_subrecords=True):
   records+=1
   for sub in record.get("subrecords",[]):
    subs+=1; blob=bytes.fromhex(sub["value_hex"])
    found=[fid for fid,needle in needles.items() if needle in blob]
    if found:
     matches.append({"source_plugin":name,"record_signature":record["signature"],"record_form_id":record["file_form_id"],"record_editor_id":record["editor_id"],"subrecord_signature":sub["signature"],"matching_perks":found,"subrecord_hex":sub["value_hex"]})
  coverage[name]={"record_count":records,"subrecord_count":subs}
 artifact={"captured_utc":datetime.now(timezone.utc).isoformat(timespec="seconds"),"source":"Configured official five masters, read-only direct TES4 parser; raw exact FormID-byte candidate scan, not semantic reverse references","plugin_sha256":hashes,"coverage":coverage,"target_perks":TARGETS,"matching_subrecord_count":len(matches),"matches":matches}
 out=ROOT/".local"/"alignment"/"transactions"/"TX-20261020-0008"/"q89"/"zeroing-perk-raw-refs.json"
 out.write_text(json.dumps(artifact,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 print(json.dumps({"artifact":str(out.relative_to(ROOT)),"sha256":digest(out),"plugin_sha256":hashes,"coverage":coverage,"matching_subrecord_count":len(matches),"matches":[{k:v for k,v in m.items() if k!="subrecord_hex"} for m in matches]},indent=2))
 return 0
if __name__=="__main__": raise SystemExit(main())
