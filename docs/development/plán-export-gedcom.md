# Plán: export rodokmenu do GEDCOM (plugin rodokmen 0.11.2)

## Context
Uživatel se ptal, zda plugin `rodokmen` umí export do GEDCOM. Prověřeno: neumí.
- Nainstalována je jen verze 0.11.2 (`~\.claude\plugins\cache\rodokmen-skill\rodokmen\0.11.2`), jiná verze v cache není.
- GEDCOM se v `tools/` vyskytuje jen v `ged_import.py` (import `.ged`) a `ftb_export.py` (záloha MyHeritage `.ftb` → `.ged`, určený jako vstup pro import).
- `tools/export_web.py` exportuje jen data pro web (JSON do Astro šablony), ne GEDCOM.
- CHANGELOG zmiňuje GEDCOM jen u importu.

## Doporučený postup
Napsat nový nástroj `tools/ged_export.py`, který převede data rodokmenu (`data/osoby.py`, `data/zaznamy.json`, `data/mista.json`) na GEDCOM 5.5.1 (UTF-8).

1. Přečíst `reference/data.md` a `template/data/osoby.py` – struktura osob, rodin, událostí a zdrojů.
2. Převzít zápis GEDCOM z `ftb_export.py` (CONC dělení řádků nad 255 znaků, hlavička, INDI/FAM bloky).
3. Mapování: osoba → INDI (NAME, SEX, BIRT, DEAT), rodina → FAM (HUSB, WIFE, CHIL, MARR), zdroje z matrik → SOUR/NOTE.
4. Soukromí: podle `reference/soukromi.md` vynechat údaje žijících osob (nebo je zeptat uživatele).
5. Obrázky a dokumenty – viz sekce níže.
6. Zapojit do SKILL.md (tabulka nástrojů) a doplnit CHANGELOG.

## Obrázky matrik, fotky a dokumenty
GEDCOM 5.5.1 obrázky nevkládá, jen na ně odkazuje záznamem `OBJE` (`FILE` + `FORM jpg` + `TITL`).
Výstupem proto bude ZIP: `rodokmen.ged` a vedle něj složka `media/` s kopiemi obrázků a relativními cestami
v `FILE media/<soubor>.jpg`, aby je MyHeritage, Gramps aj. po importu našly.

Zdroje dat (podle `reference/data.md`):
- **Zápisy z matrik** (`zaznamy.json`): `klic` je zároveň název obrázku. Každý zápis → `SOUR` (`TITL` = `nazev`,
  `TEXT` = `shrnuti`, případně přepis `orig`/`cs` z `prepisy.json`, `PAGE` = snímek, `REPO`/`NOTE` ze `svazky.json`
  včetně `odkaz`/`url`) a k němu `OBJE` na výřez `vyrezy/<klic>.jpg`; plný snímek `zdroje/<klic>.jpg` volitelně
  jako druhý `OBJE`. Osoby odkazují na zápis přes `r` → u příslušné události (BIRT/MARR/DEAT podle `druh`
  N/O/Z) citace `SOUR @Sx@`, ostatní druhy (I, S, J) jako citace přímo u `INDI`.
- **Rodinné fotky a dokumenty** (`dokumenty.json`): `img` → `OBJE` (`TITL` = `popis`), připojený ke každé osobě
  z `osoby`. Skupinová fotka tak bude u všech zobrazených osob.
- **Portréty** (`img` obsahuje `portret` bez ohledu na diakritiku a velikost písmen): `OBJE` u osoby s `_PRIM Y`
  (MyHeritage/Ancestry ho použijí jako profilovou fotku). Výběr portrétu převzít z logiky `export_web.py`
  (první existující v pořadí `dokumenty.json`).
- **Zvýraznění** (`zvyrazneni.json`): do GEDCOM nejde; exportovat výřezy bez rámečků.
- Chybějící soubor obrázku přeskočit a vypsat varování (stejně jako `export_web.py`).

Volby příkazu: `--bez-obrazku` (jen `.ged`, bez ZIP), `--plne-snimky` (přidat i `zdroje/`).

## Soukromí
Podle `reference/soukromi.md`: žijícím osobám vynechat data i fotky a dokumenty (jen jméno nebo „Žijící osoba“);
údaje od rodiny (`udaje_od_rodiny.md`) exportovat jen s `--vcetne-rodiny`. Před uložením vypsat souhrn,
co v exportu je (počet osob, zápisů, obrázků, vynechaných žijících).

## Sloučení s existujícím stromem (MyHeritage)
Cíl: na začátku bádání stažený GEDCOM z MyHeritage rozšířit o nová zjištění a vrátit zpět na MyHeritage,
aniž by se ztratil stávající strom.

Omezení MyHeritage (ověřeno v nápovědě, 11/2026):
- Nahrání GEDCOM na web vytvoří vždy **nový samostatný strom**, se stávajícím se nesloučí.
- Family Tree Builder (FTB) při importu GEDCOM nabídne „Merge into project …“ a projekt se pak synchronizuje
  s webem. Stejné osoby se ale **nespojí automaticky** – vzniknou duplicity, které se spojují ručně
  (Merge people / Tools → hledání duplicit).

### Předpoklad: vazba osob na původní GEDCOM
`ged_import.py --osoby` dnes zahazuje identifikátory osob (`@I123@`). Doplnit:
- do kostry `osoby.py` pole `ged="@I123@"` (a `uid`, pokud export MyHeritage obsahuje `_UID` – ověřit na
  skutečném souboru), u `SIDE` totéž;
- původní `.ged` ponechat v `dokumenty/` a jeho cestu zapsat do `data/STAV.md`;
- `kontrola.py`: upozornit na osobu se `st="fam"` bez `ged` (nelze ji spárovat).

### Doporučený postup: rozdílový GEDCOM přes FTB (varianta B)
Nový režim `ged_export.py --rozdil dokumenty/strom.ged`:
1. Načíst původní strom (`read()` z `ged_import.py`) a data projektu, spárovat osoby přes `ged`/`uid`.
2. Roztřídit: **nové osoby** (bez `ged`), **změněné** (nové/odlišné fakty, nové zápisy, obrázky) a **kotvy**
   (existující osoby, na které se nové připojují jako rodiče/děti/partneři).
3. Vyrobit GEDCOM jen s novými, změněnými a kotvami; změněné a kotvy s původním jménem a ID v `NOTE`
   („Sloučit s @I123@ v MyHeritage“), aby šly v FTB snadno najít a spojit.
4. Vypsat čitelný **přehled změn** (`pracovni/zmeny_pro_myheritage.md`): u každé osoby co přibylo/změnilo se,
   zdroj a obrázek; slouží jako kontrolní seznam pro slučování duplicit v FTB.
5. Návod pro uživatele (do `reference/data.md`): FTB → otevřít projekt synchronizovaný s webem → Import
   GEDCOM → „Merge into project“ → spojit duplicity podle přehledu → Sync.

Výhody: zůstane stávající strom včetně Smart Matches, Record Matches, online fotek a **propojení DNA testů**.
Ruční práce jen se slučováním kotev a změněných osob.

Práce v FTB je **úplně ruční** (rozhodnutí uživatele): skill vyrobí jen rozdílový GEDCOM a přehled změn, import,
spojení duplicit i Sync dělá uživatel. FTB je potřeba jen pro tuto variantu; před každým importem záloha
v FTB (File → Backup). Neautomatizovat: FTB nemá API ani příkazovou řádku, veřejné API MyHeritage už není,
zápis přímo do `.ftb` riskuje poškození synchronizace a úpravy webu přes prohlížeč porušují `soukromi.md`
(zkušenost se zablokovaným účtem).

### Varianty (nepreferované)
- **A. Celý nový strom** (`--sloucit`): původní `.ged` + nová zjištění → kompletní GEDCOM, nahrát jako nový
  strom a starý smazat. Čisté, ale ztratí se Smart/Record Matches, online fotky, spolupracovníci a vazba DNA.
  Jen pro stromy bez DNA a bez hodnotných online dat.
- **C. Jen přehled změn** (`--jen-prehled`): bez GEDCOM, ruční zadání na webu. Nejbezpečnější, nejvíc práce.
  Vzniká stejně v kroku 4, takže stačí volba.

### Otevřené otázky
- Obsahuje GEDCOM z MyHeritage `_UID` a zachová ho FTB při importu/merge? (Ověřit na exportu uživatele.)
- Převezme FTB při importu obrázky z `OBJE` (relativní cesty v ZIPu)? Ověřit na zkušebním projektu.
- Rozpor údajů (jiné datum v MyHeritage a v matrice): v přehledu změn označit a jako výchozí doporučit
  údaj doložený zápisem (`st="doc"`).

## Ověření
- Spustit nad ukázkovými daty (`template/ukazka`, obsahují i obrázky v `ukazka_vyrezy/` a `ukazka_zdroje/`)
  přes `python -I -X utf8 tools/ged_export.py`.
- Round-trip: výstup načíst `ged_import.py` a porovnat počet osob a rodin.
- Zkontrolovat ZIP: každý `FILE` v `.ged` existuje v `media/`, žádný obrázek žijící osoby.
- Nahrát ZIP do Gramps (a volitelně MyHeritage) a ověřit, že se zobrazí výřezy matrik u událostí a portréty.
- Přidat test do `tests/` (malý strom s obrázkem, kontrola `OBJE` a cest).
- Sloučení: test s malým původním `.ged` + projektem s jednou novou osobou, jednou změněnou a jednou beze změny
  → rozdílový GEDCOM obsahuje novou, změněnou a kotvu, ne nezměněnou; přehled změn je odpovídá.
- Ruční zkouška v FTB na kopii projektu (ne na synchronizovaném stromu): import s „Merge into project“,
  spojení duplicit, kontrola výsledku před Sync.

## Poznámka
Úpravy dělat v klonu `C:\Users\tomas\Documents\VSCode\rodokmen-skill` (ne v cache pluginu) a postupovat podle
„Postup po každé úpravě skillu“ v `CLAUDE.md` (zvýšit verzi, commit, `/plugin marketplace update`).
