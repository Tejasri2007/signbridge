# Complete Deployment Guide - SignBridge

## Architecture
- **Backend**: Render.com (Flask app)
- **Database**: MongoDB Atlas (cloud)
- **File Storage**: Supabase (videos, audio)
- **ML Models**: Spacy, Whisper (built-in)

---

## STEP 1: Setup MongoDB Atlas (5 minutes)

1. Go to https://www.mongodb.com/cloud/atlas
2. Sign up with email
3. Create a free cluster:
   - Provider: AWS
   - Region: Closest to you
   - Cluster name: `signbridge`
4. Go to "Database Access" → Create user:
   - Username: `admin`
   - Password: Generate strong password (save it!)
5. Go to "Network Access" → Allow access from anywhere (0.0.0.0/0)
6. Click "Connect" → Copy connection string:
   ```
   mongodb+srv://admin:PASSWORD@cluster.mongodb.net/signbridge?retryWrites=true&w=majority
   ```
   Replace PASSWORD with your password

---

## STEP 2: Setup Supabase (5 minutes)

1. Go to https://supabase.com
2. Sign up with GitHub
3. Create new project:
   - Organization: Create new
   - Project name: `signbridge`
   - Database password: Generate strong (save it!)
   - Region: Closest to you
4. Wait for project to deploy (~2 min)
5. Go to Settings → API:
   - Copy `Project URL` (SUPABASE_URL)
   - Copy `anon public` key (SUPABASE_KEY)
6. Create storage buckets:
   - Go to Storage
   - New bucket: `sign_videos` (Public)
   - New bucket: `audio_uploads` (Public)
   - New bucket: `merged_videos` (Public)

---

## STEP 3: Setup GitHub (5 minutes)

1. Go to https://github.com and sign up
2. Create new repository:
   - Name: `signbridge`
   - Description: Sign Language Learning Platform
   - Public
3. Clone to your computer:
   ```bash
   git clone https://github.com/YOUR_USERNAME/signbridge.git
   cd signbridge
   ```

---

## STEP 4: Prepare Local Code (10 minutes)

1. Copy all project files to the cloned repo folder
2. Create `.env` file:
   ```
   MONGODB_URI=mongodb+srv://admin:PASSWORD@cluster.mongodb.net/signbridge?retryWrites=true&w=majority
   SUPABASE_URL=https://xxxxx.supabase.co
   SUPABASE_KEY=your-anon-key
   FLASK_ENV=production
   SECRET_KEY=generate-a-random-secret-key-here
   ```

3. Update requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Test locally:
   ```bash
   python app.py
   ```
   Visit: http://localhost:5000

---

## STEP 5: Push to GitHub (5 minutes)

```bash
git add .
git commit -m "Initial SignBridge deployment"
git branch -M main
git push -u origin main
```

---

## STEP 6: Deploy on Render (10 minutes)

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Web Service"
4. Select your `signbridge` repository
5. Configure:
   - Name: `signbridge`
   - Environment: Python 3
   - Build command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - Start command: `gunicorn app:app`
   - Plan: Free
6. Add Environment Variables:
   - `MONGODB_URI`: Your MongoDB connection string
   - `SUPABASE_URL`: Your Supabase URL
   - `SUPABASE_KEY`: Your Supabase key
   - `FLASK_ENV`: `production`
   - `SECRET_KEY`: Generate random string
7. Click "Create Web Service"
8. Wait for deployment (2-5 minutes)

---

## STEP 7: Test Your Deployment

1. Your app will be at: `https://signbridge.onrender.com`
2. Sign up and test:
   - Create account
   - Login
   - Upload audio
   - Convert to sign language
   - Upload videos

---

## Features That Work:
✅ User authentication (signup/login)
✅ Student/Teacher/Parent/Admin dashboards
✅ Audio upload & Whisper transcription
✅ Speech-to-sign conversion
✅ Video upload & storage
✅ Progress tracking
✅ Video merging
✅ Reports (PDF/CSV)

---

## Troubleshooting

**App won't deploy:**
- Check build logs in Render dashboard
- Ensure all environment variables are set
- Verify MongoDB connection string

**Videos not uploading:**
- Check Supabase bucket permissions
- Verify SUPABASE_KEY is correct
- Check Supabase storage limits

**Whisper model too large:**
- Use smaller model: `base` instead of `large`
- First deployment takes longer

**Cold start slow:**
- Normal on Render free tier
- Upgrade to paid plan for faster starts

---

## Next Steps:
1. Add custom domain
2. Setup SSL certificate
3. Monitor app performance
4. Scale to paid plan if needed

