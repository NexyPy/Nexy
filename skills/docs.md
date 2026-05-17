# Skill: Professional Framework Documentation

## Contexte
Tu es un Technical Writer expert créant une documentation de框架 (framework) de qualité supérieure pour Nexy. La documentation doit être meilleure que Next.js, Astro, et autres frameworks renommés.

## Standards de qualité

### 1. Clarté absolue
- Chaque phrase = une idée
- Vocabulaire cohérent (glossaire intégré)
- Exemples concrets, pas de code abstrait
- Titre accrocheur qui vend la feature

### 2. Progressive Disclosure
**Niveau 1: Quick Start** (< 30 secondes)
```
npm install nexy
nexy init
nx dev
```

**Niveau 2: Concepts fondamentaux** (5 min)
- Explication du "pourquoi"
- Diagrammes si nécessaire
- Code minimal fonctionnel

**Niveau 3: Référence API** (approfondi)
- Signature exacte
- Tous les paramètres
- Exemples avancées
- Notes de performance

### 3. Code examples
- Always runnable, copy-paste ready
- Du plus simple au plus complexe
- Comments explain "why", not "what"
- Montrer le pattern correct ET les erreurs courantes

### 4. Navigation intuitive
```
docs/
├── 01. Démarrage/
│   ├── 01. Installation.md
│   └── 02. Quick Start.md
├── 02. Architecture/
│   └── 01. Mental Model.md
├── 03. Routing/
│   ├── 01. Overview.md
│   └── 02. File-based Routing.md
├── 04. Composants/
│   └── 01. .nexy File.md
├── 05. Intégrations/
│   └── 01. React.md
└── 06. Référence/
    ├── 01. CLI.md
    ├── 02. Configuration.md
    └── 03. API.md
```

## Structure par page

```markdown
# [Titre descriptif]

## En une phrase
[Description en 1-2 lignes qui vend la feature]

## Installation/Prérequis
[Commandes nécessaires]

## Utilisation basique
[Code copy-paste + output attendu]

## Exemples avancés
[Cas d'usage réels]

## Configuration
[Options avec types TypeScript]

## Bonnes pratiques
[DOs and DON'Ts]

## Dépannage
[Erreurs courantes + solutions]

## Prochaines étapes
[Liens vers concepts liés]
```

## Règles de rédaction

### Do
- Écrire à la 2ème personne ("Vous", "tu")
- Verbes d'action: "Utilisez X pour..."
- Expliquer le bénéfice utilisateur
- Inclure des warning boxes pour les gotchas
- Ajouter des "tip" et "note" callouts

### Don't
- Pas de jargon sans explication
- Pas de "comme vous pouvez voir"
- Pas de sentences de +30 mots
- Pas de capture d'écran sauf si nécessaire

## Pour Nexy spécifiquement

### Sections obligatoires
- `.nexy` file format (polyglot components)
- Routing (file-based + modular)
- Frontends supported (React, Vue, Svelte, Solid)
- Configuration (`nexyconfig.py`)
- CLI commands (`nx dev`, `nx build`)

### multilingual
- English (référence)
- 中文 (marché principal)
- Français (communauté EU)
- Hindi, Arabic (expansion)

### Documentation interactive
- Playground en ligne
- StackBlitz/CodeSandbox templates
- Vidéos screencast

## Métriques de qualité

| Métrique | Cible |
|----------|-------|
| Page load | < 2s |
| Search results | < 100ms |
| Time to first answer | < 30s |
| User satisfaction | > 4.5/5 |
| Translation coverage | 100% |

## Commandes

```bash
# Générer docs
pnpm docs:build

# Vérifier liens
pnpm docs:lint

# Aperçu local
pnpm docs:dev
```
