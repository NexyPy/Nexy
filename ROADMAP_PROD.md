# Plan de Production (Prod-Ready) - Nexy Framework

Ce plan suit les principes **SOLID**, **KISS** et **TDD** pour garantir une architecture maintenable, simple et robuste, tout en préservant l'existant et l'âme de Nexy.

## 0. Philosophie & Principes d'Implémentation
*   **Intentionnalité Pure** : Chaque fichier, package, classe et méthode doit répondre à une seule question : "Pourquoi j'existe ?". Si une méthode fait deux choses, elle est scindée.
- **Code Unique, Usage Partout (DRY)** : Aucune duplication de logique. Les utilitaires de manipulation de chaînes ou de parsing AST sont centralisés dans `core` ou `utils`.
- **Stabilité (Pas de Rupture)** : On ne casse pas ce qui fonctionne. Le compilateur actuel est *refactorisé* (nettoyé) et non réécrit de zéro, pour conserver sa logique métier éprouvée.
- **Lisibilité Pro** : Nommage explicite. Pas de `data`, mais `template_metadata`. Pas de `process`, mais `compile_logic_block`.

## 1. Core & Architecture (SOLID & KISS)
*L'objectif est de séparer les données de la logique et d'assurer une configuration robuste.*

| Fichier | Intention | Classe / Méthode Clé | Principe |
| :--- | :--- | :--- | :--- |
| `nexy/core/models.py` | DTO (Data Transfer Objects) | `NexyComponent`, `RouteConfig` | **SRP** : Uniquement de la donnée. |
| `nexy/core/exceptions.py` | Gestion centralisée des erreurs | `NexyCompilerError`, `NexyRuntimeError` | **KISS** : Erreurs explicites. |
| `nexy/core/config.py` | Configuration immuable | `NexySettings.load()` | **DIP** : Source unique de vérité. |

## 2. Compilateur (Intention : Transformer sans casser)
*Le compilateur actuel est puissant mais doit être mieux structuré.*

| Fichier | Intention | Classe / Méthode Clé | Principe |
| :--- | :--- | :--- | :--- |
| `nexy/compiler/parser/scanner.py` | Découpage brut (RegEx/String) | `Scanner.split_blocks()` | **KISS** : Pas d'intelligence, juste du découpage. |
| `nexy/compiler/parser/logic.py` | Analyse AST Python | `LogicParser.extract_props()` | **TDD** : Tests sur chaque cas d'import/prop. |
| `nexy/compiler/generator/template.py` | Assemblage HTML/JS | `Generator.build_ssr_bundle()` | **OCP** : Facile d'ajouter un framework (ex: Qwik). |

## 3. Runtime (Intention : Exécuter avec performance)
*Ici, tout est à construire de façon intentionnelle.*

| Fichier | Intention | Classe / Méthode Clé | Principe |
| :--- | :--- | :--- | :--- |
| `nexy/runtime/renderer.py` | Moteur de rendu SSR | `Renderer.render_page(context)` | **SOLID** : Abstraction totale du moteur. |
| `nexy/runtime/router.py` | Routage FastAPI optimisé | `Router.register_routes(app)` | **KISS** : Pas de surcharge sur les requêtes. |
| `nexy/runtime/injection.py` | Injection de dépendances | `Container.resolve(service_name)` | **DIP** : Découplage services/templates. |

## 4. Stratégie de Migration & Stabilité
1. **Tests Avant Tout** : On écrit les tests pour le compilateur actuel. S'ils passent, on refactorise le code dans les nouveaux fichiers.
2. **Refactorisation par Extraction** : On déplace la logique de `logic.py` vers les nouvelles classes sans changer le comportement.
3. **Double Run (Optionnel)** : Possibilité de garder l'ancien parser en fallback pendant la transition.

## 5. Developer Experience (DX) & Error Reporting
*L'objectif est de fournir des erreurs si précises que le débogage devient quasi-instantané.*

| Fichier | Intention | Classe / Méthode Clé | Principe |
| :--- | :--- | :--- | :--- |
| `nexy/errors/formatter.py` | Formatage des erreurs pour la console | `ErrorFormatter.pretty_print(error)` | **DX-First** : L'erreur doit guider le dev. |
| `nexy/errors/models.py` | Structures de données des erreurs | `NexyErrorContext(file, line, col, code_snippet)` | **SRP** : La donnée d'erreur est un DTO. |
| `nexy/compiler/parser/validator.py` | Intégration du contexte d'erreur | `Validator.validate_syntax(context)` | **TDD** : Chaque erreur de syntaxe est testée. |

**Fonctionnement :**
1. Le `Parser` attrape une `SyntaxError` et l'encapsule dans une `NexyCompilerError`, en y ajoutant le `NexyErrorContext`.
2. Le `ErrorFormatter` reçoit cette erreur et génère un message clair en console, avec le nom du fichier, la ligne, et un extrait de code surligné.

## 6. Feature Parity & New Features
*Aligning with key features from modern frameworks like Next.js.*

| File | Intent | Key Class / Method | Principle |
| :--- | :--- | :--- | :--- |
| `nexy/audio.py` | Integrated `<Audio>` component | `nexy.audio(src, ...)` | **KISS** : Simple and direct API. |
| `nexy/decorators.py` | `@action` decorator | `@action def my_server_action():` | **DIP** : Decoupled from parser, registers server actions. |
| `nexy/runtime/router.py` | Server Actions Exposure | `Router.expose_actions()` | **SOLID** : Automatically maps registered actions to endpoints. |

**Implementation of `@action`:**
1. **Independent Registration**: The `@action` decorator in `nexy/decorators.py` can be used anywhere (services, controllers, or standalone files). It registers the function in a global `ActionRegistry`.
2. **Runtime Exposure**: The `Router` in `nexy/runtime/router.py` automatically discovers these registered actions and exposes them as secure internal endpoints.
3. **Client-Side Calling**: These actions can be called from any client component (Vue, React, Svelte, etc.). The runtime provides a bridge so that calling `my_server_action()` from the frontend automatically triggers a `fetch` to the corresponding server endpoint.

---
**Final Goal**: A developer should be able to open any file and understand its role within 5 seconds thanks to its name and structure. All code and comments must be in **English** to ensure professional standards and maintainability.
