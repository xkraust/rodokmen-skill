"""Test sčítání lidu v portafontium.py (scitani, domy, info/link/svazek pro dům) – offline na uložených stránkách.

Z kořene repozitáře:
  python3 -I tests/portafontium/test_scitani.py skills/rodokmen/tools
Na archiv nechodí: get() se nahradí uloženými stránkami portálu (scitani_*.html, stav 12. 11. 2026):
přehled /contents/census, soudní okres Plánice 1880 a 1921, dům Zbyslav čp. 43 (1921, /iipimage/34443948).
Ostatní roky okresu vrací prázdnou stránku (obec v nich „není“).
"""
import contextlib, io, json, os, shutil, sys, tempfile

TOOLS = os.path.abspath(sys.argv[1])
TU = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, TOOLS)
sys.argv = sys.argv[:1] + ["x"]   # portafontium.py bez argumentů vypíše nápovědu a skončí
import portafontium as pf  # noqa: E402

vysledky = []


def check(nazev, ok, detail=""):
    vysledky.append(bool(ok))
    print(f"[{'OK ' if ok else 'CHYBA'}] {nazev}{'' if ok else '  ' + str(detail)[:600]}", flush=True)


def stranka(n):
    return open(os.path.join(TU, n), encoding="utf-8").read()


ADRESY = []
STRANKY = {"/contents/census": "scitani_prehled.html",
           "/census/soap-kt/1880/okres-planice": "scitani_planice_1880.html",
           "/census/soap-kt/1921/okres-planice": "scitani_planice_1921.html",
           "/iipimage/34443948": "scitani_dum_34443948.html"}


def fake_get(url, binary=False):
    ADRESY.append(url)
    return stranka(STRANKY[url]) if url in STRANKY else "<html>/census/ prázdná stránka okresu</html>"


def vystup(f, *a):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        f(*a)
    return out.getvalue()


tmp = tempfile.mkdtemp()
try:
    pf.get = fake_get
    pf.CACHE = os.path.join(tmp, "cache")
    pf.ROOT = tmp
    os.makedirs(os.path.join(tmp, "data"))

    prehled = pf.scitani_prehled()
    okresy = {(a, o): r for a, o, r in prehled}
    check("přehled: 32 soudních okresů", len(prehled) == 32, len(prehled))
    check("přehled: Plánice 1880–1921", okresy.get(("soap-kt", "okres-planice")) == [1880, 1890, 1900, 1910, 1921],
          okresy.get(("soap-kt", "okres-planice")))
    check("přehled: Domažlice od 1857", okresy.get(("soap-do", "okres-domazlice"), [0])[0] == 1857)

    obce = pf.scitani_okres("soap-kt", 1921, "okres-planice")
    zby = [x for x in obce if x[0].startswith("Zbyslav")]
    check("okres 1921: Zbyslav 46 domů, první dům 34443905", zby == [("Zbyslav (Zbyslaw)", 46, "34443905", "")], zby)
    check("okres 1921: německá část stránky se nezdvojí", len([x for x in obce if x[0].startswith("Zbyslav")]) == 1)
    obce80 = pf.scitani_okres("soap-kt", 1880, "okres-planice")
    jen_souhrn = [x for x in obce80 if x[0].startswith("Ústaleč") and not x[2]]
    check("okres 1880: obec jen se souhrnem (Ústaleč)", jen_souhrn and jen_souhrn[0][3] == "34441350", jen_souhrn)

    check("shoda názvu: osada jiné obce", pf._sedi("Újezd u Plánice - Zbyslav (Aujezd - Zbyslaw)", "zbyslav"))
    check("shoda názvu: německý název", pf._sedi("Zbyslav (Zbyslaw)", "Zbyslaw"))
    check("shoda názvu: jen celé slovo", not pf._sedi("Zbyslavice (X)", "Zbyslav"))

    ADRESY.clear()
    t = vystup(pf.scitani, "Zbyslav", "Plánice")
    check("hledání s okresem: jen stránky okresu Plánice", all("planice" in u for u in ADRESY), ADRESY)
    check("hledání: 1880 jako osada Újezdu", "1880 | Újezd u Plánice - Zbyslav (Aujezd - Zbyslaw) | 42 domů | 34441229" in t, t)
    check("hledání: 1921", "1921 | Zbyslav (Zbyslaw) | 46 domů | 34443905" in t, t)
    check("hledání: hlásí roky okresu bez obce", "1890, 1900, 1910" in t, t)

    t = vystup(pf.domy, "34443948")
    check("domy: čp. 43 je aktuální stránka", "čp. 43 | 34443948" in t, t)
    check("domy: další archy domu (8_0001_1)", "čp. 8_0001_1 | 34443913" in t, t)
    check("domy: čp. 40 chybí", "čp. 40 |" not in t, t)
    radky = [r.split(" |")[0] for r in t.splitlines() if r.startswith("čp.")]
    check("domy: řazení podle čísla", radky.index("čp. 9") < radky.index("čp. 10") < radky.index("čp. 43"), radky[:12])
    check("domy: tentýž dům v jiných letech", "Tentýž dům (čp. 43) v jiných letech: 1900 -> 34443904" in t, t)

    k, f, s, l = pf.info("34443948")
    check("info: název a okres", f.get("Název") == "Census 1921 Zbyslav (Zbyslaw), Nr. 43"
          and f.get("Okres") == "Politický okres: Klatovy, Soudní okres: Plánice", f)
    check("info: 3 snímky", len(s) == 3, s)
    check("link: snímek 2", pf.BASE + pf.scan("34443948", 2)[3]
          == "https://www.portafontium.eu/iipimage/34443948/soap-kt_01159_census-1921-zbyslav-cp043_0020")

    vystup(pf.svazek, "34443948")
    sv = json.load(open(os.path.join(tmp, "data", "svazky.json"), encoding="utf-8"))["pf_34443948"]
    check("svazek: archiv SOkA Klatovy", sv["archiv"] == "SOkA Klatovy – sčítací operáty", sv)
    check("svazek: název s čp.", sv["svazek"] == "Sčítání lidu 1921 Zbyslav (Zbyslaw), čp. 43", sv)
    check("svazek: adresa domu", sv["url"] == "https://www.portafontium.eu/iipimage/34443948", sv)

    ADRESY.clear()
    pf.scitani_okres("soap-kt", 1921, "okres-planice")
    check("stránky okresu jsou v mezipaměti", ADRESY == [], ADRESY)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(vysledky)} z {len(vysledky)} správně")
sys.exit(0 if all(vysledky) else 1)
