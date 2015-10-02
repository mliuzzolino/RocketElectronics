import time
import serial
import numpy as np
import matplotlib.pyplot as plt



# Connect to serial port
ser = serial.Serial('/dev/tty.usbmodem1421', 9600)
print("connected to: " + ser.portstr)

time.sleep(1)

# 
outputFile = open("./data/outputFile.txt", "w")

count = 0
k = 0

line = ser.readline()
maxPlot = 21
minPlot = 20


prevTemp = None
while True:
    if (ser.readline() == None):
        continue

    # Gets value from serial
    line = ser.readline()
    print("ser.readline() = {}".format(line))
    print("line type: {}".format(type(line)))

    # Dynamically adjusts the max and min plot values
    if float(line) > maxPlot:
        maxPlot = float(line) + 2
    elif float(line) < minPlot:
        minPlot = float(line) - 2

    # Accounts for very large anomolies destroying resolution of plot
    errors = 0
    if (prevTemp == None or abs(prevTemp - float(line))) > 10:
        errors += 1
        continue

    # Write to file
    outputFile.write(str(count))
    outputFile.write(", ")
    outputFile.write(line)


    # Real-time Data plot

    if (count < 100):
        plt.axis([0, count + 10, minPlot, maxPlot])
        plt.ion()
        plt.show()

        y = line
        plt.scatter(count, y)
        plt.draw()
        time.sleep(0.05)

        count += 1
        prevTemp = float(line)
    else:
        plt.axis([0 + k, count + 10, minPlot, maxPlot])
        plt.ion()
        plt.show()

        y = line
        plt.scatter(count, y)
        plt.draw()
        time.sleep(0.05)

        k += 1
        count += 1
        prevTemp = float(line)



# Close serial port
ser.close()

# Close file
outputFile.close()
