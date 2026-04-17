import os

# Configuration de la base de données PostgreSQL
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "osteopathes"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
}

# Clé API pour l'authentification
# En production, utiliser une variable d'environnement
API_KEY = os.getenv("API_KEY", "dev-secret-key-123")