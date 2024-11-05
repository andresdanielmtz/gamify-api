from werkzeug.security import generate_password_hash, check_password_hash
from ..database import get_db
import sqlite3

class User:
    @staticmethod
    def get_user_by_id(user_id):
        try:
            response = supabase.table('users').select('*').eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error fetching user from Supabase: {str(e)}")
            return None

    @staticmethod
    def create_user_profile(user_id, email, username=None):
        try:
            user_data = {
                'id': user_id,
                'email': email,
                'username': username or email.split('@')[0],
                'created_at': 'now()'
            }
            response = supabase.table('users').insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error creating user profile in Supabase: {str(e)}")
            return None

    @staticmethod
    def update_user_profile(user_id, update_data):
        try:
            response = supabase.table('users').update(update_data).eq('id', user_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating user profile in Supabase: {str(e)}")
            return None
