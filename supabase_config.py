import os
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_file(file_path, bucket_name, file_name):
    """Upload file to Supabase"""
    try:
        with open(file_path, 'rb') as f:
            supabase.storage.from_(bucket_name).upload(file_name, f)
        return True
    except Exception as e:
        print(f"Upload error: {e}")
        return False

def download_file(bucket_name, file_name, save_path):
    """Download file from Supabase"""
    try:
        response = supabase.storage.from_(bucket_name).download(file_name)
        with open(save_path, 'wb') as f:
            f.write(response)
        return True
    except Exception as e:
        print(f"Download error: {e}")
        return False

def get_file_url(bucket_name, file_name):
    """Get public URL of file"""
    try:
        return supabase.storage.from_(bucket_name).get_public_url(file_name)
    except:
        return None

def delete_file(bucket_name, file_name):
    """Delete file from Supabase"""
    try:
        supabase.storage.from_(bucket_name).remove([file_name])
        return True
    except:
        return False
