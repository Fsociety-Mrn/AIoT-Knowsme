
import serial
from time import sleep


# Define the serial port and baud rate
ser = serial.Serial('COM4', 9600, timeout=1)  # Replace 'COM3' with the correct port name
ser.reset_input_buffer()
    
def serial_data():
    ser.flush()
    data = ser.readline().decode('utf-8').rstrip()
    print(data)
    sleep(1)
    return data

        

