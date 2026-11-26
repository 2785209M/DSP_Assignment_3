import time
import numpy as np
from scipy import signal
from IIR_form1 import IIR_form1 as iir1
from IIR_form2 import IIR_form2 as iir2
from IIR_form1_fixedpoint import IIR_form1_fixedpoint as iir1Fixedpoint

# 1. Design the filter
fs = 200
fc = [0.5, 7]
fpython = [fc[0] / fs * 2, fc[1] / fs * 2]
sos = signal.butter(2, fpython, btype="bandpass", output="sos")

Q = 29
SCALE = 1 << Q
sos_q = np.round(sos * SCALE).astype(np.int64)

# 2. Pre-generate a large test signal (100,000 samples = 500s of 200 Hz PPG data)
# Convert to Python lists so NumPy indexing overhead doesn't skew per-sample timing
N = 100_000
rng = np.random.default_rng(0)
sig_float_np = rng.random(N)
sig_float = sig_float_np.tolist()
sig_fixed = [int(round(v * SCALE)) for v in sig_float]

# 3. Helper to time any single-sample filter chain
def benchmark_chain(name, make_stages, samples, runs=5):
    times = []
    for _ in range(runs):
        stages = make_stages()
        t0 = time.perf_counter()
        for x in samples:
            val = x
            for f in stages:
                val = f.filter(val)
        t1 = time.perf_counter()
        times.append(t1 - t0)

    best = min(times)
    us_per_sample = (best / len(samples)) * 1e6
    print(f"{name:<26} | {best*1000:7.2f} ms total | {us_per_sample:6.3f} µs/sample")

# 4. Run benchmarks
print(f"Benchmarking {N:,} samples (real-time budget at 200 Hz = {1e6/fs:.0f} µs/sample)\n")

benchmark_chain(
    "IIR Direct Form 1 (float)",
    lambda: [iir1(row[0], row[1], row[2], row[4], row[5]) for row in sos],
    sig_float,
)

benchmark_chain(
    "IIR Direct Form 2 (float)",
    lambda: [iir2(row[0], row[1], row[2], row[4], row[5]) for row in sos],
    sig_float,
)

benchmark_chain(
    f"IIR Direct Form 1 (Q{Q})",
    lambda: [iir1Fixedpoint(int(r[0]), int(r[1]), int(r[2]), int(r[4]), int(r[5]), Q) for r in sos_q],
    sig_fixed,
)

# Optional: SciPy C-implemented reference
t0 = time.perf_counter()
_ = signal.sosfilt(sos, sig_float_np)
t1 = time.perf_counter()
print(f"{'SciPy sosfilt (C array)':<26} | {(t1-t0)*1000:7.2f} ms total | {(t1-t0)/N*1e6:6.3f} µs/sample")