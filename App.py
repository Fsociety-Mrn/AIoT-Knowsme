
from Firebase.firebase import Firebase as Fbase
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL

from flask_cors import CORS
from flask import Flask, render_template, Response,request,jsonify
from datetime import datetime

import cv2
import os
import time
import shutil
import numpy as np
import serial

app = Flask(__name__)
 
CORS(app, resources={r"/*": {"origins": ["http://127.0.0.1:1000", "http://192.168.0.101:1000"]}})


app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "camera is loading",True
app.config["BGR"] = 0,255,255
app.config["training"] = False


@app.route('/api/serial-ir', methods=['GET'])
def serial_ir():
    
    try:
        # Define the serial port and baud rate
        ser = serial.Serial('COM8', 9600, timeout=1)  # Replace 'COM3' with the correct port name
        ser.reset_input_buffer()
        time.sleep(2)
        ser.flush()
        data = ser.readline().decode('utf-8').rstrip()
        ser.close()
        return jsonify(data)
    except:
        return jsonify(0)


faceDetection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

# face recognition api | Time in  =========================================== #
@app.route('/face_recognition', methods=['GET'])
def face_recognition():
    name,percent = app.config["FACE_RESULT"] 
    message,status = app.config["CAMERA_STATUS"]
    return jsonify({
        "camera_status": message,
        "status": status,
        "percent": percent,
        "name": name
    }),200

@app.route('/api/facial-status', methods=['GET'])
def status():
    return jsonify(app.config["training"])

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/received-images', methods=['POST'])
def received_images(): 
    
    filepath = app.config['REGISTER_FACIAL']
    filename = f'{len(os.listdir(filepath)) + 1}.png'
    file = request.files.get('file')

    if not file:
        return jsonify({
            'message': 'No file in request'
        }), 400


    if not allowed_file(file.filename):
        return jsonify({
            'message': 'Invalid file type. Allowed file types are png, jpeg, jpg, gif.'
        }), 400
    
    npImage = np.frombuffer(file.read(), np.uint8)
    image = cv2.imdecode(npImage, cv2.IMREAD_COLOR)

    cv2.imwrite(f"{filepath}/{filename}", image)
    
    app.config["training"] = True if len(os.listdir(filepath)) == 20 else False
    return jsonify({
        'message': f'file successfully save: {filepath}/{filename}'
    })
        

def remove_folder():
    location = "Jolo_Recognition/Registered-Faces"
    data = Fbase().firebaseRead("Account")
    
    # Get a list of all folder names from data
    names_to_keep = [each['name'] for _, each in data.items()]
    
    # List all folders in the directory
    all_folders = os.listdir(location)  # Replace "Your_Folder_Path_Here" with the actual path
    
    for folder_name in all_folders:
        if folder_name not in names_to_keep:
            folder_path = os.path.join(location, folder_name)  # Replace "Your_Folder_Path_Here" with the actual path
            if os.path.isdir(folder_path):
                shutil.rmtree(folder_path)
                print(f"Folder '{folder_name}' removed.")
            else:
                print(f"Path '{folder_path}' is not a directory.")
        else:
            print(f"Folder '{folder_name}' exists in data, skipping removal.")

@app.route('/api/id-verifications', methods=['POST']) 
def id_verifications():
    
    ID = request.json
    
    if not ID['employee_id']:
        return jsonify({"message": 'enter your Employee ID'}), 400
    
    result, name = Fbase().firebaseCheck_ID(ID['employee_id'])
    if not result:
        return jsonify({"message": 'Invalid Employee ID'}), 400

    remove_folder()

    folder_name = f"{str(name).capitalize()}"

    path = f"Jolo_Recognition/Registered-Faces/{folder_name}"

    if os.path.exists(path):
        shutil.rmtree(path)

    os.makedirs(path)
    app.config['REGISTER_FACIAL'] = path
    app.config["training"] = "process"
    return jsonify({"message": f"Folder {path} created successfully"}), 200

@app.route('/facial_training', methods=['GET'])
def facial_training():

    remove_folder()

    result = JL().Face_Train()
    app.config["training"] = False
    return jsonify(result),200
    
# Get temperature status =========================================== #
@app.route('/check', methods=['GET'])
def CHECK():
    return jsonify("hello friend"),200

# Facial Detection =========================================== #
@app.route('/video_feed')
def video_feed():

    app.config["FACE_RESULT"] = "",""
    app.config["CAMERA_STATUS"] = "camera is loading",True
    app.config["BGR"] = 0,255,255

    # load a camera and face detection
    camera = cv2.VideoCapture(0)
    face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(Facial_Detection(camera=camera, face_detector=face_detection), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')

def face_crop(frame,face_height,face_width,x,y):
    
    try:
        scale_factor = 1.2
        new_w = int(face_width * scale_factor)
        new_h = int(face_height * scale_factor)

        new_x = max(0, x - (new_w - face_width) // 2)
        new_y = max(0, y - (new_h - face_height) // 2)

        faceCrop = frame[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
                    
        return faceCrop
    except:
        pass
    return None


def facialRecognition(frame):

    result = JL().Face_Compare(face=frame,threshold=0.55)

    app.config["FACE_RESULT"] = result
    app.config["BGR"] = (0,0,255) if result[0] == "No match detected" else (0,255,0 )
    app.config["CAMERA_STATUS"] = ("Access Denied",True) if result[0] == "No match detected" else ("Access Granted",False) 
 
    # Get current date and time
    current_datetime = datetime.now()

    # Format date as "Month Day Year" (e.g., "April 03 2024")
    formatted_date = current_datetime.strftime("%B %d %Y")

    # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
    formatted_time = current_datetime.strftime("%I:%M %p")
    
    if str(result[0])== "No match detected":
        return 
    
    Fbase().firebaseUpdate(
                         keyName=formatted_date,
                         name=result[0],
                         data="Time Out",
                         time=formatted_time)

def detect_blur_in_face(face_gray,person=None,Blurred=1000):
        
    # Calculate the Laplacian
    laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
    
    # Calculate the variance of the Laplacian
    variance = laplacian.var()
        
    Face_blured = float("{:.2f}".format(variance))
    

    return True if Face_blured > Blurred else False
    
def Facial_Detection(camera=None, face_detector=None):
    
    # Initialize the timer and the start time
    timer = 0
    start_time = time.time()
    
    while True:
        
        # Capture a frame from the camera
        ret, frame = camera.read()
        
        if not ret:
            app.config["CAMERA_STATUS"] = "camera is not detected",True
            break
        
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(150, 150), flags=cv2.CASCADE_SCALE_IMAGE)

      
        if len(faces) == 1:
            
            
            (x, y, w, h) = faces[0]
            
            faceCrop = frame[y:y+h, x:x+w]
            face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
            
            is_blurred = detect_blur_in_face(face_gray=face_gray)
            
            # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()
            
            faceCrop = face_crop(frame=frame,face_height=h,face_width=w,x=x,y=y)

            # Check if 3 seconds have elapsed since the last send
            if timer >= 2:
                app.config["BGR"] = 0,255,255
                
                if is_blurred and faceCrop is not None:
                    facialRecognition(frame=frame)
                    
                # Reset the timer and the start time
                timer = 0
                start_time = time.time()
            
            B,G,R = app.config["BGR"]          
            Name,percent = app.config["FACE_RESULT"]
            
            if is_blurred:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (B,G,R), 2)
                cv2.putText(frame,Name + " " + str(percent),(x -60,y+h+30),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
            
   
        elif len(faces) > 1:
            
            for i,(x, y, w, h) in enumerate(faces,0):
                
                app.config["CAMERA_STATUS"] = "Multiple person is detected",True
                
                try:
                    faceCrop = frame[y:y+h, x:x+w]
                    face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)


                    is_blurred = detect_blur_in_face(face_gray,f"person_{i}",1500)
                    faceCrop = face_crop(frame=frame,face_height=h,face_width=w,x=x,y=y)
                    
                    if is_blurred and faceCrop is not None:
                        facialRecognition(frame=faceCrop)
                
                        B,G,R = app.config["BGR"]          
                        Name,percent = app.config["FACE_RESULT"]
            
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (B,G,R), 2)
                        cv2.putText(frame,f"person_{i}: " + Name + " " + str(percent),(x -60,y+h+30),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
                except:
                    pass   
                    
        else:
            app.config["BGR"] = 0,255,255
            app.config["FACE_RESULT"] = "",""
            app.config["CAMERA_STATUS"] = "No Face is detected",True
        

        
        _, frame_encoded  = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')

# homepage =========================================== #
@app.route('/')
def index():
    return render_template('index.html')

# facial training =========================================== #
@app.route('/face_training')
def face_training():
    return render_template('face_training.html')

# facial capture =========================================== #
@app.route('/facial_capture')
def facial_capture():
    return render_template('facial_capture.html')

# facial capture =========================================== #
@app.route('/Time_in')
def facial_recognition():
    return render_template('face_recogition.html')

if __name__ == '__main__':

    app.run(
        # host='192.168.100.134',
        host='0.0.0.0',
        debug=True,
        port=2000)
