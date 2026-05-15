from flask import Blueprint, request, jsonify
from database.db import mysql
from utils.auth_utils import token_required, customer_required

reviews_bp = Blueprint("reviews", __name__)


# ADD REVIEW
@reviews_bp.route("/add", methods=["POST"])
@token_required
@customer_required
def add_review(current_user):

    data = request.get_json()

    user_id = current_user["user_id"]
    sparepart_id = data.get("sparepart_id")
    workshop_id = data.get("workshop_id")
    rating = data.get("rating")
    comment = data.get("comment")

    if not rating or rating < 1 or rating > 5:
        return jsonify({
            "message": "Rating must be between 1 and 5"
        }), 400

    if not sparepart_id and not workshop_id:
        return jsonify({
            "message": "You must review either a spare part or a workshop"
        }), 400

    if sparepart_id and workshop_id:
        return jsonify({
            "message": "Review only one item at a time"
        }), 400

    cur = mysql.connection.cursor()

    query = """
    INSERT INTO review (
        User_ID,
        Sparepart_ID,
        Workshop_ID,
        Rating,
        Comment
    )
    VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(query, (
        user_id,
        sparepart_id,
        workshop_id,
        rating,
        comment
    ))

    mysql.connection.commit()
    cur.close()

    return jsonify({
        "message": "Review added successfully"
    })
# GET SPARE PART REVIEWS
@reviews_bp.route("/sparepart/<int:part_id>", methods=["GET"])
def get_sparepart_reviews(part_id):

    cur = mysql.connection.cursor()

    query = """
    SELECT
        r.Review_ID,
        r.Rating,
        r.Comment,
        r.Created_At,
        u.Name
    FROM review r
    JOIN user u ON r.User_ID = u.User_ID
    WHERE r.Sparepart_ID = %s
    ORDER BY r.Created_At DESC
    """

    cur.execute(query, (part_id,))

    reviews = cur.fetchall()

    cur.close()

    results = []

    for review in reviews:
        results.append({
            "review_id": review[0],
            "rating": review[1],
            "comment": review[2],
            "created_at": str(review[3]),
            "customer_name": review[4]
        })

    return jsonify(results)
# GET WORKSHOP REVIEWS
@reviews_bp.route("/workshop/<int:workshop_id>", methods=["GET"])
def get_workshop_reviews(workshop_id):

    cur = mysql.connection.cursor()

    query = """
    SELECT
        r.Review_ID,
        r.Rating,
        r.Comment,
        r.Created_At,
        u.Name
    FROM review r
    JOIN user u ON r.User_ID = u.User_ID
    WHERE r.Workshop_ID = %s
    ORDER BY r.Created_At DESC
    """

    cur.execute(query, (workshop_id,))

    reviews = cur.fetchall()

    cur.close()

    results = []

    for review in reviews:
        results.append({
            "review_id": review[0],
            "rating": review[1],
            "comment": review[2],
            "created_at": str(review[3]),
            "customer_name": review[4]
        })

    return jsonify(results)
# GET SPARE PART AVERAGE RATING
@reviews_bp.route("/average/sparepart/<int:part_id>", methods=["GET"])
def get_sparepart_average_rating(part_id):

    cur = mysql.connection.cursor()

    query = """
    SELECT AVG(Rating)
    FROM review
    WHERE Sparepart_ID = %s
    """

    cur.execute(query, (part_id,))

    result = cur.fetchone()

    cur.close()

    average_rating = result[0]

    if average_rating is None:
        average_rating = 0

    return jsonify({
        "sparepart_id": part_id,
        "average_rating": round(float(average_rating), 1)
    })


# GET WORKSHOP AVERAGE RATING
@reviews_bp.route("/average/workshop/<int:workshop_id>", methods=["GET"])
def get_workshop_average_rating(workshop_id):

    cur = mysql.connection.cursor()

    query = """
    SELECT AVG(Rating)
    FROM review
    WHERE Workshop_ID = %s
    """

    cur.execute(query, (workshop_id,))

    result = cur.fetchone()

    cur.close()

    average_rating = result[0]

    if average_rating is None:
        average_rating = 0

    return jsonify({
        "workshop_id": workshop_id,
        "average_rating": round(float(average_rating), 1)
    })