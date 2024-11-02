
# PIP library installed
from flask import Blueprint, jsonify as json, request, Response

import time
import requests
import cv2

# Custom Library
from models import Firebase as firebase
from utilities import ImageStorageManager as image_storage_manager
from utilities import FaceSettings as face_settings

face_register = Blueprint('face_register', __name__)

# NOTE:  PA LI TAN ANG IP ADDRESS KA DA MAG PA PA LIT NG WIFI/CONNECTION\
API_ENDPOINT_TIMEOUT = 'http://192.168.100.38:2000'
BLURRINESS_VALUE = 0

config = {
    "training": False,
    "folder_path": None,
    "capture_count": 0,
    "camera_status": ("", False),
}

@face_register.route('/api/face-register/capture-counter', methods=["GET"])
def capture_counter():
    
    camera_msg,is_camera = config["camera_status"]
    
    return json({
                "is_camera_connected" : is_camera,
                "capture_counter":config['capture_count'],
                "camera_message" : camera_msg
            })
    
    
@face_register.route('/api/face-register/status', methods=['GET'])
def status():
    return json(config["training"])

  
@face_register.route('/api/face-register/id-verifications', methods=['POST']) 
def id_verifications():
    
    try:

        employee_id = request.json

        if not employee_id['employee_id']:
            return json({"message": 'Enter your Employee ID'}), 400
    
        result, name = firebase().verify_id(employee_id['employee_id'])

        if not result:
            return json({"message": 'Invalid Employee ID'}), 400
        
        data = firebase().get_registered_faces()
        image_storage_manager().remove_folder(data=data)
        config["folder_path"] = image_storage_manager().create_folder(folder_name=f"{str(name).capitalize()}")

        response = requests.post(
            url= f"{API_ENDPOINT_TIMEOUT}/api/id-verifications", 
            json=request.json, 
            headers={
                'Content-Type': 'application/json'
            }
        )
    
        if not response.status_code == 200:
            return response.json(), response.status_code
        config["training"] = "process"
        return json({"message": f"Folder {name} created successfully"}), 200

    except Exception as e:
        return json({"message": e}), 500
 
   
@face_register.route('/api/face-register/detect-face')
def facial_register(): 
    
    # app.config["FACE_RESULT"] = "",""
    # app.config["CAMERA_STATUS"] = "",True
    # app.config["BGR"] = 0,255,255

    camera = cv2.VideoCapture(0)  # Set height to 1080p
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    return Response(facial_register_camera(camera=camera, face_detector=face_detector), 
                        mimetype='multipart/x-mixed-replace; boundary=frame')

def facial_register_camera(camera, face_detector):

    timer = 0
    start_time = time.time()

    direction = 1
    speed = 2
    line_y = None

    while True:
        ret, frame = camera.read()

        if not ret:
            break

        frame = cv2.flip(frame, 1)
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_faces = face_detector.detectMultiScale(
                                        grayscale_frame, 
                                        scaleFactor=1.1, 
                                        minNeighbors=20, 
                                        minSize=(150, 150),
                                        flags=cv2.CASCADE_SCALE_IMAGE)
 
        if len(detected_faces) == 1:
            
            x, y, width, height = detected_faces[0]
            face_crop = frame[y:y+height, x:x+width]
                    
            face_crop = face_settings().face_crop(frame,x,y,width,height)
            is_blurred = face_settings().is_face_blurry(cv2, face_crop, BLURRINESS_VALUE)

            timer += time.time() - start_time
            start_time = time.time()

            if is_blurred:

                if timer >= 0.5:
                    is_capture_done,image_count = image_storage_manager().save_images(cv2,face_crop,config["folder_path"])
                    config['capture_count'] = image_count
                    
                    if is_capture_done:
                        config["training"] = "sending"
                        break
                
                    timer = 0
                    start_time = time.time()
                    
                if line_y is None:
                    line_y = y + (height // 2)
                    
                face_settings().draw_custom_face_box(
                                    cv2=cv2, 
                                    frame=frame, 
                                    x=x, 
                                    y_face=y, 
                                    w=width, 
                                    h=height, 
                                    line_y=line_y, 
                                    scan=True,
                                    scanColor=(0,255,255)
                                )
                    
                line_y += speed * direction

                if line_y >= y + height:
                    direction = -1
                elif line_y <= y:
                    direction = 1
                    
                config["CAMERA_STATUS"] = ("Please align your face properly.",False) if is_blurred else ("Oops! Your camera's not in focus. Try moving it or wiping the lens",False)

        _, encoded_frame = cv2.imencode('.png', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_frame.tobytes() + b'\r\n')
