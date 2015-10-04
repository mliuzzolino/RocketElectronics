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

const int writePin = 5;
const int readPin = 9;
const int pausePin = 7;
const int sensorPin = A0;   // Temperature Pin
const float baselineTemp = 20.0;

int addr = 0;   // Initializes address at 0 for EEPROM

char mode = 'm';
char menuChoice = '0';

// SETUP of Serial port and PINS for LED
void setup() {
  Serial.begin(9600);
  pinMode(writePin, OUTPUT);
  pinMode(readPin, OUTPUT);
  pinMode(pausePin, OUTPUT);
  pinMode(sensorPin, INPUT);
}


// MAIN LOOP
void loop() {


  // MENU 
  if (mode == 'm') {
      Serial.println("     Menu");
      Serial.println("-----------------");
      Serial.println("  [w]rite Data");
      Serial.println("  [r]ead Data");
      Serial.println("-----------------");
      Serial.println("Type the number and press enter");
      Serial.println("Press [m]enu to return to menu,");
      Serial.println("or press any other key to pause during any point of the program.");

      while (menuChoice == '0') {
          digitalWrite(writePin, HIGH);
          digitalWrite(readPin, HIGH);
          digitalWrite(pausePin, LOW);
          
          // send data only when you receive data:
          if (Serial.available() > 0) {
      
              // read the incoming char:
              menuChoice = Serial.read();
      
              Serial.print("I received: ");
              Serial.println(menuChoice);
           

              if ((menuChoice == 'w') || (menuChoice == 'W')) {
                   Serial.println("\n");
                   Serial.println("Beginning to write data to EEPROM...");
                   WriteData(sensorPin);
                   mode = 'w';
              }
              else if ((menuChoice == 'r') || (menuChoice == 'R') ) {
                   Serial.println("\n");
                   Serial.println("Beginning to read data from EEPROM...");
                   ReadData(sensorPin);
                   mode = 'r';
              }
              else if ((menuChoice == 'm') || (menuChoice == 'M') ) {
                   Serial.println("\n");
                   Serial.println("Returning to menu...");
                   mode = 'm';
                   menuChoice = '1';
              }
              else {
                   Serial.println("\n");
                   Serial.println("************************************");
                   Serial.println("Error. Please enter a valid command.");
                   Serial.println("************************************");
                   mode = 'm';
                   menuChoice = '1';
              } // END INNER IF ELSE BRANCHING
          } // END OUTER IF ELSE BRANCHING
        
          
      }
        
  }
  else if (mode == 'w') {
      digitalWrite(writePin, HIGH);
      digitalWrite(readPin, LOW);
      digitalWrite(pausePin, LOW);
      WriteData(sensorPin);
  }
  else if (mode == 'r') {
      digitalWrite(writePin, LOW);
      digitalWrite(readPin, HIGH);
      digitalWrite(pausePin, LOW);
      ReadData(sensorPin);
  }
  else {

      // LED Outputs
      digitalWrite(writePin, LOW);
      digitalWrite(readPin, LOW);    
      digitalWrite(pausePin, HIGH);
   
      char userPause = 'y';
      Serial.print("Program Paused. Would you like to: ");
      Serial.println("[m]enu; [w]rite; [r]ead");
      while (userPause == 'y') {
           if (Serial.available() > 0) {
              
                  // read the incoming char:
                  mode = Serial.read();

                  if (mode == 'm') {
                        // Reset menuChoice to 0 to get out of infinite menu loop
                        menuChoice = '0';
                        userPause = 'n';
              
                        // Resets EEPROM memory to address 0
                        addr = 0;
                 
                        Serial.println("Returning to menu...");
                   }
                   else if (mode == 'w') {
                        menuChoice = 'w';
                        userPause = 'n';

                        Serial.print("Resuming writing data to EEPROM at address ");
                        Serial.print(addr);
                        Serial.println("...");
                   }
                   else if (mode == 'r') {
                        menuChoice = 'r';
                        userPause = 'n';

                        // Resets EEPROM memory to address 0 for reading
                        addr = 0;
                        Serial.println("Proceeding to read EEPROM data...");  
                   }
            } // END IF
       } // END WHILE
  } // END ELSE


  // Enables us to break out of data writing or reading and go back to menu
  if (Serial.available() > 0) {
      
              // read the incoming char:
              mode = Serial.read();

              
   } // END if
   else if (menuChoice == '1') {
          menuChoice = '0';
   }
    
} // END void loop 





void WriteData(int Pin) {
  
  // Declarations
  int sensorVal = analogRead(sensorPin);
  int voltVal;
  float voltage, degreesC;
  
  
  // First we'll measure the voltage at the analog pin. Normally
  // we'd use analogRead(), which returns a number from 0 to 1023.
  // Here we've written a function (further down) called
  // getVoltage() that returns the true voltage (0 to 5 Volts)
  // present on an analog input pin.
  voltage = getVoltage(sensorPin);
  
  // Now we'll convert the voltage to degrees Celsius.
  // This formula comes from the temperature sensor datasheet:
  // CONVERT IN PYTHON SCRIPT
  // degreesC = (voltage - 0.5) * 100.0;
  Serial.print("Address[");
  Serial.print(addr);
  Serial.print("]: \t");
  Serial.println(voltage);
  /***
    Write the value to the appropriate byte of the EEPROM.
    these values will remain there when the board is
    turned off.
  ***/

  voltVal = (voltage * 1000) / 4;
  
  EEPROM.write(addr, voltVal);
  /***
    Advance to the next address, when at the end restart at the beginning.

    Larger AVR processors have larger EEPROM sizes, E.g:
    - Arduno Duemilanove: 512b EEPROM storage.
    - Arduino Uno:        1kb EEPROM storage.
    - Arduino Mega:       4kb EEPROM storage.

    Rather than hard-coding the length, you should use the pre-provided length function.
    This will make your code portable to all AVR processors.
  ***/
  addr = addr + 1;
  if (addr == EEPROM.length()) {
    addr = 0;
  }

  /***
    As the EEPROM sizes are powers of two, wrapping (preventing overflow) of an
    EEPROM address is also doable by a bitwise and of the length - 1.

    ++addr &= EEPROM.length() - 1;
  ***/

  
 
  delay(100);
  return;
}



void ReadData(int Pin) {

  // Declarations
  byte value;
  float voltageVal;
  float voltage, degreesC;
  
  value = EEPROM.read(addr);  

  voltageVal = value;

  voltage = voltageVal * 4 / 1000;
  //Serial.print("Voltage: ");
  //Serial.print("\t");
  //Serial.println(voltage);

  degreesC = (voltage - 0.5) * 100.0;
  //Serial.print("Degrees C: ");
  //Serial.print("\t");
  

  Serial.print("Address[");
  Serial.print(addr);
  Serial.print("]: \t");
  Serial.println(degreesC);
  

  /***
    Advance to the next address, when at the end restart at the beginning.

    Larger AVR processors have larger EEPROM sizes, E.g:
    - Arduno Duemilanove: 512b EEPROM storage.
    - Arduino Uno:        1kb EEPROM storage.
    - Arduino Mega:       4kb EEPROM storage.

    Rather than hard-coding the length, you should use the pre-provided length function.
    This will make your code portable to all AVR processors.
  ***/
  addr = addr + 1;
  if (addr == EEPROM.length()) {
    addr = 0;
  }
  delay(100);
  return;
}


float getVoltage(int pin) {
  // This function has one input parameter, the analog pin number
  // to read. You might notice that this function does not have
  // "void" in front of it; this is because it returns a floating-
  // point value, which is the true voltage on that pin (0 to 5V).


  return (analogRead(pin) * 0.004882814);
  // This equation converts the 0 to 1023 value that analogRead()
  // returns, into a 0.0 to 5.0 value that is the true voltage
  // being read at that pin.
}

