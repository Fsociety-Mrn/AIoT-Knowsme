from flask import Flask, render_template, Response,request,jsonify
from flask_cors import CORS
from datetime import datetime
from Firebase.firebase import Firebase as Fbase

import cv2
import time

app = Flask(__name__)
CORS(app)
app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "cameara is loading"
app.config["BGR"] = 0,255,255


# Facial Detection =========================================== #
@app.route('/video_feed')
def video_feed():

    # load a camera and face detection
    camera = cv2.VideoCapture(0)
    face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(Facial_Detection(camera=camera, face_detector=face_detection), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    
def Facial_Detection(camera=None, face_detector=None):
    
    # Initialize the timer and the start time
    timer = 0
    start_time = time.time()
    
    while True:
        
        # Capture a frame from the camera
        ret, frame = camera.read()
        
        if not ret:
            app.config["CAMERA_STATUS"] = "camera is not detected"
            break
        
     

        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)


        app.config["CAMERA_STATUS"] = "No Face is detected"
    
        for (x, y, w, h) in faces:
            
            app.config["CAMERA_STATUS"] = "FACIAL RECOGNITION"

            
            # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()
            
            # Check if 2 seconds have elapsed since the last send
            if timer >= 5:
                app.config["BGR"] = 0,255,255
                app.config["FACE_RESULT"] = "",""
                
                # Reset the timer and the start time
                timer = 0
                start_time = time.time()
           
            
            B,G,R = app.config["BGR"]          
            Name,percent = app.config["FACE_RESULT"]
                          
            # Get the coordinates of the face,draw rectangele and put text
            cv2.rectangle(frame, (x, y), (x+w, y+h), (B,G,R), 2)
            cv2.putText(frame,Name + " " + str(percent),(x -60,y+h+30),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
            

            
        _, frame_encoded  = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')


# homepage =========================================== #
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        port=1000)