import os
import shutil
from flask import Blueprint, jsonify, request


import requests


face_register = Blueprint('face_register', __name__)

# NOTE:  PALITAN ANG IP ADDRESS KADA MAG PAPALIT NG WIFI/CONNECTION
API_ENDPOINT_TIMEOUT = 'http://192.168.100.38:2000'
BLURRINESS_VALUE = 0
RECOGNITION_THRESHOLD = 0.55

config = {
    "training": False
}


@face_register.route('/api/face-register/status', methods=['GET'])
def status():
    return jsonify(config["training"])

  
@face_register.route('/api/id-verifications', methods=['POST']) 
def id_verifications():
    
    ID = request.json
    headers = {
        'Content-Type': 'application/json'
    }
    if not ID['employee_id']:
        return jsonify({"message": 'enter your fullname'}), 400
    
    result, name = Fbase().firebaseCheck_ID(ID['employee_id'])
    if not result:
        return jsonify({"message": 'Invalid Employee ID'}), 400

    remove_folder()

    folder_name = f"{str(name).capitalize()}"

    path = f"Jolo_Recognition/Registered-Faces/{folder_name}"

    if os.path.exists(path):

        shutil.rmtree(path)

    os.makedirs(path)
    face_register.config['REGISTER_FACIAL'] = path
    
    
    response = requests.post(f"{API_ENDPOINT_TIMEOUT}/api/id-verifications", json=request.json, headers=headers)
    
    if not response.status_code == 200:
        return response.json(), response.status_code
    
    return jsonify({"message": f"Folder {path} created successfully"}), 200