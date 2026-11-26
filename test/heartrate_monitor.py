class Heartrate_Monitor:
    def __init__(self, fs, threshold=0.01):
        self.p0 = 0
        self.p1 = 0
        self.p2 = 0
        self.threshold = threshold
        self.cooldown = 0
        self.indexCounter = 0
        self.heartrate = 0
        self.fs = fs

    def getHeartrate(self, sample):
        # Shift 3-sample window
        self.p0 = self.p1
        self.p1 = self.p2
        self.p2 = sample

        if self.cooldown > 0:
            self.cooldown -= 1

        # Detect local peak above threshold
        if self.cooldown == 0 and self.p0 < self.p1 > self.p2 and self.p1 > self.threshold:
            if self.indexCounter > 0:
                self.heartrate = int(60.0 * self.fs / self.indexCounter)
                print(f"BPM: {self.heartrate}")  # Print only on beat
            self.indexCounter = 0
            self.cooldown = int(self.fs / (220 / 60))
        else:
            self.indexCounter += 1

        return self.heartrate