-- Table temporaire (staging)
DROP TABLE IF EXISTS staging_annonces;
CREATE TABLE staging_annonces (
    id INT,
    source TEXT,
    titre TEXT,
    ville TEXT,
    region TEXT,
    type_offre TEXT,
    telephone TEXT,
    date_publication TEXT,
    contact TEXT,
    description TEXT,
    lien_annonce TEXT,
    -- Nouvelles colonnes OpenData INSEE
    latitude TEXT,
    longitude TEXT,
    code_postal TEXT,
    nom_departement TEXT
);

-- Import du CSV nettoyé
COPY staging_annonces 
FROM '/mnt/output/annonces_clean.csv' 
DELIMITER ',' 
CSV HEADER;

-- Table principale (base propre)
DROP TABLE IF EXISTS annonces;
CREATE TABLE annonces (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100),
    titre TEXT,
    ville VARCHAR(100),
    region VARCHAR(100),
    type_offre VARCHAR(100),
    telephone VARCHAR(20),
    date_publication DATE,
    contact VARCHAR(100),
    description TEXT,
    lien_annonce TEXT UNIQUE,
    -- Nouvelles colonnes OpenData INSEE
    latitude NUMERIC(10, 7),
    longitude NUMERIC(10, 7),
    code_postal VARCHAR(10),
    nom_departement VARCHAR(100)
);

-- Transfert depuis staging
INSERT INTO annonces (
    source, titre, ville, region, type_offre, telephone,
    date_publication, contact, description, lien_annonce,
    latitude, longitude, code_postal, nom_departement
)
SELECT
    NULLIF(source, ''),
    NULLIF(titre, ''),
    NULLIF(ville, ''),
    NULLIF(region, ''),
    NULLIF(type_offre, ''),
    NULLIF(telephone, ''),
    CASE 
        WHEN date_publication ~ '^\d{4}-\d{2}-\d{2}$' 
        THEN date_publication::date
        ELSE NULL
    END,
    NULLIF(contact, ''),
    NULLIF(description, ''),
    NULLIF(lien_annonce, ''),
    CASE 
        WHEN latitude ~ '^-?\d+\.?\d*$' 
        THEN latitude::NUMERIC(10,7)
        ELSE NULL
    END,
    CASE 
        WHEN longitude ~ '^-?\d+\.?\d*$' 
        THEN longitude::NUMERIC(10,7)
        ELSE NULL
    END,
    NULLIF(code_postal, ''),
    NULLIF(nom_departement, '')
FROM staging_annonces
WHERE lien_annonce IS NOT NULL;

-- Vue existante : annonces par région
CREATE OR REPLACE VIEW v_annonces_par_region AS
SELECT region, COUNT(*) AS total
FROM annonces
WHERE region IS NOT NULL
GROUP BY region
ORDER BY total DESC;

-- Vue existante : annonces par type d'offre
CREATE OR REPLACE VIEW v_annonces_par_type AS
SELECT type_offre, COUNT(*) AS total
FROM annonces
WHERE type_offre IS NOT NULL
GROUP BY type_offre
ORDER BY total DESC;

-- Vue existante : annonces récentes
CREATE OR REPLACE VIEW v_annonces_recent AS
SELECT titre, ville, region, type_offre, date_publication
FROM annonces
WHERE date_publication >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date_publication DESC;

-- Nouvelle vue : annonces avec coordonnées GPS (pour cartographie)
CREATE OR REPLACE VIEW v_annonces_geolocalisees AS
SELECT 
    titre, ville, region, nom_departement,
    type_offre, latitude, longitude, code_postal
FROM annonces
WHERE latitude IS NOT NULL 
  AND longitude IS NOT NULL
ORDER BY region;

-- Nouvelle vue : densité d'annonces par département
CREATE OR REPLACE VIEW v_densite_par_departement AS
SELECT 
    nom_departement,
    COUNT(*) AS nb_annonces,
    STRING_AGG(DISTINCT type_offre, ', ') AS types_offres
FROM annonces
WHERE nom_departement IS NOT NULL
GROUP BY nom_departement
ORDER BY nb_annonces DESC;