# Face Recognition Attendance System (Web-Based)

## Features
- Register new users with face and name
- Mark attendance via face recognition (webcam)
- Attendance records stored in CSV
- Web-based interface (Flask + HTML/JS)

## Setup
1. Clone/download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Open your browser at [http://localhost:5000](http://localhost:5000)

## Deployment
- For local use: see above
- For cloud (Heroku/Render):
  - Add a `Procfile` with: `web: python app.py`
  - Ensure all dependencies are in `requirements.txt`
  - Follow platform-specific deployment steps

## Project Structure
- `app.py` - Main Flask app
- `requirements.txt` - Python dependencies
- `README.md` - This file
- (To be added) `templates/`, `static/`, `attendance.csv`, `known_faces/`

## Next Steps
- Implement registration and attendance pages
- Integrate webcam capture and face recognition
- Store and display attendance records 