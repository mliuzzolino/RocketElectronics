import sys
import glob
import serial
import time

import handShake as hs
import downloader as dl


def collect_data(serial_socket):
    print("Entering collect data mode...")
    
    waiting = True
    serial_socket.write(chr(0)) 


    while waiting:
        if serial_socket.inWaiting() > 0:
            incoming=ord(serial_socket.read(1))
            if incoming == 126:
                print 'Connection successfull!'
                waiting = False

    while True:
        while serial_socket.inWaiting() > 0:
            print ord(serial_socket.read(1))
        
        time.sleep(0.2)




def download_data(serial_socket):
    print("Entering download data mode...")
    
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
        collect_data(serial_socket)

    elif (mode == 'd'):
        download_data(serial_socket)
        


if __name__ == "__main__":
    main()