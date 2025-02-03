# Nexy Framework

> Un framework Python moderne qui transforme le développement web en une expérience agréable et productive, construit sur la puissance de FastAPI.

## Table des Matières

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Guide de Démarrage](#guide-de-démarrage)
4. [Architecture](#architecture)
5. [Fonctionnalités Principales](#fonctionnalités-principales)
6. [Fonctionnalités Avancées](#fonctionnalités-avancées)
7. [Sécurité](#sécurité)
8. [Performance](#performance)
9. [Déploiement](#déploiement)
10. [Contribution](#contribution)
11. [Ressources](#ressources)

## Introduction

### La Vision de Nexy

Nexy est né d'une vision simple mais ambitieuse : créer un framework web Python qui allie la puissance de FastAPI avec une expérience développeur exceptionnelle. Notre objectif est de permettre aux développeurs de se concentrer sur la création de valeur plutôt que sur la configuration technique.

### Pourquoi Nexy ?

- **Simplicité d'Utilisation** : Architecture intuitive et conventions claires
- **Performance Optimale** : Basé sur FastAPI et ses fondations asynchrones
- **Productivité Maximale** : Génération automatique de code et outils CLI puissants
- **Flexibilité** : S'adapte aussi bien aux petits projets qu'aux applications d'entreprise
- **Sécurité Intégrée** : Bonnes pratiques de sécurité par défaut
- **Documentation Complète** : Guides détaillés et exemples pratiques

### Comparaison avec d'Autres Frameworks

| Caractéristique | Nexy | FastAPI | Django | Flask |
|----------------|------|----------|---------|-------|
| Setup Rapide | ✅ | ⚠️ | ❌ | ✅ |
| Performance | ✅ | ✅ | ⚠️ | ⚠️ |
| Batteries Included | ✅ | ❌ | ✅ | ❌ |
| Courbe d'Apprentissage | Faible | Moyenne | Élevée | Faible |

## Installation

### Prérequis Détaillés

- Python 3.12 ou supérieur
- pip version 21.0 ou supérieure
- Virtualenv (recommandé)
- Git (pour le contrôle de version)

### Installation Pas à Pas

```bash
# 1. Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Installer Nexy et ses dépendances
pip install nexy inquirerpy=="0.3.4"

# 3. Créer un nouveau projet
nexy new mon-projet

# 4. Initialiser Git (optionnel mais recommandé)
cd mon-projet
git init
```

### Structure Initiale Détaillée

```plaintext
mon-projet/
├── app/
│   ├── controller.py    # Contrôleur principal
│   ├── view.html       # Vue principale
│   ├── models/         # Modèles de données
│   │   └── __init__.py
│   ├── services/       # Services métier
│   │   └── __init__.py
│   └── utils/         # Utilitaires
│       └── __init__.py
├── public/             # Fichiers statiques
│   ├── css/
│   ├── js/
│   └── images/
├── tests/             # Tests unitaires et d'intégration
│   └── __init__.py
├── .env               # Variables d'environnement
├── .gitignore        # Configuration Git
└── nexy-config.py    # Configuration de l'application
```

## Guide de Démarrage

### Premier Contrôleur

```python
# app/controller.py
from typing import Dict, Optional
from pydantic import BaseModel

class Response(BaseModel):
    status: str
    message: str
    data: Optional[Dict] = None

async def GET():
    """
    Point d'entrée principal - GET /
    
    Returns:
        Response: Message de bienvenue avec statut
    """
    return Response(
        status="success",
        message="Bienvenue sur Nexy!",
        data={"version": "1.0.0"}
    )

async def POST(data: dict):
    """
    Gestion des requêtes POST sur /
    
    Args:
        data (dict): Données reçues dans la requête
        
    Returns:
        Response: Confirmation de réception des données
    """
    return Response(
        status="success",
        message="Données reçues avec succès",
        data=data
    )
```

### Première Vue

```html
<!-- app/view.html -->
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title | default("Mon Application Nexy") }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <nav>
            <ul>
                <li><a href="/">Accueil</a></li>
                <li><a href="/users">Utilisateurs</a></li>
                <li><a href="/about">À propos</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <h1>{{ title }}</h1>
        
        <div response="content">
            {% block content %}
                <p>{{ message }}</p>
            {% endblock %}
        </div>
    </main>

    <footer>
        <p>&copy; {{ year }} Mon Application Nexy</p>
    </footer>

    <script src="/static/js/main.js"></script>
</body>
</html>
```

## Architecture

### Système de Routing Détaillé

Le routing dans Nexy est basé sur la structure des dossiers, avec plusieurs options avancées :

#### Routes Statiques

```plaintext
app/
├── controller.py         # /
├── about/
│   └── controller.py     # /about
└── contact/
    └── controller.py     # /contact
```

#### Routes Dynamiques

```python
# app/users/[id]/controller.py
from typing import Union
from nexy import NotFoundError

async def GET(id: int):
    """
    Récupère un utilisateur par son ID
    
    Args:
        id (int): ID de l'utilisateur
        
    Raises:
        NotFoundError: Si l'utilisateur n'existe pas
        
    Returns:
        dict: Données de l'utilisateur
    """
    user = await get_user_by_id(id)
    if not user:
        raise NotFoundError(f"Utilisateur {id} non trouvé")
    return user

async def PUT(id: int, data: dict):
    """
    Met à jour un utilisateur
    
    Args:
        id (int): ID de l'utilisateur
        data (dict): Nouvelles données
        
    Returns:
        dict: Utilisateur mis à jour
    """
    return await update_user(id, data)

async def DELETE(id: int):
    """
    Supprime un utilisateur
    
    Args:
        id (int): ID de l'utilisateur
        
    Returns:
        dict: Confirmation de suppression
    """
    await delete_user(id)
    return {"status": "success", "message": f"Utilisateur {id} supprimé"}
```

#### Routes avec Middleware

```python
# app/admin/middleware.py
from nexy import Middleware
from .auth import verify_admin_token

class AdminMiddleware(Middleware):
    async def process_request(self, request):
        token = request.headers.get("Authorization")
        if not await verify_admin_token(token):
            raise UnauthorizedError("Accès non autorisé")
```

### Services et Logique Métier

```python
# app/services/user_service.py
from typing import List, Optional
from .database import Database
from ..models.user import User

class UserService:
    def __init__(self):
        self.db = Database()
    
    async def get_all(self) -> List[User]:
        """Récupère tous les utilisateurs"""
        users = await self.db.query("SELECT * FROM users")
        return [User(**user) for user in users]
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par son ID"""
        user = await self.db.query_one(
            "SELECT * FROM users WHERE id = ?",
            [user_id]
        )
        return User(**user) if user else None
    
    async def create(self, user_data: dict) -> User:
        """Crée un nouvel utilisateur"""
        user_id = await self.db.insert("users", user_data)
        return await self.get_by_id(user_id)
    
    async def update(self, user_id: int, user_data: dict) -> Optional[User]:
        """Met à jour un utilisateur"""
        success = await self.db.update(
            "users",
            user_data,
            {"id": user_id}
        )
        return await self.get_by_id(user_id) if success else None
    
    async def delete(self, user_id: int) -> bool:
        """Supprime un utilisateur"""
        return await self.db.delete("users", {"id": user_id})
```

## Fonctionnalités Principales

### Système de Templates Avancé

#### Layouts

```html
<!-- app/layouts/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %} - MonApp</title>
    {% block head %}{% endblock %}
</head>
<body>
    <header>
        {% include "components/nav.html" %}
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        {% include "components/footer.html" %}
    </footer>
</body>
</html>
```

#### Composants Réutilisables

```html
<!-- app/components/button.html -->
{% macro Button(text, type="button", class="", disabled=false) %}
<button 
    type="{{ type }}"
    class="btn {{ class }}"
    {% if disabled %}disabled{% endif %}
    {% block attributes %}{% endblock %}
>
    {{ text }}
</button>
{% endmacro %}

<!-- Utilisation -->
{% from "components/button.html" import Button %}
{{ Button("Envoyer", type="submit", class="btn-primary") }}
```

### Gestion d'État

```python
# app/state.py
from nexy import State, StateManager

# État global
app_state = StateManager()

# États spécifiques
users = State([])
settings = State({
    "theme": "light",
    "language": "fr"
})

# Actions
@app_state.action
def add_user(state, user):
    users.set([*users.get(), user])
    return users.get()

@app_state.action
def update_settings(state, new_settings):
    settings.set({**settings.get(), **new_settings})
    return settings.get()
```

## Fonctionnalités Avancées

### Validation des Données

```python
# app/models/user.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True
```

### WebSockets

```python
# app/websockets/chat.py
from nexy import WebSocket
from typing import List, Set
from .models import Message

class ChatWebSocket(WebSocket):
    clients: Set[WebSocket] = set()
    
    async def connect(self):
        await self.accept()
        self.clients.add(self)
        await self.broadcast({"type": "join", "user": self.user.username})
    
    async def disconnect(self, close_code):
        self.clients.remove(self)
        await self.broadcast({"type": "leave", "user": self.user.username})
    
    async def receive_json(self, content):
        message = Message(**content)
        await self.broadcast({
            "type": "message",
            "user": self.user.username,
            "content": message.content
        })
    
    @classmethod
    async def broadcast(cls, message: dict):
        for client in cls.clients:
            await client.send_json(message)
```

### Tâches en Arrière-plan

```python
# app/tasks/scheduler.py
from nexy import Task
from datetime import timedelta

@Task.periodic(timedelta(minutes=15))
async def cleanup_sessions():
    """Nettoie les sessions expirées toutes les 15 minutes"""
    await db.delete_expired_sessions()

@Task.delayed
async def send_welcome_email(user_id: int):
    """Envoie un email de bienvenue de façon asynchrone"""
    user = await User.get(user_id)
    await mailer.send(
        to=user.email,
        template="welcome",
        context={"user": user}
    )
```

## Sécurité

### Authentification

```python
# app/auth/jwt.py
from nexy import JWT, JWTConfig
from datetime import timedelta

jwt = JWT(
    config=JWTConfig(
        secret_key="votre-clé-secrète",
        algorithm="HS256",
        access_token_expire=timedelta(minutes=15),
        refresh_token_expire=timedelta(days=7)
    )
)

# Middleware d'authentification
from nexy import Middleware

class AuthMiddleware(Middleware):
    async def process_request(self, request):
        token = request.headers.get("Authorization")
        if not token:
            raise UnauthorizedError()
        
        try:
            payload = jwt.decode(token)
            request.user = await User.get(payload["user_id"])
        except JWTError:
            raise UnauthorizedError()
```

### CORS

```python
# nexy-config.py
from nexy import Nexy, CORSConfig

app = Nexy(
    cors=CORSConfig(
        allow_origins=["https://monapp.com"],
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization"],
        max_age=3600
    )
)
```

## Performance

### Cache

```python
# app/cache.py
from nexy import Cache
from datetime import timedelta

cache = Cache()

@cache.cached(ttl=timedelta(minutes=