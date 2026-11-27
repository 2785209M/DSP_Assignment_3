#!/usr/bin/python3

from pyfirmata2 import Arduino, STRING_DATA, util
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy import signal
from test.IIR_form2 import IIR_form2 as iir2
from test.IIR_chain import IIR_chain as iir_chain
from test.heartrate_monitor import Heartrate_Monitor
import time

# Realtime oscilloscope at a sampling rate of 100Hz
# It displays analog channel 0.
# You can plot multiple chnannels just by instantiating
# more RealtimePlotWindow instances and registering
# callbacks from the other channels.
# Copyright (c) 2018-2020, Bernd Porr <mail@berndporr.me.uk>
# see LICENSE file.

PORT = Arduino.AUTODETECT
# PORT = '/dev/ttyUSB0'

# Creates a scrolling data display
class RealtimePlotWindow:

    def __init__(self, ax, axisLimits, title="Signal", hasBPM = False):
        self.lcd_counter = 0
        # create a plot window
        self.ax = ax
        # that's our plotbuffer
        self.plotbuffer = np.zeros(500)
        # create an empty line
        self.line, = self.ax.plot(self.plotbuffer)
        # axis
        self.ax.set_ylim(axisLimits[0], axisLimits[1])
        self.base_title = title
        # initialize bpm to 0
        self.current_bpm = 0
        self.hasBPM = hasBPM
        # That's our ringbuffer which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []
        # add any initialisation code here (filters etc)

    # updates the plot
    def update(self):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []
        # set the new 500 points of channel 9
        self.line.set_ydata(self.plotbuffer)

        # Update the title on the GUI thread
        if(self.hasBPM):
            bpm_text = f"{self.current_bpm} BPM" if self.current_bpm > 0 else "-- BPM"
            self.ax.set_title(f"{self.base_title} | {bpm_text}")

            # self.lcd_counter += 1
            # if self.lcd_counter >= 5:
            #     self.lcd_counter = 0
            #     try:
            #         row0 = f"0HR: {bpm_text:<12}"[:17]
            #         board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(row0))

            #         recent = self.plotbuffer[-225::14][:16]
            #         levels = np.clip(((recent + 0.1) / 0.2) * 7, 0, 7).astype(int)
            #         row1 = "1" + "".join(str(l) for l in levels)
            #         board.send_sysex(STRING_DATA, util.str_to_two_byte_iter(row1))
            #     except Exception as e:
            #         print("LCD update error:", e)
        else:
            self.ax.set_title(f"{self.base_title}")
        return self.line

    def setBpm(self, bpm):
        self.current_bpm = bpm

    # appends data to the ringbuffer
    def addData(self, v):
        self.ringbuffer.append(v)

    # saves the last n_samples (default 150 = 0.75s at 200Hz) from plotbuffer
    def saveSegment(self, n_samples=500, filename="ppg_template.npy"):
        # Flush any pending ringbuffer samples first so we have the newest data
        if self.ringbuffer:
            self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)[-500:]
            self.ringbuffer = []
        segment = self.plotbuffer[-n_samples:].copy()
        np.save(filename, segment)
        np.savetxt(filename.replace(".npy", ".csv"), segment, delimiter=",")
        print(f"Saved {len(segment)} samples to {filename} and .csv")


# Create an instance of an animated scrolling window
fig, axes = plt.subplots(3, 1, figsize=(10,  6), sharex = True)
axes = np.atleast_1d(axes)

# To plot more channels just create more instances and add callback handlers below
realtimePlotWindow = RealtimePlotWindow(axes[0], [0, 0.5], title="Raw PPG")
realtimePlotWindowFiltered = RealtimePlotWindow(axes[1], [-0.1, 0.1], title = "PPG bandpass filtered 0.5-7Hz")
realtimePlotWindowheartrate = RealtimePlotWindow(axes[2], [-0.1, 0.1], title = "heartrate (Lowpass)", hasBPM=True)

all_plots = [realtimePlotWindow, realtimePlotWindowFiltered, realtimePlotWindowheartrate]

def update_all(frame):
    return [p.update() for p in all_plots]

fig.tight_layout()
ani = animation.FuncAnimation(fig, update_all, interval=100, cache_frame_data=False)

def onKeyPress(event):
    if event.key == "s":
        # Save last 160 samples (~0.8s at 200Hz) of filtered data
        realtimePlotWindowFiltered.saveSegment(n_samples=500, filename="ppg_template.npy")

fig.canvas.mpl_connect("key_press_event", onKeyPress)

# sampling rate: 150Hz
samplingRate = 150

# Define Filters
fs = samplingRate

#Bandpass Filter for PPG
fc = [0.5, 7] 
fpython = [fc[0] / fs * 2, fc[1] / fs * 2] #Normalised to Nyquist

sosBp = signal.butter(2, fpython, btype = 'bandpass', output = 'sos')

print(sosBp)

bandpassFilterStructures = [
    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sosBp
]

BandPassFilter = iir_chain(bandpassFilterStructures)

#Lowpass Filter to make heartbeat detection easier
fc = 2
fpython = fc / fs * 2 #Normalised to Nyquist

sosLp = signal.butter(2, fpython, btype = 'lowpass', output = 'sos')

print(sosLp)

lowpassFilterStructures = [
    iir2(row[0], row[1], row[2], row[4], row[5]) for row in sosLp
]

LowPassFilter = iir_chain(lowpassFilterStructures)

#Instantiate heartrate monitor
monitor = Heartrate_Monitor(fs)

# called for every new sample which has arrived from the Arduino
def callBack(data):
    t0 = time.perf_counter()

    # send the sample to the plotwindow
    realtimePlotWindow.addData(data)
    # add any filtering here:
    data = BandPassFilter.filter(data)
    realtimePlotWindowFiltered.addData(data)

    data = LowPassFilter.filter(data)
    realtimePlotWindowheartrate.addData(data)

    heartrate = monitor.getHeartrate(data)
    realtimePlotWindowheartrate.setBpm(heartrate)

    t1 = time.perf_counter()
    t = (t1 - t0)
    if t > 1/fs:
        print("Callback routine is running slower than sampling interval")

# Get the Ardunio board.
board = Arduino(PORT)

# Set the sampling rate in the Arduino
board.samplingOn(1000 / samplingRate)

# Register the callback which adds the data to the animated plot
board.analog[0].register_callback(callBack)

# Enable the callback
board.analog[0].enable_reporting()

# show the plot and start the animation
plt.show()

# needs to be called to close the serial port
board.exit()

print("finished")