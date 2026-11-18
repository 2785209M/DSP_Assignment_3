# IIR Filter class for second order filter
class IIR_filter:
    def __init__(self, b0, b1, b2, a1, a2, buffer1=0, buffer2=0):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2
        self.buffer1 = buffer1
        self.buffer2 = buffer2

    def filter(self, x):
        acc_input = x - self.a1 * self.buffer1 - self.a2 * self.buffer2
        acc_output = self.b0 * acc_input + self.b1 * self.buffer1 + self.b2 * self.buffer2
        self.buffer2 = self.buffer1
        self.buffer1 = acc_input
        return acc_output
