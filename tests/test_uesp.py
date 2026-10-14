from __future__ import annotations

import bz2
import json
import tempfile
import unittest
from pathlib import Path

from tools.uesp.core import CorpusError, doctor, ingest, page, related, search


FIXTURE = b'''<?xml version="1.0" encoding="UTF-8"?>
<mediawiki><siteinfo><sitename>UESPWiki</sitename><dbname>uesp</dbname>
<base>https://en.uesp.net/wiki/Main_Page</base><generator>MediaWiki 1.31.16</generator>
<namespaces><namespace key="0"/><namespace key="10">Template</namespace>
<namespace key="134">Skyrim</namespace><namespace key="142">Skyrim Mod</namespace></namespaces></siteinfo>
<page><title>Skyrim:Armor</title><ns>134</ns><id>1</id><revision><id>101</id><timestamp>2026-10-01T00:00:00Z</timestamp>
<text xml:space="preserve">Armor skill experience and [[Skyrim:Quests|quest links]]. {{Infobox|level=20|value={{num|42}}}} [[Category:Combat]]</text></revision></page>
<page><title>Skyrim:Quests</title><ns>134</ns><id>2</id><revision><id>102</id><timestamp>2026-10-02T00:00:00Z</timestamp><text>Quest level requirement.</text></revision></page>
<page><title>Skyrim Mod:Armor Mod</title><ns>142</ns><id>3</id><revision><id>103</id><timestamp>2026-10-03T00:00:00Z</timestamp><text>Armor skill experience.</text></revision></page>
</mediawiki>'''


class UespImportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.xml = self.root / "fixture.xml.bz2"
        self.xml.write_bytes(bz2.compress(FIXTURE))
        self.db = self.root / "index.sqlite3"
        from tools.uesp import core
        self.old_local_root = core.LOCAL_ROOT
        core.LOCAL_ROOT = self.root.resolve()
        self.meta = ingest(self.xml, self.db, source_url="https://example.invalid/fixture")

    def tearDown(self) -> None:
        from tools.uesp import core
        core.LOCAL_ROOT = self.old_local_root
        self.tmp.cleanup()

    def test_custom_namespace_and_search_filter(self) -> None:
        self.assertEqual(self.meta["skyrim_namespace_id"], 134)
        self.assertEqual(self.meta["skyrim_namespace_pages"], 2)
        found = search(self.db, "armor skill experience", namespace="Skyrim")
        self.assertEqual([item["title"] for item in found], ["Skyrim:Armor"])
        self.assertEqual(search(self.db, "armor skill experience", namespace="Skyrim Mod")[0]["title"], "Skyrim Mod:Armor Mod")

    def test_raw_template_parameters_and_citation_survive(self) -> None:
        result = page(self.db, "Skyrim:Armor", raw=True)
        self.assertIn("{{Infobox|level=20|value={{num|42}}}}", result["content"])
        self.assertIn("oldid=101", result["url"])
        self.assertEqual(result["revision_id"], 101)
        relations = related(self.db, "Skyrim:Armor")
        self.assertIn("Combat", relations["categories"])
        self.assertTrue(any(link.endswith("Quests") for link in relations["links"]))

    def test_nested_template_parameter_index_and_doctor_scope(self) -> None:
        report = doctor(self.db)
        self.assertTrue(report["has_skyrim_namespace"])
        self.assertEqual(report["source_completeness"], "unverified against official dump inventory")
        import sqlite3
        with sqlite3.connect(self.db) as conn:
            rows = conn.execute("SELECT name,parameters_json FROM templates ORDER BY ordinal").fetchall()
        self.assertEqual(rows[0][0], "num")
        self.assertIn('"1": "42"', rows[0][1])
        self.assertEqual(rows[1][0], "Infobox")
        self.assertIn('"level": "20"', rows[1][1])

    def test_existing_index_is_not_overwritten_without_rebuild(self) -> None:
        before = self.db.read_bytes()
        with self.assertRaises(CorpusError):
            ingest(self.xml, self.db)
        self.assertEqual(self.db.read_bytes(), before)

    def test_partial_namespace_does_not_claim_completeness(self) -> None:
        self.assertIn("not dump completeness", doctor(self.db)["completeness_warning"])

    def test_refuses_index_write_outside_local_storage(self) -> None:
        from tools.uesp import core
        core.LOCAL_ROOT = (self.root / "allowed").resolve()
        with self.assertRaisesRegex(CorpusError, r"outside ignored \.local/"):
            ingest(self.xml, self.root / "outside.sqlite3")


if __name__ == "__main__":
    unittest.main()
