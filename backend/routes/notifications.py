from flask import Blueprint, jsonify
from database.db import mysql
from utils.auth_utils import token_required

notifications_bp = Blueprint("notifications", __name__)


# GET USER NOTIFICATIONS
@notifications_bp.route("/", methods=["GET"])
@token_required
def get_notifications(current_user):

    user_id = current_user["user_id"]

    cur = mysql.connection.cursor()

    query = """
    SELECT Notification_ID, Message, Is_Read, Created_At
    FROM notification
    WHERE User_ID = %s
    ORDER BY Created_At DESC
    """

    cur.execute(query, (user_id,))

    notifications = cur.fetchall()
    cur.close()

    result = []

    for notification in notifications:
        result.append({
            "notification_id": notification[0],
            "message": notification[1],
            "is_read": bool(notification[2]),
            "created_at": str(notification[3])
        })

    return jsonify(result)