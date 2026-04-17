from flask import Blueprint, jsonify
from api.auth import require_api_key
import psycopg2
import psycopg2.extras
from api.config import DB_CONFIG

stats_bp = Blueprint("stats", __name__)


def get_db():
    return psycopg2.connect(**DB_CONFIG)


@stats_bp.route("/stats/regions", methods=["GET"])
@require_api_key
def stats_regions():
    """Retourne le nombre d'annonces par région (vue SQL v_annonces_par_region)."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM v_annonces_par_region")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"data": [dict(r) for r in data]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/stats/types", methods=["GET"])
@require_api_key
def stats_types():
    """Retourne le nombre d'annonces par type d'offre (vue SQL v_annonces_par_type)."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM v_annonces_par_type")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"data": [dict(r) for r in data]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@stats_bp.route("/stats/geolocalisees", methods=["GET"])
@require_api_key
def stats_geolocalisees():
    """Retourne les annonces géolocalisées (vue SQL v_annonces_geolocalisees)."""
    try:
        conn = get_db()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM v_annonces_geolocalisees")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify({"data": [dict(r) for r in data]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500