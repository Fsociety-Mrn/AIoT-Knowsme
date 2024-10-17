# library
import cv2
import time

# custom classes
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL



cap = cv2.VideoCapture('multiple_face_recognition.mp4')
cap = cv2.VideoCapture('false_recognition.mp4')

face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


timer = 0
start_time = time.time()
bgr_color = (0,255,255)      
name_result = ""             
                       
def frame_resized(frame):
    original_height, original_width = frame.shape[:2]

    aspect_ratio = original_width / original_height

    new_width = 800
    new_height = int(new_width / aspect_ratio)
    
    return cv2.resize(frame, (new_width, new_height))


def face_crop(frame,face_height,face_width):
    
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


def face_recognition(frame):
    global name_result,bgr_color
    
    result = JL().Face_Compare(face=frame,threshold=0.55)
    name_result = result[0]
    bgr_color = (0,0,255) if result[0] == "No match detected" else (0,255,0)
    
    print(name_result,bgr_color)



while True:

    success, frame = cap.read()
    
    if not success:
        print("Failed to grab frame")
        break


    frame = cv2.flip(frame_resized(frame),1)
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    face_detected = face_detection.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)
    
    timer += time.time() - start_time
    start_time = time.time()
    
    for face_id,(x, y, w, h) in enumerate(face_detected,0):
        
        if timer >= 0.5:
            face_recognition(frame=face_crop(frame=frame,face_height=h,face_width=w))
            timer = 0
            start_time = time.time()
            
        cv2.rectangle(frame, (x, y), (x+w, y+h), (bgr_color), 2)
        cv2.putText(frame,name_result,(x, y-10),cv2.FONT_HERSHEY_COMPLEX,1,(bgr_color),1)

    cv2.imshow('Video Stream', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
