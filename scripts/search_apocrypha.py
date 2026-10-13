#!/usr/bin/env python3
import argparse,sqlite3,json
ap=argparse.ArgumentParser();ap.add_argument('terms');ap.add_argument('--db',default='research/apocrypha-index.sqlite');ap.add_argument('--limit',type=int,default=15);a=ap.parse_args()
con=sqlite3.connect(a.db);con.row_factory=sqlite3.Row
rows=con.execute('SELECT m.message_id,m.channel,m.timestamp,m.author,m.content,m.source FROM message_fts f JOIN messages m ON f.message_key=m.message_key WHERE message_fts MATCH ? ORDER BY bm25(message_fts) LIMIT ?', (a.terms,min(a.limit,100))).fetchall()
print(json.dumps([dict(r) for r in rows],ensure_ascii=False,indent=2))
