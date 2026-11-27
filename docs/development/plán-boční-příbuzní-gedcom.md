# Plán: boční příbuzní (`SIDE`) v GEDCOM jako osoby (`INDI`)

Stav: **návrh (27. 11. 2026)**, neimplementováno. Navazuje na otevřený bod v `plán-export-gedcom.md`
(„Otevřený bod: boční příbuzní (`SIDE`) jako osoby“).

## Výchozí stav
- `ged_export.py` vyváží každého bočního příbuzného jen jako řádek `1 NOTE Příbuzný: <n> – <t>` u předka `k`
  (`person_lines`, ř. ~607). V MyHeritage a FTB tak sourozenec není osobou: chybí ve stromu, nemá kartu,
  nejdou k němu fotky a Smart Matches ho nenajdou.
- Zápisy z `r` se u bočních příbuzných necitují vůbec (`records_of` čte jen `P` a aliasy `SAME`).
- Soukromí (`side_protected`) bere roky z textu `n`. Příbuzný bez roku projde vždy.
- `SIDE` má jen volný text: `dict(k=16, n="Josef Novák (1865–1920)", t="Bratr Jana. Kovář v …", r=[…])`.
  Chybí pohlaví, přesná data a vztah k předkovi.

## Cíl
Na požádání vyvézt boční příbuzné jako skutečné osoby (`INDI`) navázané na rodiny (`FAM`) předků. U každého bude
narození, úmrtí, citace jeho zápisů a poznámka z `t`. Bez volby zůstane export beze změny.

## Volba exportu: `--bocni`
Ano, nová volba, ve výchozím stavu vypnutá:

```
python3 -I tools/ged_export.py --bocni                     # celý strom + boční příbuzní jako osoby
python3 -I tools/ged_export.py --bocni --koren 3           # jen maminčina strana, i s jejími bočními příbuznými
python3 -I tools/ged_export.py --bocni --rozdil strom.ged  # sloučení se stromem (viz fáze B)
```

Proč volba a ne nový výchozí stav:
- **Duplicity při sloučení:** strom na MyHeritage sourozence předků často už má. Bez spárování (`ged`) by každý
  vznikl podruhé a musel by se ve FTB ručně spojit.
- **Kvalita dat:** u starších projektů jsou `SIDE` jen text. Dokud nemají doplněný vztah, zůstanou poznámkou.
  Uživatel by se divil, proč se někdo stal osobou a jiný ne.
- **Soukromí:** z osoby `INDI` se toho do cizí služby dostane víc než z jedné věty v poznámce.

Až se volba osvědčí na skutečném projektu, lze ji zvážit jako výchozí (s volbou `--bez-bocnich`).

## Data: nová nepovinná pole v `SIDE`
Stávající `n`, `t` a `r` zůstanou, web (`export_web.py`) se nemění. Přibudou tato pole:

| pole    | význam | příklad |
|---------|--------|---------|
| `vztah` | vztah k osobě `k`: `sourozenec`, `dite`, `manzel` (manžel nebo manželka) | `"sourozenec"` |
| `sex`   | `"M"` / `"F"` | `"M"` |
| `f`     | fakta ve stejném tvaru jako u `P` (`*`, `†`, `×`, povolání) | `["* 3. 5. 1865 Holice čp. 12", "† 1920 Holice"]` |
| `ged`, `uid` | vazba na osobu v původním stromu (jako u `P`) | `"@I245@"` |

Pravidla, když pole chybí:
- **`vztah`:** odvodí se z prvního slova `t`. „Bratr“ nebo „Sestra“ dá sourozence, „Syn“ nebo „Dcera“ dítě,
  „Manžel“ nebo „Manželka“ (i „první/druhá manželka“) manžela. Jiný vztah (strýc, bratranec, švagr, synovec) se
  neodhaduje a příbuzný zůstane poznámkou. Do souhrnu se vypíše s radou: „přesuň `k` na předka, ke kterému je
  sourozenec, dítě nebo manžel, a doplň `vztah`“. Strýc je třeba sourozenec rodiče, tedy `k` = rodič a
  `vztah="sourozenec"`.
- **`sex`:** podle slova vztahu v `t` (bratr, syn, manžel = M; sestra, dcera, manželka = F), jinak podle příjmení
  (-ová, -á = F), jinak `U`.
- **Data:** když chybí `f`, vezmou se roky ze závorky v `n`. „(1865–1920)“ dá `BIRT 1865` a `DEAT 1920`,
  „(* 1865)“ jen narození, „(asi 1865–1920)“ dá `ABT`. Co nejde přečíst, vypíše souhrn
  (jako dnes u `unparsed`).
- **Jméno:** `n` bez závorek a otazníků, příjmení je poslední slovo: `1 NAME Josef /Novák/`.

## Export (fáze A: běžný export)
1. **Načtení:** `self.side`, seznam bočních příbuzných s vlastním ID `@B<n>@` (n = pořadí v `SIDE` od 1;
  `@I…@` zůstane číslům `P`, aby se nezměnila ID předků). Předek `k` se převede přes `canon()`. Když v exportu
  není (`--koren`, zástupná osoba), příbuzný se vynechá.
2. **Příprava:** fakta přes `parse_fact()` jako u `P`, záznam do `self.info` pod klíčem `("B", n)` (nebo
  rozšířit `info` na řetězcové klíče). `records_of()` vrátí i `r` bočních příbuzných.
3. **Soukromí:** stejná pravidla jako u předků (`is_protected`). Nově i **bez roku**: odhad podle předka `k`.
  Sourozenec a manžel = rok narození předka, dítě = rok předka + 20. Když neznáme ani ten, příbuzný je chráněný.
  Chráněný boční příbuzný se **vynechá celý** (ne „Žijící osoba“: do stromu nic nepřidá, jen prázdnou kartu),
  počítá se dál jako `side_skipped`. Jeho zápisy jdou do `rec_protected` (bez obrázku a přepisu).
4. **Rodiny:**
   - `sourozenec` dostane `CHIL` v rodině, kde je předek `k` dítětem (`famc[k]`). Když předek rodiče v `P` nemá,
     vznikne nová `FAM` bez `HUSB`/`WIFE` jen s dětmi (ověřit ve FTB, viz níže).
   - `dite` dostane `CHIL` v rodině předka `k` s partnerem `k ^ 1`, tedy v rodině, kde je `k // 2` dítětem.
     U `k = 1` vznikne nová `FAM` s `HUSB`/`WIFE` = 1. Dítě z jiného manželství se nepodporuje
     (zůstane poznámkou s radou v souhrnu).
   - `manzel` vytvoří novou `FAM` předka `k` s příbuzným. Sňatek `MARR` se vezme z faktu `×` (stejně jako
     `marriage()`) a s ním i citace zápisu O z `r`.
   - Děti v `FAM` se řadí podle roku narození (předek mezi sourozenci), bez roku na konec. GEDCOM pořadí `CHIL`
     zachovává a FTB i MyHeritage ho tak zobrazí.
5. **Osoba:** `person_lines` se zobecní (nebo vznikne `side_lines`): `NAME`, `SEX`, události s citacemi (zápis
  k události, když sedí druh a rok, jinak u osoby, jako `match_records`), `NOTE` z `t`, „Původ údajů“, je-li `st`,
  `FAMC`/`FAMS`. `RIN MH:I…` se nepřidá (boční příbuzní portrét nemají, `dokumenty.json` zná jen čísla `P`).
6. **Poznámka u předka:** příbuzný vyvezený jako osoba už nebude mít řádek `NOTE Příbuzný: …` (byl by tam dvakrát).
  Kdo zůstal poznámkou (neznámý vztah), ten ho má dál.
7. **Souhrn:** „boční příbuzní: N jako osoby, M jako poznámka (neznámý vztah: …), K vynecháno kvůli soukromí“.

## Sloučení se stromem (fáze B: `--bocni --rozdil`)
- `diff_classify()` bere boční příbuzné jako další osoby: s `ged` ve stromu = ve stromu, bez něj = nová.
  Kotvy a rodiny se dopočítají stejným kódem (sourozenec je dítětem v `FAM` s rodiči předka, takže rodiče jsou kotvy).
- **Párování:** `ged_import.py <strom> "Výchozí osoba" --ged-id` rozšířit o `SIDE`. U každého bočního příbuzného
  se hledá ve stromu mezi dětmi rodičů předka (sourozenec), dětmi předka (dítě) a jeho manžely (manžel), stejnou
  shodou jako u předků (křestní jméno, příjmení podle začátku slova, rok ±1). `--zapsat` doplní `ged`/`uid`.
- `zapis.py ged` umí dnes jen číslo osoby. Doplnit cílení části jména (jako `zapis.py odkaz` u `SIDE`).
- Boční příbuzný bez `ged`, kterého strom podle jména a roku asi má, se v přehledu `rozdil_zmeny.md` označí
  „ve stromu asi už je: …, nespojovat automaticky“ (jako stávající `similar`).
- Bez spárování jde `--bocni --rozdil` spustit, ale nástroj na začátku varuje, kolik bočních příbuzných nemá `ged`.

## Další úpravy
- `template/data/osoby.py`: komentář u `SIDE` s novými poli.
- `reference/data.md`: popis polí, pravidla odvození, volba `--bocni` v sekci exportu, rada Claudovi:
  „před exportem s `--bocni` projdi `SIDE` a doplň `vztah`, `sex` a `f` podle `t` a zápisů z `r`; strýce a
  bratrance přesuň k bližšímu předkovi“.
- `kontrola.py`: chyba při neznámé hodnotě `vztah` nebo `sex`, při špatném tvaru `ged` a při stejném `ged`
  jako u osoby z `P`. Informace, kolik `SIDE` nemá vztah, který jde určit.
- `tools/ged_export.py` docstring a `--help`.
- Testy `tests/gedcom/test_ged_export.py`:
  - sourozenec v `FAM` rodičů a pořadí dětí;
  - dítě (i u `k = 1`) a manžel s `MARR`;
  - odvození vztahu a pohlaví z `t`;
  - roky z `n` a `ABT`;
  - soukromí bez roku (odhad z předka, vynechání);
  - citace `r` u události;
  - bez volby výstup beze změny;
  - `--koren` a `--rozdil` (nová a spárovaná).
- Vydání verze podle `CLAUDE.md`. Formát mezi `tools/` a `template/web/` se nemění, test aktualizace projektu
  tedy není nutný.

## K ověření
1. Zobrazí FTB a MyHeritage rodinu bez rodičů (`FAM` jen s `CHIL`) jako sourozence? Jinak přidat zástupného
  rodiče „otec neuveden“, nebo sourozence bez známých rodičů nechat poznámkou.
2. Pohlaví `U`: jak ho MyHeritage zobrazí a jestli nevadí při spojování osob.
3. Na kopii skutečného projektu (16 `SIDE`): kolik jich vyjde jako osoby bez ručních úprav a kolik po doplnění
  `vztah`. Ověřit import do FTB (zkušební projekt) a zobrazení ve stromu.

## Rozdělení práce
- **Fáze A** (samostatná verze): pole `SIDE`, volba `--bocni`, export, kontrola, návod, testy.
- **Fáze B** (další verze): párování přes `ged_import.py --ged-id`, `zapis.py ged` pro `SIDE`, `--bocni --rozdil`.
