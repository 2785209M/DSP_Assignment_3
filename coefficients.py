from scipy import signal
import numpy as np
import matplotlib.pyplot as plt

fs = 1000
fc = 5 #? random for testing, this needs to be frequency of hand tremor
fpython = fc / fs * 2 #Normalised to Nyquist

#How the hell I know what order I want my filter to be? slope steepness?

b, a = signal.butter(4, fpython)
sos = signal.butter(4, fpython, output = 'sos')

print(sos)