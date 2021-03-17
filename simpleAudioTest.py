import numpy as np
import simpleaudio as sa
from time import time,sleep

class AsyncBeeper:
    def __init__(self,freq, dur, trim2Zero=True):
        self.freq,self.dur_msec = freq,int(dur*1000)
        self.sample_rate = 44100

        t = np.linspace(0, dur, int(dur*self.sample_rate), False)
        # t = np.linspace(0, dur,  num=(1+self.sample_rate), endpoint=True)
        self.raw = np.sin(freq * t * 2 * np.pi)
        if trim2Zero: self.cutBack2Zero()
        print(len(t),len(self.raw),t[0],self.raw[-1])
        self.audio = self.raw*32767 / np.max(np.abs(self.raw))
        self.audio = self.audio.astype(np.int16)
        self.wave_obj = sa.WaveObject(self.audio, 1, 2, self.sample_rate)

    def createFromWav(self,wav):
        self.wave_obj = sa.WaveObject.from_wave_file(wav)

    def cutBack2Zero(self):
        sz = len(self.raw)
        for i in range(sz):
            n = sz - i - 1
            if np.abs(self.raw[n]) <= 0.05 :
                break
        # print(sz, n, self.raw[n])
        self.raw = self.raw[:n+1]

    def play(self):
        # self.audio = self.raw*vol*32767 / np.max(np.abs(self.raw))
        # self.audio = self.audio.astype(np.int16)
        # self.play_obj = sa.play_buffer(self.audio, 1, 2, self.sample_rate)
        self.play_obj = self.wave_obj.play()
        return self.play_obj

    def play_sync(self):
        self.play().wait_done()

    def isPlaying(self):
        return self.play_obj.is_playing()

class BeeperManager:
    def __init__(self,freqs = [], dur = 0.1, trim2Zero=True):
        self.iPlayer = -1
        self.beepers = []
        for f in freqs:
            self.beepers.append(AsyncBeeper(f,dur,trim2Zero))

    def setAllBeepers(self,fMin=300,fMax=3000,nSample=10,dur=0.05,trim2Zero=True, reverse = True):
        base = np.exp(np.log(fMax/fMin)/nSample)
        freqs = [fMin*base**i for i in range(nSample+1)]
        if reverse: freqs.reverse()
        self.beepers = []
        for f in freqs:
            self.beepers.append(AsyncBeeper(f,dur,trim2Zero))
        return self

    def addKnock(self):
        f,dur,trim2Zero = 300,0.01,False
        player = AsyncBeeper(f,dur,trim2Zero)
        player.createFromWav('Knocking-on-door-two-knocks.wav')
        self.beepers.append(player)
        return self

    def beep_by_distance(self,d,dMax=6):
        iPlayer = int((1 - d/dMax)*len(self.beepers))
        self.playi(iPlayer)

    
    def playi(self,iPlayer):
        if iPlayer == self.iPlayer and self.beepers[iPlayer].isPlaying():
            return None
        if iPlayer < 0: iPlayer  = 0
        elif iPlayer >= len(self.beepers): iPlayer = len(self.beepers) - 1
        self.beepers[iPlayer].play()
        return self.beepers[iPlayer]

    def isPlaying(self):
        for b in self.beepers:
            if b.isPlaying():
                return True
        return False

    def playAll(self):
        for b in self.beepers:
            b.play_sync()


def test2(fMin=300,fMax=3000,nSample=10):
    base = np.exp(np.log(fMax/fMin)/nSample)
    freqs = [fMin*base**i for i in range(nSample+1)]
    print(len(freqs))
    bm = BeeperManager(freqs,dur=0.15,trim2Zero=True)
    t0 = time()
    bm.playAll()
    bm.playi(11).play_obj.wait_done()
    # bm.playi(5).play_obj.wait_done()
    bm.playi(0).play_obj.wait_done()
    print('dt = ', time()-t0)

def test3():
    bm = BeeperManager().setAllBeepers(fMin=300, fMax=3000, nSample=20, dur=0.05, trim2Zero=True).addKnock()
    t0 = time()
    bm.playAll()
    print('fps = ', 1/(time()-t0)*20)

def getFreq1():
    f0 = [880, ]
    k = 2**(-1.0/12.0)
    f1 = 586.67
    f0.extend( [f1*k**(0.1*d/0.1) for d in range(0,6)])
    print(f0)
    return f0

def getPlayerNew():
    return BeeperManager(freqs = getFreq1(), dur = 0.05, trim2Zero=True)

def test4():
    bm = getPlayerNew()
    bm.playi(0).play_obj.wait_done() 
    bm.playi(1).play_obj.wait_done()
    bm.playi(6).play_obj.wait_done()
if __name__ == '__main__':
    # AsyncBeeper(440,0.25).play_sync()
    test3()
