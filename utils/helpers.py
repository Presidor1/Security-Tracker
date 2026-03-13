"""
Helper Utilities for Security Tracker
Common functions used across modules
"""

import os
import hashlib
import base64
from datetime import datetime
import json
import re

def generate_unique_id(prefix="ID"):
    """Generate a unique identifier with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:6]
    return f"{prefix}_{timestamp}_{random_suffix}"

def hash_file(filepath):
    """Generate MD5 hash of a file"""
    hash_md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def encode_image_base64(image_path):
    """Encode image to base64 string"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"[✗] Error encoding image: {str(e)}")
        return None

def decode_image_base64(base64_string, output_path):
    """Decode base64 string to image file"""
    try:
        image_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(f"[✗] Error decoding image: {str(e)}")
        return False

def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    # Remove any path components
    filename = os.path.basename(filename)
    
    # Replace spaces with underscores
    filename = filename.replace(' ', '_')
    
    # Remove any non-alphanumeric characters except underscores, dots, and hyphens
    filename = re.sub(r'[^a-zA-Z0-9_.-]', '', filename)
    
    # Ensure filename is not too long
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200] + ext
    
    return filename

def format_timestamp(timestamp_str, format='%Y-%m-%d %H:%M:%S'):
    """Format timestamp string for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime(format)
    except:
        return timestamp_str

def time_ago(timestamp_str):
    """Convert timestamp to 'time ago' format"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif seconds < 3600:
            return f"{int(seconds/60)} minutes ago"
        elif seconds < 86400:
            return f"{int(seconds/3600)} hours ago"
        elif seconds < 604800:
            return f"{int(seconds/86400)} days ago"
        elif seconds < 2592000:
            return f"{int(seconds/604800)} weeks ago"
        elif seconds < 31536000:
            return f"{int(seconds/2592000)} months ago"
        else:
            return f"{int(seconds/31536000)} years ago"
    except:
        return timestamp_str

def truncate_text(text, max_length=100, suffix='...'):
    """Truncate text to specified length"""
    if not text:
        return ''
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + suffix

def parse_json_safe(json_string, default=None):
    """Safely parse JSON string"""
    if not json_string:
        return default
    try:
        return json.loads(json_string)
    except:
        return default

def format_file_size(size_bytes):
    """Format file size in human-readable format"""
    if size_bytes == 0:
        return "0 Bytes"
    
    size_names = ["Bytes", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def validate_email(email):
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_url(url):
    """Validate URL format"""
    pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    return re.match(pattern, url) is not None

def clean_text(text):
    """Clean and normalize text"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?-]', '', text)
    
    return text.strip()

def extract_hashtags(text):
    """Extract hashtags from text"""
    if not text:
        return []
    return re.findall(r'#\w+', text)

def extract_mentions(text):
    """Extract @mentions from text"""
    if not text:
        return []
    return re.findall(r'@\w+', text)

def extract_urls(text):
    """Extract URLs from text"""
    if not text:
        return []
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def calculate_similarity_score(str1, str2):
    """Calculate similarity score between two strings (0-1)"""
    if not str1 or not str2:
        return 0.0
    
    # Convert to lowercase
    str1 = str1.lower()
    str2 = str2.lower()
    
    # Simple character-based similarity
    len1, len2 = len(str1), len(str2)
    max_len = max(len1, len2)
    
    if max_len == 0:
        return 1.0
    
    # Calculate Levenshtein distance (simplified)
    distance = levenshtein_distance(str1, str2)
    similarity = 1 - (distance / max_len)
    
    return max(0, similarity)

def levenshtein_distance(s1, s2):
    """Calculate Levenshtein distance between two strings"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

def mask_sensitive_data(text, mask_char='*'):
    """Mask sensitive information in text"""
    if not text:
        return ''
    
    # Mask email addresses
    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
    text = re.sub(email_pattern, lambda m: mask_char * len(m.group()), text)
    
    # Mask phone numbers
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    text = re.sub(phone_pattern, lambda m: mask_char * len(m.group()), text)
    
    # Mask SSN
    ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'
    text = re.sub(ssn_pattern, lambda m: mask_char * len(m.group()), text)
    
    return text

def get_file_extension(filename):
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_image_file(filename):
    """Check if file is an image"""
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return get_file_extension(filename) in image_extensions

def is_video_file(filename):
    """Check if file is a video"""
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv'}
    return get_file_extension(filename) in video_extensions

def create_directory_if_not_exists(directory_path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        return True
    return False

def get_directory_size(directory_path):
    """Get total size of directory in bytes"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def count_files_in_directory(directory_path, extensions=None):
    """Count files in directory, optionally filtered by extensions"""
    count = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for f in filenames:
            if extensions is None or any(f.endswith(ext) for ext in extensions):
                count += 1
    return count

def batch_process(items, process_func, batch_size=10):
    """Process items in batches"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = [process_func(item) for item in batch]
        results.extend(batch_results)
    return results

def retry_operation(operation, max_retries=3, delay=1):
    """Retry an operation with exponential backoff"""
    import time
    
    for attempt in range(max_retries):
        try:
            return operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(delay * (2 ** attempt))
    
    return None
