import os
import shutil

class ImageStorageManager:

    def __init__(self):
        
        self.folder_path = os.path.join('time-in', 'library', 'facial_recognition','registered-faces').replace("\\", "/")
        
        
    def remove_folder(self, data):
        
        names_to_keep = [each['name'] for _, each in data.items()]
        all_folders = os.listdir(self.folder_path)
    
        for folder_name in all_folders:
            
            if folder_name not in names_to_keep:
                
                folder_path = os.path.join(self.folder_path, folder_name)
                
                if os.path.isdir(folder_path):
                    shutil.rmtree(folder_path)
                    
                    
    def create_folder(self,folder_name):
        
        folder_path = f"{self.folder_path}/{folder_name}"
        
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        os.makedirs(folder_path)
    
        return folder_path