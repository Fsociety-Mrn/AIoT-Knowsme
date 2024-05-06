# import cv2
# from Jolo_Recognition.Face_Recognition import JoloRecognition as JL

# face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# # Read the image
# image = cv2.imread("Images/Multiple.jpg")
    
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
# # load facial detector haar
# faces = face_detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(100, 100), flags=cv2.CASCADE_SCALE_IMAGE)

# for i, (x, y, w, h) in enumerate(faces, 0):
          
#     x, y, w, h = faces[i]
#     faceCrop = image[y:y+h, x:x+w]
    
#     # Calculate new width and height
#     scale_factor = 1.2
#     new_w = int(w * scale_factor)
#     new_h = int(h * scale_factor)

#     # Adjust x and y to keep the center of the face in the crop
#     new_x = max(0, x - (new_w - w) // 2)
#     new_y = max(0, y - (new_h - h) // 2)

#     # Crop the image with the new dimensions
#     faceCrop = image[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
    
    
#     # facial reconition
#     result = JL().Face_Compare(face=faceCrop,threshold=0.6,person=f"person_{i}")
    
#     B,G,R = (0,0,255) if result[0] == 'No match detected' else (0,255,0)
    
    
#     cv2.rectangle(image, (x, y), (x+w, y+h), (B,G,R), 2)
#     cv2.putText(image, f'{result[0]} {result[1]}', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (B,G,R), 2)

    
    
# # Display the image
# cv2.imshow("Image", image)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


import cv2
import numpy as np
import retinaface as  RetinaFace

def Facial_Detection(camera=None):
    while True:
        ret, frame = camera.read()
        
        if not ret:
            print("Camera not detected")
            break
        
        faces = RetinaFace.detect_faces(frame)
        
        for face in faces:
            # Extract face coordinates
            x1, y1, x2, y2 = face['facial_area']
            
            # Draw rectangle around face
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        _, frame_encoded = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_encoded.tobytes() + b'\r\n')

# Example usage
camera = cv2.VideoCapture(0)

for frame in Facial_Detection(camera=camera):
    # Display or do something with the frame
    cv2.imshow('Facial Detection', cv2.imdecode(np.frombuffer(frame, np.uint8), cv2.IMREAD_COLOR))
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()

