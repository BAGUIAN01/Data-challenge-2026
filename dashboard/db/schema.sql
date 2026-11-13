-- Schema of the dashboard database (Neon / PostgreSQL). Idempotent: safe to run again.
-- One published data set at a time (table jeu_donnees, one row marked actif); region-level
-- tables hold the rows of that version. Field entries (saisie_ecoles) are kept across versions.

CREATE TABLE IF NOT EXISTS jeu_donnees (
  version     text PRIMARY KEY,
  genere_le   date NOT NULL,
  charge_le   timestamptz NOT NULL DEFAULT now(),
  actif       boolean NOT NULL DEFAULT false,
  parametres  jsonb NOT NULL          -- years, national series, thresholds, nowcast slope, validation, map
);
-- At most one active version.
CREATE UNIQUE INDEX IF NOT EXISTS jeu_donnees_un_actif ON jeu_donnees (actif) WHERE actif;

CREATE TABLE IF NOT EXISTS region (
  version           text NOT NULL REFERENCES jeu_donnees(version) ON DELETE CASCADE,
  cle               text NOT NULL,     -- former region key, e.g. CENTRENORD
  nom               text NOT NULL,     -- 2025 name, e.g. Koulsé
  ancienne          text NOT NULL,
  codes             text NOT NULL,
  type              text NOT NULL,     -- renommage, scission en 2, scission en 3
  profil            text NOT NULL,
  priorite          smallint NOT NULL CHECK (priorite BETWEEN 1 AND 3),
  enfants_hors_cm2  integer NOT NULL,
  prevision_2025_26 jsonb NOT NULL,    -- {centrale, basse, haute}
  PRIMARY KEY (version, cle)
);

-- One value per region, indicator and school year (long format, easy to query).
CREATE TABLE IF NOT EXISTS indicateur (
  version     text NOT NULL,
  cle         text NOT NULL,
  indicateur  text NOT NULL,           -- tap, tap_f, tap_g, eleves, ecoles, incidents
  annee       text NOT NULL,           -- 15/16 ... 24/25 (25/26 for incidents)
  rang        smallint NOT NULL,       -- position in the series
  valeur      double precision,
  PRIMARY KEY (version, cle, indicateur, annee),
  FOREIGN KEY (version, cle) REFERENCES region(version, cle) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerte (
  version      text NOT NULL,
  cle          text NOT NULL,
  periode      text NOT NULL,          -- janv_2025_26, sept_2026_27, ref_2026_27
  probabilite  smallint NOT NULL,      -- % of a drop of more than 5 % in pupils
  PRIMARY KEY (version, cle, periode),
  FOREIGN KEY (version, cle) REFERENCES region(version, cle) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS facteur (
  version  text NOT NULL,
  cle      text NOT NULL,
  facteur  text NOT NULL,
  valeur   double precision,
  niveau   smallint NOT NULL CHECK (niveau BETWEEN 1 AND 3),  -- 1 = among the 4 most exposed
  PRIMARY KEY (version, cle, facteur),
  FOREIGN KEY (version, cle) REFERENCES region(version, cle) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS texte (
  version  text NOT NULL,
  cle      text NOT NULL,
  genre    text NOT NULL CHECK (genre IN ('fait', 'levier', 'levier_facteur')),
  rang     smallint NOT NULL,
  contenu  text NOT NULL,
  PRIMARY KEY (version, cle, genre, rang),
  FOREIGN KEY (version, cle) REFERENCES region(version, cle) ON DELETE CASCADE
);

-- Field entries: number of schools open at the start of the year, typed on a device, possibly
-- offline. client_id is the idempotency key: the same entry sent twice is stored once.
CREATE TABLE IF NOT EXISTS saisie_ecoles (
  client_id        uuid PRIMARY KEY,
  cle              text NOT NULL,
  annee            text NOT NULL,      -- school year of the count, e.g. 2026-2027
  ecoles_ouvertes  integer NOT NULL CHECK (ecoles_ouvertes >= 0),
  saisi_le         timestamptz NOT NULL,
  recu_le          timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS saisie_ecoles_par_region ON saisie_ecoles (cle, annee, saisi_le DESC);
