from flask import Blueprint, request, jsonify 

review_bp = Blueprint("review", __name__)

@review_bp.route('/reviews', methods=['GET'])
def get_reviews():
    return jsonify({"message": "All reviews"}), 200

