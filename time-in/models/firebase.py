import pyrebase

class Firebase:
    def __init__(self):
  
        self.configuration = {
            "apiKey": "AIzaSyAFfT2IDTJN8ZvuBT521G5wlmhy2OxFzVk",
            "authDomain": "aiot-knows-me.firebaseapp.com", 
            "databaseURL": "https://aiot-knows-me-default-rtdb.asia-southeast1.firebasedatabase.app", 
            "storageBucket": "aiot-knows-me.appspot.com"
        }
        self.firebase = pyrebase.initialize_app(self.configuration)
        self.realtime_db = self.firebase.database() # realTime database
        

    def log_employee_time(self,keyName, name,data,time,Temp="N/A"):
        self.realtime_db.child("Test").child(keyName).push({
                                                        "name": name,
                                                        "time": time,
                                                        "data": data,
                                                        "temp": Temp
                                                    })
    def verify_id(self,ID):
        data = self.get_registered_faces()
        for __, each in data.items():
            
            if each['idNumber'] == ID:
                return True,each['name']
            
        return False,""
    
    def get_registered_faces(self):
        data = self.realtime_db.child("Account").get().val()
        return data
    
    

