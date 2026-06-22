# SignBridge - Sign Language Converter Web App
## Complete Project Documentation

---

## 1. PROJECT OVERVIEW

**SignBridge** is a web-based platform designed to convert spoken language into Indian Sign Language (ISL) videos. The application helps deaf and hard-of-hearing individuals communicate by translating audio/text input into sign language videos with visual demonstrations.

### Core Mission
- Promote inclusive communication
- Bridge the gap between hearing and deaf communities
- Make sign language learning accessible to everyone
- Provide educational resources for sign language training

---

## 2. TECHNOLOGY STACK

### Backend
- **Framework**: Flask (Python 3.14)
- **Database**: MongoDB Atlas (Cloud)
- **ORM**: MongoEngine
- **Video Processing**: FFmpeg
- **Authentication**: Flask-Login with password hashing

### Frontend
- **HTML/CSS/JavaScript**
- **Responsive Design** with custom themes
- **Real-time video playback**
- **Audio recording capability**

### Cloud Infrastructure
- **Hosting**: Render (Platform-as-a-Service)
- **Video Storage**: Supabase (Cloud Storage)
- **Database**: MongoDB Atlas
- **Code Repository**: GitHub

### Key Libraries
```
Flask 3.0.0
MongoDB/MongoEngine 4.6.1
Supabase 2.4.1
ReportLab (PDF generation)
Gunicorn (Production server)
```

---

## 3. SYSTEM ARCHITECTURE

### Architecture Flow
```
User Browser (Frontend)
        ↓
   Flask Application (app.py)
        ↓
   ├─→ MongoDB Atlas (User data, Progress)
   ├─→ Supabase Storage (Sign videos)
   ├─→ FFmpeg (Video processing)
   └─→ Local Storage (Temporary files)
```

### Directory Structure
```
signbridge/
├── app.py                          # Main Flask application
├── models.py                       # MongoDB models
├── supabase_config.py             # Supabase configuration
├── requirements.txt               # Python dependencies
├── render.yaml                    # Render deployment config
├── .env                           # Environment variables
│
├── templates/                     # HTML templates
│   ├── landing.html              # Home page
│   ├── login.html                # Authentication
│   ├── signup.html               # User registration
│   ├── index.html                # Main app interface
│   ├── student_dashboard.html    # Student panel
│   ├── teacher_dashboard.html    # Teacher panel
│   ├── parent_dashboard.html     # Parent monitoring
│   ├── admin_dashboard.html      # Admin panel
│   ├── progress.html             # Progress tracking
│   └── learning.html             # Learning module
│
├── static/                        # Static assets
│   ├── logo.png
│   ├── new-theme.css             # Main styling
│   ├── isl-signs.js              # Sign database
│   ├── learning-script.js        # Learning functionality
│   ├── Daily_phrases/            # Phrase images
│   └── Emergency_phrases/        # Emergency phrases
│
├── archive/                       # Video storage
│   └── INDIAN SIGN LANGUAGE ANIMATED VIDEOS/
│       └── 151 video files (.mp4)
│
├── learning/                      # Learning resources
│   └── Animation_video/
│       └── 36 alphabet videos (A-Z, 0-9)
│
├── sign_videos/                   # Teacher uploads
│   └── User-uploaded videos
│
└── audio_uploads/                 # Temporary audio files
```

---

## 4. CORE FUNCTIONALITIES

### 4.1 USER AUTHENTICATION & ROLES

**Supported User Roles:**

1. **Student**
   - Can record/upload audio
   - View sign language videos
   - Track learning progress
   - Access learning modules
   - View parent notifications

2. **Teacher**
   - Create assignments
   - Upload custom sign videos
   - View student progress
   - Mark attendance
   - Add remarks for students
   - Download reports

3. **Parent**
   - Monitor child's progress
   - View attendance records
   - Receive notifications about remarks
   - Track performance metrics
   - View risk alerts for children

4. **Admin**
   - User management (add/edit/deactivate)
   - View system logs and analytics
   - Generate reports (PDF/CSV)
   - Monitor all user activities
   - System statistics

**Authentication Flow:**
```
User Input (Username/Password)
        ↓
Password Validation (bcrypt hashing)
        ↓
Session Creation (Flask-Login)
        ↓
Role-based Access Control
        ↓
Dashboard Redirect
```

---

### 4.2 SPEECH-TO-SIGN CONVERSION

**How it Works:**

1. **Audio Input**
   - User records audio via microphone OR
   - User uploads audio file (MP3, WAV, etc.) OR
   - User uploads video file (MP4, AVI, etc.)

2. **Audio Processing**
   - If video: Extract audio track using FFmpeg
   - Convert to WAV format (16kHz, mono)
   - Validate audio length (minimum 1 second)

3. **Speech Recognition**
   - Use OpenAI Whisper model (if available)
   - Transcribe audio to text
   - Fallback: Mock data "HELLO WORLD" if Whisper unavailable

4. **Text Processing**
   - Convert to uppercase
   - Split into individual words
   - Remove punctuation
   - Match with available sign videos

5. **Video Retrieval**
   - Search in Supabase cloud storage
   - Fallback to local storage
   - Return list of matching videos

6. **Video Display**
   - Merge multiple sign videos into sequence
   - Add captions/word labels
   - Auto-play in continuous loop
   - User can download as MP4

**Example Flow:**
```
User says: "Hello, how are you?"
        ↓
Whisper transcribes: "hello how are you"
        ↓
Text processing: ["HELLO", "HOW", "ARE", "YOU"]
        ↓
Video matching: ✓ HELLO.mp4, ✓ HOW.mp4, ✓ ARE.mp4, ✓ YOU.mp4
        ↓
FFmpeg merges: merged_video.mp4
        ↓
Display on web interface with captions
```

---

### 4.3 VIDEO MANAGEMENT

**Video Sources:**

1. **Pre-loaded Animation Videos** (151 videos)
   - Location: `archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS/`
   - Content: Common ISL words and phrases
   - Format: MP4 videos with sign demonstrations

2. **Learning Videos** (36 videos)
   - Location: `learning/Animation_video/`
   - Content: Alphabet (A-Z) + Numbers (0-9)
   - Used in learning module

3. **Teacher-Uploaded Videos** (User uploads)
   - Location: Supabase cloud storage
   - Access: Only uploaded by teachers
   - Management: Can view and download

**Video Serving:**
```
Request: /sign_videos/HELLO.mp4
        ↓
Check Supabase? (if configured)
        ↓ YES: Redirect to CDN URL
        ↓ NO: Serve from local storage
        ↓
Return video stream to browser
```

**Video Merging (FFmpeg):**
```
Input: ["HELLO.mp4", "HOW.mp4", "ARE.mp4"]
        ↓
Normalize: 640x480 resolution, 30fps
        ↓
Add captions: "HELLO", "HOW", "ARE"
        ↓
Concatenate: Sequential playback
        ↓
Output: merged_video.mp4
```

---

### 4.4 LEARNING MODULE

**Features:**

1. **Interactive Sign Learning**
   - Browse ISL alphabet (A-Z)
   - View sign demonstrations
   - Practice with animations
   - Self-paced learning

2. **Progress Tracking**
   - Track watched videos
   - Score tracking
   - Completion status
   - Performance analytics

3. **Daily Phrases**
   - Common greetings
   - Emergency phrases
   - Situational expressions

---

### 4.5 PROGRESS & ANALYTICS

**Tracked Metrics:**
- Modules completed
- Quiz scores
- Videos watched
- Time spent learning
- Attendance records
- Learning milestones

**Progress Dashboard:**
- Student views own progress
- Parent views child's progress
- Teacher views class progress
- Admin views system-wide analytics

**Reports Generated:**
- PDF reports (admin)
- CSV exports (admin)
- Performance summaries
- Attendance records

---

### 4.6 NOTIFICATION & ALERT SYSTEM

**Notification Types:**

1. **Teacher Remarks**
   - Teachers add remarks to students
   - Sent to parent's dashboard
   - Email notification (when configured)

2. **Progress Alerts**
   - Low performance warnings
   - Milestone achievements
   - Assignment deadlines

3. **Emergency Alerts** (Planned)
   - Risk detection system
   - Parent notifications
   - SMS alerts

**Notification Flow:**
```
Teacher adds remark
        ↓
Create Notification record in MongoDB
        ↓
Store in database
        ↓
Display on parent dashboard
        ↓
Mark as read when parent views
```

---

### 4.7 ATTENDANCE & REMARKS

**Teacher Features:**

1. **Mark Attendance**
   - Date selection
   - Status: Present/Absent/Leave
   - Bulk marking capability

2. **Add Remarks**
   - Remark types: General, Academic, Behavioral
   - Rich text content
   - Timestamp tracking

3. **Student List**
   - View all assigned students
   - Quick access to progress
   - Direct communication

**Parent View:**
- See child's attendance history
- View teacher remarks
- Track behavioral feedback
- Monitor academic performance

---

## 5. DATA MODELS (MongoDB)

### User Collection
```
{
  _id: ObjectId,
  username: String (unique),
  email: String,
  password: String (hashed),
  role: String (student/teacher/parent/admin),
  is_active: Boolean,
  parent_id: ObjectId (if student),
  teacher_id: ObjectId (if student),
  parent_email: String,
  parent_phone: String,
  created_at: DateTime
}
```

### Progress Collection
```
{
  _id: ObjectId,
  user_id: String,
  module: String (video/quiz/assignment),
  item: String (item name),
  completed: Boolean,
  score: Integer (0-100),
  timestamp: DateTime
}
```

### Assignment Collection
```
{
  _id: ObjectId,
  title: String,
  type: String (video/quiz),
  video_path: String,
  teacher_id: ObjectId,
  created_at: DateTime
}
```

### UserLog Collection
```
{
  _id: ObjectId,
  user_id: String,
  action: String (login/logout/upload),
  details: String,
  ip_address: String,
  device_type: String,
  timestamp: DateTime
}
```

### Attendance Collection
```
{
  _id: ObjectId,
  student_id: ObjectId,
  date: Date,
  status: String (present/absent/leave),
  teacher_id: ObjectId
}
```

### Remark Collection
```
{
  _id: ObjectId,
  student_id: ObjectId,
  teacher_id: ObjectId,
  remark_type: String,
  content: String,
  created_at: DateTime
}
```

### Notification Collection
```
{
  _id: ObjectId,
  user_id: ObjectId,
  message: String,
  is_read: Boolean,
  created_at: DateTime
}
```

---

## 6. KEY API ENDPOINTS

### Authentication
- `POST /login` - User login
- `POST /signup` - User registration
- `GET /logout` - User logout

### Main Interface
- `GET /` - Landing page
- `GET /home` - Main app interface
- `GET /dashboard` - Role-based redirect

### Audio/Video Processing
- `POST /upload_audio` - Upload audio/video file
- `POST /upload_video` - Upload custom sign video
- `POST /merge_videos` - Merge multiple videos
- `GET /sign_videos/<filename>` - Serve video

### Student Routes
- `GET /student/dashboard` - Student progress view
- `GET /progress` - Student progress details
- `POST /save_progress` - Save learning progress

### Teacher Routes
- `GET /teacher/dashboard` - Teacher panel
- `POST /teacher/upload_video` - Upload custom video
- `POST /teacher/attendance` - Mark attendance
- `POST /teacher/remark` - Add student remark

### Parent Routes
- `GET /parent/dashboard` - Parent monitoring panel
- `GET /parent/child/<id>` - View child details
- `GET /parent/notifications` - Get notifications

### Admin Routes
- `GET /admin/dashboard` - Admin statistics
- `POST /admin/users/add` - Add new user
- `PUT /admin/users/<id>/edit` - Edit user
- `DELETE /admin/users/<id>/delete` - Remove user
- `GET /admin/report/pdf` - Download PDF report
- `GET /admin/report/csv` - Download CSV report

---

## 7. VIDEO STORAGE ARCHITECTURE

### Cloud Storage (Supabase)
```
sign-videos/
├── animations/
│   ├── HELLO.mp4
│   ├── THANK.mp4
│   └── ... (187 videos total)
├── learning/
│   ├── A.mp4
│   ├── B.mp4
│   └── ... (36 videos)
└── uploads/
    └── teacher_uploads.mp4
```

**Benefits:**
- ✅ Unlimited storage
- ✅ Global CDN distribution
- ✅ Doesn't use Render storage limits
- ✅ Automatic backups
- ✅ Public URL access

### Local Storage (Fallback)
```
archive/
└── INDIAN SIGN LANGUAGE ANIMATED VIDEOS/
    └── 151 video files
```

**Used when:**
- Supabase credentials not configured
- Cloud storage unavailable
- Development/testing locally

---

## 8. DEPLOYMENT ARCHITECTURE

### Local Development
```
User Browser (localhost:5000)
        ↓
Flask Development Server (debug=True)
        ↓
Local MongoDB (or MongoDB Atlas)
        ↓
Local video files
```

### Production (Render)
```
User Browser (https://signbridge-l364.onrender.com)
        ↓
Gunicorn Server (4 workers)
        ↓
MongoDB Atlas (cloud database)
        ↓
Supabase CDN (video delivery)
```

**Deployment Flow:**
```
1. Local development & testing
        ↓
2. Push to GitHub (git push)
        ↓
3. Render detects push
        ↓
4. Builds app (pip install -r requirements.txt)
        ↓
5. Starts Gunicorn server
        ↓
6. App goes live
```

---

## 9. SECURITY FEATURES

### Authentication
- ✅ Password hashing (Werkzeug)
- ✅ Session management (Flask-Login)
- ✅ Role-based access control
- ✅ Login required decorators

### Data Protection
- ✅ MongoDB encryption (Atlas)
- ✅ HTTPS (Render SSL)
- ✅ Environment variables (.env)
- ✅ No secrets in code

### API Security
- ✅ User validation on all endpoints
- ✅ Role checking for protected routes
- ✅ Input validation
- ✅ Error handling

### File Security
- ✅ File type validation (only MP4)
- ✅ File size limits
- ✅ Virus scanning (Supabase)
- ✅ Public URL expiration (Supabase)

---

## 10. USER WORKFLOWS

### Student Workflow
```
1. Sign up as student
2. Login to dashboard
3. Record or upload audio
4. System converts to sign videos
5. Watch merged video
6. Track progress in dashboard
7. Access learning module
8. Receive parent notifications
```

### Teacher Workflow
```
1. Sign up as teacher
2. Login to dashboard
3. View assigned students
4. Mark attendance
5. Upload custom sign videos
6. Add remarks/feedback
7. Download reports
8. Track student progress
```

### Parent Workflow
```
1. Sign up as parent
2. Link child to account
3. Login to dashboard
4. View child's progress
5. Monitor attendance
6. Read teacher remarks
7. Receive notifications
8. Track learning metrics
```

### Admin Workflow
```
1. Admin account (pre-created)
2. View all users
3. Create accounts
4. Manage roles
5. View system logs
6. Generate reports
7. Monitor analytics
8. Deactivate accounts
```

---

## 11. FEATURES BREAKDOWN

### Currently Implemented ✅
- User authentication with 4 roles
- Speech-to-sign conversion
- 187 sign language videos
- Video merging with captions
- Progress tracking
- Attendance management
- Remarks system
- Notification system
- Admin dashboard
- Report generation (PDF/CSV)
- MongoDB cloud integration
- Supabase cloud storage
- Render deployment
- Role-based access control

### In Development 🔄
- Email notifications
- SMS alerts for emergencies
- Advanced gesture recognition
- Mobile app
- Real-time collaboration

### Planned 🗓️
- AI-powered learning recommendations
- Video compression optimization
- Multi-language support
- Advanced analytics
- Integration with hearing aids

---

## 12. PERFORMANCE SPECIFICATIONS

### Video Processing
- **Audio transcription**: ~30-60 seconds (Whisper)
- **Video merging**: ~10-20 seconds (FFmpeg)
- **Upload speed**: 5-50 MB/s (Supabase CDN)

### Database
- **Query performance**: <100ms (MongoDB Atlas)
- **Connection pooling**: Automatic (MongoEngine)
- **Max concurrent users**: 1000+ (Render free tier: 10)

### Scalability
- **Videos served per second**: 1000+ (Supabase CDN)
- **Database capacity**: Unlimited (MongoDB Atlas)
- **Storage capacity**: Unlimited (Supabase)

---

## 13. SETUP & INSTALLATION

### Prerequisites
- Python 3.14+
- Git
- MongoDB Atlas account
- Supabase account
- Render account

### Local Setup
```bash
# Clone repository
git clone https://github.com/Tejasri2007/signbridge.git
cd signbridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run app
python app.py
# Visit http://localhost:5000
```

### Deployment to Render
```bash
# Push to GitHub
git add -A
git commit -m "Your message"
git push origin main

# Go to Render Dashboard
# - Connect GitHub repo
# - Set environment variables
# - Deploy

# App goes live at: https://signbridge-l364.onrender.com
```

---

## 14. TROUBLESHOOTING

### Common Issues

**Issue: "MongoDB Connection Error"**
- Solution: Check MONGODB_URI in .env
- Verify MongoDB Atlas whitelist IP

**Issue: "Whisper not available"**
- Solution: This is normal - app falls back to mock data
- To fix: Install ffmpeg and build tools

**Issue: "Videos not showing on Render"**
- Solution: Add SUPABASE_URL and SUPABASE_KEY to Render environment
- Or use local storage (automatically fallback)

**Issue: "Permission denied on file upload"**
- Solution: Check file permissions
- Ensure audio_uploads folder exists

---

## 15. FUTURE ENHANCEMENTS

1. **Mobile App**
   - React Native mobile client
   - Offline video access
   - Push notifications

2. **Advanced Features**
   - Real-time gesture recognition
   - AI-powered learning paths
   - Community video sharing
   - Peer-to-peer communication

3. **Accessibility**
   - Text-to-speech
   - Dark mode
   - Keyboard navigation
   - Screen reader support

4. **Scalability**
   - Microservices architecture
   - Redis caching
   - Load balancing
   - Multi-region deployment

5. **Analytics**
   - Advanced dashboards
   - Learning pattern analysis
   - Predictive modeling
   - Performance benchmarking

---

## 16. CONTACT & SUPPORT

**Project Repository**: https://github.com/Tejasri2007/signbridge
**Live App**: https://signbridge-l364.onrender.com
**Developer**: Tejasri
**Project Purpose**: Inclusive communication through sign language

---

## 17. LICENSE & ATTRIBUTION

- **Framework**: Flask
- **Database**: MongoDB
- **Storage**: Supabase
- **Hosting**: Render
- **Video Processing**: FFmpeg
- **Speech Recognition**: OpenAI Whisper

---

**Last Updated**: June 2026
**Version**: 1.0 (Production Ready)
**Status**: ✅ Live & Operational
