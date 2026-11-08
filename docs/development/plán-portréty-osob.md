# Plán: portréty na stránkách osob

Datum: 8. 11. 2026

Stav: implementováno ve verzi 0.9.3 dne 8. 11. 2026. Automatické kontroly prošly; vizuální kontrola v prohlížeči zbývá, protože připojení prohlížeče nebylo dostupné.

## Cíl

Na stránce osoby zobrazovat její portrét vedle jména, štítků a výpisu událostí podle dodaného screenshotu. Portrét se nebude zobrazovat mezi rodinnými dokumenty ani ve společné galerii u příběhu rodu. Rozpoznání bude automatické podle názvu obrázku obsahujícího `portrét` nebo `portret`, bez ohledu na velikost písmen a zápis diakritiky.

Při prohlížení rodinných dokumentů má asistent navíc rozpoznat fotografii vhodnou jako portrét jedné osoby, oznámit to uživateli a nabídnout její použití. Teprve po souhlasu ji označí názvem pro portrét a oznámí konkrétní změnu názvu.

## Ověřený současný stav

- Rodinné fotografie jsou evidovány v `data/dokumenty.json`. Pole `img` obsahuje klíč obrázku bez přípony a pole `osoby` čísla osob, ke kterým fotografie patří.
- `skills/rodokmen/tools/vyrez.py` vytváří `vyrezy/<klíč>.jpg` pro web a `zdroje/<klíč>.jpg` v plném rozlišení.
- `skills/rodokmen/tools/export_web.py` vytváří seznam dokumentů každé osoby i společný seznam dokumentů a kopíruje obrázky do webu.
- `skills/rodokmen/template/web/src/pages/osoba/[slug].astro` vykresluje jméno, štítky, události a níže sekci Rodinné dokumenty.
- `skills/rodokmen/template/web/src/pages/pribehy/index.astro` vykresluje společnou galerii Rodinné dokumenty a fotografie.
- Řešení lze doplnit do současného exportu a šablony bez nové knihovny.
- `skills/rodokmen/SKILL.md` ve fázi 1 již ukládá asistentovi prohlédnout a vytěžit fotografie z `dokumenty/`. Sem lze doplnit vizuální posouzení a rozhovor s uživatelem. Současné Python nástroje obsah fotografií jako portrét neklasifikují.
- `skills/rodokmen/tools/zapis.py` používá `img` jako identifikátor dokumentu a vyžaduje jeho shodu s klíčem příkazu. Změnu klíče existující položky nepodporuje; zápis pod novým klíčem by přidal další položku.

## Postup implementace

### 0. Nabídka portrétu při prohlížení dokumentů

Rozšířit `skills/rodokmen/SKILL.md` ve fázi 1 a podrobný postup v `skills/rodokmen/reference/data.md`:

1. Při skutečném prohlížení obrázku vyhodnotit, zda jde o samostatnou fotografii jedné osoby vhodnou pro záhlaví její stránky. Nestačí samotný název souboru nebo jediná tvář uvnitř skenu dokumentu. Skupinové fotografie, koláže a dokumenty s vloženou fotografií automaticky nenabízet jako hotový portrét; případný výřez řešit zvlášť.
2. Oznámit zjištění jako návrh, například: „Na fotografii `IMG_1234.jpg` je jedna osoba a snímek by se hodil jako portrét. Chcete ho použít na stránce Josefa Krause?“ Jméno použít pouze tehdy, když přiřazení vyplývá z údajů uživatele nebo evidence. Když není známo, zeptat se také, komu fotografie patří; identitu neurčovat podle obličeje.
3. Před rozhodnutím stručně vysvětlit, že fotografie bude u jména a událostí a nebude v galerii dokumentů. Nabídnout použití jako portrét, ponechání mezi dokumenty nebo odložení rozhodnutí.
4. Po souhlasu oznámit konkrétní plánovaný název, například: „Pro web fotografii uložím jako `josef_kraus_portret.jpg`, aby se zobrazovala jako portrét.“ Po úspěšném zpracování potvrdit skutečný výsledek. Souhlas s touto nabídkou zahrnuje popsané pojmenování; nevyžadovat druhé potvrzení téhož kroku.
5. Rozhodnutí a vazbu původního souboru na osobu a výsledný klíč zaznamenat do `data/udaje_od_rodiny.md`, aby se zamítnutá či již vyřízená nabídka při dalším prohlížení neopakovala. Při odložení se k ní vrátit v odpovídajícím kontextu.

Vizuální posouzení provádí asistent při práci s dokumenty, nikoliv export webu. Může se mýlit; proto jde o návrh s rozhodnutím uživatele. Pro tento postup není potřeba přidávat knihovnu na rozpoznávání obličejů ani samostatnou službu. Bez možnosti skutečně zobrazit obrázek automatické posouzení neslibovat a vyžádat popis nebo označení uživatelem. Nepřetržité sledování složky není součástí návrhu.

#### Pojmenování a již evidované fotografie

- Doporučená varianta ponechá vstupní originál v `dokumenty/` pod původním názvem a označí jako portrét webové kopie v `vyrezy/` a `zdroje/` a klíč `img`. U nového snímku tak jde o uložení pod zvoleným názvem, nikoliv o přejmenování originálu; sdělení uživateli musí tento rozdíl přesně popsat.
- Pokud má být přejmenován také vstupní originál, musí to být součástí konkrétně popsané nabídky, včetně původního a nového názvu, a aktualizovat se musí jeho evidované odkazy. Pro funkci portrétu to není nutné.
- U již evidovaného obrázku přejmenovat existující webové kopie a změnit `img` ve stejné položce; nevytvářet druhou položku dokumentu. Zachovat popis a přiřazení osoby.
- Pro tento případ rozšířit `zapis.py` o explicitní změnu klíče existujícího dokumentu s kontrolou kolize. Soubory a související odkazy přejmenovat koordinovaně podle návodu; předem zkontrolovat cílové názvy a při chybě obnovit původní stav. Nepřepisovat jiný obrázek, při kolizi zvolit jedinečný název.
- Před přejmenováním vyhledat odkazy na starý klíč v datech a textech (například `web.json`, markdownové příběhy a případná zvýraznění), aktualizovat relevantní odkazy a znovu exportovat web. Zohlednit, že export nyní staré kopie v `web/public/` sám neodstraňuje; ověřit jejich využití a cíleně odstranit pouze nahrazené soubory bez dalších odkazů.
- Pokud osoba už portrét má, nabídnout ponechání současného nebo nahrazení novým. Při nahrazení vyřešit i označení původního obrázku, aby o výsledku nerozhodovalo náhodné pořadí dvou kandidátů. Pravidlo „první existující“ zůstává záložním chováním exportu pro ručně připravená data.
- Při odmítnutí nepřidávat označení `portret`. Jestli ho už obsahuje název vstupního souboru, použít po vysvětlení pro běžný dokument neutrální webový klíč bez tohoto označení, aby ho export přesto nevybral jako portrét.

### 1. Rozpoznání portrétu

V `skills/rodokmen/tools/export_web.py` přidat rozpoznávání podle názvu z pole `img`:

1. Normalizovat Unicode zápis názvu.
2. Odstranit diakritická znaménka a sjednotit velikost písmen.
3. Hledat podřetězec `portret` kdekoliv v názvu.

Příklady rozpoznaných názvů: `josef_portrét_1938`, `Josef_PORTRET`, `Josef_PoRtRéT`. Ověřeno i pro diakritiku zapsanou samostatným kombinujícím znaménkem. Normalizace slouží pouze k rozpoznávání; skutečný název souboru se tím nemění.

### 2. Oddělení portrétů při exportu

- Osobě exportovat samostatné pole `portrait` s obrázkem a popiskem, případně informací o dostupném plném rozlišení. Bez portrétu bude hodnota `null`.
- Přiřazení konkrétní osoby nadále odvozovat z `osoby`, nikoliv ze jména člověka v názvu souboru.
- Zohlednit alternativní čísla téže osoby v `SAME` a zabránit duplicitnímu výběru stejného obrázku.
- Portréty vyřadit z osobního i společného seznamu dokumentů.
- Zachovat kopírování obrázků portrétů do webu, i když už nebudou součástí seznamů dokumentů.

### 3. Vzhled stránky osoby

Upravit `skills/rodokmen/template/web/src/pages/osoba/[slug].astro` a odpovídající styly v `skills/rodokmen/template/web/src/styles/global.css`:

- Horní blok na větší obrazovce rozdělit na text vlevo a portrét vpravo, zarovnaný k začátku bloku.
- Textová část zahrne jméno, štítky a události. Portrét bude přibližně 220–260 px široký, s omezenou výškou a zachováním proporcí bez automatického ořezu obličeje.
- Poznámku osoby ponechat pod tímto blokem přes celou šířku.
- Na mobilu umístit portrét pod údaje a nad poznámku.
- Doplnit smysluplný alternativní text. Kliknutí otevře plné rozlišení, pokud existuje, jinak webovou verzi obrázku.
- U osoby bez portrétu nevytvářet prázdný rámeček ani rezervovaný sloupec. Šablona musí zvládnout i starší export bez pole `portrait`.

### 4. Nejednoznačné a chybové případy

- Při více portrétech vybrat první existující obrázek podle pořadí v `dokumenty.json` a při exportu vypsat upozornění.
- Chybějící soubor přeskočit a oznámit; nezobrazovat nefunkční obrázek.
- U portrétu bez platného přiřazení k osobě vypsat upozornění, aby nezmizel z galerií bez vysvětlení.
- Běžné rodinné dokumenty ponechat v dosavadních sekcích.

### 5. Návod pro přidání fotografie

Rozšířit `skills/rodokmen/reference/data.md` o pojmenování a příklad evidence portrétu; podle potřeby doplnit `skills/rodokmen/reference/web.md`.

Rozhodující je název zpracovaného obrázku v `img`, například `josef_kraus_portret`, nikoliv pouze původní název fotografie. Při zpracování přes `vyrez.py` je proto nutné označení zachovat v klíči. Fotografii nadále evidovat v `dokumenty.json` a přiřadit správné číslo osoby v `osoby`.

Tento postup využívá stávající přidávání fotografií; nezahrnuje vytváření formuláře pro nahrávání přímo na webu.

## Ověření před dokončením

- Na ukázkách samostatné fotografie, skupinové fotografie a dokumentu s vloženou fotografií ověřit správnou nabídku asistenta; nepovažovat vizuální klasifikaci za zaručenou.
- Ověřit rozhovor při souhlasu, odmítnutí, odložení, neznámé identitě a již existujícím portrétu. Před souhlasem se fotografie nesmí přejmenovat ani změnit její zařazení.
- Ověřit přesné oznámení nového názvu, zachování originálu v doporučené variantě a zaznamenání rozhodnutí bez opakované nabídky.
- Otestovat změnu klíče již evidovaného dokumentu: žádná duplicitní položka, zachované údaje, funkční odkazy, kontrola kolizí a zotavení z neúspěšného přejmenování.
- Rozpoznání variant s diakritikou, bez diakritiky, s různou velikostí písmen a s kombinujícími znaménky; běžná fotografie se nesmí označit za portrét.
- Správné přiřazení portrétu včetně alternativního čísla osoby, chybějícího souboru a více kandidátů.
- Portrét se zobrazí v horní části stránky a nebude v žádné ze dvou galerií dokumentů; běžné dokumenty zůstanou zobrazené.
- Zobrazení na počítači a mobilu, dlouhé jméno a události, fotografie různých proporcí a osoba bez portrétu.
- Funkční proklik na obrázek a dostupnost souborů ve výsledném webu.
- Export a sestavení ukázkového projektu pomocí `npm run data` a `npm run build`.
- Aktualizace projektu založeného předchozí verzí: `novy_projekt.py` na stejnou složku, `npm install`, `npm run data` a `npm run build`.

## Promítnutí do existujícího rodokmenu

Tento repozitář obsahuje šablonu webu. Pro zobrazení na existujícím rodokmenu je potřeba aktualizovat také jeho projekt a znovu vygenerovat web. Ověření proběhlo na odděleném ukázkovém projektu; uživatelův rodokmen se touto implementací neaktualizoval ani nenasazoval.

## Výsledek implementace a ověření

- Export rozděluje běžné dokumenty a portréty, kontroluje přiřazení a existenci obrázku, slučuje aliasy osoby a upozorňuje na více kandidátů.
- Stránka osoby zobrazuje portrét a popisek s proklikem; styly obsahují jednu kolonu pod 640 px a zachování proporcí fotografie.
- `zapis.py dokumenty <starý_klíč> --prejmenovat <nový_klíč> [--nahled]` koordinuje změnu evidence, odvozených JPG a známých odkazů. Originály zachovává; kolize odmítá a při chybě vrací provedené změny.
- Nabídka portrétu a rozhodování uživatele jsou popsány v `SKILL.md` a `reference/data.md`; scénáře souhlasu, odmítnutí, odložení a náhrady byly zkontrolovány v pokynech. Skutečný rozhovor s uživatelem nad novými fotografiemi nebyl součástí testu.
- `python -I -X utf8 tests/portrety/test_portrety.py -v`: 15 testů, včetně celého exportu, názvů shodných s poli datového formátu, zachování přihlašovacího nastavení a návratu změn při simulovaném selhání přejmenování i zápisu.
- `python -I -X utf8 tests/aktualizace/test_aktualizace.py skills/rodokmen`: 20 testů prošlo.
- Validátor `skill-creator/scripts/quick_validate.py`: skill je platný.
- Ukázkový projekt založený z upstream commitu `f0f8337` (0.9.2) aktualizován přes `novy_projekt.py`; `npm install`, `npm run data` a `npm run build` prošly. Astro sestavilo 587 stránek a Pagefind vytvořil vyhledávací index.
- `python -I -X utf8 tests/portrety/test_built.py <ukázkový_projekt>/web`: ověřeno HTML všech 261 osob, dva portréty, odkazy na dostupné obrázky a vyloučení z obou galerií. Testovací snímky měly různé proporce.
- Finální sestavení ověřilo také osobu ze staršího exportu bez pole `portrait` a stránku s dlouhým jménem, událostí a poznámkou; kontrola byla na úrovni sestavení a HTML.
- Vizuální kontrolu na počítači a mobilu nelze prohlásit za provedenou: nástroj prohlížeče hlásil nedostupný browser host i native pipe. Responzivní styly a HTML jsou připravené, zbývá jejich kontrola v připojeném prohlížeči.
- Při přípravě verze byly opraveny dříve commitnuté značky konfliktů v `plugin.json`, `VERZE`, README a changelogu; historie obou větví zůstala zachována.
