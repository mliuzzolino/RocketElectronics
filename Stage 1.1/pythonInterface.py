
import serial
import time
import numpy as np
import matplotlib.pyplot as plt


global launch
launch = 0

ser = serial.Serial('/dev/tty.usbmodem1421', 9600, timeout = 5)
ser.flushInput()
time.sleep(0.1)
ser.flushOutput()
time.sleep(0.1)


print ("Connected to serial port: {}".format(ser.name))


def Menu():
    data_left = 1

    while (data_left != 0):
        print(ser.readline())
        time.sleep(.1)
        data_left = ser.inWaiting()

    return

def RealTimePlot(y, count, minPlot, maxPlot):

    INTERVAL = 100
    if (count < INTERVAL):
        
        plt.axis([0, count + 10, minPlot, maxPlot])
        plt.ion()
        plt.show()


        plt.scatter(count, y)
        plt.draw()
        time.sleep(0.05)
        count += 1

    else:

        k = count % INTERVAL

        plt.axis([0 + k, count + 10, minPlot, maxPlot])
        plt.ion()
        plt.show()


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
    count = 0
    global launch


    # Gets data from Serial

    if (plotData == 'n') and (launch == 0):
        print("Not plotting real-time data.")

    if launch <= 1:
        while ser.inWaiting() > 0:

            out = ser.readline()
            print(out)
            time.sleep(0.1)
            launch += 1

    else:
        while ser.inWaiting() > 0:


            out = ser.readline()

            time.sleep(0.1)
            launch = 1


            # Plots data in real time
            if (plotData == 'y'):
                x = (float)(out)
                y = (x - 0.5) * 100.0

                print("{}: \t {}".format(count, y))
                if y > maxPlot:
                    maxPlot = y + 2
                elif y < minPlot:
                    minPlot = y - 2


                count = RealTimePlot(y, count, minPlot, maxPlot)



            elif (plotData == 'n'):
                x = (float)(out)
                y = (x - 0.5) * 100.0
                count += 1
                print("{}: \t {}".format(count, y))

    return

def ReadData(mode):
    """
    Need to implement data check here
    """

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

    return


def ProgramIntro():
    print("Welcome to the program!")
    print("Would you like to plot real-time data? (y/n)")
    plotData = raw_input("> ")
    return plotData


def PauseProgram():
    mode = raw_input("")
    return mode


def main():
    global launch

    plotData = ProgramIntro()

    time.sleep(1)
    Menu()

    mode = raw_input("> ")

    while (1):


        if ((mode == "end") or (mode == 'exit')) :
            ser.close()
            exit()

        elif (mode == 'm'):

            ser.write(mode)
            time.sleep(1)
            Menu()
            mode = raw_input("> ")
            if (mode == 'm'):
                print("Already at menu. Would you like to:")
                print("[w]rite")
                print("[r]ead")
                print("[c]lear")

        elif (mode == 'w'):
            count = 0
            WriteData(mode, plotData)
            #mode = PauseProgram()


        elif (mode == 'r'):

            ReadData(mode)
            #mode = PauseProgram()


        elif (mode == 'c'):

            ser.write(mode)
            time.sleep(1)

            while ser.inWaiting() > 0:
                out = ser.readline()
                print(out)
                time.sleep(0.1)

            mode = 'm'



    print("Goodbye!")


    #Closes the connection
    ser.close()




if (__name__ == "__main__"):
    main()
