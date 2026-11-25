import numpy as np
import matplotlib.pyplot as plt

# First Order IIR Filter
class IIR_Filter:
    def __init__(self,_b,_a):
        self.a = _a
        self.b = _b
        self.buffer = 0

    def filter(self, x):
        y = x * self.b - self.buffer*self.a
        self.buffer = y
        return y

f = 0.1
q = 10
si = complex(-np.pi * f / q, np.pi * f * np.sqrt(4 - (1 / (q**2))))

# coeffs
b1 = np.conj(si) / (np.conj(si)-si)
a1 = -np.exp(np.conj(si))

b2 = si / (np.conj(si)-si)
a2 = -np.exp(si)

f1 = IIR_Filter(b1, a1)
f2 = IIR_Filter(b2, a2)

x = np.zeros(100)
x[10] = 1
y1 = np.zeros(100, dtype=complex)
y2 = np.zeros(100, dtype=complex)

for i in range(len(x)):
    y1[i] = f1.filter(x[i])
    y2[i] = f2.filter(x[i])

y = y1 - y2

y = np.real(y)


plt.plot(y)
plt.show()