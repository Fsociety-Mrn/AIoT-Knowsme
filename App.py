from flask import Flask, render_template, Response,request,jsonify
from datetime import datetime
from Firebase.firebase import Firebase as Fbase
from flask_cors import CORS
from werkzeug.utils import secure_filename
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL

import cv2
import os
import time
import shutil

import serial


app = Flask(__name__)
CORS(app)



app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "camera is loading",True
app.config["BGR"] = 0,255,255
app.config["target_temp"] = ""
app.config["training"] = False




# serial comunication
@app.route('/serial_IR', methods=['GET'])
def serial_IR():
    
    try:
        # Define the serial port and baud rate
        ser = serial.Serial('COM4', 9600, timeout=1)  # Replace 'COM3' with the correct port name
        ser.reset_input_buffer()
        time.sleep(2)
        ser.flush()
        data = ser.readline().decode('utf-8').rstrip()
    
        ser.close()
        return jsonify(data)
    except:
        return jsonify(0)

# face detection
faceDetection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

# face recognition api | Time in  =========================================== #
@app.route('/face_recognition', methods=['GET'])
def face_recognition():
    name,__ = app.config["FACE_RESULT"] 
    message,status = app.config["CAMERA_STATUS"]
    return jsonify({
        "camera_status": message,
        "status": status,
        "name": name
    }),200
     
# Get temperature status =========================================== #
@app.route('/status', methods=['GET'])
def status():
    return jsonify(app.config["training"])

# facial register =========================================== #
# validate the extentsion
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        
# facial register endpoint
@app.route('/face_register', methods=['POST'])
def face_register(): 
    # Check if a file was uploaded
    file = request.files.get('file')
    
    if not file:
        return jsonify({'message': 'No file in request'}), 400

    # Check if the file is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed file types are png, jpeg, jpg, gif.'}), 400
    
    # save the images if the folder of user is not 20
    if not len(os.listdir(app.config['REGISTER_FACIAL'])) == 20:
        
        # Save the file
        filename = secure_filename(file.filename)
        
        # Detect faces in the frame
        file.save(os.path.join('static/time_in', filename))
        files = cv2.imread(os.path.join('static/time_in', filename))
        gray = cv2.cvtColor(files, cv2.COLOR_BGR2GRAY)
        faces = faceDetection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)
        
        # Check if faces are detected 
        if len(faces) == 0:
            return jsonify({
                "message":"Align your Face Properly", 
                "result": False
            })
        
        app.config["training"] = "process"
        cv2.imwrite(f"{app.config['REGISTER_FACIAL']}/{int(len(os.listdir(app.config['REGISTER_FACIAL']))) + 1}.png", files)
   
        return jsonify({
            "message":f"{20 - int(len(os.listdir(app.config['REGISTER_FACIAL'])))} left capture images", 
            "result": False
            })
        
    
    app.config["training"] = True
    return jsonify({"message":"File saved successfully","result": True})


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
            
# name register 
@app.route('/name_register', methods=['POST']) 
def name_register():
    
    # Get the first and last name from the request body
    ID = request.json
    
    # Check that both first and last name are provided
    if not ID['name']:
        return jsonify({"message": 'enter your fullname'}), 400
    
    result, name = Fbase().firebaseCheck_ID(ID['name'])
    if not result:
        return jsonify({"message": 'Invalid Employee ID'}), 400

    remove_folder()

    # Define the name of the folder you want to create
    folder_name = f"{str(name).capitalize()}"

    # Define the path to the folder you want to create
    path = f"Jolo_Recognition/Registered-Faces/{folder_name}"

    # Check if the folder already exists
    if os.path.exists(path):
        # Remove all contents of the folder
        shutil.rmtree(path)

    os.makedirs(path)
    app.config['REGISTER_FACIAL'] = path
    
    # Return a success message
    return jsonify({"message": f"Folder {path} created successfully"}), 200

@app.route('/facial_training', methods=['GET'])
def facial_training():
    result = JL().Face_Train()
    app.config["training"] = False
    return jsonify(result),200

# Get temperature status =========================================== #
@app.route('/Temperature', methods=['GET'])
def Temperature():
    try:
        time.sleep(2)
        targetTemp = "27.8"
        # targetTemp = "{:.2f}".format(mlx.object_temperature)
        app.config["target_temp"] = targetTemp
 
        return jsonify(targetTemp),200
    except Exception as E:
        pass
        app.config["target_temp"] = 0.0
        print(E)
        return jsonify("N/A"),200
    
# Get temperature status =========================================== #
@app.route('/check', methods=['GET'])
def CHECK():
    return jsonify("tangina mo carl de roque uwi nako kaya ka madaming basher sa regular e"),200

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

# Facial Recognition function
def facialRecognition(frame):
    # facial reconition
    result = JL().Face_Compare(face=frame,threshold=0.7)

    app.config["FACE_RESULT"] = result
    app.config["BGR"] = (0,0,255) if result[0] == "No match detected" else (0,255,0 )
    app.config["CAMERA_STATUS"] = ("Access Denied",True) if result[0] == "No match detected" else ("Access Granted",False) 
 
    # Get current date and time
    current_datetime = datetime.now()

    # Format date as "Month Day Year" (e.g., "April 03 2024")
    formatted_date = current_datetime.strftime("%B %d %Y")

    # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
    formatted_time = current_datetime.strftime("%I:%M %p")
                
    Fbase().firebaseUpdate(
                         keyName=formatted_date,
                         name=result[0],
                         data="Time In",
                         time=formatted_time)
        
    # temperature
    Fbase().firebaseUpdate(
                         keyName=formatted_date,
                         name=result[0],
                         data="temp",
                         time=str(app.config["target_temp"]))

# check face blurred level
def detect_blur_in_face(face_gray,person=None,Blurred=1000):
        
    # Calculate the Laplacian
    laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
    
    # Calculate the variance of the Laplacian
    variance = laplacian.var()
        
    Face_blured = float("{:.2f}".format(variance))
    
    print(person,Face_blured)
    
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
            
            blureness = detect_blur_in_face(face_gray)
            
            
            
            # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()

            # Check if 3 seconds have elapsed since the last send
            if timer >= 1:
                app.config["BGR"] = 0,255,255
                
                
                if blureness:
                    facialRecognition(frame=frame)
                    
                # Reset the timer and the start time
                timer = 0
                start_time = time.time()
            
            B,G,R = app.config["BGR"]          
            Name,percent = app.config["FACE_RESULT"]
            
            if blureness:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (B,G,R), 2)
                cv2.putText(frame,Name + " " + str(percent),(x -60,y+h+30),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
            
   
        elif len(faces) > 1:
            
            for i,(x, y, w, h) in enumerate(faces,0):
                
                app.config["CAMERA_STATUS"] = "Multiple person is detected",True
                
                face_crop = frame[y:y+h, x:x+w]
                face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
            
                # Calculate new width and height
                scale_factor = 1.2
                new_w = int(w * scale_factor)
                new_h = int(h * scale_factor)

                # Adjust x and y to keep the center of the face in the crop
                new_x = max(0, x - (new_w - w) // 2)
                new_y = max(0, y - (new_h - h) // 2)

                # Crop the image with the new dimensions
                faceCrop = frame[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
                
                blureness = detect_blur_in_face(face_gray,f"person_{i}",1500)
                
                if blureness:
                    facialRecognition(frame=face_crop)
                
                    B,G,R = app.config["BGR"]          
                    Name,percent = app.config["FACE_RESULT"]
            
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (B,G,R), 2)
                    cv2.putText(frame,f"person_{i}: " + Name + " " + str(percent),(x -60,y+h+30),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
                    
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

# facial register =========================================== #
@app.route('/facial_register')
def facial_register():
    return render_template('facial_register.html')

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
        port=1000)
