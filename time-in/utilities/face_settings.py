

class FaceSettings:


    def is_face_blurry(self,cv2, face_crop, blurred_threshold=1000):
        
        face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance > blurred_threshold

    def face_crop(self,frame,x,y,face_width,face_height):
    
        try:

            scale_factor = 1.2
            new_w = int(face_width * scale_factor)
            new_h = int(face_height * scale_factor)

            new_x = max(0, x - (new_w - face_width) // 2)
            new_y = max(0, y - (new_h - face_height) // 2) - 15

            face_crop = frame[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
                    
            return face_crop
        except Exception as e:
            print(f"Error in face_crop: {e}")

            return None

    def draw_custom_face_box(self,cv2,frame, x, y_face, w, h, line_y = None, box_color = (255, 255, 255), scan = False, scanColor=(255, 215, 0)):
        
        line_thickness = 2
        corner_length = 30  # Length of the corner lines


        def draw_corner(x,y,coordinates_x,coordinates_y):
            cv2.line(frame, (x, y), coordinates_x, box_color, line_thickness)
            cv2.line(frame, (x, y), coordinates_y, box_color, line_thickness)

        draw_corner(x, y_face,(x + corner_length, y_face), (x, y_face + corner_length))    
        draw_corner(x + w, y_face,(x + w - corner_length, y_face), (x + w, y_face + corner_length))
        draw_corner(x, y_face + h, (x + corner_length, y_face + h), (x, y_face + h - corner_length))
        draw_corner(x + w, y_face + h, (x + w - corner_length, y_face + h),(x + w, y_face + h - corner_length))

        if scan:
            cv2.line(frame, (x, line_y), (x + w, line_y), scanColor, 2)