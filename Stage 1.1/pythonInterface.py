
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1421', 9600, timeout = 2)



print ser.name



def Menu():
    data_left = 1

    while (data_left != 0):

        print(ser.readline())

        data_left = ser.inWaiting()
        time.sleep(.1)




def Data():
    
    data_left = 1
   

    while (data_left != 0):
        word = raw_input("")
        print(ser.read())
    
        data_left = ser.inWaiting()
        
        if ((word == "m") or (word == "M")):
            ser.write(word)
            return

    return


def main():

    Menu()
    
    time.sleep(1)

    while (1):
        
        while (1):

            word = raw_input("> ")
            
            if ((word == "end") or (word == 'exit')) :
                return

            elif (word == "m"):
                time.sleep(2)
                ser.write(word)
                Menu()

            
            
            elif ((word == "w") or (word == "W")):
                ser.write(word)
                time.sleep(2)
                
                Data()
            

            """
            elif ((word == "r") or (word == "R")):
                ser.write(word)
                time.sleep(0.1)
                
                Data()
            """

        


    #Closes the connection
    ser.close()



if (__name__ == "__main__"):
    main()