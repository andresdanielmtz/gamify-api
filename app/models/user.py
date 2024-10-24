from ..database import get_db
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    @staticmethod
    def create(username, password):
        db = get_db()
        hashed_password = generate_password_hash(password)
        with db:
            db.execute(
                'INSERT INTO users (username, password) VALUES (?, ?)',
                (username, hashed_password)
            )
        return True

    @staticmethod
    def get_by_username(username):
        db = get_db()
        return db.execute(
            'SELECT * FROM users WHERE username = ?', (username,)
        ).fetchone()

    @staticmethod
    def check_password(user, password):
        return check_password_hash(user['password'], password)

