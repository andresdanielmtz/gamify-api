from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from ..models.user import User
from flask_cors import cross_origin

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    user = User.get_by_username(username)
    if user and check_password_hash(user.password, password):
        session["user_id"] = user.id
        return jsonify({"message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful"}), 200


@auth_bp.route("/get_username", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_username():
    if "user_id" in session:
        user = User.get(session["user_id"])
        if user:
            return jsonify({"username": user.username}), 200
    return (
        jsonify({"error": "You are not authenticated"}),
        401,
    )


@auth_bp.route("/register", methods=["POST"])
@cross_origin(supports_credentials=True)
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    print(f"Username: {username}, Password: {password}")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if User.get_by_username(username):
        return jsonify({"error": "Username already exists"}), 400

    try:
        # Use the create static method instead of constructing User directly
        User.create(username, password)
        return jsonify({"message": "User created successfully"}), 201
    except Exception as e:
        print(f"Error creating user: {str(e)}")
        return jsonify({"error": "Error creating user"}), 500


@auth_bp.route("/check", methods=["GET"])
@cross_origin(supports_credentials=True)
def check_auth():
    if "user_id" in session:
        user = User.get(session["user_id"])
        if user:
            return jsonify({"authenticated": True, "user": user.username}), 200
    return (
        jsonify({"authenticated": False, "message": "You are not authenticated"}),
        401,
    )
