# library
import cv2
import time

# custom classes
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL



cap = cv2.VideoCapture('multiple_face_recognition.mp4')
# cap = cv2.VideoCapture('false_recognition.mp4')

face_detection = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255)]

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

# check face blurred level
def detect_blur_in_face(face_gray,person=None,Blurred=1000):
        
    # Calculate the Laplacian
    laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
    
    # Calculate the variance of the Laplacian
    variance = laplacian.var()
        
    Face_blured = float("{:.2f}".format(variance)) 
        
    return True if Face_blured > Blurred else False

def face_recognition(frame):
    global name_result,bgr_color
    
    result = JL().Face_Compare(face=frame,threshold=0.6)
    name_result = result[0]
    bgr_color = (0,0,255) if result[0] == "No match detected" else (0,255,255) 
    
def draw_custom_face_box(frame, x, y_face, w, h, line_y=None, box_color = (255, 255, 255), scan = True, scanColor=(255, 215, 0)):
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

def recognize_multiple_faces(frame):
    global name_result,bgr_color
    
    for id,(x, y, w, h) in enumerate(face_detected,0):
        
        faceCrop = frame[y:y+h, x:x+w]
        face_gray = cv2.cvtColor(faceCrop, cv2.COLOR_BGR2GRAY)
        
        is_blurred = detect_blur_in_face(face_gray,f"person_{id}",1500)
        faceCrop = face_crop(frame=frame,face_height=h,face_width=w)
        
        if is_blurred and faceCrop is not None:

            result = JL().Face_Compare(face=faceCrop,threshold=0.8)

            name_result = result[0]
            bgr_color = (0,0,255) if result[0] == "No match detected" else (0,255,0) 
            
            # cv2.putText(frame,name_result,(x, y-10),cv2.FONT_HERSHEY_COMPLEX,1,(color),1)
            
            # print(f"person_{id}: {result[0]}")
         

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
        color = colors[face_id % len(colors)]

        if timer >= 0.5:
            
            recognize_multiple_faces(frame=frame)
            
            timer = 0
            start_time = time.time()
            
        draw_custom_face_box(frame, x, y, w, h,box_color=bgr_color)
                        


    cv2.imshow('Video Stream', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
