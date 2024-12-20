from flask import Flask, render_template, Response
import cv2
import numpy as np
import tensorflow as tf
import mediapipe as mp
import threading
import time
import json
from flask_socketio import SocketIO, emit
import pygame

app = Flask(__name__)
socketio = SocketIO(app)

# Load the trained violence detection model
model = tf.keras.models.load_model('violence_detection_model.h5')

# Initialize Mediapipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Load the Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Load the pre-trained models for gender detection
gender_net = cv2.dnn.readNetFromCaffe(r'C:\Users\Shanta Das\Desktop\html\models\deploy_gender.prototxt', r'C:\Users\Shanta Das\Desktop\html\models\gender_net.caffemodel')
gender_list = ['Male', 'Female']

# Alarm system flags
alarm_triggered = False
violence_duration = 0  # Track duration of detected violence

# Initialize variables for optical flow
prev_gray = None

# Initialize pygame mixer for playing sounds
pygame.mixer.init()

# Initialize video stream
video_stream = None

# Notification flags
notified = {"lone_woman": False, "woman_surrounded": False}

def extract_pose_landmarks(image):
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        landmarks = [[lmk.x, lmk.y, lmk.z] for lmk in results.pose_landmarks.landmark]
        return np.array(landmarks).flatten()
    return None

def gen_frames():
    global prev_gray, video_stream, notified

    if video_stream is None:
        video_stream = cv2.VideoCapture(0)

    ret, frame = video_stream.read()
    if not ret:
        print("Error: Camera not accessible or not found.")
        return
    prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    while video_stream.isOpened():
        ret, frame = video_stream.read()
        if not ret:
            break

        # Calculate optical flow
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            movement = np.mean(magnitude)

            # Determine if movement is violent
            movement_threshold = 2.0  # Adjust this threshold based on your requirement
            label = 'Non-Violent'
            color = (255, 0, 0)  # Blue for non-violent

            if movement > movement_threshold:
                label = 'Violent'
                color = (0, 0, 255)  # Red for violent
                global alarm_triggered, violence_duration
                violence_duration += 1
                if violence_duration > 5:  # Adjust this threshold based on your requirement
                    alarm_triggered = True
            else:
                violence_duration = 0

            # Display label and bounding box
            cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        prev_gray = gray

        # Haar Cascade for face detection and gender detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        detected_genders = []
        for (x, y, w, h) in faces:
            face = frame[y:y+h, x:x+w]
            blob = cv2.dnn.blobFromImage(face, 1.0, (227, 227), (78.4263377603, 87.7689143744, 114.895847746), swapRB=False)
            gender_net.setInput(blob)
            gender_preds = gender_net.forward()
            gender = gender_list[gender_preds[0].argmax()]
            detected_genders.append(gender)
            label = f"{gender}"
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

        # Check for lone women or women surrounded by men
        if 'Female' in detected_genders:
            num_females = detected_genders.count('Female')
            num_males = detected_genders.count('Male')
            if num_females == 1 and num_males == 0 and not notified["lone_woman"]:
                socketio.emit('notification', {'message': 'Lone woman detected'})
                notified["lone_woman"] = True
                notified["woman_surrounded"] = False
            elif num_females > 0 and num_males > num_females and not notified["woman_surrounded"]:
                socketio.emit('notification', {'message': 'Woman surrounded by men'})
                notified["woman_surrounded"] = True
                notified["lone_woman"] = False
        else:
            notified = {"lone_woman": False, "woman_surrounded": False}

        # Display frame
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
    
    video_stream.release()

def alarm_system():
    global alarm_triggered
    while True:
        if alarm_triggered:
            print("Alarm! Person detected alone or violent act detected.")
            try:
                pygame.mixer.music.load("alarm.mp3")
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(1)  # Wait until sound has finished playing
            except Exception as e:
                print(f"Error playing sound: {e}")
            alarm_triggered = False
        time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_video_feed')
def start_video_feed():
    global video_stream, prev_gray
    if video_stream is None:
        video_stream = cv2.VideoCapture(0)
        ret, frame = video_stream.read()
        if not ret:
            return "Error: Camera not accessible or not found.", 500
        prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return ('', 204)  # Return no content

@app.route('/stop_video_feed')
def stop_video_feed():
    global video_stream
    if video_stream is not None:
        video_stream.release()
        video_stream = None
    return ('', 204)  # Return no content

@socketio.on('connect')
def handle_connect():
    print("Client connected")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == '__main__':
    threading.Thread(target=alarm_system).start()  # Start the alarm system in a separate thread
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
