from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from ..models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.get_by_username(username)
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout successful"}), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.get(session['user_id'])
        if user:
            return jsonify({"authenticated": True, "user": user.username}), 200
    return jsonify({"authenticated": False, "msg": "You are not authenticated"}), 401