import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1421', 9600)

filename = "./output.txt"
outputFile = open(filename, "w")

print("connected to: " + ser.portstr)
count = 1

while True:
    line = ser.readline()
    
    print("count: {}, line: {}".format(count, line))
    
    if (int(line) > 50):
        break;

    outputFile.write(line)
    count += 1


# Closes the file
outputFile.close()


# Closes the connection
ser.close()
