from flask import Flask, send_file
import cv2

app = Flask(__name__)

# Function to capture frames from webcam
def capture_frames():
    camera = cv2.VideoCapture(0)
    success, frame = camera.read()
    if success:
        return frame
    else:
        return None

@app.route('/')
def index():
    return 'Webcam Stream'

@app.route('/capture_image')
def capture_image():
    frame = capture_frames()
    if frame is not None:
        cv2.imwrite('captured_image.jpg', frame)
        return send_file('captured_image.jpg', mimetype='image/jpeg')
    else:
        return 'Failed to capture image'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
