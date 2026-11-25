import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2 as iir2
from scipy import signal
from IIR_form2_chain import IIR_form2_chain as iir2_chain

fs = 200
fc = [0.5, 7] 
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sos = signal.butter(2, fpython, btype = 'bandpass', output = 'sos')

print(sos)

bandpassFilterStructures = [
    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos
]

BandPassFilter = iir2_chain(bandpassFilterStructures)

x = BandPassFilter.getImpulseResponse(fs)

y = BandPassFilter.getFrequencyResponse(fs)

plt.figure()
plt.title("impulse response")
plt.plot(x)
plt.show()

plt.figure()
plt.title("frequency response")
plt.plot(y)
plt.show()








