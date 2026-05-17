# Audit et Spécifications de la Documentation Nexy

## 1. Rapport d'Audit Détaillé

### 1.1 État Actuel
- **Framework** : Nexy (Python + React/Vite).
- **Contenu** : Doublon entre `_docs/` (Markdown multilingue) et `docs/src/routes/docs/` (Composants Nexy).
- **Navigation** : Manuelle, rigide, et non synchronisée avec le contenu Markdown.
- **Recherche** : Interface présente mais moteur de recherche absent.
- **Accessibilité** : Basique, non conforme aux normes WCAG 2.1 AA.
- **Expérience Utilisateur** : Design fonctionnel mais manque de finesse typographique et d'interactions modernes.

### 1.2 Points Forts
- Structure de fichiers multilingue déjà en place dans `_docs/`.
- Utilisation de Tailwind CSS 4.0 pour le styling.
- Framework Nexy capable de compiler du MDX.

### 1.3 Lacunes Critiques
- Absence d'automatisation : chaque page doit être créée manuellement.
- Pas d'exemples de code interactifs.
- Pas de système de recherche performant.
- Maintenance difficile à cause de la duplication du contenu.

---

## 2. Spécifications Fonctionnelles

### 2.1 Navigation et Structure
- **Sidebar Dynamique** : Générée automatiquement à partir de la structure de `_docs/`.
- **Table des Matières (TOC)** : Sticky, avec suivi de la lecture (active scroll).
- **Fils d'Ariane (Breadcrumbs)** : Pour une meilleure orientation.
- **Navigation Multilingue** : Basculement fluide entre EN, FR, ZH, HI, AR.

### 2.2 Fonctionnalités Avancées
- **Recherche Omnibar** : Raccourci `Ctrl+K`, recherche plein texte instantanée avec FlexSearch.
- **Code Playgrounds** : Blocs de code éditables avec prévisualisation en direct pour React, Vue, Svelte, et Solid.
- **Callouts et Alertes** : Composants MDX personnalisés pour les notes, avertissements et astuces.
- **Mode Sombre/Clair** : Support natif respectant les préférences système.

### 2.3 Accessibilité et Performance
- **WCAG 2.1 AA** : Contrastes élevés, navigation au clavier, attributs ARIA.
- **Performance** : SSG (Static Site Generation) pour des temps de chargement instantanés.
- **Mobile First** : Navigation optimisée pour les écrans tactiles.

---

## 3. Architecture Technique

### 3.1 Stack Technologique
- **Core** : Nexy Framework.
- **Frontend** : React 19 + Tailwind CSS 4.0.
- **Moteur MDX** : Intégration de `unified`, `remark`, et `rehype` pour le traitement Markdown.
- **Recherche** : FlexSearch pour l'indexation côté client.
- **Composants UI** : Radix UI (pour l'accessibilité) + Lucide Icons.

### 3.2 Flux de Données
1. **Crawl** : Un script Python scanne `_docs/` pour générer un `manifest.json`.
2. **Indexing** : Génération d'un index de recherche au build.
3. **Routing** : Utilisation du routage dynamique de Nexy (`[...slug]`) pour mapper les URLs aux fichiers Markdown.
4. **Rendering** : Le compilateur Nexy transforme le MDX en composants React avec des "shortcodes" personnalisés.

---

## 4. Guide de Déploiement Continu (CI/CD)
1. **Lint & Test** : Vérification de la syntaxe MDX et des liens morts.
2. **Build** : Exécution de `nexy build` pour générer le site statique.
3. **Deploy** : Déploiement automatique vers Vercel ou Netlify via GitHub Actions.
