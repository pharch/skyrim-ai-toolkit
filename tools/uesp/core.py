"""Streaming MediaWiki dump importer and local citation/search interface.

Raw wikitext and the site's namespace map are retained. The cleaned text is a
search aid only; templates are stored separately and never treated as expanded
facts. The database is built beside its destination and atomically renamed.
"""

from __future__ import annotations

import argparse
import bz2
import gzip
import hashlib
import html
import json
import os
import re
import sqlite3
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import BinaryIO, Iterator
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
LOCAL_ROOT = (ROOT / ".local").resolve()

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE namespaces (namespace_id INTEGER PRIMARY KEY, name TEXT NOT NULL, key TEXT);
CREATE TABLE pages (
  row_id INTEGER PRIMARY KEY,
  page_id INTEGER,
  namespace_id INTEGER NOT NULL,
  title TEXT NOT NULL,
  revision_id INTEGER,
  timestamp TEXT,
  redirect_title TEXT,
  raw_wikitext TEXT NOT NULL,
  readable_text TEXT NOT NULL,
  UNIQUE(namespace_id, title),
  UNIQUE(page_id)
);
CREATE INDEX pages_title ON pages(title COLLATE NOCASE);
CREATE INDEX pages_namespace ON pages(namespace_id);
CREATE TABLE page_categories (page_row INTEGER NOT NULL REFERENCES pages(row_id), category TEXT NOT NULL);
CREATE INDEX category_lookup ON page_categories(category COLLATE NOCASE);
CREATE TABLE page_links (page_row INTEGER NOT NULL REFERENCES pages(row_id), target TEXT NOT NULL);
CREATE INDEX link_lookup ON page_links(target COLLATE NOCASE);
CREATE TABLE templates (
  page_row INTEGER NOT NULL REFERENCES pages(row_id),
  ordinal INTEGER NOT NULL,
  name TEXT NOT NULL,
  parameters_json TEXT NOT NULL,
  raw_invocation TEXT NOT NULL,
  PRIMARY KEY(page_row, ordinal)
);
CREATE VIRTUAL TABLE page_fts USING fts5(title, readable_text, raw_wikitext, content='');
"""


class CorpusError(RuntimeError):
    """Raised when a source dump or index violates its data contract."""


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _open_dump(path: Path) -> BinaryIO:
    suffix = path.name.lower()
    if suffix.endswith(".bz2"):
        return bz2.open(path, "rb")
    if suffix.endswith(".gz"):
        return gzip.open(path, "rb")
    return path.open("rb")


def _child_text(parent: ET.Element, name: str) -> str | None:
    for child in parent:
        if _local(child.tag) == name:
            return child.text
    return None


def _siteinfo(elem: ET.Element) -> tuple[dict[str, str], dict[int, tuple[str, str | None]]]:
    info: dict[str, str] = {}
    namespaces: dict[int, tuple[str, str | None]] = {}
    for child in elem.iter():
        tag = _local(child.tag)
        if tag in {"sitename", "dbname", "base", "generator", "case"} and child.text:
            info[tag] = child.text
        elif tag == "namespace":
            try:
                ns_id = int(child.attrib["key"])
            except (KeyError, ValueError):
                continue
            namespaces[ns_id] = (child.text or "", child.attrib.get("canonical"))
    if not namespaces:
        raise CorpusError("dump siteinfo has no namespace declarations")
    return info, namespaces


def _page(elem: ET.Element) -> dict[str, object]:
    title = _child_text(elem, "title")
    namespace = _child_text(elem, "ns")
    page_id_text = _child_text(elem, "id")
    if title is None or namespace is None:
        raise CorpusError("page is missing title or namespace")
    revision_id = None
    timestamp = None
    wikitext = ""
    for child in elem:
        if _local(child.tag) != "revision":
            continue
        rid = _child_text(child, "id")
        stamp = _child_text(child, "timestamp")
        revision_id = int(rid) if rid and rid.isdigit() else None
        timestamp = stamp
        for node in child.iter():
            if _local(node.tag) == "text":
                wikitext = node.text or ""
                break
        break
    redirect = next((child.attrib.get("title") for child in elem if _local(child.tag) == "redirect"), None)
    try:
        page_id = int(page_id_text) if page_id_text else None
        namespace_id = int(namespace)
    except ValueError as exc:
        raise CorpusError(f"invalid page id/namespace for {title!r}") from exc
    return {
        "page_id": page_id,
        "namespace_id": namespace_id,
        "title": title,
        "revision_id": revision_id,
        "timestamp": timestamp,
        "redirect_title": redirect,
        "raw_wikitext": wikitext,
    }


def _iter_dump(path: Path) -> Iterator[tuple[dict[str, str], dict[int, tuple[str, str | None]], dict[str, object]]]:
    with _open_dump(path) as stream:
        context = ET.iterparse(stream, events=("start", "end"))
        try:
            _event, root = next(context)
        except StopIteration as exc:
            raise CorpusError("empty XML dump") from exc
        info: dict[str, str] = {}
        namespaces: dict[int, tuple[str, str | None]] = {}
        siteinfo_seen = False
        for event, elem in context:
            if event != "end":
                continue
            tag = _local(elem.tag)
            if tag == "siteinfo":
                info, namespaces = _siteinfo(elem)
                siteinfo_seen = True
                root.clear()
            elif tag == "page":
                if not siteinfo_seen:
                    raise CorpusError("page appeared before siteinfo")
                yield info, namespaces, _page(elem)
                elem.clear()
                root.clear()
        if not siteinfo_seen:
            raise CorpusError("dump is missing siteinfo")


def _split_top_level(text: str, delimiter: str = "|") -> list[str]:
    out: list[str] = []
    depth = 0
    start = 0
    i = 0
    while i < len(text):
        if text.startswith("{{", i):
            depth += 1
            i += 2
        elif text.startswith("}}", i) and depth:
            depth -= 1
            i += 2
        elif text[i] == delimiter and depth == 0:
            out.append(text[start:i])
            start = i + 1
            i += 1
        else:
            i += 1
    out.append(text[start:])
    return out


def _templates(text: str) -> Iterator[tuple[str, dict[str, str], str]]:
    stack: list[int] = []
    i = 0
    ordinal = 0
    while i < len(text) - 1:
        if text.startswith("{{", i):
            stack.append(i)
            i += 2
            continue
        if text.startswith("}}", i) and stack:
            start = stack.pop()
            end = i + 2
            raw = text[start:end]
            body = text[start + 2:i]
            fields = _split_top_level(body)
            name = fields[0].strip() if fields else ""
            params: dict[str, str] = {}
            positional = 1
            for field in fields[1:]:
                pair = _split_top_level(field, "=")
                if len(pair) > 1:
                    params[pair[0].strip()] = "=".join(pair[1:]).strip()
                else:
                    params[str(positional)] = field.strip()
                    positional += 1
            if name:
                ordinal += 1
                yield name, params, raw
            i = end
            continue
        i += 1


def _readable(text: str) -> str:
    value = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    value = re.sub(r"<ref\b[^>]*>.*?</ref\s*>", " ", value, flags=re.I | re.S)
    value = re.sub(r"<ref\b[^>]*/\s*>", " ", value, flags=re.I)
    value = re.sub(r"\{\{.*?\}\}", " ", value, flags=re.S)
    value = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)
    value = re.sub(r"\[https?://\S+\s+([^\]]+)\]", r"\1", value)
    value = re.sub(r"<[^>]+>", " ", value)
    value = re.sub(r"'{2,5}", "", value)
    value = re.sub(r"^\s*[|!{}-]+\s*", " ", value, flags=re.M)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def _namespace_display(namespace_id: int, title: str, namespaces: dict[int, tuple[str, str | None]]) -> str:
    name = namespaces.get(namespace_id, ("", None))[0]
    if not name or title.casefold().startswith(name.casefold() + ":"):
        return title
    return f"{name}:{title}"


def _citation(title: str, revision_id: int | None) -> str:
    url = "https://en.uesp.net/wiki/" + quote(title.replace(" ", "_"), safe="/:()'!,.-_~")
    if revision_id is not None:
        url = "https://en.uesp.net/w/index.php?title=" + quote(title.replace(" ", "_"), safe="/:()'!,.-_~") + f"&oldid={revision_id}"
    return url


def _create_schema(conn: sqlite3.Connection) -> None:
    try:
        conn.executescript(SCHEMA)
    except sqlite3.OperationalError as exc:
        if "fts5" in str(exc).lower():
            raise CorpusError("this Python SQLite build lacks FTS5") from exc
        raise


def ingest(input_path: Path, database: Path, *, rebuild: bool = False, source_url: str | None = None) -> dict[str, object]:
    input_path = input_path.resolve()
    database = database.resolve()
    if not database.is_relative_to(LOCAL_ROOT):
        raise CorpusError("refusing to write a UESP index outside ignored .local/")
    if not input_path.is_file():
        raise CorpusError(f"input file does not exist: {input_path}")
    if database.exists() and not rebuild:
        raise CorpusError(f"index exists; pass --rebuild to replace it: {database}")
    database.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=database.name + ".", suffix=".building", dir=database.parent)
    os.close(fd)
    temp_db = Path(temp_name)
    temp_db.unlink()
    input_hash = hashlib.sha256()
    with input_path.open("rb") as raw:
        for chunk in iter(lambda: raw.read(1024 * 1024), b""):
            input_hash.update(chunk)
    digest = input_hash.hexdigest()
    counts: Counter[int] = Counter()
    title_prefix_counts: Counter[str] = Counter()
    no_text = 0
    duplicates = 0
    parse_errors = 0
    site: dict[str, str] = {}
    namespace_map: dict[int, tuple[str, str | None]] = {}
    conn = sqlite3.connect(temp_db)
    conn.execute("PRAGMA journal_mode=DELETE")
    conn.execute("PRAGMA synchronous=NORMAL")
    _create_schema(conn)
    batch = 0
    try:
        for site, namespace_map, page in _iter_dump(input_path):
            nsid = int(page["namespace_id"])
            title = str(page["title"])
            raw_text = str(page["raw_wikitext"])
            title_prefix = "Skyrim" if title.casefold().startswith("skyrim:") else None
            if title_prefix:
                title_prefix_counts[title_prefix] += 1
            try:
                cur = conn.execute(
                    "INSERT INTO pages(page_id,namespace_id,title,revision_id,timestamp,redirect_title,raw_wikitext,readable_text) VALUES (?,?,?,?,?,?,?,?)",
                    (page["page_id"], nsid, title, page["revision_id"], page["timestamp"], page["redirect_title"], raw_text, _readable(raw_text)),
                )
            except sqlite3.IntegrityError as exc:
                duplicates += 1
                raise CorpusError(f"duplicate page key/id at namespace {nsid}, title {title!r}: {exc}") from exc
            row_id = cur.lastrowid
            counts[nsid] += 1
            if not raw_text.strip():
                no_text += 1
            conn.execute("INSERT INTO page_fts(rowid,title,readable_text,raw_wikitext) VALUES (?,?,?,?)", (row_id, title, _readable(raw_text), raw_text))
            for category in re.findall(r"\[\[\s*Category\s*:\s*([^|\]]+)", raw_text, flags=re.I):
                conn.execute("INSERT INTO page_categories VALUES (?,?)", (row_id, category.strip()))
            for target in re.findall(r"\[\[\s*([^|\]#]+)", raw_text):
                clean = target.strip()
                if clean and not clean.casefold().startswith("category:"):
                    conn.execute("INSERT INTO page_links VALUES (?,?)", (row_id, clean))
            for ordinal, (name, params, invocation) in enumerate(_templates(raw_text), 1):
                conn.execute("INSERT INTO templates VALUES (?,?,?,?,?)", (row_id, ordinal, name, json.dumps(params, ensure_ascii=False), invocation))
            batch += 1
            if batch >= 500:
                conn.commit()
                batch = 0
        if not site or not namespace_map:
            raise CorpusError("source did not yield a MediaWiki siteinfo block")
        for nsid, (name, canonical) in namespace_map.items():
            conn.execute("INSERT INTO namespaces(namespace_id,name,key) VALUES (?,?,?)", (nsid, name, canonical))
        metadata = {
            "source_file_name": input_path.name,
            "source_sha256": digest,
            "source_url": source_url or "unknown; not supplied",
            "imported_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "siteinfo": site,
            "namespace_map": {str(k): {"name": v[0], "canonical": v[1]} for k, v in sorted(namespace_map.items())},
            "namespace_page_counts": {str(k): v for k, v in sorted(counts.items())},
            "skyrim_namespace_id": next((k for k, v in namespace_map.items() if v[0].casefold() == "skyrim"), None),
            "skyrim_namespace_pages": next((n for k, n in counts.items() if namespace_map.get(k, ("", None))[0].casefold() == "skyrim"), 0),
            "skyrim_literal_title_prefix_pages": title_prefix_counts["Skyrim"],
            "total_pages": sum(counts.values()),
            "empty_text_pages": no_text,
            "duplicate_pages": duplicates,
            "parse_errors": parse_errors,
            "source_completeness": "unverified against official dump inventory",
        }
        for key, value in metadata.items():
            conn.execute("INSERT INTO metadata(key,value) VALUES (?,?)", (key, json.dumps(value, ensure_ascii=False)))
        conn.commit()
        conn.execute("INSERT INTO page_fts(page_fts) VALUES ('optimize')")
        conn.commit()
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise CorpusError(f"SQLite integrity check failed: {integrity}")
        conn.close()
        os.replace(temp_db, database)
        return metadata
    except (ET.ParseError, OSError, sqlite3.Error, CorpusError) as exc:
        parse_errors += 1
        try:
            conn.close()
        except sqlite3.Error:
            pass
        for suffix in ("", "-wal", "-shm"):
            try:
                Path(str(temp_db) + suffix).unlink(missing_ok=True)
            except OSError:
                pass
        if isinstance(exc, CorpusError):
            raise
        raise CorpusError(f"import failed ({type(exc).__name__}): {exc}") from exc


def _db(path: Path) -> sqlite3.Connection:
    if not path.is_file():
        raise CorpusError(f"UESP_NOT_INDEXED: database is missing: {path}")
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def _metadata(conn: sqlite3.Connection) -> dict[str, object]:
    return {row["key"]: json.loads(row["value"]) for row in conn.execute("SELECT key,value FROM metadata")}


def _namespace_id(conn: sqlite3.Connection, requested: str) -> tuple[int | None, str | None]:
    row = conn.execute("SELECT namespace_id,name FROM namespaces WHERE name=? COLLATE NOCASE", (requested,)).fetchone()
    if row:
        return int(row["namespace_id"]), None
    return None, requested.casefold() + ":%"


def _fts_query(query: str) -> str:
    terms = re.findall(r"[^\W_]+", query, flags=re.UNICODE)
    if not terms:
        raise CorpusError("search query has no searchable words")
    return " AND ".join('"' + term.replace('"', '""') + '"' for term in terms)


def _full_title(conn: sqlite3.Connection, namespace_id: int, title: str) -> str:
    row = conn.execute("SELECT name FROM namespaces WHERE namespace_id=?", (namespace_id,)).fetchone()
    name = row["name"] if row else ""
    return _namespace_display(namespace_id, title, {namespace_id: (name, None)})


def _find_page_row(conn: sqlite3.Connection, title: str) -> sqlite3.Row | None:
    normalized = title.replace("_", " ")
    if ":" in title:
        prefix, remainder = title.split(":", 1)
        namespace_id, _ = _namespace_id(conn, prefix)
        if namespace_id is not None:
            # MediaWiki dumps commonly keep the namespace prefix inside <title>,
            # even though <ns> also carries its numeric namespace ID. Older
            # fixtures and exports may store only the title remainder.
            candidates = dict.fromkeys((remainder.replace("_", " "), normalized))
            for candidate in candidates:
                row = conn.execute(
                    "SELECT * FROM pages WHERE namespace_id=? AND title=? COLLATE NOCASE",
                    (namespace_id, candidate),
                ).fetchone()
                if row is not None:
                    return row
            return None
    return conn.execute(
        "SELECT * FROM pages WHERE title=? COLLATE NOCASE ORDER BY namespace_id LIMIT 1",
        (normalized,),
    ).fetchone()


def search(database: Path, query: str, *, namespace: str | None = None, limit: int = 10) -> list[dict[str, object]]:
    conn = _db(database)
    try:
        expr = _fts_query(query)
        sql = "SELECT p.row_id,p.page_id,p.namespace_id,p.title,p.revision_id,p.timestamp,p.redirect_title,bm25(page_fts) AS rank FROM page_fts JOIN pages p ON p.row_id=page_fts.rowid WHERE page_fts MATCH ?"
        args: list[object] = [expr]
        if namespace:
            nsid, prefix = _namespace_id(conn, namespace)
            if nsid is not None:
                sql += " AND p.namespace_id=?"
                args.append(nsid)
            else:
                sql += " AND lower(p.title) LIKE ?"
                args.append(prefix)
        sql += " ORDER BY rank LIMIT ?"
        args.append(max(1, min(limit, 100)))
        rows = conn.execute(sql, args).fetchall()
        result = []
        for row in rows:
            title = _full_title(conn, row["namespace_id"], row["title"])
            result.append({"title": title, "page_id": row["page_id"], "namespace_id": row["namespace_id"], "revision_id": row["revision_id"], "timestamp": row["timestamp"], "redirect": row["redirect_title"], "url": _citation(title, row["revision_id"])})
        return result
    except sqlite3.Error as exc:
        raise CorpusError(f"search failed: {exc}") from exc
    finally:
        conn.close()


def page(database: Path, title: str, *, raw: bool = False) -> dict[str, object]:
    conn = _db(database)
    try:
        row = _find_page_row(conn, title)
        if row is None:
            raise CorpusError(f"page not found: {title}")
        full = _full_title(conn, row["namespace_id"], row["title"])
        result = {"title": full, "page_id": row["page_id"], "namespace_id": row["namespace_id"], "revision_id": row["revision_id"], "timestamp": row["timestamp"], "redirect": row["redirect_title"], "url": _citation(full, row["revision_id"]), "content": row["raw_wikitext"] if raw else row["readable_text"], "content_type": "wikitext" if raw else "search-cleaned text"}
        return result
    finally:
        conn.close()


def related(database: Path, title: str) -> dict[str, object]:
    content = page(database, title, raw=True)
    conn = _db(database)
    try:
        row = _find_page_row(conn, title)
        if row is None:
            return {"page": content, "categories": [], "links": []}
        return {"page": content, "categories": [r[0] for r in conn.execute("SELECT category FROM page_categories WHERE page_row=? ORDER BY category", (row[0],))], "links": [r[0] for r in conn.execute("SELECT target FROM page_links WHERE page_row=? ORDER BY target LIMIT 100", (row[0],))]}
    finally:
        conn.close()


def stats(database: Path) -> dict[str, object]:
    conn = _db(database)
    try:
        meta = _metadata(conn)
        counts = {str(r["name"] or "<main>"): int(r["n"]) for r in conn.execute("SELECT n.name,COUNT(p.row_id) n FROM namespaces n LEFT JOIN pages p USING(namespace_id) GROUP BY n.namespace_id ORDER BY n.namespace_id")}
        fts_rows = conn.execute("SELECT count(*) FROM page_fts").fetchone()[0]
        return {"source_file_name": meta.get("source_file_name"), "source_sha256": meta.get("source_sha256"), "siteinfo": meta.get("siteinfo"), "total_pages": meta.get("total_pages"), "namespace_page_counts": counts, "skyrim_namespace_id": meta.get("skyrim_namespace_id"), "skyrim_namespace_pages": meta.get("skyrim_namespace_pages"), "skyrim_literal_title_prefix_pages": meta.get("skyrim_literal_title_prefix_pages"), "empty_text_pages": meta.get("empty_text_pages"), "duplicate_pages": meta.get("duplicate_pages"), "parse_errors": meta.get("parse_errors"), "fts_rows": fts_rows, "source_completeness": meta.get("source_completeness")}
    finally:
        conn.close()


def doctor(database: Path) -> dict[str, object]:
    report = stats(database)
    conn = _db(database)
    try:
        sample = conn.execute("SELECT title,namespace_id,revision_id FROM pages WHERE namespace_id=? ORDER BY title LIMIT 1", (report.get("skyrim_namespace_id"),)).fetchone()
        report["has_skyrim_namespace"] = bool(report.get("skyrim_namespace_id") is not None and report.get("skyrim_namespace_pages", 0) > 0)
        report["sample_skyrim_page"] = dict(sample) if sample else None
        report["completeness_warning"] = "A nonempty Skyrim namespace proves presence, not dump completeness; compare against an official inventory before claiming a complete UESP mirror."
        report["fts5_search"] = bool(search(database, "Skyrim", namespace="Skyrim", limit=1))
        return report
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import/search an offline UESP MediaWiki export")
    subs = parser.add_subparsers(dest="command", required=True)
    p_ingest = subs.add_parser("ingest")
    p_ingest.add_argument("--input", required=True, type=Path)
    p_ingest.add_argument("--db", required=True, type=Path)
    p_ingest.add_argument("--source-url")
    p_ingest.add_argument("--rebuild", action="store_true")
    p_stats = subs.add_parser("stats")
    p_stats.add_argument("--db", required=True, type=Path)
    p_search = subs.add_parser("search")
    p_search.add_argument("--db", required=True, type=Path)
    p_search.add_argument("--ns")
    p_search.add_argument("--limit", type=int, default=10)
    p_search.add_argument("query")
    p_page = subs.add_parser("page")
    p_page.add_argument("--db", required=True, type=Path)
    p_page.add_argument("--raw", action="store_true")
    p_page.add_argument("title")
    p_source = subs.add_parser("source")
    p_source.add_argument("--db", required=True, type=Path)
    p_source.add_argument("title")
    p_related = subs.add_parser("related")
    p_related.add_argument("--db", required=True, type=Path)
    p_related.add_argument("title")
    p_doctor = subs.add_parser("doctor")
    p_doctor.add_argument("--db", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "ingest":
            result = ingest(args.input, args.db, rebuild=args.rebuild, source_url=args.source_url)
        elif args.command == "stats":
            result = stats(args.db)
        elif args.command == "search":
            result = search(args.db, args.query, namespace=args.ns, limit=args.limit)
        elif args.command == "page":
            result = page(args.db, args.title, raw=args.raw)
        elif args.command == "source":
            item = page(args.db, args.title, raw=False)
            result = {key: item[key] for key in ("title", "revision_id", "timestamp", "url")}
        elif args.command == "related":
            result = related(args.db, args.title)
        else:
            result = doctor(args.db)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (CorpusError, OSError, sqlite3.Error, ET.ParseError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
