import matplotlib.pyplot as plt
import numpy as np
from IIR_form2 import IIR_form2 as iir2
from IIR_form1 import IIR_form1 as iir1
from scipy import signal
from IIR_form2_chain import IIR_form2_chain as iir2_chain
from IIR_form1_chain import IIR_form1_chain as iir1_chain

fs = 200
fc = [0.5, 7] 
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sos = signal.butter(2, fpython, btype = 'bandpass', output = 'sos')

print(sos)

#Just between iir1 to iir2 below and when defining the filter chain to test the responses from either form

bandpassFilterStructures = [
    iir1(row[0], row[1], row[2], row[4], row[5]) for row in sos
]

BandPassFilter = iir1_chain(bandpassFilterStructures)

x, tx = BandPassFilter.getImpulseResponse(fs)

y, fy = BandPassFilter.getFrequencyResponse(fs)

plt.figure()
plt.title("impulse response")
plt.plot(tx, x)
plt.show()

plt.figure()
plt.title("frequency response")
plt.plot(fy, y)
plt.show()








