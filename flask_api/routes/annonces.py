from flask import Blueprint, jsonify, request
from api.auth import require_api_key
import psycopg2
import psycopg2.extras
from api.config import DB_CONFIG

annonces_bp = Blueprint("annonces", __name__)


def get_db():
    """Connexion à la base PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


@annonces_bp.route("/annonces", methods=["GET"])
@require_api_key
def get_annonces():
    """
    Récupère la liste des annonces avec filtres optionnels.
    Paramètres query :
        - region : filtrer par région
        - type_offre : filtrer par type d'offre
        - limit : nombre de résultats (défaut 20, max 100)
        - offset : pagination (défaut 0)
    """
    region = request.args.get("region")
    type_offre = request.args.get("type_offre")
    limit = min(int(request.args.get("limit", 20)), 100)
    offset = int(request.args.get("offset", 0))

    query = "SELECT * FROM annonces WHERE 1=1"
    params = []

    if region:
        query += " AND region ILIKE %s"
        params.append(f"%{region}%")
    if type_offre:
        query += " AND type_offre ILIKE %s"
        params.append(f"%{type_offre}%")

    query += " ORDER BY id DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(query, params)
        annonces = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({
            "total": len(annonces),
            "limit": limit,
            "offset": offset,
            "data": [dict(a) for a in annonces]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@annonces_bp.route("/annonces/<int:annonce_id>", methods=["GET"])
@require_api_key
def get_annonce(annonce_id):
    """Récupère le détail d'une annonce par son ID."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM annonces WHERE id = %s", (annonce_id,))
        annonce = cur.fetchone()
        cur.close()
        conn.close()

        if not annonce:
            return jsonify({"error": "Annonce non trouvée"}), 404
        return jsonify(dict(annonce)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500