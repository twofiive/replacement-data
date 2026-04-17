import unicodedata
import pandas as pd
import requests
import os
import re

# Source : data.gouv.fr - Fichier des communes INSEE
# Permet d'enrichir les annonces avec données géographiques officielles
COMMUNES_URL = (
    "https://www.data.gouv.fr/fr/datasets/r/"
    "dbe8a621-a9c4-4bc3-9cae-be1699c5ff25"
)


def download_opendata(output_path="output/communes_insee.csv"):
    """
    Télécharge le fichier OpenData des communes françaises depuis data.gouv.fr
    Contient : code INSEE, nom commune, département, région, coordonnées GPS
    Source officielle : INSEE / data.gouv.fr
    """
    print("Téléchargement des données OpenData communes INSEE...")
    try:
        response = requests.get(COMMUNES_URL, timeout=60)
        response.raise_for_status()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"Fichier téléchargé : {output_path}")
        return output_path
    except Exception as e:
        print(f"Erreur lors du téléchargement : {e}")
        return None


def load_opendata(csv_path="output/communes_insee.csv"):
    """
    Charge le fichier INSEE et retourne un DataFrame normalisé.
    Colonnes conservées : nom_commune, nom_departement, nom_region,
    latitude, longitude, code_postal
    """
    try:
        df = pd.read_csv(csv_path, sep=",", encoding="utf-8", dtype=str)
        
        # Colonnes utiles uniquement
        colonnes = [
            "nom_commune",
            "code_postal", 
            "nom_departement",
            "nom_region",
            "latitude",
            "longitude"
        ]
        df = df[colonnes].copy()
        
        # Normalisation
        df["nom_commune"] = df["nom_commune"].str.strip().str.title()
        df["nom_region"] = df["nom_region"].str.strip()
        df["nom_departement"] = df["nom_departement"].str.strip()
        
        # Suppression des doublons sur nom_commune
        df = df.drop_duplicates(subset=["nom_commune"])
        
        print(f"OpenData INSEE chargé : {len(df)} communes")
        return df
    
    except Exception as e:
        print(f"Erreur chargement OpenData : {e}")
        return None


def normaliser_ville(nom: str) -> str:
    """
    Normalise un nom de ville pour le matching :
    - Minuscules
    - Suppression des accents
    - Suppression des tirets, apostrophes, espaces multiples
    - Suppression des suffixes parasites (Sud, Nord, Est, Ouest, 19e...)
    """
    if not nom:
        return ""
    
    nom = nom.lower().strip()
    
    # Suppression des accents
    nom = unicodedata.normalize("NFD", nom)
    nom = nom.encode("ascii", "ignore").decode("utf-8")
    
    # Suppression des suffixes parasites
    suffixes = [
        r"\s*(sud|nord|est|ouest|centre)$",
        r"\s*\d+e?$",           # 19e, 13, etc.
        r"\s*/.*$",             # /Paris 19e
        r"[-']",                # tirets et apostrophes
    ]
    for pattern in suffixes:
        nom = re.sub(pattern, " ", nom)
    
    # Nettoyage des espaces multiples
    nom = re.sub(r"\s+", " ", nom).strip()
    
    return nom


def enrichir_annonces(annonces: list, csv_path="output/communes_insee.csv"):
    """
    Enrichit les annonces avec les données géographiques officielles INSEE.
    Utilise un matching normalisé pour gérer les variations de noms de villes.
    """
    df_insee = load_opendata(csv_path)
    if df_insee is None:
        print("Impossible d'enrichir : OpenData non disponible")
        return annonces

    # Construction d'un index normalisé
    index_normalise = {}
    for _, row in df_insee.iterrows():
        cle = normaliser_ville(str(row["nom_commune"]))
        if cle not in index_normalise:
            index_normalise[cle] = {
                "latitude": row.get("latitude", ""),
                "longitude": row.get("longitude", ""),
                "code_postal": row.get("code_postal", ""),
                "nom_departement": row.get("nom_departement", ""),
            }

    enriched = 0
    non_trouve = []

    for annonce in annonces:
        ville_raw = str(annonce.get("ville", "")).strip()
        ville_norm = normaliser_ville(ville_raw)

        if ville_norm in index_normalise:
            info = index_normalise[ville_norm]
            annonce["latitude"] = info["latitude"]
            annonce["longitude"] = info["longitude"]
            annonce["code_postal"] = info["code_postal"]
            annonce["nom_departement"] = info["nom_departement"]
            enriched += 1
        else:
            annonce["latitude"] = ""
            annonce["longitude"] = ""
            annonce["code_postal"] = ""
            annonce["nom_departement"] = ""
            non_trouve.append(ville_raw)

    print(f"Annonces enrichies : {enriched}/{len(annonces)}")
    if non_trouve:
        print(f"Villes non trouvées ({len(non_trouve)}) : {non_trouve[:5]}...")

    return annonces