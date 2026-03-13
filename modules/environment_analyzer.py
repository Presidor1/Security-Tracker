"""
Environment Analysis Module
Analyzes backgrounds and environments to detect locations
"""

import cv2
import numpy as np
from PIL import Image
import os
import requests
import json
from collections import Counter

class EnvironmentAnalyzer:
    def __init__(self):
        # Known location features database (simplified)
        self.location_features = self._load_location_database()
        
    def _load_location_database(self):
        """Load known location features"""
        return {
            'urban_street': {
                'features': ['buildings', 'cars', 'roads', 'sidewalks'],
                'indicators': ['vertical_lines', 'rectangular_shapes']
            },
            'indoor_office': {
                'features': ['desks', 'chairs', 'computers', 'whiteboards'],
                'indicators': ['horizontal_surfaces', 'artificial_lighting']
            },
            'residential': {
                'features': ['furniture', 'decorations', 'windows', 'doors'],
                'indicators': ['domestic_objects', 'personal_items']
            },
            'commercial': {
                'features': ['shelves', 'products', 'counters', 'signs'],
                'indicators': ['display_items', 'commercial_lighting']
            },
            'outdoor_nature': {
                'features': ['trees', 'grass', 'sky', 'natural_light'],
                'indicators': ['green_colors', 'natural_textures']
            }
        }
    
    def analyze_location(self, image_path):
        """
        Analyze image to detect location/environment
        Returns location data with confidence score
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            # Extract various features
            color_analysis = self._analyze_colors(image)
            texture_analysis = self._analyze_textures(image)
            object_analysis = self._detect_objects(image)
            architectural_features = self._detect_architectural_features(image)
            
            # Combine analyses to determine location
            location_result = self._determine_location(
                color_analysis,
                texture_analysis,
                object_analysis,
                architectural_features
            )
            
            # Try to identify specific landmarks
            landmarks = self._identify_landmarks(image)
            if landmarks:
                location_result['landmarks'] = landmarks
            
            # Extract text from environment
            text_elements = self._extract_environment_text(image)
            if text_elements:
                location_result['text_elements'] = text_elements
            
            return location_result
            
        except Exception as e:
            print(f"[✗] Error analyzing location: {str(e)}")
            return None
    
    def _analyze_colors(self, image):
        """Analyze color distribution in image"""
        # Convert to HSV for better color analysis
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Calculate color histograms
        h_hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        s_hist = cv2.calcHist([hsv], [1], None, [256], [0, 256])
        v_hist = cv2.calcHist([hsv], [2], None, [256], [0, 256])
        
        # Dominant colors
        dominant_hue = np.argmax(h_hist)
        dominant_sat = np.argmax(s_hist)
        dominant_val = np.argmax(v_hist)
        
        # Determine if image is mostly natural or artificial
        green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
        blue_mask = cv2.inRange(hsv, (100, 50, 50), (130, 255, 255))
        gray_mask = cv2.inRange(hsv, (0, 0, 50), (180, 30, 200))
        
        green_ratio = np.sum(green_mask > 0) / (image.shape[0] * image.shape[1])
        blue_ratio = np.sum(blue_mask > 0) / (image.shape[0] * image.shape[1])
        gray_ratio = np.sum(gray_mask > 0) / (image.shape[0] * image.shape[1])
        
        return {
            'dominant_hue': int(dominant_hue),
            'dominant_saturation': int(dominant_sat),
            'dominant_value': int(dominant_val),
            'green_ratio': round(green_ratio, 3),
            'blue_ratio': round(blue_ratio, 3),
            'gray_ratio': round(gray_ratio, 3),
            'is_natural': green_ratio > 0.2,
            'is_urban': gray_ratio > 0.3
        }
    
    def _analyze_textures(self, image):
        """Analyze textures in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate texture features using GLCM (simplified)
        # In practice, would use more sophisticated texture analysis
        
        # Edge detection for texture analysis
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
        
        # Detect patterns
        vertical_lines = self._detect_vertical_lines(edges)
        horizontal_lines = self._detect_horizontal_lines(edges)
        
        return {
            'edge_density': round(edge_density, 3),
            'vertical_structure': len(vertical_lines) > 10,
            'horizontal_structure': len(horizontal_lines) > 10,
            'has_regular_pattern': len(vertical_lines) > 20 or len(horizontal_lines) > 20
        }
    
    def _detect_objects(self, image):
        """Detect common objects in environment"""
        detected_objects = []
        
        # This would use object detection models like YOLO
        # For now, use simplified detection
        
        # Detect vehicles (simplified)
        vehicles = self._detect_vehicles(image)
        if vehicles:
            detected_objects.extend(['vehicle'] * len(vehicles))
        
        # Detect people (simplified)
        people = self._detect_people(image)
        if people:
            detected_objects.extend(['person'] * len(people))
        
        # Detect furniture (simplified)
        furniture = self._detect_furniture(image)
        if furniture:
            detected_objects.extend(['furniture'] * len(furniture))
        
        return Counter(detected_objects)
    
    def _detect_vehicles(self, image):
        """Detect vehicles in image"""
        # Simplified detection - would use trained model
        return []
    
    def _detect_people(self, image):
        """Detect people in image"""
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        people, _ = hog.detectMultiScale(gray, winStride=(8, 8), padding=(16, 16), scale=1.05)
        
        return people
    
    def _detect_furniture(self, image):
        """Detect furniture in image"""
        # Simplified detection
        return []
    
    def _detect_architectural_features(self, image):
        """Detect architectural features"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)
        
        features = {
            'has_walls': False,
            'has_ceiling': False,
            'has_windows': False,
            'has_doors': False,
            'line_count': 0
        }
        
        if lines is not None:
            features['line_count'] = len(lines)
            
            # Analyze line orientations
            horizontal = 0
            vertical = 0
            
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                
                if angle < 20 or angle > 160:
                    horizontal += 1
                elif 70 < angle < 110:
                    vertical += 1
            
            features['has_walls'] = vertical > 5
            features['has_ceiling'] = horizontal > 5
        
        # Detect windows (rectangular patterns)
        features['has_windows'] = self._detect_windows(image)
        
        return features
    
    def _detect_windows(self, image):
        """Detect windows in image"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Look for rectangular patterns that could be windows
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        window_candidates = 0
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            if len(approx) == 4:  # Rectangle
                x, y, w, h = cv2.boundingRect(approx)
                aspect_ratio = float(w)/h
                if 0.5 < aspect_ratio < 2.0 and w > 50 and h > 50:
                    window_candidates += 1
        
        return window_candidates > 2
    
    def _detect_vertical_lines(self, edges):
        """Detect vertical lines"""
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        vertical_lines = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if 80 < angle < 100:
                    vertical_lines.append(line)
        
        return vertical_lines
    
    def _detect_horizontal_lines(self, edges):
        """Detect horizontal lines"""
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
        horizontal_lines = []
        
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 10 or angle > 170:
                    horizontal_lines.append(line)
        
        return horizontal_lines
    
    def _determine_location(self, color_analysis, texture_analysis, object_analysis, architectural_features):
        """Determine location type based on all analyses"""
        scores = {
            'urban_street': 0,
            'indoor_office': 0,
            'residential': 0,
            'commercial': 0,
            'outdoor_nature': 0
        }
        
        # Score based on color analysis
        if color_analysis['is_urban']:
            scores['urban_street'] += 2
            scores['indoor_office'] += 1
            scores['commercial'] += 1
        
        if color_analysis['is_natural']:
            scores['outdoor_nature'] += 3
        
        # Score based on texture analysis
        if texture_analysis['vertical_structure']:
            scores['urban_street'] += 1
            scores['indoor_office'] += 1
        
        if texture_analysis['has_regular_pattern']:
            scores['indoor_office'] += 1
            scores['commercial'] += 1
        
        # Score based on architectural features
        if architectural_features['has_walls']:
            scores['indoor_office'] += 2
            scores['residential'] += 2
            scores['commercial'] += 1
        
        if architectural_features['has_windows']:
            scores['indoor_office'] += 1
            scores['residential'] += 1
            scores['commercial'] += 1
        
        # Score based on objects
        if 'person' in object_analysis:
            scores['urban_street'] += 1
            scores['commercial'] += 1
        
        if 'vehicle' in object_analysis:
            scores['urban_street'] += 2
        
        # Determine best match
        best_location = max(scores, key=scores.get)
        best_score = scores[best_location]
        
        # Calculate confidence
        total_score = sum(scores.values())
        confidence = best_score / total_score if total_score > 0 else 0
        
        # Create description
        descriptions = {
            'urban_street': 'Urban outdoor environment, likely a street or public area',
            'indoor_office': 'Indoor office or professional environment',
            'residential': 'Residential indoor setting, likely a home or apartment',
            'commercial': 'Commercial establishment such as a store or restaurant',
            'outdoor_nature': 'Outdoor natural environment with vegetation'
        }
        
        return {
            'location': best_location,
            'description': descriptions.get(best_location, 'Unknown environment'),
            'confidence': round(confidence, 2),
            'all_scores': scores,
            'indicators': self._get_location_indicators(best_location, color_analysis, architectural_features)
        }
    
    def _get_location_indicators(self, location_type, color_analysis, architectural_features):
        """Get specific indicators for the detected location"""
        indicators = []
        
        if location_type == 'urban_street':
            if color_analysis.get('gray_ratio', 0) > 0.3:
                indicators.append('Concrete/man-made structures detected')
            if color_analysis.get('blue_ratio', 0) > 0.15:
                indicators.append('Sky visible in frame')
        
        elif location_type == 'indoor_office':
            if architectural_features.get('has_walls'):
                indicators.append('Wall structures detected')
            if architectural_features.get('has_windows'):
                indicators.append('Windows present')
        
        elif location_type == 'outdoor_nature':
            if color_analysis.get('green_ratio', 0) > 0.2:
                indicators.append('Vegetation detected')
        
        return indicators
    
    def _identify_landmarks(self, image):
        """Try to identify specific landmarks"""
        # This would integrate with landmark recognition APIs
        # For now, return empty
        return []
    
    def _extract_environment_text(self, image):
        """Extract text visible in the environment"""
        # This would use OCR
        # For now, return empty
        return []
    
    def reverse_image_search_location(self, image_path):
        """
        Perform reverse image search to find similar locations
        This would integrate with search APIs
        """
        # Placeholder for reverse image search
        return {
            'similar_locations': [],
            'possible_addresses': [],
            'geolocation_hints': []
        }
