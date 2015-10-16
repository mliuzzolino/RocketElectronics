"""
    Authors: Guillaume Biton and Michael Iuzzolino
    Organization: University of Arizona
    Date: September - December 2015

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
        self.raw_file = open('./output/{}flight.raw_data'.format(time.strftime("%d-%m_%H-%M-%S", time.gmtime())), 'w')
        self.k = 0
        self.t = 0
        self.min_x = -5.0
        self.max_x = 5.0
        self.min_y = -5.0
        self.max_y = 5.0
        self.min_z = 0.0
        self.max_z = 0.0

    # update plot
    def update(self, frame_num, data_lines, lines, ax):
       

        # generate data:
        waiting = True
        input_buffer = []

        while waiting:
            
            if self.ser.inWaiting() > 0:
                
                if len(input_buffer) == 21:
                    converted_data = []

                    # Time stamp
                    time_stamp = input_buffer[0]
                    converted_data.append(time_stamp)

                    # Fine Acceleration
                    x0_fine = input_buffer[1]
                    x1_fine = input_buffer[2]
                    x_fine_coord = x0_fine + x1_fine
                    converted_data.append(x_fine_coord)

                    y0_fine = input_buffer[3]
                    y1_fine = input_buffer[4]
                    y_fine_coord = y0_fine + y1_fine
                    converted_data.append(y_fine_coord)

                    z0_fine = input_buffer[5]
                    z1_fine = input_buffer[6]
                    z_fine_coord = z0_fine + z1_fine
                    converted_data.append(z_fine_coord)

                    # Rough Acceleration
                    X0_rough = input_buffer[7]
                    X1_rough = input_buffer[8]
                    X_rough_coord = X0_rough * 256 + X1_rough
                    converted_data.append(X_rough_coord)

                    Y0_rough = input_buffer[9]
                    Y1_rough = input_buffer[10]
                    Y_rough_coord = Y0_rough * 256 + Y1_rough
                    converted_data.append(Y_rough_coord)

                    Z0_rough = input_buffer[11]
                    Z1_rough = input_buffer[12]
                    Z_rough_coord = Z0_rough * 256 + Z1_rough
                    converted_data.append(Z_rough_coord)

                    # Rotation data
                    rx0_fine = input_buffer[13]
                    rx1_fine = input_buffer[14]
                    rx_fine_coord = rx0_fine * 256 + rx1_fine
                    converted_data.append(rx_fine_coord)

                    ry0_fine = input_buffer[15]
                    ry1_fine = input_buffer[16]
                    ry_fine_coord = ry0_fine * 256 + ry1_fine
                    converted_data.append(ry_fine_coord)

                    rz0_fine = input_buffer[17]
                    rz1_fine = input_buffer[18]
                    rz_fine_coord = rz0_fine * 256 + rz1_fine
                    converted_data.append(rz_fine_coord)

                    # Altitude data
                    alt0 = input_buffer[19]
                    alt1 = input_buffer[20]
                    altitude_data = alt0 * 256 + alt1
                    converted_data.append(altitude_data)

                    
                    # Simulate data for plotting

                    if self.t <= 200:
                        #x_coord = (x_fine_coord + (self.k % 5)) / 1e2
                        #y_coord = (y_fine_coord + (self.k % 6)) / 1e2
                        #z_coord = (z_fine_coord + np.exp(self.k * 0.1)) / 1e2
                        x_coord = self.t * 0.1
                        y_coord = self.t * 0.2
                        z_coord = -self.t**2 + 200*self.t
                        self.t += 1
                    else:
                        x_coord = 0
                        y_coord = 0
                        z_coord = 0

                    print("{}: {},{},{}".format(time_stamp, x_coord, y_coord, z_coord))

                    data_lines[0][0, time_stamp] = float(x_coord)
                    data_lines[0][1, time_stamp] = float(y_coord)
                    data_lines[0][2, time_stamp] = float(z_coord)

                    if x_coord > self.max_x:
                        self.max_x = x_coord + 10.0

                    if y_coord > self.max_y:
                        self.max_y = y_coord + 10.0

                    if z_coord > self.max_z: 
                        self.max_z = z_coord + 10.0

                    if x_coord < self.min_x:
                        self.min_x = x_coord - 10.0

                    if y_coord < self.min_y:
                        self.min_y = y_coord - 10.0

            



                    #ax.set_xlim3d([-5.0, 5.0])
                    
                    #ax.set_ylim3d([-5.0, 5.0])
                    ax.set_xlim3d([self.min_x, self.max_x])
                    ax.set_ylim3d([self.min_y, self.max_y])
                    ax.set_zlim3d([0, self.max_z])

                    waiting = False



                    # Write to data file
                    dl.create_raw_data_file_in_RT(self.raw_file, converted_data)

                    

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
        ax.set_xlim3d([-5.0, 5.0])
        ax.set_xlabel('X')
        ax.set_ylim3d([-5.0, 5.0])
        ax.set_ylabel('Y')
        ax.set_zlim3d([0.0, 250.0])
        ax.set_zlabel('Z')

        frame_num = 2500

        data_lines = [np.empty((3, frame_num))]
        
        lines = [ax.plot([0], [0], [0])[0]]
        

        anim = animation.FuncAnimation(fig, analog_plot.update, frame_num, fargs=(data_lines, lines, ax), interval=50, blit=False)

        
        
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



