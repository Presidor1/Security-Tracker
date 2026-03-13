"""
Suspect Profiling Module
Generates comprehensive intelligence reports on suspects
"""

import sqlite3
import json
from datetime import datetime
from collections import Counter

class SuspectProfiler:
    def __init__(self):
        self.report_templates = {
            'basic': self._basic_report,
            'comprehensive': self._comprehensive_report,
            'intelligence': self._intelligence_report
        }
    
    def generate_full_report(self, suspect_id, database_path):
        """Generate comprehensive report for a suspect"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        try:
            # Gather all suspect data
            suspect_data = self._gather_suspect_data(cursor, suspect_id)
            
            # Generate report sections
            report = {
                'suspect_id': suspect_id,
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive_intelligence',
                'executive_summary': self._generate_executive_summary(suspect_data),
                'identity_analysis': self._analyze_identity(suspect_data),
                'digital_footprint': self._analyze_digital_footprint(suspect_data),
                'location_analysis': self._analyze_locations(suspect_data),
                'social_connections': self._analyze_connections(suspect_data),
                'behavioral_profile': self._analyze_behavior(suspect_data),
                'risk_assessment': self._assess_risk(suspect_data),
                'recommendations': self._generate_recommendations(suspect_data),
                'sources': self._compile_sources(suspect_data),
                'confidence_score': self._calculate_confidence(suspect_data)
            }
            
            return report
            
        except Exception as e:
            return {
                'error': str(e),
                'suspect_id': suspect_id,
                'generated_at': datetime.now().isoformat()
            }
        finally:
            conn.close()
    
    def _gather_suspect_data(self, cursor, suspect_id):
        """Gather all data related to a suspect"""
        data = {
            'suspect_id': suspect_id,
            'profile': None,
            'media': [],
            'faces': [],
            'social_matches': [],
            'previous_reports': []
        }
        
        # Get suspect profile
        cursor.execute("SELECT * FROM suspects WHERE suspect_id = ?", (suspect_id,))
        data['profile'] = cursor.fetchone()
        
        # Get all media
        cursor.execute("""
            SELECT * FROM media_uploads 
            WHERE suspect_id = ? 
            ORDER BY upload_date DESC
        """, (suspect_id,))
        data['media'] = cursor.fetchall()
        
        # Get all faces
        cursor.execute("""
            SELECT f.*, m.file_path as source_media, m.location_detected
            FROM extracted_faces f
            JOIN media_uploads m ON f.media_id = m.id
            WHERE m.suspect_id = ?
        """, (suspect_id,))
        data['faces'] = cursor.fetchall()
        
        # Get social media matches
        cursor.execute("""
            SELECT sm.*, f.face_path, f.confidence as face_confidence
            FROM social_matches sm
            JOIN extracted_faces f ON sm.face_id = f.id
            JOIN media_uploads m ON f.media_id = m.id
            WHERE m.suspect_id = ?
            ORDER BY sm.match_confidence DESC
        """, (suspect_id,))
        data['social_matches'] = cursor.fetchall()
        
        # Get previous reports
        cursor.execute("""
            SELECT * FROM intelligence_reports 
            WHERE suspect_id = ? 
            ORDER BY generated_at DESC
        """, (suspect_id,))
        data['previous_reports'] = cursor.fetchall()
        
        return data
    
    def _generate_executive_summary(self, data):
        """Generate executive summary of findings"""
        summary = {
            'overview': '',
            'key_findings': [],
            'confidence_level': '',
            'priority': ''
        }
        
        # Build overview
        media_count = len(data['media'])
        face_count = len(data['faces'])
        match_count = len(data['social_matches'])
        
        summary['overview'] = (
            f"Intelligence analysis conducted on suspect {data['suspect_id']}. "
            f"Analysis includes {media_count} media files, {face_count} extracted facial images, "
            f"and {match_count} potential social media matches."
        )
        
        # Key findings
        if match_count > 0:
            platforms = list(set([m[2] for m in data['social_matches']]))  # platform column
            summary['key_findings'].append(
                f"Potential matches found on: {', '.join(platforms)}"
            )
        
        # Locations detected
        locations = [m[6] for m in data['media'] if m[6]]  # location_detected column
        if locations:
            unique_locations = list(set(locations))
            summary['key_findings'].append(
                f"Environment analysis suggests locations: {', '.join(unique_locations)}"
            )
        
        # Confidence and priority
        if match_count >= 5:
            summary['confidence_level'] = 'High'
            summary['priority'] = 'High Priority'
        elif match_count >= 2:
            summary['confidence_level'] = 'Medium'
            summary['priority'] = 'Medium Priority'
        else:
            summary['confidence_level'] = 'Low'
            summary['priority'] = 'Standard Priority'
        
        return summary
    
    def _analyze_identity(self, data):
        """Analyze potential identity information"""
        identity = {
            'possible_names': [],
            'possible_aliases': [],
            'age_estimate': None,
            'gender_estimate': None,
            'distinguishing_features': [],
            'verification_status': 'unverified'
        }
        
        # Extract names from social matches
        for match in data['social_matches']:
            profile_name = match[4]  # profile_name column
            if profile_name:
                identity['possible_names'].append(profile_name)
        
        # Remove duplicates
        identity['possible_names'] = list(set(identity['possible_names']))
        
        # Analyze facial attributes
        if data['faces']:
            ages = [f[5] for f in data['faces'] if f[5]]  # age_estimate
            genders = [f[6] for f in data['faces'] if f[6]]  # gender
            
            if ages:
                identity['age_estimate'] = int(sum(ages) / len(ages))
            
            if genders:
                gender_counts = Counter(genders)
                identity['gender_estimate'] = gender_counts.most_common(1)[0][0]
        
        # Determine verification status
        if len(identity['possible_names']) > 0:
            identity['verification_status'] = 'partially_verified'
        
        return identity
    
    def _analyze_digital_footprint(self, data):
        """Analyze digital footprint across platforms"""
        footprint = {
            'platforms_found': [],
            'platform_details': {},
            'online_presence_score': 0,
            'activity_indicators': [],
            'privacy_level': 'unknown'
        }
        
        # Analyze each platform
        platform_data = {}
        for match in data['social_matches']:
            platform = match[2]  # platform column
            profile_url = match[3]
            profile_name = match[4]
            bio = match[8]
            confidence = match[6]
            
            if platform not in platform_data:
                platform_data[platform] = {
                    'profiles': [],
                    'highest_confidence': 0
                }
            
            platform_data[platform]['profiles'].append({
                'url': profile_url,
                'name': profile_name,
                'confidence': confidence,
                'bio': bio
            })
            
            if confidence > platform_data[platform]['highest_confidence']:
                platform_data[platform]['highest_confidence'] = confidence
        
        footprint['platforms_found'] = list(platform_data.keys())
        footprint['platform_details'] = platform_data
        
        # Calculate online presence score
        if platform_data:
            avg_confidence = sum(p['highest_confidence'] for p in platform_data.values()) / len(platform_data)
            footprint['online_presence_score'] = round(avg_confidence * len(platform_data) / 5, 2)
        
        # Determine privacy level
        if len(platform_data) >= 4:
            footprint['privacy_level'] = 'low'
            footprint['activity_indicators'].append('High visibility across multiple platforms')
        elif len(platform_data) >= 2:
            footprint['privacy_level'] = 'medium'
        else:
            footprint['privacy_level'] = 'high'
        
        return footprint
    
    def _analyze_locations(self, data):
        """Analyze location data"""
        locations = {
            'detected_environments': [],
            'claimed_locations': [],
            'location_consistency': 'unknown',
            'geographic_pattern': None,
            'confidence': 0
        }
        
        # Get detected environments from media
        env_locations = [m[6] for m in data['media'] if m[6]]
        if env_locations:
            locations['detected_environments'] = list(set(env_locations))
        
        # Get claimed locations from social profiles
        claimed = []
        for match in data['social_matches']:
            location_info = match[7]  # location_info column
            if location_info:
                claimed.append(location_info)
        
        if claimed:
            locations['claimed_locations'] = list(set(claimed))
        
        # Check consistency
        if env_locations and claimed:
            # Simple consistency check
            locations['location_consistency'] = 'partial'
        elif claimed:
            locations['location_consistency'] = 'profile_only'
        elif env_locations:
            locations['location_consistency'] = 'environment_only'
        
        return locations
    
    def _analyze_connections(self, data):
        """Analyze social connections"""
        connections = {
            'network_size_estimate': 0,
            'connection_types': [],
            'influencer_score': 0,
            'network_analysis': 'insufficient_data'
        }
        
        # Estimate network size based on platform presence
        platform_count = len(set([m[2] for m in data['social_matches']]))
        connections['network_size_estimate'] = platform_count * 100  # Rough estimate
        
        # Connection types
        if platform_count > 0:
            connections['connection_types'] = ['social', 'professional'] if platform_count > 2 else ['social']
        
        return connections
    
    def _analyze_behavior(self, data):
        """Analyze behavioral patterns"""
        behavior = {
            'posting_patterns': 'unknown',
            'content_themes': [],
            'activity_times': [],
            'behavioral_flags': [],
            'personality_indicators': []
        }
        
        # Analyze emotions from face detection
        emotions_data = []
        for face in data['faces']:
            emotions = face[7]  # emotions column (JSON)
            if emotions:
                try:
                    emotions_dict = json.loads(emotions)
                    emotions_data.append(emotions_dict)
                except:
                    pass
        
        if emotions_data:
            # Aggregate emotion data
            avg_emotions = {}
            for emotion in emotions_data:
                for key, value in emotion.items():
                    if key not in avg_emotions:
                        avg_emotions[key] = []
                    avg_emotions[key].append(value)
            
            # Calculate averages
            for key in avg_emotions:
                avg_emotions[key] = sum(avg_emotions[key]) / len(avg_emotions[key])
            
            # Determine dominant emotion
            if avg_emotions:
                dominant = max(avg_emotions, key=avg_emotions.get)
                behavior['personality_indicators'].append(f"Dominant emotion: {dominant}")
        
        return behavior
    
    def _assess_risk(self, data):
        """Assess risk level"""
        risk = {
            'overall_risk': 'unknown',
            'risk_score': 0,
            'risk_factors': [],
            'mitigating_factors': [],
            'threat_assessment': 'insufficient_data'
        }
        
        score = 0
        
        # Factors increasing risk
        if len(data['social_matches']) >= 5:
            score += 2
            risk['risk_factors'].append('High visibility on social media')
        
        if len(data['media']) >= 3:
            score += 1
            risk['risk_factors'].append('Multiple media sources')
        
        # Factors decreasing risk
        if len(data['social_matches']) == 0:
            score -= 1
            risk['mitigating_factors'].append('No social media presence found')
        
        # Determine overall risk
        if score >= 3:
            risk['overall_risk'] = 'high'
            risk['threat_assessment'] = 'requires_immediate_attention'
        elif score >= 1:
            risk['overall_risk'] = 'medium'
            risk['threat_assessment'] = 'monitoring_recommended'
        else:
            risk['overall_risk'] = 'low'
            risk['threat_assessment'] = 'standard_procedures'
        
        risk['risk_score'] = max(0, score)
        
        return risk
    
    def _generate_recommendations(self, data):
        """Generate investigation recommendations"""
        recommendations = []
        
        # Based on social matches
        if data['social_matches']:
            top_platforms = list(set([m[2] for m in data['social_matches'][:3]]))
            recommendations.append({
                'priority': 'high',
                'action': f"Investigate profiles on: {', '.join(top_platforms)}",
                'rationale': 'Potential identity matches found'
            })
        
        # Based on locations
        locations = [m[6] for m in data['media'] if m[6]]
        if locations:
            recommendations.append({
                'priority': 'medium',
                'action': f"Verify locations: {', '.join(set(locations))}",
                'rationale': 'Environment analysis indicates possible locations'
            })
        
        # General recommendations
        recommendations.append({
            'priority': 'standard',
            'action': 'Continue monitoring for new uploads and matches',
            'rationale': 'Ongoing investigation'
        })
        
        return recommendations
    
    def _compile_sources(self, data):
        """Compile all data sources"""
        sources = []
        
        # Media sources
        for media in data['media']:
            sources.append({
                'type': 'media_upload',
                'file': media[2],
                'date': media[5],
                'reliability': 'high'
            })
        
        # Social media sources
        for match in data['social_matches']:
            sources.append({
                'type': 'social_media',
                'platform': match[2],
                'url': match[3],
                'confidence': match[6],
                'reliability': 'medium' if match[6] > 0.7 else 'low'
            })
        
        return sources
    
    def _calculate_confidence(self, data):
        """Calculate overall confidence score"""
        scores = []
        
        # Confidence from face detection
        if data['faces']:
            face_confidences = [f[4] for f in data['faces'] if f[4]]
            if face_confidences:
                scores.append(sum(face_confidences) / len(face_confidences))
        
        # Confidence from social matches
        if data['social_matches']:
            match_confidences = [m[6] for m in data['social_matches'] if m[6]]
            if match_confidences:
                scores.append(sum(match_confidences) / len(match_confidences))
        
        if scores:
            return round(sum(scores) / len(scores), 2)
        
        return 0.0
    
    def _basic_report(self, data):
        """Generate basic report"""
        return {
            'suspect_id': data['suspect_id'],
            'media_count': len(data['media']),
            'face_count': len(data['faces']),
            'match_count': len(data['social_matches'])
        }
    
    def _comprehensive_report(self, data):
        """Generate comprehensive report"""
        return self.generate_full_report(data['suspect_id'], 'security_tracker.db')
    
    def _intelligence_report(self, data):
        """Generate intelligence-focused report"""
        report = self.generate_full_report(data['suspect_id'], 'security_tracker.db')
        
        # Focus on intelligence aspects
        return {
            'suspect_id': report['suspect_id'],
            'identity_analysis': report['identity_analysis'],
            'digital_footprint': report['digital_footprint'],
            'location_analysis': report['location_analysis'],
            'risk_assessment': report['risk_assessment'],
            'sources': report['sources']
        }
