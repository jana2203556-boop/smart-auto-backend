from functools import wraps
from flask import request, jsonify, current_app
import jwt


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        token = None

        if "Authorization" in request.headers:

            auth_header = request.headers["Authorization"]

            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({
                "message": "Token is missing"
            }), 401

        try:

            current_user = jwt.decode(
                token,
                current_app.config["SECRET_KEY"],
                algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            return jsonify({
                "message": "Token expired"
            }), 401

        except jwt.InvalidTokenError:
            return jsonify({
                "message": "Invalid token"
            }), 401

        return f(current_user, *args, **kwargs)

    return decorated


def seller_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):

        if current_user["role_id"] != 2:

            return jsonify({
                "message": "Access denied. Sellers only."
            }), 403

        return f(current_user, *args, **kwargs)

    return decorated