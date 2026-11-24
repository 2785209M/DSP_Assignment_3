import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2 as iir2
from scipy import signal

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()
num_samples = len(ecg_signal)

fs = 250
fc = [48, 52] # 50hz noise
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sos = signal.butter(4, fpython, btype = 'bandstop', output = 'sos')

#print(b)
print(sos)

mainsFilter = iir2(sos[0][0], sos[0][1], sos[0][2], sos[0][4], sos[0][5])
mainsFilter2 = iir2(sos[1][0], sos[1][1], sos[1][2], sos[1][4], sos[1][5])
mainsFilter3 = iir2(sos[2][0], sos[2][1], sos[2][2], sos[2][4], sos[2][5])
mainsFilter4 = iir2(sos[3][0], sos[3][1], sos[3][2], sos[3][4], sos[3][5])

filtered_ecg_signal = np.zeros(num_samples)
for i in range(num_samples):
    filtered_ecg_signal[i] = mainsFilter.filter(ecg_signal[i])
    filtered_ecg_signal[i] = mainsFilter2.filter(filtered_ecg_signal[i])
    filtered_ecg_signal[i] = mainsFilter3.filter(filtered_ecg_signal[i])
    filtered_ecg_signal[i] = mainsFilter4.filter(filtered_ecg_signal[i])

plt.figure()
plt.title("unfiltered signal")
plt.plot(ecg_signal)
plt.savefig("unfilteredtest.svg")

plt.figure()
plt.title("filtered signal")
plt.plot(filtered_ecg_signal)
plt.savefig("filter_test.svg")



