import numpy as np
from IIR_form1_fixedpoint import IIR_form1_fixedpoint as iirFixedPoint

class IIR_chain:
    def __init__(self, secondOrderFilters):
        self.SecondOrderFilters = secondOrderFilters

    def filter(self, x):
        #Pass the input through the chain of filters
        for f in self.SecondOrderFilters:
            x = f.filter(x)
        return x

    def getImpulseResponse(self, fs):
        #Clear the existing buffers
        for f in self.SecondOrderFilters:
            f.clearBuffers()

        #Ensure num_samples is long enough to get good resolution
        num_samples = fs * 10

        #Define the impulse and impulse response as int if for fixedpoint and float otherwise
        if self.SecondOrderFilters and isinstance(self.SecondOrderFilters[0], iirFixedPoint):
            impulse = np.zeros(num_samples, dtype=np.int64)
            impulse[0] = 1 << self.SecondOrderFilters[0].Q
            impulseResponse = np.zeros(num_samples, dtype=np.int64)
            out_dtype = np.int64
        else:
            impulse = np.zeros(num_samples)
            impulse[0] = 1
            impulseResponse = np.zeros(num_samples)
            out_dtype = np.float64

        #Pass the impulse response through the chain of filters
        for f in self.SecondOrderFilters:
            out = np.zeros(num_samples, dtype=out_dtype)
            for i in range(num_samples):
                out[i] = f.filter(int(impulse[i]) if out_dtype == np.int64 else float(impulse[i]))
            impulse = out

        impulseResponse = impulse

        #Create a time axis to return for plotting
        timeAxis = np.linspace(0, 10, num_samples)

        return impulseResponse, timeAxis

    def getFrequencyResponse(self, fs):
        #Get the impulse response
        impulseResponse, tx = self.getImpulseResponse(fs)

        num_samples = fs * 10

        #Take the fourier transform of the impulse response
        frequencyResponse = np.abs(np.fft.fft(impulseResponse))

        #Create a frequency axis to return for plotting
        frequencyAxis = np.linspace(0, fs, num_samples)

        return frequencyResponse, frequencyAxis

