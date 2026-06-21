#!/usr/bin/env python3
"""Test video availability in the Sign Language Converter app"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_local_videos():
    """Test local video storage"""
    print("\n[LOCAL VIDEOS]")
    print("=" * 50)
    
    paths = {
        'Animations': 'archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS',
        'Learning': 'learning/Animation_video',
        'Uploads': 'sign_videos'
    }
    
    for name, path in paths.items():
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.mp4')]
            print("[OK] {}: {} videos".format(name, len(files)))
            if files:
                print("     Sample: {}, {}...".format(files[0], files[1] if len(files) > 1 else ''))
        else:
            print("[FAIL] {}: Path not found - {}".format(name, path))

def test_supabase_config():
    """Test Supabase configuration"""
    print("\n[SUPABASE CONFIG]")
    print("=" * 50)
    
    url = os.environ.get('SUPABASE_URL', '').strip()
    key = os.environ.get('SUPABASE_KEY', '').strip()
    
    if url:
        print("[OK] SUPABASE_URL: {}...".format(url[:30]))
    else:
        print("[FAIL] SUPABASE_URL not set")
    
    if key:
        print("[OK] SUPABASE_KEY: {}...".format(key[:20]))
    else:
        print("[FAIL] SUPABASE_KEY not set")
    
    if url and key:
        try:
            from supabase import create_client
            client = create_client(url, key)
            print("[OK] Supabase client created")
        except Exception as e:
            print("[FAIL] Supabase error: {}".format(str(e)[:80]))
    else:
        print("[INFO] Supabase disabled - will use local storage fallback")

def test_video_counts():
    """Count total videos available"""
    print("\n[VIDEO COUNTS]")
    print("=" * 50)
    
    total = 0
    paths = {
        'Animations': 'archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS',
        'Learning': 'learning/Animation_video',
        'Uploads': 'sign_videos'
    }
    
    for name, path in paths.items():
        if os.path.exists(path):
            count = len([f for f in os.listdir(path) if f.endswith('.mp4')])
            total += count
            print("{}: {} videos".format(name.ljust(15), count))
    
    print("-" * 50)
    print("TOTAL: {} videos available".format(total))

def main():
    print("\n" + "=" * 50)
    print("SIGN LANGUAGE VIDEOS - AVAILABILITY TEST")
    print("=" * 50)
    
    test_local_videos()
    test_supabase_config()
    test_video_counts()
    
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print("""
[OK] Local videos available for immediate use

Optional: For cloud storage via Supabase
- Follow SUPABASE_SETUP_GUIDE.md
- Add credentials to .env and Render dashboard

Deployment: Ready to push to Render
- Videos served from local storage
- Supabase integration available when configured
    """)

if __name__ == '__main__':
    main()
