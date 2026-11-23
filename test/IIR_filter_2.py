# IIR Filter class Direct form 2
class IIR_filter_2:
    def __init__(self, b0, b1, b2, a1, a2):
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2
        self.buffer1 = 0
        self.buffer2 = 0

    def filter(self, x):
        acc_input = x - self.a1 * self.buffer1 - self.a2 * self.buffer2
        acc_output = self.b0 * acc_input + self.b1 * self.buffer1 + self.b2 * self.buffer2
        self.buffer2 = self.buffer1
        self.buffer1 = acc_input
        return acc_output
