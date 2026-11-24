# Plán: připomínka exportu do GEDCOM (MyHeritage) při práci na webu (navrženo pro 0.12.6)

## Context
Uživatel navrhl, aby se Claude při sestavování webu zeptal, zda provést i export pro externí službu (MyHeritage).
Zjištěno (24. 11. 2026):
- Web se **automaticky nesestavuje nikdy** – v projektu není hook ani hlídání souborů (jediný hook z `novy_projekt.py`
  je hlídač sítě, `PreToolUse`). Sestavení spouští Claude podle pokynu ve `SKILL.md` (Fáze 4, krok 3: „po každé změně
  dat `npm run data && npm run build`“), uživatel přes `npm run nahled`, nebo nasazení (`npm run nasadit-cloudflare`,
  `nasadit`, `deploy-caprover` – vždy `npm run data -- --nasazeni` + build). `npm run data` = `tools/export_web.py`.
- Sestavení proběhne po každém kole práce – ptát se při něm by bylo příliš často. Přirozená chvíle je **nasazení webu
  nebo konec sezení** (SKILL.md, Fáze 5: „nasazuj na pokyn nebo jednou na konci sezení“).
- Export dnes vždy vyrobí **celý strom**: nahraný na web MyHeritage = nový samostatný strom, import do FTB „Merge into
  project“ = duplicity. Rozdílový export je fáze 2 v `plán-export-gedcom.md` (neimplementována). Připomínka proto má jen
  **nabídnout** čerstvý export a upozornit na to, ne k němu tlačit ani ho spouštět sama.
- `export_web.py` kopíruje celý `data/web.json` do webu (`texts["web.json"]`, ř. ~473) – nastavení exportu proto
  **nesmí** být ve `web.json` (šlo by s webem ven, i volba „včetně žijících“).

## Návrh
### 1. Zapamatovaná volba: `data/export_gedcom.json` (nový soubor, ne `web.json`)
```json
{"nabidnout": true, "cil": "MyHeritage", "koren": 3, "cp_v_miste": true, "slozka": true,
 "posledni": {"datum": "2026-11-24", "vystup": "pracovni/rodokmen_koren3", "otisk": "…"}}
```
- `nabidnout: false` = uživatel export nechce, Claude se už neptá (odpověď „ne“ se také ukládá).
- **Žijící osoby se neukládají** – na `--zijici` se Claude ptá pokaždé znovu (pravidlo SKILL.md a `data.md`).
- `posledni` zapisuje sám `ged_export.py` po úspěšném exportu (datum, výstup, otisk dat). Soubor vznikne až při prvním
  exportu nebo odpovědi uživatele; `novy_projekt.py` ho nezakládá ani nepřepisuje.

### 2. Otisk dat místo data změny
Datum změny souborů je na Google Disku/OneDrive nespolehlivé (synchronizace mění čas). `ged_export.py` spočítá otisk
(SHA-256) obsahu `data/osoby.py`, `zaznamy.json`, `svazky.json`, `prepisy.json`, `mista.json`, `dokumenty.json` a seznamu
jmen a velikostí v `vyrezy/` a `zdroje/`; sdílená funkce v novém `tools/otisk_dat.py` (používá ji i `export_web.py`).

### 3. Připomínka v nástroji
`export_web.py` jen při `--nasazeni` načte `data/export_gedcom.json`:
- `nabidnout: true` a otisk ≠ `posledni.otisk` → vypíše řádek
  `EXPORT GEDCOM: data se od posledního exportu (24. 11. 2026, pracovni/rodokmen_koren3) změnila – nabídni nový export.`
- soubor chybí → nic (dotaz řídí pokyn v SKILL.md, viz 4). Nástroj nic neexportuje ani se neptá – jen hlásí.
Výhoda: nezávisí na tom, zda si Claude pokyn pamatuje; hlášku uvidí ve výstupu `npm run nasadit…`.

### 4. Pokyn ve `SKILL.md`
- Fáze 5 (zveřejnění) a konec sezení: když výstup obsahuje `EXPORT GEDCOM:`, nabídni export se zapamatovanými volbami
  (zeptej se na žijící osoby), upozorni, že jde o celý strom (nový strom na webu MyHeritage / duplicity při sloučení ve
  FTB), a po exportu připomeň postup pro FTB včetně restartu.
- Když `data/export_gedcom.json` neexistuje a uživatel zmínil MyHeritage (nebo má `dokumenty/strom.ged`/`.ftb`
  z MyHeritage), zeptej se **jednou** při prvním nasazení, zda chce rodokmen exportovat i do MyHeritage; odpověď ulož
  (`nabidnout` true/false).
- Odkaz na `reference/data.md` → Export do GEDCOM.

### 5. Dokumentace a testy
- `reference/data.md`: sekce „Export do GEDCOM“ – soubor `export_gedcom.json`, klíče, že se žijící neukládají.
- `tests/gedcom/test_ged_export.py`: `posledni` se zapíše po exportu; otisk se nezmění bez změny dat a změní po úpravě
  `osoby.py`; export bez `--slozka` a s `--vystup` mimo `pracovni/` zapíše správnou cestu.
- `tests/web/…` (nebo nový test): `export_web.py --nasazeni` vypíše `EXPORT GEDCOM:` jen při změně a `nabidnout: true`;
  `export_gedcom.json` se do webu nezkopíruje.
- Aktualizace projektu (`novy_projekt.py` na stávající složku): soubor se nepřepíše ani nesmaže.

### 6. Vydání
Zvýšit verzi (`plugin.json`, `VERZE`, README 2×), CHANGELOG („Nové“), commit, `/plugin marketplace update`,
`/reload-plugins`, ověřit na skutečném projektu uživatele (`novy_projekt.py`, `npm run data -- --nasazeni` bez nasazení – jen hláška),
push na pokyn.

## Mimo rozsah
- Automatický export bez dotazu (rozhodnutí o žijících, import do FTB je ruční).
- Hook Claude Code na sestavení webu – připomínka ve výstupu nástroje stačí a funguje i v Claude Desktop/claude.ai.
- Rozdílový export a sloučení se stromem MyHeritage – fáze 2 v `plán-export-gedcom.md`; po jejím dokončení změnit text
  připomínky („nabídni rozdílový export“).
- Vlastní skript `skripty/web_varianty.py` v projektu uživatele (tři weby) – volá `export_web.py` po svém; ověřit, zda
  hláška projde jeho výstupem.

## Rozhodnuto (24. 11. 2026)
1. Změnu hlásit **jen při nasazení** (`export_web.py --nasazeni`), ne při běžném `npm run data` po každém kole.
2. **Zatím jeden cíl** exportu (jeden záznam v `export_gedcom.json`); více cílů (MyHeritage i Gramps, různé `--koren`)
   až na požádání.
