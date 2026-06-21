# Sign Language Videos - Supabase Cloud Storage Setup

## Current Status ✅

Your app now supports serving videos from **Supabase Cloud Storage**. This allows:
- Unlimited video storage (doesn't count toward Render deployment limits)
- Faster video delivery globally
- Easy video management from Supabase dashboard
- Local fallback when videos aren't available in cloud

## Two Modes

### Mode 1: Supabase Cloud Storage (Production) 🚀
- Videos served from Supabase CDN
- Best for production deployments
- Requires valid Supabase credentials in `.env`

### Mode 2: Local Storage (Development) 💻
- Videos served from `/archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS/`
- Works without Supabase setup
- Current default mode

## Getting Your Supabase Credentials

### Step 1: Go to Supabase Dashboard
https://supabase.com → Log in → Select your project

### Step 2: Navigate to Settings → API
You'll find:
- **Project URL**: `https://xxxx.supabase.co`
- **Service Role Secret**: Long key starting with `eyJhb...`
- **Anon Public**: Different key

### Step 3: Create Storage Bucket
1. Go to **Storage** → **Create bucket**
2. Name: `sign-videos`
3. Enable **Public** access
4. Click **Create**

### Step 4: Update .env File
```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Step 5: Upload Videos (3 Options)

**Option A: Python Script**
```bash
python upload_videos_to_supabase.py
```

**Option B: Supabase UI**
- Go to Storage → sign-videos
- Manually upload folders and files

**Option C: Supabase CLI**
```bash
npm install -g supabase
supabase storage upload -r sign-videos/animations/ "archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS/"
```

## Video Organization in Supabase

After uploading, structure should be:
```
sign-videos/
├── animations/        (156+ sign videos)
│   ├── HELLO.mp4
│   ├── THANK.mp4
│   └── ...
├── learning/          (Alphabet videos A-Z, 0-9)
│   ├── A.mp4
│   └── ...
└── uploads/           (Teacher uploaded videos)
    ├── teacher_xxx.mp4
    └── ...
```

## Deployment to Render

1. Add Supabase credentials to Render environment:
   - Go to Render Dashboard → signbridge service
   - Settings → Environment
   - Add: `SUPABASE_URL` and `SUPABASE_KEY`

2. Push to GitHub:
   ```bash
   git add -A
   git commit -m "Configure Supabase credentials"
   git push origin main
   ```

3. Render will auto-redeploy with new variables

## How Videos Are Served

**User requests video:**
```
1. Request: /sign_videos/HELLO.mp4
2. App checks: Is Supabase available?
   → YES: Redirect to Supabase CDN URL
   → NO: Serve from local storage (fallback)
```

## Testing Locally

```bash
python app.py
```

Then visit:
- http://localhost:5000/animations/HELLO.mp4 (will use local storage)
- http://localhost:5000/learning_videos/A.mp4 (will use local storage)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Invalid API key` | Use Service Role Secret, not Anon Public key |
| `Bucket not found` | Ensure bucket name is lowercase: `sign-videos` |
| `Permission denied` | Check bucket is set to Public |
| Videos still local | Supabase credentials invalid, using local fallback |
| Render deployment fails | Add `SUPABASE_URL` and `SUPABASE_KEY` to environment |

## Files Modified

- `app.py` - Added Supabase integration
- `requirements.txt` - Added `supabase==2.4.1`
- `.env` - Updated with Supabase URL
- `.env.example` - Template for configuration
- `upload_videos_to_supabase.py` - Batch upload script (new)

## Benefits

✅ Videos don't count toward Render storage limits
✅ Faster global CDN delivery
✅ Automatic fallback to local storage
✅ Easy management from Supabase dashboard
✅ Scalable as you add more videos
✅ Works with multiple regional deployments
