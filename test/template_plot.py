import matplotlib.pyplot as plt
import numpy as np
from test.IIR_form2 import IIR_filter_2 as iir2
from scipy import signal

csv = np.loadtxt("ppg_template.csv", delimiter=",")
ppg_signal = csv.copy()
num_samples = len(ppg_signal)

plt.figure()
plt.title("filtered ppg signal")
#plt.ylim(-0.1, 0.1)
plt.plot(ppg_signal[360:460])
plt.savefig("filtered_ppg.svg")

