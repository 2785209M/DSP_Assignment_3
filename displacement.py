#!/usr/bin/python3

from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'


class DisplacementIntegrator:
    """
    Estimates dynamic (oscillatory) displacement in cm from normalized
    pyfirmata2 readings using high-pass filtering + leaky double integration.
    """

    def __init__(self, fs=100.0, cutoff_hz=0.3, adc_ref=5.0, sensitivity=0.33):
        self.dt = 1.0 / fs
        # Converts normalized (0-1) reading change directly to m/s^2
        self.scale = (adc_ref / sensitivity) * 9.81

        # First-order high-pass / leak coefficient to prevent runaway drift
        omega_c = 2.0 * np.pi * cutoff_hz
        self.alpha = 1.0 / (1.0 + omega_c * self.dt)

        # Collect 1 second of stationary samples to zero out bias & gravity
        self.cal_samples = []
        self.cal_target = int(fs)
        self.baseline = None

        self.prev_a = 0.0
        self.a_hp = 0.0
        self.vel = 0.0
        self.pos = 0.0

    def process(self, raw_norm):
        if raw_norm is None:
            return None

        if self.baseline is None:
            self.cal_samples.append(raw_norm)
            if len(self.cal_samples) >= self.cal_target:
                self.baseline = float(np.mean(self.cal_samples))
            return 0.0

        # Acceleration relative to resting baseline (m/s^2)
        a = (raw_norm - self.baseline) * self.scale

        # High-pass filter acceleration to strip residual DC offset
        self.a_hp = self.alpha * (self.a_hp + a - self.prev_a)
        self.prev_a = a

        # Leaky double integration: acceleration -> velocity -> displacement
        self.vel = self.alpha * self.vel + self.a_hp * self.dt
        self.pos = self.alpha * self.pos + self.vel * self.dt

        return self.pos * 100.0  # return in centimetres


class RealtimePlotWindow:

    def __init__(self, labels=("X disp (cm)", "Y disp (cm)", "Z disp (cm)")):
        self.num_channels = len(labels)
        self.buffer_size = 500

        self.fig, self.axes = plt.subplots(
            self.num_channels, 1, sharex=True, figsize=(8, 6)
        )
        self.fig.suptitle("ADXL335 Estimated Dynamic Displacement (Hold still 1s to calibrate)")

        colors = ["tab:red", "tab:green", "tab:blue"]
        self.plotbuffers = []
        self.ringbuffers = []
        self.lines = []

        for i, (ax, label) in enumerate(zip(self.axes, labels)):
            buf = np.zeros(self.buffer_size)
            line, = ax.plot(buf, color=colors[i % len(colors)])
            ax.set_ylabel(label)
            ax.set_ylim(-10, 10)  # ±10 cm range; adjust to suit your motion
            ax.grid(True, alpha=0.3)

            self.plotbuffers.append(buf)
            self.ringbuffers.append([])
            self.lines.append(line)

        self.axes[-1].set_xlabel("Samples (100 Hz)")
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])

        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=100, cache_frame_data=False
        )

    def update(self, frame):
        for i in range(self.num_channels):
            new_samples = self.ringbuffers[i]
            self.ringbuffers[i] = []

            if new_samples:
                self.plotbuffers[i] = np.append(self.plotbuffers[i], new_samples)[
                    -self.buffer_size:
                ]
                self.lines[i].set_ydata(self.plotbuffers[i])

        return self.lines

    def addData(self, channel, v):
        if v is not None:
            self.ringbuffers[channel].append(v)


samplingRate = 100

realtimePlotWindow = RealtimePlotWindow()
integrators = [DisplacementIntegrator(fs=samplingRate) for _ in range(3)]


def callBackX(data):
    realtimePlotWindow.addData(0, integrators[0].process(data))


def callBackY(data):
    realtimePlotWindow.addData(1, integrators[1].process(data))


def callBackZ(data):
    realtimePlotWindow.addData(2, integrators[2].process(data))


board = Arduino(PORT)
board.samplingOn(1000 / samplingRate)

board.analog[0].register_callback(callBackX)
board.analog[1].register_callback(callBackY)
board.analog[2].register_callback(callBackZ)

board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()

plt.show()

board.exit()
print("finished")