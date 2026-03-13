#!/usr/bin/env python3
"""
Demo Data Generator for Security Tracker
Generates sample data for testing purposes
"""

import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

def generate_demo_data():
    """Generate demo data for testing"""
    print("[*] Generating demo data...")
    
    DATABASE = 'security_tracker.db'
    
    if not os.path.exists(DATABASE):
        print("[!] Database not found. Please run 'python start.py --setup' first.")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Sample data
    suspect_ids = [
        'SUSPECT_DEMO_001',
        'SUSPECT_DEMO_002',
        'SUSPECT_DEMO_003'
    ]
    
    platforms = ['Facebook', 'Instagram', 'Twitter', 'LinkedIn', 'TikTok']
    locations = ['New York, NY', 'Los Angeles, CA', 'Chicago, IL', 'Miami, FL', 'London, UK']
    risk_levels = ['low', 'medium', 'high']
    statuses = ['active', 'under_investigation', 'resolved']
    
    # Clear existing demo data
    print("[*] Clearing existing demo data...")
    for suspect_id in suspect_ids:
        cursor.execute("DELETE FROM social_matches WHERE face_id IN (SELECT id FROM extracted_faces WHERE media_id IN (SELECT id FROM media_uploads WHERE suspect_id = ?))", (suspect_id,))
        cursor.execute("DELETE FROM extracted_faces WHERE media_id IN (SELECT id FROM media_uploads WHERE suspect_id = ?)", (suspect_id,))
        cursor.execute("DELETE FROM intelligence_reports WHERE suspect_id = ?", (suspect_id,))
        cursor.execute("DELETE FROM media_uploads WHERE suspect_id = ?", (suspect_id,))
        cursor.execute("DELETE FROM suspects WHERE suspect_id = ?", (suspect_id,))
    
    # Generate suspects
    print("[*] Creating demo suspects...")
    for i, suspect_id in enumerate(suspect_ids):
        created_at = (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        
        cursor.execute("""
            INSERT INTO suspects (suspect_id, created_at, updated_at, status, risk_level, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            suspect_id,
            created_at,
            created_at,
            random.choice(statuses),
            risk_levels[i % len(risk_levels)],
            f"Demo suspect #{i+1} for testing purposes"
        ))
        
        # Generate media uploads
        num_media = random.randint(1, 3)
        for j in range(num_media):
            media_time = (datetime.now() - timedelta(days=random.randint(0, 10), hours=random.randint(0, 23))).isoformat()
            file_type = random.choice(['image', 'video'])
            filename = f"{suspect_id}_media_{j+1}.jpg" if file_type == 'image' else f"{suspect_id}_media_{j+1}.mp4"
            
            cursor.execute("""
                INSERT INTO media_uploads (suspect_id, filename, file_path, file_type, upload_date, analysis_status, location_detected, location_confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                suspect_id,
                filename,
                f"static/uploads/{filename}",
                file_type,
                media_time,
                'completed',
                random.choice(locations),
                round(random.uniform(0.5, 0.95), 2)
            ))
            
            media_id = cursor.lastrowid
            
            # Generate extracted faces
            num_faces = random.randint(1, 3)
            for k in range(num_faces):
                face_filename = f"face_{media_id}_{k+1}.jpg"
                emotions = json.dumps({
                    'neutral': round(random.uniform(0.4, 0.8), 2),
                    'happy': round(random.uniform(0.0, 0.3), 2),
                    'sad': round(random.uniform(0.0, 0.2), 2),
                    'angry': round(random.uniform(0.0, 0.2), 2),
                    'fearful': round(random.uniform(0.0, 0.1), 2),
                    'disgusted': round(random.uniform(0.0, 0.1), 2),
                    'surprised': round(random.uniform(0.0, 0.2), 2)
                })
                
                cursor.execute("""
                    INSERT INTO extracted_faces (media_id, face_path, confidence, age_estimate, gender, emotions)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    media_id,
                    f"static/faces/{face_filename}",
                    round(random.uniform(0.6, 0.95), 2),
                    random.randint(20, 55),
                    random.choice(['male', 'female']),
                    emotions
                ))
                
                face_id = cursor.lastrowid
                
                # Generate social matches
                num_matches = random.randint(0, 4)
                for m in range(num_matches):
                    platform = platforms[m % len(platforms)]
                    
                    cursor.execute("""
                        INSERT INTO social_matches (face_id, platform, profile_url, profile_name, match_confidence, location_info, bio, found_date)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        face_id,
                        platform,
                        f"https://{platform.lower()}.com/demo_profile_{m+1}",
                        f"Demo User {m+1}",
                        round(random.uniform(0.5, 0.9), 2),
                        random.choice(locations),
                        f"Demo bio for testing purposes. This is a simulated profile.",
                        (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat()
                    ))
        
        # Generate intelligence reports
        report_data = {
            'executive_summary': {
                'overview': f'Intelligence analysis for {suspect_id}',
                'key_findings': ['Demo finding 1', 'Demo finding 2'],
                'confidence_level': 'Medium',
                'priority': 'Standard'
            },
            'identity_analysis': {
                'possible_names': ['Demo Name 1', 'Demo Name 2'],
                'age_estimate': random.randint(25, 50),
                'gender_estimate': random.choice(['male', 'female']),
                'verification_status': 'partially_verified'
            },
            'digital_footprint': {
                'platforms_found': random.sample(platforms, random.randint(1, 4)),
                'online_presence_score': round(random.uniform(0.3, 0.8), 2),
                'privacy_level': random.choice(['low', 'medium', 'high'])
            },
            'risk_assessment': {
                'overall_risk': risk_levels[i % len(risk_levels)],
                'risk_score': random.randint(1, 5),
                'threat_assessment': 'monitoring_recommended'
            }
        }
        
        cursor.execute("""
            INSERT INTO intelligence_reports (suspect_id, report_type, report_content, sources, generated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            suspect_id,
            'comprehensive',
            json.dumps(report_data),
            json.dumps(['demo_source_1', 'demo_source_2']),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()
    
    print("[✓] Demo data generated successfully!")
    print()
    print("Demo suspects created:")
    for suspect_id in suspect_ids:
        print(f"  - {suspect_id}")
    print()
    print("You can now view these suspects in the web interface.")

def clear_demo_data():
    """Clear all demo data"""
    print("[*] Clearing demo data...")
    
    DATABASE = 'security_tracker.db'
    
    if not os.path.exists(DATABASE):
        print("[!] Database not found.")
        return
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    suspect_ids = ['SUSPECT_DEMO_001', 'SUSPECT_DEMO_002', 'SUSPECT_DEMO_003']
    
    for suspect_id in suspect_ids:
        cursor.execute("DELETE FROM social_matches WHERE face_id IN (SELECT id FROM extracted_faces WHERE media_id IN (SELECT id FROM media_uploads WHERE suspect_id = ?))", (suspect_id,))
        cursor.execute("DELETE FROM extracted_faces WHERE media_id IN (SELECT id FROM media_uploads WHERE suspect_id = ?)", (suspect_id,))
        cursor.execute("DELETE FROM intelligence_reports WHERE suspect_id = ?", (suspect_id,))
        cursor.execute("DELETE FROM media_uploads WHERE suspect_id = ?", (suspect_id,))
        cursor.execute("DELETE FROM suspects WHERE suspect_id = ?", (suspect_id,))
    
    conn.commit()
    conn.close()
    
    print("[✓] Demo data cleared.")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate or clear demo data')
    parser.add_argument('--clear', action='store_true', help='Clear demo data instead of generating')
    
    args = parser.parse_args()
    
    if args.clear:
        clear_demo_data()
    else:
        generate_demo_data()
