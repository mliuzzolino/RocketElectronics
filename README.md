# RocketElectronics
# --------------------------------------------------
# Authors:      Guillaume Biton & Michael Iuzzolino
# Organization: University of Arizona
# Project:      Rocket Payload Design
# Dates:        October 1st - December 25th
# --------------------------------------------------

Stage 1:
Utilize Arduino Uno with a simple temperature circuit to gather temperature
data, send it to serial, and use a Python script (using Pyserial) to read from
serial and create real-time plot of temperature vs. time.

This stage will familiarize us with how we can use Python to read serial data, store it as csv format to memory (for later manipulation with Matlab, Excel, etc), and create a real-time plot (using matplotlib.pyplot).


Stage 2:
Create python script to generate test data to store on EEPROM. Then, utilize another python script to recover data from EEPROM, implementing error correction schemes for high fidelity data retrieval, etc.

Stage 3:
