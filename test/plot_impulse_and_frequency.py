import matplotlib.pyplot as plt
import numpy as np
from IIR_form2 import IIR_form2 as iir2
from IIR_form1_fixedpoint import IIR_form1_fixedpoint as iir1Fixedpoint
from IIR_form1 import IIR_form1 as iir1
from scipy import signal
from IIR_chain import IIR_chain as iir_chain

fs = 200
fc = [0.5, 7] 
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sos = signal.butter(2, fpython, btype = 'bandpass', output = 'sos')

print(sos)

#need to comments out all below and uncomment the other initialisation of bandpassFilterStructures for floating point forms

Q = 29
SCALE = 1 << Q

sos_q = np.round(sos * SCALE).astype(np.int64)
bandpassFilterStructures = [
    iir1Fixedpoint(int(row[0]), int(row[1]), int(row[2]), int(row[4]), int(row[5]), Q)
    for row in sos_q
]

#bandpassFilterStructures = [
#    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos
#]

BandPassFilter = iir_chain(bandpassFilterStructures)

x, tx = BandPassFilter.getImpulseResponse(fs)

y, fy = BandPassFilter.getFrequencyResponse(fs)

plt.figure()
plt.title("impulse response")
plt.plot(tx, x)

plt.figure()
plt.title("frequency response")
plt.plot(fy, y)
plt.show()








