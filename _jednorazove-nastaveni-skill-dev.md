# Nastavení vývoje skillu rodokmen na dalším PC

Cíl: na dalším počítači mít stejné nastavení jako na hlavním PC, tedy plugin `rodokmen@rodokmen-skill`
nainstalovaný z lokálního klonu forku `xkraust/rodokmen-skill`, který lze upravovat ve VS Code.

Nastavení Claude Code je uložené v `~\.claude` konkrétního počítače a nesynchronizuje se.
Proto je potřeba tento postup provést na každém PC zvlášť.

## Jak to funguje
- Jediné místo pro úpravy je klon forku (zde `C:\Users\tomas\Documents\VSCode\rodokmen-skill`).
  Remote `origin` = `xkraust/rodokmen-skill`, remote `upstream` = `sarsonj/rodokmen-skill` (repo autora).
- Marketplace `rodokmen-skill` má zdroj `directory` s cestou ke klonu. GitHub se při aktualizaci pluginu nepoužívá.
- Claude Code při instalaci a aktualizaci KOPÍRUJE soubory z klonu do
  `~\.claude\plugins\cache\rodokmen-skill\rodokmen\<verze>\`. Tyto soubory neupravuj, přepisují se.
- Nová verze se do cache zkopíruje jen tehdy, když se změní `version` v `.claude-plugin/plugin.json`.

## Nastavení na dalším PC

### 1. Naklonuj fork
Doporučuji stejnou cestu jako na hlavním PC (pokud existuje stejný uživatel a složka), jinak jakoukoli mimo `~\.claude`:
```
git clone https://github.com/xkraust/rodokmen-skill C:\Users\tomas\Documents\VSCode\rodokmen-skill
```

### 2. Přidej remote upstream (původní repo autora)
```
cd C:\Users\tomas\Documents\VSCode\rodokmen-skill
git remote add upstream https://github.com/sarsonj/rodokmen-skill.git
git remote -v
```
Výpis má ukázat `origin` na `xkraust` a `upstream` na `sarsonj`.

### 3. Odeber případný existující marketplace
Pokud už je na PC nainstalovaný původní plugin od autora nebo jiný marketplace stejného jména:
```
/plugin marketplace remove rodokmen-skill
```
Dva marketplace stejného jména nemohou existovat zároveň. Pokud tam nic není, krok přeskoč.

### 4. Přidej marketplace z lokálního klonu
V Claude Code:
```
/plugin marketplace add C:\Users\tomas\Documents\VSCode\rodokmen-skill
```
(Použij skutečnou cestu ke klonu na tomto PC.)

### 5. Nainstaluj plugin
```
/plugin install rodokmen@rodokmen-skill
/reload-plugins
```
Rozsah: `user`. Krok 4 nelze vynechat, bez něj install skončí chybou „Marketplace not found“.

### 6. Zkontroluj výsledek
- `~\.claude\plugins\known_marketplaces.json`: `rodokmen-skill` má `"source": "directory"` s cestou ke klonu.
- `~\.claude\settings.json`: `"rodokmen@rodokmen-skill": true` a v `extraKnownMarketplaces` je zdroj `directory`.
- `~\.claude\plugins\installed_plugins.json`: `rodokmen@rodokmen-skill` ukazuje do `cache\rodokmen-skill\rodokmen\<verze>`.
- Skill `rodokmen:rodokmen` je dostupný (po restartu session nebo `/reload-plugins`).

## Každodenní práce na obou PC

### Před začátkem práce
```
git pull origin main
```
Jinak vznikne rozdvojená historie mezi počítači.

### Úprava skillu
1. Uprav soubory v klonu (typicky `skills/rodokmen/`, `tools/`, `template/web/`, `docs/`).
2. Zvyš `version` v `.claude-plugin/plugin.json`. Bez zvýšení se úprava v Claude Code neprojeví.
   Při vydání verze zvyš číslo i v `skills/rodokmen/VERZE` a v README a doplň `CHANGELOG.md`
   (podrobnosti jsou v `CLAUDE.md`).
3. Commitni: `git add -A`, `git commit -m "popis změny"`.
4. V Claude Code: `/plugin marketplace update rodokmen-skill` a `/reload-plugins` (případně restart session).
5. Ověř, že skill funguje.

### Na konci práce
```
git push origin main
```
Bez pushe se změny na druhém PC neobjeví.

## Další tipy
- Rychlé zkoušení bez cache a bez zvyšování verze:
  `claude --plugin-dir C:\Users\tomas\Documents\VSCode\rodokmen-skill`
  (nainstalovanou verzi pak dočasně vypni, ať se skilly nepřekrývají).
- Novinky od autora: `git fetch upstream`, pak `git merge upstream/main`. Fork se sám nesynchronizuje.
- Návrat k verzi autora: `/plugin marketplace remove rodokmen-skill`, pak
  `/plugin marketplace add sarsonj/rodokmen-skill` a `/plugin install rodokmen@rodokmen-skill`.
- Data k bádání (např. složky `Rodokmen-Krausovi`, `Rodokmen-Hesovi`) jsou samostatná věc a s pluginem
  se nesynchronizují. Pokud jsou na cloudovém disku, je potřeba ověřit, že se na druhý PC synchronizují.
