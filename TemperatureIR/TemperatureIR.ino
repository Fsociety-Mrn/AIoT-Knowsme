#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
const int irSensorPin = 2; // IR sensor pin
const int relay = 3; // IR sensor pin
void setup() {
  Serial.begin(9600);
  while (!Serial);


  
  if (!mlx.begin()) {

    while (1);
  }

  pinMode(irSensorPin, INPUT); // Set IR sensor pin as input
  pinMode(relay, OUTPUT);

}

void loop() {
  float objectTemp = mlx.readObjectTempC(); // Read object temperature in Celsius
  int irSensorValue = digitalRead(irSensorPin); // Read IR sensor value
  

  Serial.println(String(objectTemp + 2.0) + "," + String(irSensorValue));

  if (irSensorValue == 1) {
    digitalWrite(relay, HIGH); // Turn on the relay
  } else {
    digitalWrite(relay, LOW); // Turn off the relay
  }

  delay(200); // Adjust delay as needed
}