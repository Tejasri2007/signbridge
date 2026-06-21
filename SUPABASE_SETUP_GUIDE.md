# Supabase Video Storage Setup Guide

## Step 1: Get Your Supabase Credentials

1. Go to https://supabase.com and log in
2. Select your project
3. Click **Settings** → **API**
4. Copy the following:
   - **Project URL** (under "Project API keys")
   - **Service Role Secret** (keep this secret, only for backend)
   - **Anon Public** (for frontend)

## Step 2: Create Storage Bucket

1. In Supabase dashboard, go to **Storage**
2. Click **New bucket**
3. Name it: `sign-videos`
4. Make it **Public** (enable public access)
5. Click **Create**

## Step 3: Update .env File

Replace the credentials in `.env`:

```env
MONGODB_URI=mongodb+srv://Tejasri:Teja2007@mobilerecharge.raj1zpx.mongodb.net/signbridge?retryWrites=true&w=majority
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... (your service role secret)
FLASK_ENV=development
SECRET_KEY=dev-secret-key-signbridge-2025
```

## Step 4: Upload Videos Using CLI

### Option A: Using Python Script (After updating .env)

```bash
python upload_videos_to_supabase.py
```

### Option B: Using Supabase UI

1. Go to **Storage** → **sign-videos** bucket
2. Create folders:
   - `animations/`
   - `learning/`
   - `uploads/`
3. Manually upload videos to each folder

### Option C: Using Supabase CLI

```bash
npm install -g supabase

supabase start

# Upload files
supabase storage upload -r sign-videos/animations/ "archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS/"
supabase storage upload -r sign-videos/learning/ "learning/Animation_video/"
```

## Step 5: Test Configuration

Run this Python script to test:

```python
from supabase import create_client
import os

supabase = create_client(
    os.environ['SUPABASE_URL'],
    os.environ['SUPABASE_KEY']
)

# List files
response = supabase.storage.from_('sign-videos').list('animations')
print(response)
```

## Step 6: Deploy to Render

Make sure your Render environment has:
- `SUPABASE_URL`
- `SUPABASE_KEY`

Then push to GitHub and redeploy.

## Troubleshooting

**"Invalid API key"**: Use Service Role Secret, not Anon Public key

**"Bucket not found"**: Make sure bucket name is lowercase: `sign-videos`

**"Permission denied"**: Check bucket is set to Public
