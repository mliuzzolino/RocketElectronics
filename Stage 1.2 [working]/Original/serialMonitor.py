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
while True:
    while serialSocket.inWaiting()>0:
        print ord(serialSocket.read(1))
    response = convert(raw_input('Response :\n'))
    if response != 'false':
       serialSocket.write(chr(response))
    time.sleep(0.2)