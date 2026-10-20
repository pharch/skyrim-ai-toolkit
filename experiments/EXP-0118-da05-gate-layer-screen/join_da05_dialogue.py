#!/usr/bin/env python3
"""Join official Skyrim.esm DA05 DIAL topics to their group-linked INFO children."""
from __future__ import annotations
import argparse, hashlib, json, mmap, re, struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / ".local/xedit-data/official-ae-v1/Skyrim.esm"
EXPECTED_SHA256 = "2bbc77fdec35a70ef96b710f8c525e50a1db9e63e11a391a0eb9ee8f56d36107"
DA05 = 0x0002A49A
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from tools.plugin_reader import read_plugin

def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def subs(row):
    out={}
    for item in row.get("subrecords",[]): out.setdefault(item["signature"],[]).append(bytes.fromhex(item["value_hex"]))
    return out

def ctda(raw):
    if len(raw)!=32: return {"raw_hex":raw.hex(),"length":len(raw),"decoded":False}
    flags=raw[0]; global_value=bool(flags&4)
    return {"raw_hex":raw.hex(),"type_byte":f"0x{flags:02X}","operator":{0:"=",32:"!=",64:">",96:">=",128:"<",160:"<="}.get(flags&0xF0,"unknown"),"or_flag":bool(flags&1),"use_global":global_value,"comparison_float":struct.unpack_from("<f",raw,4)[0] if not global_value else None,"function_index":struct.unpack_from("<H",raw,8)[0],"param1_u32":struct.unpack_from("<I",raw,12)[0],"param2_u32":struct.unpack_from("<I",raw,16)[0],"run_on":struct.unpack_from("<I",raw,20)[0],"reference_form_id":f"{struct.unpack_from('<I',raw,24)[0]:08X}"}

def group_index(path):
    matched={}; count=0
    def walk(data,start,end,ancestry):
        nonlocal count
        pos=start
        while pos<end:
            if end-pos<24: raise ValueError(f"truncated group/record header at 0x{pos:X}")
            sig,size=struct.unpack_from("<4sI",data,pos)
            if sig==b"GRUP":
                if size<24 or pos+size>end: raise ValueError(f"invalid GRUP boundary at 0x{pos:X}")
                label=data[pos+8:pos+12]
                entry={"type":struct.unpack_from("<I",data,pos+12)[0],"label_hex":label.hex(),"label_form_id":int.from_bytes(label,"little")}
                walk(data,pos+24,pos+size,ancestry+[entry]);pos+=size;continue
            if pos+24+size>end: raise ValueError(f"record exceeds containing group at 0x{pos:X}")
            count+=1; form=struct.unpack_from("<I",data,pos+12)[0]
            if sig==b"INFO":
                owners=[g for g in ancestry if g["type"]==7]
                if owners: matched[form]=owners
            pos+=24+size
    with path.open("rb") as f, mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as data: walk(data,0,len(data),[])
    return matched,count

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    if not SOURCE.is_file(): raise SystemExit("prepared official Skyrim.esm is unavailable")
    out=a.output if a.output.is_absolute() else ROOT/a.output
    if not out.resolve().is_relative_to((ROOT/".local").resolve()): raise SystemExit("capture output must remain under ignored .local/")
    source_hash=digest(SOURCE)
    if source_hash!=EXPECTED_SHA256: raise SystemExit("prepared official Skyrim.esm SHA-256 mismatch")
    dials=list(read_plugin(SOURCE,"DIAL",include_subrecords=True)); topics={}
    for row in dials:
        s=subs(row)
        if not any(len(v)==4 and int.from_bytes(v,"little")==DA05 for v in s.get("QNAM",[])): continue
        fid=int(row["file_form_id"],16)
        topics[fid]={"form_id":row["file_form_id"],"editor_id":row["editor_id"],"topic_type":s.get("SNAM",[b""])[0].decode("ascii","replace"),"tif_count":int.from_bytes(s.get("TIFC",[b"\0"*4])[0],"little"),"record_offset":row["offset"]}
    parents,walked=group_index(SOURCE);infos={};reference_infos={}
    quest_bytes=DA05.to_bytes(4,"little")
    dial_by_id={int(row["file_form_id"],16):row for row in dials}
    for row in read_plugin(SOURCE,"INFO",include_subrecords=True):
        fid=int(row["file_form_id"],16)
        s=subs(row);vmad=s.get("VMAD",[]);names=[]
        for value in vmad: names.extend(re.findall(r"TIF_[A-Za-z0-9_]+",value.decode("latin-1")))
        conditions=[ctda(v) for v in s.get("CTDA",[])]
        owned=any(g["label_form_id"] in topics for g in parents.get(fid,[]))
        references_da05=any(quest_bytes in v for v in [*s.get("CTDA",[]),*vmad])
        if not owned and not references_da05: continue
        info={"form_id":row["file_form_id"],"editor_id":row["editor_id"],"record_offset":row["offset"],"parent_groups":parents.get(fid,[]),"conditions":conditions,"tif_script_name_candidates":sorted(set(names)),"vmad_hex":[v.hex() for v in vmad]}
        if owned: infos[fid]=info
        if references_da05:
            info["dial_parents"]=[]
            for group in info["parent_groups"]:
                dial=dial_by_id.get(group["label_form_id"])
                if dial:
                    ds=subs(dial);qnam=ds.get("QNAM",[b""])[0]
                    info["dial_parents"].append({"form_id":dial["file_form_id"],"editor_id":dial["editor_id"],"quest_form_id":f"{int.from_bytes(qnam,'little'):08X}" if len(qnam)==4 else None})
            reference_infos[fid]=info
    for tid,topic in topics.items(): topic["infos"]=[infos[i] for i in sorted(infos) if tid in {g["label_form_id"] for g in parents[i]}]
    for fid,topic in topics.items():
        topic["infos"]=[infos[i] for i in sorted(infos) if fid in {g["label_form_id"] for g in parents.get(i,[])}]
    levels=[{"topic":t["form_id"],"info":i["form_id"],"condition":c} for t in topics.values() for i in t["infos"] for c in i["conditions"] if c.get("function_index")==80]
    ref_levels=[{"info":i["form_id"],"dial_parents":i["dial_parents"],"condition":c} for i in reference_infos.values() for c in i["conditions"] if c.get("function_index")==80]
    result={"source_plugin":"Skyrim.esm","source_sha256":source_hash,"parser":"tools.plugin_reader.read_plugin plus full GRUP ancestry walk","source_scope":"prepared official Skyrim.esm; not a winning-record/profile query","main_quest":"0002A49A DA05","records_walked":walked,"dials_read":len(dials),"da05_dial_count":len(topics),"da05_info_count":len(infos),"linked_getlevel_condition_count":len(levels),"linked_getlevel_conditions":levels,"all_direct_da05_info_reference_count":len(reference_infos),"all_direct_da05_info_references":[reference_infos[k] for k in sorted(reference_infos)],"da05_owned_topics":[topics[k] for k in sorted(topics)]}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    names=sorted({n for i in [*infos.values(),*reference_infos.values()] for n in i["tif_script_name_candidates"]})
    print(json.dumps({"source_sha256":source_hash,"records_walked":walked,"dials_read":len(dials),"da05_dial_count":len(topics),"da05_info_count":len(infos),"linked_getlevel_condition_count":len(levels),"all_direct_da05_info_reference_count":len(reference_infos),"linked_script_names":names,"output":out.relative_to(ROOT).as_posix()},indent=2))
if __name__=="__main__": main()
