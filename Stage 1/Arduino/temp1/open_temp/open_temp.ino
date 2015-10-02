#include <EEPROM.h>

int maxAddress, address = 0;
int value;



void setup() {
  Serial.begin(9600);
  while (!Serial) {
    ;
  }
}

void loop() {  
  
  value = EEPROM.read(address);
  
  if (value > 50) {
    maxAddress = address;
    address = 0;
  }
  
  if (address == EEPROM.length()) {
    address = 0;
  }
  Serial.print(value, DEC);
  Serial.println();

  address += 1;
  

  delay(500);
}
