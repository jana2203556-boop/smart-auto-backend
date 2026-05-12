from flask import Blueprint, request, jsonify
from database.db import mysql
import bcrypt
import jwt
import datetime
from flask import current_app

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    name = data["name"]
    email = data["email"]
    phone = data["phone"]
    password = data["password"]
    address = data["address"]
    role_id = data["role_id"]

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    cur = mysql.connection.cursor()

    query = """
    INSERT INTO user
    (Role_ID, Name, Email, Phone, Password, Address)
    VALUES (%s,%s,%s,%s,%s,%s)
    """

    cur.execute(query, (
        role_id,
        name,
        email,
        phone,
        hashed_password,
        address
    ))

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "User registered successfully"
    })


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    cur = mysql.connection.cursor()

    cur.execute(
        "SELECT User_ID, Role_ID, Name, Email, Phone, Password, Address FROM user WHERE Email=%s",
        [email]
    )

    user = cur.fetchone()
    cur.close()

    if user:
        stored_password = str(user[5])

        if bcrypt.checkpw(
            password.encode("utf-8"),
            stored_password.encode("utf-8")
        ):

            token = jwt.encode({
                "user_id": user[0],
                "role_id": user[1],
                "email": user[3],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
            }, current_app.config["SECRET_KEY"], algorithm="HS256")

            return jsonify({
                "message": "Login successful",
                "token": token,
                "user": {
                    "user_id": user[0],
                    "role_id": user[1],
                    "name": user[2],
                    "email": user[3],
                    "phone": user[4],
                    "address": user[6]
                }
            })

    return jsonify({
        "message": "Invalid email or password"
    }), 401