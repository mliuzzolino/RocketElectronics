
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1421', 9600)

time.sleep(1)

print ser.name



def Menu():
    data_left = 1

    while (data_left != 0):
        print(ser.readline())

        data_left = ser.inWaiting()
        time.sleep(0.1)




def Data():
    
    data_left = 1

    while (data_left != 0):
        print(ser.readline())
    
        data_left = ser.inWaiting()
        time.sleep(0.1)
    



def main():

    Menu()
    
    while (1):
        
        while (1):

            word = raw_input("> ")
            
            if ((word == "end") or (word == 'exit')) :
                return
            
            elif ((word == "w") or (word == "W")):
                ser.write(word)
                Data()

            elif ((word == "r") or (word == "R")):
                ser.write(word)
                Data()

            elif (word == "m"):
                time.sleep(1)
                ser.write(word)
                Menu()


            
               


         



    #Closes the connection
    ser.close()



if (__name__ == "__main__"):
    main()