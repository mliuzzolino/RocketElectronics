"""
    Authors: Guillaume Biton and Michael Iuzzolino
    Organization: University of Arizona
    Date: September - December 2015
"""




# This programm download and process data from our IMU device
# By Guillaume Biton at the University of Arizona - October 2015
# Version 1.0

import sys
import glob
import serial
import time


# !!!! The following function is from StackOverflow.com !

# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    bar_length = 20 # Modify this to change the length of the progress bar
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
    block = int(round(bar_length * progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#" * block + "-" * (bar_length-block), progress * 100, status)
    sys.stdout.write(text)
    sys.stdout.flush()
    


def receive_a_byte(serial_socket, timeout=2):
    # receive_a_byte(serial_socket, timeout) : wait for a byte for timeout
    ## As a byte should always come in double, it waits for the second one to come, check if it is the same and, otherwise ask for a third repeat

    received_data = 0;
    request_time = time.time()
    waiting1 = True; waiting2 = True
    incoming1 = 0; incoming2 = 0; incoming3 = 0


    prev_time = 0
    elapsed_time = 0

    while waiting1:

        #We wait to have received 2 bytes
        if serial_socket.inWaiting() > 1:
            incoming1 = ord(serial_socket.read(1))
            incoming2 = ord(serial_socket.read(1))
            
            
            if incoming1 == incoming2: # If both bytes are equals, we go on
                serial_socket.write(chr(100)) # Well received !
                result = incoming1
            else : #Else, we ask for a third repetition
                print("ERROR")
                serial_socket.write(chr(111)) # Ask for a third !
                request_time_2 = time.time()
                while waiting2:
                    if serial_socket.inWaiting() > 0:
                        incoming3 = ord(serial_socket.read(1))
                        if incoming3 == incoming1:
                            result = incoming1
                        elif incoming3 == incoming2:
                            result = incoming2
                        else:
                            print('Transmission error')
                            result = 256 #No well received byte can be at 256
                        waiting1 = False
                        waiting2 = False 

                    #TIMEOUT
                    elif time.time() - request_time_2 > timeout:
                        waiting1 = False
                        waiting2 = False
                        result = 256 #No well received byte can be at 256
                        print('Connection timeout')

            waiting1 = False

        # TIMEOUT
        elif time.time() - request_time > timeout:
            waiting1 = False
            result = 256 #No well received byte can be at 256
            print('Connection timeout')

    return result
      


def receive_a_block(serial_socket):
    result = []
    for i in range(0, 26):
        received = receive_a_byte(serial_socket, 2)
        if received == 256: 
            received = "###"
        result.append(str(received))
    return result



def create_raw_data_file(raw_data):
        raw_file = open('./output/{}RT_flight_data.raw_data'.format(time.strftime("%d-%m_%H-%M-%S", time.gmtime())), 'w')
        for i in range(0, len(raw_data)):
            for j in range(0,len(raw_data[i])):
                raw_file.write(str(raw_data[i][j]))
                if j == len(raw_data[i]) - 1:
                    raw_file.write('\n')
                else:
                    raw_file.write(',')
        raw_file.close()
        print('Raw-data file ready.\nProcessing the data.')



def create_csv_file(raw_data):

        # Create a new file to store the processed data
        processed_file = open('./output/{}flight.csv'.format(time.strftime("%d-%m_%H-%M-%S", time.gmtime())), 'w')
        date = 0

        # create header in file
        
        processed_file.write("ID,TIMESTAMP,x,y,z,X,Y,Z,rx,ry,rz,ALT,CHECK\n")

        
        #Store all the lines in the file, and check that they are consistent
        for i in range(0, len(raw_data)):
            error = False
            

            block_id = int(raw_data[i][0]) * 256 + int(raw_data[i][1])
            date = date + int(raw_data[i][2]) * 256 + int(raw_data[i][3])
            #print(block_id)
            verification_block = int(raw_data[i][24]) * 256 + int(raw_data[i][25])
            #print(verification_block)
            
            if block_id != i:
                print('Error on line {} : block ID inconsistent.\n Please have a look at the raw-data file to figure out the error.'.format(i+1))
                error = True
            if verification_block != 31565:
                print('Error on line {} : verification bytes inconsistent.\n Please have a look at the raw-data file to figure out the error.'.format(i+1))
                error = True
            if error == False:
                for x in range(0, 13):
                    if x == 1 :
                        processed_file.write(str(date))
                    else:
                        processed_file.write(str(int(raw_data[i][x * 2]) * 256 + int(raw_data[i][x * 2 + 1])))
                    if x == 12:
                        processed_file.write('\n')
                    else:
                        processed_file.write(',')
            else:
                raise Exception('Error with the data')
        
        if error == False:
            print('Data Processed!')








# RT data writing

def receive_a_RT_block(serial_socket):
    result = []
    for i in range(0, 21):
        received = ord(serial_socket.read(1))
        result.append(str(received))
    return result



def create_raw_data_file_in_RT(raw_file, raw_data):
        for i in range(0, len(raw_data)):
            raw_file.write(str(raw_data[i]))
            raw_file.write(',')
            
        raw_file.write('\n')
    
    

                    





def downloader_main(serial_socket):
    # CONSTANTS declaration :
    RECORDING_FREQUENCY = 0.1
    BLOCK_SIZE = 25

    communication_error = False
    

    # Establish a connection :
    serial_socket.write(chr(125))

    #Wait for a response :
    waiting = True
    request_time = time.time()
    while waiting :
        if serial_socket.inWaiting() > 1:
            number_of_blocks = ord(serial_socket.read(1)) * 256 + ord(serial_socket.read(1))
            print('There are {} blocks stored on the device (~{} seconds of recording) !'.format(number_of_blocks, number_of_blocks * RECORDING_FREQUENCY))
            waiting = False
        if time.time() - request_time > 15:
            print('Connection timout : Is the device still connected ?')
            waiting = False
            communication_error = True
            serial_socket.close()
        time.sleep(0.2)


    if communication_error == False:
        print('Let\'s download the data')
        raw_data = []
        update_progress(0)
        time.sleep(2)
        #Download all the blocks 1 by 1 :
        for i in range(0, number_of_blocks):
            raw_data.append(receive_a_block(serial_socket))
            update_progress(float(float(i) / float(number_of_blocks)))
        update_progress(1)
        print('All data downloaded from device !')
        print('Generating the raw-data file...')
        

        # Create raw data file
        create_raw_data_file(raw_data)
        
        # Create CSV file
        create_csv_file(raw_data)

        