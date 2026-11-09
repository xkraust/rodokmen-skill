# Plán: úvodní fotka bez ořezu a nové pořadí sekcí na úvodní stránce

Datum: 9. 11. 2026

Stav: implementováno ve verzi 0.9.4 dne 9. 11. 2026, ověřeno na ukázkovém projektu včetně screenshotů z headless Chrome. Do projektu Krausovi zatím nepromítnuto.

## Cíl

1. Úvodní fotka (`uvod.foto`) se nebude oříznutá tak, aby zmizela podstatná část záběru (například těla lidí na rodinné fotografii na výšku).
2. Na úvodní stránce se změní pořadí sekcí. Nové pořadí shora:
   1. nadpis a úvodní blok s fotkou (`.teaser`) – beze změny,
   2. čtyři čísla (předci, doloženo, generace, zápisy) – beze změny,
   3. **Zajímavosti** (pokud nějaké jsou),
   4. **Rodokmen** (mobilní strom a náhled vějíře s tlačítky),
   5. **Rody** (karty rodů),
   6. **Kde žili naši předci** (mapa) – nově úplně na konci.

## Ověřený současný stav

- Fotku určuje `uvod.foto` v `data/web.json`. Export (`skills/rodokmen/tools/export_web.py`) zkopíruje `vyrezy/<klíč>.jpg` do `web/public/img/`. Fotka se zobrazí jen tehdy, když je vyplněné `uvod.nadpis` nebo `uvod.odstavce`.
- V projektu s více weby (Krausovi) se `data/web.json` hluboce sloučí s částí `web` v `data/weby/<varianta>.json` (`skripty/web_varianty.py`). Varianta spolecny používá `web.json` beze změny, krausovi a havlickovi mají vlastní `uvod`, včetně fotky. Úprava šablony se proto týká všech variant najednou.
- `vyrez.py` ukládá do `vyrezy/` obrázek zmenšený nejvýše na 1800×1800 px. Poměr stran zůstává podle zdroje.
- Styl `.teaser img` v `skills/rodokmen/template/web/src/styles/global.css` (řádek 170): `width: 100%; max-height: 300px; object-fit: cover; object-position: center 22%`. Sloupec fotky má při širokém okně asi 600 px, takže rámeček je přibližně 600×300 (poměr 2:1) a vše mimo se ořízne.
- Fotky na výšku tím trpí: rodinná fotka 832×1293 ukáže asi 32 % výšky (od 15 % do 47 %), čtvercový portrét 1800×1800 asi 50 % (od 11 % do 61 %). Hodnota `22 %` je nastavená pro fotografie na šířku.
- `skills/rodokmen/template/web/src/pages/index.astro` má sekce v pořadí: úvod, čísla, Zajímavosti, Kde žili naši předci (mapa), Rody, Rodokmen.
- Pořadí položek v menu (`src/layouts/Base.astro`) s tím nesouvisí a měnit se nebude.

## Postup implementace

### 1. Fotka bez ořezu

V `global.css` upravit `.teaser img` a jeho odkaz:

- Fotka se zobrazí celá, bez ořezu: `width: auto; height: auto; max-width: 100%; max-height: 420px; object-fit: contain; display: block`.
- Odkaz kolem fotky (`.teaser > a`) vycentrovat ve sloupci (`justify-self: center`), aby fotka na výšku nezůstala přilepená k okraji.
- Zaoblené rohy ponechat. Kvůli fotkám na výšku nevytvářet pozadí ani rámeček navíc.
- Na mobilu (pod 760 px) fotka zůstane pod textem, s omezením výšky přibližně na 60 % výšky okna, aby nezabrala celou obrazovku.
- Šablonu `index.astro` pro fotku neměnit: HTML zůstává stejné, rozhoduje jen CSS.

Doplňkově zvážit volitelné pole `uvod.foto_pozice` v `web.json`. Použilo by se jen tehdy, když by někdo fotku chtěl přesto vyplnit celý rámeček s ořezem. V první verzi ho nepřidávat, pokud se při kontrole ukáže, že řešení výše stačí. Úvahu dopsat do výsledku.

### 2. Nové pořadí sekcí

V `skills/rodokmen/template/web/src/pages/index.astro` přesunout celé bloky, bez změny jejich obsahu:

1. Zajímavosti (podmínka `cards.length > 0`) zůstanou na stejném místě po čtyřech číslech.
2. Rodokmen (nadpis `Rodokmen`, `.only-mobile` s `MobileTree`, `.fan-preview` a odkazy) přesunout hned za Zajímavosti.
3. Rody (nadpis `linesTitle(...)` a karty, podmínka `lineList.length > 0`) přesunout za Rodokmen.
4. Kde žili naši předci (`FamilyMap`, podmínka `site.places.length > 0`) přesunout na konec.

Zachovat všechny podmínky zobrazení, aby stránka fungovala i bez zajímavostí, rodů nebo míst.

### 3. Dokumentace

- Doplnit `skills/rodokmen/reference/web.md` o pořadí sekcí na úvodní stránce a poznámku, že fotka se zobrazuje celá.
- Zkontrolovat, jestli `SKILL.md` nebo `reference/pribehy.md` nepopisují pořadí sekcí nebo ořez fotky; případné zmínky opravit.
- Neměnit formát `web.json`, takže uživatelská data zůstanou kompatibilní.

### 4. Vydání verze 0.9.4

Podle `CLAUDE.md`:

- zvýšit číslo ve třech místech: `.claude-plugin/plugin.json`, `skills/rodokmen/VERZE`, README (na dvou místech, s datem vydání),
- doplnit nahoru `CHANGELOG.md` sekci `## 0.9.4 – D. M. 2026` (Nové / Opravy / Návody),
- commit, aktualizace pluginu v Claude Code (`/plugin marketplace update rodokmen-skill`, `/reload-plugins`), ověření, a teprve potom `git push origin main`; tag a vydání na GitHubu až po pushi a na pokyn.

## Ověření před dokončením

- Ukázkový projekt: `novy_projekt.py ~/Rodokmen-ukazka --ukazka`, `npm install`, `npm run data`, `npm run build`. V sestaveném `dist/index.html` zkontrolovat pořadí nadpisů: Zajímavosti, Rodokmen, Rody, Kde žili naši předci.
- Úvod bez zajímavostí, bez míst a bez rodů: stránka se sestaví a sekce nechybí ani nezůstanou prázdné nadpisy.
- Zobrazení na počítači a mobilu v prohlížeči: fotka na výšku (832×1293), čtvercová (1800×1800) a na šířku. Žádná se nesmí oříznout a nesmí vzniknout zbytečně velká prázdná plocha vedle textu.
- Mapa na konci stránky se správně načte (Leaflet se inicializuje i mimo první obrazovku) a odkaz „Celá mapa…“ funguje.
- Béžové okraje na rodinné fotce Krausových: po zobrazení celé fotky zkontrolovat, jestli jsou součástí skenu. Pokud ano, doporučit přeříznutí přes `vyrez.py` s oblastí; samotný obrázek se bez souhlasu uživatele nemění.
- Aktualizace projektu založeného předchozí verzí: `novy_projekt.py` na stejnou složku, `npm install`, `npm run data`, `npm run build` (`tests/aktualizace/test_aktualizace.py skills/rodokmen`). Změna se týká jen šablony webu, ne formátu mezi `tools/` a `template/web/`.
- Nesmí selhat existující testy webu v `tests/` (spustit celou sadu, ne jen aktualizační test).

## Promítnutí do existujícího rodokmenu (Krausovi)

Úprava je zatím jen v šabloně v tomto repozitáři. Aby se projevila na webu:

1. Po vydání verze spustit `novy_projekt.py` na `C:\Users\tomas\Můj disk\Rodokmen\Krausovi`. Zkontrolovat, jestli v hlášení nejsou konflikty ve `web/src/pages/index.astro` nebo `web/src/styles/global.css` (pokud má projekt vlastní úpravy, soubory se sloučí třícestně nebo se uloží záloha do `pracovni/zaloha_<datum>/puvodni/`).
2. `skripty/web_varianty.py build vse` a náhled přes `skripty/nahled.py <varianta> <port>` pro všechny tři varianty (spolecny, krausovi, havlickovi). Varianta havlickovi nemá fotku, takže u ní se kontroluje jen nové pořadí sekcí.
3. Nasazení (`web_varianty.py nasadit <varianta>`) jen na výslovný pokyn uživatele.

## Otevřené otázky

- Maximální výška fotky: navržených 420 px je odhad. Doladit při kontrole v prohlížeči, případně zvolit jinou hodnotu pro počítač a pro mobil.
- Zda má smysl pole `uvod.foto_pozice` (viz výše), nebo stačí zobrazení celé fotky.

## Výsledek implementace a ověření

- `global.css`: `.teaser img` zobrazuje fotku celou (`object-fit: contain`, `max-height: 420px`, na mobilu `60vh`), odkaz kolem ní je vycentrovaný ve sloupci (`justify-self: center`). Starý ořez `cover` s pozicí `center 22%` je pryč.
- `index.astro`: bloky přesunuté beze změny obsahu a podmínek. Pořadí: úvod, čísla, Zajímavosti, Rodokmen, Rody, Kde žili naši předci.
- `reference/web.md`: popis pořadí úvodní stránky a rada ořezat okraje fotky ve `vyrez.py`. `SKILL.md` ani `pribehy.md` pořadí ani ořez nepopisují, beze změny. Pole `uvod.foto_pozice` nepřidáno, zobrazení celé fotky stačí.
- Verze 0.9.4: `plugin.json`, `VERZE`, README (obě místa), `CHANGELOG.md`.
- Aktualizace projektu: ukázka založená verzí 0.9.3 (worktree `HEAD`) a aktualizovaná novou šablonou přes `novy_projekt.py` (2 soubory přepsány bez vlastních úprav), `npm install`, `npm run data`, `npm run build` prošly. V `dist/index.html` jsou nadpisy v pořadí Zajímavosti, Rodokmen, Osm rodů, Kde žili naši předci.
- Vizuální kontrola (headless Chrome nad `dist/`, testovací fotka s červenými okraji): na šířce 1440 px fotka 832×1293, 1800×900 i 1800×1800 celá a vycentrovaná, všechny okraje viditelné. Na šířce 600 px (mobilní rozvržení) fotka pod textem, celá, výška 60 % okna. Mapa na konci stránky se načte i s body. Šířka 390 px se v headless Chrome nedala spolehlivě nasimulovat (minimální šířka okna), na skutečném telefonu ověřit.
- Testy: `aktualizace` 20/20, `verze` 22/22, `portrety` 15, `mista` 39/39, `kontrola` 65/65, `web/test_cloudflare` 34/34, `web/test_nginx` 8/8 (nginx -t přeskočeno bez Dockeru), další testy nástrojů prošly. `web/test_overit` 12/13 – selhává stejně i bez této změny (pád Node na Windows `UV_HANDLE_CLOSING`). `brzda/test_brzda` 24/25 – zátěžový test časování brzdy archivů, šablony se netýká.
- Béžové okraje u fotky `foto_krausovi_rodina` zatím neověřeny – ukážou se až po promítnutí do projektu Krausovi.
