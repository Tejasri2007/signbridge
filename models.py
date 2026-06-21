from mongoengine import Document, StringField, IntField, BooleanField, DateTimeField, ReferenceField, ListField, FloatField
from flask_login import UserMixin
from datetime import datetime

class User(Document, UserMixin):
    username = StringField(unique=True, required=True)
    email = StringField(unique=True, required=True)
    password = StringField(required=True)
    role = StringField(required=True)
    is_active = BooleanField(default=True)
    parent_id = StringField(null=True)
    parent_email = StringField(null=True)
    parent_phone = StringField(null=True)
    teacher_id = StringField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'users'}

class Progress(Document):
    user_id = StringField(required=True)
    module = StringField(required=True)
    item = StringField(required=True)
    completed = BooleanField(default=False)
    score = IntField(default=0)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'progress'}

class Assignment(Document):
    teacher_id = StringField(required=True)
    title = StringField(required=True)
    description = StringField(null=True)
    type = StringField(default='assignment')
    video_path = StringField(null=True)
    module = StringField(null=True)
    items = StringField(null=True)
    due_date = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'assignments'}

class UserLog(Document):
    user_id = StringField(required=True)
    action = StringField(required=True)
    details = StringField(null=True)
    ip_address = StringField(null=True)
    device_type = StringField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'user_logs'}

class Attendance(Document):
    student_id = StringField(required=True)
    date = DateTimeField(required=True)
    status = StringField(default='present')
    teacher_id = StringField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'attendance'}

class Remark(Document):
    student_id = StringField(required=True)
    teacher_id = StringField(required=True)
    remark_type = StringField(null=True)
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'remarks'}

class Notification(Document):
    user_id = StringField(required=True)
    message = StringField(required=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'notifications'}

class Feedback(Document):
    name = StringField(required=True)
    email = StringField(required=True)
    message = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'feedback'}

class Alert(Document):
    student_id = StringField(required=True)
    parent_id = StringField(required=True)
    sign_detected = StringField(required=True)
    latitude = FloatField(required=True)
    longitude = FloatField(required=True)
    is_read = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {'collection': 'alerts'}
