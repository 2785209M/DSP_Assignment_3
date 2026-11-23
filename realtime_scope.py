#!/usr/bin/python3
from pyfirmata2 import Arduino
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channel 0.
# You can plot multiple chnannels just by instantiating
# more RealtimePlotWindow instances and registering
# callbacks from the other channels.
# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'


class RealtimePlotWindow:

    def __init__(self, labels=("X-axis (A0)", "Y-axis (A1)", "Z-axis (A2)")):
        self.num_channels = len(labels)
        self.buffer_size = 500

        # Create one window with 3 stacked subplots sharing the same x-axis
        self.fig, self.axes = plt.subplots(
            self.num_channels, 1, sharex=True, figsize=(8, 6)
        )
        self.fig.suptitle("ADXL335 Realtime Accelerometer")

        colors = ["tab:red", "tab:green", "tab:blue"]
        self.plotbuffers = []
        self.ringbuffers = []
        self.lines = []

        for i, (ax, label) in enumerate(zip(self.axes, labels)):
            buf = np.zeros(self.buffer_size)
            line, = ax.plot(buf, color=colors[i % len(colors)])
            ax.set_ylabel(label)
            # Normalized 0.0 - 1.0 (tighten to 0.15, 0.55 to zoom in on ±1g tilts)
            ax.set_ylim(0, 1.0)
            ax.grid(True, alpha=0.3)

            self.plotbuffers.append(buf)
            self.ringbuffers.append([])
            self.lines.append(line)

        self.axes[-1].set_xlabel("Samples")
        self.fig.tight_layout(rect=[0, 0, 1, 0.95])

        # A single animation updates all three subplots together
        self.ani = animation.FuncAnimation(
            self.fig, self.update, interval=100, cache_frame_data=False
        )

    def update(self, frame):
        for i in range(self.num_channels):
            # Detach the current ringbuffer before clearing so new samples aren't dropped
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


# Single window managing channel 0 (X), channel 1 (Y), and channel 2 (Z)
realtimePlotWindow = RealtimePlotWindow()

# Sampling rate: 100 Hz
samplingRate = 100


def callBackX(data):
    realtimePlotWindow.addData(0, data)


def callBackY(data):
    realtimePlotWindow.addData(1, data)


def callBackZ(data):
    realtimePlotWindow.addData(2, data)


# Connect to the Arduino board
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register callbacks for A0 (X), A1 (Y), and A2 (Z)
board.analog[0].register_callback(callBackX)
board.analog[1].register_callback(callBackY)
board.analog[2].register_callback(callBackZ)

# Enable reporting on all three channels
board.analog[0].enable_reporting()
board.analog[1].enable_reporting()
board.analog[2].enable_reporting()

# Show the combined plot window and start the animation
plt.show()

# Close the serial port cleanly when the window is closed
board.exit()

print("finished")