# Plán: portréty na stránkách osob

Datum: 8. 11. 2026

Stav: návrh odsouhlasen uživatelem, implementace zatím neprovedena.

## Cíl

Na stránce osoby zobrazovat její portrét vedle jména, štítků a výpisu událostí podle dodaného screenshotu. Portrét se nebude zobrazovat mezi rodinnými dokumenty ani ve společné galerii u příběhu rodu. Rozpoznání bude automatické podle názvu obrázku obsahujícího `portrét` nebo `portret`, bez ohledu na velikost písmen a zápis diakritiky.

## Ověřený současný stav

- Rodinné fotografie jsou evidovány v `data/dokumenty.json`. Pole `img` obsahuje klíč obrázku bez přípony a pole `osoby` čísla osob, ke kterým fotografie patří.
- `skills/rodokmen/tools/vyrez.py` vytváří `vyrezy/<klíč>.jpg` pro web a `zdroje/<klíč>.jpg` v plném rozlišení.
- `skills/rodokmen/tools/export_web.py` vytváří seznam dokumentů každé osoby i společný seznam dokumentů a kopíruje obrázky do webu.
- `skills/rodokmen/template/web/src/pages/osoba/[slug].astro` vykresluje jméno, štítky, události a níže sekci Rodinné dokumenty.
- `skills/rodokmen/template/web/src/pages/pribehy/index.astro` vykresluje společnou galerii Rodinné dokumenty a fotografie.
- Řešení lze doplnit do současného exportu a šablony bez nové knihovny.

## Postup implementace

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

- Rozpoznání variant s diakritikou, bez diakritiky, s různou velikostí písmen a s kombinujícími znaménky; běžná fotografie se nesmí označit za portrét.
- Správné přiřazení portrétu včetně alternativního čísla osoby, chybějícího souboru a více kandidátů.
- Portrét se zobrazí v horní části stránky a nebude v žádné ze dvou galerií dokumentů; běžné dokumenty zůstanou zobrazené.
- Zobrazení na počítači a mobilu, dlouhé jméno a události, fotografie různých proporcí a osoba bez portrétu.
- Funkční proklik na obrázek a dostupnost souborů ve výsledném webu.
- Export a sestavení ukázkového projektu pomocí `npm run data` a `npm run build`.
- Aktualizace projektu založeného předchozí verzí: `novy_projekt.py` na stejnou složku, `npm install`, `npm run data` a `npm run build`.

## Promítnutí do existujícího rodokmenu

Tento repozitář obsahuje šablonu webu. Po implementaci bude pro zobrazení na existujícím rodokmenu potřeba aktualizovat také jeho projekt a znovu vygenerovat web. Samotné uložení tohoto plánu funkčnost webu nemění.
