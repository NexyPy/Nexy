# Task 26: Translate all French comments and strings to English

## Rule
Nexy is an international framework. **All code comments, variable names, console messages, and docstrings must be in English.** Zero French.

## What to change

### 1. `nexy/decorators.py`

| Line | French | English |
|------|--------|---------|
| 12 | `# --- 1. DÉCORATEUR INJECTABLE (Doit être défini avant le Container pour référence) ---` | `# --- 1. INJECTABLE DECORATOR ---` |
| 20 | `# --- 2. SYSTEME D'INJECTION (CONTAINER INTELLIGENT) ---` | `# --- 2. DI CONTAINER ---` |
| 29 | `"""1. Accès rapide (Fast path) sans verrou"""` | `"""1. Fast path — no lock"""` |
| 39 | `# 3. Détection de cycle (Dépendances circulaires)` | `# 3. Cycle detection` |
| 45 | `# 4. Résolution simplifiée` | `# 4. Simple resolution` |
| 59 | `f"Dépendance {name}: {dep_type} non injectable dans {target_cls.__name__}"` | `f"Dependency {name}: {dep_type} is not injectable in {target_cls.__name__}"` |
| 234 | `raise ValueError(f"Module {cls.__name__} doit avoir au moins un controller")` | `raise ValueError(f"Module {cls.__name__} must have at least one controller")` |
| 240 | `raise ValueError(f"{provider_cls.__name__} doit être @Injectable()")` | `raise ValueError(f"{provider_cls.__name__} must be @Injectable()")` |
| 258 | `# ICI : Container.resolve va analyser le Controller, voir qu'il a besoin d'un Service,...` | `# Container.resolve analyzes the Controller, resolves its Service dependency` |

### 2. `nexy/core/string.py`

| Line | French | English |
|------|--------|---------|
| 12 | `"""Transforme [slug] en {slug}."""` | `"""Convert [slug] to {slug}."""` |
| 16 | `"""Transforme [...slug] en {slug:path}."""` | `"""Convert [...slug] to {slug:path}."""` |
| 21 | `"""Supprime les segments entre parenthèses comme /(user)/."""` | `"""Remove parenthesized segments like /(user)/."""` |
| 30 | `# Next.js : /docs/index -> /docs et /index -> /` | `# Next.js: /docs/index -> /docs and /index -> /` |

### 3. `nexy/template.py`

| Line | String |
|------|--------|
| 17 | `"""Classe pour gérer le rendu des templates Jinja2 et Markdown."""` → `"""Jinja2 and Markdown template renderer."""` |
| 23 | `# Sécurité : autoescape activé pour éviter les failles XSS` → `# Security: autoescape prevents XSS` |
| 36 | `"""Convertit le texte Markdown en HTML."""` → `"""Convert Markdown text to HTML."""` |

### 4. `nexy/vite.py`

| Line | String |
|------|--------|
| 10 | `# 1. Vérification config` → `# 1. Check config` |
| 51 | `# 3. Mode Développement (Dynamique via le navigateur)` → `# 3. Dev mode (dynamic via browser)` |
| 54 | `# On utilise un petit script JS pour injecter les balises avec le bon hostname` → `# Inject script tags with the correct hostname` |

### 5. `nexy/compiler/parser/__init__.py`

| Line | French | English |
|------|--------|---------|
| 18 | `# Nettoie les {% ... %}` → `# Clean Jinja2 tags` |
| 27 | `# 1. Découpage` → `# 1. Split` |
| 30 | `# 2. Analyse de la logique (Python)` → `# 2. Parse Python logic` |
| 37 | `# 3. Préparation des composants connus pour le template` → `# 3. Collect known components` |

### 6. `nexy/cli/commands/utilities/server.py`

| Line | French | English |
|------|--------|---------|
| 17-19 | French comments on port utilities | Translate to English |
| 23-24 | `"""Vérifie si un port est libre..."""` → `"""Check if a port is available."""` |
| 44-46 | `"""Parcourt les ports..."""` → `"""Find an available port."""` |
| 142 | `f"[red]✘ Échec du lancement du serveur :[/red] {exc}"` → `f"[red]✘ Server launch failed:[/red] {exc}"` |

### 7. `nexy/cli/commands/utilities/uvicorn_config.py`

| Line | French | English |
|------|--------|---------|
| 8 | `# Couleurs ANSI pour le terminal` → `# ANSI color codes` |
| 20 | `# Messages systèmes d'Uvicorn à masquer pour épurer la console` → `# Uvicorn system messages to filter from console` |
| 31 | `# Signes associés aux principaux codes de statut HTTP (sans emojis)` → `# Status code indicators` |
| 42 | `"""Filtre de nettoyage..."""` → `"""Filter to suppress redundant init logs."""` |
| 49 | `"""Formatter ultra-lisible..."""` → `"""Readable HTTP access log formatter."""` |
| 93 | `"""Formatter universel..."""` → `"""Universal error-aware log formatter."""` |

### 8. `nexy/routers/fbrouter/__init__.py`

Check for French comments and translate.

### 9. `nexy/compiler/generator/__init__.py` and `logic.py`

Check for French comments and translate.

### 10. `nexy/frontend/solid.py`

Line with `# OPTIMISATION` / `# REMPLACEMENT` — translate to English.

## Search command
```bash
git grep -n '[éèêëàâùûôöîïç]' -- '*.py'
```

This will find all French-accented characters. Each occurrence needs translation.

## Verify
- [ ] Zero French-accented characters in `nexy/*.py`
- [ ] All console strings are in English
- [ ] All comments are in English
- [ ] `python -m pytest tests/ -v` — no regressions (no functional changes)
