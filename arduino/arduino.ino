#include <Wire.h>
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();

void setup() {
  Serial.begin(9600);
  mlx.begin();
}

void loop() {
  delay(2000);
  
  float targetTemp;
  char buffer[10];
  
  mlx.readObjectTempC();
  targetTemp = mlx.objectTemperature();
  
  dtostrf(targetTemp, 4, 2, buffer); // Convert float to char array with 2 decimal places
  
  Serial.println(buffer);
  
  delay(1000);
}
