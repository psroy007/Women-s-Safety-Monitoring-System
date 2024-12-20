## Women's Safety Monitoring System

# Overview

This Women's Safety Monitoring System leverages AI and CCTV cameras to detect potential threats to women's safety in real-time. The model analyzes the surrounding environment and identifies if a woman is being surrounded by men, possibly in distress or forced conditions. If such an incident is detected, the system automatically starts recording and alerts nearby police stations. Additionally, the system incorporates GIS mapping, allowing law enforcement to view the exact location of the incident.

# Key Features

-- Real-time Monitoring: CCTV cameras stream live footage, and the system continuously analyzes gender, actions, and expressions to detect suspicious behavior.

-- Alert System: The system sends automatic notifications to the police if a woman is surrounded or is in distress (e.g., being gagged or forced).
-- Database Storage: Video footage of incidents is stored in a secure database for future analysis and reference.
-- GIS Mapping: Police can track the exact location of the incident in real-time on a GIS map.
-- Historical Data: Previous crime data is stored, and the system can detect if a person involved in a current incident matches a criminal record.

# Technologies Used

-- SQLite: For storing recorded video footage and relevant data.
-- HTML, CSS, JS: Frontend and backend of the web application, which displays live footage, recorded videos, and GIS mapping.
-- Mediapipe: For recognizing hand gestures and body postures to detect if a woman is under distress.
-- OpenCV: To operate the CCTV cameras and handle video streaming.
-- Flask: To host the web application and handle backend server-side requests.

# Installation

# Prerequisites

-- Python 3.x
-- Flask
-- SQLite3
-- OpenCV
-- Mediapipe

Additional libraries for video processing and GIS mapping (e.g., folium, opencv-python, pandas, etc.)

# Step 1: Clone the Repository

            git clone https://github.com/your-repository-link.git
            cd your-repository-folder

# Step 2: Install Dependencies

Ensure you have all the required libraries installed using pip:

            pip install -r requirements.txt

# Step 3: Database Setup

Run the following script to initialize the SQLite database and store required tables:

            python database_setup.py

# Step 4: Run the Application

To start the web application, run the Flask server:

            python app.py

The application will now be live at http://127.0.0.1:5000/.

# Usage

# Login Page

When you access the web application, you will be prompted for a secret key/password to access the login page.

# Login

After entering the secret key, log in with the admin or police credentials to gain access to the dashboard.

# Dashboard

Once logged in, you will be directed to the Dashboard, which provides:

-- Live CCTV Feed: Choose a CCTV camera and view its live stream.
-- Data Collection: View all recorded footage where incidents were detected.
-- GIS Mapping: View the real-time location of the CCTV and incidents related to the detected crime.

# Admin/Police Roles

-- Admin: Has the ability to view recorded video footage, live streams, and incident data.
-- Police: Can view live locations on the GIS map and receive crime alerts.

# Alert System

If the system detects a woman being surrounded by men or in a forced situation, it will:

-- Start recording and save the footage to the database.
-- Automatically send an alert to the nearby police station.
-- Send notifications to the police with the GPS location of the incident on the GIS map.

# Dataset and Model Training

The model has been trained on various datasets containing images and videos of people in public spaces to detect the following:

-- Gender recognition
-- Identifying distress signals from body language and hand gestures
-- Recognizing forced actions (e.g., gagging, physical restraint)

The model uses a combination of deep learning and computer vision to analyze these factors and make real-time decisions.

# Security

-- Login Security: The application requires a secret key for access and ensures that only authorized personnel can log in to the system.
-- Data Encryption: Video footage and alerts are securely stored and encrypted in the SQLite database.


# Contributing

If you'd like to contribute to this project, feel free to fork the repository and submit pull requests. Contributions are always welcome to improve women's safety and enhance the system’s effectiveness.

# Future Enhancements

-- Integrate with more advanced AI models for even more accurate distress detection.
-- Implement facial recognition for further verification of potential threats.
-- Integrate real-time communication with police officers for quicker response times.

# License

This project is licensed under the MIT License - see the LICENSE file for details.

Note: This system is designed for ethical use in protecting women's safety and should be deployed with privacy and consent considerations in mind.
