// References
// https://learn.sparkfun.com/tutorials/sik-experiment-guide-for-arduino---v32/experiment-7-reading-a-temperature-sensor
// https://www.arduino.cc/en/Tutorial/EEPROMWrite
// https://www.arduino.cc/en/Tutorial/EEPROMRead
//
// The following may be useful to read on storing EEPROM data:
// http://www.vernier.com/engineering/arduino/store-data-eeprom/
// Info on 2-byte storage and retrieval
// http://playground.arduino.cc/Code/EEPROMReadWriteLong
//

#include <ctype.h>
#include <stdlib.h>
#include <math.h>
#include <EEPROM.h>
#include <SoftwareSerial.h>

SoftwareSerial XBee(2, 3);

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
long ReadFromEEPROM(int addr, int evenCheckCounter);
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
    XBee.begin(9600);
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
    int cnt = 0;
    // Establish connection with Python script
    if (XBee.available() > 0) {
        if (XBee.read() == 123) {         // python sends 123 to unit on rocket
            while (cnt < 1000) {
            XBee.write(124);              // rocket writes 124 on xbee to send back to laptop python script
            cnt++;
            }
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

    int userMode, cnt = 0;
    
    while (1) {
        if (XBee.available() > 0) {
            userMode = XBee.read();
            if (userMode == 0) {
                while (cnt < 1000) {
                XBee.write(126);        // rocket confirms user mode change by sending 126 to computer on ground
                cnt++;
                }
                digitalWrite(sendPin, LOW);
                digitalWrite(collectPin, HIGH);
                
                return 'c';
            }
            else if (userMode == 1) {
                delay(2000);
                XBee.write(127);      // rocket confirms user mode change by sending 127 to computer on ground
                digitalWrite(sendPin, HIGH);
                digitalWrite(collectPin, LOW);
                
                return 'd';
            }
            else {
                XBee.write(128);       // rocket confirms user mode change error by sending 128 to computer on ground
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
            if (Serial.read() == 125) {         // read 125 from ground computer
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
                XBee.write(blocks / 256);   // #1    #blocks / 256        // rocket sends data to ground
                XBee.write(blocks % 256);   // #2    #blocks % 256

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

    long value;
    int userContinue, addr = 2;
    char checkingDataErrors;
    int evenCheckCounter = 0;
   
    delay(2000);
    while (1) {

        value = ReadFromEEPROM(addr, evenCheckCounter);
        evenCheckCounter++;

        // First send
        XBee.write(value);
        // Second send (to compare to first)
        XBee.write(value);
        
        checkingDataErrors = 'y';
        
        while (checkingDataErrors == 'y') {
            if (Serial.available() > 0) {
                if (Serial.read() == 100) {
                    checkingDataErrors = 'n';
                    break;
                }
                else if (Serial.read() == 111) {
                    // Send data 3rd time to check
                    XBee.write(value); 
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
 
long ReadFromEEPROM(int addr, int evenCheckCounter) {
    long value;
    
    value = EEPROM.read(addr);
    delay(100);
    return ((value << 0) & 0xFF);
      
   
}




void InitializeBlock(void) {
    EEPROM.write(0, -1);
    EEPROM.write(1, -1);

    return;
}




char DataCollectInitialize(void) {
    char dataCollectInitialize = 'n';
    char realTimeData = 'n';
    int val, cnt = 0;
    int blinkErrorCnt = 0;
    
    while (dataCollectInitialize == 'n') {
    
        if (XBee.available() > 0) {
            val = XBee.read();
            if (val == 244) {
                while (cnt < 1000) {
                    XBee.write(11);
                    cnt++;
                }

                digitalWrite(RTDataPin, HIGH);
                return 'y';
                
            }
            else if (val == 245) {
                delay(2000);
                XBee.write(12);
                digitalWrite(RTDataPin, LOW);
                return 'n';
            }
            else {
                delay(2000);
                XBee.write(13);
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

    int id = 0;
    byte id_0, id_1;

    int timeStamp = 0;
    byte timeStamp_0, timeStamp_1;

    int x, y, z;
    byte x_0, x_1, y_0, y_1, z_0, z_1;

    int X, Y, Z;
    byte X_0, X_1, Y_0, Y_1, Z_0, Z_1;

    int r_x, r_y, r_z;
    byte r_x0, r_x1, r_y0, r_y1, r_z0, r_z1;

    int alt;
    byte alt_0, alt_1;
    
    int endCheck = 31565;
    byte endCheck_0, endCheck_1;
    
     
    while (1) {
      
        voltage = analogRead(sensorPin);
        
        // Data Format: ID, timeStamp, x, y, z, X, Y, Z, r_x, r_y, r_z, alt, end_check

        // First get ID:
        id_0 = (id & 0xFF);
        id_1 = ((id >> 8) & 0xFF);
        EEPROM.write(addr, id_1);
        addr++;
        EEPROM.write(addr, id_0);
        addr++;

        // Then get timeStamp:
        timeStamp_1 = (timeStamp & 0xFF);
        timeStamp_0 = ((timeStamp >> 8) & 0xFF);

        EEPROM.write(addr, timeStamp_1);
        addr++;
        EEPROM.write(addr, timeStamp_0);
        addr++;
        
        // Then x, y, z acceleration (FINE)
        x = voltage;
        y = voltage;
        z = voltage;
      
        x_0 = (x & 0xFF);
        x_1 = ((x >> 8) & 0xFF);
        y_0 = (y & 0xFF);
        y_1 = ((y >> 8) & 0xFF);
        z_0 = (z & 0xFF);
        z_1 = ((z >> 8) & 0xFF);

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
        
        X = voltage;
        Y = voltage;
        Z = voltage;

        X_0 = (X & 0xFF);
        X_1 = ((X >> 8) & 0xFF);
        Y_0 = (Y & 0xFF);
        Y_1 = ((Y >> 8) & 0xFF);
        Z_0 = (Z & 0xFF);
        Z_1 = ((Z >> 8) & 0xFF);
        
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
        
        r_x = voltage;
        r_y = voltage;
        r_z = voltage;

        r_x0 = (r_x & 0xFF);
        r_x1 = ((r_x >> 8) & 0xFF);
        r_y0 = (r_y & 0xFF);
        r_y1 = ((r_y >> 8) & 0xFF);
        r_z0 = (r_z & 0xFF);
        r_z1 = ((r_z >> 8) & 0xFF);


        
        EEPROM.write(addr, r_x1);
        addr++;
        EEPROM.write(addr, r_x0);
        addr++;
        EEPROM.write(addr, r_y1);
        addr++;
        EEPROM.write(addr, r_y0);
        addr++;
        EEPROM.write(addr, r_z1);
        addr++;
        EEPROM.write(addr, r_z0);
        addr++;
        
        
        
        
        
        // Then pressure
        alt = voltage;
        alt_0 = (alt & 0xFF);
        alt_1 = ((alt >> 8) & 0xFF);

 
        EEPROM.write(addr, alt_1);
        addr++;
        EEPROM.write(addr, alt_0);
        addr++;
        
        
        endCheck_0 = (endCheck & 0xFF);
        endCheck_1 = ((endCheck >> 8) & 0xFF);
        // Then unique end 1
        EEPROM.write(addr, endCheck_1);
        addr++;
        // Then unique end 2
        EEPROM.write(addr, endCheck_0);
        addr++;
        
        
        
        // Prints to serial monitor
        if (realTimeData == 'y') {
            

            // Data Format: id_0, id_1, timeStamp_0, timeStamp_1,
            //              x_0, x_1, y_0, y_1, z_0, z_1, 
            //              X_0, X_1, Y_0, Y_1, Z_0, Z_1, 
            //              r_x0, r_x1, r_y0, r_y1, r_z0, r_z1, 
            //              alt_0, alt_1, endCheck0, endCheck1

            XBee.write(blocks);           // 0

            // Fine acceleration
            XBee.write(x_0);              // 1
            XBee.write(x_1);              // 2
            XBee.write(y_0);              // 3
            XBee.write(y_1);              // 4
            XBee.write(z_0);              // 5
            XBee.write(z_1);              // 6

            // Rough acceleration
            XBee.write(X_0);              // 7
            XBee.write(X_1);              // 8
            XBee.write(Y_0);              // 9
            XBee.write(Y_1);              // 10
            XBee.write(Z_0);              // 11
            XBee.write(Z_1);              // 12

            // Rotational data
            XBee.write(r_x0);             // 13
            XBee.write(r_x1);             // 14
            XBee.write(r_y0);             // 15
            XBee.write(r_y1);             // 16
            XBee.write(r_z0);             // 17
            XBee.write(r_z1);             // 18

            // Altitude data
            XBee.write(alt_0);            // 19
            XBee.write(alt_1);            // 20
        }
        else if (realTimeData == 'n') {
            
            // timestamp
            XBee.write(blocks);
            
        }
        
          
        // keep track of how many blocks in program
        blocks++;
        
        if (blocks < 256) {
            EEPROM.write(1, blocks);
        }
        else {
            EEPROM.write(0, blocks);
        } 
        
        id++;
        timeStamp_0++;
        delay(100); 

        
    }   // END WHILE
    
    
    return;
}