class Heartrate_Monitor:
    def __init__(self, fs, peak_detection_threshold=0.005):
        self.prev_lopass = 0
        self.prev_hipass = 0
        self.cooldown = 0
        self.indexCounter = 0
        self.heartrate = 0
        self.fs = fs
        self.peak_detection_threshold = peak_detection_threshold

    def getHeartRate(self, lopass, hipass):
            self.indexCounter += 1

            # Rising Edge Detection
            crossed_above = (self.prev_hipass <= self.prev_lopass) and (hipass > lopass)
            above_threshold = hipass > self.peak_detection_threshold

            if self.cooldown > 0:
                self.cooldown -= 1

            elif crossed_above and above_threshold:
                self.heartrate = int(60.0 * self.fs / self.indexCounter)
                self.indexCounter = 0
                self.cooldown = int(self.fs / (300 / 60))
                print(f"BPM: {self.heartrate}")

            self.prev_lopass = lopass
            self.prev_hipass = hipass

            return self.heartrate