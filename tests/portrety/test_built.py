"""Kontrola portrétů ve skutečně sestaveném webu.

python -I -X utf8 tests/portrety/test_built.py <projekt>/web
Předem spusťte npm run data a npm run build v daném ukázkovém projektu.
"""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.stack, self.portraits, self.documents = [], [], []
        self.has_portrait = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = {c for _, a in self.stack for c in (a.get("class") or "").split()}
        if "has-portrait" in (attrs.get("class") or "").split():
            self.has_portrait = True
        if tag == "img":
            if "person-portrait" in classes:
                link = next(a["href"] for t, a in reversed(self.stack) if t == "a")
                assert "person-intro" in classes, "Portrét není v záhlaví osoby"
                self.portraits.append((attrs, link))
            if "docs" in classes:
                self.documents.append(unquote(urlsplit(attrs["src"]).path))
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append((tag, attrs))

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break


def main():
    web = Path(sys.argv[1])
    site = json.loads((web / "src/data/site.json").read_text(encoding="utf-8"))
    count = 0
    for p in site["people"].values():
        page = Page((web / "dist/osoba" / p["slug"] / "index.html").read_text(encoding="utf-8"))
        portrait = p.get("portrait")
        assert page.has_portrait == bool(portrait), p["slug"]
        assert len(page.portraits) == (1 if portrait else 0), p["slug"]
        assert page.documents == [f"/img/{d['img']}.jpg" for d in p["docs"]], p["slug"]
        if portrait:
            count += 1
            img, href = page.portraits[0]
            assert img["alt"] == f"Portrét: {p['name']}", p["slug"]
            assert unquote(img["src"]) == f"/img/{portrait['img']}.jpg", p["slug"]
            assert unquote(href) == f"/{'zdroje' if portrait['full'] else 'img'}/{portrait['img']}.jpg", p["slug"]
            for url in (img["src"], href):
                assert (web / "dist" / unquote(url).lstrip("/")).is_file(), url
            assert unquote(img["src"]) not in page.documents
    story = Page((web / "dist/pribehy/index.html").read_text(encoding="utf-8"))
    assert story.documents == [f"/img/{d['img']}.jpg" for d in site["docs"]]
    print(f"OK: {len(site['people'])} stránek osob, {count} portréty, odkazy na obrázky a obě galerie.")


if __name__ == "__main__":
    main()
