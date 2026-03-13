#!/usr/bin/env python3
"""
Test Script for Security Tracker System
Verifies all components are working correctly
"""

import os
import sys
import sqlite3

def test_imports():
    """Test that all required modules can be imported"""
    print("[*] Testing imports...")
    
    try:
        import flask
        print("  [✓] Flask imported")
    except ImportError as e:
        print(f"  [✗] Flask import failed: {e}")
        return False
    
    try:
        import cv2
        print("  [✓] OpenCV imported")
    except ImportError as e:
        print(f"  [✗] OpenCV import failed: {e}")
        return False
    
    try:
        import numpy
        print("  [✓] NumPy imported")
    except ImportError as e:
        print(f"  [✗] NumPy import failed: {e}")
        return False
    
    try:
        from PIL import Image
        print("  [✓] Pillow imported")
    except ImportError as e:
        print(f"  [✗] Pillow import failed: {e}")
        return False
    
    try:
        import face_recognition
        print("  [✓] face_recognition imported")
    except ImportError as e:
        print(f"  [✗] face_recognition import failed: {e}")
        print("  [!] Note: face_recognition requires dlib which may take time to install")
        return False
    
    try:
        import requests
        print("  [✓] requests imported")
    except ImportError as e:
        print(f"  [✗] requests import failed: {e}")
        return False
    
    try:
        from bs4 import BeautifulSoup
        print("  [✓] BeautifulSoup imported")
    except ImportError as e:
        print(f"  [✗] BeautifulSoup import failed: {e}")
        return False
    
    print("[✓] All imports successful\n")
    return True

def test_directories():
    """Test that required directories exist"""
    print("[*] Testing directories...")
    
    required_dirs = [
        'static/uploads',
        'static/faces',
        'static/results',
        'modules',
        'templates',
        'utils'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  [✓] {dir_path} exists")
        else:
            print(f"  [✗] {dir_path} missing")
            all_exist = False
    
    if all_exist:
        print("[✓] All directories present\n")
    else:
        print("[!] Some directories missing\n")
    
    return all_exist

def test_database():
    """Test database connection and schema"""
    print("[*] Testing database...")
    
    try:
        from app import init_database, DATABASE
        init_database()
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        required_tables = ['suspects', 'media_uploads', 'extracted_faces', 'social_matches', 'intelligence_reports']
        
        for table in required_tables:
            if table in tables:
                print(f"  [✓] Table '{table}' exists")
            else:
                print(f"  [✗] Table '{table}' missing")
        
        conn.close()
        print("[✓] Database test completed\n")
        return True
        
    except Exception as e:
        print(f"  [✗] Database test failed: {e}\n")
        return False

def test_modules():
    """Test custom modules"""
    print("[*] Testing custom modules...")
    
    try:
        from modules.face_analyzer import FaceAnalyzer
        analyzer = FaceAnalyzer()
        print("  [✓] FaceAnalyzer initialized")
    except Exception as e:
        print(f"  [✗] FaceAnalyzer failed: {e}")
        return False
    
    try:
        from modules.environment_analyzer import EnvironmentAnalyzer
        analyzer = EnvironmentAnalyzer()
        print("  [✓] EnvironmentAnalyzer initialized")
    except Exception as e:
        print(f"  [✗] EnvironmentAnalyzer failed: {e}")
        return False
    
    try:
        from modules.social_search import SocialMediaSearcher
        searcher = SocialMediaSearcher()
        print("  [✓] SocialMediaSearcher initialized")
    except Exception as e:
        print(f"  [✗] SocialMediaSearcher failed: {e}")
        return False
    
    try:
        from modules.suspect_profiler import SuspectProfiler
        profiler = SuspectProfiler()
        print("  [✓] SuspectProfiler initialized")
    except Exception as e:
        print(f"  [✗] SuspectProfiler failed: {e}")
        return False
    
    print("[✓] All modules initialized\n")
    return True

def test_face_recognition():
    """Test face recognition functionality"""
    print("[*] Testing face recognition...")
    
    try:
        import face_recognition
        import numpy as np
        from PIL import Image
        
        # Create a simple test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Try to find faces (will be empty but should not error)
        face_locations = face_recognition.face_locations(test_image)
        
        print(f"  [✓] face_recognition working (found {len(face_locations)} faces in test image)")
        print("[✓] Face recognition test completed\n")
        return True
        
    except Exception as e:
        print(f"  [✗] Face recognition test failed: {e}\n")
        return False

def test_templates():
    """Test that all templates exist"""
    print("[*] Testing templates...")
    
    required_templates = [
        'base.html',
        'index.html',
        'upload.html',
        'suspect_profile.html',
        'analysis_result.html'
    ]
    
    all_exist = True
    for template in required_templates:
        template_path = os.path.join('templates', template)
        if os.path.exists(template_path):
            print(f"  [✓] Template '{template}' exists")
        else:
            print(f"  [✗] Template '{template}' missing")
            all_exist = False
    
    if all_exist:
        print("[✓] All templates present\n")
    else:
        print("[!] Some templates missing\n")
    
    return all_exist

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("  SECURITY TRACKER SYSTEM TEST")
    print("=" * 60)
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Directories", test_directories()))
    results.append(("Database", test_database()))
    results.append(("Modules", test_modules()))
    results.append(("Face Recognition", test_face_recognition()))
    results.append(("Templates", test_templates()))
    
    print("=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n[✓] All tests passed! System is ready.")
        return 0
    else:
        print("\n[!] Some tests failed. Please check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())
