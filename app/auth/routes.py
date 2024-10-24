from flask import Blueprint, request, jsonify, session
from ..models.user import User
import sqlite3

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/register", methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        try:
            User.create(username, password)
            return jsonify({'message': 'User registered successfully'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username already exists'}), 409

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route("/login", methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400

        user = User.get_by_username(username)

        if user and User.check_password(user, password):
            session.permanent = True
            session['user_id'] = user['id']
            return jsonify({
                'message': 'Login successful',
                'user': {'id': user['id'], 'username': user['username']}
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route("/check", methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True}), 200
    return jsonify({'authenticated': False}), 401

@auth_bp.route("/logout", methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logout successful'}), 200

