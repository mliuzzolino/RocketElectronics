"""
    Authors: Guillaume Biton and Michael Iuzzolino
    Organization: University of Arizona
    Date: September - December 2015
"""


import sys
import glob
import serial
import time



def choose_serial_ports():
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    connection_successful = False
    
    #Loop while we don't have a successfull connection with IMU device
    while connection_successful == False:
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
        print ('\nHere are the serial ports available :')
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
            serial_port = int(raw_input('Please enter the number of the one corresponding to the IMU device :\n'))
        except ValueError:
            serial_port = False
        
        if serial_port != False and serial_port >= 1 and serial_port <= i + 1 :
            serial_port = result[serial_port - 1]
            print('Sending identification request on {}'.format(serial_port))
            serial_socket = serial.Serial(port=serial_port, baudrate=9600, timeout=1) #Open a connection on this port
            time.sleep(2)
            serial_socket.write(chr(123))  #Send identification code on this port
            
            #Waiting for an appropriate response from the device :
            waiting = True
            request_time = time.time()
            
            while waiting :
                
                if serial_socket.inWaiting()>0:
                     
                    incoming = ord(serial_socket.read(1))
                    print("Incoming: {}".format(incoming))
                    if incoming == 124:
                        print ('Connection successfull !')
                        connection_successful = True
                        waiting = False
                elif time.time()- request_time > 5:
                    print ('Connection timout : the device is either busy or not an IMU')
                    waiting = False
                    serial_socket.close()
                #time.sleep(0.2)
        else :
            print ('This is not a valid answer.')

    return serial_socket



def hand_shake(serial_socket, python_send, arduino_success, arduino_fail=128, message_success="Connection succesful!", message_fail="Unsuccessful.\nGoodbye!"):

    waiting = True
    request_time = time.time()
    
    serial_socket.write(chr(python_send))

    while waiting:

        if serial_socket.inWaiting() > 0:
            
            incoming=ord(serial_socket.read(1))

            if incoming == arduino_success:
                print (message_success)
                waiting = False

            elif incoming == arduino_fail:
                print(message_fail)
                exit()
                
        # CHECK FOR TIMEOUT
        elif time.time() - request_time > 5:
            print ('Connection timout!!!')
            waiting = False
            serial_socket.close()
        
        








