import os
import shutil

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
        
class Register(QtWidgets.QFrame):
    
    def __init__(self):
        super().__init__()
        
        self.setObjectName("Frame")
        self.resize(750, 452)
        
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
        
        # textbox
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(50, 20, 541, 31))
        self.lineEdit.setObjectName("lineEdit")
        
        # create folder
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(610, 20, 81, 31))
        self.pushButton.setObjectName("pushButton")
        
        # video streaming
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(60, 70, 621, 50))
        self.label.setObjectName("label")
        
        # video streaming
        self.video = QtWidgets.QLabel(self)
        self.video.setGeometry(QtCore.QRect(60, 70, 621, 311))
        self.video.setObjectName("label")
        
        # facial register
        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(320, 400, 111, 31))
        self.pushButton_2.setObjectName("pushButton_2")
        
        # back button
        self.backButton = QtWidgets.QPushButton(self)
        self.backButton.setGeometry(QtCore.QRect(60, 400, 81, 31))
        self.backButton.setObjectName("pushButton")
        
        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        
        
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Frame", "Frame"))
        self.pushButton.setText(_translate("Frame", "create folder"))
        self.backButton.setText(_translate("Frame", "back to login"))
        self.label.setText(_translate("Frame", "Camera is loading"))
        self.video.setText(_translate("Frame", "Camera is loading"))
        self.pushButton_2.setText(_translate("Frame", "Facial Register"))
        
        # event functions
        self.pushButton.clicked.connect(self.create_folder)
        
        
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

if __name__ == "__main__":
    
    import sys
    # Create a new QApplication object
    app = QApplication(sys.argv)

    New_menu = Register()
    New_menu.show() 

    sys.exit(app.exec_())