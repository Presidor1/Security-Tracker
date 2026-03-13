# Quick Start Guide

## Security Intelligence & Suspect Tracking System

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation (5 minutes)

1. **Navigate to the project directory:**
   ```bash
   cd security_tracker
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: This may take 5-10 minutes as `face-recognition` and `dlib` need to compile.

3. **Run the system:**
   ```bash
   python start.py
   ```

4. **Open your browser:**
   ```
   http://localhost:5000
   ```

### First Time Setup

The system will automatically:
- Create the database
- Set up required directories
- Initialize all modules

### Basic Usage

#### 1. Upload Media
- Click "Upload Media" on the dashboard
- Select an image or video file
- Click "Upload & Analyze"

#### 2. View Results
- Go to the Dashboard
- Click on the suspect ID
- View extracted faces, location analysis, and social matches

#### 3. Search Faces
- On the suspect profile, go to the "Faces" tab
- Click "Search on Social Media" for any face
- View matches on various platforms

#### 4. Generate Reports
- On the suspect profile, click "Generate Report"
- View comprehensive intelligence reports

### Demo Data

To generate sample data for testing:

```bash
python generate_demo_data.py
```

To clear demo data:

```bash
python generate_demo_data.py --clear
```

### Testing

Run system tests:

```bash
python test_system.py
```

### Common Commands

```bash
# Start server (default)
python start.py

# Start with custom port
python start.py --port 8080

# Start in debug mode
python start.py --debug

# Run setup only
python start.py --setup
```

### Troubleshooting

**Issue: `dlib` installation fails**
- Windows: Install Visual Studio Build Tools
- Linux: `sudo apt-get install cmake`
- Mac: `brew install cmake`

**Issue: Face recognition not working**
- Ensure images have clear, visible faces
- Check that faces are well-lit and facing forward

**Issue: Database errors**
- Delete `security_tracker.db` and restart
- The database will be recreated automatically

### Features Overview

| Feature | Description |
|---------|-------------|
| Media Upload | Images (JPG, PNG, GIF) & Videos (MP4, AVI, MOV) |
| Face Extraction | Automatic face detection and extraction |
| Location Analysis | Environment analysis for location clues |
| Social Search | Search faces across social media platforms |
| Intelligence Reports | Comprehensive suspect profiling |
| API Access | RESTful API for integration |

### File Structure

```
security_tracker/
├── app.py              # Main application
├── start.py            # Startup script
├── config.py           # Configuration
├── modules/            # Analysis modules
│   ├── face_analyzer.py
│   ├── environment_analyzer.py
│   ├── social_search.py
│   └── suspect_profiler.py
├── templates/          # HTML templates
├── static/            # Uploaded files & results
│   ├── uploads/
│   ├── faces/
│   └── results/
└── utils/             # Helper utilities
```

### Support

For issues or questions:
1. Check the README.md for detailed documentation
2. Run `python test_system.py` to diagnose issues
3. Review error logs in the console

---

**Ready to start tracking suspects!** 🎯
