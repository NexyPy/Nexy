## Nexy VS Code

Extension VS Code pour le langage de templates **Nexy** (`.nexy`), pensée pour une DX/UX moderne : LSP dédié, snippets, décorations visuelles et commandes de scaffolding.

### Fonctionnalités

- **Coloration & grammaire Nexy**
  - Grammaire TextMate dédiée pour le header (`---` imports/props) et la partie template (HTML + Jinja2).
  - Mise en avant des composants personnalisés (`<Component />`) et des props déclarées dans le header.

- **Serveur de langage (LSP) Nexy**
  - **Complétions contextuelles** dans le header (props, `from ... import ...`) et le template (tags HTML, attributs, filtres Jinja, composants importés).
  - **Infobulles (hover)** sur les composants importés et les props (`prop[...]`) avec type et valeur par défaut.
  - **Diagnostics Nexy** :
    - Composants utilisés dans le template mais non importés dans le header.
    - Imports Nexy/JSX/TSX inutilisés.
    - Props déclarées mais jamais utilisées dans le template.
  - **Quick fixes** :
    - Ajout automatique d'un `from "./components/Component.nexy" import Component` pour un composant manquant.
    - Suppression rapide des imports et props inutilisés.

- **Décorations & barre de statut**
  - Décorations colorées des composants selon leur framework d'origine (Vue, Nexy, React, Svelte).
  - Barre de statut Nexy indiquant la section courante (Header/Template), le nombre de props et d'importations.

- **Snippets Nexy & Jinja2**
  - Snippets pour le header Nexy, les props (`prop`, `propo`, `propc`), les imports (`nfrom`), les blocs Jinja (`nif`, `nfor`, `ife`) et les structures HTML utiles (`ndiv`, `nscript`, `nstyle`).
  - Snippet de **template complet** (`nexy`) et de **page Nexy** (`npage`) avec header + titre.

- **Commandes DX**
  - `Nexy: Créer un composant` (`nexy.createComponent`) : QuickPick de type (Page/Layout/Component UI), nom du composant, création d'un fichier `.nexy` prêt à l'emploi.
  - `Nexy: Insérer un header` (`nexy.insertHeader`) : insère un header Nexy standard en haut du fichier courant.
  - `Nexy: Envelopper avec un composant` (`nexy.wrapWithComponent`) : enveloppe la sélection actuelle dans `<MyComponent>…</MyComponent>`.

### Paramètres d’extension

Cette extension contribue les paramètres suivants :

- `nexy.decorations.enableFrameworkColors` (`boolean`, défaut : `true`)  
  Active/désactive les décorations colorées des composants par framework.

- `nexy.statusBar.enabled` (`boolean`, défaut : `true`)  
  Active/désactive l’élément de barre de statut Nexy (section, props, imports).

### Prise en main

1. Ouvrez un projet contenant des fichiers `.nexy`.
2. Créez un nouveau composant via la palette de commandes : **“Nexy: Créer un composant”**.
3. Utilisez les snippets (`nexy`, `npage`, `prop`, `nif`, `nfor`, …) pour accélérer l’édition.
4. Surveillez les diagnostics et utilisez les quick fixes (ampoule) pour corriger rapidement imports et props.

### Notes

- L’extension nécessite une version de VS Code ≥ `1.109.0`.
- Le serveur de langage tourne via Node et est packagé avec l’extension (esbuild).
