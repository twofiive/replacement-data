import requests
from bs4 import BeautifulSoup
import re
from api.localisation import get_ville_info

# Regex pour extraire un numéro de téléphone français
TEL_REGEX = re.compile(r"(0[1-9](?:[\s.-]?\d{2}){4})", re.MULTILINE)


def extract_telephone(text: str) -> str:
    if not text:
        return ""
    m = TEL_REGEX.search(text)
    return m.group(1) if m else ""


def get_remplacement_links():
    url = "https://osteofrance.com/petites-annonces/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")
    liens = set()
    for a in soup.select("table.annonces td.title a[href^='/petite-annonce/']"):
        href = a.get("href")
        if href:
            liens.add("https://osteofrance.com" + href)

    return list(liens)


def scrape_osteopathes_de_france():
    liens = get_remplacement_links()
    annonces = []

    for lien in liens:
        try:
            r = requests.get(lien, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            titre_tag = soup.select_one("h1.title")
            titre = titre_tag.get_text(strip=True) if titre_tag else ""

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

            # Description (sans le bloc p.meta)
            entry = soup.select_one("div.entry-body")
            if entry:
                for meta_p in entry.select("p.meta"):
                    meta_p.decompose()
                description = entry.get_text(separator="\n", strip=True)
            else:
                description = ""

            date_publication = ""
            time_tag = soup.select_one("time.updated")
            if time_tag and time_tag.has_attr("datetime"):
                date_publication = time_tag["datetime"].strip()
            elif time_tag:
                date_publication = time_tag.get_text(strip=True)

            ville_tag = soup.select_one("div.address span.uc")
            ville = ville_tag.get_text(strip=True) if ville_tag else "N/A"
            ville = ville.title() if ville and ville != "N/A" else ville

            contact_tag = soup.select_one("div.name strong")
            contact = contact_tag.get_text(" ", strip=True) if contact_tag else ""

            vcard = soup.select_one("div.vcard")
            telephone = (
                extract_telephone(vcard.get_text(" ", strip=True)) if vcard else ""
            )
            if not telephone:
                telephone = extract_telephone(description)

            departement, region, _ = get_ville_info(ville)
            departement = departement or "N/A"
            region = region or "N/A"

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
                    "source": "osteofrance.com",
                }
            )

        except Exception as e:
            print(f"Erreur sur {lien} : {e}")
            continue

    return annonces