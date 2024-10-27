import cv2

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def draw_custom_face_box(frame, x, y_face, w, h, line_y, color_blue = (255, 255, 255), scan = True, scanColor=(255, 215, 0)):
    """Draws a face box with blue corners and a moving horizontal line."""

    line_thickness = 2
    corner_length = 30  # Length of the corner lines
     # Light blue corner color

    # Top-left corner
    cv2.line(frame, (x, y_face), (x + corner_length, y_face), color_blue, line_thickness)
    cv2.line(frame, (x, y_face), (x, y_face + corner_length), color_blue, line_thickness)

    # Top-right corner
    cv2.line(frame, (x + w, y_face), (x + w - corner_length, y_face), color_blue, line_thickness)
    cv2.line(frame, (x + w, y_face), (x + w, y_face + corner_length), color_blue, line_thickness)

    # Bottom-left corner
    cv2.line(frame, (x, y_face + h), (x + corner_length, y_face + h), color_blue, line_thickness)
    cv2.line(frame, (x, y_face + h), (x, y_face + h - corner_length), color_blue, line_thickness)

    # Bottom-right corner
    cv2.line(frame, (x + w, y_face + h), (x + w - corner_length, y_face + h), color_blue, line_thickness)
    cv2.line(frame, (x + w, y_face + h), (x + w, y_face + h - corner_length), color_blue, line_thickness)

    if scan:
        cv2.line(frame, (x, line_y), (x + w, line_y), scanColor, 2)  # Yellow moving line

def main():
    cap = cv2.VideoCapture(0)  # Use webcam
    direction = 1  # 1 for down, -1 for up
    speed = 2  # Speed of the line movement
    line_y = None  # Line's vertical position
    last_face = None  # Store the last detected face

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=20, minSize=(150, 150), flags=cv2.CASCADE_SCALE_IMAGE)

        if len(faces) > 0:
            # Use the first detected face
            x, y_face, w, h = faces[0]
            last_face = (x, y_face, w, h)  # Store last face coordinates

            # Initialize the line position if it's the first detection
            if line_y is None:
                line_y = y_face + (h // 2)  # Start in the middle of the face box

            # Draw the face box with moving line
            draw_custom_face_box(frame, x, y_face, w, h, line_y)

            # Update the line position (moving up or down)
            line_y += speed * direction

            # Bounce the line when it hits the top or bottom of the face box
            if line_y >= y_face + h:
                direction = -1  # Reverse to move up
            elif line_y <= y_face:
                direction = 1  # Reverse to move down



        # Display the resulting frame
        cv2.imshow('Face Detection with Customized Box', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
