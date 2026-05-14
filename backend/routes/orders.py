from flask import Blueprint, jsonify, request
from database.db import mysql
from utils.auth_utils import (
    token_required,
    customer_required,
    seller_required,
    admin_required
)

orders_bp = Blueprint("orders", __name__)


# CREATE ORDER (CUSTOMER ONLY)
@orders_bp.route("/create", methods=["POST"])
@token_required
@customer_required
def create_order(current_user):

    data = request.get_json()

    user_id = current_user["user_id"]

    part_id = data["part_id"]
    quantity = data["quantity"]

    cur = mysql.connection.cursor()

    # Check if spare part exists
    cur.execute(
        "SELECT Price, Stock_Quantity FROM sparepart WHERE Part_ID = %s",
        [part_id]
    )

    part = cur.fetchone()

    if not part:
        cur.close()

        return jsonify({
            "message": "Spare part not found"
        }), 404

    price = float(part[0])
    stock_quantity = int(part[1])

    # Check stock availability
    if quantity > stock_quantity:
        cur.close()

        return jsonify({
            "message": "Not enough stock available"
        }), 400

    # Calculate total amount
    total_amount = price * quantity

    order_status = "Pending"

    # Create order
    order_query = """
    INSERT INTO orders
    (User_ID, Total_amount, Order_status)
    VALUES (%s, %s, %s)
    """

    cur.execute(order_query, (
        user_id,
        total_amount,
        order_status
    ))

    mysql.connection.commit()

    order_id = cur.lastrowid

    # Create order item
    item_query = """
    INSERT INTO orderitem
    (Order_ID, Part_ID, Quantity, Price)
    VALUES (%s, %s, %s, %s)
    """

    cur.execute(item_query, (
        order_id,
        part_id,
        quantity,
        price
    ))

    # Reduce stock automatically
    new_stock = stock_quantity - quantity

    update_stock_query = """
    UPDATE sparepart
    SET Stock_Quantity = %s
    WHERE Part_ID = %s
    """

    cur.execute(update_stock_query, (
        new_stock,
        part_id
    ))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Order created successfully",
        "order_id": order_id,
        "total_amount": total_amount,
        "remaining_stock": new_stock
    })


# GET ALL ORDERS (ADMIN ONLY)
@orders_bp.route("/", methods=["GET"])
@token_required
@admin_required
def get_orders(current_user):

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM orders
    """

    cur.execute(query)

    orders = cur.fetchall()

    cur.close()

    result = []

    for order in orders:

        result.append({
            "order_id": order[0],
            "user_id": order[1],
            "total_amount": str(order[2]),
            "order_status": order[3]
        })

    return jsonify(result)


# GET MY ORDERS
@orders_bp.route("/myorders", methods=["GET"])
@token_required
def get_my_orders(current_user):

    user_id = current_user["user_id"]

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM orders
    WHERE User_ID = %s
    """

    cur.execute(query, [user_id])

    orders = cur.fetchall()

    cur.close()

    result = []

    for order in orders:

        result.append({
            "order_id": order[0],
            "user_id": order[1],
            "total_amount": str(order[2]),
            "order_status": order[3]
        })

    return jsonify(result)


# UPDATE ORDER STATUS (SELLER ONLY)
@orders_bp.route("/status/<int:order_id>", methods=["PUT"])
@token_required
@seller_required
def update_order_status(current_user, order_id):

    data = request.get_json()

    new_status = data["order_status"]

    cur = mysql.connection.cursor()

    query = """
    UPDATE orders
    SET Order_status = %s
    WHERE Order_ID = %s
    """

    cur.execute(query, (
        new_status,
        order_id
    ))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Order status updated successfully"
    })


# DELETE ORDER
@orders_bp.route("/delete/<int:order_id>", methods=["DELETE"])
@token_required
def delete_order(current_user, order_id):

    cur = mysql.connection.cursor()

    # Delete order items first
    delete_items_query = """
    DELETE FROM orderitem
    WHERE Order_ID = %s
    """

    cur.execute(delete_items_query, [order_id])

    # Delete order
    delete_order_query = """
    DELETE FROM orders
    WHERE Order_ID = %s
    """

    cur.execute(delete_order_query, [order_id])

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Order deleted successfully"
    })