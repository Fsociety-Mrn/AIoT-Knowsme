import pyrebase

from datetime import datetime

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
        
        if not name == 'No match detected':
            self.db.child("History").child(keyName).child(name).child(data).set(time)
            return
        
        self.db.child("History").child(keyName).child(name).push({ data:time })
        
    # read the data
    def firebaseRead_Today(self):
        
        try:
            
            # Get the current date
            current_date = datetime.now()

            # Format the date as "Month day year" e.g. "April 12 2024"
            formatted_date = current_date.strftime("%B %d %Y")

            return self.db.child("History").child(formatted_date).get().val()

        except Exception as e:
            pass
            print(f"firebaseRead: keyname is not existed")
            return False            
            
    def firebaseCheck_ID(self,ID):
        data = self.firebaseRead("Account")
        for __, each in data.items():
            
            if each['idNumber'] == ID:
                return True,each['name']
            
        return False,""
    
    def firebaseRead(self,ID):
        data = self.db.child(ID).get().val()
        return data
    


