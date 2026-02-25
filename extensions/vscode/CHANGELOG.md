# Change Log

All notable changes to the "nexy" extension will be documented in this file.

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.

## [Unreleased]

## [0.0.1] - 2026-02-25

### Ajouté

- Grammaire TextMate Nexy (header + template HTML/Jinja2) et configuration de langage.
- Serveur LSP Nexy avec complétions, hovers et diagnostics basiques.
- Décorations des composants par framework.
- Snippets Nexy (header, props, imports, blocs Jinja, template complet).

### Amélioré

- Mutualisation du parsing Nexy entre client et serveur (module partagé `src/shared/nexyParser.ts`).
- Diagnostics LSP supplémentaires :
  - Composants utilisés mais non importés dans le header.
  - Imports inutilisés.
  - Props déclarées mais jamais utilisées dans le template.
- Quick fixes pour ajouter un import manquant et supprimer imports/props inutilisés.
- Nouvelles commandes DX :
  - `nexy.createComponent`
  - `nexy.insertHeader`
  - `nexy.wrapWithComponent`
- Barre de statut Nexy (section courante, nombre de props/imports).
- Snippets renommés pour éviter les collisions (`nif`, `nfor`, `ndiv`, `nscript`, `nstyle`, `nfrom`, `npage`).