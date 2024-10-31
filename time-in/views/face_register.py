
# PIP library installed
from flask import Blueprint, jsonify as json, request

import requests

# Custom Library
from models import Firebase as firebase
from utilities import ImageStorageManager as image_storage_manager

face_register = Blueprint('face_register', __name__)

# NOTE:  PA LI TAN ANG IP ADDRESS KA DA MAG PA PA LIT NG WIFI/CONNECTION\
API_ENDPOINT_TIMEOUT = 'http://192.168.100.38:2000'
BLURRINESS_VALUE = 0
RECOGNITION_THRESHOLD = 0.55


config = {
    "training": False
}


@face_register.route('/api/face-register/status', methods=['GET'])
def status():
    return json(config["training"])

  
@face_register.route('/api/face-register/id-verifications', methods=['POST']) 
def id_verifications():
    
    try:

        employee_id = request.json

        if not employee_id['employee_id']:
            return json({"message": 'Enter your Employee ID'}), 400
    
        result, name = firebase().verify_id(employee_id['employee_id'])

        if not result:
            return json({"message": 'Invalid Employee ID'}), 400
        
        data = firebase().get_registered_faces()
        image_storage_manager().remove_folder(data=data)
        image_storage_manager().create_folder(folder_name=f"{str(name).capitalize()}")

        response = requests.post(
            url= f"{API_ENDPOINT_TIMEOUT}/api/id-verifications", 
            json=request.json, 
            headers={
                'Content-Type': 'application/json'
            }
        )
    
        if not response.status_code == 200:
            return response.json(), response.status_code
    
        return json({"message": f"Folder {name} created successfully"}), 200

    except Exception as e:
        return json({"message": e}), 500