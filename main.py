import pandas as pd

from scrapers.osteoweb_fr import get_info_remplacement
from scrapers.osteopathe_syndicat_fr import scrape_osteopathe_syndicat
from scrapers.osteofrance_com import scrape_osteopathes_de_france
from storage.storage import save_to_csv
from cleaner.cleaner import cleaner_function


# Point d'entrée principal du script


if __name__ == "__main__":
    print("=== Lancement des scrapers ===\n")

    data = []

    # Scraping des différentes sources
    try:
        print("[1/3] Scraping osteoweb.fr ...")
        data += get_info_remplacement()
        print("Terminé : osteoweb.fr")
    except Exception as e:
        print(f"Erreur sur osteoweb.fr : {e}")

    try:
        print("[2/3] Scraping osteopathe-syndicat.fr ...")
        data += scrape_osteopathe_syndicat()
        print("Terminé : osteopathe-syndicat.fr")
    except Exception as e:
        print(f"Erreur sur osteopathe-syndicat.fr : {e}")

    try:
        print("[3/3] Scraping osteofrance.com ...")
        data += scrape_osteopathes_de_france()
        print("Terminé : osteofrance.com")
    except Exception as e:
        print(f"Erreur sur osteofrance.com : {e}")

    print(f"\nTotal d'annonces collectées : {len(data)}")

    if not data:
        print("Aucune annonce collectée, arrêt.")
    else:
        for i, item in enumerate(data, start=1):
            item["id"] = i

        # Sauvegarde des données brutes dans un fichier CSV
        output_path = r"output/annonces_brutes.csv"
        save_to_csv(data, output_path)

        print(f"\nExport terminé : {output_path}")
        df = pd.read_csv(output_path)
        print("\nAperçu du fichier généré :")
        print(df.head())

        # Nettoyage et uniformisation des données

        print("\nNettoyage et uniformisation des données...")
        cleaner_function(output_path, "output/annonces_clean.csv")
        print("Nettoyage terminé. Fichier propre généré : output/annonces_clean.csv")
