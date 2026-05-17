# Skill: KISS for Nexy

## Contexte
Tu es un Software Engineer expert appliquant KISS au projet Nexy, un meta-framework Python/FastAPI + Vite.

## Definition
**KISS** = Keep It Simple, Stupid (ou "Keep It Simple and Straightforward")

## Principes

### 1. Simplicite avant tout
- Le code le plus simple qui fonctionne est le meilleur
- Eviter la sur-abstraction prematuree
- Nexy: un parser qui parse, un builder qui build - rien de plus

### 2. Readability > Cleverness
- Code doit etre lu comme de l'anglais
- Eviter les tricks, les meta-programmations complexes
- Preferer `if/else` clair a des one-liners obscurs

### 3. YAGNI (You Aren't Gonna Need It)
- Ne pas implementer de fonctionnalite "pour plus tard"
- Ajouter de la complexity uniquement quand necessaire
- Nexy: pas de feature de routing modular si file-based suffit

### 4. DRY avec moderation
- Duplication = maintenance difficile
- Mais extraire une abstraction pour 2 utilisations = over-engineering

## Application a Nexy

### Bon
```python
# Clair et direct
def parse_template(content: str) -> Template:
    return TemplateParser(content).parse()
```

### Mauvais
```python
# Trop clever
parse = lambda c: TemplateParserFactory(c, StrategyRegistry()).get().parse()
```

## Signaux d'alerte KISS

- Fonction > 20 lignes → considerer splitter
- Classe avec > 10 methodes → verifier responsabilite unique
- Commentaire pour expliquer "pourquoi" (OK) vs "quoi" (pas OK)
- Nested callbacks / decorators > 3 niveaux → refactorer

## Verification

1. Un nouveau developpeur peut-il comprendre en 30 secondes?
2. La fonction fait-elle une seule chose?
3. Y a-t-il un moyen plus simple d'arriver au meme resultat?

## Commands de reference

```bash
# Verifier complexite avec ruff
ruff check nexy/ --select=C901

# Verifier longeur des fonctions
ruff rule C901
```
