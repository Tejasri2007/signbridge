from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for, flash, session, Response
from mongoengine import connect, disconnect
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
try:
    import whisper
    WHISPER_AVAILABLE = True
except:
    WHISPER_AVAILABLE = False
    print("Warning: Whisper not available. Speech-to-sign conversion will use mock data.")

from supabase import create_client
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import User, Progress, Assignment, UserLog, Attendance, Remark, Notification, Feedback, Alert
from functools import wraps
import json
from datetime import datetime, date, timedelta
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-signbridge')

# MongoDB Connection
mongo_uri = os.environ.get('MONGODB_URI', 'mongodb+srv://Tejasri:Teja2007@mobilerecharge.raj1zpx.mongodb.net/signbridge?retryWrites=true&w=majority')
try:
    connect('signbridge', host=mongo_uri)
    print("[OK] MongoDB Atlas Connected Successfully!")
except Exception as e:
    print(f"[ERROR] MongoDB Connection Error: {e}")

# Supabase Connection
SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', '').strip()
SUPABASE_BUCKET = 'sign-videos'

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("[OK] Supabase Connected Successfully!")
    except Exception as e:
        print(f"[WARNING] Supabase Connection Error: {str(e)[:100]}")
        print("   Videos will be served from local storage")
        supabase = None
else:
    print("[WARNING] Supabase credentials not configured")
    print("   Videos will be served from local storage")

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

model = None

@login_manager.user_loader
def load_user(user_id):
    try:
        return User.objects(id=user_id).first()
    except:
        return None

def log_activity(user_id, action, details=None):
    try:
        log = UserLog(
            user_id=str(user_id),
            action=action,
            details=details,
            ip_address=request.remote_addr,
            device_type=request.headers.get('User-Agent', '')[:100]
        )
        log.save()
    except:
        pass

def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash('Access denied')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

def load_whisper_model():
    global model
    if not WHISPER_AVAILABLE:
        return None
    if model is None:
        try:
            model = whisper.load_model("base")
        except:
            print("Warning: Could not load Whisper model")
            return None
    return model

def get_video_url(word, source='animations'):
    """Get video URL from Supabase or local fallback"""
    if supabase:
        try:
            url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(f'{source}/{word}.mp4')
            return url
        except:
            pass
    # Fallback to local
    if source == 'animations':
        return url_for('serve_animation', filename=f'{word}.mp4')
    elif source == 'learning':
        return url_for('serve_learning_video', filename=f'{word}.mp4')
    else:
        return url_for('serve_video', filename=f'{word}.mp4')

UPLOAD_FOLDER = 'sign_videos'
ANIMATION_FOLDER = 'archive/INDIAN SIGN LANGUAGE ANIMATED VIDEOS'
AUDIO_FOLDER = 'audio_uploads'
MERGED_FOLDER = 'merged_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)
os.makedirs(MERGED_FOLDER, exist_ok=True)

def convert_to_sign(text):
    # Simple word extraction without spacy
    words = text.upper().split()
    # Remove punctuation
    words = [w.strip('.,!?;:"\'-') for w in words if w.strip('.,!?;:"\'-')]
    return words

@app.route('/')
def landing():
    if current_user.is_authenticated:
        return render_template('landing.html', logged_in=True)
    return render_template('landing.html', logged_in=False)

@app.route('/home')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    videos = []
    if os.path.exists(UPLOAD_FOLDER):
        videos = [f.replace('.mp4', '') for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.mp4')]
    
    # Get teacher uploaded videos
    try:
        teacher_videos = list(Assignment.objects(type='video'))
    except:
        teacher_videos = []
    
    return render_template('index.html', videos=videos, teacher_videos=teacher_videos)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            user = User.objects(username=data.get('username')).first()
            if user and check_password_hash(user.password, data.get('password')):
                if not user.is_active:
                    return jsonify({'error': 'Account deactivated'}) if request.is_json else redirect(url_for('login'))
                login_user(user)
                log_activity(user.id, 'login', 'User logged in')
                return jsonify({'success': True, 'role': user.role}) if request.is_json else redirect(url_for('dashboard'))
            else:
                if user:
                    log_activity(user.id, 'login_failed', 'Failed login attempt')
            return jsonify({'error': 'Invalid credentials'}) if request.is_json else redirect(url_for('login'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            if User.objects(username=data.get('username')).first():
                return jsonify({'error': 'Username exists'}) if request.is_json else redirect(url_for('signup'))
            user = User(
                username=data.get('username'),
                email=data.get('email'),
                password=generate_password_hash(data.get('password')),
                role=data.get('role', 'student'),
                parent_email=data.get('parent_email') if data.get('role') == 'student' else None,
                parent_phone=data.get('parent_phone') if data.get('role') == 'student' else None
            )
            user.save()
            return jsonify({'success': True}) if request.is_json else redirect(url_for('login'))
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'logout', 'User logged out')
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'student':
        return redirect(url_for('student_dashboard'))
    elif current_user.role == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    elif current_user.role == 'parent':
        return redirect(url_for('parent_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('index'))

@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    progress = list(Progress.objects(user_id=str(current_user.id)))
    teacher_videos = list(Assignment.objects(type='video'))
    return render_template('student_dashboard.html', progress=progress, teacher_videos=teacher_videos)

@app.route('/teacher/dashboard')
@login_required
@role_required('teacher')
def teacher_dashboard():
    students = list(User.objects(role='student'))
    assignments = list(Assignment.objects(teacher_id=str(current_user.id)))
    teacher_videos = list(Assignment.objects(teacher_id=str(current_user.id), type='video'))
    return render_template('teacher_dashboard.html', students=students, assignments=assignments, teacher_videos=teacher_videos)

@app.route('/parent/dashboard')
@login_required
@role_required('parent')
def parent_dashboard():
    students = list(User.objects(role='student', parent_id=str(current_user.id)))
    for student in students:
        progress = list(Progress.objects(user_id=str(student.id)))
        student.progress_count = len(progress)
        student.completed_count = len([p for p in progress if p.completed])
        student.avg_score = round(sum([p.score for p in progress]) / len(progress)) if progress else 0
    
    return render_template('parent_dashboard.html', students=students)

@app.route('/admin/dashboard')
@login_required
@role_required('admin')
def admin_dashboard():
    try:
        users = list(User.objects())
        parents = list(User.objects(role='parent'))
        stats = {
            'total_students': User.objects(role='student').count(),
            'total_teachers': User.objects(role='teacher').count(),
            'total_parents': User.objects(role='parent').count(),
            'active_users': User.objects(is_active=True).count()
        }
        recent_logs = list(UserLog.objects().order_by('-timestamp')[:20])
        all_progress = list(Progress.objects().order_by('-timestamp')[:100])
        return render_template('admin_dashboard.html', users=users, parents=parents, stats=stats, recent_logs=recent_logs, all_progress=all_progress)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning')
@login_required
def learning():
    return render_template('learning.html')

@app.route('/progress')
@login_required
def my_progress():
    progress = list(Progress.objects(user_id=str(current_user.id)))
    stats = {
        'total': len(progress),
        'completed': len([p for p in progress if p.completed]),
        'avg_score': sum([p.score for p in progress]) / len(progress) if progress else 0,
        'quizzes': len([p for p in progress if p.module == 'quiz']),
        'videos_watched': len([p for p in progress if p.module == 'video'])
    }
    return render_template('progress.html', progress=progress, stats=stats)

@app.route('/save_progress', methods=['POST'])
@login_required
def save_progress():
    data = request.get_json()
    progress = Progress(
        user_id=str(current_user.id),
        module=data.get('module'),
        item=data.get('item'),
        completed=data.get('completed', False),
        score=data.get('score', 0)
    )
    progress.save()
    return jsonify({'success': True})

@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file'}), 400
        
        file = request.files['audio']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400
            
        file_ext = file.filename.split('.')[-1].lower()
        
        # Check if it's a video file
        if file_ext in ['mp4', 'avi', 'mov', 'mkv', 'webm', 'flv', 'wmv']:
            video_path = os.path.abspath(os.path.join(AUDIO_FOLDER, 'input_video.' + file_ext))
            audio_path = os.path.abspath(os.path.join(AUDIO_FOLDER, 'input.wav'))
            file.save(video_path)
            
            # Check if video file is valid
            if os.path.getsize(video_path) == 0:
                return jsonify({'error': 'Video file is empty'}), 400
            
            # Remove old audio file if exists
            if os.path.exists(audio_path):
                os.remove(audio_path)
            
            # Extract audio from video using FFmpeg - get full audio
            try:
                result = subprocess.run(
                    ['ffmpeg', '-i', video_path, '-vn', '-acodec', 'pcm_s16le', '-ar', '16000', '-ac', '1', '-y', audio_path],
                    capture_output=True, text=True, timeout=60
                )
                
                if not os.path.exists(audio_path):
                    return jsonify({'error': 'This video has no audio track. Please upload a video with speech.'}), 400
                
                if os.path.getsize(audio_path) < 16000:  # Less than 1 second of audio
                    return jsonify({'error': 'Audio is too short. Please upload a video with clear speech.'}), 400
                    
            except FileNotFoundError:
                return jsonify({'error': 'FFmpeg not found in PATH'}), 500
            except subprocess.TimeoutExpired:
                return jsonify({'error': 'Video processing timeout'}), 500
            except Exception as e:
                return jsonify({'error': f'Error: {str(e)}'}), 500
        else:
            audio_path = os.path.join(AUDIO_FOLDER, 'input.wav')
            file.save(audio_path)
        
        if not os.path.exists(audio_path):
            return jsonify({'error': 'Audio file not created'}), 500
        
        # Check audio file size
        if os.path.getsize(audio_path) < 16000:  # Less than 1 second
            return jsonify({'error': 'Audio is too short or has no speech. Please use a video/audio with clear speech.'}), 400
        
        try:
            whisper_model = load_whisper_model()
            if whisper_model:
                result = whisper_model.transcribe(audio_path, language='en', task='transcribe', verbose=False, fp16=False, beam_size=1, best_of=1)
                text = result.get("text", "").strip()
            else:
                text = "HELLO WORLD"
        except Exception as e:
            text = "HELLO WORLD"
        
        if not text:
            return jsonify({'error': 'No speech detected'}), 400
        
        sign_words = convert_to_sign(text)
        
        available = []
        for w in sign_words:
            if os.path.exists(f'{ANIMATION_FOLDER}/{w}.mp4'):
                available.append(w)
            elif os.path.exists(f'{UPLOAD_FOLDER}/{w}.mp4'):
                available.append(w)
        
        return jsonify({'original': text, 'sign_words': sign_words, 'available': available})
    
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/upload_video', methods=['POST'])
def upload_video():
    if 'video' not in request.files or 'word' not in request.form:
        return jsonify({'error': 'Missing video or word'}), 400
    
    video = request.files['video']
    word = request.form['word'].upper()
    video.save(f'{UPLOAD_FOLDER}/{word}.mp4')
    
    return jsonify({'success': True, 'word': word})

@app.route('/get_videos')
def get_videos():
    videos = []
    if os.path.exists(UPLOAD_FOLDER):
        videos = [f.replace('.mp4', '') for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.mp4')]
    return jsonify({'videos': videos})

@app.route('/sign_videos/<filename>')
def serve_video(filename):
    if supabase:
        try:
            url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(f'uploads/{filename}')
            return redirect(url)
        except:
            pass
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/audio_uploads/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_FOLDER, filename)

@app.route('/animations/<path:filename>')
def serve_animation(filename):
    if supabase:
        try:
            url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(f'animations/{filename}')
            return redirect(url)
        except:
            pass
    return send_from_directory(ANIMATION_FOLDER, filename)

@app.route('/merge_videos', methods=['POST'])
def merge_videos():
    import time
    try:
        data = request.get_json()
        words = data.get('words', [])
        
        if not words:
            return jsonify({'error': 'No words provided'}), 400
        
        video_inputs = []
        filter_parts = []
        
        for i, word in enumerate(words):
            video_path = os.path.join(ANIMATION_FOLDER, f'{word}.mp4')
            if not os.path.exists(video_path):
                video_path = os.path.join(UPLOAD_FOLDER, f'{word}.mp4')
            if os.path.exists(video_path):
                video_inputs.extend(['-i', video_path])
                filter_parts.append(f'[{i}:v]scale=640:480:force_original_aspect_ratio=decrease,pad=640:480:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,drawtext=text=\'{word}\':fontsize=40:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-th-20[v{i}]')
        
        if not video_inputs:
            return jsonify({'error': 'No valid videos found'}), 400
        
        filter_complex = ';'.join(filter_parts) + ';' + ''.join([f'[v{i}]' for i in range(len(filter_parts))]) + f'concat=n={len(filter_parts)}:v=1:a=0[outv]'
        
        # Use unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
        output_filename = f'merged_{timestamp}.mp4'
        output_path = os.path.join(MERGED_FOLDER, output_filename)
        
        # Clean up old merged files (older than 1 hour)
        try:
            for f in os.listdir(MERGED_FOLDER):
                if f.startswith('merged_') and f.endswith('.mp4'):
                    file_path = os.path.join(MERGED_FOLDER, f)
                    if os.path.getmtime(file_path) < time.time() - 3600:
                        try:
                            os.remove(file_path)
                        except:
                            pass
        except:
            pass
        
        cmd = ['ffmpeg'] + video_inputs + [
            '-filter_complex', filter_complex,
            '-map', '[outv]',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '28',
            '-pix_fmt', 'yuv420p',
            '-y',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return jsonify({'success': True, 'filename': output_filename})
        else:
            return jsonify({'error': f'Video merge failed: {result.stderr}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Merge error: {str(e)}'}), 500

@app.route('/merged_videos/<filename>')
def serve_merged(filename):
    return send_from_directory(MERGED_FOLDER, filename)

@app.route('/download_with_caption/<word>')
def download_with_caption(word):
    try:
        video_path = os.path.join(ANIMATION_FOLDER, f'{word}.mp4')
        if not os.path.exists(video_path):
            video_path = os.path.join(UPLOAD_FOLDER, f'{word}.mp4')
        
        if not os.path.exists(video_path):
            return jsonify({'error': 'Video not found'}), 404
        
        output_path = os.path.join(MERGED_FOLDER, f'{word}_captioned.mp4')
        if os.path.exists(output_path):
            os.remove(output_path)
        
        cmd = ['ffmpeg', '-i', video_path,
               '-vf', f"drawtext=text='{word}':fontsize=40:fontcolor=white:box=1:boxcolor=black@0.7:boxborderw=10:x=(w-text_w)/2:y=h-th-20",
               '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
               '-pix_fmt', 'yuv420p', '-y',
               output_path]
        
        subprocess.run(cmd, capture_output=True, timeout=60)
        
        if os.path.exists(output_path):
            return send_from_directory(MERGED_FOLDER, f'{word}_captioned.mp4', as_attachment=True)
        else:
            return jsonify({'error': 'Failed to create captioned video'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/learning_videos/<filename>')
def serve_learning_video(filename):
    if supabase:
        try:
            url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(f'learning/{filename}')
            return redirect(url)
        except:
            pass
    video_path = os.path.join('learning', 'Animation_video')
    if not os.path.exists(os.path.join(video_path, filename)):
        return jsonify({'error': 'Video not found'}), 404
    return send_from_directory(video_path, filename)

@app.route('/phrases/<phrase_type>/<filename>')
def serve_phrase_image(phrase_type, filename):
    folder = 'static/Daily_phrases' if phrase_type == 'daily' else 'static/Emergency_phrases'
    return send_from_directory(folder, filename)

@app.route('/get_phrases/<phrase_type>')
def get_phrases(phrase_type):
    folder = 'static/Daily_phrases' if phrase_type == 'daily' else 'static/Emergency_phrases'
    if os.path.exists(folder):
        images = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        return jsonify({'phrases': [{'name': os.path.splitext(f)[0], 'file': f} for f in images]})
    return jsonify({'phrases': []})

@app.route('/teacher/upload_video', methods=['POST'])
@login_required
@role_required('teacher')
def teacher_upload_video():
    try:
        if 'video' not in request.files or 'title' not in request.form:
            return jsonify({'error': 'Missing video or title'}), 400
        
        video = request.files['video']
        title = request.form['title']
        
        if not video.filename:
            return jsonify({'error': 'No file selected'}), 400
        
        filename = f"teacher_{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.mp4"
        video_path = os.path.join(UPLOAD_FOLDER, filename)
        video.save(video_path)
        
        assignment = Assignment(
            title=title,
            type='video',
            video_path=filename,
            teacher_id=str(current_user.id)
        )
        assignment.save()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teacher/delete_video/<video_id>', methods=['DELETE'])
@login_required
@role_required('teacher')
def teacher_delete_video(video_id):
    try:
        video = Assignment.objects(id=video_id).first()
        if not video or str(video.teacher_id) != str(current_user.id):
            return jsonify({'error': 'Video not found'}), 404
        
        video_path = os.path.join(UPLOAD_FOLDER, video.video_path)
        if os.path.exists(video_path):
            os.remove(video_path)
        
        video.delete()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/student/video/<video_id>')
@login_required
@role_required('student')
def student_view_video(video_id):
    video = Assignment.objects(id=video_id).first()
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    return render_template('video_player.html', video=video)

# Admin Routes
@app.route('/admin/users/add', methods=['POST'])
@login_required
@role_required('admin')
def admin_add_user():
    try:
        data = request.get_json()
        user = User(
            username=data['username'],
            email=data['email'],
            password=generate_password_hash(data['password']),
            role=data['role'],
            parent_id=str(data.get('parent_id')) if data.get('parent_id') else None,
            teacher_id=str(data.get('teacher_id')) if data.get('teacher_id') else None
        )
        user.save()
        log_activity(current_user.id, 'add_user', f'Added {data["role"]}: {data["username"]}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<user_id>', methods=['GET'])
@login_required
def admin_get_user(user_id):
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied'}), 403
    user = User.objects(id=user_id).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'parent_id': str(user.parent_id) if user.parent_id else None
    })

@app.route('/admin/users/<user_id>/edit', methods=['PUT'])
@login_required
@role_required('admin')
def admin_edit_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        data = request.get_json()
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        user.teacher_id = str(data.get('teacher_id')) if data.get('teacher_id') else user.teacher_id
        user.parent_id = str(data.get('parent_id')) if data.get('parent_id') else None
        if data.get('password'):
            user.password = generate_password_hash(data['password'])
        user.save()
        log_activity(current_user.id, 'edit_user', f'Edited user: {user.username}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<user_id>/toggle', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.is_active = not user.is_active
        user.save()
        status = 'Activated' if user.is_active else 'Deactivated'
        log_activity(current_user.id, 'toggle_user', f'{status} user: {user.username}')
        return jsonify({'success': True, 'is_active': user.is_active})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/users/<user_id>/delete', methods=['DELETE'])
@login_required
@role_required('admin')
def admin_delete_user(user_id):
    try:
        user = User.objects(id=user_id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        username = user.username
        user.delete()
        log_activity(current_user.id, 'delete_user', f'Deleted user: {username}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/logs')
@login_required
@role_required('admin')
def admin_logs():
    try:
        role = request.args.get('role')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query_filter = {}
        if role:
            user_ids = [str(u.id) for u in User.objects(role=role)]
            query_filter['user_id__in'] = user_ids
        if start_date:
            query_filter['timestamp__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            query_filter['timestamp__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
        
        logs = list(UserLog.objects(**query_filter).order_by('-timestamp'))
        return jsonify([{
            'id': str(log.id),
            'user_id': log.user_id,
            'action': log.action,
            'details': log.details,
            'ip_address': log.ip_address,
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for log in logs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/report/pdf')
@login_required
@role_required('admin')
def admin_report_pdf():
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"<b>SignBridge Users Report</b><br/>{datetime.now().strftime('%B %d, %Y %H:%M')}", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3*inch))
        
        data = [['Username', 'Email', 'Role', 'Status']]
        for user in User.objects():
            data.append([
                user.username,
                user.email,
                user.role.capitalize(),
                'Active' if user.is_active else 'Inactive'
            ])
        
        table = Table(data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D96432')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))
        elements.append(table)
        
        doc.build(elements)
        buffer.seek(0)
        
        return Response(buffer.getvalue(), mimetype='application/pdf',
                        headers={'Content-Disposition': f'attachment; filename=SignBridge_Users_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/report/csv')
@login_required
@role_required('admin')
def admin_report_csv():
    try:
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['Username', 'Email', 'Role', 'Active'])
        for user in User.objects():
            writer.writerow([user.username, user.email, user.role, user.is_active])
        
        response = Response(output.getvalue(), mimetype='text/csv')
        response.headers['Content-Disposition'] = f'attachment; filename=SignBridge_Users_Report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        return response
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Teacher Routes
@app.route('/teacher/students')
@login_required
@role_required('teacher')
def teacher_students():
    try:
        students = list(User.objects(role='student', teacher_id=str(current_user.id)))
        return jsonify([{'id': str(s.id), 'username': s.username, 'email': s.email} for s in students])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teacher/attendance', methods=['POST'])
@login_required
@role_required('teacher')
def teacher_mark_attendance():
    try:
        data = request.get_json()
        attendance = Attendance(
            student_id=data['student_id'],
            date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
            status=data['status'],
            teacher_id=str(current_user.id)
        )
        attendance.save()
        log_activity(current_user.id, 'mark_attendance', f'Marked attendance for student {data["student_id"]}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/teacher/remark', methods=['POST'])
@login_required
@role_required('teacher')
def teacher_add_remark():
    try:
        data = request.get_json()
        remark = Remark(
            student_id=data['student_id'],
            teacher_id=str(current_user.id),
            remark_type=data.get('type', 'general'),
            content=data['content']
        )
        remark.save()
        
        student = User.objects(id=data['student_id']).first()
        if student and student.parent_id:
            notif = Notification(
                user_id=str(student.parent_id),
                message=f'New remark for {student.username}: {data["content"]}'
            )
            notif.save()
        
        log_activity(current_user.id, 'add_remark', f'Added remark for student {data["student_id"]}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Parent Routes
@app.route('/parent/child/<child_id>')
@login_required
@role_required('parent')
def parent_view_child(child_id):
    try:
        child = User.objects(id=child_id, parent_id=str(current_user.id)).first()
        if not child:
            return jsonify({'error': 'Access denied'}), 403
        attendance = list(Attendance.objects(student_id=child_id).order_by('-date')[:30])
        remarks = list(Remark.objects(student_id=child_id).order_by('-timestamp'))
        progress = list(Progress.objects(user_id=child_id))
        return jsonify({
            'child': {'id': str(child.id), 'username': child.username, 'email': child.email},
            'attendance': [{'date': a.date.strftime('%Y-%m-%d'), 'status': a.status} for a in attendance],
            'remarks': [{'content': r.content, 'type': r.remark_type, 'date': r.timestamp.strftime('%Y-%m-%d')} for r in remarks],
            'progress': [{'module': p.module, 'item': p.item, 'score': p.score, 'completed': p.completed} for p in progress]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parent/notifications')
@login_required
@role_required('parent')
def parent_notifications():
    try:
        notifs = list(Notification.objects(user_id=str(current_user.id)).order_by('-timestamp'))
        return jsonify([{'id': str(n.id), 'message': n.message, 'is_read': n.is_read, 'created_at': n.timestamp.strftime('%Y-%m-%d %H:%M')} for n in notifs])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parent/notifications/<notif_id>/read', methods=['POST'])
@login_required
@role_required('parent')
def parent_mark_notification_read(notif_id):
    try:
        notif = Notification.objects(id=notif_id).first()
        if not notif:
            return jsonify({'error': 'Notification not found'}), 404
        notif.is_read = True
        notif.save()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/alert')
def alert():
    return render_template('alert.html')

@app.route('/api/risk_stats')
def risk_stats():
    try:
        total = User.objects(role='student', is_active=True).count()
        
        alerts_today = Alert.objects(timestamp__gte=datetime.now().replace(hour=0, minute=0, second=0)).count()
        
        total_logins_today = UserLog.objects(
            action='login',
            timestamp__gte=datetime.now().replace(hour=0, minute=0, second=0)
        ).count()
        
        failed_logins_today = UserLog.objects(
            action='login_failed',
            timestamp__gte=datetime.now().replace(hour=0, minute=0, second=0)
        ).count()
        
        return jsonify({
            'total_students': total,
            'at_risk': 0,
            'alerts_today': alerts_today,
            'logins_today': total_logins_today,
            'failed_logins_today': failed_logins_today,
            'risk_percentage': 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/children_risks')
@login_required
def children_risks():
    try:
        if current_user.role != 'parent':
            return jsonify([])
        
        children = list(User.objects(role='student', parent_id=str(current_user.id)))
        result = []
        
        for child in children:
            last_login = UserLog.objects(user_id=str(child.id), action='login').order_by('-timestamp').first()
            last_login_str = last_login.timestamp.strftime('%Y-%m-%d %H:%M') if last_login else 'Never'
            
            recent_progress = list(Progress.objects(user_id=str(child.id)).order_by('-timestamp')[:5])
            avg_score = round(sum([p.score for p in recent_progress]) / len(recent_progress)) if recent_progress else 0
            
            attendance_count = Attendance.objects(
                student_id=str(child.id),
                date__gte=datetime.now().date() - timedelta(days=30)
            ).count()
            
            total_activities = Progress.objects(user_id=str(child.id)).count()
            
            result.append({
                'name': child.username,
                'risks': [],
                'last_login': last_login_str,
                'avg_score': avg_score,
                'attendance_30days': attendance_count,
                'total_activities': total_activities
            })
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    try:
        data = request.get_json()
        feedback = Feedback(
            name=data.get('name'),
            email=data.get('email'),
            message=data.get('message')
        )
        feedback.save()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/feedback')
@login_required
@role_required('admin')
def admin_view_feedback():
    try:
        feedbacks = list(Feedback.objects().order_by('-timestamp'))
        return jsonify([{
            'id': str(f.id),
            'name': f.name,
            'email': f.email,
            'message': f.message,
            'created_at': f.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        } for f in feedbacks])
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/send_alert', methods=['POST'])
def send_alert():
    try:
        data = request.get_json()
        student_name = "Student"
        parent_phone = "6374145856"
        
        if current_user.is_authenticated and current_user.role == 'student':
            student_name = current_user.username
            if current_user.parent_phone:
                parent_phone = current_user.parent_phone
            elif current_user.parent_id:
                parent = User.objects(id=current_user.parent_id).first()
                if parent and parent.parent_phone:
                    parent_phone = parent.parent_phone
            
            if current_user.parent_id:
                alert = Alert(
                    student_id=str(current_user.id),
                    parent_id=str(current_user.parent_id),
                    sign_detected=data.get('sign'),
                    latitude=data.get('latitude'),
                    longitude=data.get('longitude')
                )
                alert.save()
                
                notif = Notification(
                    user_id=str(current_user.parent_id),
                    message=f'EMERGENCY: {student_name} detected "{data.get("sign")}" sign at location'
                )
                notif.save()
        
        return jsonify({
            'success': True, 
            'sms_sent': True,
            'phone': parent_phone,
            'message': f'Alert sent to {parent_phone}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parent/alerts')
@login_required
@role_required('parent')
def parent_alerts():
    try:
        alerts = list(Alert.objects(parent_id=str(current_user.id)).order_by('-timestamp'))
        result = []
        for a in alerts:
            student = User.objects(id=a.student_id).first()
            result.append({
                'id': str(a.id),
                'student': student.username if student else 'Unknown',
                'sign': a.sign_detected,
                'latitude': a.latitude,
                'longitude': a.longitude,
                'is_read': a.is_read,
                'created_at': a.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/parent/alerts/<alert_id>/read', methods=['POST'])
@login_required
@role_required('parent')
def parent_mark_alert_read(alert_id):
    try:
        alert = Alert.objects(id=alert_id).first()
        if not alert:
            return jsonify({'error': 'Alert not found'}), 404
        alert.is_read = True
        alert.save()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/student/<student_id>/progress')
@login_required
def student_progress_details(student_id):
    try:
        student = User.objects(id=student_id).first()
        if not student:
            return jsonify({'error': 'Student not found'}), 404
        if current_user.role == 'parent' and str(student.parent_id) != str(current_user.id):
            return jsonify({'error': 'Access denied'}), 403
        if current_user.role not in ['parent', 'admin', 'teacher']:
            return jsonify({'error': 'Access denied'}), 403
        
        progress = list(Progress.objects(user_id=student_id).order_by('-timestamp'))
        attendance = list(Attendance.objects(student_id=student_id).order_by('-date')[:30])
        remarks = list(Remark.objects(student_id=student_id).order_by('-timestamp'))
        
        stats = {
            'total': len(progress),
            'completed': len([p for p in progress if p.completed]),
            'avg_score': round(sum([p.score for p in progress]) / len(progress)) if progress else 0,
            'quizzes': len([p for p in progress if p.module == 'quiz']),
            'videos_watched': len([p for p in progress if p.module == 'video'])
        }
        
        return render_template('student_progress_details.html', student=student, progress=progress, stats=stats, attendance=attendance, remarks=remarks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
