import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
from heartrate_monitor import Heartrate_Monitor 
from IIR_form2 import IIR_form2 as iir2
from IIR_chain import IIR_chain as iir_chain

csv = np.loadtxt("ppg_template.csv", delimiter=",")
ppg_signal = csv.copy()
num_samples = len(ppg_signal)

fs = 200
fc = 2
fpython = fc / fs * 2 #Normalised to Nyquist

sos = signal.butter(2, fpython, btype = 'lowpass', output = 'sos')

print(sos)

lowpassFilterStructures = [
    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos
]

LowPassFilter = iir_chain(lowpassFilterStructures)

filteredPpgSignal = np.zeros(num_samples)

for i in range(num_samples):
    filteredPpgSignal[i] = LowPassFilter.filter(ppg_signal[i])

plt.figure()
plt.title("ppg low pass filtered")
plt.plot(filteredPpgSignal)
plt.show()

monitor = Heartrate_Monitor(fs)

currentHeartrate = 0

for i in range(num_samples):
    heartrate = monitor.getHeartrate(filteredPpgSignal[i])
    if heartrate != currentHeartrate:
        print(heartrate)
        currentHeartrate = heartrate

