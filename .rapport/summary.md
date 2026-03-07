# Nexy – Audit Technique Complet

Ce document synthétise l’audit du framework Nexy (Python/TypeScript) selon SOLID, KISS et TDD, avec un score de dette technique par module et des priorités de remédiation. Les chemins critiques et propositions de refactor sont détaillés, ainsi que les optimisations attendues (algorithmes, structures de données, i18n, DX, performances).

## Barème de dette
- 0–10: Excellent
- 11–25: Bon
- 26–50: Moyen (actions recommandées)
- 51–75: Élevé (actions prioritaires)
- 76–100: Critique (actions immédiates)

---

## Python

### nexy.core.config [dette: 48/100] – Priorité: Haute
- Observations (SOLID/KISS)
  - Mélange de constantes et d’état runtime dans une seule classe (SRP violé). 
  - Mutation globale de `sys.path` au chargement → effets de bord cachés (KISS, testabilité).
  - Variables et chaînes partiellement en français → défaut d’uniformité i18n.
  - Constantes configurables exposées comme attributs de classe plutôt qu’instances immutables.
- TDD
  - Absence de tests unitaires dédiés à la validation de la config et de ses invariants.
- Refactor proposé
  - Introduire un modèle immuable `@dataclass(frozen=True)` (ex: AppConfig) validé à la frontière.
  - Isoler la logique d’initialisation (résolution de chemins, aliases, watchers) dans des fonctions pures.
  - Interdire les mutations globales ; encapsuler dans une factory.

### nexy.core.models [dette: 35/100] – Priorité: Moyenne
- Observations
  - `PaserModel` orthographe erronée, risque de confusion (API/maintenabilité).
  - `ContextModel` n’est pas respecté dans `Parser.process` (liste contenant `None`).
  - Enum `ComponentType` OK ; plusieurs `@dataclass` pertinentes mais pas immuables.
- TDD
  - Tests de parsing présents, pas de tests ciblant les invariants des modèles.
- Refactor proposé
  - Renommer `PaserModel` → `ParserModel` (breaking change à planifier).
  - Rendre les dataclasses immuables (`frozen=True`) et types stricts.

### nexy.compiler.parser.* [dette: 52/100] – Priorité: Haute
- Observations
  - `Parser.process` renvoie `context=[None]` → incohérence de type (bug latent).
  - Couplage serré entre parsing logique Jinja/python et préparation des composants (SRP).
  - Gestion d’exception silencieuse sur `ast.parse` (masque erreurs).
- TDD
  - Bon socle de tests scanner ; compléter sur logique/validator/erreurs.
- Refactor proposé
  - Séparer strictement: `scan` → `parse_logic` → `validate_imports` → `parse_template`.
  - Lever des exceptions typées ; supprimer `except SyntaxError: pass`.
  - Interfaces: `LogicParser.process(source:str)->LogicResult`, `TemplateParser.parse(...)->str` déjà en place; renforcer types.

### nexy.compiler.__init__.py (Compiler) [dette: 46/100] – Priorité: Moyenne
- Observations
  - Chemin de sortie résolu dans la même méthode que la compilation (SRP).
  - `print` d’erreur et `return None` → préférer exceptions structurées.
  - Détection `.nexy/.mdx` dispersée.
- Refactor proposé
  - Extraire un `OutputPlanner` pur; lever `CompilationError`.
  - API: `compile(input)->CompiledArtifact` + `write(artifact)`.

### nexy.builder [dette: 34/100] – Priorité: Moyenne
- Observations
  - Boucle de build séquentielle; logs couplés à la compilation.
  - Pas de stratégie de cache LRU au niveau du builder (optimisation possible).
- Refactor/Perf
  - Introduire un cache LRU par timestamp/fingerprint des fichiers.
  - Option de compilation parallèle (pool) avec garde-fou I/O.

### nexy.routers.file_based_routing.__init__ [316 LOC] [dette: 71/100] – Priorité: Critique
- Observations
  - Fichier monolithe >150 LOC ; mélange découverte, introspection, mapping HTTP, et binding FastAPI.
  - Risque élevé de duplication logique et de bugs difficiles à couvrir.
- Refactor proposé (découpage)
  - route_discovery.py (existe) : garder découverte de modules/fichiers.
  - route_introspection.py : extraire annotations, deps, signatures.
  - route_registration.py : enregistrer les routes (APIRouter/FastAPI).
  - http_map.py : map statique METHOD→handler.
  - Interfaces:
    - `discover_routes(root)->Iterable[RouteSpec]`
    - `introspect(spec)->HandlerSpec`
    - `register(app/spec)`

### nexy.cli (Typer) [dette: 43/100] – Priorité: Haute
- Observations
  - Mix FR/EN; chaînes en clair; i18n absent.
  - `init`: questionnaire présent mais pas d’implémentation de clone/template/registry.
  - Manque `--template/-t` et listing via REST.
- Refactor/Features
  - Introduire i18n minimal (JSON) + `t(key)` côté CLI.
  - Ajouter `nexy init -t, --template` avec fetch REST (registry configurable).
  - Implémenter `clone` silencieux (git/python API), contrôles d’erreurs, rollback.

### nexy.routers.app [dette: 28/100] – Priorité: Moyenne
- Observations
  - Multiples branches pour docs/redocs; lisibilité moyenne.
  - Valeurs par défaut imbriquées.
- Refactor
  - Extraire une fonction pure `resolve_docs_urls(config)->tuple[str|None,str|None]`.

### nexy.cli.commands.utilities.uvicorn_config [dette: 32/100] – Priorité: Moyenne
- Observations
  - Formatteurs custom longs; logique i18n absente; commentaires FR.
  - Bon correctif d’emoji via `.get()` ; OK.
- Refactor
  - Scinder formatteurs, constants de couleurs et table d’emojis.

---

## TypeScript – VS Code extension (extensions/vscode)

### src/shared/nexy.parser.ts [dette: 22/100] – Priorité: Basse
- Observations
  - Types clairs; pas d’`any`; interfaces OK.
- Améliorations
  - Extraire lib i18n des libellés côté client/serveur si nécessaire.

### package.json / snippets / syntaxes [dette: 40/100] – Priorité: Moyenne
- Observations
  - Descriptions de snippets en français → défaut d’uniformité en EN par défaut.
  - i18n absent.
- Refactor
  - English par défaut; extraire messages dans `i18n/en.json` (centralisation).

---

## Décomposition des artefacts >150 LOC
- nexy/routers/file_based_routing/__init__.py → 4 sous-modules listés ci-dessus.
- extensions/vscode/syntaxes/nexy.tmLanguage.json (config, non critique): conserver, documenter.

---

## Optimisations d’algorithmes (chemins chauds)
- Builder
  - Cache LRU sur fichiers déjà compilés (hash/mtime) pour atteindre O(n) sur scan, éviter recompilations.
- Router FBR
  - Éviter introspections répétées; mémoïsation des signatures.
  - Regrouper enregistrements par module (batch) plutôt que N+1 imports.

---

## Structures de données
- Dataclasses immuables pour modèles (LogicResult, TemplateResult, etc.).
- Remplacer dict bruts par `TypedDict`/`Enum`/Pydantic (validation frontière CLI et config).

---

## Internationalisation
- Anglais par défaut dans la CLI et l’extension VS Code.
- Extraction progressive des chaînes → `i18n/en.json`, prêt pour d’autres locales.

---

## DX & Onboarding
- API publique documentée (Google-style docstrings) après refactor.
- Exemples exécutables à ajouter par module (à planifier).
- Couverture tests: viser ≥95% (pytest), jest pour extension (à compléter).

---

## Performance (cibles)
- CLI cold-start ≤ 50 ms (objectif) : décharger imports lourds, différer i18n/HTTP.
- Génération template ≤ 200 ms : cache builder + IO réduits.
- `make perf` automatique (échoue si régression >5%) – harnais ajouté.

---

## Priorités d’action (P0 → P2)
- P0
  - Corriger bug `context=[None]` dans `Parser.process` et orthographe `PaserModel`.
  - Découper `file_based_routing.__init__` en sous-modules.
  - Passer la CLI à l’anglais par défaut + i18n minimal.
- P1
  - Introduire cache LRU dans Builder; exceptions structurées dans Compiler.
  - Ajouter `--template` avec listing REST dans `nexy init`.
- P2
  - Immutabilité généralisée des modèles et docs/EXAMPLES.
  - i18n complet extension VS Code et snippets.

---

## Estimation des gains
- Lisibilité & maintenabilité: +30–40% (réduction de LOC par responsabilité).
- Build incrémental: -60–80% temps compilation à chaud.
- Démarrage CLI: -20–40 ms attendu via différé d’imports.
- Couverture tests: +40–60% (ciblage modules clés).

— Fin du résumé —

