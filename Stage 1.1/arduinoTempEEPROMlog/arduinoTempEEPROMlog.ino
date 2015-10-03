// Code pieces taken from 
// https://learn.sparkfun.com/tutorials/sik-experiment-guide-for-arduino---v32/experiment-7-reading-a-temperature-sensor

#include <ctype.h>
#include <stdlib.h>
#include <math.h>
#include <EEPROM.h>


const int sensorPin = A0;
const float baselineTemp = 20.0;
char mode = 'm';
int addr = 0;
char menuChoice = '0';


void setup() {
  Serial.begin(9600);
}

void loop() {
  
  if (mode == 'm') {

      Serial.println("Menu");
      Serial.println("--------------");
      Serial.println("1. Pre-launch");
      Serial.println("2. Post-launch");
      Serial.println("--------------");
      Serial.println("Type the number and press enter");
      Serial.println("Press [m]enu to return to menu at any point.");

      while (menuChoice == '0') {
          // send data only when you receive data:
          if (Serial.available() > 0) {
      
              // read the incoming char:
              menuChoice = Serial.read();
      
              Serial.print("I received: ");
              Serial.println(menuChoice);
           }

           if (menuChoice == '1') {
              Serial.println("Beginning to write data to EEPROM...");
              WriteData(sensorPin);
              mode = 'w';
           }
           else if (menuChoice == '2') {
              Serial.println("Beginning to read data from EEPROM...");
              ReadData(sensorPin);
              mode = 'r';
           }
      }
        
  }
  else if (mode == 'w') {
      WriteData(sensorPin);
  }
  else if (mode == 'r') {
      ReadData(sensorPin);
  }
  
  if (Serial.available() > 0) {
      
              // read the incoming char:
              mode = Serial.read();

              
              // Reset menuChoice to 0 to get out of infinite menu loop
              menuChoice = '0';

              // Resets EEPROM memory to address 0
              addr = 0;

              
              Serial.println("Returning to menu...");
              
           }
}

void WriteData(int Pin) {
  
  // Declarations
  int sensorVal = analogRead(sensorPin);
  int voltVal, count = 0;
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
  Serial.print("Address: ");
  Serial.print(addr);
  Serial.print("\t");
  Serial.println(voltage);
  /***
    Write the value to the appropriate byte of the EEPROM.
    these values will remain there when the board is
    turned off.
  ***/

  voltVal = (voltage * 1000) / 4;
  Serial.print("voltVal: ");
  Serial.print("\t");
  Serial.println(voltVal);
  
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

  count++;
 
  delay(100);
  return;
}



void ReadData(int Pin) {

  // Declarations
  byte value;
  float voltageVal;
  float voltage, degreesC;
  
  value = EEPROM.read(addr);  
  Serial.print("Address: ");
  Serial.print(addr);
  Serial.print("\t");
  Serial.println(value, DEC);



  voltageVal = value;


  voltage = voltageVal * 4 / 1000;
  //Serial.print("Voltage: ");
  //Serial.print("\t");
  //Serial.println(voltage);

  degreesC = (voltage - 0.5) * 100.0;
  //Serial.print("Degrees C: ");
  //Serial.print("\t");
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

  // You can write your own functions that take in parameters
  // and return values. Here's how:

    // To take in parameters, put their type and name in the
    // parenthesis after the function name (see above). You can
    // have multiple parameters, separated with commas.

    // To return a value, put the type BEFORE the function name
    // (see "float", above), and use a return() statement in your code
    // to actually return the value (see below).

    // If you don't need to get any parameters, you can just put
    // "()" after the function name.

    // If you don't need to return a value, just write "void" before
    // the function name.

  // Here's the return statement for this function. We're doing
  // all the math we need to do within this statement:

  return (analogRead(pin) * 0.004882814);
  // This equation converts the 0 to 1023 value that analogRead()
  // returns, into a 0.0 to 5.0 value that is the true voltage
  // being read at that pin.
}

