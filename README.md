
![Description de l'image](logo.svg)

## 🌟 **Nexy**  

> *Un framework Python conçu pour allier simplicité, performance et plaisir du développement.*  

---

## **📢 Un message de l'équipe Nexy**  

⚠️ *Cette documentation est en cours de création.*  
L’équipe de développement travaille activement sur un **site dédié**, pour offrir une documentation complète, claire et accessible. Notre objectif est de vous fournir une **expérience développeur exceptionnelle**, adaptée aussi bien aux débutants qu'aux experts.

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

**Le code, c’est de l’art**. Chez Nexy, chaque ligne doit être un plaisir à écrire, et votre expérience développeur compte autant que la performance du code.

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

## **🚀 Installation et Démarrage**  

### Étape 1 : Créez et activez un environnement virtuel

Avant de commencer, il est fortement recommandé de créer un environnement virtuel pour isoler les dépendances de votre projet.

1. **Créez un environnement virtuel** :
   ```bash
   python -m venv venv
   ```

2. **Activez l'environnement virtuel** :
   - **Sous Windows** :
     ```bash
     venv\Scripts\activate
     ```
   - **Sous macOS/Linux** :
     ```bash
     source venv/bin/activate
     ```

### Étape 2 : Initialisez votre projet  

1. Créez un répertoire pour votre projet et placez-vous dedans :
   ```bash
   mkdir nexy-app && cd nexy-app
   ```

2. Installez Nexy et ses dépendances :
   ```bash
   pip install nexy uvicorn
   ```

3. Créez les fichiers nécessaires au projet :
   - **main.py** : Le fichier principal de votre application.
   - **app/controller.py** : Le contrôleur de base pour gérer vos routes.

4. Exemple de code pour **`main.py`** :

   ```python
   from nexy import Nexy

   app = Nexy()

   # Appel à un contrôleur dans 'app/controller.py'
   ```

5. Exemple de code pour **`app/controller.py`** :

   ```python
   # app/controller.py
   async def GET():
       return {"message": "Bienvenue sur Nexy"}

   def POST():
       return 12
   ```

6. Lancez le serveur avec `uvicorn` :
   ```bash
   uvicorn main:app --reload
   ```

---

## **📚 Pourquoi Nexy ?**  

- **Pour les débutants** : Vous trouverez une approche simple, sans surcharge de concepts, pour apprendre à coder rapidement.
- **Pour les experts** : La structure modulaire et la performance vous permettront de réaliser des projets de grande envergure tout en gardant un code propre et bien organisé.
- **Pour tous les développeurs** : Profitez de la facilité d’utilisation tout en écrivant un code performant et élégant.

Avec Nexy, vous allez découvrir un framework **simple, puissant et agréable à utiliser**. Ce n’est pas seulement un framework : c'est un outil pour **libérer votre créativité**, **accélérer votre développement**, et surtout, **vous faire apprécier chaque ligne de code**.




