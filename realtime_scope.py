#!/usr/bin/python3

from pyfirmata2 import Arduino
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

    def __init__(self, axisLimits, title="Signal"):
        # create a plot window
        self.fig, self.ax = plt.subplots()
        # that's our plotbuffer
        self.plotbuffer = np.zeros(500)
        # create an empty line
        self.line, = self.ax.plot(self.plotbuffer)
        # axis
        self.ax.set_ylim(axisLimits[0], axisLimits[1])
        # That's our ringbuffer which accumluates the samples
        # It's emptied every time when the plot window below
        # does a repaint
        self.ringbuffer = []
        # add any initialisation code here (filters etc)
        # start the animation
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100, cache_frame_data=False)

    # updates the plot
    def update(self, data):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-500:]
        self.ringbuffer = []
        # set the new 500 points of channel 9
        self.line.set_ydata(self.plotbuffer)
        return self.line,

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
# To plot more channels just create more instances and add callback handlers below
realtimePlotWindow = RealtimePlotWindow([0, 1], title="Raw PPG")
realtimePlotWindowFiltered = RealtimePlotWindow([-0.1, 0.1], title = "PPG bandpass filtered 0.5-7Hz")
realtimePlotWindowheartrate = RealtimePlotWindow([-0.1, 0.1], title = "heartrate")

def onKeyPress(event):
    if event.key == "s":
        # Save last 160 samples (~0.8s at 200Hz) of filtered data
        realtimePlotWindowFiltered.saveSegment(n_samples=500, filename="ppg_template.npy")

realtimePlotWindowFiltered.fig.canvas.mpl_connect("key_press_event", onKeyPress)

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
    #I think we can just start a timer here?
    t0 = time.perf_counter()

    # send the sample to the plotwindow
    realtimePlotWindow.addData(data)
    # add any filtering here:
    data = BandPassFilter.filter(data)
    realtimePlotWindowFiltered.addData(data)

    data = LowPassFilter.filter(data)
    realtimePlotWindowheartrate.addData(data)

    heartrate = monitor.getHeartrate(data)
    #print(heartrate)

    t1 = time.perf_counter()
    t = (t1 - t0)
    print(t)
    if t > 1/fs:
        print("Callback routine is running slower than sampling interval")

    #And end the timer here? then compare it against 1/fs

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