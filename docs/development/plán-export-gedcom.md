# Plán: export rodokmenu do GEDCOM (navrženo pro 0.11.2, fáze 1 vydána v 0.12.0–0.12.6)

## Context
Uživatel se ptal, zda plugin `rodokmen` umí export do GEDCOM. Prověřeno: neumí.
- Nainstalována je jen verze 0.11.2 (`~\.claude\plugins\cache\rodokmen-skill\rodokmen\0.11.2`), jiná verze v cache není.
- GEDCOM se v `tools/` vyskytuje jen v `ged_import.py` (import `.ged`) a `ftb_export.py` (záloha MyHeritage `.ftb` → `.ged`, určený jako vstup pro import).
- `tools/export_web.py` exportuje jen data pro web (JSON do Astro šablony), ne GEDCOM.
- CHANGELOG zmiňuje GEDCOM jen u importu.

Cesty `tools/`, `reference/`, `template/` v tomto plánu jsou relativní ke `skills/rodokmen/`.

Export se dělá jako nový nástroj uvnitř stávajícího skillu `rodokmen` (ne jako samostatný skill), protože navazuje na `ged_import.py`, čte data projektu a `novy_projekt.py` ho zkopíruje do projektů spolu s ostatními nástroji.

## Rozdělení do dvou verzí
Druhá část (sloučení s MyHeritage) stojí na dvou neověřených předpokladech (viz „Otevřené otázky“), proto se dělá zvlášť:
- **Fáze 1 – export:** `tools/ged_export.py` (osoby, rodiny, zdroje, obrázky, soukromí). Nezávislá, hned testovatelná.
- **Fáze 2 – sloučení:** vazba osob na původní GEDCOM (`ged`), rozdílový režim, přehled změn, návod pro FTB.
  Začíná dvěma zkouškami (viz „Otevřené otázky“), teprve podle výsledku se implementuje.

---

# Fáze 1: export

**Stav (23. 11. 2026):** implementováno ve verzi 0.12.0 – `tools/ged_export.py`, úprava `ged_import.py` (import bez
vedlejších efektů), test `tests/gedcom/test_ged_export.py` (76 kontrol), dokumentace v `reference/data.md`, SKILL.md,
README a CHANGELOG. Navíc volba `--koren <číslo>` (export jedné větve jako samostatného stromu – uživatel chce
maminčinu stranu, č. 3, jako vlastní strom v MyHeritage). Zbývá ruční zkouška importu ZIP do MyHeritage
(uživatel ho používá) a volitelně do Gramps.

**Stav (24. 11. 2026, verze 0.12.2):** web MyHeritage ZIP odmítá a obrázky z GEDCOM nenačte – návod přes Family Tree
Builder (0.12.1), volby `--slozka` a `--cp-v-miste` (0.12.2), viz `plán-myheritage-obrázky.md`. Zkouška ve FTB 24. 11. 2026:
obrázky jen s absolutními cestami → oprava v 0.12.3. Zbývá čp. v místě, mapa, Sync a volitelně Gramps.

**Stav (24. 11. 2026, verze 0.12.6) – fáze 1 hotová.** Export do složky (`--slozka`) pro Family Tree Builder ověřen
importem jedné větve skutečného projektu (52 osob, 27 rodin): data a místa (čp. v místě s `--cp-v-miste`), zdroje a citace, výřezy
a fotky v plném rozlišení u osob i zdrojů, portrét v okénku osoby ve stromu; obrázky FTB ukáže až **po restartu**.
Pro FTB se proti návrhu níže zavedlo (jen s `--slozka`; ZIP a `--bez-obrazku` beze změny, podrobně
`plán-myheritage-obrázky.md`):
- absolutní cesty k obrázkům, soubor UTF-8 s BOM a CRLF (bez BOM FTB nenačte cestu s diakritikou);
- **záložní řešení „jeden `SOUR` na zápis“** (viz Mapování: zdroje a citace) – FTB obrázky z citací zahodí, ale umí je
  u zdroje; zdroj = zápis (titul „zápis, svazek, snímek N“, archiv svazku) s výřezem;
- výřez každého citovaného zápisu i přímo u osoby (`1 OBJE`), výřez sňatku u obou manželů;
- obrázky v plném rozlišení ze `zdroje/` (jinak `vyrezy/`), `--plne-rozliseni` pak nepřidá druhou kopii;
- portrét jako osobní fotka FTB (dvojice `OBJE` s `_PRIM_CUTOUT`/`_CUTOUT`/`_PARENTRIN`), `1 RIN MH:I<číslo>` u osob,
  `_PHOTO_RIN MH:P500001…` a `_FILESIZE` u každého obrázku.
Testy 113 kontrol (`tests/gedcom/test_ged_export.py`), včetně round-tripu přes `ged_import.read()` a stromu s aliasem
`SAME` a zástupným rodičem.

Zbývá z fáze 1:
- **Sync na MyHeritage** – přenesou se fotky, výřezy, portrét do okénka a špendlíky na mapě (`MAP`/`LATI`/`LONG`; FTB mapu
  ukáže jen u synchronizovaného stromu)? Zkouší uživatel.
- **Import do Gramps** (bod Ověření) – nezkoušeno.
- Drobnosti: `QUAY 2` ukazuje FTB jako „Sporná hodnověrnost důkazu“ (ověřit pořadí voleb ve FTB); fakt
  „Obec (?), okres X“ dává u události navíc poznámky „?“ a „okres X“; absolutní cesta může u hluboko
  vnořené složky překročit 255 znaků na řádek `FILE` (nejde dělit).

Rozdíly proti návrhu níže (rozhodnuto při implementaci):
- `PLAC` = plný název z pole `osm` v `mista.json` bez PSČ (např. „Holice, okres Pardubice, Pardubický kraj, Česko“),
  když začíná názvem obce; jinak jen název obce. `dotaz` je dotaz pro OpenStreetMap, ne název.
- Zápis ↔ událost: u narození a úmrtí tolerance ±1 rok (křest či pohřeb až další rok), u sňatku přesná shoda roku.
- `OBJE` jsou vložené přímo u citací a osob (ne sdílené záznamy `0 @M…@ OBJE`) – širší podpora v programech.
- Zápis bez svazku ve `svazky.json` má vlastní `SOUR` s názvem zápisu.
- Sňatek chráněného páru se nevyváží (rodina má `RESN privacy`, jen vazby); fakt `×` nesedící na partnera → `NOTE`.
- Chybějící obrázky souhrn hlásí jednou větou (počet a příklady), ne po jednom.
- Výstup: výchozí `pracovni/rodokmen.zip`, s `--koren N` `pracovni/rodokmen_koren<N>.zip`; existující soubor jen
  s `--prepsat`; výstup do `web/` odmítne; přípona musí odpovídat (`.zip` / `.ged`). S `--zijici` upozorní, že soubor
  dostane i cloud, je-li složka synchronizovaná (podle názvu cesty: Google Disk / Můj disk, OneDrive, Dropbox, iCloud).

## Datový model projektu (co export musí zvládnout)
Data nejsou obecný graf osob, rodin a událostí (viz `reference/data.md`):
- `osoby.py`: `P` podle Kekulého čísel; rodiny a vztahy se **odvozují z čísel** (otec 2k, matka 2k+1, dítě k).
  Fakta `f` jsou **volný text** (`"* 14. 2. 1890 Holice čp. 112"`, `"† 1855 Holice, na choleru"`,
  `"* 1895 Dolní Roveň čp. 7 (datum podle sčítání 1921)"`), ne strukturované události.
- `SAME` (alias → hlavní číslo): předek v rodokmenu dvakrát = jedna osoba.
- `SIDE`: boční příbuzní jako volný text (`n`, `t`), bez dat.
- Zástupné osoby („otec neuveden“, `st="unk"`) nejsou osoby.
- Žijící osoba nemá v datech žádné pole, jen konvenci `note="Žijící – údaje jen základní."`.

## Postup
Nový nástroj `tools/ged_export.py`, který převede `data/osoby.py`, `data/zaznamy.json`, `data/svazky.json`,
`data/prepisy.json`, `data/mista.json`, `data/dokumenty.json` na GEDCOM 5.5.1 (UTF-8).

1. Přečíst `reference/data.md`, `template/ukazka/osoby.py` a v `export_web.py` logiku rodin (ř. 333–358: spojení
   rodin přes `SAME`, zástupné osoby) a portrétů (`document_lists()`, `is_portrait()`).
2. Převzít zápis GEDCOM z `ftb_export.py` (`chunks()`/`gtext()` pro CONC/CONT, hlavička, INDI/FAM bloky).
3. Mapování podle níže, soukromí podle „Soukromí“, obrázky podle „Obrázky“.
4. Zapojit do SKILL.md (tabulka nástrojů, ř. ~255), `reference/data.md` (nová sekce „Export do GEDCOM“),
   README (zmínka o GEDCOM, ř. ~152) a CHANGELOG.

### Technické předpoklady (udělat jako první)
- `ged_import.py` jde dnes importovat jen s úpravou: hned po načtení volá `sys.exit(__doc__)`, když v `argv` není
  soubor (a na `-h`), a mění `stdout`. Kontrolu argumentů a `reconfigure` přesunout do `main()`, aby šlo
  `from ged_import import read`.
- `python -I` nepřidává složku skriptu do `sys.path`. Sourozenecké moduly importovat přes
  `sys.path.insert(0, <složka tools>)`, jako [aron_img.py:20](../../skills/rodokmen/tools/aron_img.py#L20).
  Platí i pro `export_web.py` (portréty) – nebo logiku portrétů v `ged_export.py` krátce zopakovat.
- Výstup do `pracovni/` (nejde na web): `pracovni/rodokmen.zip`, resp. `pracovni/rodokmen.ged` s `--bez-obrazku`.
  Ověřit, že `.gitignore` v šabloně `pracovni/` ignoruje (ZIP obsahuje osobní údaje).

### Mapování: osoby a rodiny
- **Osoba → `INDI`.** Zástupné osoby (`placeholder()` z `export_web.py`) a aliasy z `SAME` se jako `INDI` nevyváží;
  alias se promítne do `FAMS` hlavní osoby.
- **`NAME`:** `n` rozdělit na `GIVN` / `SURN` (poslední slovo = příjmení, bez `()?`; ženy rodným příjmením).
  Fakt `provd. Nováková` → druhé `NAME` s `TYPE married` (jako v `ftb_export.py`).
- **`SEX`:** z parity čísla (sudá M, lichá F), u čísla 1 z pole `sex`.
- **Rodina → `FAM`:** pro každé k, jehož otec nebo matka existuje: `HUSB` 2k, `WIFE` 2k+1, `CHIL` k. Stejný pár
  potkaný dvakrát (přes `SAME`) = jedna `FAM` s více `CHIL`. Zástupný rodič se vynechá (`FAM` má jen jednoho).
  `FAMC` / `FAMS` doplnit u osob.
- **Fakta (volný text) → události.** `*` → `BIRT`, `†` → `DEAT`, `×` → `MARR` v `FAM`, jiný text → `OCCU` (krátký) nebo
  `NOTE`. Parser faktu:
  - datum: `14. 2. 1890` → `14 FEB 1890`; `asi` → `ABT`, `před` → `BEF`, `po` → `AFT`, `mezi X a Y` → `BET … AND …`;
    zápis `datum` v `zaznamy.json` má i tvar `3/1867` (měsíc/rok) a `1797`. Co se nepodaří převést →
    `DATE (původní text)` (fráze v závorkách);
  - místo: odděl `čp. N` a závorkové poznámky (→ `NOTE` u události), zbytek je obec. Obec najít v `mista.json`
    (výraz `re`) a do `PLAC` dát plný název (`dotaz`, např. „Holice, Česko“) a `MAP` (`LATI`, `LONG`); neznámá obec
    → `PLAC` tak, jak je. Místa s `hypoteza: true` se nepoužijí;
  - příčina úmrtí (`† 1855 Holice, na choleru`) → `CAUS` jen u nežijících a jen když soukromí povolí (viz níže);
  - fakt, který se nepodařilo rozebrat, jde celý do `NOTE` u osoby (nic se neztratí) a nástroj ho vypíše do souhrnu.
- **Jistota údaje (`st`):** `doc` → `QUAY 3`, `prob` → `QUAY 2`, `fam`/`mh`/`unk` → bez `QUAY`, ale k osobě
  `NOTE` „Původ údajů: od rodiny / jen z cizího rodokmenu“. Stejně `note` osoby (kromě žijících) → `NOTE`.
- **Neexportuje se:** `LINES`, `ISSUES`, `HYPOTEZY`, `zvyrazneni.json`. `SIDE` → `NOTE` u osoby `k`
  („Příbuzný: Josef Novák (1865–1920) – text“), protože jde o volný text bez dat.

### Mapování: zdroje a citace
Zápis (`zaznamy.json`) ≠ osoba. **Seznam `r` u osoby obsahuje i zápisy jejích dětí a rodičů** (v ukázce má Václav Novák (16)
v `r` křest svého syna Jana, Josef Pokorný (18) sňatek své dcery). Pravidlo „`druh` N/O/Z = událost této osoby“ proto
neplatí. Postup:
1. Pro každý fakt `*`, `×`, `†` osoby najít v jejím `r` zápis odpovídajícího druhu (N→`BIRT`, O→`MARR`, Z→`DEAT`),
   jehož `datum` se shoduje **v roce** s rokem faktu (u sňatku s rokem sňatku obou manželů).
2. Shoda → citace u té události (sňatek pod `MARR` v záznamu `FAM`, ne u `INDI`).
3. Zápis bez shody (druhy I, S, J, nebo zápis cizí události) → citace přímo u `INDI` s `PAGE` a poznámkou
   „zápis se týká i jiné osoby / události“. Nic se neuhaduje.

Struktura záznamů:
- **`SOUR` jeden na svazek** (`svazky.json`): `TITL` = `svazek`, `CALN` = signatura, `REPO` odkazem na samostatný
  záznam `REPO` (`NAME` = `archiv`). Odkaz na svazek (`url`) jako `NOTE` (5.5.1 nemá tag pro URL).
- **Citace zápisu** (úroveň 2/3 u události): `PAGE` = „snímek N“ + `nazev`, `DATA` / `TEXT` = `shrnuti`
  (případně přepis `orig` a `cs` z `prepisy.json`), `OBJE` na výřez. Odkaz `odkaz` jako `NOTE`.
- Pokud se při zkoušce ukáže, že Gramps/MyHeritage `OBJE` u citace nepřevezmou, použít záložní řešení
  „jeden `SOUR` na zápis“ s `OBJE` u `SOUR` (`PAGE` pak dát jen do citace). Rozhodnout po zkoušce, ne dopředu.
- Sčítací arch (`S`) je jeden zápis pro více osob – `SOUR`/`OBJE` se zapíše jednou, citují ho všichni členové.

## Obrázky matrik, fotky a dokumenty
GEDCOM 5.5.1 obrázky nevkládá, jen na ně odkazuje: `1 OBJE` / `2 FILE media/<soubor>.jpg` / `3 FORM jpeg` / `2 TITL …`.
Výstupem proto bude ZIP: `rodokmen.ged` a vedle něj složka `media/` s kopiemi obrázků a relativními cestami.
Že cesty z ZIPu správně načte **webový import MyHeritage, není ověřeno** (viz „Otevřené otázky“); Gramps ano.

Zdroje dat (podle `reference/data.md`):
- **Zápisy z matrik** (`zaznamy.json`): `klic` je zároveň název obrázku. `OBJE` na výřez `vyrezy/<klic>.jpg`;
  výřez v plném rozlišení `zdroje/<klic>.jpg` volitelně jako druhý `OBJE` (volba `--plne-rozliseni`).
  (`zdroje/` není „plný snímek stránky“, ale týž výřez ve vyšším rozlišení.)
- **Rodinné fotky a dokumenty** (`dokumenty.json`): `img` → `OBJE` (`TITL` = `popis`) u každé osoby z `osoby`
  (u aliasu `SAME` jednou u hlavní osoby). Skupinová fotka tak bude u všech zobrazených osob.
- **Portréty** (`img` obsahuje `portret` bez ohledu na diakritiku a velikost písmen, viz `is_portrait()`): `OBJE` u osoby
  s `_PRIM Y` (MyHeritage/Ancestry ho použijí jako profilovou fotku). Výběr portrétu z `document_lists()`
  (první existující v pořadí `dokumenty.json`, jedna osoba = jeden portrét).
- **Zvýraznění** (`zvyrazneni.json`): do GEDCOM nejde; výřezy se kopírují bez rámečků.
- Chybějící soubor obrázku přeskočit a vypsat varování (stejně jako `export_web.py`).

Volby příkazu: `--bez-obrazku` (jen `.ged`, bez ZIP), `--plne-rozliseni` (přidat i `zdroje/`), `--zijici` (viz níže).

## Soukromí
Export míří do cizích služeb (MyHeritage, Gramps…), proto je výchozí nastavení přísné; `reference/soukromi.md`
platí i pro něj.

**Jak se pozná chráněná osoba** (v datech není pole, proto pravidlo – návrh k potvrzení uživatelem):
1. `note` začíná „Žijící“, nebo
2. nemá fakt `†` a narodila se později než (letos − 100 let) nebo rok narození neznáme a `st` je `fam`, nebo
3. zemřela před méně než 30 lety (stejná lhůta jako u archivu pro úmrtí; `soukromi.md` chrání i nedávno zemřelé).

Pro chráněné osoby:
- v GEDCOM zůstanou jen jako uzel stromu: `NAME` „Žijící osoba“ (příp. s křestním jménem jen s `--zijici`), `SEX`,
  `RESN privacy`, vazby `FAMC`/`FAMS`; žádná data, místa, `note`, `CAUS`, `OBJE` (portrét, dokumenty);
- zápisy a obrázky matrik se exportují jen když je cituje alespoň jedna **nechráněná** osoba; zápis, který cituje
  i chráněnou osobu (např. sčítací arch), se vypíše v souhrnu k ruční kontrole a `OBJE` se k němu nepřidá.

**Výjimka `--zijici`:** vyexportuje i údaje chráněných osob. Skill se před každým exportem **zeptá**, zda exportovat
i žijící osoby (rozhodnutí uživatele 23. 11. 2026), vysvětlí, že údaje dostane cílová služba, a výchozí je „ne“.
Nástroj při `--zijici` vypíše upozornění; na web takový soubor nepatří.

`udaje_od_rodiny.md` je volný text bez vazby na osoby, do GEDCOM se **neexportuje**. Údaje od rodiny (`st="fam"`)
jsou v `f` osob a exportují se stejně jako ostatní.

Před uložením vypsat souhrn: počet osob, rodin, zápisů, obrázků, chráněných osob (vynechaných/zjednodušených),
faktů, které se nepodařilo rozebrat, chybějících obrázků a zápisů citovaných i chráněnou osobou.
Kontrola `CITLIVÉ` v `kontrola.py` hlídá jen web; export proto `note` a příčiny úmrtí u osob z posledních ~100 let
vynechá stejně jako u chráněných osob.

## Ověření (fáze 1)
- Test v `tests/gedcom/` zakládá **dočasný projekt přes `novy_projekt.py --ukazka`** (nástroj čte `data/`, `vyrezy/`,
  `zdroje/` v kořeni projektu, ne `template/ukazka*`) a nad ním spustí
  `python -I -X utf8 tools/ged_export.py`. Ukázka má jen 3 obrázky k 20+ zápisům (vyzkouší varování o chybějících
  souborech) a osoby 1–3 jsou žijící (vyzkouší soukromí).
- Kontroly: každý `FILE` v `.ged` existuje v `media/`, žádný obrázek chráněné osoby; křest syna se necituje jako
  narození otce; sňatek je citován pod `MARR` v `FAM`; datum `14. 2. 1890` → `14 FEB 1890`, `asi 1720` → `ABT 1720`.
- Round-trip: výstup načíst `ged_import.py` (`read()`) a porovnat s **očekávaným** počtem: osoby − zástupné − aliasy
  `SAME`, rodiny podle odvozených párů (chráněné osoby zůstávají jako uzly).
- Nahrát ZIP do Gramps a ověřit, že se u událostí zobrazí výřezy matrik a portréty (MyHeritage viz fáze 2).
- Test na jednoduchém stromu s aliasem `SAME` a zástupným rodičem.

---

# Fáze 2: sloučení s existujícím stromem (MyHeritage)
Cíl: na začátku bádání stažený GEDCOM z MyHeritage rozšířit o nová zjištění a vrátit zpět na MyHeritage,
aniž by se ztratil stávající strom.

Omezení MyHeritage (ověřeno v nápovědě, 11/2026):
- Nahrání GEDCOM na web vytvoří vždy **nový samostatný strom**, se stávajícím se nesloučí.
- Family Tree Builder (FTB) při importu GEDCOM nabídne „Merge into project …“ a projekt se pak synchronizuje
  s webem. Stejné osoby se ale **nespojí automaticky** – vzniknou duplicity, které se spojují ručně
  (Merge people / Tools → hledání duplicit).

## Nejdřív zkoušky (před implementací)
1. Obsahuje GEDCOM z MyHeritage `_UID` a zachová ho FTB při importu a merge? Jak stabilní jsou `@I…@` mezi dvěma
   exporty téhož stromu? (Ověřit na exportu uživatele, rozhodne o párování osob.)
   **Částečně ověřeno (24. 11. 2026):** export z webu MyHeritage (`dokumenty/strom.ged`, 28. 10. 2026, 213 osob) má
   u každé osoby `1 RIN MH:I…` a `1 _UID` (32 hex znaků; `_UID` mají i rodiny a události). Export GEDCOM z FTB
   synchronizovaného projektu téhož stromu (24. 11. 2026) má u téže osoby **stejné** `@I500001@`, `RIN MH:I500001`
   i `_UID 56B453DD…` – ID a `_UID` jsou mezi exporty (web i FTB, s odstupem měsíce) stálé, párování na nich jde
   postavit. **Zbývá:** zachová FTB `_UID` (a `RIN`) osob při importu s „Merge into project“ a po Sync? Zkouška na kopii
   projektu: import malého GEDCOM s `_UID` existující osoby → spojí ji FTB, nebo vytvoří duplicitu, a jaké `_UID`
   má výsledek v dalším exportu?
   **Výsledek zkoušky (24. 11. 2026):** kopie stromu = import exportu GEDCOM z FTB jako nový projekt „… Family Tree
   Kopie“ (258 osob, 84 rodin, stejná ID a `_UID`). Do ní Import GEDCOM → „Merge into project“ souboru s kotvou
   osobou A (`@I500004@`, `RIN MH:I500004`, `_UID` jako ve stromu) a jejím novým otcem B. Výsledek:
   260 osob, 85 rodin – **FTB přidal obě osoby jako nové** (A ID 259, B ID 260, spolu jako
   samostatná rodina); původní A (ve FTB zobrazená pod příjmením po sňatku, ID 4) zůstala beze změny a bez rodičů.
   **FTB při sloučení osoby podle `@I…@`, `RIN` ani `_UID` nepáruje** a jeho hledání duplicit dvojici nenašlo
   (původní vedená pod příjmením po sňatku, importovaná pod rodným). Párování na straně FTB tedy není – každá kotva
   = ruční spojení (Osoba → Sloučit osoby). Pro skill platí dál: `ged`/`uid` slouží k tomu, aby **skill** poznal, co je
   ve stromu nové a co je kotva, a v přehledu změn uvedl přesnou dvojici ke spojení.
2. Převezme FTB i webový import MyHeritage obrázky z `OBJE` s relativní cestou v ZIPu? Ověřit na zkušebním projektu.
   **Web: ne** (ověřeno 23. 11. 2026 – ZIP odmítne, bere jen `.ged`; podle nápovědy MyHeritage GEDCOM obrázky
   nepřenáší, jen odkazy). **FTB: relativní cesty ne, absolutní ano** (ověřeno 24. 11. 2026; `--slozka` od 0.12.3 zapisuje absolutní –
   viz `plán-myheritage-obrázky.md`).
Výsledky zapsat sem; podle nich se upraví návrh níže.

## Předpoklad: vazba osob na původní GEDCOM
`ged_import.py --osoby` dnes zahazuje identifikátory osob (`@I123@`). Doplnit:
- do kostry `osoby.py` pole `ged="@I123@"` (a `uid`, pokud export obsahuje `_UID`), u `SIDE` totéž;
- původní `.ged` ponechat v `dokumenty/` a jeho cestu a datum stažení zapsat do `data/STAV.md`;
- **migrace stávajících projektů:** projekty, které strom už importovaly, nemají `ged` vůbec. Nový příkaz
  (např. `ged_import.py strom.ged "Výchozí osoba" --ged-id`) projde strom od stejné výchozí osoby (stejné Kekulé číslo =
  stejná osoba), ověří jméno a rok narození a vypíše dvojice `číslo → @I…@` k doplnění přes `zapis.py`. Neshody jen hlásí;
- `kontrola.py`: hlásit osoby bez `ged` **jen když `STAV.md` eviduje původní `.ged`** (`st="fam"` neznamená „z GEDCOM“,
  v ukázce by to hlásilo falešné poplachy; nově zjištěný předek bez `ged` je v pořádku, kontrola je jen informační).

**Stav (24. 11. 2026, verze 0.13.0): implementováno** (kromě `SIDE` – boční příbuzní nemají ve stromu Kekulé číslo,
párovat je až spolu s rozhodnutím níže):
- `ged_import.py --osoby`: kostra má `ged="@I…@"` a `uid` (`_UID`, je-li). Stavba stromu vyčleněna do `ancestors()`.
- `ged_import.py <strom> "Výchozí osoba" --ged-id [--zapsat]`: shoda = první křestní jméno a příjmení podle
  společného začátku slova (Novák/Nováková, Dvořák/Dvořáková, Anton/Antonín), i příjmení po sňatku z faktu
  „provd. …“; rok narození ±1. Vypíše shody, NESEDÍ, JINÉ ID (osoba už má jiné `ged`), „už mají“ a nově zjištěné předky
  (nejsou ve stromu). `--zapsat` zapíše jen shody přes `zapis.nastav()`.
- `zapis.py ged <číslo> <@I…@> [<uid>]` (`nastav()`): nahradí/přidá pole v `dict(…)` i `{…}`, zachová styl uvozovek,
  pojistka jako u `odkaz` (soubor jde načíst, jinak se nic nezměnilo).
- `kontrola.py`: chyba při špatném tvaru `ged`, upozornění na stejné `ged` u dvou osob (kromě aliasů `SAME`),
  „informace:“ se seznamem osob bez `ged`. **Odchylka od návrhu:** informace se vypíše, když má `ged` aspoň jedna osoba
  (ne podle `STAV.md` – volný text, nespolehlivé); v ukázce bez `ged` tedy nic.
- Původní `.ged` v `dokumenty/` a záznam do `STAV.md`: pokyn v `reference/data.md` (dělá Claude, ne nástroj).
- Testy `tests/gedcom/test_ged_vazba.py` (19 kontrol: kostra, párování v ukázce `{…}` i `dict(…)`, opakování,
  ruční zápis, kontrola).
- **Ověřeno na skutečném projektu uživatele** (kopie, bez zápisu) proti `dokumenty/strom.ged`: 50 shod, 3 neshody – č. 75
  (jiný pravopis křestního jména, potvrdí uživatel), č. 128/129 (strom má jiné předky než doložil výzkum – vazbu nezapisovat), 91 nově zjištěných předků.

## Otevřený bod: boční příbuzní (`SIDE`) jako osoby
**Stav (24. 11. 2026):** Fáze 1 vyváží `SIDE` jen jako poznámku u předka (`1 NOTE Příbuzný: <n> – <t>`,
`ged_export.py` ř. ~556), nikoli jako `INDI`. Na MyHeritage proto sourozenci a další příbuzní z webové sekce
„Příbuzní mimo přímou linii“ nemají vlastní kartu (nejsou ve stromu, nejdou k nim přidat fotky), jejich data jsou
jen volný text a jejich zápisy (`r`) se necitují (kromě zápisů, které má i předek). Ověřeno zkušebním exportem
skutečného projektu: 16 `SIDE` → 15 poznámek, 1 vynechán kvůli soukromí.

Možné řešení: `SIDE` jako `INDI` – dítě v `FAM` rodičů předka (je-li `t` „sourozenec“), roky narození a úmrtí
z `n`, zbytek `t` jako `NOTE`, citace zápisů z `r`. Překážky:
- `SIDE` nemá strukturovaná data (jen `n`/`t` textem); pohlaví, přesné datum, vztah k předkovi (sourozenec ×
  bratranec × švagr) ani manžele nelze spolehlivě určit – vyžadovalo by to strukturovaná pole v `SIDE`
  (např. `vztah`, `pohlavi`, `nar`, `zem`), jejich doplnění v existujících projektech a úpravu webu.
- Ochrana soukromí: `side_protected` bere roky z `n`; záznam bez roku projde. U `INDI` by bylo nutné bez roku chránit.
- Sloučení přes FTB: strom z MyHeritage sourozence předků často už má → další duplicity k ručnímu spojení.
  Párování `SIDE` s osobami původního stromu (`ged`, viz výše) by to vyřešilo, proto rozhodnout až spolu s ním.

Rozhodnutí zatím: ponechat jako poznámku; řešit ve fázi 2 po zkoušce 1 (`_UID`, stabilita `@I…@`).
Rozpracováno v `plán-boční-příbuzní-gedcom.md` (volba `--bocni`, 27. 11. 2026).

## Doporučený postup: rozdílový GEDCOM přes FTB
Nový režim `ged_export.py --rozdil dokumenty/strom.ged`:
1. Načíst původní strom (`read()` z `ged_import.py`) a data projektu, spárovat osoby přes `ged`/`uid`.
2. Roztřídit: **nové osoby** (bez `ged`), **změněné** a **kotvy** (existující osoby, na které se nové připojují jako
   rodiče/děti/partneři; v datech jde vždy o přímé předky, protože nová osoba je buď předek, nebo dítě předka k//2).
   „Změněné“ = jen to, co jde spolehlivě porovnat: **nový zdroj/zápis**, **nový obrázek**, **nový údaj** (datum,
   místo, povolání, který původní osoba nemá). Rozdílné údaje se jen označí, neřeší se obecný diff volného textu.
3. Vyrobit GEDCOM jen s novými, změněnými a kotvami; změněné a kotvy s původním jménem a ID v `NOTE`
   („Sloučit s @I123@ v MyHeritage“), aby šly v FTB snadno najít a spojit.
   **Podle zkoušky 1 (FTB nepáruje, hledání duplicit kotvu nenašlo):** kotvu zapsat **pod jménem, které má ve stromu**
   (`NAME` z původního `.ged`, u žen i příjmení po sňatku, jak ho strom zobrazuje), aby ji spíš našlo i hledání duplicit;
   kotev co nejméně (jen nejbližší existující osoba, ke které se nová připojuje – každá = jedno ruční spojení);
   v přehledu změn u každé kotvy dvojice „<jméno> (rok, z importu) → spojit s <jméno ve stromu> (rok)“ a pořadí
   spojování (nejdřív kotvy, pak kontrola nových osob). Ověřit dodatečnou zkouškou: najde hledání duplicit kotvu,
   když má stejné jméno a data jako ve stromu? FTB ukládá příjmení po sňatku jako `2 _MARNM Nováková` pod `NAME`
   a zobrazuje ho (export FTB) – kotva má proto převzít z původního `.ged` celé `NAME` včetně `_MARNM`, `SEX`
   a `BIRT`/`DEAT` (datum, místo). Zkouška 2: `zkouska_slouceni2.ged` (A s `_MARNM` a daty jako ve stromu + B) do kopie s „Merge into project“ → najde ji hledání duplicit?
   **Výsledek zkoušky 2 (24. 11. 2026):** import se sám nespojí (kotva zůstane jako druhá osoba), ale **Nástroje →
   Kontrola duplicit** po importu kotvu najde: „A (příjmení po sňatku), datum narození–rok úmrtí, otec B“ × „A,
   manžel …“ – shoda 52 %, odkud jde rovnou spojit. Celkem 41 nálezů (i starší podobné dvojice ve stromu,
   např. jedna dvojice 50 %). Kotva proto **musí** převzít ze stromu `NAME` s `_MARNM` a data narození a úmrtí
   (v první zkoušce bez `_MARNM` a s jiným místem ji kontrola nenašla). Postup pro uživatele: import → Kontrola duplicit
   → spojit dvojice podle přehledu změn (přehled uvede, které nálezy jsou kotvy; ostatní nálezy nechat).
   **Soukromí:** kotva, která je chráněná osoba (typicky rodiče výchozí osoby), se v tomto režimu neanonymizuje na
   „Žijící osoba“ (nešla by spojit), ale vyexportuje se s původním jménem a ID z `ged` a **bez dalších údajů**
   (jen jméno, ID, vazby). Vyžaduje to zapnutou volbu `--zijici-kotvy` a upozornění, že soubor jde jen do vlastního FTB.
4. Vypsat čitelný **přehled změn** (`pracovni/zmeny_pro_myheritage.md`): u každé osoby co přibylo/změnilo se,
   zdroj a obrázek; slouží jako kontrolní seznam pro slučování duplicit v FTB.
5. Návod pro uživatele (do `reference/data.md`): FTB → otevřít projekt synchronizovaný s webem → Import
   GEDCOM → „Merge into project“ → spojit duplicity podle přehledu → Sync.
6. **Další kolo:** po Sync a spojení stáhnout z MyHeritage čerstvý GEDCOM, doplnit `ged` novým osobám (příkaz
   z migrace) a původní `.ged` v `dokumenty/` nahradit novým. Bez toho by se nové osoby při dalším `--rozdil` znovu
   tvářily jako nové a vznikly by duplicity.

**Stav (24. 11. 2026, verze 0.13.0): implementováno** `ged_export.py --rozdil <strom.ged>` (s `--slozka`, ZIP
i `--bez-obrazku`, s `--koren`):
- Roztřídění (`diff_classify`): ve stromu = `ged` osoby je v původním `.ged`; **nové** = ostatní (osoba s `ged`, které ve
  stromu není → nová + varování); **kotvy** = osoby ze stromu v rodině (`FAM`) s novou osobou; **změněné** = ostatní
  osoby ze stromu se zápisem nebo obrázkem. Rodiny jen ty s novou osobou. Rozhodnutí uživatele: změněné ve výchozím
  stavu jen v přehledu, do souboru volbou **`--se-zmenenymi`** (bez rodinných vazeb, jen ke spojení).
- Kotva (`anchor_lines`): `NAME` s `GIVN`/`SURN`/`_MARNM`, `SEX`, `BIRT`/`DEAT` (datum, místo) **ze stromu** + `NOTE`
  „KOTVA…“ + vazby; **i chráněná kotva má jméno a data ze stromu** (rozhodnutí uživatele 24. 11. 2026: kotva jen
  vrací do stromu, co v něm je; volba `--zijici-kotvy` zrušena). Zemřelí do 30 let jsou „Chráněná osoba“, ne „Žijící osoba“. Kotva se změnami
  (se `--se-zmenenymi`) a změněná osoba: plné údaje projektu, jméno ze stromu, `NOTE` „ZMĚNA…“ (`changed_lines`).
- **Obsazené místo** (nové za zkoušky na skutečném projektu): nová osoba na pozici rodiče osoby ze stromu, kde strom
  už rodiče má (jiný předek – č. 128/129, nebo nespárovaná tatáž osoba – č. 75, jiný pravopis jména). Přehled to uvede u kotvy
  („po spojení by měl dvoje rodiče“) i u nové osoby (kdo je ve stromu, `zapis.py ged …` když tatáž), souhrn to hlásí.
- Přehled `pracovni/rozdil[_koren<N>]_zmeny.md` (`diff_report`): postup ve FTB (záloha, Merge into project, restart,
  Kontrola duplicit, Sync, nový GEDCOM a `--ged-id --zapsat`), 1. kotvy (dvojice ke spojení), 2. nové osoby se vztahem,
  3. osoby ve stromu s novými údaji (zápisy, obrázky, rozpory), 4. rozpory dat u ostatních (strom × projekt, „doloženo
  zápisem“). Přepis jen s `--prepsat`. Bez jakékoli vazby `ged` nástroj skončí s radou `--ged-id`.
- Ověřeno na kopii skutečného projektu: 91 nových, 12 kotev, 30 změněných (jen v přehledu), 3 obsazená místa, 1 chráněná
  kotva (č. 7). Testy `tests/gedcom/test_ged_vazba.py` (33 kontrol).
- **Zkouška na kopii (24. 11. 2026, čerstvý strom z FTB, 258 osob):** 84 nových, 10 kotev; Kontrola duplicit našla
  **2 z 10 kotev** (oba s úplným datem narození i úmrtí ve stromu, shoda 60 %); osoba A
  (strom: jen rok úmrtí) ani kotvy bez dat nalezeny nebyly; jeden falešný nález nové osoby (dvě různé ženy se stejným křestním jménem, 30 %). Přehled proto u každé kotvy uvádí „Kontrola duplicit ji nejspíš najde“ / „spojte ručně“.
  Dřívější starý strom (28. 10.) neznal osoby přidané později (dvě osoby) → upozornění na strom
  starší než týden a hledání možných shod nových osob v celém stromu (jméno, pohlaví, roky).
- **Kontrola duplicit se sníženou citlivostí** (po importu, 52 nálezů): **8 z 10 kotev** (40–60 %); nenašla kotvu
  (kotva s dvojicí rodičů navíc) a chráněnou osobu (tehdy „Žijící osoba“). Nálezů je ale mnoho i mimo import (starší
  podobnosti ve stromu) a jeden chybný návrh (nová osoba × jiná osoba stromu stejného jména – rozhodnuto „jiná“). **ID ve FTB po
  importu = pořadí osoby v souboru** (1, 2, 43…; strom má 500…) – ověřeno shodou všech 8 dvojic. Přehled proto uvádí
  u kotvy „spojit ID N × ID 500…“, u nové osoby její ID a u možných shod „dvojici … nespojujte“. Odhad „najde / ručně“
  podle dat ve stromu zrušen (při snížené citlivosti neplatí).
- **Zbývá:** ruční zkouška celého postupu ve FTB na kopii projektu (import `pracovni/rozdil`, spojení 12 kotev
  v Kontrole duplicit, kontrola nových osob a fotek); `SIDE` beze změny (poznámky); rozpor údajů jen hlásí.

Výhody: zůstane stávající strom včetně Smart Matches, Record Matches, online fotek a **propojení DNA testů**.
Ruční práce jen se slučováním kotev a změněných osob.

Práce v FTB je **úplně ruční** (rozhodnutí uživatele): skill vyrobí jen rozdílový GEDCOM a přehled změn, import,
spojení duplicit i Sync dělá uživatel. FTB je potřeba jen pro tuto variantu; před každým importem záloha
v FTB (File → Backup). Neautomatizovat: FTB nemá API ani příkazovou řádku, veřejné API MyHeritage už není,
zápis přímo do `.ftb` riskuje poškození synchronizace a úpravy webu přes prohlížeč porušují `soukromi.md`
(zkušenost se zablokovaným účtem).

### Další možnosti (nepreferované)
- **Celý nový strom** (`--sloucit`): původní `.ged` + nová zjištění → kompletní GEDCOM, nahrát jako nový
  strom a starý smazat. Čisté, ale ztratí se Smart/Record Matches, online fotky, spolupracovníci a vazba DNA.
  Jen pro stromy bez DNA a bez hodnotných online dat. **Zatím neimplementovat** (až bude potřeba, doplnit i test).
- **Jen přehled změn** (`--jen-prehled`): bez GEDCOM, ruční zadání na webu. Nejbezpečnější, nejvíc práce.
  Vzniká stejně v kroku 4, takže stačí volba.

### Rozpor údajů
Jiné datum v MyHeritage a v matrice: v přehledu změn označit a jako výchozí doporučit údaj doložený zápisem
(`st="doc"`).

## Ověření (fáze 2)
- Test s malým původním `.ged` + projektem s jednou novou osobou, jednou změněnou a jednou beze změny → rozdílový
  GEDCOM obsahuje novou, změněnou a kotvu, ne nezměněnou; přehled změn odpovídá.
- Test migrace: stávající projekt s importovaným stromem dostane správné `ged`, neshoda jména se ohlásí.
- Test druhého kola: po doplnění `ged` novým osobám je `--rozdil` prázdný.
- Ruční zkouška v FTB na kopii projektu (ne na synchronizovaném stromu): import s „Merge into project“,
  spojení duplicit, kontrola výsledku před Sync.

---

## Poznámka
Úpravy dělat v klonu (cesta v `CLAUDE.local.md`) (ne v cache pluginu) a postupovat podle
„Postup po každé úpravě skillu“ a „Vydání verze“ v `CLAUDE.md` (zvýšit verzi na třech místech, README, CHANGELOG,
commit, `/plugin marketplace update`). Fáze 1 a fáze 2 vyjdou jako dvě samostatné verze; mění-li fáze 2 formát
`osoby.py` (pole `ged`), otestovat i aktualizaci projektu založeného předchozí verzí.
