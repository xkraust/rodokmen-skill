#!/usr/bin/env python3
"""Fulltext v digitální knihovně Kramerius (API v5): Národní knihovna ČR, s --armada vojenská knihovna MO.

Použití:
  kramerius.py [--armada] 'SOLR_DOTAZ' [počet]       hledá ve stránkách; u nálezu vypíše odkaz do prohlížeče
  kramerius.py [--armada] --text <uuid|odkaz>        celý OCR text stránky
  kramerius.py [--armada] --snimek <uuid|odkaz> <soubor.jpg>   stáhne snímek stránky (existující soubor nepřepíše)

Příklady:
  kramerius.py 'text_ocr:"Jan Novák" AND datum_begin:[1860 TO 1920]'
  kramerius.py --armada 'text_ocr:"Nowak Johann 1885"~15'      seznamy ztrát, vojenské matriky (reference/portaly.md)

--armada = kramerius.army.cz (Digitální studovna Ministerstva obrany ČR; vojáci, hlavně 1. světová válka)."""
import json, os, re, sys, urllib.error, urllib.parse, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import slusne  # noqa: E402,F401 – brzda proti zablokování archivem (společný limit dotazů, tools/slusne.py)

NKP = "https://kramerius5.nkp.cz"
ARMADA = "https://kramerius.army.cz"


def stahni(url):
    """Obsah adresy. Neveřejné nebo chybějící dílo skončí srozumitelnou hláškou místo výpisu výjimky."""
    try:
        with urllib.request.urlopen(url, timeout=90) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 403:
            sys.exit("Dílo není veřejně dostupné (licence) – jde číst jen v badatelně knihovny.")
        if e.code == 404:
            sys.exit("Nenalezeno (HTTP 404): špatné uuid, jiná knihovna (--armada?), nebo stránka nemá text či snímek.")
        sys.exit(f"Knihovna vrátila chybu HTTP {e.code}: {url}")
    except urllib.error.URLError as e:
        sys.exit(f"Knihovna neodpovídá ({e.reason}) – zkus to později.")


def uuid_stranky(zadani):
    """uuid stránky z holého uuid, „uuid:…“ nebo z odkazu do prohlížeče (rozhoduje poslední uuid – to je za page=)."""
    if "@" in zadani:
        sys.exit("Stránka uvnitř PDF dokumentu (uuid@číslo) samostatný text ani snímek nemá – otevři dokument v prohlížeči.")
    nalez = re.findall(r"[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}", zadani)
    if not nalez:
        sys.exit(f"Tohle není uuid stránky ani odkaz s ním: {zadani}")
    return "uuid:" + nalez[-1].lower()


def odkaz(base, doc):
    """Odkaz do prohlížeče: /view/<nadřazený objekt>?page=<stránka>. Adresa /search/handle/… v prohlížeči nefunguje,
    ačkoli server odpoví 200 (ověřeno 26. 11. 2026)."""
    pid = doc["PID"]
    if "@" in pid:   # strana uvnitř PDF
        dok, strana = pid.split("@", 1)
        return f"{base}/view/{dok}  (strana {strana} v PDF)"
    rodic = doc.get("parent_pid") or []
    rodic = rodic if isinstance(rodic, str) else (rodic[0] if rodic else None)
    return f"{base}/view/{rodic}?page={pid}" if rodic and rodic != pid else f"{base}/view/{pid}"


def hledej(base, dotaz, pocet):
    p = {"q": f"({dotaz}) AND fedora.model:page",   # závorky: OR v dotazu nesmí obejít omezení na stránky
         "fl": "PID,parent_pid,root_title,root_pid,datum_str,details,dostupnost", "rows": pocet, "wt": "json",
         "hl": "true", "hl.fl": "text_ocr", "hl.fragsize": "250", "hl.snippets": "3"}
    d = json.loads(stahni(base + "/search/api/v5.0/search?" + urllib.parse.urlencode(p)))
    print("found", d["response"]["numFound"])
    hl = d.get("highlighting", {})
    for x in d["response"]["docs"]:
        det = x.get("details")
        det = " ".join(" ".join(det if isinstance(det, list) else [str(det or "")]).replace("##", " ").split())
        print("-", x.get("datum_str"), "|", str(x.get("root_title"))[:60], "|", det, "|", x["PID"], "|", x.get("dostupnost"))
        print("   ", odkaz(base, x))
        h = " ".join(" | ".join(hl.get(x["PID"], {}).get("text_ocr", [])).split())[:400]
        if h:
            print("   ", h)
    if not d["response"]["numFound"] and "datum_begin" in dotaz and base == ARMADA:
        print("Pozn.: seznamy ztrát nemají datum_begin – zkus dotaz bez omezení na roky.")


def text(base, zadani):
    pid = uuid_stranky(zadani)
    print(stahni(f"{base}/search/api/v5.0/item/{pid}/streams/TEXT_OCR").decode("utf-8-sig", "replace"))


def snimek(base, zadani, soubor):
    pid = uuid_stranky(zadani)
    if os.path.exists(soubor):
        sys.exit(f"Soubor už existuje, nepřepisuji: {soubor}")
    data = stahni(f"{base}/search/img?pid={pid}&stream=IMG_FULL&action=GETRAW")
    pripona = ".jpg" if data[:2] == b"\xff\xd8" else ".png" if data[:8] == b"\x89PNG\r\n\x1a\n" else None
    if not pripona:
        sys.exit("Knihovna nevrátila obrázek JPEG ani PNG (jiný formát nebo chybová stránka) – otevři stránku v prohlížeči.")
    if os.path.splitext(soubor)[1].lower() not in ((".jpg", ".jpeg") if pripona == ".jpg" else (".png",)):
        sys.exit(f"Snímek je {pripona[1:].upper()} – dej souboru příponu {pripona}: {soubor}")
    os.makedirs(os.path.dirname(os.path.abspath(soubor)), exist_ok=True)
    try:
        with open(soubor, "xb") as f:
            f.write(data)
    except FileExistsError:
        sys.exit(f"Soubor už existuje, nepřepisuji: {soubor}")
    print(f"uloženo: {soubor} ({len(data) // 1024} kB)")


def main(argv):
    base = ARMADA if "--armada" in argv else NKP
    argv = [a for a in argv if a != "--armada"]
    if not argv or argv[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if argv[0] == "--text" and len(argv) == 2:
        return text(base, argv[1])
    if argv[0] == "--snimek" and len(argv) == 3:
        return snimek(base, argv[1], argv[2])
    if argv[0].startswith("--") or len(argv) > 2 or (len(argv) == 2 and not argv[1].isdigit()):
        sys.exit(__doc__)
    hledej(base, argv[0], argv[1] if len(argv) == 2 else "30")


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):   # UTF-8 výstup i na Windows bez -X utf8 (cp1250 neumí třeba „→“)
        if hasattr(_s, "reconfigure"):
            _s.reconfigure(encoding="utf-8", errors="replace")
    main(sys.argv[1:])
