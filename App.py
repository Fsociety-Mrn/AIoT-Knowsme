from flask import Flask, render_template, Response,request,jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL
from datetime import datetime
from Firebase.firebase import Firebase as Fbase

import cv2 
import os
import time
import shutil

app = Flask(__name__)
CORS(app)
app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "cameara is loading"
app.config["BGR"] = 0,255,255

app.config["BGR_timeIn"] = 0,255,255

# Initialize timer variables
start_time = time.time()

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
# @app.route('/Temperature', methods=['GET'])
# def Temperature():
#     targetTemp = "{:.2f}".format(mlx.object_temperature)
#     app.config['UPLOAD_FOLDER'] = targetTemp
#     return jsonify({data: targetTemp})
    
# validate the extentsion
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    
# face recognition api | Time out
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
            app.config["BGR"] = 0,255,255
            print('time out')
            return jsonify({
                "name": ("No face is detected",""),
                "RGB" : str(app.config["BGR"])
            }), 200
        
        # facial reconition
        result = JL().Face_Compare(face=file,threshold=0.6)
        
        
        
        print("time out result: ",result)
        # Get current date and time
        current_datetime = datetime.now()

        # Format date as "Month Day Year" (e.g., "April 03 2024")
        formatted_date = current_datetime.strftime("%B %d %Y")

        # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
        formatted_time = current_datetime.strftime("%I:%M %p")
        
        Fbase().firebaseUpdate(
            keyName=formatted_date,
            name=result[0],
            data=data,
            time=formatted_time)
        
        app.config["FACE_RESULT"] = "No match detected", ""
        app.config["BGR"] = 0,0,255
            
        if not result[0] == 'No match detected':
            app.config["FACE_RESULT"] = result
            app.config["BGR"] = 0,255,0
        
        
    
        # return the result
        return jsonify({
                "name": result        ,
                "RGB" : str(app.config["BGR"])
            }),200
    else:
        
        # invalid file
        return jsonify({
                "name": result,
                "RGB" : str(app.config["BGR"])
            }),401

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

# facial register 
@app.route('/face_register', methods=['POST'])
def face_register(): 
    # Check if a file was uploaded
    file = request.files.get('file')
    
    if not file:
        return jsonify({'No file in request'}), 400

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
        
        # file_path = os.path.join(app.config['REGISTER_FACIAL'], f"{int(len(os.listdir(app.config['REGISTER_FACIAL']))) + 1}.jpg")
        # file.save(file_path)
        
        cv2.imwrite(f"{app.config['REGISTER_FACIAL']}/{int(len(os.listdir(app.config['REGISTER_FACIAL']))) + 1}.png", files)
   
        return jsonify({
            "message":f"{20 - int(len(os.listdir(app.config['REGISTER_FACIAL'])))} left capture images", 
            "result": False
            })

    return jsonify({"message":"File saved successfully","result": True})

@app.route('/facial_training', methods=['GET'])
def facial_training():
    result = JL().Face_Train()
    return jsonify(result),200

# Facial Detection =========================================== #
@app.route('/video_feed')
def video_feed():

    # load a camera and face detection
    camera = cv2.VideoCapture(0)
    face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(Facial_Detection(camera=camera, face_detector=face_detection), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')


def faceCrop(frame,face):
    
    # Calculate new width and height
    x, y, w, h = face
    scale_factor = 1.2
    new_w = int(w * scale_factor)
    new_h = int(h * scale_factor)

    # Adjust x and y to keep the center of the face in the crop
    new_x = max(0, x - (new_w - w) // 2)
    new_y = max(0, y - (new_h - h) // 2)

    # Crop the image with the new dimensions
    faceCrop = frame[new_y - 40:new_y + new_h + 30, new_x - 40:new_x + new_w + 30]
            
    return faceCrop
    
def Facial_Detection(camera=None, face_detector=None):
    
    B, G, R = (0, 255, 255)
    Name, percent = "", ""
    
    # Variable to keep track of time
    start_time = time.time()
    
    while True:

        # Capture a frame from the camera
        ret, frame = camera.read()
        
        if not ret:
            app.config["CAMERA_STATUS"] = "camera is not detected"
            break
        
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(50, 50), flags=cv2.CASCADE_SCALE_IMAGE)
        
        app.config["CAMERA_STATUS"] = "No Face is detected"
    
        
        # Iterate over each detected face
        for i, (x, y, w, h) in enumerate(faces, 0):
            
            # Get the coordinates of the face, draw rectangle and put text
            cv2.rectangle(frame, (x, y), (x + w, y + h), (B, G, R), 2)
            cv2.putText(frame, f'person_{i}: {percent}', (x - 60, y + h + 30), cv2.FONT_HERSHEY_COMPLEX, 1, (B, G, R), 1)
        
        # Encoding and yielding the frame
        _, frame_encoded = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')
        
        # break





# homepage =========================================== #
@app.route('/')
def index():
    return render_template('index.html')

# facial register =========================================== #
@app.route('/facial_register')
def facial_register():
    return render_template('facial_register.html')

# facial register =========================================== #
@app.route('/face_training')
def face_training_():
    return render_template('face_training.html')

# History =========================================== #
@app.route('/Today_History')
def Today_History():
    data = Fbase().firebaseRead_Today()
    return jsonify(data)

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        debug=True,
        threaded=True,
        port=1000)