# Nexy

Nexy est un meta-framework Python Fullstack conçu pour simplifier la création d'applications web modernes. En combinant la robustesse de FastAPI avec la flexibilité des outils frontend actuels (Vite, React, Vue, Svelte, Solid), Nexy 2 permet de bâtir des interfaces riches et performantes au sein d'un écosystème Python unifié.

## La vision de Nexy 2

Nexy 2 transforme l'expérience de développement en masquant la complexité architecturale derrière une interface intuitive. Le framework gère l'orchestration entre le serveur Python et le client JavaScript, vous permettant de vous concentrer exclusivement sur la logique métier et l'interface utilisateur.

## Concepts Fondamentaux

L'apprentissage de Nexy repose sur trois piliers essentiels :

### 1. Le Format .nexy (Composant Polyglotte)
L'unité de base de Nexy est le fichier `.nexy`. Contrairement aux frameworks traditionnels, il permet une composition fluide de plusieurs langages :
- **Header (Python)** : Délimité par `---`, c'est ici que vous définissez vos propriétés (`prop`) et importez vos composants (qu'ils soient `.nexy`, `.vue`, `.tsx`, ou même des fonctions Python).
- **Template (HTML/Jinja2)** : La structure de votre composant, rendue côté serveur avec la puissance de Jinja2.


```html
---
# Logique de définition (Python)
title : prop[str] = "Composant Nexy"
from "@/components/Card.nexy" import Card
from nexy import Vite  # Injection automatique des assets
---
<!-- Rendu Serveur (Jinja2) -->
<div class="p-6 bg-white rounded-xl shadow-lg">
    <h1 class="text-2xl font-bold">{{ title }}</h1>
    <Card content="Je peux contenir d'autres composants." />
</div>

```

### 2. Routage Hybride et Intelligent
Nexy s'adapte à la taille de votre projet :
- **File-Based Routing** : La structure de `src/routes/` définit vos URLs (ex: `index.nexy` -> `/`).
- **Module-Based Routing** : Pour les architectures d'entreprise, utilisez une approche modulaire inspirée de NestJS.
- **Rendu Hybride** : Mélangez pages statiques et routes API dynamiques dans un même projet.

### 3. Écosystème Unifié via Vite
Nexy n'impose pas de framework client. Vous pouvez importer et utiliser des composants React, Vue, Svelte ou Solid directement dans vos templates Nexy. Le pipeline de build Vite s'occupe de tout, garantissant des performances optimales et une configuration zéro.

## Outillage et Développement

### CLI Nexy (nx)
L'outil `nx` centralise vos commandes de développement :
- `nx init` ou `nexy init` : Initialise un projet nexy 
- `nx dev` ou `nexy dev` : Lance le serveur Nexy pour le developpement avec Vite en parallèle.
- `nx build` ou `nexy build` : Compile vos assets pour une mise en production optimisée.
- `nx start` ou ``nexy start` : lance le serveur Nexy pour la production et sans vite en parrallèle 

### Extension VS Code
Une extension dédiée (LSP) est incluse dans le dépôt pour offrir une expérience de développement de premier plan : diagnostics en temps réel, auto-complétion des props et des imports, et snippets contextuels.

## Démarrage Rapide

### Pré-requis
- Python 3.10+
- Node.js 18+

### Installation
```bash
pip install nexy
```

### Initialisation
```bash
nexy init
```
L'assistant interactif vous permettra de choisir votre framework frontend préféré et d'activer Tailwind CSS.

### Lancement
```bash
nexy dev
```

## Sécurité et Fiabilité
- **Typage Strict** : Utilisation de Pydantic pour la validation des données et des props.
- **Protection Native** : Auto-escaping Jinja2 contre les failles XSS.
- **Architecture Durable** : Respect des principes SOLID pour faciliter la maintenance à long terme.

## Licence
Distribué sous licence MIT.