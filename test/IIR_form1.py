# IIR filter class Direct Form 1
class IIR_form1:
    def __init__(self, b0, b1, b2, a1, a2, Q=29):
        self.Q = Q
        self.half = 1 << (Q - 1)
        
        self.b0 = b0
        self.b1 = b1
        self.b2 = b2
        self.a1 = a1
        self.a2 = a2

        self.bufferX1 = 0
        self.bufferX2 = 0
        self.bufferY1 = 0
        self.bufferY2 = 0

    def filter(self, x):
        # This accumulater becomes an integer of order 2 * Q (e.g Q = 32 means acc becomes an int64 etc.)
        accumulator = x * self.b0 + self.bufferX1 * self.b1 + self.bufferX2 * self.b2 - self.bufferY1 * self.a1 - self.bufferY2 * self.a2

        # Scale the output back down to int32 (add half to make this a rounding operation instead of a flooring operation)
        y = (accumulator + self.half) >> self.Q

        self.bufferX2 = self.bufferX1
        self.bufferX1 = x
        self.bufferY2 = self.bufferY1
        self.bufferY1 = y
        return y
