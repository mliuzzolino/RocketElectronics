# This programm download and process data from our IMU device
# By Guillaume Biton at the University of Arizona - October 2015
# Version 1.0

import sys
import glob
import serial
import time


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
        
        try:
            serialPort = int(raw_input('Please enter the number of the one corresponding to the IMU device :\n'))
        except ValueError:
            serialPort = False
        
        if serialPort != False and serialPort >=1 and serialPort <= i+1 :
            serialPort = result[serialPort-1]
            print('Sending identification request on {}'.format(serialPort))
            serialSocket = serial.Serial(port=serialPort, baudrate=9600, timeout=1) #Open a connection on this port
            time.sleep(2)
            serialSocket.write(chr(123))  #Send identification code on this port
            
            #Waiting for an appropriate response from the device :
            waiting = True
            requestTime = time.time()
            
            while waiting :

                if serialSocket.inWaiting()>0:
                    
                    incoming=ord(serialSocket.read(1))
                    
                    
                    if incoming == 124:
                        print 'Connection successfull !'
                        connectionSuccessfull = True
                        waiting = False
                elif time.time()- requestTime > 5:
                    print 'Connection timout : the device is either busy or not an IMU'
                    waiting = False
                    serialSocket.close()
                time.sleep(0.2)
        else :
            print 'This is not a valid answer.'
    return serialSocket
    
    
# !!!! The following function is from StackOverflow.com !

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    
def receiveAByte(serialSocket, timeout=2):
    # receiveAByte(serialSocket, timeout) : wait for a byte for timeout
    ## As a byte should always come in double, it waits for the second one to come, check if it is the same and, otherwise ask for a third repeat

    receivedData = 0;
    requestTime = time.time()
    waiting1 = True; waiting2 = True
    incoming1 = 0;incoming2 = 0;incoming3 = 0
    while waiting1 :
        #We wait to have received 2 bytes
        if serialSocket.inWaiting()>1:
            incoming1=ord(serialSocket.read(1))
            incoming2=ord(serialSocket.read(1))
            if incoming1 == incoming2: # If both bytes are equals, we go on
                serialSocket.write(chr(100)) # Well received !
                result = incoming1
            else : #Else, we ask for a third repetition
                serialSocket.write(chr(111)) # Ask for a third !
                requestTime2 = time.time()
                while waiting2:
                    if serialSocket.inWaiting()>0:
                        incoming3=ord(serialSocket.read(1))
                        if incoming3 == incoming1:
                            result = incoming1
                        elif incoming3 == incoming2:
                            result = incoming2
                        else:
                            print('Transmission error')
                            result = 256 #No well received byte can be at 256
                        waiting2 = False;waiting1 = False
                    elif time.time() - requestTime2 > timeout:
                        waiting2 = False;waiting1 = False
                        result = 256 #No well received byte can be at 256
                        print('Connexion timeout')
            waiting1 = False
        elif time.time() - requestTime > timeout:
            waiting1 = False
            result = 256 #No well received byte can be at 256
            print('Connexion timeout')
    return result
            
def receiveABlock(serialSocket):
    result = []
    for i in range(0, 26):
        received = receiveAByte(serialSocket,2)
        if received == 256 : received = "###"
        result.append(str(received))
    return result



# CONSTANTS declaration :
RECORDING_FREQUENCY = 0.1
BLOCK_SIZE = 25

communicationError = False
# Establish a connection :
serialSocket = chooseSerialPorts()
# Ask for the number of blocks stored on EEPROM :

serialSocket.write(chr(125))

#Wait for a response :
waiting = True
requestTime = time.time()
while waiting :
    if serialSocket.inWaiting()>1:
        numberOfBlocks=ord(serialSocket.read(1))*256 + ord(serialSocket.read(1))
        print ('There are {} blocks stored on the device (~{} seconds of recording) !'.format(numberOfBlocks, numberOfBlocks*RECORDING_FREQUENCY))
        waiting = False
    if time.time()- requestTime > 15:
        print 'Connection timout : is the device still plugged ?'
        waiting = False
        communicationError = True
        serialSocket.close()
    time.sleep(0.2)

if communicationError==False :
    print 'Let\'s download the data'
    rawData = []
    update_progress(0)
    #Download all the blocks 1 by 1 :
    for i in range(0, numberOfBlocks):
        rawData.append(receiveABlock(serialSocket))
        update_progress(float(float(i)/float(numberOfBlocks)))
    update_progress(1)
    print('All data downloaded from device !')
    print('Generating the raw-data file...')
    # Create a new file to store the raw data
    rawFile = open('./output/{}flight.rawdata'.format(time.strftime("%d-%m_%H-%M-%S", time.gmtime())), 'w')
    for i in range(0, len(rawData)):
        for j in range(0,len(rawData[i])):
            rawFile.write(str(rawData[i][j]))
            if j == len(rawData[i])-1:
                rawFile.write('\n')
            else :
                rawFile.write(',')
    rawFile.close()
    print('Raw-data file ready.\nProcessing the data.')
    # Create a new file to store the processed data
    processedFile = open('./output/{}flight.csv'.format(time.strftime("%d-%m_%H-%M-%S", time.gmtime())), 'w')
    date = 0
    #Store all the lines in the file, and check that they are consistent
    for i in range(0, len(rawData)):
        error = False
        blockID = int(rawData[i][0])*256 + int(rawData[i][1])
        date = date + int(rawData[i][2])*256 + int(rawData[i][3])
        print(blockID)
        verificationBlock = int(rawData[i][24])*256 + int(rawData[i][25])
        print(verificationBlock)
        
        if blockID != i:
            print('Error on line {} : block ID inconsistent.\n Please have a look at the raw-data file to figure out the error.'.format(i+1))
            error = True
        if verificationBlock != 31565:
            print('Error on line {} : verification bytes inconsistent.\n Please have a look at the raw-data file to figure out the error.'.format(i+1))
            error = True
        if error == False:
            for x in range(0,13):
                if x == 1 :
                    processedFile.write(str(date))
                else:
                    processedFile.write(str(int(rawData[i][x*2])*256+int(rawData[i][x*2+1])))
                if x == 12:
                    processedFile.write('\n')
                else:
                    processedFile.write(',')
        else:
            raise Exception('Error with the data')



