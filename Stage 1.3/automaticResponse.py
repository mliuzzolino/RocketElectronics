#The only aim of this programm is to simulate the response of the device to send data to our downloading program through serial

import sys
import glob
import serial
import time

def convert(str):
    try:
        val = int(str)
    except ValueError:
        val = 'false'

    return val

def chooseSerialPorts():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    connectionSuccessfull = False
    
    #Loop while we don't have a successfull connection with IMU device
    while connectionSuccessfull == False:
        #Adapt to the plateform we're running on :
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        i = 1
        #List availbles serial ports :
        print '\nHere are the serial ports available :'
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
                print '{} - {}'.format(i,port)
                i+=1
            except (OSError, serial.SerialException):
                pass
          
        serialPort = convert(raw_input('Please enter the number of the one corresponding to the IMU device :\n')) #Ask the user to choose a port
        
        if serialPort != False and serialPort >=1 and serialPort <= i+1 :
            serialPort = result[serialPort-1]
            serialSocket = serial.Serial(port=serialPort, baudrate=9600, timeout=1) #Open a connection on this port
            connectionSuccessfull = True
        else :
            print 'This is not a valid answer.'
    return serialSocket

# Establish a connection :
serialSocket = chooseSerialPorts()
# Ask for the number of blocks stored on EEPROM :
listeEnvois = [ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 123, 77],
                [0, 1, 0, 65, 0, 0, 26, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 123, 77],
                [0, 2, 1, 14, 0, 0, 122, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 123, 77],
                [0, 2, 0, 122, 0, 0, 206, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 123, 77],
                [0, 3, 1, 35, 0, 1, 26, 0, 0, 0 , 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 39, 123, 77]]
                
continueLoop = True
while continueLoop:
    if serialSocket.inWaiting()>0:
        if ord(serialSocket.read(1)) == 123:
            serialSocket.write(chr(124))
            continueLoop = False
continueLoop = True
while continueLoop:
    if serialSocket.inWaiting()>0:
        if ord(serialSocket.read(1)) == 125:
            serialSocket.write(chr(0))
            serialSocket.write(chr(len(listeEnvois)))
            continueLoop = False
for i in range(0, len(listeEnvois)):
    for j in range(0, len(listeEnvois[i])):
        serialSocket.write(chr(listeEnvois[i][j]))
        serialSocket.write(chr(listeEnvois[i][j]))


        