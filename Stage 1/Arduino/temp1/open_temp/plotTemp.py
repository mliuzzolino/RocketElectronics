import matplotlib.pyplot as plt
import numpy as np


inputFile = open("./output.txt", "r")

t = 0
temp = []
time = []

for line in inputFile:
    temp.append(line)
    time.append(t)
    t  += 1


plt.plot(time, temp)
plt.axis([0, 140, 35, 45])
plt.show()

inputFile.close()