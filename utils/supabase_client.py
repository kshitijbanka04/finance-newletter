from supabase import create_client
import os

# Load Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def fetch_table_data(table_name):
    """Fetch all data from a given table."""
    response = supabase.table(table_name).select("*").execute()
    return response.data

def insert_table_data(table_name, data):
    """Insert data into a given table."""
    response = supabase.table(table_name).insert(data).execute()
    return response.data

def update_table_data(table_name, filters, updates):
    """Update rows in a given table."""
    query = supabase.table(table_name)
    for key, value in filters.items():
        query = query.eq(key, value)
    response = query.update(updates).execute()
    return response.data
