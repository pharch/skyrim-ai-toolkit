#!/usr/bin/env python3
"""Index an authorized MediaWiki pages-articles XML/XML.GZ dump with SQLite FTS5.

No downloads. You must obtain lawful/authorized UESP data and follow its
license/attribution and redistribution terms. Store the DB locally, not in Git.
"""
import argparse, gzip, sqlite3, xml.etree.ElementTree as ET
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('dump',type=Path)
ap.add_argument('--db',type=Path,default=Path('research/uesp-cache/uesp.sqlite'))
a=ap.parse_args()
a.db.parent.mkdir(parents=True,exist_ok=True)
con=sqlite3.connect(str(a.db))
con.execute('PRAGMA journal_mode=WAL')
con.executescript('''CREATE TABLE IF NOT EXISTS wiki_pages(title TEXT PRIMARY KEY,page_id TEXT,revision_id TEXT,updated_at TEXT,wikitext TEXT,source_dump TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS wiki_fts USING fts5(title, wikitext, tokenize='unicode61');''')
openfile=gzip.open if a.dump.suffix.lower()=='.gz' else open
n=0
with openfile(a.dump,'rb') as f:
    context=ET.iterparse(f,events=('start','end'))
    _,root=next(context)
    for event,elem in context:
        if event!='end' or elem.tag.rsplit('}',1)[-1] != 'page':continue
        def sub(node,name):
            for x in node:
                if x.tag.rsplit('}',1)[-1]==name:return x
            return None
        title=sub(elem,'title');ns=sub(elem,'ns');pid=sub(elem,'id');rev=sub(elem,'revision')
        if title is not None and (ns is None or ns.text=='0') and rev is not None:
            rid=sub(rev,'id');ts=sub(rev,'timestamp');text=sub(rev,'text')
            if text is not None and text.text:
                titletext=title.text or ''
                con.execute('INSERT OR REPLACE INTO wiki_pages VALUES (?,?,?,?,?,?)',(
                    titletext, pid.text if pid is not None else '', rid.text if rid is not None else '',
                    ts.text if ts is not None else '',text.text,str(a.dump)))
                n+=1
                if n%500==0:
                    con.commit();print(f'Indexed {n} wiki pages',flush=True)
        root.clear()  # Release processed page nodes in a large XML export.
con.commit()
# Rebuild from final canonical pages so incremental re-import doesn't duplicate FTS rows.
con.execute('DELETE FROM wiki_fts')
con.execute('INSERT INTO wiki_fts(title,wikitext) SELECT title,wikitext FROM wiki_pages')
con.commit();con.close()
print(f'Indexed {n} pages from authorized dump into {a.db}')
