
SignBridge

A Web-Based Sign Language Learning and Communication Platform

---

Project Overview

SignBridge is an AI-powered web application developed to bridge the communication gap between hearing individuals and the deaf or hard-of-hearing community. The system converts speech into Indian Sign Language (ISL) videos and provides an interactive learning platform for users to learn and practice sign language.

The platform supports students, teachers, parents, and administrators through dedicated dashboards and role-based access control. It also includes progress tracking, attendance monitoring, notification management, and cloud-based video storage.

---

System Architecture

## System Architecture

![System Architecture](images/system-architecture.png.jpeg)

Architecture Description

The SignBridge system follows a multi-layer architecture consisting of:

- User Interface Layer (HTML, CSS, JavaScript)
- Flask Backend Application
- Speech Recognition Module (OpenAI Whisper)
- NLP and Text Processing Module
- Video Processing Module (FFmpeg)
- MongoDB Atlas Database
- Supabase Cloud Storage
- Render Cloud Deployment

The frontend communicates with the Flask backend, which processes user requests, manages authentication, handles speech-to-sign conversion, stores user data in MongoDB, and retrieves sign language videos from cloud storage.

---

Workflow Diagram

## Workflow Diagram

![Workflow Diagram](images/workflow.png.jpeg)

Workflow Description

1. User records or uploads audio.
2. Audio is converted into text using speech recognition.
3. Text is processed and analyzed.
4. Matching sign language videos are identified.
5. Videos are retrieved from storage.
6. FFmpeg merges the videos into a single sequence.
7. Generated sign language output is displayed.
8. User progress and activity are stored in the database.
9. Teachers, parents, and administrators can monitor performance through dashboards.

---

Features

Speech-to-Sign Language Conversion

- Audio recording support
- Audio file upload
- Speech recognition
- Sign language video generation
- Video playback and download

Learning Module

- ISL alphabet learning
- Number learning
- Interactive sign demonstrations
- Daily phrase learning
- Progress monitoring

User Management

- Student Dashboard
- Teacher Dashboard
- Parent Dashboard
- Admin Dashboard

Progress Tracking

- Learning analytics
- Completion monitoring
- Performance reports

Attendance Management

- Attendance tracking
- Student monitoring
- Attendance reports

Notification System

- Parent notifications
- Teacher remarks
- Progress alerts

Report Generation

- PDF reports
- CSV reports
- Performance summaries

---

User Roles

Student

- Learn sign language
- Convert speech to sign language
- Track learning progress
- Access educational resources

Teacher

- Upload learning materials
- Manage students
- Mark attendance
- Add remarks and feedback
- Monitor performance

Parent

- Monitor child progress
- View attendance records
- Receive notifications
- Review teacher remarks

Admin

- Manage users
- Generate reports
- Monitor activities
- View analytics

---

Technology Stack

Frontend

- HTML5
- CSS3
- JavaScript

Backend

- Flask
- Python

Database

- MongoDB Atlas

Cloud Storage

- Supabase

Video Processing

- FFmpeg

Speech Recognition

- OpenAI Whisper

Deployment

- Render

Version Control

- Git
- GitHub

---

Project Structure

SignBridge/
│
├── app.py
├── models.py
├── requirements.txt
├── render.yaml
├── templates/
├── static/
├── learning/
├── archive/
├── sign_videos/
├── audio_uploads/
├── images/
│   ├── system-architecture.png.jpeg
│   └── workflow.png.jpeg
└── README.md

---

Installation

Clone the Repository

git clone https://github.com/Tejasri2007/signbridge.git
cd signbridge

Create Virtual Environment

python -m venv venv

Activate Virtual Environment

Windows:

venv\Scripts\activate

Linux/Mac:

source venv/bin/activate

Install Dependencies

pip install -r requirements.txt

Run the Application

python app.py

Open in Browser

http://localhost:5000

---

Deployment

The application is deployed using:

- GitHub
- Render Cloud Platform
- MongoDB Atlas
- Supabase Storage

---

Security Features

- Password Hashing
- Secure Authentication
- Session Management
- Role-Based Access Control
- Environment Variable Protection
- HTTPS Deployment

---

Future Enhancements

- Mobile Application
- Real-Time Gesture Recognition
- AI-Based Learning Recommendations
- Multi-Language Support
- SMS and Email Notifications
- Advanced Analytics Dashboard
- Offline Learning Support

---

Results

The SignBridge platform successfully converts speech into Indian Sign Language videos, improves accessibility for deaf and hard-of-hearing users, and provides a structured learning environment through interactive educational modules and progress tracking systems.

---

Conclusion

SignBridge serves as an effective communication and learning platform that promotes inclusivity through sign language technology. By integrating speech recognition, video processing, cloud storage, and educational tools, the system contributes to accessible communication and digital learning.

---

Developer

Tejasri

---

License

This project is developed for educational and academic purposes.
