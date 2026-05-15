from flask import Blueprint, request, jsonify
import requests
from database.db import mysql

payments_bp = Blueprint("payments", __name__)

# PAYMOB KEYS
SECRET_KEY = "ZXlKaGJHY2lPaUpJVXpVeE1pSXNJblI1Y0NJNklrcFhWQ0o5LmV5SmpiR0Z6Y3lJNklrMWxjbU5vWVc1MElpd2ljSEp2Wm1sc1pWOXdheUk2TVRFMk16TTVOQ3dpYm1GdFpTSTZJbWx1YVhScFlXd2lmUS5DdDNmbXNScUZ6VUdVZlB1bTN6OFhxTkNsZmJXalRVbFZiV2VrSWFaWXhNbkx6ZmE5Z2lsU2NWU3BoSlk4ZHRTb0dkc2VsN3VMWlRPTmVVLVJCamY0dw=="
PUBLIC_KEY = "egy_pk_test_LgzceQYgSdZUd3CJsRV3ksjjPrImmB1R"
INTEGRATION_ID = "5666869"


# CREATE PAYMENT
@payments_bp.route("/create", methods=["POST"])
def create_payment():

    data = request.get_json()

    order_id = data["order_id"]
    amount = data["amount"]

    # 1. AUTH REQUEST
    auth_response = requests.post(
        "https://accept.paymobsolutions.com/api/auth/tokens",
        json={
            "api_key": SECRET_KEY
        }
    )

    if auth_response.status_code not in [200, 201]:
        return jsonify({
            "message": "Paymob auth failed",
            "status_code": auth_response.status_code,
            "response": auth_response.text
        }), 400

    auth_token = auth_response.json()["token"]

# 2. CREATE PAYMOB ORDER
    order_response = requests.post(
        "https://accept.paymobsolutions.com/api/ecommerce/orders",
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
        json={
            "delivery_needed": "false",
            "amount_cents": int(float(amount) * 100),
            "currency": "EGP",
            "items": []
        }
    )

    if order_response.status_code not in [200, 201]:
        return jsonify({
            "message": "Paymob order failed",
            "status_code": order_response.status_code,
            "response": order_response.text
        }), 400

    order_data = order_response.json()
    paymob_order_id = order_data["id"]

    cur = mysql.connection.cursor()

    insert_query = """
    INSERT INTO payment_mapping (
        local_order_id,
        paymob_order_id
    )
    VALUES (%s, %s)
    """

    cur.execute(insert_query, (
        order_id,
        paymob_order_id
    ))

    mysql.connection.commit()
    cur.close()

    # 3. GENERATE PAYMENT KEY
    payment_key_response = requests.post(
        "https://accept.paymobsolutions.com/api/acceptance/payment_keys",
        headers={
            "Authorization": f"Bearer {auth_token}"
        },
        json={
            "amount_cents": int(float(amount) * 100),
            "expiration": 3600,
            "order_id": paymob_order_id,
            "billing_data": {
                "apartment": "NA",
                "email": "test@example.com",
                "floor": "NA",
                "first_name": "Test",
                "street": "NA",
                "building": "NA",
                "phone_number": "01000000000",
                "shipping_method": "NA",
                "postal_code": "NA",
                "city": "Cairo",
                "country": "EG",
                "last_name": "User",
                "state": "Cairo"
            },
            "currency": "EGP",
            "integration_id": int(INTEGRATION_ID)
        }
    )

    if payment_key_response.status_code not in [200, 201]:
        return jsonify({
            "message": "Payment key failed",
            "response": payment_key_response.text
        }), 400

    payment_token = payment_key_response.json()["token"]

    payment_url = f"https://accept.paymobsolutions.com/api/acceptance/iframes/1043028?payment_token={payment_token}"

    return jsonify({
        "message": "Payment link created successfully",
        "local_order_id": order_id,
        "paymob_order_id": paymob_order_id,
        "payment_token": payment_token,
        "payment_url": payment_url
    })
@payments_bp.route("/callback", methods=["POST", "GET"])
def paymob_callback():

    data = request.get_json()

    print("CALLBACK FUNCTION WORKED", flush=True)
    print("========== PAYMOB CALLBACK ==========", flush=True)
    print(data, flush=True)

    transaction_data = data["obj"]

    success = transaction_data["success"]
    paymob_order_id = transaction_data["order"]["id"]
    transaction_id = transaction_data["id"]

    print("SUCCESS:", success, flush=True)
    print("PAYMOB ORDER ID:", paymob_order_id, flush=True)
    print("TRANSACTION ID:", transaction_id, flush=True)

    if success:
        payment_status = "Paid"
        order_status = "Confirmed"
    else:
        payment_status = "Failed"
        order_status = "Pending"

    cur = mysql.connection.cursor()

    select_query = """
    SELECT local_order_id
    FROM payment_mapping
    WHERE paymob_order_id = %s
    """

    cur.execute(select_query, (paymob_order_id,))
    result = cur.fetchone()

    if not result:
        cur.close()
        return jsonify({
            "message": "Payment mapping not found",
            "paymob_order_id": paymob_order_id
        }), 404

    local_order_id = result[0]

    update_query = """
    UPDATE orders
    SET Order_status = %s
    WHERE Order_ID = %s
    """

    cur.execute(update_query, (
        order_status,
        local_order_id
    ))

    mysql.connection.commit()
    payment_update_query = """
    UPDATE payment
    SET Payment_Status = %s,
    Transaction_ID = %s
    WHERE Order_ID = %s
    """

    cur.execute(payment_update_query, (
    payment_status,
    transaction_id,
    local_order_id
))

    mysql.connection.commit()
    cur.close()

    print("LOCAL ORDER ID:", local_order_id, flush=True)
    print("PAYMENT STATUS:", payment_status, flush=True)
    print("ORDER STATUS:", order_status, flush=True)

    return jsonify({
        "message": "Callback received and order updated",
        "payment_status": payment_status,
        "order_status": order_status,
        "local_order_id": local_order_id,
        "paymob_order_id": paymob_order_id,
        "transaction_id": transaction_id
    })