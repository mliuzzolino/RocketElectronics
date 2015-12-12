/*****************************************************************
XBee_Serial_Passthrough.ino

Set up a software serial port to pass data between an XBee Shield
and the serial monitor.

Hardware Hookup:
  The XBee Shield makes all of the connections you'll need
  between Arduino and XBee. If you have the shield make
  sure the SWITCH IS IN THE "DLINE" POSITION. That will connect
  the XBee's DOUT and DIN pins to Arduino pins 2 and 3.

*****************************************************************/
// We'll use SoftwareSerial to communicate with the XBee:
#include <ctype.h>
#include <stdlib.h>
#include <math.h>
#include <EEPROM.h>
// XBee's DOUT (TX) is connected to pin 2 (Arduino's Software RX)
// XBee's DIN (RX) is connected to pin 3 (Arduino's Software TX)


void setup()
{
  // Set up both ports at 9600 baud. This value is most important
  // for the XBee. Make sure the baud rate matches the config
  // setting of your XBee.
  
  Serial.begin(9600);
  Serial.println("Arduino started sending bytes via XBee");
}

void loop()
{
  if (Serial.available())
  { // If data comes in from serial monitor, send it out to XBee
    Serial.write(Serial.read());    // from rocket TO computer
  }
  if (Serial.available())
  { // If data comes in from XBee, send it out to serial monitor
    Serial.write("Yes");    // from computer TO rocket
    Serial.write(Serial.read());
  }
}

