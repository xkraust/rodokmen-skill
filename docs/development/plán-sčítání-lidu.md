# Plán: sčítání lidu jako pramen

Datum: 12. 11. 2026

Stav: **implementováno ve verzi 0.11.0 (12. 11. 2026)** – návod `reference/scitani.md`, odkazy v ostatních
návodech, `portafontium.py scitani` / `domy` (+ `info`, `snimek`, `link`, `svazek` pro dům), test
`tests/portafontium/test_scitani.py`, zápis sčítání v ukázce. Ověřeno na skutečném projektu (Zbyslav čp. 43, 1921).
Zbývá: body v „K ověření“ 1 a 3–7 (ostatní portály jsou v návodu označené „neověřeno“); nástroj pro ARON jen
po ověření, že starší operáty mají snímky. Body označené **[ověřit]** níže je potřeba ověřit přímo na portálu
(v prohlížeči, ne skriptem tam, kde to brzda `tools/slusne.py` nepovoluje).

Poznámka z implementace: `ramecek.py` při zápisu přeformátuje celý `zvyrazneni.json` (`indent=1`), na rozdíl
od `zapis.py`, který mění jen jednu položku – v ukázce s kompaktním tvarem to dělá velký diff. Kandidát na opravu.

## Cíl

Aby skill uměl uživateli nabídnout sčítací operáty (1857–1921) tam, kde pomohou: věděl, kdy se vyplatí, kde jsou
v jednotlivých krajích online, jak je číst, přepsat a citovat a jak je zapsat do dat a na web. Nový nástroj jen tam,
kde to archiv dovolí a kde ušetří práci.

## Rozhodnutí

- **Žádný nový skill.** Sčítání se přidá do stávajícího skillu `rodokmen` (rozhodnutí uživatele 12. 11. 2026).
  Důvody: stejný postup a stejná data projektu (`zaznamy.json` s druhem `S`, `prepisy.json`, `osoby.py`, web),
  společné nástroje a brzda, jedna verze, žádné soupeření dvou skillů o stejné dotazy.
- Podrobnosti budou v novém návodu **`skills/rodokmen/reference/scitani.md`**, který se čte až při potřebě.
  `SKILL.md` dostane jen krátký odkaz, `portaly.md`, `metodika.md` a `matriky.md` jen odkazy a opravy.
- Jako vzorový arch slouží **Zbyslav čp. 43, 1921** (Havlíčkovi, rodina uživatele). Do veřejných souborů skillu
  (návod, ukázka) ale jdou jen struktura a fiktivní jména. Skutečné údaje patří do projektu uživatele.

## Ověřený současný stav v repozitáři

- `skills/rodokmen/reference/matriky.md:11` – jedna věta: sčítání lidu 1857–1921, „domácnosti s daty narození“,
  operáty 1930 jen v Národním archivu a nejsou online.
- `skills/rodokmen/reference/portaly.md:281-286` – podrobný postup jen pro **MZA Brno**
  (`https://www.mza.cz/scitacioperaty/digisada/search`, jen prohlížeč, sada = obec + rok, snímek 1 = soupis s rozpisem
  čísel popisných, 1857 jen rok narození, 1869 a 1880 i místo a datum, svislý sloupec dat).
- `skills/rodokmen/reference/portaly.md:39` – „v ARON jsou i další fondy (sčítání lidu …) – `aron_search.py "Obec" "název fondu"`“;
  název fondu neuveden, postup nevyzkoušený.
- `skills/rodokmen/reference/metodika.md:117` – Slovensko: „Slovakia, Census, 1869“ na FamilySearch.
- `skills/rodokmen/reference/metodika.md:173-190` – tabulka milníků bez let sčítání (jen 1651, 1654, 1770/71).
- `skills/rodokmen/reference/metodika.md:82-85` – postup „kniha se nedochovala“ zmiňuje soupisy (konskripce), sčítání ne.
- `skills/rodokmen/reference/data.md:58-59` – druh zápisu `S` (sčítání), klíč `…_scitani_…`;
  `skills/rodokmen/tools/export_web.py:29` – na webu „sčítání lidu“. Vzor přepisu pro arch sčítání chybí.
- `skills/rodokmen/template/ukazka/` – žádný zápis druhu `S`.
- Žádný nástroj v `skills/rodokmen/tools/` sčítací operáty nehledá ani nestahuje.
- Brzda `tools/slusne.py`: MZA – skriptem jen hledání matrik; SOA Třeboň a SOA Praha – skriptem nic (od 2. 11. 2026);
  Porta fontium – Crawl-delay 10 s; ZA Opava – přísné limity na obrázky; ARON – povoleno.

## Zjištění z webu (12. 11. 2026)

### Kde jsou sčítací operáty online

| Archiv | Portál podle zdrojů | Roky | Poznámka |
|---|---|---|---|
| MZA Brno | `mza.cz/scitacioperaty/digisada/search` (v repo); inventář `mza.cz/a8web/A8Apps1/XTRSO02/XTRSO02-Inventar.pdf` | 1857–1921, částečně | v repo popsáno |
| SOA Třeboň | `digi.ceskearchivy.cz/Census` | 1857–1921 | jen prohlížeč (brzda) **[ověřit]** strukturu |
| SOA Plzeň | `portafontium.eu/contents/census` (přehled po soudních okresech a letech) | 1857–1921 podle okresu | **ověřeno 12. 11. 2026**, viz níže |
| SOA Litoměřice | `vademecum.soalitomerice.cz` (ikona „osoby“) | 1857–1921 | **[ověřit]** vyhledávání a snímky |
| ZA Opava | `digi.archives.cz/da/` | 1857–1921 | **[ověřit]**; přísné limity obrázků |
| SOA Zámrsk | ARON | po okresních archivech | viz níže |
| SOA Praha | eBadatelna (archiválie) | 1869, 1880, 1900, částečně | jen prohlížeč (brzda) |
| AHMP | katalog Praga Publica | 1869–1921 | katalog; **[ověřit]** snímky |
| AM Brna, AM Ostravy | digiarchiv.brno.cz, amo.ostrava.cz | ? | **[ověřit]** |
| Národní archiv | – | 1930 a mladší | online nejsou, jen žádost |

Zdroje: MyCzechRoots (článek asi 13 let starý, odkazy mohou být zastaralé), FamilySearch Wiki „Czechia Census“
(upraveno 3. 11. 2026).

### Porta fontium (SOA Plzeň) – ověřeno na obci Zbyslav (soudní okres Plánice)

- **Přehled:** `https://www.portafontium.eu/contents/census` – tabulka okres × rok (1857–1921), u každé buňky
  odkaz `/census/<archiv>/<rok>/okres-<soudní-okres>`, např. `/census/soap-kt/1921/okres-planice`. Archivy: `amp`
  (Archiv města Plzně), `soap-ch`, `soap-do`, `soap-kt` … (SOkA). Které roky má který okres, se liší:
  Klatovy, Nýrsko a Plánice 1880–1921, Domažlice 1857–1921, Hartmanice, Kašperské Hory a Sušice jen 1921.
- **Stránka okresu a roku:** seznam obcí a osad s počtem domů, např. `Zbyslav (46 domů)`, s odkazem na
  `/iipimage/<id>` (první dům) a „souhrn“ (soupis obce). Název obce je i německy v atributu `title`.
- **Hledání (záložka „Sčítání lidu“, `/searching/census`, pole Nadpis / Místo / Text / roky)** skriptem nevrací
  výsledky ani pro Kdyni. Výsledky se nejspíš načítají JavaScriptem. Použitelná cesta je přehled → okres → obec.
- **Sada = obec × rok, rozdělená po domech:** každé číslo popisné je samostatná stránka `/iipimage/<id>`. Na stránce
  je navigace „Nr. 1 · Nr. 2 …“ s odkazy na `/iipimage/<id>` dalších domů (id jdou po sobě, ale chybějící čp. se
  přeskakují – ve Zbyslavi 1921 chybí čp. 40) a odkazy na stejnou obec v jiných letech („1880 – 1890 – 1900 – 1910 – 1921“).
- **Snímky:** stejné jako u matrik – `data-iip-path="census/soap-kt/census-1921-okres-planice/zbyslav/cp043/
  soap-kt_01159_census-1921-zbyslav-cp043_0010.jp2"`, server `/fcgi-bin/iipsrv.fcgi?IIIF=<path>/full/<size>/0/default.jpg`
  (ověřeno: náhled pct:25 = JPEG 76 kB). Trvalý odkaz na snímek: `/iipimage/<id>/<název souboru bez .jp2>`.
  Čp. 43 má 3 snímky: 1 = **sběrný arch domovní** (země, soudní okres, obec, čp., majitel domu, byty a počet osob),
  2–3 = sčítací arch s osobami.
- **Zbyslav:** 1880 jako osada „Újezd u Plánice – Zbyslav“ (`/iipimage/34441229`, 42 domů), 1890 (`/iipimage/34443819`,
  42 domů), 1900 (`/iipimage/34443862`, 43 domů), **1910 v seznamu chybí**, 1921 (`/iipimage/34443905`, 46 domů;
  čp. 43 = `/iipimage/34443948`). Pozor: obec může být v jednom roce samostatně a v jiném jako osada jiné obce.
- **Dopad na nástroj:** `portafontium.py` umí snímky přes IIIF a trvalé odkazy. Chybí mu jen čtení stránky `/iipimage/<id>`
  místo `/register/…` a průchod přehled → okres → obec → čp. Rozšíření je malé, Crawl-delay 10 s platí
  (průchod jedné obce ≈ 3 dotazy + 1 na dům).

### ARON – ověřeno dotazem na API

- Pole `name` obsahuje „sčítání“ u 562 popisů archiválií – drtivá většina je **SOkA Jičín, ONV – sčítání lidu, domů
  a bytů 1980** (pro rodokmen nepoužitelné, a navíc mladé).
- Samostatné fondy „Sčítací operáty“: **SOkA Náchod – Sčítací operáty 1900–1910**, **SOkA Svitavy (Litomyšl) –
  Sčítací operáty z obcí okresu Svitavy**. Popisy zatím bez strukturovaného popisu.
- Starší operáty (1857–1921) jsou ve Východních Čechách nejspíš uložené ve fondech obcí a okresních úřadů,
  ne pod slovem „sčítání“ v názvu. **[ověřit]** jak je najít a zda mají snímky (`aron_img.py <id> info`).
- `aron_search.py` filtruje vždy pole `name` a pevně `type = ARCH_DESC`; fond se zadává jako druhý argument.
  Pro sčítání by šlo použít, ale chybí ověřený příklad.

### FamilySearch a placené databáze

- **„Czech Republic Censuses and Inhabitant Registers, 1800–1990“, kolekce 1930345** – snímky z Litoměřic, Trutnova
  (SOkA), Třeboně, Brna a Opavy; pro oblast Zámrsku i **jmenný rejstřík**. Katalog má záznamy po obcích
  („Czech Republic, <okres>, <obec>, census, 1869–1921“). Nové snímky přibývají. **[ověřit]** zda je potřeba
  přihlášení (skill už pro FamilySearch postup s přihlášeným prohlížečem má, `portaly.md:318`).
- Ancestry „Czech Republic, Censuses, 1857–1921“ (dbid 60253) a MyHeritage 1900, 1910 a 1921 (rejstřík a snímky)
  jsou placené. Zmínit jen jako možnost, nástroj ne.

### Obsah jednotlivých ročníků

- Rozhodné dny: 31. 10. 1857, 31. 12. 1869/1880/1890/1900/1910, 15. 2. 1921.
- 1857: německé formuláře, rok narození (v repo z MZA). 1869: jméno, pohlaví, **rok a místo narození**, náboženství,
  stav, povolání, **domovská příslušnost** – zásadní ročník. Od 1880 navíc obcovací řeč a gramotnost
  (vlastní znalost, **[ověřit]** na snímku). 1921 kompletní archy, území ČSR.
- Archy zachycují celou domácnost včetně nepřítomných, vztah k hlavě domácnosti. Někdy je přiložen výpis z matriky
  (hlavně u mladých mužů).
- Dochovanost záleží na obci. Na Moravě jsou starší ročníky úplnější.

## Mezery

1. **Kdy sčítání použít.** Metodika neříká, že sčítání 1921 (případně 1910) nahradí matriky narozených ze svazků,
   které jsou kvůli lhůtě 100 let od posledního zápisu ještě na úřadě (`matriky.md:29`). Chybí také ověření složení
   domácnosti a hledání sourozenců, místa narození přistěhovalých (1869+) a domovské obce.
2. **Kde je najít.** Pro Čechy a Slezsko není nic konkrétního. FamilySearch se u sčítání zmiňuje jen pro Slovensko.
3. **Nesoulad.** `matriky.md:11` uvádí „data narození“, 1857 přitom má jen rok.
4. **Milníky.** V tabulce v `metodika.md` chybí roky sčítání a jejich obsah.
5. **Přepis a citace.** Chybí vzor přepisu archu (`[Dům]`, `[Osoba]`, `[Vztah]`, `[Narozen]`, `[Místo narození]`,
   `[Náboženství]`, `[Povolání]`, `[Domovská obec]`) a vzor citace (archiv, fond, obec, rok, čp., číslo archu, snímek).
6. **Data.** Chybí zápis `S` v ukázce. Technicky jeden arch k více osobám připojit jde – každá osoba má vlastní
   seznam `r` a `export_web.py:318` bere každý klíč, který je v `zaznamy.json` (ověřeno). Chybí jen pokyn v `data.md`,
   že klíč archu patří do `r` všech členů domácnosti.
7. **Nástroje.** Žádné. Skriptem by šlo jen ARON a možná Porta fontium (census) a FamilySearch (přes prohlížeč).

## Návrh úprav

### 1. Nový návod `reference/scitani.md` (bez nového kódu)

Osnova:
1. **Kdy sčítání použít:** narození ze svazků, které jsou ještě na matričním úřadě (1921, 1910), složení
   domácnosti a sourozenci, místo narození přistěhovalých (od 1869), domovská obec, tchyně, výměnkáři a bratři
   v domě (vztahy, které matriky neukážou), kontrola věku a data narození (arch může mít jiný rok než matrika –
   matrika má přednost, rozpor zapsat).
2. **Ročníky:** rozhodné dny, co který obsahuje (1857 jen rok narození, 1869 a dál datum a místo, 1921 viz vzor),
   jazyk formulářů, 1930 a mladší jen Národní archiv na žádost.
3. **Struktura sady:** obec × rok, souhrn obce, po domech sběrný arch domovní (majitel domu, byty, počet osob) a
   sčítací arch pro každý byt. Červená čísla tužkou jsou statistické kódy úřadu – nepřepisovat.
4. **Portály po krajích:** Porta fontium (postup přehled → soudní okres → obec → čp.), MZA (přesunout z `portaly.md`),
   Třeboň, Litoměřice, Opava, ARON, FamilySearch 1930345. Jen ověřené. U každého skript / jen prohlížeč.
5. **Pasti:** obec hledat podle **soudního** okresu (Zbyslav → Plánice, ne Klatovy), osada vedená pod jinou obcí
   (Zbyslav 1880 = „Újezd u Plánice – Zbyslav“), chybějící roky a čísla popisná, přečíslování domů, svisle psaná data.
6. **Přepis a citace:** vzor níže.
7. **Do dat:** jeden zápis `S` na byt (arch). Jeho klíč patří do `r` všech zapsaných osob z rodu, údaje do `f`
   („domkář ve Zbyslavi čp. 43 (1921)“). Vztahy z archu (tchyně, bratr) jsou nepřímý doklad – ověřit matrikou.

Vzor přepisu (`prepisy.json`, ověřeno na archu 1921, 20 sloupců; jména fiktivní):

```
[Arch] sčítání 1921, Čechy, soudní okres Plánice, obec Zbyslav, čp. 43, byt 1, bytová strana: Novák Jan, domkář
[1] Novák Jan | majitel bytu | muž | ženatý | * 26. 7. 1887 | Zbyslav, Plánice, Čechy | v obci od narození |
    domovská obec Zbyslav | česká | římskokatolické | čte a píše | zemědělství, samostatný majitel |
    16. 7. 1914: ano, zemědělství, samostatný rolník
[2] Nováková Anna | manželka | žena | vdaná | * 4. 8. 1888 | …
[Podpis] Novák Jan, 16. 2. 1921; sčítací komisař …
```

Sloupce 1921: 1 pořadí, 2 příjmení, 3 jméno, 4 poměr k majiteli bytu, 5 pohlaví, 6 rodinný stav, 7 den / měsíc / rok
narození, 8 rodiště (obec, soudní okres, země), 9 od kdy bydlí v obci, 10 domovská příslušnost, 11 národnost (mateřský
jazyk), 12 náboženství, 13 čtení a psaní, 14–16 povolání (druh, postavení, závod), 17–19 povolání 16. 7. 1914
(byl-li činný, druh, postavení), 20 poznámka. Pole `cs` = český souvislý text („V domě čp. 43 žil v únoru 1921
domkář Jan Novák (* 26. 7. 1887) s manželkou …“).

Citace (`svazky.json` / `odkaz`): archiv a fond (SOkA Klatovy, sčítací operáty 1921), soudní okres, obec, čp., snímek;
trvalý odkaz `https://www.portafontium.eu/iipimage/<id>/<soubor>`.

### 2. Úpravy stávajících návodů

- `SKILL.md`: dvě až tři řádky v části o hledání – kdy zkusit sčítání → `reference/scitani.md`; doplnit
  `scitani.md` do výčtu referencí na začátku.
- `reference/metodika.md`: do tabulky milníků řádky 1857, 1869, 1880–1910, 1921, 1930; do postupu „kniha se
  nedochovala“ sčítání; oddíl Slovensko ponechat.
- `reference/portaly.md`: oddíl MZA – sčítací operáty přesunout do `scitani.md`, nechat odkaz; řádek 39 (ARON)
  opravit podle ověření.
- `reference/matriky.md:11`: opravit „data narození“ a odkázat na `scitani.md`.
- `reference/data.md`: u druhu `S` odkaz na vzor přepisu v `scitani.md`.

### 2b. Data a web

- `template/ukazka/`: jeden zápis `S` (fiktivní arch 1921) s přepisem, aby byl vidět na webu.
- Ověřit, že `kontrola.py` a web zápis `S` zpracují správně (datum = rozhodný den sčítání, 15. 2. 1921).

### 3. Nástroje (volitelné, až po ověření)

- **ARON:** buď jen zdokumentovat `aron_search.py "<obec>" "Sčítací operáty"`, nebo přidat přepínač, který hledá
  v popisu archiválií mimo matriční fond. Nejdřív ověřit, zda mají snímky.
- **Porta fontium (ověřeno, stejné IIIF jako matriky):** rozšířit `portafontium.py` o
  `census <obec> [rok]` (přehled → okres → obec, vypíše roky a `/iipimage/<id>` včetně osad jiných obcí),
  `census-domy <id>` (čp. → id) a `snimek`/`link`/`svazek` i pro `/iipimage/<id>`. Crawl-delay 10 s dodržet,
  stránku okresu a obce kešovat (`pracovni/.cache_pf/`).
- MZA, Třeboň, SOA Praha: žádný nástroj (brzda), jen postup v prohlížeči.

### 4. Vydání

Podle `CLAUDE.md`: verze v `plugin.json`, `VERZE`, README (obě místa) a `CHANGELOG.md`. Kódové změny jen v bodě 3.
Formát mezi `tools/` a `template/web/` se nemění, test aktualizace starého projektu stačí, pokud se změní bod 2.

## K ověření před implementací

1. Třeboň `digi.ceskearchivy.cz/Census` – hledání obce, struktura sady, trvalý odkaz na snímek (v prohlížeči).
2. ~~Porta fontium census – adresa sady, IIIF, trvalý odkaz.~~ Ověřeno 12. 11. 2026 (Zbyslav). Zbývá zjistit,
   proč chybí Zbyslav 1910 (nedochováno, nebo jinde) a jestli hledání v prohlížeči najde obec bez znalosti okresu.
3. Litoměřice Vademecum – kde jsou operáty, zda mají snímky.
4. ZA Opava `digi.archives.cz` – zda jsou operáty v digitálním archivu a jak se hledají.
5. ARON – kde jsou starší operáty (1869–1921) pro obce východních Čech a zda mají snímky.
6. FamilySearch kolekce 1930345 – přihlášení, jmenný rejstřík pro Zámrsk, katalog po obcích.
7. Obsah ročníků 1880–1910 (obcovací řeč, gramotnost, domovská příslušnost) na skutečném snímku.
   Ročník 1921 ověřen na Zbyslavi čp. 43 (20 sloupců, viz vzor přepisu).

## Mimo rozsah

- Sčítání 1930 a mladší (online nejsou, citlivé údaje).
- Konskripce 1770/71 a soupis 1651 (už pokryté).
- Placené databáze (Ancestry, MyHeritage) – jen zmínka.
