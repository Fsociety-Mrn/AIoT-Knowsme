import os
import shutil
import cv2
import time

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from Jolo_Recognition.Face_Recognition import JoloRecognition as JL
        
class Register(QtWidgets.QFrame):
    
    def __init__(self,parent):
        super().__init__(parent)
        
        self.mainmenu = parent
        self.setObjectName("Frame")
        self.resize(928, 565)
        
        # capture status
        self.captureStat = 1
        
        # facial detection
        self.face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # message box
        self.MessageBox = QtWidgets.QMessageBox()
        self.MessageBox.setStyleSheet("""
                  QMessageBox { 
                      text-align: center;
                  }
                  QMessageBox::icon {
                      subcontrol-position: center;
                  }
                  QPushButton { 
                      width: 250px; 
                      height: 30px; 
                      font-size: 15px;
                  }
              """)
        
        self.widget = QtWidgets.QWidget(self)
        self.widget.setGeometry(QtCore.QRect(0, 0, 931, 571))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.widget.setFont(font)
        self.widget.setStyleSheet("background-color: #faf4f4;")
        self.widget.setObjectName("widget")
        
        # textbox
        self.lineEdit = QtWidgets.QLineEdit(self.widget)
        self.lineEdit.setGeometry(QtCore.QRect(80, 50, 741, 51))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(20)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("background: transparents;\n"
"color: #1a1313;\n"
"background-color: #faf4f4;\n"
"border: 2px solid #1a1313;\n"
"border-radius: 20px;")
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.lineEdit.setCursorMoveStyle(QtCore.Qt.VisualMoveStyle)
        self.lineEdit.setClearButtonEnabled(True)
        self.lineEdit.setObjectName("lineEdit")
        
        # create folder
        self.pushButton = QtWidgets.QPushButton(self.widget)
        self.pushButton.setGeometry(QtCore.QRect(830, 50, 61, 51))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        self.pushButton.setFont(font)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("Images/icon-create.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(50, 50))
        self.pushButton.setFlat(True)
        self.pushButton.setObjectName("pushButton")
        
        # label
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setGeometry(QtCore.QRect(140, 110, 631, 31))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(18)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label_2")
        
        # video streaming
        self.video = QtWidgets.QLabel(self.widget)
        self.video.setGeometry(QtCore.QRect(130, 150, 651, 391))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(14)
        self.video.setFont(font)
        self.video.setStyleSheet("border:2px solid #1a1313;\n"
"border-radius : 30%;\n"
"color: #1a1313;")
        self.video.setAlignment(QtCore.Qt.AlignCenter)
        self.video.setObjectName("label")
        
        # facial register
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(310, 540, 111, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        
        # back button
        self.backButton = QtWidgets.QPushButton(self.widget)
        self.backButton.setGeometry(QtCore.QRect(10, 10, 51, 51))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)
        self.backButton.setFont(font)
        self.backButton.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
#         self.backButton.setStyleSheet("border-radius: 20%;\n"
# "border: 2px solid #1a1313;")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("Images/icon-back.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.backButton.setIcon(icon1)
        self.backButton.setIconSize(QtCore.QSize(50, 50))
        self.backButton.setFlat(True)
        self.backButton.setObjectName("pushButton_3")
        
        # video streaming start
        self.videoStream = cv2.VideoCapture(0)
        self.videoStream.set(4, 1080)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.videoStreaming)
        # self.timer.start(30)
        
        # for count down
        self.start_start = 0
        self.last_recognition_time = time.time()
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Frame", ""))
        self.pushButton.setText(_translate("Frame", ""))
        self.backButton.setText(_translate("Frame", ""))
        self.label.setText(_translate("Frame", ""))
        self.video.setText(_translate("Frame", "Camera is loading"))
        self.lineEdit.setPlaceholderText(_translate("Frame", "Please input your name"))
        self.pushButton_2.setText(_translate("Frame", "Facial Register"))
        self.pushButton_2.setDisabled(True)
        
        # event functions
        self.pushButton.clicked.connect(self.create_folder)
        self.backButton.clicked.connect(self.bButton)
        
        
    # creating folder name
    def create_folder(self):
        
        # check if TokenID is not empty
        if not self.lineEdit.text():
            return self.messageBoxShow(
                icon=self.MessageBox.Warning,
                title="",
                text="Name cannot be empty",
                buttons=self.MessageBox.Ok)
            
        # Define the path for the known faces folder
        path = f"Jolo_Recognition/Registered-Faces/{str(self.lineEdit.text())}"
        
        if os.path.exists(path):

            # Remove all contents of the folder
            shutil.rmtree(path)
            os.makedirs(path, exist_ok=True)

        else:

            # Create the known faces folder if it doesn't exist
            os.makedirs(path, exist_ok=True)
        
        self.lineEdit.setDisabled(True)
        
        self.start_start = time.time()
        self.timer.start(30)
            
    # video Streaming
    def videoStreaming(self):
        
        ret, notFlip = self.videoStream.read()

        if not ret:
            self.label.setText("Camera wont load")
            return

        # process the frame
        frame = cv2.flip(notFlip, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    

        # load facial detector haar
        faces = self.face_detector.detectMultiScale(gray,
                                                    scaleFactor=1.1,
                                                    minNeighbors=20,
                                                    minSize=(100, 100),
                                                    flags=cv2.CASCADE_SCALE_IMAGE)
        
        
        current_time = time.time()
        
        if current_time - self.start_start <= 5:
            
            self.label.setText(f"capture start at {int(5)-int(current_time - self.start_start)}")
            
            if len(faces) == 1:  
                x, y, w, h = faces[0]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                
                
            height, width, channel = frame.shape
            bytesPerLine = channel * width
            qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
            pixmap = QtGui.QPixmap.fromImage(qImg)
            self.video.setPixmap(pixmap)
            return
        
        if len(faces) == 1:  
            x, y, w, h = faces[0]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            status = self.captureSave(current_time=current_time, frame=notFlip) 
            if status:
                self.facialTraining() 

        elif len(faces) >= 1:
            self.label.setText("Multiple face is detected")
        else:
            self.label.setText("No face is detected")
                
         
        height, width, channel = frame.shape
        bytesPerLine = channel * width
        qImg = QtGui.QImage(frame.data, width, height, bytesPerLine, QtGui.QImage.Format_BGR888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.video.setPixmap(pixmap)
        
        self.label.setText("capturing start please bear with me")
       
    # messagebox 
    def messageBoxShow(self, icon=None, title=None, text=None, buttons=None):
    
        # Set the window icon, title, and text
        self.MessageBox.setIcon(icon)
        self.MessageBox.setWindowTitle(title)
        self.MessageBox.setText(text)

        # Set the window size
        self.MessageBox.setFixedWidth(400)

        # Set the standard buttons
        self.MessageBox.setStandardButtons(buttons)

        result = self.MessageBox.exec_()

        self.MessageBox.close()
        # Show the message box and return the result
        return result

    # capture images
    def captureSave(self, current_time=None, frame=None):

        # Set time delay to avoid over capturing
        if current_time - self.last_recognition_time <= 0.5:
            return

        self.last_recognition_time = current_time
    
        # Save captured images if capture count is less than 20
        if self.captureStat <= 20:

            path = f"Jolo_Recognition/Registered-Faces/{str(self.lineEdit.text())}/{self.captureStat}.png"
            
            cv2.imwrite(path, frame)
            self.captureStat += 1
            self.label.setText("Please align your face properly")
            
            return False
        else:
            # enable facial training button
            self.pushButton_2.setDisabled(True)
            return True

    # Facial Training
    def facialTraining(self):
        
        self.timer.stop()
        
        self.videoStream.release()
        cv2.destroyAllWindows()

        
        self.label.setText("Facial training please wait")

        # Delay the creation of the FacialLogin object by 100 milliseconds
        QtCore.QTimer.singleShot(100, self.startFacialTraining)
        
    def startFacialTraining(self):
        
        # Train the facial recognition model
        JL().Face_Train()
        
        # Show the result
        title = "Facial Registration"
        text = "Successfully trained" 
        icon = self.MessageBox.Information
        self.messageBoxShow(title=title, text=text, buttons=self.MessageBox.Ok, icon=icon)
        
    # backt to main
    def bButton(self):
        self.mainmenu.videoStreamingStart()
        self.close()

if __name__ == "__main__":
    
    import sys
    # Create a new QApplication object
    app = QApplication(sys.argv)

    New_menu = Register()
    New_menu.show() 

    sys.exit(app.exec_())