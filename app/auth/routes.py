from flask import Blueprint, request, jsonify, make_response
from flask_cors import cross_origin
from ..supabase import supabase

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/check", methods=["GET"])
@cross_origin(supports_credentials=True)
def check_auth():
    try:
        session = supabase.auth.get_session()
        if not session:
            return (
                jsonify({"authenticated": False, "message": "Not authenticated"}),
                401,
            )

        user_data = (
            supabase.table("users")
            .select("*")
            .eq("email", session.user.email)
            .execute()
        )

        return (
            jsonify(
                {
                    "authenticated": True,
                    "user": user_data.data[0] if user_data.data else None,
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"authenticated": False, "message": "Authentication failed"}),
            401,
        )


@auth_bp.route("/register", methods=["POST"])
@cross_origin(supports_credentials=True)
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {"email": email}
                }
            })

            if not response.user:
                return jsonify({"error": "Registration failed"}), 400

            # Create response with cookies
            resp = make_response(
                jsonify({
                    "message": "Registration successful",
                    "user": {
                        "id": response.user.id,
                        "email": response.user.email
                    }
                }), 
                201
            )

            # Set cookies if session exists
            if response.session:
                resp.set_cookie(
                    'sb-access-token',
                    response.session.access_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    path='/'
                )
                resp.set_cookie(
                    'sb-refresh-token',
                    response.session.refresh_token,
                    httponly=True,
                    secure=True,
                    samesite='Lax',
                    path='/'
                )

            return resp

        except Exception as e:
            error_message = str(e)
            if "cannot be used as it is not authorized" in error_message:
                return jsonify({
                    "error": "This email domain is not authorized. Please use an allowed email domain."
                }), 403
            if "User already registered" in error_message:
                return jsonify({"error": "Email already registered"}), 409
            raise e

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400

        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        if not response.user:
            return jsonify({"error": "Invalid credentials"}), 401

        # Set session cookie
        session_data = response.session
        if session_data:
            response.headers.add(
                "Set-Cookie",
                f"sb-access-token={session_data.access_token}; Path=/; HttpOnly",
            )
            response.headers.add(
                "Set-Cookie",
                f"sb-refresh-token={session_data.refresh_token}; Path=/; HttpOnly",
            )

        user_data = supabase.table("users").select("*").eq("email", email).execute()

        return (
            jsonify(
                {
                    "message": "Login successful",
                    "user": (
                        user_data.data[0]
                        if user_data.data
                        else {"id": response.user.id, "email": response.user.email}
                    ),
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({"error": "Invalid credentials"}), 401


@auth_bp.route("/logout", methods=["POST"])
@cross_origin(supports_credentials=True)
def logout():
    try:
        supabase.auth.sign_out()
        response = jsonify({"message": "Logout successful"})

        # Clear cookies
        response.delete_cookie("sb-access-token")
        response.delete_cookie("sb-refresh-token")

        return response, 200
    except Exception as e:
        return jsonify({"error": "Logout failed"}), 500


@auth_bp.route("/get_username", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_username():
    try:
        session = supabase.auth.get_session()
        if not session:
            return jsonify({"error": "Not authenticated"}), 401

        user_data = (
            supabase.table("users")
            .select("username")
            .eq("email", session.user.email)
            .execute()
        )

        if not user_data.data:
            return jsonify({"error": "Username not found"}), 404

        return (
            jsonify(
                {
                    "username": user_data.data[0].get("username")
                    or session.user.email.split("@")[0]
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Failed to fetch username"}), 500
