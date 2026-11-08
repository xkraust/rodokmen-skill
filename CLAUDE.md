# Správa repozitáře rodokmen-skill

## Plány úprav

- Každý plán úpravy ukládej jako Markdown soubor do `docs/development/`.
- První slovo názvu souboru musí být vždy `plán` (s diakritikou a malým písmenem), například `plán-portréty-osob.md`.
- Použij výstižný název podle plánované úpravy; při zpřesnění stejného plánu aktualizuj jeho existující soubor.
- Toto pravidlo platí pro všechny budoucí plány úprav v tomto repozitáři.

## Vydání verze

Vydání nové verze: zvedni číslo ve třech místech najednou – `.claude-plugin/plugin.json` (`version`),
`skills/rodokmen/VERZE` (podle něj Claude u uživatele pozná, že má aktualizovat projekt) a README na dvou místech – nahoře „Aktuální verze: X.Y.Z (vydána D. M. RRRR)“ a v požadavcích
„Stav k D. M. RRRR (verze X.Y.Z)“, vždy s číslem verze i datem vydání.
Do `CHANGELOG.md` přidej nahoru sekci `## X.Y.Z – D. M. RRRR` (Nové / Opravy / Návody, krátké odrážky pro uživatele,
čísla issues jako `#11`). Po commitu a pushi vytvoř tag a vydání na GitHubu s textem té sekce:
`awk '/^## X.Y.Z /{f=1;next} /^## /{f=0} f' CHANGELOG.md > /tmp/notes.md && gh release create vX.Y.Z --target main --title "X.Y.Z" --notes-file /tmp/notes.md`.
Mění-li se formát mezi `tools/` a `template/web/`, otestuj i aktualizaci projektu založeného předchozí verzí
(`novy_projekt.py` na stejnou složku, `npm install`, `npm run data`, `npm run build`).

# Vývoj forku lokálně (xkraust/rodokmen-skill)

## Jak je plugin zapojený do Claude Code
- Pracovní kopie (jediné místo pro úpravy): `C:\Users\tomas\Documents\VSCode\rodokmen-skill`.
  Je to klon forku `xkraust/rodokmen-skill` (remote `origin`); původní repo autora je remote `upstream`
  (`sarsonj/rodokmen-skill`).
- Marketplace `rodokmen-skill` má v nastavení Claude Code zdroj `directory` s cestou k tomuto klonu
  (`~\.claude\settings.json` → `extraKnownMarketplaces`, `~\.claude\plugins\known_marketplaces.json`).
  GitHub se při aktualizaci pluginu nepoužívá.
- Plugin je `rodokmen@rodokmen-skill`. Claude Code z klonu při instalaci a aktualizaci KOPÍRUJE soubory do
  `~\.claude\plugins\cache\rodokmen-skill\rodokmen\<verze>\`. Soubory v `~\.claude\plugins\` nikdy needituj,
  přepisují se.

## Postup po každé úpravě skillu
1. Uprav soubory v klonu (typicky `skills/rodokmen/`, `tools/`, `template/web/`, `docs/`).
2. Zvyš `version` v `.claude-plugin/plugin.json`. Pokud se verze nezmění, Claude Code ponechá starou kopii v cache
   a úprava se neprojeví. Při vydání verze zvyš číslo i v `skills/rodokmen/VERZE` a v README (obě místa: „Aktuální verze“ na začátku i „Stav k … (verze …)“)
   a doplň `CHANGELOG.md` (viz postup výše).
3. Commitni změny (`git add -A`, `git commit`).
4. V Claude Code spusť `/plugin marketplace update rodokmen-skill` a `/reload-plugins`
   (případně restartuj session).
5. Ověř, že skill funguje, a teprve potom `git push origin main`.

## Poznámky
- Rychlé zkoušení bez cache a bez zvyšování verze: `claude --plugin-dir C:\Users\tomas\Documents\VSCode\rodokmen-skill`
  (nainstalovanou verzi pak dočasně vypni, ať se skilly nepřekrývají).
- Novinky od autora: `git fetch upstream`, pak `git merge upstream/main`. Fork se sám nesynchronizuje.
- Přepnutí zpět na repo autora: `/plugin marketplace remove rodokmen-skill`, pak
  `/plugin marketplace add sarsonj/rodokmen-skill` a `/plugin install rodokmen@rodokmen-skill`.
