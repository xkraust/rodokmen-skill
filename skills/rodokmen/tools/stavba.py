#!/usr/bin/env python3
"""Sestavení webu mimo synchronizovanou složku (Google Disk, OneDrive, Dropbox, iCloud).

Leží-li projekt ve složce, kterou synchronizuje cloud, `npm` ve `web/` by tam založilo desetitisíce souborů
(node_modules, dist, .astro, …) a synchronizace by se zahltila nebo skončila chybou (červený křížek u složky).
Odkazy (junction, symlink) na složky mimo Disk nepomůžou: Disk Google je neumí přeskočit a hlásí u nich chybu.

Proto tenhle nástroj projekt zrcadlí do  ~/projekt-rodokmen/<projekt>/stavba/  (jen zdroje: data, výřezy, nástroje,
web bez buildu) a `npm` spustí tam. Build, závislosti a vše, co generuje `npm run data`, vznikne jen v zrcadle
a na Disk se nedostane. Cesta se odvozuje z domovské složky, takže funguje na každém počítači (PC i laptop),
i když je tam jiné uživatelské jméno. Každý počítač má své zrcadlo; mezi počítači se přenáší jen projekt na Disku.

Projekt mimo cloud: příkaz se spustí přímo ve `web/` (stejně jako dřív `cd web && npm …`).

Použití (z kořene projektu; na Windows `python -I -X utf8`, jinde `python3 -I`):
  python3 -I tools/stavba.py run nahled               # = cd web && npm run nahled
  python3 -I tools/stavba.py run nasadit-cloudflare   # = cd web && npm run nasadit-cloudflare
  python3 -I tools/stavba.py install                  # = cd web && npm install
  python3 -I tools/stavba.py --kde                    # vypíše, kde se web staví, a zkontroluje web/
  python3 -I tools/stavba.py --uklid                  # odstraní z web/ na Disku odkazy a build složky
                                                      # (obsah přesune do zrcadla, nic nemaže)
Volby: --zrcadlo <složka> (jiné místo zrcadla; také proměnná RODOKMEN_STAVBA), --na-miste (stavět ve web/,
i když projekt leží v cloudu), --v-cloudu (zrcadlit, i když cloud nepoznám podle cesty).
Závislosti (`npm install`) doinstaluje sám, chybí-li nebo změnil-li se package-lock.json.
"""
import hashlib, json, os, shutil, stat, subprocess, sys, unicodedata

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
CLOUD = ("Google Drive", "GoogleDrive", "Můj disk", "My Drive", "OneDrive", "Dropbox", "iCloud", "Mobile Documents",
         "CloudStorage")

# Co se do zrcadla nekopíruje: historie, pracovní soubory a vše, co vyrábí npm a `npm run data` (to vznikne v zrcadle).
# Cesty relativně ke kořeni projektu, oddělovač „/“. V zrcadle se tyto cesty nikdy nemažou.
VYNECHAT = {
    ".git", ".skill_sablona", "pracovni", ".claude",
    "web/node_modules", "web/dist", "web/.astro", "web/.netlify", "web/.wrangler",
    "web/src/data/site.json", "web/src/generated", "web/public/img", "web/public/zdroje",
    "web/public/prihlaseni.html", "web/nginx.conf", "web/netlify/edge-functions", "web/cloudflare/worker.js",
    "web/wrangler.jsonc",
}
VYNECHAT_JMENA = {"__pycache__", "desktop.ini", "Thumbs.db", ".DS_Store", ".stavba.json"}
BUILD = ("node_modules", "dist", ".astro", ".netlify", ".wrangler")   # složky ve web/, které na Disk nepatří
STAV = ".stavba.json"   # v zrcadle: otisk package-lock.json při poslední instalaci


def vynechat(rel, jmeno):
    return (rel in VYNECHAT or jmeno in VYNECHAT_JMENA or jmeno.startswith(".tmp.drive")
            or jmeno.startswith("~$") or jmeno.endswith(".tar.gz"))


def je_odkaz(p):
    """Symlink nebo junction (Windows). os.path.islink junction nepozná (do Pythonu 3.12)."""
    if os.path.islink(p):
        return True
    if hasattr(os.path, "isjunction") and os.path.isjunction(p):
        return True
    try:
        return bool(os.lstat(p).st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except (AttributeError, OSError):
        return False


def v_cloudu(cesta):
    c = os.path.realpath(cesta).casefold()
    return any(m.casefold() in c for m in CLOUD)


def ascii_jmeno(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode() or "projekt"


def zrcadlo_cesta(argv):
    # realpath: na Windows převede krátká jména (TOM~1) na plná – Vite/Astro by se v nich ztratil
    if "--zrcadlo" in argv:
        return os.path.realpath(argv[argv.index("--zrcadlo") + 1])
    if os.environ.get("RODOKMEN_STAVBA"):
        return os.path.realpath(os.environ["RODOKMEN_STAVBA"])
    return os.path.join(os.path.realpath(os.path.expanduser("~")), "projekt-rodokmen",
                        ascii_jmeno(os.path.basename(ROOT)), "stavba")


def zrcadlit(zdroj, cil):
    """Jednosměrně zkopíruje projekt do zrcadla (jen změněné soubory) a smaže v zrcadle, co ze zdroje zmizelo.
    Vynechané cesty (build, generované soubory) v zrcadle zůstanou. Odkazy ve zdroji přeskočí (nenásleduje je)."""
    zkop = smaz = 0
    for adr, slozky, soubory in os.walk(zdroj):
        rel_adr = os.path.relpath(adr, zdroj).replace(os.sep, "/")
        rel_adr = "" if rel_adr == "." else rel_adr + "/"
        cil_adr = os.path.join(cil, rel_adr)
        os.makedirs(cil_adr, exist_ok=True)
        slozky[:] = [d for d in slozky
                     if not vynechat(rel_adr + d, d) and not je_odkaz(os.path.join(adr, d))]
        soubory = [f for f in soubory if not vynechat(rel_adr + f, f) and not je_odkaz(os.path.join(adr, f))]
        for f in soubory:
            s, c = os.path.join(adr, f), os.path.join(cil_adr, f)
            ss = os.stat(s)
            try:
                cs = os.stat(c)
                stejny = cs.st_size == ss.st_size and int(cs.st_mtime) == int(ss.st_mtime)
            except OSError:
                stejny = False
            if not stejny:
                shutil.copy2(s, c)
                zkop += 1
        # co v zrcadle přebývá (a není vynechané), smazat
        drzet = set(slozky) | set(soubory)
        for jm in os.listdir(cil_adr):
            if jm not in drzet:
                smaz += smaz_krome(os.path.join(cil_adr, jm), rel_adr + jm)
    return zkop, smaz


def smaz_krome(p, rel):
    """Smaže položku zrcadla, která ve zdroji není – kromě vynechaných cest (i uvnitř: web/src/data/ vzniká
    jen v zrcadle a drží generovaný site.json)."""
    if vynechat(rel, os.path.basename(rel)):
        return 0
    if os.path.isdir(p) and not je_odkaz(p):
        if any(v.startswith(rel + "/") for v in VYNECHAT):
            n = sum(smaz_krome(os.path.join(p, jm), rel + "/" + jm) for jm in os.listdir(p))
            if not os.listdir(p):
                os.rmdir(p)
            return n
        shutil.rmtree(p)
    else:
        os.remove(p)
    return 1


def kontrola_webu(cil_web, uklid):
    """Najde ve web/ na Disku build složky a odkazy. S uklid je odstraní: odkaz smaže (cíl zůstane) a jeho obsah,
    stejně jako skutečnou složku, přesune do zrcadla – jen když tam ještě není (nic nepřepíše ani nesmaže)."""
    web = os.path.join(ROOT, "web")
    problem = 0
    for n in BUILD:
        p = os.path.join(web, n)
        if not os.path.lexists(p):
            continue
        odkaz = je_odkaz(p)
        druh = "odkaz (junction/symlink)" if odkaz else "složka"
        if not uklid:
            print(f"POZOR: web/{n} je na Disku ({druh}) – Disk ho nesynchronizuje dobře. Spusť tools/stavba.py --uklid.")
            problem += 1
            continue
        c = os.path.join(cil_web, n)
        if odkaz:
            cil_odkazu = os.path.realpath(p)
            # Windows: junction i symlink na složku maže rmdir (jen odkaz, cíl zůstane); jinde unlink
            (os.rmdir if os.name == "nt" and os.path.isdir(p) else os.unlink)(p)
            if os.path.isdir(cil_odkazu) and not os.path.exists(c):
                os.makedirs(cil_web, exist_ok=True)
                shutil.move(cil_odkazu, c)
                print(f"web/{n}: odkaz odstraněn, obsah přesunut z {cil_odkazu} do {c}")
            else:
                print(f"web/{n}: odkaz odstraněn (cíl {cil_odkazu} zůstal beze změny)")
        elif not os.path.exists(c):
            os.makedirs(cil_web, exist_ok=True)
            shutil.move(p, c)
            print(f"web/{n}: složka přesunuta z Disku do {c}")
        else:
            print(f"POZOR: web/{n} je na Disku i v zrcadle ({c}) – nic nepřesouvám, rozhodni ručně "
                  f"(obsah buildu jde vždy vyrobit znovu).")
            problem += 1
    return problem


def otisk(p):
    try:
        return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except OSError:
        return ""


def npm(args, cwd):
    exe = shutil.which("npm")
    if not exe:
        sys.exit("CHYBA: npm nenalezeno – nainstaluj Node.js LTS (https://nodejs.org) a spusť znovu.")
    print(f"> npm {' '.join(args)}   (ve {cwd})", flush=True)
    return subprocess.run([exe, *args], cwd=cwd).returncode


def main(argv):
    volby = {"--kde", "--uklid", "--na-miste", "--v-cloudu"}
    zrc = zrcadlo_cesta(argv)
    npm_args = [a for i, a in enumerate(argv)
                if a not in volby and a != "--zrcadlo" and not (i and argv[i - 1] == "--zrcadlo")]
    mimo = "--na-miste" not in argv and ("--v-cloudu" in argv or bool(os.environ.get("RODOKMEN_STAVBA"))
                                         or "--zrcadlo" in argv or v_cloudu(ROOT))
    if not os.path.isfile(os.path.join(ROOT, "web", "package.json")):
        sys.exit(f"CHYBA: {ROOT} nevypadá jako projekt rodokmenu (chybí web/package.json).")
    cil_web = os.path.join(zrc, "web")

    if "--kde" in argv or "--uklid" in argv:
        print(f"Projekt: {ROOT}")
        print(f"Web se staví: {cil_web if mimo else os.path.join(ROOT, 'web')}"
              + ("  (projekt je v synchronizované složce)" if mimo else ""))
        p = kontrola_webu(cil_web, "--uklid" in argv)
        print("web/ na Disku je v pořádku." if not p else f"Nevyřešeno: {p}.")
        return 1 if p else 0

    if not mimo:
        return npm(npm_args, os.path.join(ROOT, "web")) if npm_args else 0

    kontrola_webu(cil_web, False)   # jen upozorní, build v zrcadle tím netrpí
    print(f"Zrcadlím projekt do {zrc} …", flush=True)
    zkop, smaz = zrcadlit(ROOT, zrc)
    print(f"Zrcadlo aktuální (zkopírováno {zkop}, smazáno {smaz}).", flush=True)
    if not npm_args:
        return 0

    stav_p = os.path.join(zrc, STAV)
    try:
        stav = json.load(open(stav_p, encoding="utf-8"))
    except (OSError, ValueError):
        stav = {}
    # Otisk package.json + package-lock.json z projektu (ne ze zrcadla – tam ho npm install může přepsat
    # a příští zrcadlení vrátí verzi z projektu; to nemá znamenat novou instalaci).
    zdroj_web = os.path.join(ROOT, "web")
    otisk_zdroje = otisk(os.path.join(zdroj_web, "package.json")) + otisk(os.path.join(zdroj_web, "package-lock.json"))
    instalace = npm_args[0] in ("install", "i", "ci")
    if not instalace and (not os.path.isdir(os.path.join(cil_web, "node_modules")) or stav.get("lock") != otisk_zdroje):
        if npm(["install", "--no-audit", "--no-fund"], cil_web) != 0:
            return 1
        stav["lock"] = otisk_zdroje
        json.dump(stav, open(stav_p, "w", encoding="utf-8"))
    kod = npm(npm_args, cil_web)
    if instalace and kod == 0:
        # vědomá instalace (třeba nového balíčku) mění package.json/lock – ty patří do projektu (a gitu)
        for f in ("package.json", "package-lock.json"):
            if otisk(os.path.join(cil_web, f)) != otisk(os.path.join(zdroj_web, f)):
                shutil.copy2(os.path.join(cil_web, f), os.path.join(zdroj_web, f))
                print(f"web/{f} se změnil – zkopírován zpět do projektu.")
        stav["lock"] = otisk(os.path.join(zdroj_web, "package.json")) + otisk(os.path.join(zdroj_web, "package-lock.json"))
        json.dump(stav, open(stav_p, "w", encoding="utf-8"))
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
