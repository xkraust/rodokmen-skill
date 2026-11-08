"""Portréty: export, aliasy, kolize a návrat přejmenování při chybě.

Spuštění: python -I -X utf8 tests/portrety/test_portrety.py
Testy používají pouze dočasná data a standardní knihovnu.
"""
import contextlib
import importlib.util
import io
import json
import os
import shutil
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "skills/rodokmen/tools" / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


export = module("export_web")
zapis = module("zapis")


class Portraits(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="portrety-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.out = io.StringIO()
        self.capture = contextlib.redirect_stdout(self.out)
        self.capture.__enter__()
        self.addCleanup(self.capture.__exit__, None, None, None)

    def file(self, name, content=b"image"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode("utf-8"))
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def document(self, key, people=None):
        return dict(img=key, popis="Rodinná fotografie", osoby=[2] if people is None else people)

    def export(self, docs):
        with patch.object(export, "VYREZY", str(self.root / "vyrezy")), patch.object(export, "ZDROJE", str(self.root / "zdroje")):
            return export.document_lists(docs, {1: "root", 2: "josef", 8: "josef", 3: "anna"})

    def fixture(self):
        self.file("data/dokumenty.json", '[\n {"img": "foto", "popis": "Popis", "osoby": [2], "vlastni": true},\n {"img": "svatba", "osoby": [2, 3]}\n]\n')
        self.file("data/web.json", '{"uvod": {"foto": "foto", "nadpis": "foto"}, "odkaz": "/img/foto.jpg", "prihlaseni": {"odpoved": "foto", "otazka": "/img/foto.jpg"}}\n')
        self.file("data/zvyrazneni.json", '{"foto": {"boxes": [[0, 0, 1, 1]]}}\n')
        self.file("data/pribeh.md", '![Fotka](/img/foto.jpg) [Velká](/zdroje/foto.jpg) /img/foto.jpg.bak\n')
        self.file("data/osoby.py", 'note = "[Fotka](/img/foto.jpg)"\nsource = "vyrezy/foto.jpg"\n')
        self.file("web/src/pages/vlastni.astro", '<img src="/img/foto.jpg" />\n')
        self.file("dokumenty/foto.jpg", b"original")
        for d in ("vyrezy", "zdroje", "web/public/img", "web/public/zdroje"):
            self.file(d + "/foto.jpg", d.encode())

    def test_names(self):
        for name in ("josef_portrét", "PORTRET_1930", "PoRtRéT", "portre\u0301t", "xportrétx"):
            self.assertTrue(export.is_portrait(name), name)
        for name in ("foto", "svatba", "portret/adresa/foto"):
            self.assertFalse(export.is_portrait(name), name)

    def test_aliases_and_galleries(self):
        self.file("vyrezy/josef_PORTRÉT.jpg")
        self.file("zdroje/josef_PORTRÉT.jpg")
        self.file("vyrezy/svatba.jpg")
        docs, portraits, people = self.export([self.document("josef_PORTRÉT", [8, 2]), self.document("svatba", [2, 8, 3])])
        self.assertEqual(list(portraits), ["josef"])
        self.assertTrue(portraits["josef"]["full"])
        self.assertEqual([d["img"] for d in docs], ["svatba"])
        self.assertEqual([d["img"] for d in people["josef"]], ["svatba"])
        self.assertEqual(docs[0]["people"], ["josef", "anna"])

    def test_missing_multiple_and_duplicate_portraits(self):
        for key in ("portret_2", "portret_3"):
            self.file(f"vyrezy/{key}.jpg")
        _, portraits, _ = self.export([self.document(k) for k in ("portret_1", "portret_2", "portret_2", "portret_3")])
        self.assertEqual(portraits["josef"]["img"], "portret_2")
        self.assertFalse(portraits["josef"]["full"])
        self.assertIn("chybí", self.out.getvalue())
        self.assertIn("více portrétů", self.out.getvalue())
        self.assertIn("duplicitní", self.out.getvalue())

    def test_invalid_assignment_is_reported_and_hidden(self):
        self.file("vyrezy/portret.jpg")
        for persons in ([], [999], [2, 999], [2, 3]):
            self.assertEqual(self.export([self.document("portret", persons)]), ([], {}, {}))
        self.assertIn("právě jednu známou osobu", self.out.getvalue())

    def test_no_portrait_and_missing_ordinary_image(self):
        self.assertEqual(self.export([]), ([], {}, {}))
        self.assertEqual(self.export([self.document("foto")]), ([], {}, {}))

    def test_rename_preserves_document_and_updates_all_references(self):
        self.fixture()
        zapis.rename_document(self.root, "foto", "josef_portrét")
        docs = json.loads((self.root / "data/dokumenty.json").read_text(encoding="utf-8"))
        self.assertEqual(docs[0], dict(img="josef_portrét", popis="Popis", osoby=[2], vlastni=True))
        self.assertEqual(len(docs), 2)
        for directory in ("vyrezy", "zdroje", "web/public/img", "web/public/zdroje"):
            self.assertFalse((self.root / directory / "foto.jpg").exists())
            self.assertEqual((self.root / directory / "josef_portrét.jpg").read_bytes(), directory.encode())
        self.assertEqual((self.root / "dokumenty/foto.jpg").read_bytes(), b"original")
        self.assertEqual(json.loads((self.root / "data/web.json").read_text(encoding="utf-8"))["uvod"]["foto"], "josef_portrét")
        cfg = json.loads((self.root / "data/web.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["uvod"]["nadpis"], "foto")
        self.assertEqual(cfg["prihlaseni"], dict(odpoved="foto", otazka="/img/foto.jpg"))
        self.assertIn("josef_portrét", json.loads((self.root / "data/zvyrazneni.json").read_text(encoding="utf-8")))
        for name in ("data/pribeh.md", "data/osoby.py", "web/src/pages/vlastni.astro"):
            self.assertIn("/img/josef_portrét.jpg", unquote((self.root / name).read_text(encoding="utf-8")))
        self.assertIn("/img/foto.jpg.bak", (self.root / "data/pribeh.md").read_text(encoding="utf-8"))
        self.assertIn('source = "vyrezy/josef_portrét.jpg"', (self.root / "data/osoby.py").read_text(encoding="utf-8"))

    def test_preview_changes_nothing(self):
        self.fixture()
        before = self.snapshot()
        zapis.rename_document(self.root, "foto", "portret", preview=True)
        self.assertEqual(self.snapshot(), before)

    def test_collisions_leave_files_unchanged(self):
        self.fixture()
        self.file("web/public/zdroje/PORTRET.jpg")
        before = self.snapshot()
        for target in ("svatba", "portret", "../outside", "NUL", "foto"):
            with self.assertRaises(ValueError, msg=target):
                zapis.rename_document(self.root, "foto", target)
            self.assertEqual(self.snapshot(), before)

    def test_shared_record_and_highlight_collision(self):
        self.fixture()
        self.file("data/zaznamy.json", '[{"klic": "foto"}]')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            zapis.rename_document(self.root, "foto", "portret")
        self.assertEqual(before, self.snapshot())
        self.file("data/zaznamy.json", '[]')
        self.file("data/zvyrazneni.json", '{"foto": {}, "portret": {}}')
        before = self.snapshot()
        with self.assertRaises(ValueError):
            zapis.rename_document(self.root, "foto", "portret")
        self.assertEqual(before, self.snapshot())

    def test_rollback_after_text_write_failure(self):
        self.fixture()
        before = self.snapshot()
        real = zapis._atomic_bytes
        attempts = 0
        def failing(path, data):
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                raise OSError("simulovaná chyba zápisu")
            return real(path, data)
        with patch.object(zapis, "_atomic_bytes", side_effect=failing):
            with self.assertRaises(OSError):
                zapis.rename_document(self.root, "foto", "portret")
        self.assertEqual(self.snapshot(), before)

    def test_rollback_after_image_move_failure(self):
        self.fixture()
        before = self.snapshot()
        real = os.rename
        attempts = 0
        def failing(src, dst):
            nonlocal attempts
            attempts += 1
            if attempts == 2:
                raise OSError("simulovaná chyba přejmenování")
            return real(src, dst)
        with patch.object(zapis.os, "rename", side_effect=failing):
            with self.assertRaises(OSError):
                zapis.rename_document(self.root, "foto", "portret")
        self.assertEqual(self.snapshot(), before)

    def test_encoded_and_escaped_unicode_references(self):
        self.fixture()
        zapis.rename_document(self.root, "foto", "portrét")
        self.file("data/odkaz.md", '/img/portr%C3%A9t.jpg?x=1')
        self.file("data/web.json", '{"uvod": {"foto": "portr\\u00e9t"}, "url": "/img/portr%C3%A9t.jpg"}')
        zapis.rename_document(self.root, "portrét", "foto_nove")
        self.assertEqual((self.root / "data/odkaz.md").read_text(), '/img/foto_nove.jpg?x=1')
        data = json.loads((self.root / "data/web.json").read_text())
        self.assertEqual(data, {"uvod": {"foto": "foto_nove"}, "url": "/img/foto_nove.jpg"})

    def test_filename_matching_schema_field_preserves_highlight_schema(self):
        self.fixture()
        zapis.rename_document(self.root, "foto", "boxes")
        zapis.rename_document(self.root, "boxes", "portret")
        data = json.loads((self.root / "data/zvyrazneni.json").read_text(encoding="utf-8"))
        self.assertEqual(data, {"portret": {"boxes": [[0, 0, 1, 1]]}})

    def test_cli_and_existing_write_modes(self):
        self.fixture()
        script = self.file("tools/zapis.py", (ROOT / "skills/rodokmen/tools/zapis.py").read_bytes())
        def run(*args, input=None):
            result = subprocess.run([sys.executable, "-I", "-X", "utf8", str(script), *args], input=input,
                                    capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            return result
        run("dokumenty", "foto", "-", "--sloucit", input='{"popis": "Nový popis"}')
        run("dokumenty", "foto", "--prejmenovat", "portret", "--nahled")
        run("dokumenty", "foto", "--prejmenovat", "portret")
        docs = json.loads((self.root / "data/dokumenty.json").read_text(encoding="utf-8"))
        self.assertEqual(docs[0]["popis"], "Nový popis")
        self.assertTrue(docs[0]["vlastni"])
        run("dokumenty", "novy", "-", input='{"popis": "Další"}')
        self.assertEqual(len(json.loads((self.root / "data/dokumenty.json").read_text(encoding="utf-8"))), 3)

    def test_complete_export_copies_portrait_and_excludes_it_from_galleries(self):
        def run(script, *args):
            result = subprocess.run([sys.executable, "-I", "-X", "utf8", str(script), *args],
                                    capture_output=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        run(ROOT / "skills/rodokmen/tools/novy_projekt.py", str(self.root), "--ukazka")
        docs = [self.document("chybi_portret"), self.document("Josef_PORTRÉT"), self.document("svatba")]
        self.file("data/dokumenty.json", json.dumps(docs, ensure_ascii=False))
        fixture = ROOT / "skills/rodokmen/template/ukazka_vyrezy/ukazka_krest_jan_novak_1890.jpg"
        for key in ("Josef_PORTRÉT", "svatba"):
            shutil.copyfile(fixture, self.root / "vyrezy" / (key + ".jpg"))
        shutil.copyfile(fixture, self.root / "zdroje/Josef_PORTRÉT.jpg")
        run(self.root / "tools/export_web.py")
        site = json.loads((self.root / "web/src/data/site.json").read_text(encoding="utf-8"))
        person = next(p for p in site["people"].values() if p["k"] == 2)
        self.assertEqual(person["portrait"], dict(img="Josef_PORTRÉT", caption="Rodinná fotografie", full=True))
        self.assertEqual([d["img"] for d in person["docs"]], ["svatba"])
        self.assertEqual([d["img"] for d in site["docs"]], ["svatba"])
        self.assertTrue(all(p["portrait"] is None for p in site["people"].values() if p["k"] != 2))
        for sub in ("img", "zdroje"):
            self.assertEqual((self.root / "web/public" / sub / "Josef_PORTRÉT.jpg").read_bytes(), fixture.read_bytes())


if __name__ == "__main__":
    unittest.main()
