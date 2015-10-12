import sys
import glob
import serial
import time

import handShake as hs
import downloader as dl

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
#import mpl_toolkits.mplot3d.axes3d as p3
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation







def collect_data(serial_socket):
    
    real_time_answer = raw_input("Would you like to plot real-time data? (y/n) ")

    if real_time_answer == 'y':
        real_time_data = 'ON'
    else:
        real_time_data = 'OFF'


    waiting = True
    serial_socket.write(chr(0)) 


    while waiting:
        if serial_socket.inWaiting() > 0:
            incoming=ord(serial_socket.read(1))
            if incoming == 126:
                print 'Connection successfull!'
                waiting = False



    # RT Data
    if real_time_data == 'ON':
 
        mpl.rcParams['legend.fontsize'] = 10
        fig = plt.figure()
        ax = fig.gca(projection='3d')

        ax.set_xlabel('X')
        ax.set_xlim3d([0.0, 200.0])
        ax.set_ylabel('Y')
        ax.set_xlim3d([0.0, 200.0])
        ax.set_zlabel('Z')
        ax.set_xlim3d([0.0, 200.0])
        plt.ion()
        plt.show()
        waiting = True
    
        while waiting:

            while serial_socket.inWaiting() > 0:
                counter = 0
                while counter < 3: 
                    
                    data_value = float(ord(serial_socket.read(1)))
                    print(type(data_value))

                    if counter == 0:
                        x = [data_value]
                        
                    elif counter == 1:
                        y = [data_value]
                        
                    elif counter == 2:
                        z = [data_value]
                        
                    counter += 1
                print(x, y, z)
                ax.plot(x, y, z)
                plt.draw()

                
        
                time.sleep(0.05)


                


    # NO RT Data
    elif real_time_data == 'OFF':
        while True:
            while serial_socket.inWaiting() > 0:
                
                print ord(serial_socket.read(1))

                




        





def download_data(serial_socket):
    
    waiting = True
    serial_socket.write(chr(1)) 

    while waiting:

        if serial_socket.inWaiting() > 0:
            
            incoming=ord(serial_socket.read(1))
            
            if incoming == 127:
                print 'Connection successfull!'
                waiting = False
                
            elif incoming == 128:
                print("Unsuccessful!")
                print("Goodbye!")
                exit()

    choice = raw_input("Would you like to download now? (y/n) ")
    time.sleep(0.2)

    if choice == 'y':
        dl.downloader_main(serial_socket)
    else:
        print("Goodbye!")
        exit();



def main():



    # Handshake
    serial_socket = hs.choose_serial_ports()

    print("Welcome to the rocket program menu!")
    print("\n")
    print("      Menu      ")
    print("----------------")
    print("[c]ollect  data ")
    print("[d]ownload data ")
    print("----------------")
    print("\n")

    mode = raw_input("> ")

    if (mode == 'c'):
        print("Entering collect data mode...")
        collect_data(serial_socket)

    elif (mode == 'd'):
        print("Entering download data mode...")
        download_data(serial_socket)
        


if __name__ == "__main__":
    main()