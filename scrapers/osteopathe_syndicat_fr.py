import requests
from bs4 import BeautifulSoup
import re
from api.localisation import get_ville_info
from datetime import datetime


# Rècyupération des liens des annonces


def get_remplacement_links():
    url = "https://www.osteopathe-syndicat.fr/annonces-osteopathe"
    r = requests.get(url, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    liens = set()
    for a in soup.select("ul.listingAnnonce li h2 a[href]"):
        href = a.get("href")
        if not href or href.startswith("javascript:"):
            continue
        if "annonces-osteopathe" in href:
            continue
        full = (
            href
            if href.startswith("http")
            else "https://www.osteopathe-syndicat.fr" + href
        )
        liens.add(full)

    return list(liens)


def scrape_osteopathe_syndicat():
    liens = get_remplacement_links()
    annonces = []

    for lien in liens:
        try:
            r = requests.get(lien)
            soup = BeautifulSoup(r.text, "html.parser")

            # Titre
            titre_tag = soup.select_one("div.detailAnnonce h1") or soup.select_one("h1")
            titre = titre_tag.get_text(strip=True) if titre_tag else ""

            # Type d'offre
            type_offre = ""
            m = re.search(
                r"/(remplacement|collaboration|association|cession|recherche-de-locaux|offre-de-locaux|achat-de-materiel|vente-de-materiel|benevolat|divers)",
                lien,
                re.I,
            )
            if m:
                mapping = {
                    "remplacement": "Remplacement",
                    "collaboration": "Collaboration",
                    "association": "Association",
                    "cession": "Cession de patientèle",
                    "recherche-de-locaux": "Recherche de locaux",
                    "offre-de-locaux": "Offre de locaux",
                    "achat-de-materiel": "Achat de matériel",
                    "vente-de-materiel": "Vente de matériel",
                    "benevolat": "Bénévolat",
                    "divers": "Divers",
                }
                type_offre = mapping.get(m.group(1).lower(), m.group(1).capitalize())
            if not type_offre and titre:
                for kw, val in [
                    ("remplacement", "Remplacement"),
                    ("collaboration", "Collaboration"),
                    ("cession", "Cession de patientèle"),
                    ("locaux", "Offre de locaux"),
                ]:
                    if kw in titre.lower():
                        type_offre = val
                        break

            # Description
            description_bloc = soup.select_one(
                "div.content.wysiwyg"
            ) or soup.select_one("div.content")
            description = (
                description_bloc.get_text(separator="\n", strip=True)
                if description_bloc
                else ""
            )

            # Date
            date_tag = soup.select_one(".pa-zoneTexte .date") or soup.select_one(
                "div.detailAnnonce .date"
            )
            if date_tag:
                try:
                    date_publication = (
                        datetime.strptime(date_tag.get_text(strip=True), "%d/%m/%Y")
                        .date()
                        .isoformat()
                    )
                except Exception:
                    date_publication = date_tag.get_text(strip=True)
            else:
                date_publication = ""

            # Ville
            ville = "N/A"
            txt_for_city = f"{titre}\n{description}"
            m = re.search(
                r"\b(?:à|sur|proche|secteur|près de)\s+([A-ZÉÈÎÏÀÂÄÔÖÛÜÇ][A-Za-zÀ-ÖØ-öø-ÿ'’ \-]{2,})",
                txt_for_city,
            )
            if m:
                ville = m.group(1).strip(" .,:;’'-")

            # Contact
            contact = ""
            bloc_contact = soup.select_one("div.pa-blocContact")
            if bloc_contact:
                txt_contact = bloc_contact.get_text(" ", strip=True)
                m = re.search(r"Auteur\s*:\s*([^\n\r]+)", txt_contact, re.I)
                if m:
                    contact = m.group(1).strip()

            # Téléphone
            telephone_tag = soup.select_one("div.pa-blocContact .numTel")
            telephone = ""
            if telephone_tag:
                telephone = extract_telephone(telephone_tag.get_text(" ", strip=True))
            if not telephone:
                telephone = extract_telephone(soup.get_text(" ", strip=True))

            # Région affichée
            region_contact_tag = soup.select_one("div.pa-blocContact .region")
            region_contact = (
                region_contact_tag.get_text(strip=True) if region_contact_tag else ""
            )

            # Département / région via API à partir de la ville
            departement, region, _ = (
                get_ville_info(ville)
                if ville and ville != "N/A"
                else (None, None, None)
            )
            departement = departement or "N/A"
            region = region_contact or region or "N/A"

            annonces.append(
                {
                    "titre": titre,
                    "type_offre": type_offre,
                    "description": description,
                    "ville": ville,
                    "departement": departement,
                    "region": region,
                    "contact": contact,
                    "telephone": telephone,
                    "lien_annonce": lien,
                    "date_publication": date_publication,
                    "source": "osteopathe-syndicat.fr",
                }
            )

        except Exception as e:
            print(f"Erreur sur {lien} : {e}")
            continue

    # IDs
    for i, annonce in enumerate(annonces, start=1):
        annonce["id"] = i

    return annonces


def extract_telephone(text):
    match = re.search(r"(0[1-9](?:[\s.-]?\d{2}){4})", text)
    return match.group(1) if match else ""