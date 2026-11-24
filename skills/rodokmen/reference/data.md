# Formát dat projektu

Všechna data jsou v `data/`. Web se z nich generuje (`npm run data`), nikdy needituj `web/src/data/site.json` ručně.
Po změnách spusť `python3 -I tools/kontrola.py`. Ukázku vyplněných dat má `SKILL_DIR/template/ukazka/`.
Položky do JSON souborů přidávej a měň přes `python3 -I tools/zapis.py` (zachová formát souboru, viz SKILL.md).

## `osoby.py` – předci
Kekulého čísla: 1 = výchozí osoba, otec osoby n = 2n, matka = 2n+1.
| číslo | kdo |
|---|---|
| 1 | výchozí osoba (u ženy `sex="F"`) |
| 2, 3 | otec, matka |
| 4–7 | prarodiče (4, 5 otcovi rodiče; 6, 7 matčini) |
| 8–15 | pradědečci a prababičky = **8 rodů** (`LINES`) |
| 16–31, 32–63 … | každá další generace dvojnásobek |

Otec předka 22 je 44, matka 45; dítě předka 45 je 22 (45 // 2). Muži mají sudá čísla.

```python
P = {
 8: dict(n="Jan Novák", y="1890–1944", st="doc",
         f=["* 14. 2. 1890 Holice čp. 112", "kovář", "× 20. 6. 1919 Holice Josefa Pokorná", "† 1944 Holice"],
         r=["holice_krest_jan_novak_1890", "holice_snatek_jan_novak_josefa_pokorna_1919"],
         note="Proč nejistota / rozpor / odkud údaj"),
 9: dict(n="Josefa Pokorná", y="* 1895", st="doc", f=[...], r=[...]),
 33: dict(n="otec neuveden", st="unk", f=[], note="Nemanželský syn; otec v matrice není."),
}
```
- `n` jméno (ženy rodným příjmením), `y` roky pro přehledy (`"* 1895"`, `"1890–1944"`, `"asi 1720–1785"`, `"1680 – před 1740"`,
  `"† 1940"` když známe jen úmrtí; nic nevíme → `""`).
- `f` fakta: začínají `*` (narození), `×` (sňatek), `†` (úmrtí) nebo jsou volný text (řemeslo, bydliště).
  Názvy obcí ve faktech používá mapa (`mista.json` → `re`).
  Sňatek jmenuje partnera (`× 1919 Holice Josefa Pokorná`); `kontrola.py` hlásí, když žádný sňatek nejmenuje osobu
  na sousedním čísle (manžel 2k, manželka 2k+1, i přes `SAME`). U `doc` hlásí `čp.`, které není v žádném citovaném
  zápisu (`shrnuti`, přepis) jako číslo domu (`čp. 23`, `No 23`, `N. 23`, `[Dům] 23`, `z Ostřetína 23`; datum, věk ani
  číslo zápisu, strany či snímku neplatí); číslo převzaté odjinud označ ve faktu zdrojem: `* 1862 Ostřetín čp. 23 (podle stromu)`.
  Datum piš hned za značku (`× 20. 6. 1919 Holice …`, ne `× Holice 20. 6. 1919`). Web z faktu `*` počítá věk při sňatku
  a úmrtí (`× 20. 6. 1919 (29 let)`), u zápisů osoby a u sňatku na stránce rodiny. Úplná data dají přesný věk
  (u dětí měsíce či dny); jen rok, `asi`/`≈` nebo `st: "prob"` → „asi 54 let“; `před`/`po` nebo chybějící `*` → bez věku.
  Proto do `*` zapisuj co nejpřesnější datum narození, i když `y` má jen roky.
- `r` klíče zápisů ze `zaznamy.json`; přidávej je `python3 -I tools/zapis.py odkaz <číslo> <klíč> [<klíč> …]` (u `SIDE`
  místo čísla část jména) – nástroj zachová zbytek souboru a ověří, že zápis existuje. `st` viz `matriky.md`: `doc` přečteno v matrice, `prob` pravděpodobné,
  `fam` od rodiny (i strom, který si rodina vede sama, např. GEDCOM z jejího MyHeritage), `mh` cizí strom z internetu, `unk`.
- `LINES = {8: ("Novákové", "Kováři z Holic…"), …}` – jen čísla 8–15; název rodu = příjmení v množném čísle. Vyplň hned, jak znáš pradědečka nebo prababičku – bez LINES web neukáže rody a nepřijde rada k příběhu.
- `SIDE` – sourozenci a další příbuzní: `dict(k=<číslo předka>, n="Josef Novák (1865–1920)", t="text", r=[klíče])`.
- `ISSUES` – dvojice `("Otázka", "Vyřešeno: … / Hypotéza: … / Otevřené: …")` → stránka „Co hledáme“ (vyřešené se skryjí).
  Jde na web – nepiš sem citlivé věci (příčiny úmrtí, rodinné spory) bez souhlasu.
- `HYPOTEZY` – `dict(rod=8, nadpis="…", text="…", polozky=[("jméno", "text")], zaznamy=[klíče])` → stránka rodu.
- `SAME = {350: 140}` – předek, který je v rodokmenu dvakrát (alias → hlavní číslo; alias v `P` může mít `f=["TÁŽ OSOBA jako 140"]`).

## `zaznamy.json` – zápisy
```json
[{"klic": "holice_krest_jan_novak_1890", "svazek": "1a0b2337", "snimek": 57, "druh": "N",
  "datum": "14. 2. 1890", "nazev": "Křest Jana Nováka",
  "shrnuti": "Jan, syn Václava Nováka, kováře v Holicích čp. 112, a Barbory roz. Malé z Ostřetína.",
  "odkaz": "https://aron.vychodoceskearchivy.cz/apu/…/dao/…/file/…"}]
```
- `klic`: malá písmena bez diakritiky, `obec_druh_kdo_rok` (druh: krest, snatek, umrti, index, scitani…). Je to i název obrázku.
- `druh`: N, O, Z, I (index/rejstřík), S (sčítání – jeden zápis na sčítací arch, klíč v `r` všech členů domácnosti;
  vzor přepisu v `scitani.md`), J (jiný pramen).
- `datum` jako v češtině („14. 2. 1890“, „3/1867“, „1797“) – web podle něj řadí.

## `svazky.json`
`{"1a0b2337": {"archiv": "SOA Zámrsk – Sbírka matrik…", "portal": "ARON", "svazek": "N Holice 1880–1900, sign. …",
"popis": "obce", "url": "odkaz na svazek"}}` – u ARON zapisuje `aron_img.py <apu> svazek`.

## `prepisy.json`
`{"<klic>": {"orig": "[Datum] 14. února 1890\n[Dům] 112\n[Otec] …", "cs": "Český překlad celou větou…"}}`
- `orig` věrný přepis po sloupcích, `[Název sloupce]` v hranatých závorkách, nejisté „(?)“, nečitelné „[…]“, zkratky ponechat.
- `cs` srozumitelný překlad pro rodinu; vysvětli staré pojmy (domkář, podruh).

## `zvyrazneni.json`
`{"<klic>": {"boxes": [[x0, y0, x1, y1]], "status": "ok", "note": ""}}` – zlomky šířky/výšky obrázku `vyrezy/<klic>.jpg`.
Zapisuje `ramecek.py`. Rámeček má obepnout celý čtený zápis (ne jen jméno).

## `mista.json`
`{"Holice": {"re": "Holic", "dotaz": "Holice, Česko", "lat": 50.066, "lon": 15.986}}` – `re` je regulární výraz hledaný
ve faktech osob (kmen slova, aby sedělo skloňování: „Holic“ najde Holice i v Holicích). Spravuje `mista.py`.
Pozor na kolize (Hradec Králové × Nový Hradec Králové – použij `(?<!Nový )Hradec`; krátká jména jako `\bBuku?\b`).
Hypotéza: `"hypoteza": true, "rod": 8`. Když OpenStreetMap obec nenajde („Žár“, malé osady), zkus třetí parametr – dotaz: `mista.py pridej "Žár" "Žár" "Žár, Zdíkov, okres Prachatice"`
nebo dotaz s větší obcí či okresem. U **víceznačných názvů** (Podolí, Dub, Lhota) vezme OpenStreetMap kteroukoli ves
(„Podolí, Česko“ = Podolí u Brna) – v posledním sloupci výpisu zkontroluj okres a dej dotaz se sousední obcí
(`mista.py pridej "Podolí" "Podol" "Podolí, Odlochovice"`). Místopis nejlíp zná rodina – když si nejsi jistý, zeptej se.
`mista.py` hledá jen sídla a pod seznamem upozorní, když našel něco jiného než obec (bar, ulici) nebo když je nový bod
víc než 50 km od všech ostatních míst projektu (nejspíš jiná obec stejného jména). Kontrola mapy (`kontrola.py`) u
předků bez obce vypíše v hranatých závorkách slova z faktů, která vypadají jako obec. Když je obec v `mista.json`,
jen ji výraz `re` nechytí ve skloňovaném tvaru („v Přesece“ × `Přesek`) – uprav výraz (`Přese?[kc]`).

## `dokumenty.json` – rodinné fotky a dokumenty na webu
`[{"img": "foto_svatba_1919", "popis": "Svatba Jana a Josefy, Holice 1919.", "osoby": [8, 9]}]` – `popis` je na webu
vidět jako popisek, vyplň ho (stejně jako `t` u bočních příbuzných).
Obrázek ulož přes `vyrez.py dokumenty/<sken>.jpg foto_svatba_1919` (vznikne `vyrezy/` i `zdroje/`).

### Portréty osob

Při prohlížení dokumentů nabídni samostatnou fotografii jedné osoby jako portrét. Skupinová fotka, koláž ani
tvář uvnitř dokumentu nejsou hotový portrét; případný výřez domluv zvlášť. Posouzení obrázku je návrh, ne jistota.
Když obrázek nemůžeš zobrazit, požádej o popis či označení, nepředstírej rozpoznání. Identitu neodhaduj z obličeje:
použij přiřazení od rodiny nebo v evidenci; při nejasnosti se zeptej, kdo na snímku je.

Nabídka například: „Na fotografii `IMG_1234.jpg` je jedna osoba a snímek by se hodil jako portrét. Chcete ho použít
na stránce Josefa Krause vedle jména a událostí? Pak se nebude zobrazovat v dokumentech.“ Uživatel může souhlasit,
ponechat fotku mezi dokumenty nebo rozhodnutí odložit. Před souhlasem nic nepřejmenovávej ani nepřesouvej mezi sekcemi.

Po souhlasu oznam konkrétní jméno: „Pro web fotografii uložím jako `josef_kraus_portret.jpg`.“ Další souhlas se
stejným krokem nevyžaduj. Vstupní originál v `dokumenty/` ponech pod původním názvem; slovo „přejmenováno“ použij
jen pro skutečně přejmenované soubory. Přejmenování samotného originálu musí být součástí nabídky uživateli.
Po úspěšném zpracování potvrď výsledek a do `data/udaje_od_rodiny.md` zapiš datum, původní soubor, osobu, rozhodnutí
(ano / ne / odloženo) a výsledný klíč. Neopakuj vyřízené nabídky, odložené řeš později v odpovídajícím kontextu.

**Nová fotografie:** ověř volný klíč, vytvoř webové kopie a přidej položku přes `zapis.py`:

```text
python3 -I tools/vyrez.py dokumenty/IMG_1234.jpg josef_kraus_portret
python3 -I tools/zapis.py dokumenty josef_kraus_portret pracovni/portret.json
```

Obsah `pracovni/portret.json` (číslo 2 nahraď skutečným číslem osoby):

```json
{"img": "josef_kraus_portret", "popis": "Josef Kraus, rodinná fotografie.", "osoby": [2]}
```

Rozhodující je klíč v `img` a název výsledného JPG. Export rozpoznává podřetězec `portret` kdekoliv v názvu,
bez ohledu na diakritiku a velikost písmen: `portrét`, `PORTRET`, `PoRtRéT`. Samotný původní název nestačí.
Při odmítnutí použij neutrální webový klíč bez tohoto označení, i když ho původní soubor obsahuje; změnu vysvětli.

**Již evidovaná fotografie:** nejprve vyhledej použití starého klíče v projektu. Příkaz má náhled a kontroluje
kolize; při kolizi vyber volný klíč. Nikdy nepřidej druhý dokument jen kvůli změně názvu:

```text
python3 -I tools/zapis.py dokumenty foto_josef --prejmenovat josef_kraus_portret --nahled
python3 -I tools/zapis.py dokumenty foto_josef --prejmenovat josef_kraus_portret
```

Příkaz zachová ostatní pole položky, přejmenuje existující JPG ve `vyrezy/`, `zdroje/`, `web/public/img/`
a `web/public/zdroje/`. Opraví klíč v `web.json`, klíč zvýraznění a odkazy na JPG v textových souborech `data/`
a vlastních šablonách `web/src/` (i URL s diakritikou). Originály nemění. Při chybě vrátí provedené změny.
Pokud klíč sdílí matriční zápis, přejmenování odmítne; připrav samostatnou kopii fotografie s novým klíčem.
Nestandardní odkazy (např. vlastní skripty skládající název) oprav podle výsledku vyhledání. Pak ve `web/`
spusť `npm run data` a `npm run build`, aby se obnovily generované stránky a vyhledávání.

**Osoba už portrét má:** nabídni ponechání nebo nahrazení. Při nahrazení přejmenuj předchozí portrét na neutrální
klíč bez `portret` (oznámíš, že se vrátí mezi dokumenty), potom označ nový. Když uživatel ponechá původní,
nový snímek zůstane běžným dokumentem. Pro ručně připravená data export použije první existující portrét v pořadí
`dokumenty.json` a upozorní na další. Chybějící soubor přeskočí; chybějící či víceznačné přiřazení oznámí.
Portrét musí mít právě jednu známou osobu; více čísel téže osoby přes `SAME` nevadí. Portréty se nezobrazují
v žádné ze dvou galerií dokumentů, ani jako nevybrané alternativy.

## `web.json` – nastavení webu
Viz `web.md`.

## Markdown poznámky
- `research_log.md` – tabulka `| # | datum | zdroj | rozsah | hledáno | výsledek | citace |`, nové řádky na konec, i negativní.
  Web ji zobrazuje jako „Výzkumný deník“.
- `zajimavosti.md` – `## Nadpis` + text, odkazy `[Jméno](/osoba/<slug>/)`.
- `pribeh.md` – „Příběh <hlavního rodu>“: frontmatter `title`, `lead` + kapitoly `##`; když soubor neexistuje,
  položka menu se skryje. Jak psát: `pribehy.md`.
- Poznámky pro Clauda v markdownu piš jako `<!-- … -->` – na web nejdou.
- `archivni_dotazy.md`, `udaje_od_rodiny.md` – volný text.

## Odkazy na osoby (slug)
Slug = jméno bez diakritiky + rok, např. `jan-novak-1890`; při kolizi přidá číslo osoby. Přesné slugy po `npm run data`
v `web/src/data/site.json` (`people`). Při přejmenování osoby se slug změní – oprav odkazy v textech.

## Import rodinného stromu (Fáze 1)
- **GEDCOM** (`.ged`, export z MyHeritage/Geni/FamilySearch): `python3 -I tools/ged_import.py dokumenty/strom.ged "Jméno Příjmení"`
  vypíše předky s čísly, všechny události a poznámky a **frontu zápisů** (nejmladší známá událost u každého předka,
  a jestli už je v archivu). `--osoby` dá kostru pro `osoby.py`. Poznámky ve stromu bývají plné rodinných historek –
  přečti je a vytěž do `udaje_od_rodiny.md`.
- Starší strom z **Brother's Keeper** (kódování ANSI a česká data „SRPEN 1945“ nástroj převede sám): místa tam bývají
  v 6. pádě („Táboře“) – do `osoby.py` je přepiš do 1. pádu. Kořenem takového stromu často nejsou uživatel, ale jeho
  děti (oba rody) – výchozí osobu proto vyber jménem.
- **Záloha stromu z MyHeritage** (ZIP se souborem `<strom>.ftb` a složkou `Photos/` – databáze, ne GEDCOM): rozbal do
  vlastní složky v `dokumenty/` (bývá velká – dej ji do `.gitignore`), pak
  `python3 -I tools/ftb_export.py <strom.ftb> dokumenty/strom.ged "Jméno Příjmení" <rok narození> pracovni/prima_linie.md <složka Photos>`.
  Vznikne GEDCOM pro `ged_import.py` (bez adres, e-mailů a telefonů) a přehled přímé linie s **původem údajů** – u každé
  osoby, ze kterých cizích stromů (Smart Match) či zdrojů její údaje přišly. Osoba bez cizí citace = `fam`, doložená jen
  cizími stromy = `mh`. V přehledu jsou i připojené skeny (opisy matrik, parte, domovské listy) – přečti je, bývají to
  nejcennější rodinné doklady.
- Údaje ze stromů (i Smart Match) jsou jen vodítko k zápisu – datum a číslo domu tě dovedou na stránku, ale **jména vždy
  ověř v zápisu** (skutečná chyba: „sňatek“ ze Smart Match byl jiný pár ze stejného domu).

## Export do GEDCOM
`python3 -I tools/ged_export.py` → `pracovni/rodokmen.zip`: `rodokmen.ged` (GEDCOM 5.5.1, UTF-8) a složka `media/`
s výřezy zápisů, rodinnými fotkami a portréty. ZIP se **rozbalí** (`rodokmen.ged` a `media/` vedle sebe) a importuje
se `.ged` – obrázky si program načte podle relativních cest (Gramps ano, **Family Tree Builder ne**). **Pro import
rovnou použij `--slozka`**: nástroj zapíše rozbalenou složku `pracovni/rodokmen/` (s `--koren 3`
`pracovni/rodokmen_koren3/`), ZIP nevznikne a cesty k obrázkům jsou **absolutní** – Family Tree Builder je načte.
Složku před importem nepřesouvej (po přesunu export zopakuj). Výřez zápisu je v citaci u události a se `--slozka`
i přímo u osoby (FTB obrázky z citací zahodí – formulář citace pole pro obrázek nemá). Se `--slozka` je navíc
zdrojem jeden zápis (titul „zápis, svazek, snímek“, archiv svazku) s výřezem – FTB ho ukáže ve „Zdrojích fotografií“;
bez `--slozka` je zdrojem svazek. Soubor ve složce je UTF-8 s BOM a CRLF – bez BOM FTB špatně přečte cestu
s diakritikou a obrázky nenačte. Obrázky ve složce jsou v plném rozlišení ze `zdroje/` (jinak `vyrezy/`),
`--plne-rozliseni` je u `--slozka` zbytečné.
- **MyHeritage s obrázky:** jen přes desktopový **Family Tree Builder** (zdarma): export s `--slozka`, File → Import GEDCOM →
  `rodokmen.ged` z té složky (z ručně rozbaleného ZIPu FTB obrázky nenačte – „Failed to Load Image“) → nový projekt (nebo „Merge into project“), zkontrolovat fotky u osob, pak **Sync** – strom i obrázky
  se nahrají na web. Web MyHeritage přijímá jen `.ged` (ZIP odmítne) a obrázky z GEDCOM nenačte nikdy (soubor
  obsahuje jen odkazy na ně); nahrání jen `.ged` na web = strom bez obrázků, fotky pak jen ručně.
  Pro MyHeritage exportuj s **`--cp-v-miste`**: číslo popisné jde i do místa události („Holice čp. 112, okres …“),
  protože adresu (`ADDR`) u narození, sňatku a úmrtí MyHeritage nezobrazí (jeho vlastní stromy mají číslo domu
  v místě, např. „Obora č.21“). Každý dům je pak pro MyHeritage samostatné místo (rozpoznání místa a mapa ho
  mohou vynechat) – proto to není výchozí; bez volby je čp. jen v adrese (Gramps ji zobrazí).
- **Gramps:** importovat rozbalený `.ged`.
Volby: `--bez-obrazku` (jen `pracovni/rodokmen.ged`), `--plne-rozliseni` (i výřezy ze `zdroje/`), `--vystup <soubor>`,
`--koren <číslo>` (jen tato osoba a její předci, např. `--koren 3` = maminčina strana jako samostatný strom; čísla osob
zůstanou, aliasy `SAME` z jiné větve se přiberou i s předky; výchozí soubor `pracovni/rodokmen_koren3.zip`).
Existující soubor nástroj nepřepíše (jen s `--prepsat`), do `web/` nezapíše a hlídá příponu (`.zip`, s `--bez-obrazku` `.ged`).
U `--slozka` nahradí `--prepsat` jen `rodokmen.ged` a `media/`; složku s jinými soubory nepřepíše nikdy.
- Rodiny se odvozují z čísel (otec 2k, matka 2k+1), aliasy `SAME` jsou jedna osoba, zástupní rodiče („otec neuveden“)
  se nevyváží. Fakta se převádějí na události: `*`, `×` (sňatek v rodině), `†`; datum do tvaru GEDCOM (`asi` → ABT,
  `před` → BEF, `po` → AFT, `mezi … a …` → BET), obec podle `mista.json` (název z OpenStreetMap a souřadnice),
  `čp.` do adresy, závorky do poznámky. Ostatní fakta jsou povolání nebo poznámka. `SIDE` → poznámka u osoby,
  stav `st` → kvalita citací a poznámka „Původ údajů“. `LINES`, `ISSUES` a `HYPOTEZY` se nevyvážejí.
- Prameny: svazek = `SOUR` (archiv jako `REPO`), zápis = citace se snímkem, shrnutím, přepisem a výřezem. Zápis se cituje
  u události jen při shodě druhu a roku – křest syna v `r` otce není otcovo narození, ten se cituje u osoby.
- **Soukromí:** žijící (poznámka „Žijící…“, bez úmrtí a narození v posledních 100 letech) a zemřelí před méně než 30 lety
  zůstanou jen jako „Žijící osoba“ (vazby bez údajů, fotek a zápisů). U lidí z posledních ~100 let se vynechá poznámka
  a příčina úmrtí, boční příbuzní z té doby a dokumenty s chráněnou osobou také. Zápis, ve kterém je i chráněná osoba,
  jde bez obrázku a přepisu – souhrn ho vypíše ke kontrole. `udaje_od_rodiny.md` se nevyváží.
- **Před exportem se vždy zeptej, jestli má export obsahovat i žijící osoby** (a kam soubor půjde). Vysvětli rozdíl:
  bez nich jsou žijící a nedávno zemřelí jen „Žijící osoba“ (údaje si uživatel doplní ručně); s nimi (`--zijici`) jsou
  v souboru jejich jména, data, místa, poznámky i fotky. Nahráním do cizí služby (MyHeritage, Ancestry…) je dostane
  i ta služba – u vlastního stromu je MyHeritage ostatním skrývá, ale data u ní budou. Výchozí odpověď je „ne“;
  `--zijici` použij jen na výslovné „ano“ a připomeň souhlas dotčených (`soukromi.md`). Na web takový soubor nepatří.
  Když projekt leží ve složce synchronizované do cloudu (Google Disk, OneDrive, Dropbox), řekni, že soubor s žijícími
  dostane i ten cloud, a nabídni ho po nahrání smazat.
- Projdi s uživatelem souhrn na konci (chránění, vynechané, chybějící obrázky, data, která nešla převést) dřív, než
  soubor nahraje. Nahrání GEDCOM na web MyHeritage vytvoří **nový samostatný strom** (se stávajícím se nesloučí).
