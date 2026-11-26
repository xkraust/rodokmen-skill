# Plán: hledání ve vojenské digitální knihovně (Kramerius MO)

Stav: **implementováno ve verzi 0.13.7** (26. 11. 2026).

Výsledky ověření (oddíl „Před implementací ověřit“):
1. Obě adresy vedou na stejný server se stejnými daty. Nástroj používá `kramerius.army.cz`; vzor `KRAMERIUS`
   v `slusne.py` nově zahrnuje i `digitalnistudovna.mo.gov.cz`.
2. Odkaz `/view/<parent_pid>?page=<uuid>` funguje u periodika i u vojenské matriky.
3. U NK ČR funguje odkaz, text i snímek. U stran uvnitř PDF (`uuid@číslo`) nástroj vypíše odkaz na dokument a číslo strany.
4. Snímek z `/search/img` brzda do mezipaměti neukládá a počítá ho jako běžný dotaz (2 s). Brzdu jsme kvůli tomu
   neměnili; `--snimek` nepřepisuje existující soubor a návod to uvádí.
5. `datum_begin` má většina stránek matrik, seznamy ztrát ho nemají. Nástroj na to při prázdném výsledku upozorní.

## Problém
Vojenská digitální knihovna `kramerius.army.cz` má fulltextově prohledávatelné prameny k vojákům, hlavně z 1. světové
války, ale skill o tom neví:
- `tools/kramerius.py` hledá jen v Národní knihovně (`kramerius5.nkp.cz`),
- `reference/portaly.md` knihovnu neuvádí a `reference/metodika.md` popisuje vojenské matriky jen jako offline (Vídeň).

Hledat v ní jde, ale jen jednorázovými skripty, a to Claude u dalšího uživatele nejspíš nenapadne.

## Co je ověřeno (26. 11. 2026)
- Rozhraní Kramerius API v5, stejné jako u NK ČR; přes brzdu `slusne.py` s výchozím tempem bez potíží.
- Obsah: seznamy ztrát (`Verlustliste`, `Nachrichten über Verwundete und Kranke`, `Alphabetisches Verzeichnis …`),
  Kniha zemřelých v polních nemocnicích, 38 titulů `Matriky …` (35 pěších pluků, 2 prapory polních myslivců,
  hraničářské prapory; 37 veřejných).
- Stránky matrik mají v `text_ocr` přepsaný seznam „Příjmení Jméno rok–rok“, rejstříky „Příjmení Jméno strana“.
- `Nachrichten …` uvádějí u zemřelých i datum a místo úmrtí a číslo hrobu.
- Adresy:

| účel | adresa |
|---|---|
| hledání | `/search/api/v5.0/search?q=…&hl=true&hl.fl=text_ocr` |
| text stránky | `/search/api/v5.0/item/<uuid>/streams/TEXT_OCR` |
| snímek (JPEG, šířka asi 1500 px) | `/search/img?pid=<uuid>&stream=IMG_FULL&action=GETRAW` |
| odkaz pro člověka | `/view/<parent_pid>?page=<uuid stránky>` (ověřeno u periodika) |

Pasti:
- `/search/handle/<uuid>` vrací HTTP 200, ale v prohlížeči „Stránka nebyla nalezena“. Stavový kód nestačí.
- Obec bývá v tisku nebo v OCR zkomolená, i první písmeno.
- `curl` v Git Bash na Windows pošle diakritiku v dotazu ve špatném kódování.

## Řešení
Samostatný skill nevzniká, rozšíří se `rodokmen`.

### `tools/kramerius.py`
- Přepínač `--armada` zvolí vojenskou knihovnu; bez něj se chování nemění (NK ČR).
- U každého nálezu řádek s odkazem pro člověka (do `fl` přidat `parent_pid`).
- `--text <uuid>` vypíše OCR text stránky (úryvek ve výsledcích nestačí na přečtení celého záznamu).
- `--snimek <uuid> <soubor.jpg>` stáhne snímek pro čtení a `vyrez.py`; existující soubor nepřepíše.
- Dotaz uzavřít do závorek před `AND fedora.model:page`, aby `OR` v dotazu neměnilo jeho význam.
- Neveřejné dílo ohlásit srozumitelně, ne výpisem výjimky.
- Veškerý síťový provoz dál přes brzdu.

### Návody
- `reference/portaly.md`: nový oddíl o vojenské knihovně – co tam je, jak hledat (německy i česky, „Příjmení Jméno“
  i obrácené pořadí, jméno s ročníkem bez obce), příklady příkazů, pasti. Nenalezení v matrikách je jen orientační.
  Zápis do dat jako pramen „J“, čtení vždy ověřit na snímku.
- `reference/metodika.md`: u položky „Voják“ a u Kriegsarchivu doplnit, co je online v Česku (Kriegsarchiv zůstává
  pro to, co tam online není).
- `SKILL.md`: řádek v tabulce nástrojů a u hledání úmrtí zmínka o padlých a zemřelých vojácích.
- `README.md`: v přehledu pramenů doplnit vojenskou knihovnu.

## Před implementací ověřit
1. Která adresa je kanonická: `kramerius.army.cz`, nebo `digitalnistudovna.mo.gov.cz`. Stránka se hlásí jako
   Digitální studovna Ministerstva obrany ČR. Podle volby upravit i vzor `KRAMERIUS` v `slusne.py` (403 u
   neveřejného díla nesmí zastavit celý web).
2. Tvar odkazu `/view/…` u stránky vojenské matriky (monografie) – otevřít v prohlížeči.
3. Zda `--text`, `--snimek` a odkaz fungují i u NK ČR; kde ne, omezit je na `--armada`.
4. Zda se stažený snímek uloží do mezipaměti (`cache.py`) a jaké tempo pro něj brzda použije.
5. Zda filtr `datum_begin` funguje u vojenských matrik (část titulů nemá vyplněné datum).

## Test
`tests/kramerius/test_kramerius.py`, offline s podvrženou odpovědí (vzor `tests/anno/test_ztraty.py`):
- bez `--armada` se volá NK ČR, s ním vojenská knihovna,
- dotaz s `OR` zůstane v závorkách,
- odkaz se složí z `parent_pid` a `uuid` stránky,
- `--snimek` nepřepíše existující soubor,
- neveřejné dílo vypíše srozumitelnou hlášku.

Ručně: jeden dotaz, text a snímek přes brzdu a otevření odkazu v prohlížeči. Spustit i `tests/brzda/`.

Všechny příklady a testovací data musí být smyšlené (jména, obce, ročníky, uuid). Repozitář je veřejný, před pushem
je porovnat s daty rodinných projektů.

## Vydání
1. Nejdřív uzavřít rozpracovanou opravu `ged_export.py` (neuložené změny v `data.md`, `ged_export.py`,
   `test_ged_vazba.py`), aby se obě úpravy nesmíchaly.
2. Zvýšit verzi (0.13.6, nebo další volná) v `plugin.json`, `VERZE` a na dvou místech README; sekce v `CHANGELOG.md`.
3. Commit, `/plugin marketplace update rodokmen-skill`, `/reload-plugins`, ověřit, pak push, tag a vydání.
4. Formát mezi `tools/` a `template/web/` se nemění. Existující projekty dostanou nový nástroj přes `novy_projekt.py`.
5. Volitelně nabídnout autorovi (`upstream`) jako samostatný PR.

## Mimo rozsah
- Automatické ztotožňování vojáků se záznamy v projektu.
- Hromadné stahování celých knih.
- Kartotéka padlých VÚA a další databáze vyžadující přihlášení.
