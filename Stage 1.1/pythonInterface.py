
import serial
import time
import numpy as np
import matplotlib.pyplot as plt

ser = serial.Serial('/dev/tty.usbmodem1421', 9600, timeout = 5)
ser.flushInput()
ser.flushOutput()
time.sleep(.1)


print ser.name



def Menu():
    data_left = 1

    while (data_left != 0):
        print(ser.readline())
        time.sleep(.1)
        data_left = ser.inWaiting()

    return

def RealTimePlot(y, count, minPlot, maxPlot):


    plt.axis([0, count + 10, minPlot, maxPlot])
    plt.ion()
    plt.show()



    print(y)
    plt.scatter(count, y)
    plt.draw()
    time.sleep(0.05)
    count += 1

    return count;


def WriteData(mode, plotData = 'n'):
    ser.write(mode)
    time.sleep(1)
    maxPlot = 21
    minPlot = 20
    count = -3
    launch = 0
    # Gets data from Serial
    while ser.inWaiting() > 0:
        out = ser.readline()
        print(out)
        time.sleep(0.1)
        launch += 1
        count += 1
        print(launch)
        # Plots data in real time

        if (plotData == 'y') and (launch >= 3):
            x = (float)(out)
            y = (x - 0.5) * 100.0


            if y > maxPlot:
                maxPlot = y + 2
            elif y < minPlot:
                minPlot = y - 2
            count = RealTimePlot(y, count, minPlot, maxPlot)


        elif (plotData == 'n'):
            print("Not doing this")


    return

def ProgramIntro():
    print("Welcome to the program!")
    print("Would you like to plot real-time data? (y/n)")
    plotData = raw_input("> ")
    return plotData

def main():

    launch = 0
    plotData = ProgramIntro()

    time.sleep(1)
    Menu()

    mode = raw_input("> ")

    while (1):


        if ((mode == "end") or (mode == 'exit')) :
            ser.close()
            exit()

        elif (mode == 'm'):
            print("Returning to menu...")
            ser.write(mode)
            time.sleep(1)
            Menu()

        elif (mode == 'w'):
            count = 0
            WriteData(mode, plotData)


        elif (mode == 'r'):

            outputFile = open("./testdata/output.txt", "w")

            ser.write(mode)
            time.sleep(1)
            count = 0
            while ser.inWaiting() > 0:
                out = ser.readline()
                print(out)
                if (count != 0):
                    outputFile.write(str(count))
                    outputFile.write(", ")
                    outputFile.write(out)

                time.sleep(0.1)

                count += 1

            outputFile.close()


        #time.sleep(2)


    print("Goodbye!")


    #Closes the connection
    ser.close()




if (__name__ == "__main__"):
    main()
