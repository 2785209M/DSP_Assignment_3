import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2 as iir2
from scipy import signal

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()
num_samples = len(ecg_signal)

fs = 200
fc = [0.5, 7] # 50hz noise
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sos = signal.butter(2, fpython, btype = 'bandpass', output = 'sos')

print(sos)

bandpassFilterStructures = [
    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos
]

x = np.zeros(100)
x[0] = 1
num_samples = len(x)
h = np.zeros(num_samples)
for f in bandpassFilterStructures:
    y = np.zeros(num_samples)
    for i in range(num_samples):
       y[i] = f.filter(x[i])
       x=y

plt.figure()
plt.title("impulse response")
plt.plot(x)
plt.show()

frequencyResponse = np.fft.fft(x)

plt.figure()
plt.title("frequency response")
plt.plot(frequencyResponse)
plt.show()








