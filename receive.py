import serial

# Define the COM port and baud rate
com_port = 'COM5'
baud_rate = 9600

# Initialize the serial connection
ser = serial.Serial(com_port, baud_rate)

try:
    while True:
        # Read a line from the serial port
        line = ser.readline().decode('utf-8').strip()
        
        # Print the received data
        print("Received:", line)

except KeyboardInterrupt:
    # Close the serial port when Ctrl+C is pressed
    ser.close()
    print("Serial port closed.")
