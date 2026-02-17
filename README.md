# Nexy

Nexy est un framework web léger et flexible, conçu pour faciliter la création d'applications web modernes.

Il s'inspire de l'expérience développeur de **Next.js**, **Astro** et **NestJS**, tout en restant
100 % Python grâce à **FastAPI** et **Jinja2**.

---

## Principales fonctionnalités

- **Routage par fichiers**  
  Chaque fichier dans `src/routes` portant l'extension `.py`, `.nexy` ou `.mdx` peut devenir
  une route HTTP.

- **Composants Nexy & MDX**  
  Nexy introduit un format de composant basé sur des fichiers `.nexy` (ou `.mdx`) composés de :
  - une partie **Python** (frontmatter) pour la logique et les props
  - une partie **template** (HTML / MDX) rendue via Jinja2 et Markdown.

- **Routage modulaire**  
  En complément du routage par fichiers, Nexy prévoit un routeur modulaire inspiré de Spring Boot
  et NestJS, avec une API basée sur des décorateurs tels que `@Controller`, `@Module`,
  `@Injectable`.

- **Composants optimisés**  
  Nexy expose des composants prêts à l’emploi comme **Link**, **Image**, **Video**, **Audio**
  et **Form** pour faciliter la création d’interfaces modernes.

- **WebSockets**  
  Grâce à FastAPI, Nexy supporte nativement les WebSockets via des handlers dédiés.

- **Documentation et DX**  
  Nexy est conçu pour être *dev friendly* :
  - endpoints **Swagger UI** et **OpenAPI** via FastAPI
  - intégration possible avec **Vite.js** pour la partie front si nécessaire.

> Certaines fonctionnalités avancées (routage modulaire décoré, génération automatique de
> `sitemap.xml` / `robots.txt`…) sont en cours de conception/évolution dans le code.

---

## Structure type d'un projet

```text
projet/
  src/
    routes/
      index.py
      about.py
      user.nexy
      blog/
        index.nexy
        [slug].nexy
```

Le dossier `src/routes` est la racine de votre arborescence de routes.

---

## Routage basé sur les fichiers

Le routage par fichiers fonctionne ainsi :

- Tout fichier **`.nexy`**, **`.mdx`** ou **`.py`** dans `src/routes` est considéré comme une
  route potentielle.
- Les handlers HTTP (`get`, `post`, `put`, etc.) définis dans un fichier `.py` sont automatiquement
  exposés via FastAPI.
- Les fichiers `.nexy` et `.mdx` sont compilés en templates, puis servis comme pages HTML.

### Fichiers spéciaux

- `index.nexy`, `index.mdx`, `index.py`  
  Sont considérés comme la route par défaut d'un dossier donné.  
  On ne peut pas avoir deux fichiers `index.*` (même nom, extensions différentes) dans le même
  dossier.

- `layout.nexy`  
  Définit un layout pour un segment de route. Il suit une logique d’héritage similaire à Next.js :
  un layout parent enveloppe celui de ses enfants. Ce fichier n’est pas directement routé.

- `Error.nexy`  
- `notfound.nexy`  
  Permettent de personnaliser les pages d’erreur et de 404 pour une portion d’arborescence.

---

## Routes dynamiques et groupes de routes

Nexy reprend une syntaxe proche de Next.js pour définir des routes dynamiques :

- `(name)/`  
  Segment de **groupe de routes**. Il structure l’arborescence mais n’apparaît pas dans l’URL.

- `[name]/`  
  Segment **dynamique**. Exemple : `src/routes/blog/[slug].nexy`  
  → route `/blog/{slug}`.

- `[name].{py,nexy,mdx}`  
  Fichier de route dynamique. Exemple : `src/routes/[id].py`  
  → route `/{id}`.

- `[...name]/`  
  Segment dynamique **catch-all**. Exemple : `src/routes/docs/[...slug].nexy`  
  → route `/docs/{slug:path}`.

- `[...name].{py,nexy,mdx}`  
  Fichier de route catch-all. Exemple : `src/routes/[...all].py`  
  → route `/{all:path}`.

---

## Middlewares et dépendances

Nexy supporte la configuration par convention :

- `middlewares.py` à la racine de `src/`  
  Permet de déclarer des middlewares globaux pour l'application.

- `dependencies.py` dans `src/routes/**/`  
  Permet de définir des dépendances (authentification, contexte, etc.) avec une logique
  d’héritage par dossier, proche de celle des layouts :
  - un `dependencies.py` parent s’applique à tous ses sous-dossiers
  - un `dependencies.py` enfant peut étendre ou spécialiser ce comportement.

Comme `layout.nexy`, un fichier `dependencies.py` n’est pas une route en soi.

---

## Composants Nexy

Un composant Nexy est un fichier `.nexy` ou `.mdx` qui contient :

1. Une section **Python** (frontmatter) délimitée par `---`  
   On y déclare :
   - imports
   - variables
   - fonctions
   - **props** typées via une syntaxe comme :

   ```python
   title: prop[str] = "Titre par défaut"
   count: prop[int]
   ```

2. Une section **template** (HTML / MDX)  
   Rendu via Jinja2 et/ou Markdown, avec la possibilité d’imbriquer d’autres composants.

Les composants peuvent être importés depuis d'autres fichiers `.nexy` ou `.mdx` grâce à une
syntaxe conviviale, par exemple :

```python
from "src/components/user.nexy" import User
```

---

## Stack technique

Nexy s’appuie sur :

- **Python** (≥ 3.10)
- **FastAPI** pour le serveur HTTP et la documentation OpenAPI/Swagger
- **Jinja2** pour le moteur de templates
- **Markdown** pour le contenu MD/MDX
- **Typer** pour la CLI
- **Uvicorn** pour l’exécution ASGI
- Intégration possible avec **Vite.js** pour la partie front si besoin.

---

## Cas d’usage

Nexy est pensé pour :

- créer des **API RESTful**
- construire des **applications web modernes** basées sur des composants
- mélanger **templates server-side** et contenu **MDX**
- exposer des routes **WebSocket** en plus des routes HTTP classiques.

L’objectif est d’offrir une expérience proche des frameworks modernes du monde JavaScript, tout
en conservant la simplicité et la robustesse de l’écosystème Python.
