"""

    Author: Michael Iuzzolino
    Organization: University of Arizona
    Date: October 11th, 2015

Notes:
Possible mechanism for breaking out of data collect...

            try:   
                # Stuff
            except KeyboardInterrupt:
                print('exiting from keyboard interrupt!')


Good references on 3D plotting:

    1)  http://stackoverflow.com/questions/16037494/python-code-is-it-comma-operator

    2)  https://fossies.org/dox/matplotlib-1.4.3/art3d_8py_source.html

"""


import sys, serial, glob, time, argparse

import handShake as hs
import downloader as dl

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation


from collections import deque




# plot class
class AnalogPlot:
    # constr
    def __init__(self, serial_socket):
        # open serial port
        self.ser = serial_socket


    # update plot
    def update(self, frame_num, data_lines, lines):
        
        # generate data:
        waiting = True
        input_buffer = []

        while waiting:
            
            if self.ser.inWaiting() > 0:
                
                if len(input_buffer) == 4:
                    
                    time_stamp = input_buffer[0]
                    x_coord = input_buffer[1] * 1.1
                    y_coord = input_buffer[2] * 1.2
                    z_coord = input_buffer[3] * np.exp(time_stamp * 0.01)

                    data_lines[0][0, time_stamp] = float(x_coord)
                    data_lines[0][1, time_stamp] = float(y_coord)
                    data_lines[0][2, time_stamp] = float(z_coord)

                    waiting = False

                else:
                    input_buffer.append(ord(self.ser.read(1)))
                    
            
        # return it
    
        for line, data in zip(lines, data_lines):
            
        
            # NOTE: there is no .set_data() for 3 dim data...
            line.set_data(data[0:2, :time_stamp])
            
            line.set_3d_properties(data[2,:time_stamp])
            return lines


    # clean up
    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()  




def real_time_data_prompt(serial_socket):

    real_time_answer = raw_input("Would you like to plot real-time data? (y/n) ")
    

    if real_time_answer == 'y':
        real_time_data = 'ON'
        

        # Handshake with arduino to ensure RT data engaged
        python_send = 244
        arduino_success = 11
        arduino_fail = 13
        message_success = "RT Data Enabled!"
        message_fail = "!!!RT Data failed to enable!!!"

        hs.hand_shake(serial_socket, python_send, arduino_success, arduino_fail, message_success, message_fail)


    else:
        real_time_data = 'OFF'

        # Handshake with arduino to ensure RT data engaged
        python_send = 245
        arduino_success = 12
        arduino_fail = 13
        message_success = "RT Data Disabled!"
        message_fail = "!!!RT Data failed to disable!!!"

        hs.hand_shake(serial_socket, python_send, arduino_success, arduino_fail, message_success, message_fail)

    # HANDSHAKE COMPLETE

    return real_time_data




def collect_data(serial_socket):
    

    # Handshake with device for mode change
    python_send = 0
    arduino_success = 126
    arduino_fail = 128

    hs.hand_shake(serial_socket, python_send, arduino_success, arduino_fail)
    # HANDSHAKE complete


    real_time_data = real_time_data_prompt(serial_socket)

    print("Plotting data now...")

    # RT Data
    if real_time_data == 'ON':
        
        # Instantiate plot
        analog_plot = AnalogPlot(serial_socket)

        
        # set up animation
        # Attaching 3D axis to the figure
        fig = plt.figure()
        ax = p3.Axes3D(fig)
        
        ax.set_title('3D Test')
        ax.set_xlim3d([30.0, 60.0])
        ax.set_xlabel('X')
        ax.set_ylim3d([30.0, 60.0])
        ax.set_ylabel('Y')
        ax.set_zlim3d([0.0, 250.0])
        ax.set_zlabel('Z')

        frame_num = 2500

        data_lines = [np.empty((3, frame_num))]
        
        lines = [ax.plot([0], [0], [0])[0]]
        
        anim = animation.FuncAnimation(fig, analog_plot.update, frame_num, fargs=(data_lines, lines), interval=50, blit=False)

        
        # show plot
        plt.show()

        # clean up
        analog_plot.close()

        print('exiting.')

                

    # NO RT Data
    elif real_time_data == 'OFF':
        while True:
            while serial_socket.inWaiting() > 0:
                  
                print ord(serial_socket.read(1))
            
        




def download_data(serial_socket):
    

    # Handshake with device for mode change
    python_send = 1
    arduino_success = 127
    arduino_fail = 128

    hs.hand_shake(serial_socket, python_send, arduino_success, arduino_fail)

    # HANDSHAKE COMPLETE


    choice = raw_input("Would you like to download now? (y/n) ")
    time.sleep(0.2)

    if choice == 'y':
        dl.downloader_main(serial_socket)
    else:
        print("Goodbye!")
        exit();



def print_menu(delay=0):
    
    print("\n")
    time.sleep(delay)
    print("\t=======================")
    time.sleep(delay)
    print("\t|        Menu         |")
    time.sleep(delay)
    print("\t|---------------------|")
    time.sleep(delay)
    print("\t|  [c]ollect  data    |")
    time.sleep(delay)
    print("\t|  [d]ownload data    |")
    time.sleep(delay)
    print("\t|                     |")
    time.sleep(delay)
    print("\t=======================")
    print("\n")




def main():

    # Initial With Device Handshake
    serial_socket = hs.choose_serial_ports()

    # Welcome message
    print("\n\nWelcome to the rocket program!")

    # Print Menu
    print_menu()
    
    while True:
       
        # Get mode from user
        mode = raw_input("> ")

        # Mode 'c': Collect Data
        if (mode == 'c'):
            print("\tEntering collect data mode...")
            collect_data(serial_socket)
        # Mode 'd': Download Data
        elif (mode == 'd'):
            print("\tEntering download data mode...")
            download_data(serial_socket)
        else:
            print("\tIncorrect entry. Try again!")
            time.sleep(0.5)
            print_menu(0.1)
    

        


if __name__ == "__main__":
    main()



