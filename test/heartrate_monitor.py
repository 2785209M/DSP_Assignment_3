class Heartrate_Monitor:
    def __init__(self, fs):
        self.p0 = 0
        self.p1 = 0
        self.p2 = 0
        self.cooldown = 0
        self.indexCounter = 0
        self.heartrate = 0
        self.fs = fs

    def getHeartrate(self, x):
        #Add the new sample
        #I considered a buffer here but with length 3 I'm not sure it's worth the overhead?
        self.p0 = self.p1
        self.p1 = self.p2
        self.p2 = x

        #Decrement counter by 1 every sample
        if self.cooldown > 0:
            self.cooldown -= 1

        #if p0 < p1 > p2 then p1 is a local maximum (peak)
        if self.cooldown == 0 and self.p0 < self.p1 > self.p2:
            self.heartrate = self.indexCounter / self.fs

            #reset index counter
            self.indexCounter = 0

            #cooldown limits heartrate to 220bpm for fs
            self.cooldown = self.fs / (220 / 60)

            return self.heartrate

        else:
            #if no peak detected then increment index counter
            self.indexCounter += 1
            #and return current heartrate
            return self.heartrate


            

        