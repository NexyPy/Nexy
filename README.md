
# 🌟 **Nexy**

Bienvenue dans l'univers de **Nexy**, un framework de développement back-end **innovant et performant**, conçu pour **optimiser votre productivité**.  
🚀 **Simplicité**, 🌍 **dynamisme**, et **efficacité maximale** : Nexy vous permet de **concevoir, tester et déployer vos applications** avec rapidité et fluidité, tout en réduisant la complexité du processus de développement.

---

### **🧩 Pourquoi Choisir Nexy ?**  

👉 **Configuration simplifiée** : La structure de vos dossiers se transforme automatiquement en un routeur, sans nécessiter de décorateurs ou d'importations complexes.  

👉 **Gagnez du temps** : Ajoutez simplement un fichier ou un dossier dans `app/`, et Nexy génère les routes pour vous, automatiquement.  

👉 **Simplicité et puissance** : Libérez-vous des contraintes inutiles pour vous concentrer sur l’essentiel — votre logique métier.  

👉 **Un projet open-source, une communauté engagée** : Nexy est un projet open-source, conçu avec passion ❤️. Rejoignez notre communauté pour contribuer et façonner l'avenir du développement web.

---

### **📂 Structure de Projet avec Nexy**  

Voici comment structurer votre projet en utilisant Nexy :  

```plaintext
nexy/
 ├── app/                # Dossier contenant les contrôleurs et routes
 │   ├── controller.py   # Route par défaut /
 │   ├── documents/      # Dossier pour /documents
 │   │   ├── controller.py  # Route /documents
 │   │   └── [documentId]/  # Dossier dynamique pour /documents/{documentId}
 │   │       └── controller.py  # Route /documents/{documentId}
 │   └── users/          # Dossier pour /users
 │       └── controller.py  # Route /users
 └── main.py             # Fichier de configuration de Nexy
```

📝 **Chaque fichier `controller.py`** définit les routes de la section correspondante.  
🎯 **La structure des dossiers correspond aux routes de l'API**, générées automatiquement.

---

### **🌐 Exemple de Code avec Nexy**  

#### **Route par défaut `/`**  

**Fichier** : `app/controller.py`  

```python
async def GET():
    return {"message": "Bienvenue sur l'API Nexy"}

async def POST(data: dict):
    return {"message": "Données reçues avec succès", "data": data}
```

---

#### **Route dynamique pour `/documents/{documentId}` avec WebSocket**  

**Fichier** : `app/documents/[documentId]/controller.py`  

```python
async def GET(documentId: int):
    return {"documentId": documentId, "message": "Voici votre document"}

async def PUT(documentId: int, document: dict):
    return {"message": "Document mis à jour", "documentId": documentId, "document": document}

async def DELETE(documentId: int):
    return {"message": f"Document {documentId} supprimé"}

async def Socket(websocket):
    await websocket.accept()
    await websocket.send_text("Connexion WebSocket établie.")
    await websocket.close()
```

---

#### **Route pour `/users`**  

**Fichier** : `app/users/controller.py`  

```python
async def GET():
    return {"message": "Liste des utilisateurs"}

async def POST(user: dict):
    return {"message": "Nouvel utilisateur ajouté", "user": user}
```

---

### **✨ Pourquoi Contribuer à Nexy ?**  

🚀 **Rejoignez une aventure passionnante** : Nexy est en constante évolution, et nous avons besoin de votre expertise pour continuer à repousser les limites de l'innovation.  
🤝 **Collaborez avec une communauté dynamique** : Venez partager vos idées et apprendre aux côtés de développeurs de talent.  
🌟 **Participez à un projet qui transforme l’industrie** : Votre contribution pourrait simplifier la vie de milliers de développeurs à travers le monde.  

---

### **💬 Un Message pour Vous, Contributeurs et Passionnés**  

**Nexy est conçu pour vous** 💛. Que vous soyez débutant ou expert, ce framework est pensé pour rendre le développement **plus intuitif, rapide et agréable**.  

👉 **Testez-le dès aujourd’hui** : Téléchargez Nexy et découvrez sa simplicité.  
👉 **Envie de contribuer ?** Rejoignez-nous sur [GitHub](#) et aidez-nous à bâtir le framework full-stack de demain.  

**💡 Nexy : Simplifions ensemble le développement web avec Python.** 🌍✨

