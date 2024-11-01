

class FaceSettings:
    
    def is_camera_detected(self):
        
        return self._camera.isOpened()

    def is_face_blurry(self,cv2, face_crop, blurred_threshold=1000):
        
        face_gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        laplacian = cv2.Laplacian(face_gray, cv2.CV_64F)
        variance = laplacian.var()
        return variance > blurred_threshold

    def face_crop(frame,face_height,face_width,xy=(0,0)):
    
        try:
            x,y=xy
            
            scale_factor = 1.2
            new_w = int(face_width * scale_factor)
            new_h = int(face_height * scale_factor)

            new_x = max(0, x - (new_w - face_width) // 2)
            new_y = max(0, y - (new_h - face_height) // 2) - 15

            face_crop = frame[new_y-40:new_y+new_h+30, new_x-40:new_x+new_w+30]
                    
            return face_crop
        except:
            pass
            return None

    def draw_custom_box(self, frame, face_rect, color=(0, 255, 0), thickness=2):
        
        x, y, w, h = face_rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, thickness)
        # Add custom box logic here, such as drawing a circle or an ellipse