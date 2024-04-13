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

import board
import busio
import adafruit_mlx90614



app = Flask(__name__)
CORS(app)

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
mlx = adafruit_mlx90614.MLX90614(i2c)

app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "camera is loading"
app.config["BGR"] = 0,255,255
app.config["target_temp"] = ""
app.config["training"] = False

# face detection
faceDetection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp'}

# face recognition api | Time in  =========================================== #
@app.route('/face_recognition', methods=['POST'])
def face_recognition():
    
    file = request.files['file']
    data = request.form.get('data')
    temp = request.form.get('temp')
    
    temp = temp.replace(" ","")
  
    # check file if exist
    if file and allowed_file(file.filename):
        
        # check if file name is not malicious
        filename = secure_filename(file.filename)
        
        # save the file
        file.save(os.path.join('/home/raspberrypi/Desktop/AIoT-Knowsme/static/time_in', filename))

        # read sending file via cv2
        file = cv2.imread(os.path.join('/home/raspberrypi/Desktop/AIoT-Knowsme/static/time_in', filename))

        gray = cv2.cvtColor(file, cv2.COLOR_BGR2GRAY)
        
        # Detect faces in the frame
        faces = faceDetection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)

        # Check if faces are detected 
        if len(faces) == 0:
            app.config["BGR"] = 0,255,255
            print('time in')
            return jsonify({
                "name": ("No face is detected",""),
                "RGB" : str(app.config["BGR"])
            }), 200
            
        if float(temp) > 37:
            app.config["BGR"] = 0,0,255
            print('time in')
            return jsonify({
                "name": ("Please wait, your temperature is high",""),
                "RGB" : str(app.config["BGR"])
            }), 200
            
        
        # facial reconition
        result = JL().Face_Compare(face=file,threshold=0.7)
 
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
        
        # temperature
        Fbase().firebaseUpdate(
            keyName=formatted_date,
            name=result[0],
            data="temp",
            time=temp)
        
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
        file.save(os.path.join('/home/raspberrypi/Desktop/AIoT-Knowsme/static/time_in', filename))
        files = cv2.imread(os.path.join('/home/raspberrypi/Desktop/AIoT-Knowsme/static/time_in', filename))
        gray = cv2.cvtColor(files, cv2.COLOR_BGR2GRAY)
        faces = faceDetection.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)
        
        # Check if faces are detected 
        if len(faces) == 0:
            
            app.config["training"] = "process"
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
        
    
    app.config["training"] = True
    return jsonify({"message":"File saved successfully","result": True})

# name register 
@app.route('/name_register', methods=['POST']) 
def name_register():
    
    # Get the first and last name from the request body
    name = request.json

    # Check that both first and last name are provided
    if not name['name']:
        return jsonify({"message": 'enter your fullname'}), 400

    # Define the name of the folder you want to create
    folder_name = f"{str(name['name']).capitalize()}"

    # Define the path to the folder you want to create
    path = f"/home/raspberrypi/Desktop/AIoT-Knowsme/Jolo_Recognition/Registered-Faces/{folder_name}"

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
        targetTemp = "{:.2f}".format(mlx.object_temperature)
        app.config["target_temp"] = targetTemp
 
        return jsonify(targetTemp),200
    except Exception as E:
        pass
        app.config["target_temp"] = "N/A"
        print(E)
        return jsonify("N/A"),200

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
            cv2.putText(frame,"Temperature: " + str(app.config["target_temp"]),(30,70),cv2.FONT_HERSHEY_COMPLEX,1,(B,G,R),1)
            
    
            
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

# facial training =========================================== #
@app.route('/facial_capture')
def facial_capture():
    return render_template('facial_capture.html')

if __name__ == '__main__':

    app.run(
        # host='192.168.100.134',
        host='0.0.0.0',
        debug=True,
        port=2000)
