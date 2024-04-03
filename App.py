from flask import Flask, render_template, Response,request,jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL
from datetime import datetime
from Firebase.firebase import Firebase as Fbase

import cv2
import os
import time

app = Flask(__name__)
CORS(app)
app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "cameara is loading"
app.config["BGR"] = 0,255,255

# face detection
faceDetection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# 16 MB max file size
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  

# Upload folder status
app.config['UPLOAD_FOLDER'] = 'Static/uploads'
# accepted file type
app.config['MIMETYPES'] = {'image/png', 'image/jpeg', 'image/gif', 'image/svg+xml', 'image/webp.'}
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}



# API backend =========================================== #

# validate the extentsion
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
        
# face recognition api
@app.route('/face-recognition', methods=['POST'])
def upload_file():
    
    file = request.files['file']
    data = request.form.get('data')
    
    
    # check file if exist
    if file and allowed_file(file.filename):
        
        # check if file name is not malicious
        filename = secure_filename(file.filename)
        
        # save the file
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # read sending file via cv2
        file = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        gray = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = faceDetection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)

        # Check if faces are detected
        if len(faces) == 0:
            return jsonify("No face detected"), 200
        
        # facial reconition
        result = JL().Face_Compare(face=file,threshold=0.6)
        
        # Get current date and time
        current_datetime = datetime.now()

        # Format date as "Month Day Year" (e.g., "April 03 2024")
        formatted_date = current_datetime.strftime("%B %d %Y")

        # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
        formatted_time = current_datetime.strftime("%I:%M %p")
        
        Fbase().firebaseUpdate(
            keyName=formatted_date,
            name=result[0],
            data={formatted_time: data})
        
        app.config["FACE_RESULT"] = "No match detected", ""
        app.config["BGR"] = 0,0,255
            
        if not result[0] == 'No match detected':
            app.config["FACE_RESULT"] = result
            app.config["BGR"] = 0,255,0
        
        
    
        # return the result
        return jsonify(result[0]),200
    else:
        
        # invalid file
        return jsonify({result[0]}),401
        

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