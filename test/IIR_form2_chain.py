import numpy as np

class IIR_form2_chain:
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
            f.buffer1 = 0
            f.buffer2 = 0

        #Ensure num_samples is long enough to get good resolution
        num_samples = fs * 10

        #Define the impulse
        impulse = np.zeros(num_samples)
        impulse[0] = 1

        #Create an empty array for the impulse response
        impulseResponse = np.zeros(num_samples)

        #Pass the impulse response through the chain of filters
        for f in self.SecondOrderFilters:
            for i in range(num_samples):
                impulseResponse[i] = f.filter(impulse[i])
                impulse = impulseResponse

        return impulseResponse

    def getFrequencyResponse(self, fs):
        #Get the impulse response
        impulseResponse = self.getImpulseResponse(fs)

        #Take the fourier transform of the impulse response
        frequencyResponse = np.abs(np.fft.fft(impulseResponse))

        return frequencyResponse

