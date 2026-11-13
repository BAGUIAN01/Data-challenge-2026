# Tableau de bord local-first

En ligne : <https://kalantigui-decrochage.vercel.app>

Application Next.js du Défi 1. Elle répond à trois questions, région par région :
- **où agir en premier** : carte et matrice de priorité ;
- **où le risque monte** : calendrier d'alerte ;
- **combien d'élèves** : estimation des effectifs à partir des écoles ouvertes à la rentrée.

Elle s'utilise **sans réseau** et garde ses données dans une base **Neon** (PostgreSQL) pour la version en ligne.

Elle ne parle que des **13 régions** : les données du concours ne descendent ni aux provinces ni aux écoles.

## Une application de téléphone

Une seule page (`app/page.js`), gardée par le service worker, dans laquelle on navigue comme dans une application installée. La maquette d'origine est dans `../maquettes/application-mobile/`.

| Onglet | Ce qu'on y trouve |
| --- | --- |
| **Carte** | Les 13 régions colorées par leur score global (moitié risque de chute, moitié part d'enfants qui n'achèvent pas), une barre par région pour le score, en pourcentage, et le nom des régions. Le petit lecteur en haut à droite fait défiler les années de 2020/21 à la prévision 2026/27, sans à-coups (couleurs et barres changent) ; on peut glisser le doigt sur sa piste ou toucher une année. Toucher une région ouvre directement sa page. La feuille du bas montre le pays : les régions où agir maintenant (priorité 1, score, sur quoi agir), ce qui change entre 2025/26 et la prévision 2026/27, trois chiffres du pays, et le facteur dominant de chaque région. Sur la page d'une région, le score s'anime année par année jusqu'à la prévision 2026/27 (« Rejouer les années »). |
| **Régions** | La matrice de priorité et la liste des régions, avec des filtres. Chaque région ouvre sa fiche, dans cet ordre : le score global, le facteur dominant avec l'action à mener, puis les détails (prévision, achèvement, violence, facteurs, constats, leviers, fiche PDF). |
| **Alertes** | Le calendrier d'alerte, les saisies d'écoles ouvertes, l'alerte de septembre. |
| **Plus** | État de la synchronisation, apparence (clair, sombre), installation, méthode et sources. |

Ce qui la rend proche d'une application installée :
- **gestes** : la carte se pince et se déplace au doigt. La feuille du bas se tire au doigt. Un écran se ferme en glissant depuis le bord gauche ;
- **navigation** : le bouton retour du téléphone ferme l'écran ouvert, et chaque onglet garde ses écrans ;
- **adresse d'une région** : chaque région a la sienne (`/#region/NORD`), qui la rouvre même sans réseau ;
- **installation** : elle s'installe sur l'écran d'accueil, avec ses icônes et son manifeste.

Sur un grand écran, la carte reste à droite et les onglets passent dans un panneau à gauche.

**Le seul geste d'écriture, c'est la saisie des écoles ouvertes à la rentrée.** Les élèves attendus se calculent pendant la frappe. La saisie s'affiche aussitôt. « Annuler » reste proposé 6 secondes, et la saisie ne part pas avant.

## Comment elle fonctionne sans réseau

| Besoin | Ce qui le permet |
| --- | --- |
| **Lire** | Les données sont lues d'abord dans la base de l'appareil (IndexedDB, via Dexie). Elles sont mises à jour depuis Neon quand le serveur répond. Si l'appareil n'a encore rien, il utilise le jeu de données publié avec l'application. |
| **Écrire** | Une saisie (écoles ouvertes à la rentrée) est enregistrée tout de suite sur l'appareil et s'affiche aussitôt. Elle part vers Neon au retour du réseau, avec une clé (`client_id`) qui empêche tout doublon. |
| **Ouvrir** | Le service worker (Serwist) garde sur l'appareil toutes les pages, les 13 fiches régionales, les scripts, les données et les fiches PDF. Aucune page ne lit le serveur au moment où elle s'affiche. |
| **Dire** | Un bandeau en haut indique quand on est hors ligne (« Hors ligne · données de ce téléphone, reçues le… ») et combien de saisies attendent le réseau. Le sous-titre de la carte dit toujours de quelle version des données il s'agit. |
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

## Mettre en ligne (Vercel et Neon)

Le projet Vercel déploie à chaque `git push` sur `main`, avec `dashboard` comme dossier racine (Root Directory) et la base Neon déclarée dans ses variables d'environnement.

**Les données vont dans la base à chaque déploiement.** La commande de construction (`vercel-build`) lance `db/preparer.mjs` avant `next build`. Ce script :
- applique le schéma ;
- charge la version publiée des données et la rend active ;
- garde les saisies.

L'application lit ensuite ses données dans la base (`/api/donnees`), puis les garde sur l'appareil.

- **La variable** peut s'appeler `DATABASE_URL` ou `POSTGRES_URL` (le nom que pose l'intégration Neon de Vercel). Les noms sans *pooler* sont aussi acceptés.
- **Le paramètre `channel_binding=require`** des adresses Neon est retiré avant la connexion : le client PostgreSQL l'enverrait au serveur, qui le refuse.
- **Si la base ne peut pas être remplie, la construction s'arrête**, avec la raison dans le journal. Le déploiement précédent reste en ligne.

Sans base déclarée, le déploiement fonctionne aussi : l'application utilise les données publiées avec elle, et les saisies restent sur les téléphones (« base en ligne non configurée »).

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
| `npm run verif:hors-ligne` | Sur un écran d'iPhone, serveur arrêté, les points suivants sont vérifiés. Vu en échec avec le service worker bloqué. <ul><li>l'application s'ouvre sur une région par son adresse et dit qu'elle est hors ligne ;</li><li>le retour, un lien vers une autre région et les quatre onglets fonctionnent ;</li><li>la fiche PDF est servie ;</li><li>une saisie est gardée et comptée ;</li><li>au retour du serveur, la saisie arrive dans la base, une seule fois.</li></ul> |
| `npm run verif:ecran` | Sur un téléphone de 360 px, au toucher, les points suivants sont vérifiés. Vu en échec, point par point, avec `VERIF_SABOTAGE=1`. <ul><li>rien ne dépasse de l'écran, sur les quatre onglets ;</li><li>les noms de la carte ne se chevauchent pas ;</li><li>le retour du téléphone ferme une région sans quitter l'application ;</li><li>un glissement depuis le bord ferme l'écran ;</li><li>la feuille du bas se pose à une hauteur de repos ;</li><li>aucune erreur dans la console.</li></ul> |

Les deux contrôles demandent Playwright (`npm i -D playwright`). `verif:hors-ligne` demande aussi une base de test dans `DATABASE_URL`, ce que `verif:ecran` ne demande pas.

## Avant un usage réel

**Il faut protéger la route d'écriture** (`/api/saisies`). Aujourd'hui, toute personne qui connaît l'adresse peut écrire : il faut un code d'accès par direction régionale, et une limite de débit.
