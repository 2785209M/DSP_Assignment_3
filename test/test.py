import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2 as iir2
from scipy import signal

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()
num_samples = len(ecg_signal)

fs = 200
fc = 50 # 50hz noise
fpython = fc / fs * 2 #Normalised to Nyquist

b, a = signal.butter(1, fpython)
sos = signal.butter(1, fpython, output = 'sos')

print(b)
print(a)

mainsFilter = iir2(0.5, 0.5, 1, 0, 0)

filtered_ecg_signal = np.zeros(num_samples)
for i in range(num_samples):
    filtered_ecg_signal[i] = mainsFilter.filter(ecg_signal[i])

plt.figure()
plt.title("unfiltered signal")
plt.plot(ecg_signal[0:1000])
plt.savefig("unfilteredtest.svg")

plt.figure()
plt.title("filtered signal")
plt.plot(filtered_ecg_signal[0:1000])
plt.savefig("filter_test.svg")



