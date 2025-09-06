Nexy
Nexy est un framework Python full-stack moderne, conçu pour offrir une expérience développeur (DX) de premier ordre. Il combine la rapidité de FastAPI avec un système de composants inspiré d'Astro et un routage flexible inspiré de Next.js et NestJS.

Fonctionnalités principales
Routage flexible :

Routage par fichiers (App Router) : Créez des pages et des API simplement en structurant vos dossiers.

Routage manuel : Pour des API backend complexes, utilisez des classes de contrôleurs et des décorateurs pour un contrôle total.

Système de composants avancé :

Composants .nexy avec HTML et logique Python pour des interfaces dynamiques et réactives.

Possibilité d'utiliser des composants .html avec Python pour les routes manuelles (inspiré d'Angular).

CLI puissante : Créez et gérez vos projets, pages et composants avec des commandes simples.

Support WebSockets : Construisez des applications temps réel facilement.

Démarrage rapide
Créer un nouveau projet
nexy create mon-projet
cd mon-projet
nexy dev

Structure d’un projet typique
Nexy favorise l'organisation par convention pour les projets web.

mon-projet/
├─ app/
│  ├─ index.nexy              # Route principale '/'
│  ├─ about/
│  │  ├─ index.nexy           # Route '/about'
│  │  ├─ blog/
│  │  │  └─ [slug].nexy       # Route dynamique '/about/blog/mon-article'
│  └─ api/
│     └─ users.py            # Route d'API '/api/users' (FastAPI-style)
├─ components/
│  ├─ button.nexy
│  └─ card.nexy
├─ nexy.config.py
└─ requirements.txt

Exemples de code
Composants .nexy
Créez un composant réactif en combinant HTML et Python.

components/Counter.nexy

<button @click="increment_count">{{ count }}</button>
<script>
  let count = 0;
  def increment_count():
    count += 1
</script>

Route manuelle
Pour un routage plus précis et organisé, utilisez un contrôleur.

controllers/UserController.py

from nexy.routing import APIRouter
from models.user import User

router = APIRouter(prefix="/users")

@router.get("/{user_id}")
def get_user(user_id: int):
  user = User.get(user_id)
  return user

Contribuer
Nexy est un projet open-source collaboratif.
Consultez le Guide de contribution et le Code de conduite avant de soumettre vos contributions.

Pour plus d’informations, consultez la documentation complète.