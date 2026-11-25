"""Test tools/stavba.py: zrcadlení projektu mimo synchronizovanou složku a úklid build složek a odkazů z web/.

Bez npm a bez sítě: zkouší jen zrcadlo (--zrcadlo bez příkazu npm) a --kde/--uklid. Z kořene repozitáře:
  python3 -I tests/stavba/test_stavba.py skills/rodokmen
"""
import os, shutil, subprocess, sys, tempfile

SKILL = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "skills/rodokmen")
vysledky = []


def check(nazev, ok, detail=""):
    vysledky.append(bool(ok))
    print(f"[{'OK ' if ok else 'CHYBA'}] {nazev}{'' if ok else '  ' + str(detail)[:800]}", flush=True)


def zapis(p, text="x"):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


def stavba(projekt, *args):
    return subprocess.run([sys.executable, "-I", "-X", "utf8", os.path.join(projekt, "tools", "stavba.py"), *args],
                          capture_output=True, text=True, cwd=projekt)


tmp = tempfile.mkdtemp()
try:
    projekt = os.path.join(tmp, "Můj disk", "Rodokmen", "Novákovi")
    zrc = os.path.join(tmp, "zrcadlo")
    shutil.copytree(os.path.join(SKILL, "tools"), os.path.join(projekt, "tools"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    zapis(os.path.join(projekt, "web", "package.json"), "{}")
    zapis(os.path.join(projekt, "web", "src", "pages", "index.astro"))
    zapis(os.path.join(projekt, "data", "osoby.py"))
    zapis(os.path.join(projekt, "vyrezy", "a.jpg"))
    zapis(os.path.join(projekt, "pracovni", "velky.bin"))
    zapis(os.path.join(projekt, ".git", "HEAD"))
    zapis(os.path.join(projekt, "web", "public", "img", "stary.jpg"))   # generované – do zrcadla nepatří

    r = stavba(projekt, "--kde")
    check("--kde pozná cloud podle cesty", "synchronizované" in r.stdout and r.returncode == 0, r.stdout + r.stderr)

    r = stavba(projekt, "--zrcadlo", zrc)
    w = os.path.join(zrc, "web")
    check("zrcadlo: zdroje zkopírované", r.returncode == 0 and os.path.isfile(os.path.join(w, "src", "pages", "index.astro"))
          and os.path.isfile(os.path.join(zrc, "data", "osoby.py")), r.stdout + r.stderr)
    check("zrcadlo: bez .git, pracovni a generovaných souborů",
          not os.path.exists(os.path.join(zrc, ".git")) and not os.path.exists(os.path.join(zrc, "pracovni"))
          and not os.path.exists(os.path.join(w, "public", "img")))

    # generované a build v zrcadle přežijí další zrcadlení, smazaný zdroj zmizí
    zapis(os.path.join(w, "src", "data", "site.json"), "{}")
    zapis(os.path.join(w, "node_modules", "astro", "x.js"))
    zapis(os.path.join(w, "src", "data", "smetí.txt"))
    os.remove(os.path.join(projekt, "vyrezy", "a.jpg"))
    r = stavba(projekt, "--zrcadlo", zrc)
    check("zrcadlo: site.json a node_modules zůstanou", os.path.isfile(os.path.join(w, "src", "data", "site.json"))
          and os.path.isfile(os.path.join(w, "node_modules", "astro", "x.js")), r.stdout + r.stderr)
    check("zrcadlo: smazané ve zdroji zmizí", not os.path.exists(os.path.join(zrc, "vyrezy", "a.jpg"))
          and not os.path.exists(os.path.join(w, "src", "data", "smetí.txt")))

    # build složka a odkaz ve web/ na Disku: --kde hlásí, --uklid přesune do zrcadla
    zapis(os.path.join(projekt, "web", "dist", "index.html"))
    venku = os.path.join(tmp, "venku", ".astro")
    zapis(os.path.join(venku, "data.json"))
    odkaz = os.path.join(projekt, "web", ".astro")
    try:
        if os.name == "nt":
            import _winapi
            _winapi.CreateJunction(venku, odkaz)
        else:
            os.symlink(venku, odkaz)
        ma_odkaz = True
    except OSError:
        ma_odkaz = False
    r = stavba(projekt, "--kde", "--zrcadlo", zrc)
    check("--kde hlásí build složku na Disku", r.returncode == 1 and "web/dist" in r.stdout, r.stdout + r.stderr)
    r = stavba(projekt, "--uklid", "--zrcadlo", zrc)
    check("--uklid přesune dist do zrcadla", r.returncode == 0 and not os.path.exists(os.path.join(projekt, "web", "dist"))
          and os.path.isfile(os.path.join(w, "dist", "index.html")), r.stdout + r.stderr)
    if ma_odkaz:
        check("--uklid odstraní odkaz a obsah přesune", not os.path.lexists(odkaz)
              and os.path.isfile(os.path.join(w, ".astro", "data.json")), r.stdout + r.stderr)
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print(f"\n{sum(vysledky)}/{len(vysledky)} v pořádku")
sys.exit(0 if all(vysledky) else 1)
