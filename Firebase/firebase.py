import pyrebase

class Firebase:
    def __init__(self):
   
        # firebase API keys
        self.config = {
            "apiKey": "AIzaSyAFfT2IDTJN8ZvuBT521G5wlmhy2OxFzVk",
            "authDomain": "aiot-knows-me.firebaseapp.com", 
            "databaseURL": "https://aiot-knows-me-default-rtdb.asia-southeast1.firebasedatabase.app", 
            "storageBucket": "aiot-knows-me.appspot.com"
        }
        self.firebase = pyrebase.initialize_app(self.config)
        self.db = self.firebase.database() # realTime database
        
    # update the current data
    def firebaseUpdate(self,keyName, name,data):
        self.db.child(keyName).child(name).set(data)
    
