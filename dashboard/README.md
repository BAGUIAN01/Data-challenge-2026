# Tableau de bord local-first

Application Next.js du Défi 1. Elle répond à trois questions, région par région :
- **où agir en premier** : carte et matrice de priorité ;
- **où le risque monte** : calendrier d'alerte ;
- **combien d'élèves** : estimation des effectifs à partir des écoles ouvertes à la rentrée.

Elle s'utilise **sans réseau** et garde ses données dans une base **Neon** (PostgreSQL) pour la version en ligne.

## Comment elle fonctionne sans réseau

| Besoin | Ce qui le permet |
| --- | --- |
| **Lire** | Les données sont lues d'abord dans la base de l'appareil (IndexedDB, via Dexie). Elles sont mises à jour depuis Neon quand le serveur répond. Si l'appareil n'a encore rien, il utilise le jeu de données publié avec l'application. |
| **Écrire** | Une saisie (écoles ouvertes à la rentrée) est enregistrée tout de suite sur l'appareil et s'affiche aussitôt. Elle part vers Neon au retour du réseau, avec une clé (`client_id`) qui empêche tout doublon. |
| **Ouvrir** | Le service worker (Serwist) garde sur l'appareil toutes les pages, les 13 fiches régionales, les scripts, les données et les fiches PDF. Aucune page ne lit le serveur au moment où elle s'affiche. |
| **Dire** | Un bandeau indique d'où viennent les données (« Sans réseau : données de cet appareil, reçues le… ») et combien de saisies attendent le réseau. |
| **Prouver** | `npm run verif:hors-ligne` vérifie tout cela dans un vrai navigateur, **serveur arrêté**. Avec le service worker bloqué (`VERIF_SABOTAGE=1`), le contrôle échoue, comme il doit. |

## Lancer en local

Depuis `dashboard/` :

```bash
npm install
```

```bash
npm run build
```

```bash
npm start
```

L'application s'ouvre sur http://localhost:3000.

**Sans `DATABASE_URL`, elle fonctionne quand même.** Elle utilise le jeu de données publié avec l'application (`public/data/tableau_de_bord.json`), et les saisies restent sur l'appareil.

## Brancher Neon

1. **Créez un projet** sur neon.tech et copiez la chaîne de connexion *pooled* (avec `sslmode=require`).
2. **Copiez `.env.example` en `.env.local`** et collez-y cette chaîne : `DATABASE_URL=...`.
3. **Créez les tables, puis chargez les données :**

   ```bash
   npm run db:schema
   ```

   ```bash
   npm run db:seed
   ```

4. **Vérifiez que la base rend exactement le fichier exporté :**

   ```bash
   npm run verif:aller-retour
   ```

**En ligne (Vercel, par exemple)** : déclarez `DATABASE_URL` dans les variables d'environnement du projet, avec `dashboard` comme dossier racine.

**Le schéma** (`db/schema.sql`) :
- `jeu_donnees` : les versions publiées, dont une seule est active ;
- `region`, `indicateur`, `alerte`, `facteur`, `texte` : les données de chaque version, en tables interrogeables en SQL ;
- `saisie_ecoles` : les saisies du terrain, conservées d'une version à l'autre.

## Mettre à jour les données

Depuis la racine du dépôt, après les scripts d'analyse :

```bash
python scripts/export_tableau_de_bord.py
```

Puis, dans `dashboard/` :

```bash
npm run db:seed
```

```bash
npm run build
```

Les phrases et les leviers de chaque région viennent de la même fonction que les fiches PDF (`scripts/fiches_regionales.py`, fonction `contenu`) : la fiche et le tableau de bord ne peuvent pas se contredire.

## Contrôles

| Commande | Ce qu'elle garantit |
| --- | --- |
| `npm run verif:aller-retour` | Les 1 425 valeurs relues dans la base sont celles du fichier exporté. Vu en échec quand une valeur est modifiée en base. |
| `npm run verif:hors-ligne` | Serveur arrêté : les 5 pages s'ouvrent (dont une jamais visitée), le disent, la fiche PDF se télécharge, une saisie est gardée. Au retour du serveur, elle arrive dans la base, une seule fois. Vu en échec avec le service worker bloqué. |

`verif:hors-ligne` demande Playwright (`npm i -D playwright`) et une base de test dans `DATABASE_URL`.

## Avant un usage réel

**Il faut protéger la route d'écriture** (`/api/saisies`). Aujourd'hui, toute personne qui connaît l'adresse peut écrire : il faut un code d'accès par direction régionale, et une limite de débit.
