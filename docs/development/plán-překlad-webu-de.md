# Plán: jednorázový překlad rodinného webu do němčiny

Datum: 18. 11. 2026

Stav: obecný vzor, nic neimplementováno. Skill se nemění.

**Provedení (18. 11. 2026):** německý web se bude dělat pro samostatný projekt uživatele, ne pro jeho hlavní rodokmen. Ten nemá `web_varianty.py` ani varianty, proto má vlastní upravený plán `plán-web-de.md` v kořeni projektu (složka toho projektu) a odkaz na něj v jeho `CLAUDE.md`. Postup níže zůstává vzorem pro případný překlad webů hlavního rodokmenu. Odchylky plánu pro ten projekt: stínový projekt mimo Disk místo varianty, překlady krátkých textů podle klíčů s otiskem originálu místo slovníku „česky → německy“.

## Cíl

Vytvořit německou verzi rodinného webu jako jednorázový snímek: samostatný web se samostatným přihlášením pro německy mluvící příbuzné. Pokud by se měl překlad pravidelně obnovovat, převést řešení na vlastnost šablony (viz poslední sekce).

## Ověřený současný stav

Na webu jsou dvě vrstvy textu.

**Texty rozhraní** (malý objem):
- Stránky a komponenty v `skills/rodokmen/template/web/src/` (asi 900 řádků, překlad potřebuje jen malá část).
- `src/layouts/Base.astro` má natvrdo `<html lang="cs">`. Pagefind podle atributu `lang` volí jazyk vyhledávání.
- `skills/rodokmen/tools/export_web.py` skládá české věty: vztahy (`relation()`), roky, výchozí titulek „Příběh“.
- `skills/rodokmen/tools/fan_chart.py` má v SVG vějíře české popisky („známých předků v … generacích“, „doloženo matrikou“, „pravděpodobné“, „zatím neznámé“).
- Dále `prihlaseni.sablona.html` a stránka 404.

**Obsah** v `data/` projektu (počet slov podle `wc -w` k 18. 11. 2026):

| Soubor | Slov |
|---|---|
| `pribeh.md` | 1 250 |
| `zajimavosti.md` | 556 |
| `research_log.md` (deník) | 16 263 |
| `archivni_dotazy.md` | 983 |
| `osoby.py` (poznámky, včetně kódu) | 11 188 |
| `zaznamy.json` | 7 731 |
| `prepisy.json` | 17 052 |
| `mista.json` | 708 |
| `dokumenty.json`, `web.json` | asi 600 |

V projektu už je mechanismus variant: `skripty/web_varianty.py` připraví upravenou kopii dat, nad ní spustí běžný `tools/export_web.py` a hotový web uloží do `%LOCALAPPDATA%\Temp\rodokmen-weby\<varianta>`. Nastavení variant je v `data/weby/<varianta>.json`. Složky `skripty/` a `data/` při aktualizaci skillu `novy_projekt.py` nepřepisuje, `tools/` a `web/src/` ano (tříčestným slučováním).

## Postup

### 1. Německá varianta ve `web_varianty.py`

- Přidat variantu `<základní varianta>-de` (např. `rodina-de`, podrobnosti v kroku 5) s nastavením v `data/weby/rodina-de.json`. Která česká varianta (případně které) dostane německou verzi, rozhodne uživatel. Níže se v cestách používá `de` jako zkratka.
- Překlad je samostatná vrstva, původní data se nemění:
  - `data/weby/de/*.md`: přeložené `pribeh.md`, `zajimavosti.md` (a případně zkrácený deník)
  - `data/weby/de/preklad.json`: slovník „český text → německý text“ pro krátké texty (poznámky u osob, souhrny zápisů, popisy rodů a míst, `dokumenty.json`)
- Varianta při přípravě dat nahradí markdownové soubory a do kopie `osoby.py` a JSON souborů doplní překlad ze slovníku. Texty, které ve slovníku chybí, vypíše jako seznam k doplnění.

### 2. Rozhraní v kopii webu

- Před buildem varianta `de` zkopíruje `web/` do `pracovni/weby/de/` a v kopii nahradí české texty podle slovníku `skripty/preklad_rozhrani_de.json`. Slovník je v `skripty/`, kam aktualizace skillu nesahá.
- Stejně nahradí texty, které skládá `export_web.py`, a popisky ve vějíři z `fan_chart.py`: buď úpravou výstupu (`site.json`, SVG), nebo kopií obou skriptů upravenou pro variantu.
- `lang="de"` v `Base.astro`.
- Při překladu kopie zkontrolovat hledáním, že nezůstaly české texty (diakritika `ěščřžýáíéůú` ve výstupu `dist/` mimo vlastní jména a přepisy).

### 3. Rozsah překladu

- **Přeložit:** příběh, zajímavosti, poznámky u osob, souhrny zápisů, místa, popisy rodů, dokumenty, rozhraní.
- **Nepřekládat:** přepisy matrik zůstanou v originále (latina nebo němčina). Přeloží se jen případný český výklad.
- **Vynechat nebo jen krátce shrnout:** deník (`research_log.md`) a archivní dotazy. Pro německého čtenáře mají malou hodnotu a tvoří velkou část objemu. Stránky deníku a hledaných předků lze ve variantě skrýt nebo nahradit krátkým shrnutím.

### 4. Glosář (před samotným překladem)

Soubor `data/weby/de/glosar.md`, ze kterého se při překladu vychází:
- stavy a povolání: sedlák → Bauer, chalupník → Kleinhäusler, domkář → Häusler, podruh → Inwohner, výměnkář → Ausgedinger…
- místa: český název s historickým německým názvem v závorce, např. „Třebíč (Trebitsch)“, podle `mista.json` a historických lexikonů
- archivy: oficiální název ponechat a vysvětlit německy (SOA → Staatliches Gebietsarchiv)
- jména osob: tak, jak jsou v matrice, bez počeštění i poněmčení
- data: německý formát (`18. November 1850`)

### 5. Přihlášení a publikování

Rozhodnutí (18. 11. 2026): web nebude mít přepínač jazyků. Německá verze bude samostatný web s kódem jazyka v adrese.

**Zvolená podoba: samostatný web, kód jazyka v názvu hostitele**

| Česky | Německy |
|---|---|
| `rodina-rodokmen.netlify.app` | `rodina-de.netlify.app` |
| `rodina.<subdoména>.workers.dev` | `rodina-de.<subdoména>.workers.dev` |
| (vlastní doména) `rodina.example.cz` | `de.rodina.example.cz` nebo `rodina.example.cz` → `rodina.example.de` |

- Varianta se jmenuje `<základní varianta>-de`, např. `rodina-de`, a nastavuje se v `data/weby/rodina-de.json`:
  - `"zaklad": "rodina"`: převezme `koren`, `rody` a další nastavení základní varianty, takže se rodokmen nemusí popisovat podruhé
  - `"jazyk": "de"`: zapne překladovou vrstvu z kroků 1 a 2
  - vlastní `netlify_site` a `cloudflare_worker` (`rodina-de`)
  - přeložené `rody` a `web` (název, úvod, přeložená otázka; odpověď se nepřekládá)
- `web_varianty.py` musí umět `zaklad` (sloučit nastavení základu s nastavením varianty) a `jazyk`. Ostatní příkazy (`build`, `nasadit`, `nasadit-cf`, `nahled.py`) fungují beze změny.
- Přihlášení (rozhodnutí 18. 11. 2026): stejná otázka jako na českém webu, jen přeložená do němčiny, a stejná odpověď beze změny, takže i stejný otisk. Odpověď se při přípravě varianty bere vždy z originálního `web.json`. Weby jsou na různých adresách, takže se na každém přihlašuje zvlášť, ale stejným heslem.
- Česká a německá verze se sestavují a nasazují nezávisle. Nasazení české verze německou nijak neovlivní.
- Na úvodní stránku přidat „Stand: <datum>“, protože jde o snímek.
- Volitelně jediný nenápadný odkaz v patičce českého webu („Deutsche Version“) a naopak. Nejde o přepínač, jen o odkaz na úvodní stránku druhého webu (ten se ptá na své vlastní heslo). Vyžaduje jeden řádek v `Base.astro` řízený z `web.json`, tedy úpravu šablony. Proto zatím ne.
- Nasazovat jen na pokyn uživatele. Nový web na Netlify nejdřív založit (`netlify sites:create`) a jeho ID zapsat do `netlify_site`.

**Zamítnutá podoba: cesta `/de/` na stejném webu** (`rodina-rodokmen.netlify.app/de/`)
- Astro by potřebovalo `base: '/de/'` a v šabloně je asi 24 pevných odkazů od kořene (`/osoba/…`, `/pagefind/…`), navíc `fan_hrefs.json` z exportu. Všechny by se musely přepsat, a tím by se změnila šablona skillu.
- Brána (Netlify edge funkce i Cloudflare worker) zná jen jednu cookie `rodokmen` a jeden otisk. Oba jazyky by tedy měly stejnou otázku, nebo by se brána musela přepsat.
- `netlify deploy` nahrazuje celý web. Každé nasazení by muselo složit českou i německou verzi do jedné složky, jinak by jedna smazala druhou.

### 6. Kontrola

- `python -I -X utf8 skripty/web_varianty.py build de`
- náhled: `skripty/nahled.py de 4334`
- projít úvodní stránku, vějíř, mapu, osobu, rod, zápisy a vyhledávání (německé hledání přes Pagefind)
- hlášky exportu o nefunkčních odkazech a zbylé české texty

## Slabiny

- Překlad nesleduje pozdější změny dat ani šablony. Po aktualizaci skillu může náhrada textů v rozhraní přestat sedět (změněný text ve stránce se už nenahradí). Varianta proto vypíše nenahrazené položky slovníku.
- U textů z `osoby.py` je náhrada podle přesného znění křehká: změněná poznámka vypadne z překladu.

## Skill ano, nebo ne

- **Jednorázově:** samostatný skill nedělat. Postup, glosář a skript v projektu stačí, napsání a odladění skillu by zabralo víc času než samotný překlad.
- **Pokud by se překlad opakoval** (obnovování, další jazyky): ani pak nedělat zvláštní skill, ale vlastnost šablony v pluginu:
  - `"jazyk": "de"` v `data/web.json`
  - texty rozhraní ve slovníku (`src/i18n/cs.json`, `de.json`) místo natvrdo ve stránkách; totéž v `export_web.py` a `fan_chart.py`
  - obsahové překlady v `data/preklady/<jazyk>/`, které `export_web.py` použije místo originálu, a kontrola chybějících překladů
  - návod v `skills/rodokmen/reference/web.md` (případně nový `reference/preklad.md`), aby stávající skill rodokmen překlad vedl
  - jde o změnu formátu mezi `tools/` a `template/web/`, takže je potřeba otestovat aktualizaci projektu založeného starší verzí. Vhodné k nabídnutí do upstreamu.
