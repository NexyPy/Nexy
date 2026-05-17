# Skill: SOLID Principles for Nexy

## Contexte
Tu es un Software Engineer expert appliquant les principes SOLID au projet Nexy, un meta-framework Python/FastAPI + Vite.

## Règles fondamentales

### S - Single Responsibility Principle
- Chaque classe/ fonction a une seule raison de changer
- Pour Nexy: `TemplateParser` parse seulement, `Builder` construit seulement, `Router` rute seulement
- Les fichiers dans `nexy/cli/commands/` = une commande par fichier

### O - Open/Closed Principle
- Ouvert à l'extension, fermé à la modification
- Pour Nexy: ajouter nouveaux frontends (React, Vue, Svelte) sans modifier `nexy/frontend/__init__.py`
- Utiliser des classes de base/abstraites dans `nexy/core/` pour étendre sans modifier

### L - Liskov Substitution Principle
- Les sous-classes doivent pouvoir remplacer leurs classes parentes
- Pour Nexy: tout router (file-based, modular) doit implémenter la même interface
- Vérifier que `RouteHandler` peut être remplacé par n'importe quelle implémentation

### I - Interface Segregation Principle
- Préférer plusieurs interfaces spécifiques plutôt qu'une interface catch-all
- Pour Nexy: séparenter `IRouteDiscovery` de `IRouteRenderer`
- Les `nexy/frontend/*.py` = interfacesadrocs pour chaque framework

### D - Dependency Inversion Principle
- Dépendre des abstractions, pas des implémentations
- Pour Nexy: `nexy/router.py` ne doit pas connaître FastAPI directement
- Utiliser `Protocol` pour typer les dépendances

## Application pratique Nexy

1. Avant d'écrire du code, vérifier qu'il ne viole pas un principe SOLID
2. Si une classe fait trop (parse + render + validate), la diviser
3. Les dépendances passent par injection (voir `nexy/runtime/injection.py`)
4. Tester que les implémentations alternatives sont interchangeables

## Vérification
Après chaque modification significativ, valider que les principes SOLID sont respectés.
