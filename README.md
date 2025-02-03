![Description de l'image](logo.svg)

# Nexy

> *Un framework Python moderne qui transforme le développement web en une expérience agréable et productive, construit sur la puissance de FastAPI.*

## 📖 Table des Matières

- [Introduction](#-introduction)
- [Installation](#-installation)
- [Concepts Fondamentaux](#-concepts-fondamentaux)
- [Routing](#-routing)
- [Controllers](#-controllers)
- [Vues et Templates](#-vues-et-templates)
- [Actions et Interactivité](#-actions-et-interactivité)
- [Organisation du Code](#-organisation-du-code)
- [Déploiement](#-déploiement)
- [Bonnes Pratiques](#-bonnes-pratiques)
- [FAQ](#-faq)

## 🌟 Introduction

### Le Contexte

Le développement web en Python a toujours oscillé entre deux extrêmes :
- Des frameworks très complets mais complexes (comme Django)
- Des micro-frameworks flexibles mais nécessitant beaucoup de configuration (comme Flask)

FastAPI a révolutionné l'écosystème en apportant performance et typage moderne. Cependant, les développeurs font toujours face à des défis :

- Organisation complexe des projets grandissants
- Configuration répétitive des routes
- Manque de conventions claires
- Difficulté à gérer l'interface utilisateur

### La Vision de Nexy

Nexy est né d'une idée simple : **et si nous pouvions combiner la puissance de FastAPI avec une expérience développeur exceptionnelle ?**

Nos principes :
1. **Convention over Configuration** : Les bonnes pratiques par défaut
2. **Intuitivité** : La structure doit être naturelle et évidente
3. **Productivité** : Moins de code répétitif, plus de fonctionnalités
4. **Évolutivité** : De la petite API au projet d'entreprise

## 🚀 Installation

### Prérequis

- Python 3.12 ou supérieur
- pip (gestionnaire de paquets Python)

### Installation Simple

```bash
pip install nexy inquirerpy=="0.3.4"
```

### Création d'un Projet

```bash
nexy new mon-projet
cd mon-projet
```

### Structure Initiale

```plaintext
mon-projet/
 ├── app/
 │   ├── controller.py    # Point d'entrée principal
 │   └── view.html       # Vue principale (optionnelle)
 ├── public/             # Fichiers statiques
 └── nexy-config.py      # Configuration de l'application
```

## 🎯 Concepts Fondamentaux

### Le Routing Automatique

Nexy introduit un système de routing basé sur la structure des dossiers, inspiré des meilleures pratiques modernes.

#### Structure = Routes

```plaintext
app/
 ├── controller.py         # Route: /
 ├── users/
 │   ├── controller.py     # Route: /users
 │   └── [id]/            # Route dynamique
 │       └── controller.py # Route: /users/{id}
 └── blog/
     ├── controller.py     # Route: /blog
     └── posts/
         └── controller.py # Route: /blog/posts
```

### Les Controllers

Les controllers sont le cœur de votre application. Ils définissent comment votre application répond aux requêtes HTTP.

#### Controller Simple

```python
# app/controller.py
async def GET():
    """Route principale : GET /"""
    return {"message": "Bienvenue sur Nexy!"}

async def POST(data: dict):
    """Gestion des POST sur /"""
    return {"received": data}
```

#### Controller avec Paramètres

```python
# app/users/[id]/controller.py
async def GET(id: int):
    """Récupère un utilisateur par ID"""
    return {"user_id": id, "name": "Alice"}

async def PUT(id: int, data: dict):
    """Met à jour un utilisateur"""
    return {"updated": id, "data": data}

async def DELETE(id: int):
    """Supprime un utilisateur"""
    return {"deleted": id}
```

### Les Services

Les services permettent d'isoler la logique métier des controllers.

```python
# app/users/service.py
class UserService:
    def __init__(self):
        self.users = []
    
    def get_all(self):
        return self.users
    
    def add_user(self, user):
        self.users.append(user)
        return user

# app/users/controller.py
from .service import UserService

service = UserService()

async def GET():
    return {"users": service.get_all()}

async def POST(data: dict):
    return {"created": service.add_user(data)}
```

### Les Vues

Nexy inclut un système de templates puissant pour créer des interfaces utilisateur dynamiques.

#### Vue Simple

```html
<!-- app/view.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Mon App Nexy</title>
</head>
<body>
    <h1>Bienvenue sur {{title}}</h1>
    <ul>
        {% for user in users %}
            <li>{{user.name}}</li>
        {% endfor %}
    </ul>
</body>
</html>
```

#### Composants Réutilisables

```html
<!-- app/components/button.html -->
{% macro Button(text, type="button") %}
<button 
    class="btn btn-{{type}}"
    style="padding: 8px 16px; border-radius: 4px;">
    {{text}}
</button>
{% endmacro %}

<!-- Utilisation dans une vue -->
{% from "app/components/button.html" import Button %}

<div>
    {{ Button(text="Connexion", type="primary") }}
    {{ Button(text="Annuler", type="secondary") }}
</div>
```

### Les Layouts

Nexy supporte les layouts imbriqués pour une meilleure organisation des vues.

```html
<!-- app/layout.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    <nav>
        <!-- Navigation commune -->
    </nav>
    
    <main>
        {{children | safe}}
    </main>
    
    <footer>
        <!-- Footer commun -->
    </footer>
</body>
</html>
```

[Suite dans la prochaine partie...]

## 🌟 **Nexy**  

> *Un framework Python conçu pour allier simplicité, performance et plaisir du développement.*  

---

## **📢 Un message de l'équipe Nexy**  

⚠️ *Cette documentation est en cours de création.*  
L'équipe de développement travaille activement sur un **site dédié**, pour offrir une documentation complète, claire et accessible. Notre objectif est de vous fournir une **expérience développeur exceptionnelle**, adaptée aussi bien aux débutants qu'aux experts.

---

## **🐍 La philosophie Python au cœur de Nexy**  

Python est un langage qui se distingue par sa **simplicité, sa lisibilité** et sa grande efficacité. C'est cette philosophie qui a inspiré Nexy : rendre le développement **plus simple**, **plus rapide**, mais sans jamais sacrifier la performance.

### **Un constat**

Aujourd'hui, Python regorge de frameworks backend puissants, tels que :
- **Flask**
- **FastAPI**
- **Starlette**, etc.

Ces outils sont indéniablement **performants et modulaires**, mais leur **documentation** peut parfois être intimidante et les **configurations** complexes. Même un framework complet comme **Django** peut parfois sembler lourd et difficile à aborder, même pour les développeurs expérimentés.

### **Nexy : simplicité et efficacité**  

Chez Nexy, nous croyons que **simple ne signifie pas limité**.  
Nous avons conçu Nexy pour que les développeurs puissent se concentrer sur l'essentiel sans avoir à se perdre dans des configurations complexes.

**Ce que nous vous proposons :**  
- **Démarrage rapide** : Pas de longue configuration. Vous êtes opérationnel en quelques lignes de code.
- **Code propre et modulaire** : Organisez vos projets de manière fluide et maintenez un code lisible, même pour des projets de grande envergure.
- **Performance optimale** : Profitez de la rapidité de Python tout en préservant la simplicité.

**Le code, c'est de l'art**. Chez Nexy, chaque ligne doit être un plaisir à écrire, et votre expérience développeur compte autant que la performance du code.

---

## **🎯 Nos Objectifs**  

1. **Expérience développeur** : Rendre chaque étape du projet, du démarrage au déploiement, intuitive et agréable.
2. **Performance** : Maximiser les performances sans sacrifier la simplicité.
3. **Simplicité évolutive** : Débutez simplement et restez productif même lorsque votre projet se complexifie.

### **Ce qui nous différencie :**

- **Structure modulaire** : Organisez vos projets de manière claire et évolutive.
- **Configuration automatique** : Nexy détecte automatiquement les routes et fichiers sans que vous ayez à vous en soucier.
- **Philosophie "Plug & Play"** : Avancez rapidement sans perdre de temps dans des configurations compliquées.

---

## **📂 Structure de Projet**  

Voici un exemple d'organisation typique avec Nexy :

```plaintext
nexy/
 ├── app/
 │   ├── controller.py       # Contrôleur principal pour `/`
 │   ├── model.py            # Gestion des données pour `/`
 │   ├── service.py          # Logique métier pour `/`
 │   ├── documents/          # Endpoint `/documents`
 │   │   ├── controller.py   # Contrôleur pour `/documents`
 │   │   ├── model.py        # Gestion des données pour `/documents`
 │   │   ├── service.py      # Logique métier pour `/documents`
 │   │   └── [documentId]/   # Endpoint dynamique `/documents/{documentId}`
 │   │       ├── controller.py
 │   │       ├── model.py
 │   │       └── service.py
 │   └── users/
 │       ├── controller.py   # Contrôleur pour `/users`
 │       ├── model.py        # Gestion des données pour `/users`
 │       └── service.py      # Logique métier pour `/users`
 └── main.py                 # Point d'entrée de l'application
```

**💡 Astuce** : La structure des dossiers reflète vos routes, vous offrant ainsi une lisibilité immédiate et une organisation naturelle.

---

# Pré-requis

> Veuillez vous assurer que vous utilisez `Python >= 3.12`, car Nexy n'est **pas compatible** avec les versions `Python < 3.12`.

## Comment vérifier votre version de Python ?
Exécutez cette commande dans votre terminal :

```shell
    python --version

```



----
## **🚀 Installation et Démarrage**  

### Étape 1 : Créez un répertoire pour votre projet et placez-vous dedans 

 
1. Installez Nexy et ses dépendances :
   ```shell
   pip install nexy inquirerpy=="0.3.4"
   ```

Votre API est maintenant accessible sur **http://127.0.0.1:8000** 🎉  

Une fois que l'application est en cours d'exécution, tu peux accéder à la documentation Swagger en naviguant vers **http://localhost:8000/docs** dans ton navigateur.

---

## **🧩 Concepts Clés avec des Exemples**  

### 1. **Contrôleur de Base**  

Chaque route est définie dans un fichier `controller.py`. Exemple :  
```python
# app/controller.py
async def GET():
    return {"message": "Hello, world"}

async def POST(data: dict):
    return {"message": "Voici vos données", "data": data}
```  

### 2. **Routes Dynamiques**  

Les routes dynamiques sont automatiquement détectées :  
```plaintext
app/documents/[documentId]/controller.py
```  
```python
# app/documents/[documentId]/controller.py
async def GET(documentId: int):
    return {"documentId": documentId, "message": "Document trouvé"}
```  

### 3. **Architecture Modulaire avec `model` et `service`**  

Séparez la logique métier et la gestion des données :  
```python
# app/users/controller.py
from .service import get_users, add_user

async def GET():
    users = get_users()
    return {"users": users}

async def POST(user: dict):
    return add_user(user)
```  

```python
# app/users/service.py
from .model import User

def get_users():
    return User.all()

def add_user(data: dict):
    user = User(**data)
    user.save()
    return {"message": "Utilisateur ajouté", "user": user}
```  

---



## **📚 Pourquoi Nexy ?**  

- **Pour les débutants** : Vous trouverez une approche simple, sans surcharge de concepts, pour apprendre à coder rapidement.
- **Pour les experts** : La structure modulaire et la performance vous permettront de réaliser des projets de grande envergure tout en gardant un code propre et bien organisé.
- **Pour tous les développeurs** : Profitez de la facilité d'utilisation tout en écrivant un code performant et élégant.

Avec Nexy, vous allez découvrir un framework **simple, puissant et agréable à utiliser**. Ce n'est pas seulement un framework : c'est un outil pour **libérer votre créativité**, **accélérer votre développement**, et surtout, **vous faire apprécier chaque ligne de code**.

---


## **📢 Contribuez à Nexy !**  

🚀 Nexy est open-source et vous attend sur [GitHub](https://github.com/NexyPy/Nexy). Partagez vos idées, améliorez le framework et faites partie de la révolution backend Python.  

**💡 Nexy : Plus qu'un framework, un outil pour vous.**  
---


## 🔄 Actions et Interactivité

### Le Système d'Actions

Nexy introduit un système d'actions puissant qui permet de créer des interfaces interactives sans écrire de JavaScript complexe.

#### Actions Simples

```html
<!-- Bouton qui déclenche une action -->
<button action="increment">
    Augmenter le compteur
</button>

<!-- Zone qui se met à jour automatiquement -->
<div response="counter">
    Compteur: {{count}}
</div>
```

```python
# app/actions.py
count = 0

def increment():
    global count
    count += 1
    return count
```

#### Actions avec Paramètres

```html
<form action="add_user" method="post">
    <input type="text" name="name">
    <button type="submit">Ajouter</button>
</form>

<ul response="users">
    {% for user in users %}
        <li>
            {{user.name}}
            <button action="delete_user" data-id="{{user.id}}">❌</button>
        </li>
    {% endfor %}
</ul>
```

### Gestion d'État

Nexy permet de gérer l'état de votre application de manière simple et efficace.

```python
# app/state.py
from nexy import State

users = State([])  # État initial

def add_user(name: str):
    users.set([*users.get(), {"name": name}])
    return users.get()

def remove_user(id: int):
    users.set([u for u in users.get() if u.id != id])
    return users.get()
```

## 📦 Organisation du Code

### Structure Recommandée

```plaintext
mon-projet/
 ├── app/
 │   ├── controller.py      # Contrôleur principal
 │   ├── view.html         # Vue principale
 │   ├── actions.py        # Actions globales
 │   ├── components/       # Composants réutilisables
 │   │   ├── Button.html
 │   │   └── Card.html
 │   ├── users/           # Module Users
 │   │   ├── controller.py
 │   │   ├── view.html
 │   │   ├── actions.py
 │   │   └── service.py
 │   └── blog/            # Module Blog
 │       ├── controller.py
 │       ├── view.html
 │       └── [slug]/
 │           └── controller.py
 ├── public/              # Fichiers statiques
 │   ├── css/
 │   ├── js/
 │   └── images/
 ├── tests/              # Tests
 └── nexy-config.py      # Configuration
```

### Bonnes Pratiques

#### 1. Organisation Modulaire

Regroupez les fonctionnalités liées dans des modules :

```plaintext
app/users/
 ├── controller.py    # Gestion des requêtes
 ├── service.py       # Logique métier
 ├── view.html        # Interface utilisateur
 └── actions.py       # Interactions utilisateur
```

#### 2. Séparation des Responsabilités

```python
# app/users/controller.py
from .service import UserService

service = UserService()

async def GET():
    return service.get_users()

# app/users/service.py
class UserService:
    def get_users(self):
        # Logique métier isolée
        return [...]
```

## 🛠️ Outils de Développement

### CLI Nexy

```bash
# Création
nexy new mon-projet     # Nouveau projet
nexy g co users        # Nouveau controller
nexy g s users         # Nouveau service

# Développement
nexy dev              # Serveur de développement
nexy build            # Construction pour production
```

### Hot Reload

Nexy inclut un système de rechargement automatique en développement :
- Modifications de code Python
- Changements dans les templates
- Mise à jour des fichiers statiques

## 🚀 Déploiement

### Construction pour Production

```bash
nexy build
```

### Configuration de Production

```python
# nexy-config.py
from nexy import Nexy

app = Nexy(
    production=True,
    static_cache=True
)
```

### Plateformes Supportées

- Vercel
- Heroku
- Docker
- VPS classique

## 🎯 Exemples Complets

### 1. Application Todo

```python
# app/todos/controller.py
from nexy import HTMLResponse, CustomResponse

todos = []

@CustomResponse(type=HTMLResponse)
async def GET():
    return {"todos": todos}

async def POST(data: dict):
    todos.append(data)
    return {"status": "success"}
```

```html
<!-- app/todos/view.html -->
{% from "app/components/button.html" import Button %}

<div class="todos">
    <form action="add" method="post">
        <input type="text" name="task" placeholder="Nouvelle tâche">
        {{ Button(text="Ajouter") }}
    </form>

    <ul response="todos">
        {% for todo in todos %}
            <li>
                {{todo.task}}
                <button action="delete" data-id="{{loop.index}}">
                    Supprimer
                </button>
            </li>
        {% endfor %}
    </ul>
</div>
```

### 2. API REST

```python
# app/api/users/controller.py
from typing import List
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str

users: List[User] = []

async def GET():
    return {"users": users}

async def POST(user: User):
    users.append(user)
    return {"status": "created", "user": user}
```

## 🤝 Contribution

1. Fork le projet
2. Créez votre branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📚 Ressources

- [Documentation Officielle](https://docs.nexy.py)
- [Guide de Démarrage](https://docs.nexy.py/getting-started)
- [Exemples](https://github.com/nexy/examples)
- [Discord Community](https://discord.gg/nexy)

## ❓ FAQ

### Q: Nexy est-il prêt pour la production ?
R: Oui ! Nexy est construit sur FastAPI et suit les meilleures pratiques de développement.

### Q: Puis-je utiliser Nexy pour des APIs uniquement ?
R: Absolument ! Bien que Nexy excelle dans les applications full-stack, il est parfait pour les APIs REST.

### Q: Comment contribuer à Nexy ?
R: Consultez notre guide de contribution et rejoignez notre Discord !

## 🌟 Pour Finir

Nexy est plus qu'un framework - c'est une nouvelle façon de penser le développement web en Python. Simple mais puissant, il vous permet de vous concentrer sur ce qui compte vraiment : créer des applications exceptionnelles.

---

*Fait avec ❤️ par la communauté Python*