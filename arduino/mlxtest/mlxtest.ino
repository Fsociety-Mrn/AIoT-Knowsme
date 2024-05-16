#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
const int irSensorPin = 2; // IR sensor pin

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("MLX90614 Temperature Display");
  
  if (!mlx.begin()) {
    Serial.println("Error connecting to MLX sensor. Check wiring.");
    while (1);
  }

  pinMode(irSensorPin, INPUT); // Set IR sensor pin as input

  Serial.println("MLX sensor connected successfully!");
}

void loop() {
  float objectTemp = mlx.readObjectTempC(); // Read object temperature in Celsius
  int irSensorValue = digitalRead(irSensorPin); // Read IR sensor value
  
  Serial.print("Object Temperature: ");
  Serial.print(objectTemp);
  Serial.println(" °C");
  
  Serial.print("IR Sensor Value: ");
  Serial.println(irSensorValue);

  delay(1000); // Adjust delay as needed
}
