# from flask import Flask, render_template, Response
# import cv2
# import numpy as np
# import tensorflow as tf
# import mediapipe as mp
# import threading
# import time
# import json
# from flask_socketio import SocketIO, emit
# import pygame


# app = Flask(__name__)
# socketio = SocketIO(app)

# # Load the trained violence detection model
# model = tf.keras.models.load_model(r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\violence_detection_model.h5')

# # Initialize Mediapipe Pose
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
# mp_drawing = mp.solutions.drawing_utils

# # Load the Haar Cascade for face detection
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # Load the pre-trained models for gender detection
# gender_net = cv2.dnn.readNetFromCaffe(r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\deploy_gender.prototxt', r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\gender_net.caffemodel')
# gender_list = ['Male', 'Female']

# # Alarm system flags
# alarm_triggered = False
# violence_duration = 0  # Track duration of detected violence

# # Initialize variables for optical flow
# prev_gray = None

# # Initialize pygame mixer for playing sounds
# pygame.mixer.init()

# # Initialize video stream
# video_stream = None

# def extract_pose_landmarks(image):
#     image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = pose.process(image_rgb)
#     if results.pose_landmarks:
#         landmarks = [[lmk.x, lmk.y, lmk.z] for lmk in results.pose_landmarks.landmark]
#         return np.array(landmarks).flatten()
#     return None

# def gen_frames():
#     global prev_gray, video_stream

#     if video_stream is None:
#         video_stream = cv2.VideoCapture(0)
#         ret, frame = video_stream.read()
#         prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     while video_stream.isOpened():
#         ret, frame = video_stream.read()
#         if not ret:
#             break

#         # Calculate optical flow
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#         if prev_gray is not None:
#             flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
#             magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
#             movement = np.mean(magnitude)

#             # Determine if movement is violent
#             movement_threshold = 2.0  # Adjust this threshold based on your requirement
#             label = 'Non-Violent'
#             color = (255, 0, 0)  # Blue for non-violent

#             if movement > movement_threshold:
#                 label = 'Violent'
#                 color = (0, 0, 255)  # Red for violent
#                 global alarm_triggered, violence_duration
#                 violence_duration += 1
#                 if violence_duration > 5:  # Adjust this threshold based on your requirement
#                     alarm_triggered = True
#             else:
#                 violence_duration = 0

#             # Display label and bounding box
#             cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

#         prev_gray = gray

#         # Haar Cascade for face detection and gender detection
#         faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
#         detected_genders = []
#         for (x, y, w, h) in faces:
#             face = frame[y:y+h, x:x+w]
#             blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
#             gender_net.setInput(blob)
#             gender_preds = gender_net.forward()
#             gender = gender_list[gender_preds[0].argmax()]
#             detected_genders.append(gender)
#             label = f"{gender}"
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
#             cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

#         # Check for lone women or women surrounded by men
#         print(f"Detected genders: {detected_genders}")  # Debugging statement
#         if 'Female' in detected_genders:
#             num_females = detected_genders.count('Female')
#             num_males = detected_genders.count('Male')
#             print(f"Number of females: {num_females}, Number of males: {num_males}")  # Debugging statement
#             if num_females == 1 and num_males == 0:
#                 print("Lone woman detected")  # Debugging statement
#                 socketio.emit('notification', {'message': 'Lone woman detected'})
#             elif num_females > 0 and num_males > num_females:
#                 print("Woman surrounded by men")  # Debugging statement
#                 socketio.emit('notification', {'message': 'Woman surrounded by men'})

#         # Display frame
#         _, buffer = cv2.imencode('.jpg', frame)
#         frame = buffer.tobytes()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

#     video_stream.release()

# def alarm_system():
#     global alarm_triggered
#     while True:
#         if alarm_triggered:
#             print("Alarm! Person detected alone or violent act detected.")
#             try:
#                 pygame.mixer.music.load("alarm.mp3")
#                 pygame.mixer.music.play()
#                 while pygame.mixer.music.get_busy():
#                     time.sleep(1)  # Wait until sound has finished playing
#             except Exception as e:
#                 print(f"Error playing sound: {e}")
#             alarm_triggered = False
#         time.sleep(1)

# @app.route('/')
# def index():
#     return render_template(r'dashboard.html')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/start_video_feed')
# def start_video_feed():
#     global video_stream, prev_gray
#     if video_stream is None:
#         video_stream = cv2.VideoCapture(0)
#         ret, frame = video_stream.read()
#         prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     return ('', 204)  # Return no content

# @socketio.on('connect')
# def handle_connect():
#     print("Client connected")

# @socketio.on('disconnect')
# def handle_disconnect():
#     print("Client disconnected")

# if __name__ == '__main__':
#     threading.Thread(target=alarm_system).start()  # Start the alarm system in a separate thread
#     socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)



from flask import Flask, render_template, Response, send_from_directory
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import threading
import time
import os
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Load the trained violence detection model
model = tf.keras.models.load_model(r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\violence_detection_model.h5')

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the pre-trained models for gender detection
gender_net = cv2.dnn.readNetFromCaffe(
    r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\deploy_gender.prototxt',
    r'D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\model\gender_net.caffemodel'
)
gender_list = ['Male', 'Female']

# Initialize variables
violence_duration = 0  # Track duration of detected violence
prev_gray = None
video_stream = None
out = None
recording_start_time = 1
# video_directory = "recorded_videos"
video_directory = r"D:\SIH-2024-Project---Women-Safety-USing-CCTV--main (2)\flask\recorded_videos"

# Ensure video directory exists
os.makedirs(video_directory, exist_ok=True)

# Database Setup: Create a table to store video details
def create_db():
    conn = sqlite3.connect('video_uploads.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    filepath TEXT)''')
    conn.commit()
    conn.close()

# Call create_db to ensure the table exists
create_db()

def extract_pose_landmarks(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        landmarks = [[lmk.x, lmk.y, lmk.z] for lmk in results.pose_landmarks.landmark]
        return np.array(landmarks).flatten()
    return None

def save_video(filename, filepath):
    """Save video details in the database"""
    conn = sqlite3.connect('video_uploads.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO videos (filename, filepath) VALUES (?, ?)''', (filename, filepath))
    
    conn.commit()
    conn.close()
    print(f"Video saved in database: {filename}")

def gen_frames():
    global prev_gray, video_stream, out, recording_start_time

    if video_stream is None:
        video_stream = cv2.VideoCapture(0)
        ret, frame = video_stream.read()
        prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    while video_stream.isOpened():
        ret, frame = video_stream.read()
        if not ret:
            break

        # Calculate optical flow (movement)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            movement = np.mean(magnitude)

            # Determine if movement is violent
            movement_threshold = 2.0
            label = 'Non-Violent'
            color = (255, 0, 0)

            if movement > movement_threshold:
                label = 'Violent'
                color = (0, 0, 255)
                global violence_duration, recording_start_time

                violence_duration += 1
                if violence_duration > 5:
                    if out is None:
                        # Start recording (now in MP4 format)
                        filename = f"{int(time.time())}_video.mp4"  # Save as MP4
                        filepath = os.path.join(video_directory, filename)
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use MP4 codec
                        out = cv2.VideoWriter(filepath, fourcc, 20.0, (640, 480))
                        recording_start_time = time.time()
                        print("Recording started.")

                if recording_start_time is not None and time.time() - recording_start_time >= 10:
                    # Stop recording after 10 seconds
                    if out is not None:
                        out.release()
                        out = None
                        # Save the video details to the database
                        filename = f"{int(time.time())}_video.mp4"  # Save as MP4
                        filepath = os.path.join(video_directory, filename)
                        save_video(filename, filepath)
                        recording_start_time = None
                        print("Recording stopped after 10 seconds.")

            else:
                violence_duration = 0

            # Display label and bounding box
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        prev_gray = gray

        # Write the processed frame to the video file if recording
        if out is not None:
            out.write(frame)

        # Display frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

    video_stream.release()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/forgot')
def forgot():
    return render_template('forgot-password.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    # Get all video files from recorded_videos folder
    video_files = os.listdir(video_directory)
    video_files = [f for f in video_files if f.endswith('.mp4')]  # Filter .avi files
    return render_template('dashboard.html', videos=video_files)

@app.route('/hotspots')
def hotspots():
    return render_template('hotspots.html')

@app.route('/location')
def location():
    return render_template('location_map.html')


@app.route('/live-camera')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/videos/<filename>')
def video(filename):
    return send_from_directory(video_directory, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)