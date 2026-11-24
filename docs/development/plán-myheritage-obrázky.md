# Plán: obrázky z exportu GEDCOM do MyHeritage (přes Family Tree Builder)

## Context
Uživatel nahrál na web MyHeritage `pracovni/rodokmen.zip` z `ged_export.py` a web ZIP odmítl („umí jen .ged“).
Ověřeno (nápověda MyHeritage, článek 12851303 a 12852096):
- Web přijímá jen soubor `.ged`. GEDCOM obsahuje jen odkazy na obrázky, ne obrázky samotné, a lokální cesty
  (`media/…jpg`) web nedosáhne. **Nahráním na web se fotky nepřenesou nikdy.** Navíc vznikne nový samostatný strom.
- Cesta s obrázky: desktopový **Family Tree Builder (FTB, zdarma)** – import `.ged` z rozbaleného ZIPu
  (FTB načte soubory podle `OBJE/FILE`), pak **Sync** s MyHeritage nahraje strom i fotky na web.
- Skill to dnes popisuje špatně: `reference/data.md:186` říká „ZIP se nahrává celý“ a otevřená otázka 2
  v `docs/development/plán-export-gedcom.md:189` zůstala neověřená.

## Okamžitá rada uživateli (bez úprav kódu)
1. Rozbalit `pracovni/rodokmen.zip` do vlastní složky (`rodokmen.ged` + `media/` vedle sebe).
2. Nainstalovat Family Tree Builder, přihlásit se účtem MyHeritage.
3. FTB: File → Import GEDCOM → `rodokmen.ged` → nový projekt (nebo „Merge into project“ do stávajícího stromu).
4. Zkontrolovat, že osoby mají fotky / výřezy zápisů; pak Sync → strom i s obrázky je na webu.
5. Alternativa bez FTB: nahrát jen `rodokmen.ged` na web a fotky přidat ručně u osob.

## Úpravy skillu (repo `Documents\VSCode\rodokmen-skill`)
1. **`tools/ged_export.py`** (ř. ~429, `FILE {path}`): přidat volbu `--absolutni-cesty`? – NE, nejdřív ověřit FTB
   s relativními cestami (krok Ověření). Pokud FTB relativní cesty nenačte, přidat výpis cest relativně ke složce
   `.ged` a do souhrnu na konci text „ZIP rozbal; pro MyHeritage importuj `.ged` ve Family Tree Builderu“.
   Jinak kód neměnit – stačí upravit závěrečnou zprávu nástroje (najít, kde tiskne souhrn) o tento návod.
2. **`skills/rodokmen/reference/data.md`** sekce „Export do GEDCOM“ (ř. 184–210): nahradit „ZIP se nahrává celý“
   přesným postupem: web MyHeritage = jen `.ged`, bez fotek; s fotkami = rozbalit ZIP → FTB import → Sync;
   Gramps = rozbalit a importovat `.ged`.
3. **`skills/rodokmen/SKILL.md`** (tabulka nástrojů, řádek ged_export) a **README.md:152–154**: opravit „ZIP pro MyHeritage“
   na zmínku o FTB.
4. **`docs/development/plán-export-gedcom.md`**: otevřenou otázku 2 (ř. 189) uzavřít – web: ne (ověřeno nápovědou);
   FTB: výsledek ruční zkoušky. Tento plán uložit i jako `docs/development/plán-myheritage-obrázky.md` (pravidlo CLAUDE.md).
5. Vydání: zvýšit verzi (`plugin.json`, `VERZE`, README 2×), `CHANGELOG.md` sekce „Návody/Opravy“, commit,
   `/plugin marketplace update rodokmen-skill`, `/reload-plugins`, push.

## Doplněno (0.12.2, 23. 11. 2026)
Volba `ged_export.py --slozka`: export rovnou rozbalený do `pracovni/rodokmen[_koren<N>]/` (`rodokmen.ged` + `media/`),
bez ZIPu, který web MyHeritage odmítá. `--prepsat` nahradí jen `rodokmen.ged` a `media/`; složku s cizími soubory
nepřepíše. Pro zkoušku ve FTB stačí importovat `.ged` z této složky.

Volba `--cp-v-miste`: číslo popisné i do `PLAC` („Holice čp. 112, okres Pardubice, …“), `ADDR` zůstane. Důvod:
uživatelův strom z MyHeritage (`dokumenty/strom.ged`, export FTB) nemá žádné `ADDR`, čísla domů jsou v místě
(„Obora č.21“, „Tlucná č.30“); recenze FTB 8 uvádí, že `ADDR` po importu nezobrazí. Výchozí zůstává čp. jen
v `ADDR` (čisté místo pro mapy a Gramps).

Ruční zkouška ve FTB (jedním importem): `ged_export.py --koren 3 --slozka --cp-v-miste` → import `.ged` →
1. jsou u osob a citací výřezy z `media/`? 2. je u narození vidět „čp.“ v místě? 3. má obec špendlík na mapě
(převezme FTB `MAP`/`LATI`/`LONG`)? Výsledky zapsat sem a do `plán-export-gedcom.md` (otevřená otázka 2).

## Výsledek zkoušky ve FTB (24. 11. 2026) → 0.12.3
Export Havlíčkovi (`--koren 3 --slozka --cp-v-miste --zijici`) naimportován do nového projektu FTB: 52 osob, 27 rodin
(sedí s exportem), data a místa převzata.
- **Relativní cesty (`FILE media/…`): FTB nenačte.** Obrázek je u osoby přiřazen (titulek sedí), prohlížeč hlásí
  „Failed to Load Image“, 0×0, 0 KB – i když soubor vedle `.ged` existuje.
- **Absolutní cesty: FTB načte** (zkušební kopie `.ged` s `FILE C:\…\rodokmen_koren3\media\…` (absolutní cesta do exportní složky); portrét vidět;
  cesta s diakritikou a na Google Disku nevadí).
- Oprava 0.12.3: `--slozka` zapisuje `FILE` jako absolutní cestu do `media/` výstupní složky (`Export.file_base`);
  ZIP a `--bez-obrazku` beze změny (relativní, pro Gramps a přenos). Test: „FILE je absolutní cesta“ (98 kontrol).
- **Obrázky v citacích (`2 SOUR` → `3 OBJE`): FTB zahodí.** Formulář citace ve FTB nemá pole pro obrázek (jen zdroj,
  stránka, hodnověrnost, datum, text, poznámky); u osob byly vidět jen 4 obrázky připojené přímo k osobě, 95 výřezů
  z citací chybělo. Oprava 0.12.3: s `--slozka` (`Export.cutouts_on_person`) jde výřez každého citovaného zápisu
  i jako `1 OBJE` k osobě (každý jednou; výřez sňatku u obou manželů, chráněné zápisy ne). V citaci zůstává (Gramps).
  Havlíčkovi: 108 obrázků u osob.
- **FTB umí obrázek u zdroje** („Upravit zdroj“ → „Zdroje fotografií…“, tj. `0 @S@ SOUR` → `1 OBJE`), ne u citace.
  Zvolena varianta „zdroj = zápis“ (proti „výřezy ke svazku“ – u svazku by nebylo poznat, který výřez patří ke které
  citaci): s `--slozka` (`Export.source_per_record`) má každý citovaný zápis vlastní `SOUR` s titulem
  „<název zápisu>, <svazek>, snímek N“, `REPO`/`CALN`/popisem svazku (`volume_lines`) a jedním `OBJE` s výřezem
  (chráněný zápis bez výřezu). ZIP beze změny (zdroj = svazek). Havlíčkovi: 20 zdrojů-zápisů, každý s výřezem.
  Testy 105 kontrol.
- **Zkouška 0.12.3 ve FTB: obrázky opět „Failed to Load Image“** (i portrét), přestože cesty byly absolutní a soubory
  v pořádku. Diagnostika třemi soubory (obrázky ve stejné složce `media`):
  T3 = přesná kopie exportu (UTF-8 bez BOM, LF) → **ne**; T2 = totéž + BOM + CRLF → **ano**;
  T1 = bez BOM, LF, ale každý obrázek jako záznam `0 @Mn@ OBJE` jednou a odkazy `n OBJE @Mn@` → **ano**.
  Závěr: FTB bez BOM čte vložené (`n OBJE` + `FILE`) cesty s diakritikou („Můj disk“) zřejmě v jiném kódování,
  i když hlavička uvádí `CHAR UTF-8` (proč první zkouška s absolutními cestami bez BOM prošla, nevysvětleno).
  Oprava 0.12.4: s `--slozka` se `.ged` zapisuje jako UTF-8 s BOM a CRLF (jako export MyHeritage); ZIP
  a `--bez-obrazku` beze změny. Varianta T1 (záznamy médií) zůstává v záloze. Testy 106 kontrol.
- Riziko: absolutní cesta prodlužuje řádek `FILE` (GEDCOM max. 255 znaků, `FILE` nejde dělit `CONC`); u hluboko
  vnořené složky by mohla limit překročit – zatím neřešeno (projekt na Google Disku je daleko pod limitem).
- Zbývá ověřit: čp. v místě (u osoby, která ho má, např. narození s „čp. 33“), špendlík na mapě, výřezy u osob,
  portrét jako hlavní fotka (`_PRIM`), hodnověrnost citace (FTB ukázal u `QUAY 2` „Sporná hodnověrnost důkazu“ –
  ověřit, jak FTB čísla 0–3 pojmenovává), a Sync na web s obrázky.
- Drobnost: fakt „* 10. 6. 1922 Zbyslav (?), okres Klatovy“ dal u narození navíc poznámky „?“ a „okres Klatovy“ –
  okres za čárkou se nebere jako součást místa. Řešit samostatně.

## Ověření
- `tests/gedcom/test_ged_export.py` projde (beze změny formátu `.ged`; 93 kontrol včetně `--slozka`).
- Ruční zkouška u uživatele: import rozbaleného ZIPu ukázkového projektu do FTB → fotky u osob viditelné →
  po Sync vidět na webu MyHeritage. Výsledek zapsat do `plán-export-gedcom.md`.
