#!/usr/bin/env python3
"""Create the ignored local configuration from its portable template once."""
from __future__ import annotations
import argparse
import os
import shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def initialize(root:Path=ROOT)->bool:
    config=root/"config"; example=config/"local.env.example"; local=config/"local.env"
    if local.exists():
        print("Preserving existing local configuration: config/local.env")
        return False
    if not example.is_file(): raise FileNotFoundError("config/local.env.example is missing")
    config.mkdir(parents=True,exist_ok=True)
    with example.open("rb") as source,local.open("xb") as destination: shutil.copyfileobj(source,destination)
    if os.name!="nt": local.chmod(0o600)
    print("Created ignored config/local.env from the blank schema; bind only paths required for the selected tools.")
    return True

def main()->int:
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest="command",required=True)
    sub.add_parser("init",help="create config/local.env without overwriting it")
    args=parser.parse_args()
    if args.command=="init": initialize(); return 0
    return 2
if __name__=="__main__": raise SystemExit(main())
