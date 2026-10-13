#!/usr/bin/env python3
"""Local DiscordChatExporter JSON (or JSONL) -> provenance-preserving SQLite FTS5.
No network calls, no upload; raw export stays outside tracked Git. Requires Python SQLite FTS5.
"""
import argparse, json, sqlite3
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument('export',type=Path,help='Locally authorized Discord export JSON/JSONL')
ap.add_argument('--db',type=Path,default=Path('research/apocrypha-index.sqlite'))
args=ap.parse_args()
raw=args.export.read_text(encoding='utf-8-sig')
if args.export.suffix.lower()=='.jsonl':
    rows=[json.loads(x) for x in raw.splitlines() if x.strip()]
    meta={}
else:
    dat=json.loads(raw)
    meta=dat if isinstance(dat,dict) else {}
    rows=dat.get('messages',[]) if isinstance(dat,dict) else dat
if not isinstance(rows,list): raise SystemExit('Expected JSON messages array or JSONL')
channel=meta.get('channel') or {}
channel_id=channel.get('id','unknown') if isinstance(channel,dict) else str(channel)
args.db.parent.mkdir(parents=True,exist_ok=True)
con=sqlite3.connect(str(args.db))
con.executescript('''CREATE TABLE IF NOT EXISTS messages(message_key TEXT PRIMARY KEY, message_id TEXT, channel TEXT, timestamp TEXT, author TEXT, content TEXT, source TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS message_fts USING fts5(content, message_key UNINDEXED, tokenize='unicode61');''')
with con:
    n=0
    for i,r in enumerate(rows):
        mid=str(r.get('id') or f'row-{i}')
        c=str(r.get('content',''))
        ch=r.get('channelId') or channel_id
        ch=str(ch)
        a=r.get('author') or {}
        author=str((a.get('name') or a.get('id') or 'unknown') if isinstance(a,dict) else a)
        ts=str(r.get('timestamp') or r.get('timestampEdited') or '')
        key=f'{args.export.name}:{ch}:{mid}'
        con.execute('INSERT OR REPLACE INTO messages VALUES (?,?,?,?,?,?,?)',(key,mid,ch,ts,author,c,str(args.export)))
        n+=1
    con.execute('DELETE FROM message_fts')
    con.execute('INSERT INTO message_fts(content,message_key) SELECT content,message_key FROM messages')
con.close()
print(f'Indexed {n} messages into {args.db} (private, local only).')
