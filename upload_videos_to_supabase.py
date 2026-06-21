import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

ANIMATION_FOLDER = 'archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS'
LEARNING_FOLDER = 'learning/Animation_video'
BUCKET_NAME = 'sign-videos'

def ensure_bucket_exists():
    """Create bucket if it doesn't exist"""
    try:
        supabase.storage.create_bucket(BUCKET_NAME, options={"public": True})
        print(f"✅ Bucket '{BUCKET_NAME}' created")
    except Exception as e:
        if 'already exists' in str(e):
            print(f"✅ Bucket '{BUCKET_NAME}' already exists")
        else:
            print(f"❌ Bucket error: {e}")

def upload_videos(source_folder, remote_prefix):
    """Upload all videos from a folder to Supabase"""
    if not os.path.exists(source_folder):
        print(f"❌ Folder not found: {source_folder}")
        return 0
    
    files = [f for f in os.listdir(source_folder) if f.endswith('.mp4')]
    uploaded = 0
    
    for i, filename in enumerate(files, 1):
        file_path = os.path.join(source_folder, filename)
        remote_path = f"{remote_prefix}/{filename}"
        
        try:
            with open(file_path, 'rb') as f:
                supabase.storage.from_(BUCKET_NAME).upload(remote_path, f)
            print(f"✅ [{i}/{len(files)}] Uploaded: {remote_path}")
            uploaded += 1
        except Exception as e:
            if 'already exists' in str(e):
                print(f"⏭️  [{i}/{len(files)}] Already exists: {remote_path}")
                uploaded += 1
            else:
                print(f"❌ [{i}/{len(files)}] Failed: {filename} - {e}")
    
    return uploaded

def main():
    print("🚀 Starting video upload to Supabase...\n")
    
    ensure_bucket_exists()
    
    print(f"\n📁 Uploading from {ANIMATION_FOLDER}...")
    count1 = upload_videos(ANIMATION_FOLDER, 'animations')
    
    print(f"\n📁 Uploading from {LEARNING_FOLDER}...")
    count2 = upload_videos(LEARNING_FOLDER, 'learning')
    
    print(f"\n✅ Upload complete! Total: {count1 + count2} videos")
    
    # Test getting a public URL
    try:
        test_url = supabase.storage.from_(BUCKET_NAME).get_public_url('animations/HELLO.mp4')
        print(f"\n🔗 Sample video URL: {test_url}")
    except:
        pass

if __name__ == '__main__':
    main()
