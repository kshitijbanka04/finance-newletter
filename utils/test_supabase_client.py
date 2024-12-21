from supabase import create_client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize the client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    """Test the Supabase client connection."""
    try:
        # Fetch all rows from a table (e.g., 'user_profiles')
        response = supabase.table("user_profiles").select("*").execute()
        print(response)
        print("Supabase client successfully connected!")
        print("Data fetched from 'user_profiles':", response.data)

    except Exception as e:
        print("Error while testing Supabase connection:", e)

if __name__ == "__main__":
    test_connection()
