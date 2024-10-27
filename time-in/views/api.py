from flask import Blueprint,jsonify, request

import serial
import time



api = Blueprint('api', __name__)

@api.route('/api/serial-ir', methods=['GET'])
def serial_ir():
    
    try:

        # Define the serial port and baud rate
        ser = serial.Serial('COM5', 9600, timeout=1)  # Replace 'COM3' with the correct port name
        ser.reset_input_buffer()
        time.sleep(2)
        ser.flush()
        data = ser.readline().decode('utf-8').rstrip()
        api.config["target_temp"] = str(data).split(",")[0]
        ser.close()
        return jsonify(data)
    
    except:
        return jsonify("33,1")
    
  