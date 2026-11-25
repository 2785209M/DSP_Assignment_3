import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from heartrate_monitor import Heartrate_Monitor 

csv = np.loadtxt("ppg_template.csv", delimiter=",")
ppg_signal = csv.copy()
num_samples = len(ppg_signal)
fs = 200

monitor = Heartrate_Monitor(fs)

currentHeartrate = 0

for i in range(num_samples):
    heartrate = monitor.getHeartrate(ppg_signal[i])
    if heartrate != currentHeartrate:
        print(heartrate)
        currentHeartrate = heartrate




