"""
Security Intelligence & Suspect Tracking System
A comprehensive platform for tracking suspects through facial recognition,
environmental analysis, and social media intelligence gathering.
"""

from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import json
import sqlite3
from datetime import datetime
import cv2
import numpy as np
from PIL import Image
import face_recognition
import requests
from bs4 import BeautifulSoup
import hashlib
import threading

# Import custom modules
from modules.face_analyzer import FaceAnalyzer
from modules.environment_analyzer import EnvironmentAnalyzer
from modules.social_search import SocialMediaSearcher
from modules.suspect_profiler import SuspectProfiler

app = Flask(__name__)
app.secret_key = 'security_tracker_secret_key_2024'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Configuration
UPLOAD_FOLDER = 'static/uploads'
FACES_FOLDER = 'static/faces'
RESULTS_FOLDER = 'static/results'
DATABASE = 'security_tracker.db'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'mp4', 'avi', 'mov', 'mkv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_database():
    """Initialize SQLite database for storing suspect profiles"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Suspects table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suspects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suspect_id TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            risk_level TEXT DEFAULT 'unknown',
            notes TEXT
        )
    ''')
    
    # Media uploads table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suspect_id TEXT,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            analysis_status TEXT DEFAULT 'pending',
            location_detected TEXT,
            location_confidence REAL,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id)
        )
    ''')
    
    # Extracted faces table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS extracted_faces (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            media_id INTEGER,
            face_path TEXT NOT NULL,
            face_encoding BLOB,
            confidence REAL,
            age_estimate INTEGER,
            gender TEXT,
            emotions TEXT,
            FOREIGN KEY (media_id) REFERENCES media_uploads(id)
        )
    ''')
    
    # Social media matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            face_id INTEGER,
            platform TEXT NOT NULL,
            profile_url TEXT,
            profile_name TEXT,
            profile_image TEXT,
            match_confidence REAL,
            location_info TEXT,
            bio TEXT,
            found_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (face_id) REFERENCES extracted_faces(id)
        )
    ''')
    
    # Intelligence reports table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intelligence_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suspect_id TEXT,
            report_type TEXT,
            report_content TEXT,
            sources TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (suspect_id) REFERENCES suspects(suspect_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("[✓] Database initialized successfully")

# Initialize components
face_analyzer = FaceAnalyzer()
env_analyzer = EnvironmentAnalyzer()
social_searcher = SocialMediaSearcher()
suspect_profiler = SuspectProfiler()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Main dashboard"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) FROM suspects")
    total_suspects = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM media_uploads")
    total_uploads = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM extracted_faces")
    total_faces = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM social_matches")
    total_matches = cursor.fetchone()[0]
    
    # Get recent suspects
    cursor.execute("""
        SELECT s.suspect_id, s.created_at, s.risk_level, 
               COUNT(DISTINCT m.id) as media_count,
               COUNT(DISTINCT sm.id) as match_count
        FROM suspects s
        LEFT JOIN media_uploads m ON s.suspect_id = m.suspect_id
        LEFT JOIN extracted_faces f ON m.id = f.media_id
        LEFT JOIN social_matches sm ON f.id = sm.face_id
        GROUP BY s.suspect_id
        ORDER BY s.created_at DESC
        LIMIT 10
    """)
    recent_suspects = cursor.fetchall()
    
    conn.close()
    
    return render_template('index.html', 
                         stats={
                             'total_suspects': total_suspects,
                             'total_uploads': total_uploads,
                             'total_faces': total_faces,
                             'total_matches': total_matches
                         },
                         recent_suspects=recent_suspects)

@app.route('/upload', methods=['GET', 'POST'])
def upload_media():
    """Handle media uploads (images and videos)"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        suspect_id = request.form.get('suspect_id', '').strip()
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Generate suspect ID if not provided
            if not suspect_id:
                suspect_id = f"SUSPECT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{suspect_id}_{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Determine file type
            file_ext = filename.rsplit('.', 1)[1].lower()
            file_type = 'video' if file_ext in {'mp4', 'avi', 'mov', 'mkv'} else 'image'
            
            # Save to database
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            
            # Create suspect if doesn't exist
            cursor.execute("INSERT OR IGNORE INTO suspects (suspect_id) VALUES (?)", (suspect_id,))
            
            # Save media record
            cursor.execute("""
                INSERT INTO media_uploads (suspect_id, filename, file_path, file_type)
                VALUES (?, ?, ?, ?)
            """, (suspect_id, unique_filename, file_path, file_type))
            media_id = cursor.lastrowid
            
            conn.commit()
            conn.close()
            
            # Start analysis in background
            threading.Thread(target=analyze_media, args=(media_id, file_path, file_type, suspect_id)).start()
            
            flash(f'Media uploaded successfully! Analysis started for {suspect_id}', 'success')
            return redirect(url_for('view_suspect', suspect_id=suspect_id))
    
    return render_template('upload.html')

@app.route('/suspect/<suspect_id>')
def view_suspect(suspect_id):
    """View detailed suspect profile"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Get suspect info
    cursor.execute("SELECT * FROM suspects WHERE suspect_id = ?", (suspect_id,))
    suspect = cursor.fetchone()
    
    if not suspect:
        flash('Suspect not found', 'error')
        return redirect(url_for('index'))
    
    # Get all media for this suspect
    cursor.execute("""
        SELECT * FROM media_uploads 
        WHERE suspect_id = ? 
        ORDER BY upload_date DESC
    """, (suspect_id,))
    media_list = cursor.fetchall()
    
    # Get all faces
    cursor.execute("""
        SELECT f.*, m.file_path as source_media
        FROM extracted_faces f
        JOIN media_uploads m ON f.media_id = m.id
        WHERE m.suspect_id = ?
    """, (suspect_id,))
    faces = cursor.fetchall()
    
    # Get social media matches
    cursor.execute("""
        SELECT sm.*, f.face_path
        FROM social_matches sm
        JOIN extracted_faces f ON sm.face_id = f.id
        JOIN media_uploads m ON f.media_id = m.id
        WHERE m.suspect_id = ?
        ORDER BY sm.match_confidence DESC
    """, (suspect_id,))
    matches = cursor.fetchall()
    
    # Get intelligence reports
    cursor.execute("""
        SELECT * FROM intelligence_reports 
        WHERE suspect_id = ? 
        ORDER BY generated_at DESC
    """, (suspect_id,))
    reports = cursor.fetchall()
    
    conn.close()
    
    return render_template('suspect_profile.html',
                         suspect=suspect,
                         media_list=media_list,
                         faces=faces,
                         matches=matches,
                         reports=reports)

@app.route('/analyze/<int:media_id>')
def analyze_media_page(media_id):
    """View analysis results for a specific media"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM media_uploads WHERE id = ?", (media_id,))
    media = cursor.fetchone()
    
    if not media:
        flash('Media not found', 'error')
        return redirect(url_for('index'))
    
    # Get extracted faces
    cursor.execute("SELECT * FROM extracted_faces WHERE media_id = ?", (media_id,))
    faces = cursor.fetchall()
    
    # Get social matches for these faces
    face_ids = [f[0] for f in faces]
    matches = []
    if face_ids:
        placeholders = ','.join('?' * len(face_ids))
        cursor.execute(f"""
            SELECT * FROM social_matches 
            WHERE face_id IN ({placeholders})
            ORDER BY match_confidence DESC
        """, face_ids)
        matches = cursor.fetchall()
    
    conn.close()
    
    return render_template('analysis_result.html',
                         media=media,
                         faces=faces,
                         matches=matches)

@app.route('/search_face', methods=['POST'])
def search_face():
    """Search for a face across social media"""
    face_id = request.form.get('face_id')
    
    if not face_id:
        return jsonify({'error': 'Face ID required'}), 400
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT face_path FROM extracted_faces WHERE id = ?", (face_id,))
    result = cursor.fetchone()
    conn.close()
    
    if not result:
        return jsonify({'error': 'Face not found'}), 404
    
    face_path = result[0]
    
    # Perform social media search
    search_results = social_searcher.search_face(face_path)
    
    # Save results to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    for match in search_results:
        cursor.execute("""
            INSERT INTO social_matches 
            (face_id, platform, profile_url, profile_name, profile_image, match_confidence, location_info, bio)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            face_id,
            match.get('platform'),
            match.get('profile_url'),
            match.get('profile_name'),
            match.get('profile_image'),
            match.get('confidence'),
            match.get('location'),
            match.get('bio')
        ))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'matches_found': len(search_results),
        'results': search_results
    })

@app.route('/generate_report/<suspect_id>')
def generate_report(suspect_id):
    """Generate comprehensive intelligence report"""
    report = suspect_profiler.generate_full_report(suspect_id, DATABASE)
    
    # Save report to database
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO intelligence_reports (suspect_id, report_type, report_content, sources)
        VALUES (?, ?, ?, ?)
    """, (
        suspect_id,
        'comprehensive',
        json.dumps(report),
        json.dumps(report.get('sources', []))
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify(report)

@app.route('/api/suspects')
def api_suspects():
    """API endpoint to get all suspects"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT s.*, 
               COUNT(DISTINCT m.id) as media_count,
               COUNT(DISTINCT f.id) as face_count,
               COUNT(DISTINCT sm.id) as match_count
        FROM suspects s
        LEFT JOIN media_uploads m ON s.suspect_id = m.suspect_id
        LEFT JOIN extracted_faces f ON m.id = f.media_id
        LEFT JOIN social_matches sm ON f.id = sm.face_id
        GROUP BY s.suspect_id
        ORDER BY s.created_at DESC
    """)
    
    suspects = []
    for row in cursor.fetchall():
        suspects.append({
            'id': row[0],
            'suspect_id': row[1],
            'created_at': row[2],
            'updated_at': row[3],
            'status': row[4],
            'risk_level': row[5],
            'notes': row[6],
            'media_count': row[7],
            'face_count': row[8],
            'match_count': row[9]
        })
    
    conn.close()
    return jsonify(suspects)

@app.route('/api/search')
def api_search():
    """Search suspects by various criteria"""
    query = request.args.get('q', '')
    platform = request.args.get('platform', '')
    location = request.args.get('location', '')
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    sql = """
        SELECT DISTINCT s.* FROM suspects s
        LEFT JOIN media_uploads m ON s.suspect_id = m.suspect_id
        LEFT JOIN extracted_faces f ON m.id = f.media_id
        LEFT JOIN social_matches sm ON f.id = sm.face_id
        WHERE 1=1
    """
    params = []
    
    if query:
        sql += " AND (s.suspect_id LIKE ? OR sm.profile_name LIKE ? OR sm.bio LIKE ?)"
        params.extend([f'%{query}%', f'%{query}%', f'%{query}%'])
    
    if platform:
        sql += " AND sm.platform = ?"
        params.append(platform)
    
    if location:
        sql += " AND (m.location_detected LIKE ? OR sm.location_info LIKE ?)"
        params.extend([f'%{location}%', f'%{location}%'])
    
    sql += " ORDER BY s.created_at DESC"
    
    cursor.execute(sql, params)
    results = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'suspect_id': r[1],
        'created_at': r[2],
        'risk_level': r[5],
        'status': r[4]
    } for r in results])

# ==================== ANALYSIS FUNCTIONS ====================

def analyze_media(media_id, file_path, file_type, suspect_id):
    """Background analysis of uploaded media"""
    print(f"[+] Starting analysis for media {media_id}")
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    try:
        # Update status to processing
        cursor.execute("""
            UPDATE media_uploads SET analysis_status = 'processing' WHERE id = ?
        """, (media_id,))
        conn.commit()
        
        # Extract frames from video if needed
        frames_to_analyze = []
        if file_type == 'video':
            frames_to_analyze = extract_video_frames(file_path)
        else:
            frames_to_analyze = [file_path]
        
        # Analyze each frame
        all_faces = []
        location_detected = None
        location_confidence = 0
        
        for frame_path in frames_to_analyze:
            # Extract faces
            faces = face_analyzer.extract_faces(frame_path, media_id)
            all_faces.extend(faces)
            
            # Analyze environment/location
            env_result = env_analyzer.analyze_location(frame_path)
            if env_result and env_result.get('confidence', 0) > location_confidence:
                location_detected = env_result.get('location')
                location_confidence = env_result.get('confidence', 0)
        
        # Save faces to database
        for face in all_faces:
            cursor.execute("""
                INSERT INTO extracted_faces 
                (media_id, face_path, face_encoding, confidence, age_estimate, gender, emotions)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                media_id,
                face.get('face_path'),
                face.get('encoding'),
                face.get('confidence'),
                face.get('age'),
                face.get('gender'),
                json.dumps(face.get('emotions', {}))
            ))
        
        # Update media with location info
        cursor.execute("""
            UPDATE media_uploads 
            SET analysis_status = 'completed',
                location_detected = ?,
                location_confidence = ?
            WHERE id = ?
        """, (location_detected, location_confidence, media_id))
        
        conn.commit()
        print(f"[✓] Analysis completed for media {media_id}")
        
        # Auto-search faces on social media
        cursor.execute("SELECT id, face_path FROM extracted_faces WHERE media_id = ?", (media_id,))
        faces_to_search = cursor.fetchall()
        
        for face_id, face_path in faces_to_search:
            print(f"[+] Searching face {face_id} on social media...")
            search_results = social_searcher.search_face(face_path)
            
            for match in search_results:
                cursor.execute("""
                    INSERT INTO social_matches 
                    (face_id, platform, profile_url, profile_name, profile_image, match_confidence, location_info, bio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    face_id,
                    match.get('platform'),
                    match.get('profile_url'),
                    match.get('profile_name'),
                    match.get('profile_image'),
                    match.get('confidence'),
                    match.get('location'),
                    match.get('bio')
                ))
            
            conn.commit()
        
        # Generate intelligence report
        report = suspect_profiler.generate_full_report(suspect_id, DATABASE)
        cursor.execute("""
            INSERT INTO intelligence_reports (suspect_id, report_type, report_content, sources)
            VALUES (?, ?, ?, ?)
        """, (
            suspect_id,
            'auto_generated',
            json.dumps(report),
            json.dumps(report.get('sources', []))
        ))
        
        conn.commit()
        
    except Exception as e:
        print(f"[✗] Error analyzing media {media_id}: {str(e)}")
        cursor.execute("""
            UPDATE media_uploads SET analysis_status = 'error' WHERE id = ?
        """, (media_id,))
        conn.commit()
    
    finally:
        conn.close()

def extract_video_frames(video_path, max_frames=10):
    """Extract frames from video for analysis"""
    frames = []
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        return frames
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    interval = max(1, total_frames // max_frames)
    
    for i in range(max_frames):
        frame_pos = i * interval
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
        ret, frame = cap.read()
        
        if ret:
            frame_filename = f"{os.path.splitext(video_path)[0]}_frame_{i}.jpg"
            cv2.imwrite(frame_filename, frame)
            frames.append(frame_filename)
    
    cap.release()
    return frames

# ==================== MAIN ====================

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Create necessary directories
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(FACES_FOLDER, exist_ok=True)
    os.makedirs(RESULTS_FOLDER, exist_ok=True)
    
    print("=" * 60)
    print("SECURITY INTELLIGENCE & SUSPECT TRACKING SYSTEM")
    print("=" * 60)
    print("Starting server on http://127.0.0.1:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
