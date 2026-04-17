from flask import Flask, jsonify
from api.routes.annonces import annonces_bp
from api.routes.stats import stats_bp

def create_app():
    """Factory function pour créer l'application Flask."""
    app = Flask(__name__)

    # Enregistrement des blueprints
    app.register_blueprint(annonces_bp, url_prefix="/api/v1")
    app.register_blueprint(stats_bp, url_prefix="/api/v1")

    # Route de santé
    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "ok",
            "service": "Osteopathes Replacement API",
            "version": "1.0.0"
        }), 200

    # Route racine avec documentation des endpoints
    @app.route("/", methods=["GET"])
    def index():
        return jsonify({
            "service": "API Annonces Ostéopathes",
            "version": "1.0.0",
            "endpoints": {
                "GET /health": "Santé de l'API",
                "GET /api/v1/annonces": "Liste des annonces (filtres: region, type_offre, limit, offset)",
                "GET /api/v1/annonces/<id>": "Détail d'une annonce",
                "GET /api/v1/stats/regions": "Statistiques par région",
                "GET /api/v1/stats/types": "Statistiques par type d'offre",
                "GET /api/v1/stats/geolocalisees": "Annonces géolocalisées",
            },
            "auth": "Header requis : X-API-Key: <clé>"
        }), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)