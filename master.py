import os
import pandas as pd
from scrapers.osteoweb_fr import get_info_remplacement
from scrapers.osteopathe_syndicat_fr import scrape_osteopathe_syndicat
from scrapers.osteofrance_com import scrape_osteopathes_de_france
from storage.storage import save_to_csv
from cleaner.cleaner import cleaner_function
from opendata.insee_import import download_opendata, load_opendata, enrichir_annonces

# Chemins relatifs au projet
OUTPUT_RAW = "output/announces.csv"
OUTPUT_CLEAN = "output/annonces_clean.csv"
OUTPUT_INSEE = "output/communes_insee.csv"

if __name__ == "__main__":
    print("=== Lancement des scrapers ===\n")
    data = []

    # --- SCRAPING ---
    try:
        print("[1/3] Scraping osteoweb.fr ...")
        data += get_info_remplacement()
        print(f"Terminé : osteoweb.fr ({len(data)} annonces)")
    except Exception as e:
        print(f"Erreur sur osteoweb.fr : {e}")

    try:
        print("[2/3] Scraping osteopathe-syndicat.fr ...")
        data += scrape_osteopathe_syndicat()
        print(f"Terminé : osteopathe-syndicat.fr ({len(data)} annonces)")
    except Exception as e:
        print(f"Erreur sur osteopathe-syndicat.fr : {e}")

    try:
        print("[3/3] Scraping osteofrance.com ...")
        data += scrape_osteopathes_de_france()
        print(f"Terminé : osteofrance.com ({len(data)} annonces)")
    except Exception as e:
        print(f"Erreur sur osteofrance.com : {e}")

    print(f"\nTotal d'annonces collectées : {len(data)}")

    if not data:
        print("Aucune annonce collectée, arrêt.")
    else:
        # Ajout des IDs
        for i, item in enumerate(data, start=1):
            item["id"] = i

        # --- SOURCE OPENDATA INSEE ---
        print("\n=== Intégration OpenData INSEE ===")
        try:
            # Téléchargement si le fichier n'existe pas déjà
            if not os.path.exists(OUTPUT_INSEE):
                download_opendata(OUTPUT_INSEE)
            
            # Enrichissement des annonces avec coordonnées GPS officielles
            data = enrichir_annonces(data, OUTPUT_INSEE)
            print("Enrichissement INSEE terminé")
        except Exception as e:
            print(f"Erreur OpenData INSEE : {e}")

        # --- SAUVEGARDE ---
        os.makedirs("output", exist_ok=True)
        save_to_csv(data, OUTPUT_RAW)
        print(f"\nExport brut terminé : {OUTPUT_RAW}")

        df = pd.read_csv(OUTPUT_RAW)
        print("\nAperçu du fichier généré :")
        print(df.head(3))

        # --- NETTOYAGE ---
        print("\nNettoyage et uniformisation des données...")
        cleaner_function(OUTPUT_RAW, OUTPUT_CLEAN)
        print(f"Nettoyage terminé : {OUTPUT_CLEAN}")