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
const int writePin = 5;
const int readPin = 9;
const int pausePin = 7;
const int collectDataBtn = 3;
const int sensorPin = A0;   // Temperature Pin









// SETUP of Serial port and PINS for LED
void setup() {
  Serial.begin(9600);
  pinMode(writePin, OUTPUT);
  pinMode(readPin, OUTPUT);
  pinMode(pausePin, OUTPUT);
  pinMode(sensorPin, INPUT);
  pinMode(collectDataBtn, INPUT);

  return;
}







char mode = 'm';
char prevMode = 'm';



// MAIN LOOP
void loop() {


    switch (mode) {

        // MENU mode
        case 'm':
        case 'M':
            // Set LEDs to indicate menu mode
            digitalWrite(writePin, HIGH);
            digitalWrite(readPin, HIGH);
            digitalWrite(pausePin, LOW);

            // Print menu to serial port
            PrintMenu();
            while (mode == 'm') {
                if (Serial.available() > 0) {
                    prevMode = mode;
                    mode = Serial.read();
                }
            }
            break;

        // WRITE mode
        case 'w':
        case 'W':

            Serial.println("Entering WRITE mode...");

            mode = WriteData(sensorPin, collectDataBtn);
            break;

        // READ mode
        case 'r':
        case 'R':

            // Sets LEDs to indicate READ mode
            digitalWrite(writePin, LOW);
            digitalWrite(readPin, HIGH);
            digitalWrite(pausePin, LOW);

            Serial.println("Entering READ mode...");

            mode = ReadData(sensorPin, prevMode);
            break;

        // CLEAR eeprom mode
        case 'c':
        case 'C':
            Serial.println("Clearing EEPROM...");

            ClearEEPROM();

            Serial.println("EEPROM cleared!");
            Serial.println("Returning to menu...\n\n");
            mode = 'm';
            break;

        // PAUSE mode
        default:
            // Sets LEDs to indicate PAUSE mode
            digitalWrite(writePin, LOW);
            digitalWrite(readPin, LOW);
            digitalWrite(pausePin, HIGH);

            mode = 'p';

            mode = PauseMode(mode);
            break;
    }

} // END void loop


void ClearEEPROM(void) {
    for (int i = 0 ; i < EEPROM.length() ; i++) {

      if ((i % 100 == 0) || (i % 50 == 0)) {
          digitalWrite(writePin, HIGH);
          digitalWrite(readPin, LOW);
          digitalWrite(pausePin, LOW);
      }
      else {
          digitalWrite(writePin, LOW);
          digitalWrite(readPin, LOW);
          digitalWrite(pausePin, HIGH);

      }

      EEPROM.write(i, 0);
    }
    return;
}





char CheckModeChange(void) {

  if (Serial.available() > 0) {

      // read the incoming char:
      prevMode = mode;
      mode = Serial.read();

   }
   return mode;

}



void PrintMenu(void) {
  Serial.println("  **  Menu  **    ");
  Serial.println("------------------");
  Serial.println("  [W]rite Data    ");
  Serial.println("  [R]ead  Data    ");
  Serial.println("  [C]lear Data    ");
  Serial.println("------------------");
  Serial.println("Type the number and press enter");
  Serial.println("Enter [m]enu to return to menu at any point,");
  Serial.println("or press any other key to pause during any point of the program.\n\n\n");

  return;
}




char PauseMode(char mode){

    Serial.println("Program Paused. Choose an option from the following to continue: ");
    Serial.println("[m]enu");
    Serial.println("[w]rite");
    Serial.println("[r]ead");
    Serial.println("[c]lear \n");

    while (mode == 'p') {
        if (Serial.available() > 0) {
            mode = Serial.read();
        }
    }

    return mode;

}




char WriteData(int sensorPin, int collectDataBtn) {

    // Declarations
    int cnt, voltVal;
    int addr = 0;   // Initializes address at 0 for EEPROM
    int beginData = 0;
    float voltage, degreesC;
    char mode = 'w';

    // Collect data when button pushed. This will be replaced by z-axis acceleration threshold
    // of rocket.
    Serial.println("Waiting for launch to begin...");
    while (beginData == 0) {

        if (cnt > 20000) {
          cnt = 0;
        }

        else if (cnt < 10000) {
            digitalWrite(writePin, LOW);
            digitalWrite(readPin, LOW);
            digitalWrite(pausePin, LOW);
        }
        else {
            digitalWrite(writePin, HIGH);
            digitalWrite(readPin, LOW);
            digitalWrite(pausePin, LOW);
        }
        cnt++;

        if (digitalRead(collectDataBtn) == HIGH) {
          beginData = 1;
        }

        prevMode = mode;
        mode = CheckModeChange();
        if (prevMode != mode) {
            beginData = 1;
        }


    }

    digitalWrite(writePin, HIGH);
    digitalWrite(readPin, LOW);
    digitalWrite(pausePin, LOW);
    // Write Data loop
    while (mode == 'w') {
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
        //Serial.print("Address[");
        //Serial.print(addr);
        //Serial.print("]: \t");
        Serial.println(voltage);
        /***
          Write the value to the appropriate byte of the EEPROM.
          these values will remain there when the board is
          turned off.
        ***/

        // Convert for storage to EEPROM
        voltVal = (voltage * 1000) / 4;

        // Write to EEPROM
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


        /***
          As the EEPROM sizes are powers of two, wrapping (preventing overflow) of an
          EEPROM address is also doable by a bitwise and of the length - 1.

          ++addr &= EEPROM.length() - 1;
        ***/

        // Check for mode change
        mode = CheckModeChange();
        delay(100);
    }

    return mode;
}






char ReadData(int Pin, char prevMode) {

    // Declarations
    byte value;
    float voltageVal, voltage, degreesC;
    int addr = 0;
    char mode = 'r';

    // Checks previous mode. If previous mode was write, now that we are reading
    // we should reset the EEPROM address to 0 so we can read from the beginning.

    if ( (prevMode == 'w') || (prevMode == 'W') ) {
        addr = 0;
    }


    while (mode == 'r') {
        value = EEPROM.read(addr);

        voltageVal = value;

        voltage = voltageVal * 4 / 1000;
        //Serial.print("Voltage: ");
        //Serial.print("\t");
        //Serial.println(voltage);

        degreesC = (voltage - 0.5) * 100.0;
        //Serial.print("Degrees C: ");
        //Serial.print("\t");


        //Serial.print("Address[");
        //Serial.print(addr);
        //Serial.print("]: \t");
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
        // Check for mode change
        mode = CheckModeChange();

        delay(100);
    }

    return mode;
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
