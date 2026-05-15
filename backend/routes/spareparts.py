from flask import Blueprint, jsonify, request
from database.db import mysql
from utils.auth_utils import token_required, seller_required

spareparts_bp = Blueprint("spareparts", __name__)


@spareparts_bp.route("/", methods=["GET"])
def get_parts():

    cur = mysql.connection.cursor()

    cur.execute("SELECT * FROM sparepart")

    parts = cur.fetchall()

    cur.close()

    result = []

    for part in parts:

        result.append({
            "Part_ID": part[0],
            "Seller_ID": part[1],
            "Part_name": part[2],
            "Price": str(part[3]),
            "Stock_Quantity": part[4],
            "Description": part[5]
        })

    return jsonify(result)


@spareparts_bp.route("/add", methods=["POST"])
@token_required
@seller_required
def add_part(current_user):

    data = request.get_json()

    seller_id = data["seller_id"]

    part_name = data["part_name"]
    price = data["price"]
    stock_quantity = data["stock_quantity"]
    description = data["description"]

    cur = mysql.connection.cursor()

    query = """
    INSERT INTO sparepart
    (Seller_ID, Part_name, Price, Stock_Quantity, Description)
    VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        seller_id,
        part_name,
        price,
        stock_quantity,
        description
    ))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Spare part added successfully"
    })


@spareparts_bp.route("/update/<int:part_id>", methods=["PUT"])
@token_required
@seller_required
def update_part(current_user, part_id):

    data = request.get_json()

    part_name = data["part_name"]
    price = data["price"]
    stock_quantity = data["stock_quantity"]
    description = data["description"]

    cur = mysql.connection.cursor()

    query = """
    UPDATE sparepart
    SET Part_name=%s,
        Price=%s,
        Stock_Quantity=%s,
        Description=%s
    WHERE Part_ID=%s
    """

    cur.execute(query, (
        part_name,
        price,
        stock_quantity,
        description,
        part_id
    ))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Spare part updated successfully"
    })


@spareparts_bp.route("/delete/<int:part_id>", methods=["DELETE"])
@token_required
@seller_required
def delete_part(current_user, part_id):

    cur = mysql.connection.cursor()

    query = "DELETE FROM sparepart WHERE Part_ID=%s"

    cur.execute(query, [part_id])

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Spare part deleted successfully"
    })
@spareparts_bp.route("/search", methods=["GET"])
def search_spare_parts():

    part_name = request.args.get("name")

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM sparepart
    WHERE Part_name LIKE %s
    """

    search_value = "%" + part_name + "%"

    cur.execute(query, [search_value])

    spareparts = cur.fetchall()

    cur.close()

    result = []

    for part in spareparts:

        result.append({
            "part_id": part[0],
            "seller_id": part[1],
            "part_name": part[2],
            "price": str(part[3]),
            "stock_quantity": part[4],
            "description": part[5]
        })

    return jsonify(result)
# FILTER SPARE PARTS BY PRICE
@spareparts_bp.route("/filter", methods=["GET"])
def filter_parts():

    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM sparepart
    WHERE Price BETWEEN %s AND %s
    """

    cur.execute(query, (
        min_price,
        max_price
    ))

    parts = cur.fetchall()

    cur.close()

    result = []

    for part in parts:

        result.append({
            "part_id": part[0],
            "seller_id": part[1],
            "part_name": part[2],
            "description": part[3],
            "price": float(part[4]),
            "stock_quantity": part[5]
        })

    return jsonify(result)
# GET IN-STOCK SPARE PARTS
@spareparts_bp.route("/in-stock", methods=["GET"])
def get_in_stock_parts():

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM sparepart
    WHERE Stock_Quantity > 0
    """

    cur.execute(query)

    parts = cur.fetchall()
    cur.close()

    result = []

    for part in parts:
     result.append({
    "part_id": part[0],
    "seller_id": part[1],
    "part_name": part[2],
    "price": float(part[3]),
    "stock_quantity": part[4],
    "description": part[5]
})

    return jsonify(result)
# COMBINED SEARCH + FILTER SPARE PARTS
@spareparts_bp.route("/search-filter", methods=["GET"])
def search_filter_parts():

    name = request.args.get("name")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM sparepart
    WHERE Part_name LIKE %s
    AND Price BETWEEN %s AND %s
    """

    search_value = "%" + name + "%"

    cur.execute(query, (
        search_value,
        min_price,
        max_price
    ))

    parts = cur.fetchall()
    cur.close()

    result = []

    for part in parts:
        result.append({
            "part_id": part[0],
            "seller_id": part[1],
            "part_name": part[2],
            "price": float(part[3]),
            "stock_quantity": part[4],
            "description": part[5]
        })

    return jsonify(result)