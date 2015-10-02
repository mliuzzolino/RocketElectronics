import time
import serial
import numpy as np
import matplotlib.pyplot as plt



# Connect to serial port
ser = serial.Serial('/dev/tty.usbmodem1421', 9600)
print("connected to: " + ser.portstr)

time.sleep(1)


outputFile = open("./outputFile.txt", "w")

count = 0
k = 0
maxPlot = 5
minPlot = 0
prevTemp = None
while True:
    if (ser.readline() == None):
        continue

    line = ser.readline()
    print("ser.readline() = {}".format(line))
    print("line type: {}".format(type(line)))


    if float(line) > maxPlot:
        maxPlot = float(line)
    elif float(line) < minPlot:
        minPlot = float(line)

    # Accounts for very anomolies ruining frame
    errors = 0
    if (prevTemp == None or abs(prevTemp - float(line))) > 10:
        errors += 1
        continue

    # Write to file
    outputFile.write(str(count))
    outputFile.write(", ")
    outputFile.write(line)


    # PLOT

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
