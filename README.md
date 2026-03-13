# Security Intelligence & Suspect Tracking System

A comprehensive Python-based security platform for tracking suspects through facial recognition, environmental analysis, and social media intelligence gathering.

## Features

### Core Capabilities

1. **Media Upload System**
   - Support for images (JPG, PNG, GIF, BMP)
   - Support for videos (MP4, AVI, MOV, MKV)
   - Maximum file size: 500MB
   - Automatic suspect ID generation

2. **Facial Recognition Engine**
   - Automatic face detection and extraction
   - Face encoding for comparison
   - Age and gender estimation
   - Emotion detection
   - Confidence scoring

3. **Environmental Analysis**
   - Location detection from background analysis
   - Color and texture analysis
   - Architectural feature detection
   - Object detection (people, vehicles)
   - Landmark identification

4. **Social Media Intelligence**
   - Reverse image search across platforms
   - Profile matching on:
     - Facebook
     - Instagram
     - Twitter
     - LinkedIn
     - TikTok
   - Public records search
   - Match confidence scoring

5. **Suspect Profiling**
   - Comprehensive intelligence reports
   - Identity analysis
   - Digital footprint tracking
   - Location history
   - Social connections
   - Risk assessment
   - Behavioral analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- CMake (for dlib compilation)
- Visual Studio Build Tools (Windows) or GCC (Linux/Mac)

### Step 1: Clone/Extract the Project

```bash
cd security_tracker
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

Note: Installing `face-recognition` and `dlib` may take several minutes as they need to compile.

### Step 3: Run Setup

```bash
python start.py --setup
```

### Step 4: Start the Server

```bash
python start.py
```

Or with custom options:

```bash
python start.py --host 0.0.0.0 --port 8080 --debug
```

## Usage

### Accessing the Web Interface

Once the server is running, open your browser and navigate to:

```
http://localhost:5000
```

### Uploading Media

1. Click "Upload Media" or go to `/upload`
2. Enter a Suspect ID (optional - will auto-generate if blank)
3. Select an image or video file
4. Click "Upload & Analyze"

The system will automatically:
- Extract faces from the media
- Analyze the environment for location clues
- Search for matching faces on social media
- Generate an intelligence report

### Viewing Suspect Profiles

1. Go to the Dashboard
2. Click on any suspect ID in the "Recent Suspects" table
3. View tabs for:
   - Overview (statistics and activity)
   - Media (all uploaded files)
   - Faces (extracted facial images)
   - Social Matches (platform matches)
   - Reports (generated intelligence reports)

### Searching the Database

Use the search box on the dashboard to search by:
- Suspect ID
- Name
- Keywords
- Platform
- Location

### API Endpoints

The system provides REST API endpoints:

- `GET /api/suspects` - List all suspects
- `GET /api/search?q=query&platform=platform&location=location` - Search suspects
- `POST /search_face` - Search a face on social media
- `GET /generate_report/<suspect_id>` - Generate intelligence report

## Project Structure

```
security_tracker/
├── app.py                      # Main Flask application
├── start.py                    # Startup script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── security_tracker.db         # SQLite database (created on first run)
├── modules/
│   ├── __init__.py
│   ├── face_analyzer.py       # Facial recognition module
│   ├── environment_analyzer.py # Location detection module
│   ├── social_search.py        # Social media search module
│   └── suspect_profiler.py     # Intelligence report generator
├── static/
│   ├── uploads/               # Uploaded media files
│   ├── faces/                 # Extracted face images
│   └── results/               # Generated reports
└── templates/
    ├── base.html              # Base template
    ├── index.html             # Dashboard
    ├── upload.html            # Upload page
    ├── suspect_profile.html   # Suspect profile view
    └── analysis_result.html   # Analysis results view
```

## Database Schema

### Tables

1. **suspects** - Main suspect records
   - suspect_id (unique identifier)
   - created_at, updated_at (timestamps)
   - status, risk_level, notes

2. **media_uploads** - Uploaded media files
   - File metadata and paths
   - Analysis status
   - Detected location

3. **extracted_faces** - Extracted facial images
   - Face image paths
   - Face encodings
   - Confidence scores
   - Demographic estimates

4. **social_matches** - Social media matches
   - Platform information
   - Profile URLs and names
   - Match confidence
   - Location and bio data

5. **intelligence_reports** - Generated reports
   - Report type and content
   - Sources
   - Generation timestamp

## Configuration

### Environment Variables

- `FLASK_ENV` - Set to `development` for debug mode
- `FLASK_SECRET_KEY` - Secret key for session management
- `MAX_CONTENT_LENGTH` - Maximum upload size (default: 500MB)

### Customizing Analysis

Edit the module files in `modules/` to customize:
- Face detection parameters
- Location analysis algorithms
- Social media platforms
- Report templates

## Security Considerations

⚠️ **IMPORTANT**: This system is designed for authorized security personnel only.

- All data should be treated as confidential
- Implement proper access controls in production
- Use HTTPS in production environments
- Regularly backup the database
- Comply with local privacy laws and regulations

## Limitations

- Face recognition accuracy depends on image quality
- Social media search requires public profiles
- Location detection is approximate
- Processing time increases with file size
- Some platforms may block automated searches

## Troubleshooting

### Common Issues

1. **dlib installation fails**
   - Install CMake: `pip install cmake`
   - Install Visual Studio Build Tools (Windows)

2. **Face recognition not working**
   - Ensure images have clear, visible faces
   - Check that face_recognition module is installed

3. **Upload fails**
   - Check file size (max 500MB)
   - Verify file format is supported
   - Check directory permissions

4. **Social search returns no results**
   - Results depend on public profile availability
   - Some platforms may block automated searches

## Future Enhancements

- [ ] Real-time video analysis
- [ ] Integration with more social platforms
- [ ] Advanced geolocation services
- [ ] Machine learning model improvements
- [ ] Mobile app companion
- [ ] Multi-language support
- [ ] Advanced reporting with visualizations

## License

This software is for authorized security use only. Unauthorized access or use is prohibited.

## Support

For technical support or questions, contact your system administrator.

---

**Confidential - Authorized Use Only**
