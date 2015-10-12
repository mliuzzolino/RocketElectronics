// References
// https://learn.sparkfun.com/tutorials/sik-experiment-guide-for-arduino---v32/experiment-7-reading-a-temperature-sensor
// https://www.arduino.cc/en/Tutorial/EEPROMWrite
// https://www.arduino.cc/en/Tutorial/EEPROMRead
//
// The following may be useful to read on storing EEPROM data:
// http://www.vernier.com/engineering/arduino/store-data-eeprom/
//

#include <ctype.h>
#include <stdlib.h>
#include <math.h>
#include <EEPROM.h>


// Define pins
const int sensorPin = A0;   // Temperature Pin
const int readPin = 7;
const int buttonPin = 9;

int blocks = 0;

// 'r' read temp data and write to EEPROM
// 'w' write to serial
// 'e' erase eeprom data
char mode = 'w';



// SETUP of Serial port and PINS for LED
void setup() {
    Serial.begin(9600);
    pinMode(sensorPin, INPUT);
    pinMode(readPin, OUTPUT);
    pinMode(buttonPin, INPUT);
    
    digitalWrite(readPin, LOW);
    
}


void CheckComs() {
     int GM = 124;
    
     int incommingIDReq;

     
     while (1) {
        incommingIDReq = Serial.read();
        
        
        if (incommingIDReq == 123) {
           digitalWrite(readPin, HIGH);
           Serial.write(GM);
        }
        
     }

     Serial.write(blocks / 256);
     Serial.write(blocks % 256);
}


// MAIN LOOP
void loop() {
    int button = 0;
    
    CheckComs();
    
    
    
    button = digitalRead(buttonPin);

    if (button == HIGH) {
       
        digitalWrite(readPin, HIGH);
        delay(1000);
        
        switch (mode) {
            case 'r':
                WriteToEEP();
                break;
            case 'w':
                WriteToSerial();
                break;
            case 'e':
                ClearEEP();
                break;
        }
        
    }
      
    delay(100);
      
}






// 'r' read temp data and write to EEPROM
void WriteToEEP() {
     int addr = 0;
     int voltage;
     int button = LOW;

     
     
     Serial.println("Writing Data to EEPROM!");
     while (1) {
        button = digitalRead(buttonPin);
        if (button == HIGH) {
            digitalWrite(readPin, LOW);
            return;
        }
        
        voltage = analogRead(sensorPin) / 4;

        Serial.print("[");
        Serial.print(addr);
        Serial.print("] ");
        Serial.println(voltage);
        
        EEPROM.write(addr, voltage);
        addr = addr + 1;
        blocks++;
        delay(100);
     }

     return;
}

// 'w' write to serial
void WriteToSerial() {
     int addr = 0;
     int value;
     int button = LOW;
     
     //Serial.println("Writing Stored Data to Serial!");
     while (1) {
        button = digitalRead(buttonPin);
        if (button == HIGH) {
            digitalWrite(readPin, LOW);
            return;
        }
        value = EEPROM.read(addr);
        //Serial.print("[");
        //Serial.print(addr);
        //Serial.print("] ");
        Serial.write(value);
        
        addr = addr + 1;
        delay(100);
     }

     return;
}




// 'e' erase eeprom data
void ClearEEP() {
    int i = 0;
    Serial.println("Clearing EEPROM!");
    
    for (int i = 0 ; i < EEPROM.length() ; i++) {
      if ((i % 100 == 0) || (i % 50 == 0)) {
          digitalWrite(readPin, HIGH);
      }
      else {
          digitalWrite(readPin, LOW);
      }

      EEPROM.write(i, 0);
    }
    return;
    
}

