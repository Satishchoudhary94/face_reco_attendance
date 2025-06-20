from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory, session
import os
import base64
from datetime import datetime
import face_recognition
import numpy as np
import pandas as pd
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages

# Directory to store registered faces
KNOWN_FACES_DIR = 'known_faces'
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)

ATTENDANCE_CSV = 'attendance.csv'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        face_image_data = request.form['face_image']
        if not name or not face_image_data:
            flash('Name and face image are required!')
            return redirect(url_for('register'))
        # Parse base64 image
        header, encoded = face_image_data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        # Save image
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(KNOWN_FACES_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(img_bytes)
        flash('Registration successful!')
        return redirect(url_for('register'))
    return render_template('register.html')

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    matched_name = None
    matched_image = None
    already_marked = False
    if request.method == 'POST':
        face_image_data = request.form['face_image']
        if not face_image_data:
            flash('Face image is required!')
            return redirect(url_for('attendance'))
        # Parse base64 image
        header, encoded = face_image_data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        # Save temp image
        temp_path = 'temp_attendance.png'
        with open(temp_path, 'wb') as f:
            f.write(img_bytes)
        # Load and encode the uploaded face
        try:
            unknown_img = face_recognition.load_image_file(temp_path)
            unknown_encodings = face_recognition.face_encodings(unknown_img)
            if not unknown_encodings:
                flash('No face detected!')
                os.remove(temp_path)
                return redirect(url_for('attendance'))
            unknown_encoding = unknown_encodings[0]
        except Exception as e:
            flash('Error processing image!')
            os.remove(temp_path)
            return redirect(url_for('attendance'))
        # Compare with known faces
        for file in os.listdir(KNOWN_FACES_DIR):
            if file.endswith('.png'):
                name = file.rsplit('_', 1)[0]
                known_img = face_recognition.load_image_file(os.path.join(KNOWN_FACES_DIR, file))
                known_encodings = face_recognition.face_encodings(known_img)
                if known_encodings and face_recognition.compare_faces([known_encodings[0]], unknown_encoding)[0]:
                    matched_name = name
                    matched_image = file
                    break
        os.remove(temp_path)
        if matched_name:
            # Log attendance
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if not os.path.exists(ATTENDANCE_CSV):
                df = pd.DataFrame(columns=['Name', 'Timestamp'])
            else:
                df = pd.read_csv(ATTENDANCE_CSV)
            today = datetime.now().strftime('%Y-%m-%d')
            already_marked = ((df['Name'] == matched_name) & (df['Timestamp'].str.startswith(today))).any()
            if not already_marked:
                new_row = pd.DataFrame([{'Name': matched_name, 'Timestamp': now}])
                df = pd.concat([df, new_row], ignore_index=True)
                df.to_csv(ATTENDANCE_CSV, index=False)
                flash(f'Attendance marked for {matched_name}!')
            else:
                flash(f'Attendance already marked for {matched_name} today!')
        else:
            flash('Face not recognized!')
        return render_template('attendance.html', matched_name=matched_name, matched_image=matched_image, already_marked=already_marked)
    return render_template('attendance.html', matched_name=None, matched_image=None, already_marked=False)

@app.route('/records')
def records():
    if not os.path.exists(ATTENDANCE_CSV):
        flash('No attendance records found!')
        return render_template('records.html', records=[])
    df = pd.read_csv(ATTENDANCE_CSV)
    records = df.to_dict('records')
    return render_template('records.html', records=records)

@app.route('/download')
def download():
    if not os.path.exists(ATTENDANCE_CSV):
        flash('No attendance records to download!')
        return redirect(url_for('records'))
    return send_file(ATTENDANCE_CSV, as_attachment=True)

@app.route('/known_faces/<filename>')
def known_face_image(filename):
    return send_from_directory(KNOWN_FACES_DIR, filename)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('admin_login'))

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in as admin.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@admin_required
def admin_dashboard():
    # Example stats (can be expanded)
    user_count = len([f for f in os.listdir(KNOWN_FACES_DIR) if f.endswith('.png')])
    attendance_count = 0
    if os.path.exists(ATTENDANCE_CSV):
        attendance_count = len(pd.read_csv(ATTENDANCE_CSV))
    return render_template('admin_dashboard.html', user_count=user_count, attendance_count=attendance_count)

if __name__ == '__main__':
    app.run(debug=False) 