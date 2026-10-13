#!/usr/bin/env python3
"""FTS lookup of local, authorized MediaWiki dump with title/revision provenance."""
import argparse,sqlite3,json
ap=argparse.ArgumentParser()
ap.add_argument('query');ap.add_argument('--db',default='research/uesp-cache/uesp.sqlite')
ap.add_argument('--limit',type=int,default=12);ap.add_argument('--full-page',action='store_true')
a=ap.parse_args()
con=sqlite3.connect(a.db);con.row_factory=sqlite3.Row
if a.full_page:
    rows=con.execute('SELECT title,page_id,revision_id,updated_at,wikitext,source_dump FROM wiki_pages WHERE title=?',(a.query,)).fetchall()
else:
    rows=con.execute('''SELECT p.title,p.page_id,p.revision_id,p.updated_at,p.source_dump,
    snippet(wiki_fts,1,'[',']','...',20) AS snippet FROM wiki_fts
    JOIN wiki_pages p ON p.title=wiki_fts.title
    WHERE wiki_fts MATCH ? ORDER BY bm25(wiki_fts) LIMIT ?''',(a.query,max(1,min(50,a.limit)))).fetchall()
print(json.dumps([dict(x) for x in rows],indent=2,ensure_ascii=False))
