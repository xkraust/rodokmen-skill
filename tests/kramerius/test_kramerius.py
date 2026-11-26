"""Testy tools/kramerius.py (Národní a vojenská knihovna) – offline, odpovědi knihovny se podvrhnou.

Z kořene repozitáře:
  python3 -I tests/kramerius/test_kramerius.py skills/rodokmen/tools
  (Windows: python -I -X utf8 …)
Všechna data jsou smyšlená.
"""
import contextlib, email.message, io, json, os, shutil, sys, tempfile, urllib.error, urllib.parse, urllib.request

TOOLS = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "skills/rodokmen/tools")
sys.path.insert(0, TOOLS)
os.environ["SLUSNE_STAV"] = tempfile.mkdtemp(prefix="slusne_test_")
import kramerius, slusne  # noqa: E402

vysledky = []


def check(nazev, ok, detail=""):
    vysledky.append(bool(ok))
    print(f"[{'OK ' if ok else 'CHYBA'}] {nazev}{'' if ok else '  ' + str(detail)[:600]}", flush=True)


STRANKA = "uuid:11111111-2222-3333-4444-555555555555"
CISLO = "uuid:aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"
PDF = "uuid:99999999-8888-7777-6666-555555555555"
HLEDANI = {"response": {"numFound": 2, "docs": [
    {"PID": STRANKA, "parent_pid": [CISLO], "root_title": "Verlustliste (smyšlená)", "datum_str": "1.1.1915",
     "details": ["7 \n ##normalPage"], "dostupnost": "public"},
    {"PID": PDF + "@12", "root_title": "Kniha (smyšlená)", "dostupnost": "public"}]},
    "highlighting": {STRANKA: {"text_ocr": ["<em>Nowak</em>\n Johann, Inft."]}}}

VOLANI = []
ODPOVED = {"telo": b""}


class Odpoved(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def fake_urlopen(url, timeout=None):
    VOLANI.append(url)
    telo = ODPOVED["telo"]
    if isinstance(telo, int):
        raise urllib.error.HTTPError(url, telo, "chyba", email.message.Message(), None)
    return Odpoved(telo)


urllib.request.urlopen = fake_urlopen


def spust(argv, telo=b""):
    """Vrátí (výstup, hláška ukončení nebo None)."""
    VOLANI.clear()
    ODPOVED["telo"] = telo
    out, konec = io.StringIO(), None
    with contextlib.redirect_stdout(out):
        try:
            kramerius.main(argv)
        except SystemExit as e:
            konec = str(e.code)
    return out.getvalue(), konec


def parametry():
    return dict(urllib.parse.parse_qsl(urllib.parse.urlsplit(VOLANI[0]).query))


odp = json.dumps(HLEDANI).encode()
out, konec = spust(['text_ocr:"Nowak Johann"'], odp)
check("bez --armada se ptá Národní knihovny", VOLANI[0].startswith("https://kramerius5.nkp.cz/search/api/v5.0/search?"), VOLANI)
check("výchozí počet 30", parametry().get("rows") == "30", parametry())

out, konec = spust(["--armada", 'text_ocr:"Nowak" OR text_ocr:"Novak"', "5"], odp)
check("--armada se ptá vojenské knihovny", VOLANI[0].startswith("https://kramerius.army.cz/search/api/"), VOLANI)
check("dotaz s OR zůstane v závorkách",
      parametry().get("q") == '(text_ocr:"Nowak" OR text_ocr:"Novak") AND fedora.model:page', parametry())
check("počet nálezů z argumentu", parametry().get("rows") == "5", parametry())
check("žádá parent_pid", "parent_pid" in parametry().get("fl", ""), parametry())
check("odkaz z nadřazeného objektu a stránky",
      f"https://kramerius.army.cz/view/{CISLO}?page={STRANKA}" in out, out)
check("žádná adresa /search/handle", "/search/handle" not in out, out)
check("stránka v PDF: odkaz na dokument a číslo strany",
      f"https://kramerius.army.cz/view/{PDF}  (strana 12 v PDF)" in out, out)
check("číslo strany a úryvek na jednom řádku", "7 normalPage" in out and "<em>Nowak</em> Johann" in out, out)

out, konec = spust(["--armada", "text_ocr:Nowak AND datum_begin:[1914 TO 1918]"],
                   json.dumps({"response": {"numFound": 0, "docs": []}}).encode())
check("nic nenalezeno s datum_begin: rada", "nemají datum_begin" in out, out)

out, konec = spust(["--armada", "--text", f"https://kramerius.army.cz/view/{CISLO}?page={STRANKA}"],
                   "﻿Nowak Johann 1880-1915".encode("utf-8"))
check("--text přijme odkaz a vezme uuid stránky", VOLANI[0].endswith(f"/item/{STRANKA}/streams/TEXT_OCR"), VOLANI)
check("--text vypíše OCR bez BOM", out.strip() == "Nowak Johann 1880-1915", repr(out))

tmp = tempfile.mkdtemp(prefix="kramerius_test_")
jpg = os.path.join(tmp, "nova slozka", "strana.jpg")
out, konec = spust(["--armada", "--snimek", STRANKA[5:], jpg], b"\xff\xd8\xff\xe0obrazek")
check("--snimek uloží JPEG (i do nové složky)", konec is None and open(jpg, "rb").read().endswith(b"obrazek"), (out, konec))
check("--snimek žádá IMG_FULL", "stream=IMG_FULL" in VOLANI[0] and STRANKA in VOLANI[0], VOLANI)
out, konec = spust(["--armada", "--snimek", STRANKA, jpg], b"\xff\xd8\xff\xe0jiny")
check("--snimek existující soubor nepřepíše", "nepřepisuji" in str(konec) and open(jpg, "rb").read().endswith(b"obrazek"), konec)
check("--snimek: existující soubor bez dotazu do sítě", not VOLANI, VOLANI)
x = os.path.join(tmp, "x.jpg")
out, konec = spust(["--snimek", STRANKA, x], b"<html>chyba</html>")
check("--snimek odmítne neobrázek a nic nezapíše", "nevrátila obrázek" in str(konec) and not os.path.exists(x), konec)
out, konec = spust(["--snimek", STRANKA, x], b"\x89PNG\r\n\x1a\nobrazek")
check("--snimek hlídá příponu podle formátu", "příponu .png" in str(konec) and not os.path.exists(x), konec)

out, konec = spust(["--armada", "--text", STRANKA], 403)
check("neveřejné dílo: srozumitelná hláška", "není veřejně dostupné" in str(konec), konec)
out, konec = spust(["--armada", "--text", STRANKA], 404)
check("404: srozumitelná hláška", "Nenalezeno" in str(konec), konec)
out, konec = spust(["--armada", "--text", PDF + "@12"])
check("stránka v PDF nemá text: hláška, žádný dotaz", "PDF" in str(konec) and not VOLANI, konec)
out, konec = spust(["--text", "neco"])
check("nesmyslné uuid: hláška, žádný dotaz", "není uuid" in str(konec) and not VOLANI, konec)
for argv in ([], ["--help"], ["--armada"], ["--neznamy"], ["dotaz", "mnoho"], ["--snimek", STRANKA]):
    out, konec = spust(argv)
    check(f"nápověda místo dotazu: {argv}", "Použití:" in str(konec) and not VOLANI, (konec, VOLANI))

for web in ("kramerius.army.cz", "digitalnistudovna.mo.gov.cz"):
    check(f"brzda: 403 neveřejného díla u {web} web nezastaví",
          slusne.KRAMERIUS.search(web) and slusne.KRAMERIUS_DILO.search(f"/search/img?pid={STRANKA}&stream=IMG_FULL"))

shutil.rmtree(tmp, ignore_errors=True)
shutil.rmtree(os.environ["SLUSNE_STAV"], ignore_errors=True)
print(f"\n{sum(vysledky)} z {len(vysledky)} správně")
sys.exit(0 if all(vysledky) else 1)
