import requests
from bs4 import BeautifulSoup
from api.localisation import get_ville_info
import re


# Récupération des liens des annonces
def get_remplacement_links():
    url = "https://www.osteoweb.fr/remplacement/"
    r = requests.get(url)
    r.encoding = 'utf-8'  # Forcer l'encodage UTF-8
    soup = BeautifulSoup(r.text, "html.parser")
    liens = set()
    for a in soup.select('a[href^="https://www.osteoweb.fr/"]'):
        href = a.get("href")
        if href and "remplacement" in href and href.endswith(".htm"):
            liens.add(href)
    return list(liens)


# Extraction des informations d'une annonce de remplacement
def get_info_remplacement():
    liens = get_remplacement_links()
    data = []
    for lien in liens:
        r = requests.get(lien)
        r.encoding = 'utf-8'  # Forcer l'encodage UTF-8
        soup = BeautifulSoup(r.text, "html.parser")

        type_offre = ""
        m = re.search(
            r"/(remplacement|collaboration|association|cession|recherche-de-locaux|offre-de-locaux|achat-de-materiel|vente-de-materiel|benevolat|divers)",
            lien,
            re.I,
        )
        if m:
            # Ajuster le type d'offre selon l'URL
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

        titre = soup.find("title").get_text(strip=True)
        description = soup.find("meta", {"name": "description"})["content"]

        ville_tag = soup.find("b", string=lambda s: s and "Ville" in s)
        ville = ville_tag.next_sibling.strip() if ville_tag else "N/A"

        departement, region, _ = get_ville_info(ville)
        departement = departement or "N/A"
        region = region or "N/A"

        date_tag = soup.select_one("p.meta time")
        if date_tag and date_tag.get("datetime"):
            date_publication = date_tag["datetime"]
        else:
            date_publication = ""

        contact_tag = soup.find("b", string=lambda s: s and "Contact" in s)
        contact = contact_tag.next_sibling.strip() if contact_tag else "N/A"

        tel_tag = soup.find("font", {"color": "#990000"})
        telephone = tel_tag.get_text(strip=True) if tel_tag else "N/A"
        # Ajouter l'annonce au dataset
        data.append(
            {
                "titre": titre,
                "type_offre": "",
                "description": description,
                "ville": ville,
                "departement": departement,
                "region": region,
                "contact": contact,
                "telephone": telephone,
                "lien_annonce": lien,
                "date_publication": date_publication,
                "source": "osteoweb.fr",
            }
        )
    return data