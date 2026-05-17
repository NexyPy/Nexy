# Skill: TDD for Nexy

## Contexte
Tu es un Software Engineer expert appliquant TDD au projet Nexy, un meta-framework Python/FastAPI + Vite.

##cycle de développement

### 1. Écrire un test qui FAIL
- Avant d'écrire du code, écrire le test
- Utiliser pytest comme dans `tests/unit/nexy/parser/`
- Le test décrit le comportement attendu

### 2. Faire passer le test (vert)
- Écrire le minimum de code pour faire passer
- Pas d'optimisation prematuree
- Iterer rapidement

### 3. Refactorer
- Ameliorer le code tout en gardant les tests green
- Extraire les duplications
- Appliquer SOLID

## Structure des tests Nexy

```
tests/
  unit/           # Tests unitaires rapides
    nexy/parser/test_scanner.py
    nexy/parser/test_sanitizer.py
  integration/   # Tests d'integration
    test_runtime.py
```

### Naming des tests
- `test_<quoi>_<scenario>`: `test_scanner_valid`, `test_scanner_invalid_1`
- Tres explicite sur ce qui est testé

##Commandes

```bash
# Lancer tous les tests
python -m pytest tests/ -v

# Test unitaire specifique
python -m pytest tests/unit/nexy/parser/test_scanner.py -v

# Couverture
python -m pytest tests/ --cov=nexy
```

## Guidelines Nexy

1. ** Rouge**: Test qui échoue clairement
2. ** Vert**: Code minimal pour passer
3.  **Refactor**: Appliquer SOLID/KISS
4. **Verifier**: `mypy --strict` et `pytest` passent

##Bonnes pratiques
- Un test = une assertion principale
- Mock les dependances externes (fichiers, reseau)
- Tests reproducibles sans dependsances externes
- Garder les tests rapides (<100ms)