#include <ctype.h>
#include <stdlib.h>
#include <math.h>

const int sensorPin = A0;
const float baselineTemp = 20.0;
int count = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  int sensorVal = analogRead(sensorPin);
  float voltage, temperature;

  
  voltage = (sensorVal/1024.0) * 5.0;
  temperature = (voltage - 0.5) * 100;
  

  if ( (isnan(temperature)) || (isinf(temperature)) ) {
    
  }
  else {
    Serial.println(temperature);   
  }
  

  count++;
 
  delay(100);
  
}
