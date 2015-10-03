
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1421', 9600)

time.sleep(1)

print ser.name

collectingData = 1





def Menu():
    print(ser.readline())

    data_left = ser.inWaiting()

    if (data_left == 0):
        return 0
    else:
        return 1



def Data():
    print(ser.readline())
    time.sleep(1)
    data_left = ser.inWaiting()

    if (data_left == 0):
        return 0
    else:
        return 1


while (1):
    

    while(collectingData == 1):

        collectingData = Menu()
    
    
    word = raw_input('> ')
    if(word == "end"): 
        break;
    elif (word == "1"):
        collectingData = 1
        while(collectingData == 1):
            collectingData = Data()


    ser.write(word)
    collectingData = 1


#Closes the connection
ser.close()



