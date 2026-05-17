# Skill: VSCode Extension Refactoring for Nexy

## Contexte
Tu es un expert en développement d'extensions VSCode. Refondre l'extension Nexy pour une DX exceptionnelle.

## État actuel de l'extension

### Fichiers clés
```
extensions/vscode/
├── src/
│   ├── extension.ts          # Entry point
│   ├── server/
│   │   ├── server.ts          # LSP server
│   │   └── handlers/          # hover, completion, diagnostics, definition
│   ├── client/
│   │   ├── lspClient.ts       # Language client
│   │   ├── providers/         # embedded languages
│   │   ├── commands.ts        # VSCode commands
│   │   └── statusBar.ts      # Status bar
│   └── shared/                # Parsers, constants
├── syntaxes/                  # TextMate grammars
└── package.json
```

### Actuellements supporté
- Syntax highlighting `.nexy` / `.mdx`
- Commands (create component, insert header)
- Basic LSP (hover, completion, diagnostics)
- Status bar avec infos de section
- Decorations framework colors

## Objectifs DX pour Nexy

### 1. IntelliSense complet
- Autocomplétion props (depuis header Python)
- Autocomplétion imports (composants, frameworks)
- Suggestions de templates
- Snippets intelligentes

### 2. Navigation avancées
- Go to definition (props, imports, composants)
- Find all references
- Peek definitions
- Breadcrumbsstructurés

### 3. Refactoring inline
- Rename props/utilisateurs
- Extract to component
- Move component to file
- Auto-import manquant

### 4. Debugging
- Debug .nexy server-side
- Breakpoints dans le header Python
- Variables inspectables

### 5. Productivity
- Todo/ FIXME markers
- Task runners intégrés
- Test runnersinline
- Quick fixes pour erreurs comunes

## Pattern à appliquer

### Architecture modulaire
```
src/
├── lsp/
│   ├── server.ts              # Lanceur serveur
│   ├── lexer/                # Tokenizer .nexy
│   ├── parser/               # AST .nexy
│   └── handlers/             # Chaque feature = 1 fichier
├── features/
│   ├── autocomplete/         # Autocomplétion contextuelle
│   ├── diagnostics/          # Validation inline
│   ├── hover/                # Informations au survol
│   ├── gotoDefinition/       # Navigation
│   └── refactoring/          # Transformations
├── core/
│   ├── documentManager.ts    # État documents
│   ├── workspace.ts          # Fichiers projet
│   └── config.ts             # Settings
└── tests/
    └── integration/          # Tests LSP
```

### Gestion d'état
- DocumentProvider avec observers
- Debounced updates
- Cache intelligent
- Background workers pour parsing lourd

## Améliorations prioritaires

### Priority 1 (Essentiel)
1. **Props completion**: Analyser header Python → proposer props
2. **Import resolution**: Trouver les composants importés
3. **Error highlighting**: Parser errors inline
4. **Go to definition**: Sauter vers définition props/components

### Priority 2 (Important)
5. **Rename refactoring**: Renommer props safety
6. **Code actions**: Quick fixes automatique
7. **Inlay hints**: Types Params/Hints inline
8. **Signature help**: Paramètres de fonctions

### Priority 3 (Nice to have)
9. **Debug adapter**: Debug Python server
10. **Test explorer**: Voir et lancer tests
11. **Live templates**: Snippets paramétrables
12. **AI assist**: Génération code

## Métriques DX

| Feature | Target |
|---------|--------|
| Autocomplete latency | < 100ms |
| Diagnostics latency | < 200ms |
| Go to definition | < 150ms |
| Memory usage | < 150MB |
| Startup time | < 2s |

## Commandes

```bash
# Build extension
cd extensions/vscode
pnpm compile

# Watch mode
pnpm watch

# Package
pnpm vscode:prepublish

# Run tests
pnpm test

# Lint
pnpm lint
```

## Erreurs à éviter

- Tout mettre dans `extension.ts`
- Bloquer le main thread
- Pas de tests = bugs caché
- Ignorer les edge cases (gros fichiers)
- Couplagefort avec une version VSCode
