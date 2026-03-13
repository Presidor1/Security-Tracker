"""
Face Analysis Module
Extracts faces from images/videos and performs facial analysis
"""

import cv2
import numpy as np
import face_recognition
from PIL import Image
import os
import json
from datetime import datetime

class FaceAnalyzer:
    def __init__(self):
        self.faces_dir = 'static/faces'
        os.makedirs(self.faces_dir, exist_ok=True)
        
        # Load pre-trained models
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
    def extract_faces(self, image_path, media_id):
        """
        Extract all faces from an image
        Returns list of face data dictionaries
        """
        faces_data = []
        
        try:
            # Load image
            image = face_recognition.load_image_file(image_path)
            
            # Find all faces
            face_locations = face_recognition.face_locations(image)
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            # Load with PIL for additional processing
            pil_image = Image.open(image_path)
            
            for idx, (face_location, face_encoding) in enumerate(zip(face_locations, face_encodings)):
                top, right, bottom, left = face_location
                
                # Extract face region
                face_image = image[top:bottom, left:right]
                
                # Save face image
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                face_filename = f"face_{media_id}_{timestamp}_{idx}.jpg"
                face_path = os.path.join(self.faces_dir, face_filename)
                
                # Convert to PIL and save
                face_pil = Image.fromarray(face_image)
                face_pil.save(face_path)
                
                # Analyze face attributes
                face_data = {
                    'face_path': face_path,
                    'encoding': face_encoding.tobytes(),
                    'confidence': self._calculate_face_confidence(face_image),
                    'age': self._estimate_age(face_image),
                    'gender': self._estimate_gender(face_image),
                    'emotions': self._detect_emotions(face_image),
                    'location': face_location
                }
                
                faces_data.append(face_data)
                
            print(f"[✓] Extracted {len(faces_data)} faces from {image_path}")
            
        except Exception as e:
            print(f"[✗] Error extracting faces: {str(e)}")
        
        return faces_data
    
    def _calculate_face_confidence(self, face_image):
        """Calculate confidence score for face detection"""
        try:
            # Convert to grayscale
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            else:
                gray = face_image
            
            # Detect eyes as quality indicator
            eyes = self.eye_cascade.detectMultiScale(gray)
            
            # Score based on face size and eye detection
            face_size = gray.shape[0] * gray.shape[1]
            eye_score = min(len(eyes) * 0.3, 0.5)
            size_score = min(face_size / 10000, 0.5)
            
            return round(eye_score + size_score, 2)
            
        except Exception:
            return 0.5
    
    def _estimate_age(self, face_image):
        """Estimate age from face (simplified estimation)"""
        try:
            # Load age prediction model (placeholder - would use deep learning model)
            # For now, return placeholder
            return None
        except Exception:
            return None
    
    def _estimate_gender(self, face_image):
        """Estimate gender from face (simplified estimation)"""
        try:
            # Load gender prediction model (placeholder)
            return None
        except Exception:
            return None
    
    def _detect_emotions(self, face_image):
        """Detect emotions from face"""
        try:
            # Emotion detection would use a trained model
            # Return placeholder structure
            return {
                'neutral': 0.7,
                'happy': 0.1,
                'sad': 0.05,
                'angry': 0.05,
                'fearful': 0.05,
                'disgusted': 0.03,
                'surprised': 0.02
            }
        except Exception:
            return {}
    
    def compare_faces(self, face_encoding1, face_encoding2):
        """Compare two face encodings and return similarity score"""
        try:
            # Convert bytes back to numpy array if needed
            if isinstance(face_encoding1, bytes):
                face_encoding1 = np.frombuffer(face_encoding1, dtype=np.float64)
            if isinstance(face_encoding2, bytes):
                face_encoding2 = np.frombuffer(face_encoding2, dtype=np.float64)
            
            # Calculate face distance
            distance = face_recognition.face_distance([face_encoding1], [face_encoding2])[0]
            
            # Convert to similarity score (0-1)
            similarity = 1 - distance
            
            return round(similarity, 2)
            
        except Exception as e:
            print(f"[✗] Error comparing faces: {str(e)}")
            return 0.0
    
    def find_matching_faces(self, target_encoding, database_encodings, threshold=0.6):
        """Find matching faces in database"""
        matches = []
        
        for db_id, db_encoding in database_encodings:
            similarity = self.compare_faces(target_encoding, db_encoding)
            if similarity >= threshold:
                matches.append({
                    'id': db_id,
                    'similarity': similarity
                })
        
        # Sort by similarity
        matches.sort(key=lambda x: x['similarity'], reverse=True)
        
        return matches
    
    def enhance_face(self, face_image):
        """Enhance face image quality for better recognition"""
        try:
            # Convert to PIL Image if needed
            if isinstance(face_image, np.ndarray):
                face_image = Image.fromarray(face_image)
            
            # Enhance sharpness
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Sharpness(face_image)
            face_image = enhancer.enhance(1.5)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(face_image)
            face_image = enhancer.enhance(1.2)
            
            return face_image
            
        except Exception as e:
            print(f"[✗] Error enhancing face: {str(e)}")
            return face_image
    
    def detect_face_landmarks(self, image_path):
        """Detect facial landmarks"""
        try:
            image = face_recognition.load_image_file(image_path)
            face_landmarks_list = face_recognition.face_landmarks(image)
            
            return face_landmarks_list
            
        except Exception as e:
            print(f"[✗] Error detecting landmarks: {str(e)}")
            return []
