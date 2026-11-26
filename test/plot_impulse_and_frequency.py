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

floatingPointBandpassFilterStructures = [
   iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos
]

Q = 29
SCALE = 1 << Q

sos_q = np.round(sos * SCALE).astype(np.int64)
fixedPointBandpassFilterStructures = [
    iir1Fixedpoint(int(row[0]), int(row[1]), int(row[2]), int(row[4]), int(row[5]), Q)
    for row in sos_q
]


floatingPointBandPassFilter = iir_chain(floatingPointBandpassFilterStructures)
fixedPointBandPassFilter = iir_chain(fixedPointBandpassFilterStructures)

x, tx = fixedPointBandPassFilter.getImpulseResponse(fs)
y, fy = fixedPointBandPassFilter.getFrequencyResponse(fs)

# 1. Fixed-point group delay (zero-padded FFT for a smoother curve)
N_fft = max(8192, len(x))
freqs = np.fft.rfftfreq(N_fft, d=1.0 / fs)
H_fixed = np.fft.rfft(x, n=N_fft)

phase_unwrapped = np.unwrap(np.angle(H_fixed))
omega = 2 * np.pi * freqs / fs
gd_fixed_ms = (-np.gradient(phase_unwrapped, omega) / fs) * 1000

# 2. Analytical floating-point group delay (sum across SOS biquad sections)
gd_float_samples = np.zeros_like(freqs)
for row in sos:
    b, a = row[:3], row[3:]
    _, gd_sec = signal.group_delay((b, a), w=freqs, fs=fs)
    gd_float_samples += gd_sec
gd_float_ms = (gd_float_samples / fs) * 1000

# 3. Quantify passband drift (0.5–7 Hz)
passband = (freqs >= fc[0]) & (freqs <= fc[1])
max_err_ms = np.max(np.abs(gd_fixed_ms[passband] - gd_float_ms[passband]))
print(f"Max passband group delay difference (Q{Q} vs float): {max_err_ms:.4f} ms")

# 4. Overlay plot
plt.figure(figsize=(9, 4))
plt.plot(freqs, gd_float_ms, label="Floating-point (Analytical SOS)", linewidth=2)
plt.plot(freqs, gd_fixed_ms, "--", label=f"Fixed-point (Q{Q} Impulse FFT)", linewidth=1.5)
plt.axvline(fc[0], color="gray", linestyle=":", label="Cutoffs (0.5, 7 Hz)")
plt.axvline(fc[1], color="gray", linestyle=":")
plt.xlim(0, 15)
plt.ylim(0, 650)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Group Delay (ms)")
plt.title(f"Group Delay Comparison: Float vs. Fixed-Point Q{Q}")
plt.grid(True)
plt.legend()
plt.savefig("Group_delay.svg")

plt.figure()
plt.title("impulse response")
plt.plot(tx, x)
plt.figure()
plt.title("frequency response")
plt.plot(fy, y)
plt.savefig("Impulse_Response.svg")

#plt.show()








