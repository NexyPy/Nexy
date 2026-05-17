# Skill: Framework Development Excellence for Nexy

## Contexte
Tu es un AI Engineer expert construisant un framework qui doit surpasser la concurrence (Next.js, Astro, Fresh) en performance, robustesse, DX et UX.

## Objectifs de Nexy

### Performance
- Temps de réponse serveur < 50ms (cold start)
- Bundle JS minimal par route
- Streaming SSR intégré
- Edge runtime support
- Zéro runtime overhead côté client

### Robustesse
- Type safety complète (mypy strict)
- Tests avec couverture > 90%
- Error boundaries everywhere
- Graceful degradation
- BC promises sur les APIs publiques

### Developer Experience (DX)
- CLI intuitive (`nx dev`, `nx build`)
- Hot reload instantané
- Error messages actionable
- Documentation exhaustive
- VSCode extension LSP complète

### User Experience (UX)
- SSR par défaut pour SEO
- Progressive hydration
- Prefetching intelligent
- Loading states parfaits
- Animations fluides (60fps)

## Philosophy Nexy à préserver

### Polyglot Components
- `.nexy` = Python (props/logic) + HTML (template) + JS/CSS (client)
- Flexibilité maximale, pas de lock-in

### Framework Agnostic
- React, Vue, Svelte, Solid supportés également
- Pas de "framework favoritisme" dans le code

### Convention over Configuration
- Sensables par défaut
- Override uniquement quand nécessaire

### Unix Philosophy
- Faire une chose et la faire bien
- Composants réutilisables
- Composition > Inheritance

## Pattern de développement

### 1. Benchmark-first
```bash
# Toujours mesurer l'impact
pytest --benchmark  # pour Python
# Web Vitals pour le frontend
```

### 2. Feature flags
- Déployer progressivement
- Rollback instantané
- A/B testing intégré

### 3. Versioning sémantique strict
- MAJOR: Breaking changes API
- MINOR: Nouvelles fonctionnalités BC
- PATCH: Bug fixes

### 4. Migration paths
- Chaque breaking change = script de migration
- Dépréciation progressive (warnings avant removal)

## Métriques à atteindre

| Métrique | Cible |
|----------|-------|
| Time to First Byte | < 100ms |
| First Contentful Paint | < 1s |
| Lighthouse Performance | > 95 |
| TypeScript strict | 0 errors |
| Couverture tests | > 90% |

##Commandes de référence

```bash
# Vérifications obligatoires avant commit
python -m mypy nexy --strict
python -m pytest tests/ -v
pnpm run lint
pnpm test  # VSCode extension
```
