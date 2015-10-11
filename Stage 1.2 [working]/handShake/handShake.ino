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


// declarations
char mode = 'r';   // c: collect data, r: read and send to serial port
const int sendPin = 7;
const int collectPin = 5;
const int sensorPin = A0;
int blocks = 30;
int i = 0, j = 0, k = 0;



// Function Prototypes
void ComsHandShake(void);
void InitializeDataSend(void);
void MainDataSend(void);
byte ReadFromEEPROM(int addr);
void WriteToEEP(void);


/*
 * Function: setup
 * ---------------
 * Setup function
 * 
 */
void setup() {
    Serial.begin(9600);
    pinMode(sendPin, OUTPUT);
    pinMode(collectPin, OUTPUT);
    pinMode(sensorPin, INPUT);
    digitalWrite(sendPin, LOW);
}



/*
 * Function: loop
 * --------------
 * Main loop function
 * 
 */
 
void loop() {

    while (i == 0) { 
        ComsHandShake();
    }


    if (mode == 'r') {
        digitalWrite(sendPin, HIGH);
        digitalWrite(collectPin, LOW);
        while (j == 1) {
            InitializeDataSend();
        }
    
        while (k == 1) {
            MainDataSend();
        }
    }

    else if (mode == 'c') {
        digitalWrite(sendPin, LOW);
        digitalWrite(collectPin, HIGH);
        WriteToEEP();
    }
}



/*
 * Function: ComsHandShake
 * -------------------
 * Establishes connection with Python script
 * 
 */
 
void ComsHandShake(void) {

     // Establish connection with Python script
     if (Serial.available() > 0) {
          if (Serial.read() == 123) {
              Serial.write(124);
              i++;
              j = 1;
          }
     }
     return;

}



/*
 * Function: InitializeDataSend
 * ----------------------------
 * Initializes the data send by sending the number of blocks of data on EEPROM to python script
 * 
 */

void InitializeDataSend(void) {
     
     if(Serial.available() > 0) {
          if(Serial.read()==125) {
              j++;
              k = 1;


              blocks = 0;
              if (EEPROM.read(0) 


              
              // #1    #blocks / 256
              Serial.write(blocks / 256);
              // #2    #blocks % 256
              Serial.write(blocks % 256);       
          }
     }
     return;
}



/*
 * Function: MainDataSend
 * ----------------------------
 * Handles retrieval of data from eeprom, sending data to serial, and error checking with python script.
 * 
 */
 
void MainDataSend(void) {

    // send same data 2 times. Check for python response
    // if python response == 100, GOOD
    // else response == 111, send data 1 more time.

    byte value;
    int addr = 0;
    char checkingDataErrors;
    char sendingData = 'y';

    while (sendingData = 'y') {
        value = ReadFromEEPROM(addr);
    
        // First send
        Serial.write(value);
        // Second send (to compare to first)
        Serial.write(value);
        checkingDataErrors = 'y';
        
        while (checkingDataErrors == 'y') {
            if (Serial.available() > 0) {
                if (Serial.read() == 100) {
                    checkingDataErrors = 'n';
                    break;
                }
                else if (Serial.read() == 111) {
                    // Send data 3rd time to check
                    Serial.write(value); 
                    checkingDataErrors = 'n';
                    break;  
                }
            }
        }

        // Increment data address
        addr++;
    }
    
    return;
}



/*
 * Function: ReadFromEEPROM
 * ----------------------------
 * Retreives data (byte data type) at specified address location (passed in as argument from MainDataSend) and returns value
 * 
 */
 
byte ReadFromEEPROM(int addr) {
    byte value;
    value = EEPROM.read(addr);
    
    Serial.write(value);
    
    delay(100);
    return value;
}




/*
 * Function: WriteToEEP
 * --------------------
 * mode: 'r' read temp data and write to EEPROM
 * Data begins logging at addr = 2. First two bytes used for keeping track of number of blocks of data
 * 
 */
 
void WriteToEEP(void) {
     int blocks = 0;
    
     int addr = 2;
     int voltage;
     int timeStamp;
     int x, y, z, X, Y, Z, r_x, r_y, r_z;
     char blocksInitialized = 'n';
     
    
     Serial.println("Writing Data to EEPROM!");
     while (1) {
        
        voltage = analogRead(sensorPin) / 4;
        timeStamp = addr;

        // First print timeStamp:
        EEPROM.write(addr, timeStamp);
        

        // Then x, y, z acceleration (FINE)
        x = voltage + 25;
        y = voltage + 22;
        z = voltage + 26;

        EEPROM.write(addr, x);
        EEPROM.write(addr, y);
        EEPROM.write(addr, z);
        // Then X, Y, Z acceleration (ROUGH)

        X = voltage + 75;
        Y = voltage + 72;
        Z = voltage + 76;
        EEPROM.write(addr, X);
        EEPROM.write(addr, Y);
        EEPROM.write(addr, Z);
        // Then x, y, z rotation
  
        r_x = voltage + 15;
        r_y = voltage + 12;
        r_z = voltage + 16;
        EEPROM.write(addr, r_x);
        EEPROM.write(addr, r_y);
        EEPROM.write(addr, r_z);

        // Then pressure
        EEPROM.write(addr, voltage);
        
        // Then unique end 1
        EEPROM.write(addr, 123);
        // Then unique end 2
        EEPROM.write(addr, 77);



        // Prints to serial monitor

        // timestamp
        Serial.print(timeStamp);
        Serial.print(", ");

        // acceleration data
        Serial.print(x);
        Serial.print(", ");
        Serial.print(y);
        Serial.print(", ");
        Serial.print(z);
        Serial.print(", ");
        Serial.print(X);
        Serial.print(", ");
        Serial.print(Y);
        Serial.print(", ");
        Serial.print(Z);
        Serial.print(", ");

        // rotation data
        Serial.print(r_x);
        Serial.print(", ");
        Serial.print(r_y);
        Serial.print(", ");
        Serial.print(r_z);
        Serial.print(", ");

        // pressure data
        Serial.print(voltage);
        Serial.print(", ");

        // end key
        Serial.print(123);
        Serial.print(", ");
        Serial.print(77);
        Serial.println(", ");
        

        addr = addr + 1;
        
        // keep track of how many blocks in program
        blocks++;
        
        // Initializes block numbers to -1
        if (blocksInitialized == 'n' {
            EEPROM.write(0, -1) = ;
            EEPROM.write(1, -1) = ;
            blocksInitialized = 'y';
        }
        

        if (blocks < 256) {
            EEPROM.write(1, blocks);
        }
        else {
            EEPROM.write(0, blocks);
        }


        
        delay(100);
        
     }


    
     return;
}
