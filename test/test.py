import matplotlib.pyplot as plt
import numpy as np
from IIR_filter_2 import IIR_filter_2
from scipy import signal

tsv = np.loadtxt("James_ecg_1.tsv", delimiter="\t")
ecg_signal = tsv[:, 8].copy()


