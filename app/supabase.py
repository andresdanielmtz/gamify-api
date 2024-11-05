from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print(f"Supabase URL: {SUPABASE_URL}")  # Add debugging
print(f"Supabase Key exists: {bool(SUPABASE_KEY)}")  # Add debugging

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
