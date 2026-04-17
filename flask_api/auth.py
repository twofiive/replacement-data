from functools import wraps
from flask import request, jsonify
from flask_api.config import API_KEY


def require_api_key(f):
    """
    Décorateur pour protéger les endpoints avec une API key.
    La clé doit être passée dans le header : X-API-Key: <clé>
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key != API_KEY:
            return jsonify({
                "error": "Unauthorized",
                "message": "API key manquante ou invalide"
            }), 401
        return f(*args, **kwargs)
    return decorated