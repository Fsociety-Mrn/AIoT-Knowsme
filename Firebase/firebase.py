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
    def firebaseUpdate(self,keyName, name,data,time):
        
        print("check")
        if not name == 'No match detected':
            self.db.child("History").child(keyName).child(name).child(data).set(time)
            return
        
        self.db.child("History").child(keyName).child(name).push({ data:time })
    
    def firebaseCheck_ID(self,ID):
        data = self.firebaseRead("Account")
        for __, each in data.items():
            
            if each['idNumber'] == ID:
                return True,each['name']
            
        return False,""
    
    def firebaseRead(self,ID):
        data = self.db.child(ID).get().val()
        return data
    
    
# data = Firebase().firebaseCheck_ID("2019-201745")
# print(data)



