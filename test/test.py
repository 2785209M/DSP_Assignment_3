import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2 as iir2
from scipy import signal

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()
num_samples = len(ecg_signal)

fs = 250
fc = 30 # 50hz noise
fpython = fc / fs * 2 #Normalised to Nyquist

b, a = signal.butter(2, fpython)
sos = signal.butter(2, fpython, output = 'sos')

print(b)
print(a)
print(sos)

mainsFilter = iir2(b[0], b[1], a[0], a[1], a[2])

filtered_ecg_signal = np.zeros(num_samples)
for i in range(num_samples):
    filtered_ecg_signal[i] = mainsFilter.filter(ecg_signal[i])

plt.figure()
plt.title("unfiltered signal")
plt.plot(ecg_signal[0:500])
plt.savefig("unfilteredtest.svg")

plt.figure()
plt.title("filtered signal")
plt.plot(filtered_ecg_signal[0:500])
plt.savefig("filter_test.svg")



