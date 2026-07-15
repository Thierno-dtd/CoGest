# Gestion Commerciale — IAI Gabon

Application web complète de **Gestion Commerciale** (achats, ventes, stock, clients,
fournisseurs, facturation, tableau de bord décisionnel), développée avec **Django 5**,
**HTMX**, **Alpine.js** et **Chart.js**.

Conçue pour répondre point par point au cahier des charges *« Conception et Développement
d'une Application de Gestion Commerciale »*, avec une interface pensée par un
ingénieur logiciel et un designer produit : Bento Grid, effet « Liquid Glass »,
recherche instantanée, actions au survol, pagination claire, export PDF.

---

## 1. Aperçu des fonctionnalités

- **Produits & catégories** : CRUD complet, alertes de seuil, rupture de stock, recherche multicritère instantanée.
- **Clients & fournisseurs** : fiches complètes avec historique, chiffre d'affaires, encours de crédit, dette fournisseur.
- **Achats** : bon d'achat multi-lignes → génère automatiquement la facture d'achat et met à jour le stock (entrée).
- **Ventes** : bon de vente multi-lignes → vérifie le stock disponible, génère la facture de vente et diminue le stock (sortie). Annulation possible (restitution du stock).
- **Stock** : **jamais modifiable manuellement** — uniquement via les achats/ventes — avec historique complet des mouvements (avant/après, document d'origine).
- **Facturation & règlements** : calcul dynamique HT/TVA/TTC (jamais stocké en dur), règlements multiples, suivi des soldes, export PDF professionnel.
- **Tableau de bord** : KPI en Bento Grid, 5 graphiques interactifs (Chart.js) avec filtres indépendants (période, critère), export de l'état actuel en PDF (impression navigateur).
- **Comptes utilisateurs** : rôles (Administrateur, Vendeur, Gestionnaire de stock, Comptable), modification du profil et du mot de passe par l'utilisateur connecté.

### Détails UI/UX demandés
- **Recherche automatique** : les tableaux se filtrent au fur et à mesure de la frappe (HTMX, sans bouton « Rechercher »).
- **Actions cachées au survol** : les boutons Modifier/Supprimer d'une ligne n'apparaissent qu'au survol de cette ligne.
- **Pagination claire** : « Affichage X–Y sur Z », navigation par numéros de page.
- **Stats globales sur chaque page** (clients, produits, ventes, achats, factures…).
- **Design distinctif** : palette « atelier » sable/graphite/cuivre, typographie Fraunces + Manrope, effet verre dépoli (glassmorphism) sur les panneaux flottants, Bento Grid pour les KPI — volontairement différent des gabarits « IA générique » (pas de bordures colorées systématiques, pas de puces clignotantes).

---

## 2. Architecture technique

```
gestion_commerciale/
├── config/            # Réglages Django, urls racine
├── accounts/           # Utilisateur personnalisé (rôles), connexion, profil
├── core/               # Services métier transverses (numérotation, création achats/ventes),
│                       # pagination, décorateurs de rôle, template tags
├── produits/           # Catégories & produits
├── tiers/              # Clients & fournisseurs
├── achats/             # Achats + lignes d'achat
├── ventes/             # Ventes + lignes de vente
├── stock/               # Mouvements de stock (lecture seule, généré automatiquement)
├── facturation/        # Factures (calculs dynamiques) + règlements + génération PDF
├── dashboard/          # Tableau de bord + endpoints JSON pour les graphiques
├── static/             # CSS (design system), JS (HTMX helpers, formulaires dynamiques)
└── templates/          # base.html, connexion
```

### Choix techniques importants

- **Aucune donnée de stock n'est modifiable directement** : toute la logique passe par
  `core/services.py` (`creer_achat`, `creer_vente`, `annuler_vente`), qui gère dans une
  transaction atomique : création des lignes, mouvement de stock, mise à jour de la
  quantité, génération de la facture.
- **Montants de facture calculés dynamiquement** (jamais stockés en dur) via les
  propriétés Python de `Facture` (`montant_ht`, `montant_tva`, `montant_ttc`,
  `solde_restant`...). Les totaux d'Achat/Vente disposent d'un cache
  (`total_ttc_cache`, etc.) recalculé automatiquement à chaque modification de lignes,
  uniquement à des fins de performance d'affichage/statistiques.
- **HTMX** gère la recherche instantanée, les filtres, la pagination et les modales de
  confirmation de suppression, sans recharger toute la page.
- **Export PDF des factures** via `reportlab` (pas de dépendance système comme
  WeasyPrint — fonctionne partout, y compris sur Windows sans librairies supplémentaires).
- **Export du tableau de bord en PDF** : bouton « Exporter l'état actuel en PDF » qui
  déclenche l'impression du navigateur avec une feuille de style dédiée (masque le menu,
  la barre de recherche, etc.) — le visiteur choisit ensuite « Enregistrer en PDF »
  dans la boîte de dialogue d'impression. C'est la solution la plus fiable et la plus
  légère pour capturer plusieurs graphiques Chart.js dans leur état filtré actuel.

---

## 3. Installation pas à pas

### Prérequis
- Python 3.11 ou 3.12 installé (vérifiez avec `python3 --version` ou `python --version`)
- pip installé

### Étape 1 — Décompresser le projet
Décompressez l'archive reçue, puis ouvrez un terminal dans le dossier `gestion_commerciale`.

### Étape 2 — Créer un environnement virtuel

**Sous Windows (PowerShell) :**
```bash
python -m venv venv
venv\Scripts\activate
```

**Sous macOS / Linux :**
```bash
python3 -m venv venv
source venv/bin/activate
```

Vous devez voir `(venv)` apparaître au début de votre invite de commande.

### Étape 3 — Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 4 — Appliquer les migrations (création de la base de données)
```bash
python manage.py migrate
```

### Étape 5 — Générer des données de démonstration (recommandé)
Cette commande crée automatiquement : 4 comptes utilisateurs, 6 catégories, 24 produits,
24 clients, 7 fournisseurs, ainsi que ~140 achats/ventes avec factures et règlements
répartis sur les 6-7 derniers mois (pour que les graphiques du tableau de bord soient
immédiatement parlants).

```bash
python manage.py seed_demo
```

À l'issue de cette commande :
- **Administrateur** : `admin` / `admin1234`
- **Vendeur** : `vendeur1` / `passer1234`
- **Gestionnaire de stock** : `stock1` / `passer1234`
- **Comptable** : `compta1` / `passer1234`

> Si vous préférez repartir d'une base vierge, sautez cette étape et créez directement
> votre propre compte administrateur avec `python manage.py createsuperuser`.

### Étape 6 — Lancer le serveur de développement
```bash
python manage.py runserver
```

Ouvrez votre navigateur à l'adresse : **http://127.0.0.1:8000/**

Vous serez redirigé vers la page de connexion. Connectez-vous avec l'un des comptes
ci-dessus pour accéder au tableau de bord.

### Étape 7 (optionnelle) — Accéder à l'administration Django
`http://127.0.0.1:8000/admin/` avec le compte `admin` — utile pour une vue technique
brute de toutes les tables pendant la soutenance.

---

## 4. Utilisation rapide

1. **Créer un produit** : menu *Produits → Nouveau produit*.
2. **Enregistrer un achat** : menu *Achats → Nouvel achat* → choisir le fournisseur,
   ajouter une ou plusieurs lignes de produits → si le statut de livraison est
   « Reçue », le stock est immédiatement incrémenté et la facture d'achat générée.
3. **Enregistrer une vente** : menu *Ventes → Nouvelle vente* → le système vérifie que
   le stock est suffisant avant de valider, décrémente le stock et génère la facture.
4. **Encaisser/payer une facture** : *Factures → ouvrir une facture → Enregistrer un
   règlement* (partiel ou total, plusieurs règlements possibles).
5. **Tableau de bord** : filtrez chaque graphique indépendamment (période, critère),
   puis cliquez sur *Exporter l'état actuel en PDF*.
6. **Mon profil** : cliquez sur votre avatar en haut à droite → *Modifier mes
   informations* ou *Changer mon mot de passe*.

---

## 5. Notes pour la soutenance / le rapport

- Le **modèle de classes** fourni (`classe.docx`) a été respecté : mêmes entités,
  mêmes attributs, mêmes relations (Utilisateur, Catégorie, Produit, Client,
  Fournisseur, Achat/LigneAchat, Vente/LigneVente, MouvementStock, Facture, Règlement).
- Les champs `mot_de_passe_hash` / `sel` / `est_actif` / `date_derniere_connexion` du
  modèle `Utilisateur` sont gérés nativement par Django (`password` avec hachage
  PBKDF2+sel intégré, `is_active`, `last_login`) — c'est la pratique standard et
  sécurisée plutôt que de réinventer un système de hachage.
- Le champ *stock jamais modifiable directement* est appliqué au niveau formulaire
  (champ désactivé une fois le produit créé) **et** au niveau architecture (aucune vue
  n'expose de formulaire d'édition du stock — seuls `core/services.py` y touchent).

Bon courage pour la présentation ! 🇬🇦
