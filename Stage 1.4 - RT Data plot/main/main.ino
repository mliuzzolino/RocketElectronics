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
char mode = 'r';   // c: collect data, d: (download) read and send to serial port
char realTimeData = 'n';

// Set pins

const int RTDataPin = 11;
const int sendPin = 9;
const int collectPin = 7;
const int handShakePin = 5;
const int sensorPin = A0;


int blocks;


char handShakeSuccessful = 'n';




// Function Prototypes
void ComsHandShake(void);
void InitializeDataSend(void);
void MainDataSend(void);
byte ReadFromEEPROM(int addr);
char DataCollectInitialize(void);
void WriteToEEP(char realTimeData);


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
    pinMode(handShakePin, OUTPUT);
    pinMode(RTDataPin, OUTPUT);
    pinMode(sensorPin, INPUT);
    
    
}



/*
 * Function: loop
 * --------------
 * Main loop function
 * 
 */
 
void loop() {

    
    
    while (handShakeSuccessful == 'n') { 
        ComsHandShake();
    }

    // Get mode
    mode = GetMode();

    // Mode 'd': Download data to serial for python to read
    if (mode == 'd') {        
        // Initialize the data send
        InitializeDataSend();
        
        // Enter data send main program
        MainDataSend();
    }
    // Mode 'c': Collect Data from sensors and store to EEPROM
    else if (mode == 'c') {
        InitializeBlock();
        realTimeData = DataCollectInitialize();
        WriteToEEP(realTimeData);
    }
}









/*
 * Function: ComsHandShake
 * -----------------------------------------
 * Establishes connection with Python script
 * 
 */
 
void ComsHandShake(void) {

    // Establish connection with Python script
    if (Serial.available() > 0) {
        if (Serial.read() == 123) {
            Serial.write(124);
            handShakeSuccessful = 'y';
            digitalWrite(handShakePin, HIGH);
              
        }
    }
    return;

}


/*
 * Function: GetMode
 * -------------------
 * Obtains mode from user (collect data, download data, etc)
 * 
 */

char GetMode(void) {

    int userMode;
    
    while (1) {
        if (Serial.available() > 0) {
            userMode = Serial.read();
            if (userMode == 0) {
                Serial.write(126);
                digitalWrite(sendPin, LOW);
                digitalWrite(collectPin, HIGH);
                
                return 'c';
            }
            else if (userMode == 1) {
                delay(500);
                Serial.write(127);
                digitalWrite(sendPin, HIGH);
                digitalWrite(collectPin, LOW);
                
                return 'd';
            }
            else {
                Serial.write(128);
            }
        }
    }
    

    return mode;
}





/*
 * Function: InitializeDataSend
 * ----------------------------
 * Initializes the data send by sending the number of blocks of data on EEPROM to python script
 * 
 *  REFERENCE for code below: http://playground.arduino.cc/Code/EEPROMReadWriteLong
 */

void InitializeDataSend(void) {

    char dataInitialized = 'n';
    long one, two;
    blocks = 0;
    two = EEPROM.read(0);
    one = EEPROM.read(1);
     
    
    while (dataInitialized == 'n') {
    
        if (Serial.available() > 0) {
            if (Serial.read() == 125) {
                // Case 1: < 256 blocks
                if (EEPROM.read(0) == -1) {
                    blocks = EEPROM.read(1);
                }
                // Case 2: > 256 blocks
                else {
                    blocks = EEPROM.read(1);
                    //blocks = ((two << 16) & 0xFFFFFF) + ((one << 24) & 0xFFFFFFFF);  
                }

                // Write block data to serial for python script to read                
                Serial.write(blocks / 256);   // #1    #blocks / 256
                Serial.write(blocks % 256);   // #2    #blocks % 256

                dataInitialized == 'y';
                
                return;
            }
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
    int userContinue, addr = 2;
    char checkingDataErrors;
            
   
    delay(2000);
    while (1) {
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
        
        //delay(1000);

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

    delay(100);
    return value;
}




void InitializeBlock(void) {
    EEPROM.write(0, -1);
    EEPROM.write(1, -1);

    return;
}




char DataCollectInitialize(void) {
    char dataCollectInitialize = 'n';
    char realTimeData = 'n';
    int val;
    int blinkErrorCnt = 0;
    
    while (dataCollectInitialize == 'n') {
    
        if (Serial.available() > 0) {
            val = Serial.read();
            if (val == 244) {
                Serial.write(11);
                digitalWrite(RTDataPin, HIGH);
                return 'y';
                
            }
            else if (val == 245) {
                Serial.write(12);
                digitalWrite(RTDataPin, LOW);
                return 'n';
            }
            else {
                Serial.write(13);
                realTimeData = 'n';

                while (blinkErrorCnt < 10) {
                    if (blinkErrorCnt % 2 == 0) {
                        digitalWrite(RTDataPin, LOW);
                        delay(4000);
                    }
                    else {
                        digitalWrite(RTDataPin, LOW);
                        delay(4000);
                    }
                    blinkErrorCnt++;
                }
                
                return 'n';
            }
        }
    }
    
    return realTimeData;
  
}


/*
 * Function: WriteToEEP
 * --------------------
 * mode: 'r' read temp data and write to EEPROM
 * Data begins logging at addr = 2. First two bytes used for keeping track of number of blocks of data
 * 
 */
 
void WriteToEEP(char realTimeData) {
    int blocks = 0;
    
    int addr = 2;
    int voltage;
    int id_0 = 0, id_1 = 0;
    int timeStamp_0 = 0, timeStamp_1 = 0;
    int x_0, x_1, y_0, y_1, z_0, z_1, X_0, X_1, Y_0, Y_1, Z_0, Z_1;
    int r_x_0, r_x_1, r_y_0, r_y_1, r_z_0, r_z_1, alt_0, alt_1;
    
     
    while (1) {
      
        voltage = analogRead(sensorPin) / 4;
        

        // First get ID:
        EEPROM.write(addr, id_1);
        addr++;
        EEPROM.write(addr, id_0);
        addr++;

        // Then get timeStamp:
        EEPROM.write(addr, timeStamp_1);
        addr++;
        EEPROM.write(addr, timeStamp_0);
        addr++;
        
        
        // Then x, y, z acceleration (FINE)
        x_0 = voltage + 25;
        x_1 = 0;
        y_0 = voltage + 22;
        y_1 = 0;
        z_0 = voltage + 26;
        z_1 = 0;
        
        EEPROM.write(addr, x_1);
        addr++;
        EEPROM.write(addr, x_0);
        addr++;
        EEPROM.write(addr, y_1);
        addr++;
        EEPROM.write(addr, y_0);
        addr++;
        EEPROM.write(addr, z_1);
        addr++;
        EEPROM.write(addr, z_0);
        addr++;
        
        
        
        // Then X, Y, Z acceleration (ROUGH)
        
        X_0 = voltage;
        X_1 = 0;
        Y_0 = voltage;
        Y_1 = 0;
        Z_0 = voltage;
        Z_1 = 0;
        
        EEPROM.write(addr, X_1);
        addr++;
        EEPROM.write(addr, X_0);
        addr++;
        EEPROM.write(addr, Y_1);
        addr++;
        EEPROM.write(addr, Y_0);
        addr++;
        EEPROM.write(addr, Z_1);
        addr++;
        EEPROM.write(addr, Z_0);
        addr++;
        
        
        
        // Then x, y, z rotation
        
        r_x_0 = voltage + 15;
        r_x_1 = 0;
        r_y_0 = voltage + 12;
        r_y_1 = 0;
        r_z_0 = voltage + 16;
        r_z_1 = 0;
        EEPROM.write(addr, r_x_1);
        addr++;
        EEPROM.write(addr, r_x_0);
        addr++;
        EEPROM.write(addr, r_y_1);
        addr++;
        EEPROM.write(addr, r_y_0);
        addr++;
        EEPROM.write(addr, r_z_1);
        addr++;
        EEPROM.write(addr, r_z_0);
        addr++;
        
        
        
        
        
        // Then pressure
        alt_0 = voltage;
        alt_1 = 0;
        EEPROM.write(addr, alt_1);
        addr++;
        EEPROM.write(addr, alt_0);
        addr++;
        
        
        // Then unique end 1
        EEPROM.write(addr, 123);
        addr++;
        // Then unique end 2
        EEPROM.write(addr, 77);
        addr++;
        
        
        
        // Prints to serial monitor
        if (realTimeData == 'y') {
            //Serial.write(blocks);
            Serial.write(blocks);
            Serial.write(X_0);
            Serial.write(Y_0);
            Serial.write(Z_0);
            
        }
        else if (realTimeData == 'n') {
            
            // timestamp
            Serial.write(blocks);
            
        }
        
          
        // keep track of how many blocks in program
        blocks++;
        
        if (blocks < 256) {
            EEPROM.write(1, blocks);
        }
        else {
            EEPROM.write(0, blocks);
        } 
        
        timeStamp_0++;
        delay(100); 

        
    }   // END WHILE
    
    
    return;
}
