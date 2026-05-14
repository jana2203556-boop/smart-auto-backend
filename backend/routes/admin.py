from flask import Blueprint, jsonify
from database.db import mysql
from utils.auth_utils import token_required, admin_required

admin_bp = Blueprint("admin", __name__)


# GET PENDING SELLERS
@admin_bp.route("/pending-sellers", methods=["GET"])
@token_required
@admin_required
def get_pending_sellers(current_user):

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM seller
    WHERE Approval_status = 'Pending'
    """

    cur.execute(query)

    sellers = cur.fetchall()

    cur.close()

    result = []

    for seller in sellers:

        result.append({
            "seller_id": seller[0],
            "user_id": seller[1],
            "store_name": seller[2],
            "approval_status": seller[3]
        })

    return jsonify(result)


# APPROVE SELLER
@admin_bp.route("/approve-seller/<int:seller_id>", methods=["PUT"])
@token_required
@admin_required
def approve_seller(current_user, seller_id):

    user_id = current_user["user_id"]

    cur = mysql.connection.cursor()

    # Get Admin_ID from admin table
    cur.execute(
        "SELECT Admin_ID FROM admin WHERE User_ID = %s",
        [user_id]
    )

    admin = cur.fetchone()

    if not admin:
        cur.close()

        return jsonify({
            "message": "Admin not found"
        }), 404

    admin_id = admin[0]

    query = """
    UPDATE seller
    SET Approval_status = 'Approved',
        Approved_by_admin_ID = %s
    WHERE Seller_ID = %s
    """

    cur.execute(query, (
        admin_id,
        seller_id
    ))

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Seller approved successfully"
    })
    # REJECT SELLER
@admin_bp.route("/reject-seller/<int:seller_id>", methods=["PUT"])
@token_required
@admin_required
def reject_seller(current_user, seller_id):

    cur = mysql.connection.cursor()

    query = """
    UPDATE seller
    SET Approval_status = 'Rejected'
    WHERE Seller_ID = %s
    """

    cur.execute(query, [seller_id])

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Seller rejected successfully"
    })
    # GET PENDING WORKSHOPS
@admin_bp.route("/pending-workshops", methods=["GET"])
@token_required
@admin_required
def get_pending_workshops(current_user):

    cur = mysql.connection.cursor()

    query = """
    SELECT *
    FROM workshop
    WHERE Approval_status = 'Pending'
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
    # APPROVE WORKSHOP
@admin_bp.route("/approve-workshop/<int:workshop_id>", methods=["PUT"])
@token_required
@admin_required
def approve_workshop(current_user, workshop_id):

    cur = mysql.connection.cursor()

    query = """
    UPDATE workshop
    SET Approval_status = 'Approved'
    WHERE Workshop_ID = %s
    """

    cur.execute(query, [workshop_id])

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Workshop approved successfully"
    })
# REJECT WORKSHOP
@admin_bp.route("/reject-workshop/<int:workshop_id>", methods=["PUT"])
@token_required
@admin_required
def reject_workshop(current_user, workshop_id):

    cur = mysql.connection.cursor()

    query = """
    UPDATE workshop
    SET Approval_status = 'Rejected'
    WHERE Workshop_ID = %s
    """

    cur.execute(query, [workshop_id])

    mysql.connection.commit()

    cur.close()

    return jsonify({
        "message": "Workshop rejected successfully"
    })