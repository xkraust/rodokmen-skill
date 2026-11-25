# Plán: stavba webu mimo synchronizovanou složku

## Problém
Projekt rodokmenu často leží v Google Disku (OneDrive, Dropboxu), aby šel mezi PC a laptopem. `npm` ve `web/`
tam založí desetitisíce souborů (`node_modules`, `dist`, `.astro`, `.netlify`, `.wrangler`) a synchronizace se zahltí.

Dřívější lokální řešení (skript `priprava_stroje.ps1` v projektech, 4. 11. 2026) dávalo build složky mimo Disk
a ve `web/` nechávalo junction. Předpoklad „Disk Google junctiony ignoruje“ neplatí: Disk se je při každém
spuštění snaží přečíst, hlásí `PERMISSION_DENIED` (log `drive_fs.txt`, `local_disk_bridge.cc … Checksumming …
failed`) a celou složku projektu označí červeným křížkem.

## Řešení
Nástroj `tools/stavba.py`:
- Pozná cloud podle cesty (Google Drive, Můj disk, My Drive, OneDrive, Dropbox, iCloud, CloudStorage); mimo cloud
  spustí `npm` přímo ve `web/` (beze změny chování).
- V cloudu projekt jednosměrně zrcadlí do `~/projekt-rodokmen/<projekt bez diakritiky>/stavba/` (jen změněné soubory,
  smazané ve zdroji smaže) a `npm` spustí tam. Nezrcadlí `.git`, `.skill_sablona`, `pracovni`, `.claude`, build
  ani nic, co generuje `npm run data` (seznam podle `template/.gitignore`); ty cesty v zrcadle nikdy nemaže.
- `npm install` doplní sám, když chybí `node_modules` nebo se v projektu změnil `package.json`/`package-lock.json`.
  Vědomé `stavba.py install …` vrátí změněný `package.json`/lock do projektu.
- `--kde` ukáže, kde se staví, a najde build složky/odkazy ve `web/` na Disku; `--uklid` je odstraní (odkaz smaže,
  obsah přesune do zrcadla, nic nepřepíše ani nesmaže).
- Cesta zrcadla z domovské složky → funguje na každém počítači; každý počítač má své zrcadlo.
  Přepsání: `--zrcadlo <složka>` nebo `RODOKMEN_STAVBA`.

## Dokumentace
`SKILL.md` (Fáze 4 krok 0, aktualizace projektu, tabulka nástrojů), `reference/web.md` (sekce „Projekt
v synchronizované složce“, náhled v Claude desktop, aktualizace).

## Test
`tests/stavba/test_stavba.py` – zrcadlo, zachování generovaných souborů, mazání, `--kde`, `--uklid` s junctionem.
Ručně ověřeno: ukázkový projekt v cestě s „Můj disk“ → `stavba.py run data` a `run build` v zrcadle, na Disku nic.
