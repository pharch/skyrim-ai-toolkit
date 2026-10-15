#!/usr/bin/env python3
"""Check repository Markdown links and retired setup references."""
from __future__ import annotations
import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={".git", ".local", ".venv", ".pytest_cache", "__pycache__", "node_modules", "build", "dist"}
SKIP_FILES={"session_prompt.md", "config/LOCAL_TOOL_HANDOFF.private.md"}
RETIRED=re.compile(r"(?:migration/|session-brief/|glitch-hunting-setup|NEXT_SESSION_HANDOFF\.md|LOCAL_TOOL_HANDOFF\.md|LOCAL_TOOL_BINDINGS\.md|CODEX_START_PROMPT\.md|FINAL_HARNESS_CLOSEOUT_MISSION)",re.I)
LINK_RE=re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+[^)]*)?\)")

def markdown_files(root:Path=ROOT)->list[Path]:
    result=[]
    for directory,children,names in os.walk(root,topdown=True):
        children[:]=sorted(n for n in children if n not in SKIP_DIRS)
        for name in names:
            if name.lower().endswith((".md",".mdx")):
                path=Path(directory)/name
                if path.relative_to(root).as_posix() not in SKIP_FILES:
                    result.append(path)
    return sorted(result,key=lambda p:p.relative_to(root).as_posix().casefold())

def audit(root:Path=ROOT)->tuple[list[str],int]:
    errors=[]
    files=markdown_files(root)
    for path in files:
        relative=path.relative_to(root).as_posix()
        text=path.read_text(encoding="utf-8",errors="replace")
        for line_no,line in enumerate(text.splitlines(),1):
            if RETIRED.search(line): errors.append(f"{relative}:{line_no}: retired setup reference")
        text=re.sub(r"```.*?```|~~~.*?~~~","",text,flags=re.S)
        for target in LINK_RE.findall(text):
            parsed=urlparse(target)
            if parsed.scheme or target.startswith("#"): continue
            cleaned=unquote(target.split("#",1)[0].split("?",1)[0])
            if not cleaned: continue
            candidates=((path.parent/cleaned).resolve(),(root/cleaned).resolve())
            if not any(candidate.exists() for candidate in candidates): errors.append(f"{relative}: broken internal link {target}")
    return errors,len(files)

def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true",required=True)
    parser.parse_args(argv)
    errors,count=audit()
    print(f"Markdown links and lifecycle references: {count} files; " + ("PASS" if not errors else "FAIL"))
    for error in errors: print(error,file=sys.stderr)
    return 1 if errors else 0

if __name__=="__main__": raise SystemExit(main())
