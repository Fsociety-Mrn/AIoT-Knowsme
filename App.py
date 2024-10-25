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
import requests
import serial



# NOTE: pag i irun yung both sytem dapat http:127.0.0.1:1000 palagi irurun

app = Flask(__name__)
CORS(app)

# NOTE:  PALITAN ANG IP ADDRESS KADA MAG PAPALIT NG WIFI/CONNECTION
API_ENDPOINT_TIMEOUT = 'http://192.168.100.38:2000'
BLURRINESS_VALUE = 0
RECOGNITION_THRESHOLD = 0.55

app.config["FACE_RESULT"] = "",""
app.config["CAMERA_STATUS"] = "camera is loading",True
app.config["BGR"] = 0,255,25
app.config["target_temp"] = "35.6"
app.config["training"] = False
app.config['REGISTER_FACIAL'] = 'Jolo_Recognition/Registered-Faces/'
app.config['CAPTURE_STATUS'] = 0

@app.route('/serial_IR', methods=['GET'])
def serial_IR():
    
    try:

        # Define the serial port and baud rate
        ser = serial.Serial('COM5', 9600, timeout=1)  # Replace 'COM3' with the correct port name
        ser.reset_input_buffer()
        time.sleep(2)
        ser.flush()
        data = ser.readline().decode('utf-8').rstrip()
        app.config["target_temp"] = str(data).split(",")[0]
        ser.close()
        return jsonify(data)
    except:
        return jsonify("33,1")

@app.route('/api/send-images', methods=['GET'])
def send_images():

    for filename in os.listdir(app.config['REGISTER_FACIAL']):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
      
            image_path = os.path.join(app.config['REGISTER_FACIAL'] , filename)
            with open(image_path, 'rb') as image_file:
   
                files = {'file': image_file}
                response = requests.post(API_ENDPOINT_TIMEOUT + '/api/received-images', files=files)

                message_status = "Successfully sent {filename}" if response.status_code == 200 else f"Failed to send {filename}, Status Code: {response.status_code}"
        
                print(message_status)

        
    app.config["training"] = True
    return jsonify({
        "message": app.config['REGISTER_FACIAL'],
        "result": True
    })


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
     
@app.route('/status', methods=['GET'])
def status():
    return jsonify(app.config["training"])

@app.route('/api/capture-counter', methods=["GET"])
def capture_counter():
    
    camera_msg,is_camera = app.config["CAMERA_STATUS"]
    
    return jsonify({
                "is_camera_connected" : is_camera,
                "capture_counter": app.config['CAPTURE_STATUS'],
                "camera_message" : camera_msg
            })
    
# validate the extentsion
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_images(frame):
    path = app.config['REGISTER_FACIAL']
    
    if not len(os.listdir(path)) == 20:
        
        app.config["training"] = "process"
        capture =  int(len(os.listdir(path))) + 1
        app.config['CAPTURE_STATUS'] = capture
        cv2.imwrite(f"{path}/{capture}.png", frame)
        
        return False
    
    return True

def draw_custom_face_box(frame, x, y_face, w, h, line_y = None, box_color = (255, 255, 255), scan = False, scanColor=(255, 215, 0)):
    """Draws a face box with blue corners and a moving horizontal line."""

    line_thickness = 2
    corner_length = 30  # Length of the corner lines
     # Light blue corner color

    # Top-left corner
    cv2.line(frame, (x, y_face), (x + corner_length, y_face), box_color, line_thickness)
    cv2.line(frame, (x, y_face), (x, y_face + corner_length), box_color, line_thickness)

    # Top-right corner
    cv2.line(frame, (x + w, y_face), (x + w - corner_length, y_face), box_color, line_thickness)
    cv2.line(frame, (x + w, y_face), (x + w, y_face + corner_length), box_color, line_thickness)

    # Bottom-left corner
    cv2.line(frame, (x, y_face + h), (x + corner_length, y_face + h), box_color, line_thickness)
    cv2.line(frame, (x, y_face + h), (x, y_face + h - corner_length), box_color, line_thickness)

    # Bottom-right corner
    cv2.line(frame, (x + w, y_face + h), (x + w - corner_length, y_face + h), box_color, line_thickness)
    cv2.line(frame, (x + w, y_face + h), (x + w, y_face + h - corner_length), box_color, line_thickness)

    if scan:
        cv2.line(frame, (x, line_y), (x + w, line_y), scanColor, 2)  # Yellow moving line

def facial_register_camera(camera=None, face_detector=None):

    timer = 0
    start_time = time.time()
    while True:

        ret, frame = camera.read()
        
        if not ret:
            app.config["CAMERA_STATUS"] = "camera is not detected",True
            break
        
        frame = cv2.flip(frame,1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(150, 150), flags=cv2.CASCADE_SCALE_IMAGE)

        if len(faces) == 1:
        
            (x, y, w, h) = faces[0]
            
            faceCrop = frame[y:y+h, x:x+w]
            
            face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
            is_blurred = detect_blur_in_face(face_gray=face_gray,Blurred=BLURRINESS_VALUE)
            
            faceCrop = face_crop(frame=frame,face_height=h,face_width=w,x=x,y=y)
            
             # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()
            
            
            if is_blurred:
                
                if timer >= 0.3:
                    is_capture_done= save_images(faceCrop)
                
                    if is_capture_done:
                        app.config["training"] = "sending"
                        break
                    
                    # Reset the timer and the start time
                    timer = 0
                    start_time = time.time()
                    
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 255), 2)
                
                
            
            app.config["CAMERA_STATUS"] = ("Please align your face properly.",False) if is_blurred else ("Oops! Your camera's not in focus. Try moving it or wiping the lens",False)
            
   
        elif len(faces) > 1:
            
            app.config["CAMERA_STATUS"] = "Multiple person is detected",False

        _, frame_encoded  = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')

@app.route('/face_register')
def face_register(): 
    app.config["FACE_RESULT"] = "",""
    app.config["CAMERA_STATUS"] = "",True
    app.config["BGR"] = 0,255,255

    # load a camera and face detection
    camera = cv2.VideoCapture(0)  # Set height to 1080p
    face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(facial_register_camera(camera=camera, face_detector=face_detection), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')

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
            
@app.route('/api/id-verifications', methods=['POST']) 
def id_verifications():
    
    ID = request.json
    headers = {
        'Content-Type': 'application/json'
    }
    if not ID['employee_id']:
        return jsonify({"message": 'enter your fullname'}), 400
    
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
    
    
    response = requests.post(f"{API_ENDPOINT_TIMEOUT}/api/id-verifications", json=request.json, headers=headers)
    
    if not response.status_code == 200:
        return response.json(), response.status_code
    
    return jsonify({"message": f"Folder {path} created successfully"}), 200

@app.route('/api/facial-training', methods=['GET'])
def facial_training():

    remove_folder()
    
    result = JL().Face_Train()
    app.config["training"] = False
    return jsonify(result),200

@app.route('/Temperature', methods=['GET'])
def Temperature():
    try:
        return jsonify(app.config["target_temp"]),200
    except Exception as E:
        pass
        app.config["target_temp"] = 0.0

        return jsonify("N/A"),200
    

# Facial Detection =========================================== #
@app.route('/video_feed')
def video_feed():

    app.config["FACE_RESULT"] = "",""
    app.config["CAMERA_STATUS"] = "",True
    app.config["BGR"] = 0,255,255

    # load a camera and face detection
    camera = cv2.VideoCapture(0)
    face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(Facial_Detection(camera=camera, face_detector=face_detection), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')

last_update_time = None

def recognize_multiple_faces(frame,face_detected,is_blurred):
    
    # Get current date and time
    current_datetime = datetime.now()

    # Format date as "Month Day Year" (e.g., "April 03 2024")
    formatted_date = current_datetime.strftime("%B %d %Y")

    # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
    formatted_time = current_datetime.strftime("%I:%M %p")
    
    Name,percent = "| ",""
    for id,(x, y, w, h) in enumerate(face_detected,0):
        
        faceCrop = frame[y:y+h, x:x+w]
        face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
        
        is_blurred = detect_blur_in_face(face_gray,f"person_{id}",BLURRINESS_VALUE)
        faceCrop = face_crop(frame=frame,face_height=h,face_width=w,x=x,y=y)
        
        if is_blurred and faceCrop is not None:
            result = JL().Face_Compare(face=faceCrop,threshold=RECOGNITION_THRESHOLD)

            name_result = result[0]

            Name += name_result + " | " if result[0] == "No match detected" else ""
            percent = result[1]
            
            app.config["BGR"] = (0,0,255) if result[0] == "No match detected" else (0,255,0)
            app.config["CAMERA_STATUS"] = ("Access Denied",True) if result[0] == "No match detected" else ("Access Granted",False) 
            
            if name_result != "No match detected":
        
                Fbase().firebaseUpdate(
                    keyName=formatted_date,
                    name=result[0],
                    data="Time In",
                    time=formatted_time,
                    Temp=str(app.config["target_temp"])
                )
        
    app.config["FACE_RESULT"] = Name,percent
 

def facialRecognition(frame):

    global last_update_time

    # facial recognition
    result = JL().Face_Compare(face=frame,threshold=RECOGNITION_THRESHOLD)
    app.config["FACE_RESULT"] = result
    app.config["BGR"] = (0,0,255) if result[0] == "No match detected" else (0,255,0)
    app.config["CAMERA_STATUS"] = ("Access Denied",True) if result[0] == "No match detected" else ("Access Granted",False) 
 
    # Get current date and time
    current_datetime = datetime.now()

    # Format date as "Month Day Year" (e.g., "April 03 2024")
    formatted_date = current_datetime.strftime("%B %d %Y")

    # Format time as "Hour:Minute AM/PM" (e.g., "1:52 PM")
    formatted_time = current_datetime.strftime("%I:%M %p")

    if str(result[0]) == "No match detected":
        return 
                
    Fbase().firebaseUpdate(
            keyName=formatted_date,
            name=result[0],
            data="Time In",
            time=formatted_time,
            Temp=str(app.config["target_temp"])
        )

def face_crop(frame,face_height,face_width,x,y):
    
    try:
        scale_factor = 1.2
        new_w = int(face_width * scale_factor)
        new_h = int(face_height * scale_factor)

        new_x = max(0, x - (new_w - face_width) // 2)
        new_y = max(0, y - (new_h - face_height) // 2) - 15

        faceCrop = frame[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
                    
        return faceCrop
    except:
        pass
    return None

# check face blurred level
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
        faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)

      
        if len(faces) == 1:
        
            (x, y, w, h) = faces[0]
            
            faceCrop = frame[y:y+h, x:x+w]
            face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
            
            # Blurred Paramater = addjust nyo lang pag di marecognize yung prof 
            # either babaan or tatanggalin lang ex:  detect_blur_in_face(face_gray=face_gray)
            # or babaan  detect_blur_in_face(face_gray=face_gray,Blurred=700)
            # ang default ay 1000
            is_blurred = detect_blur_in_face(face_gray=face_gray,Blurred=BLURRINESS_VALUE)
            
        
            # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()
            
            faceCrop = face_crop(frame=frame,face_height=h,face_width=w,x=x,y=y)

            # Check if 3 seconds have elapsed since the last 
            if timer >= 2:
                app.config["BGR"] = 0,255,255
                
                if is_blurred and faceCrop is not None:
                    facialRecognition(frame=faceCrop)
                    
                # Reset the timer and the start time
                timer = 0
                start_time = time.time()
            
            B,G,R = app.config["BGR"]          
            Name,percent = app.config["FACE_RESULT"]
            
            if is_blurred:
                draw_custom_face_box(frame, x, y, w, h,box_color=(B,G,R))

          
   
        elif len(faces) > 1:
            
            # Increment the timer by the elapsed time since the last send
            timer += time.time() - start_time
            start_time = time.time()
            
            for i,(x, y, w, h) in enumerate(faces,0):
                
                try:
                    faceCrop = frame[y:y+h, x:x+w]
                    face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)

                    is_blurred = detect_blur_in_face(face_gray,f"person_{i}",1500)
        
                    if timer >= 1:
                        
                        if is_blurred and faceCrop is not None:
                            recognize_multiple_faces(frame,faces,is_blurred)
     
                    if is_blurred:
                        B,G,R = app.config["BGR"] 
                        draw_custom_face_box(frame, x, y, w, h,box_color=(B,G,R))
                
                except Exception as e:
                    print(e)
                    pass   

           
        else:
            app.config["BGR"] = 0,255,255
            app.config["FACE_RESULT"] = "",""
            app.config["CAMERA_STATUS"] = "No Face is detected",True
        

        
        _, frame_encoded  = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/facial_register')
def facial_register():
    return render_template('facial_register.html')


@app.route('/face_training')
def face_training():
    return render_template('face_training.html')


@app.route('/facial_capture')
def facial_capture():
    return render_template('facial_capture.html')


@app.route('/Time_in')
def facial_recognition():
    return render_template('face_recogition.html')

if __name__ == '__main__':

    app.run(
        # host='192.168.100.134',
        host='0.0.0.0',
        debug=True,
        port=1000)
