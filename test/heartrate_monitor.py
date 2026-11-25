class Heartrate_Monitor:
    def __init__(self, fs):
        self.p0 = 0
        self.p1 = 0
        self.p2 = 0
        self.cooldown = 0
        self.indexCounter = 0
        self.heartrate = 0
        self.fs = fs

    def checkPeak(x):
        #Logic in here
        return x