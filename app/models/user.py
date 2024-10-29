from werkzeug.security import generate_password_hash, check_password_hash
from ..database import get_db
import sqlite3


class User:
    def __init__(self, id, username, password):
        """
        Initialize a User instance
        :param id: The user's ID from the database
        :param username: The user's username
        :param password: The user's hashed password
        """
        self.id = id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        """
        Get a user by their ID
        :param user_id: The ID of the user to retrieve
        :return: User object if found, None otherwise
        """
        try:
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

            if user:
                return User(user["id"], user["username"], user["password"])
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def get_by_username(username):
        """
        Get a user by their username
        :param username: The username to search for
        :return: User object if found, None otherwise
        """
        try:
            db = get_db()
            user = db.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()

            if user:
                return User(user["id"], user["username"], user["password"])
            return None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    @staticmethod
    def create(username, password):
        """
        Create a new user
        :param username: The username for the new user
        :param password: The password for the new user (will be hashed)
        :return: True if successful, raises exception otherwise
        """
        try:
            db = get_db()
            hashed_password = generate_password_hash(password)
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password),
            )
            db.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError("Username already exists")
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")
