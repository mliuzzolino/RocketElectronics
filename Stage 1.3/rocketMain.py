import sys
import glob
import serial
import time

import handShake as hs
import downloader as dl

import numpy as np
import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d.axes3d as p3
import matplotlib.animation as animation






def update_lines(t, line_data, lines, serial_socket) :
    counter = 0
    waiting = True
    print("Here!")
    print("time: {}".format(t))
    while waiting:
        while counter < 4: 
            
            while serial_socket.inWaiting() > 0:
                print("conter {}".format(counter))
                print("time {}".format(t))
                data_value = ord(serial_socket.read(1))

                if counter == 4:
                    break

                elif counter == 0:
                    line_data[counter, t] = data_value
                    
                elif counter == 1:
                    line_data[counter, t] = data_value
                    
                elif counter == 2:
                    line_data[counter, t] = data_value
                

                
                counter += 1

        if counter == 4:
            waiting = False



    print("time: {}".format(t))
    print("Line data: {}".format(line_data))



    for line, data in zip(lines, line_data) :
        line.set_3d_properties(data[2, :t])
        
    return lines



def collect_data(serial_socket):
    

    # Handshake with device for mode change
    python_send = 0
    arduino_success = 126
    arduino_fail = 128

    hs.hand_shake(serial_socket, python_send, arduino_success, arduino_fail)
    
  
    # HANDSHAKE complete



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

        # HANDSHAKE COMPLETE




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



    # RT Data
    if real_time_data == 'ON':
        
        # Attaching 3D axis to the figure
        fig = plt.figure()
        ax = p3.Axes3D(fig)

        # Setting the axes properties
        ax.set_xlim3d([0.0, 30.0])
        ax.set_xlabel('X')

        ax.set_ylim3d([0.0, 30.0])
        ax.set_ylabel('Y')

        ax.set_zlim3d([0.0, 30.0])
        ax.set_zlabel('Z')

        ax.set_title('3D Test')


        # instantiating accel and time lists
        length = 20
        counter = 0
    

        line_data = np.empty((3, length))
        
        lines = [ax.plot(line_data[0, 0:1], line_data[1, 0:1], line_data[2, 0:1])][0]
        

       
        # Creating the Animation object
        line_ani = animation.FuncAnimation(fig, update_lines, length, fargs=(line_data, lines, serial_socket), blit=False)
        
        plt.show()


                


    # NO RT Data
    elif real_time_data == 'OFF':
        while True:
            while serial_socket.inWaiting() > 0:
                
                print ord(serial_socket.read(1))

                #time.sleep(0.2)




        





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



