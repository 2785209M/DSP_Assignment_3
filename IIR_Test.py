from IIR_filter_1 import IIR_filter_1 as iir1
import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()

num_samples = len(ecg_signal) # Number of Samples in ECG signal
sample_rate = 250 # Sampling rate of ECG signal (Hz)

fc = 50 # 50Hz Noise
fs = 250.0 # Sampling Frequency
fpython = fc / (fs / 2) # Normalized frequency for Python

Q = 30 # higher quality factor means narrower notch
b, a = signal.iirnotch(fc, Q, fs)
IIR_filter = iir1(b[0], b[1], b[2], a[1], a[2])

filtered_signal = np.zeros(num_samples)
for i in range(num_samples):
    filtered_signal[i] = IIR_filter.filter(ecg_signal[i])

plt.plot(filtered_signal)
plt.show()