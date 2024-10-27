import time
import board
import busio
import adafruit_mlx90614

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

mlx = adafruit_mlx90614.MLX90614(i2c)

while True:
    ambientTemp = "{:.2f}".format(mlx.ambient_temperature)
    targetTemp = "{:.2f}".format(mlx.object_temperature)

    time.sleep(1)

    print("Ambient Temperature: ",ambientTemp)
    print("Target Temperature: ",targetTemp)