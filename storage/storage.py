import csv
from unidecode import unidecode


# Fonction pour uniformiser les données dans un fichier CSV
def save_to_csv(data, filename="output/annonces.csv"):
    if not data:
        print("Aucune donnée à enregistrer.")
        return

    # Clés de base dans l'ordre souhaité
    keys_base = [
        "id",
        "source",
        "titre",
        "ville",
        "region",
        "type_offre",
        "telephone",
        "date_publication",
        "contact",
        "description",
        "lien_annonce",
    ]

    # Nouvelles colonnes OpenData INSEE
    keys_opendata = [
        "latitude",
        "longitude",
        "code_postal",
        "nom_departement",
    ]

    # Colonnes finales : base + opendata
    keys = keys_base + keys_opendata

    # Suppression des accents sur les colonnes texte uniquement
    # Les colonnes numériques (latitude, longitude) sont préservées
    cleaned_data = []
    for d in data:
        row = {}
        for k in keys:
            val = d.get(k, "")
            if k in ("latitude", "longitude"):
                # Conserver la valeur numérique telle quelle
                row[k] = str(val) if val != "" else ""
            else:
                row[k] = unidecode(str(val)) if val != "" else ""
        cleaned_data.append(row)

    # Écriture dans le fichier CSV
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(cleaned_data)

    print(f"Fichier sauvegardé : {filename} ({len(cleaned_data)} lignes)")