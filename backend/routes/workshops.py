from flask import Blueprint, jsonify, request
from database.db import mysql
from utils.auth_utils import token_required, customer_required, admin_required

workshops_bp = Blueprint("workshops", __name__)


# GET ALL WORKSHOPS
@workshops_bp.route("/", methods=["GET"])
def get_workshops():

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM workshop
    WHERE Approval_status = 'Approved'
    """

    cur.execute(query)

    workshops = cur.fetchall()

    cur.close()

    result = []

    for workshop in workshops:

        result.append({
            "workshop_id": workshop[0],
            "user_id": workshop[1],
            "workshop_name": workshop[2],
            "location": workshop[3],
            "service_type": workshop[4],
            "approval_status": workshop[5]
        })

    return jsonify(result)
@token_required
@customer_required
    # BOOK WORKSHOP
@workshops_bp.route("/book", methods=["POST"])
@token_required
def book_workshop(current_user):

    data = request.get_json()

    user_id = current_user["user_id"]
    workshop_id = data["workshop_id"]
    booking_date = data["booking_date"]
    timeslot = data["timeslot"]

    booking_status = "Pending"

    cur = mysql.connection.cursor()

    query = """
    INSERT INTO booking
    (User_ID, Workshop_ID, Booking_date, Booking_status, Timeslot)
    VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        user_id,
        workshop_id,
        booking_date,
        booking_status,
        timeslot
    ))

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Workshop booked successfully"
    })
@token_required
@admin_required
# GET MY BOOKINGS
@workshops_bp.route("/mybookings", methods=["GET"])
@token_required
def get_my_bookings(current_user):

    user_id = current_user["user_id"]

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM booking
    WHERE User_ID = %s
    """

    cur.execute(query, [user_id])

    bookings = cur.fetchall()
    cur.close()

    result = []

    for booking in bookings:
        result.append({
            "booking_id": booking[0],
            "user_id": booking[1],
            "workshop_id": booking[2],
            "booking_date": str(booking[3]),
            "booking_status": booking[4],
            "timeslot": booking[5]
        })

    return jsonify(result)
@token_required
@admin_required
# UPDATE BOOKING STATUS
@workshops_bp.route("/booking/status/<int:booking_id>", methods=["PUT"])
@token_required
def update_booking_status(current_user, booking_id):

    data = request.get_json()

    new_status = data["booking_status"]

    cur = mysql.connection.cursor()

    query = """
    UPDATE booking
    SET Booking_status = %s
    WHERE Booking_ID = %s
    """

    cur.execute(query, (
        new_status,
        booking_id
    ))

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Booking status updated successfully"
    })
# DELETE BOOKING
@workshops_bp.route("/booking/delete/<int:booking_id>", methods=["DELETE"])
@token_required
def delete_booking(current_user, booking_id):

    cur = mysql.connection.cursor()

    query = """
    DELETE FROM booking
    WHERE Booking_ID = %s
    """

    cur.execute(query, [booking_id])

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Booking deleted successfully"
    })
# GET ALL BOOKINGS
@workshops_bp.route("/bookings", methods=["GET"])
@token_required
def get_all_bookings(current_user):

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM booking
    """

    cur.execute(query)

    bookings = cur.fetchall()

    cur.close()

    result = []

    for booking in bookings:

        result.append({
            "booking_id": booking[0],
            "user_id": booking[1],
            "workshop_id": booking[2],
            "booking_date": str(booking[3]),
            "booking_status": booking[4],
            "timeslot": booking[5]
        })

    return jsonify(result)