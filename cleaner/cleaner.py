import pandas as pd, numpy as np, re
from datetime import datetime
import os

# Nettoyage des données
def cleaner_function(
    path_in="output/annonces.csv", path_out="output/annonces_clean.csv"
):
    df = pd.read_csv(path_in, encoding="utf-8", encoding_errors="replace")

    # Remplacement des NaN selon le type de colonne
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            df[col] = df[col].fillna(0)
        else:
            df[col] = df[col].fillna("")
            
    df.drop_duplicates(subset=["lien_annonce"], keep="first", inplace=True)

    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].astype(str).str.strip()

    if "ville" in df:
        df["ville"] = df["ville"].str.title()

    if "region" in df:
        df["region"] = df["region"].str.title()

    if "type_offre" in df:
        df["type_offre"] = (
            df["type_offre"]
            .str.lower()
            .replace(
                {
                    "remplacement": "Remplacement",
                    "collaboration": "Collaboration",
                    "cession": "Cession",
                }
            )
        )

    if "telephone" in df:

        def clean_phone(x):
            x = re.sub(r"\D", "", str(x))
            if x.startswith("0"):
                x = "+33" + x[1:]
            elif x.startswith("33"):
                x = "+" + x
            return x

        df["telephone"] = df["telephone"].apply(clean_phone)

    if "date_publication" in df:

        def norm_date(x):
            try:
                return pd.to_datetime(x, errors="coerce").strftime("%Y-%m-%d")
            except:
                return ""

        df["date_publication"] = df["date_publication"].apply(norm_date).fillna("")

    df["titre"] = df["titre"].str.replace(r"Ã©", "é", regex=True)
    df["titre"] = df["titre"].str.replace(r"Ã", "à", regex=True)
    df["description"] = df["description"].str.replace(r"Ã©", "é", regex=True)
    df["description"] = df["description"].str.replace(r"Ã", "à", regex=True)

    df.replace("nan", "", inplace=True)

    os.makedirs(os.path.dirname(path_out), exist_ok=True)
    df.to_csv(path_out, index=False, encoding="utf-8")

    print(f"Fichier nettoyé exporté : {path_out}")
