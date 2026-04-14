## Projet d’agrégation de données – Ostéopathie

**Équipe :** Hugo, Robin et Ryan

---

### Présentation

Ce projet a pour but de regrouper sur un même fichier toutes les **annonces de remplacement d’ostéopathes** publiées sur différents sites français.
On a utilisé du **web scraping** pour récupérer les données, et une **API de géolocalisation** pour fiabiliser automatiquement les informations sur les villes, départements et régions.

---

### Fonctionnement

Le script principal lance plusieurs scrapers qui collectent les annonces, fusionne les résultats, nettoie les données, puis les exporte dans un fichier CSV unique.
Les données sont ensuite prêtes à être importées dans une base **PostgreSQL** via Docker.

---

### Arborescence du projet

```
Projet final
├── api/                  → appels API pour la localisation
├── scrapers/             → scripts de scraping
├── storage/              → gestion du CSV
├── output/               → résultats (annonces.csv)
├── bdd_requetes/         → scripts SQL
├── main.py               → script principal
└── docker-compose.yml    → base PostgreSQL
```

---

### Utilisation

1. Lancer la collecte
   ```bash
   python main.py
   ```
2. Les résultats sont disponibles dans `output/annonces.csv`.

---
