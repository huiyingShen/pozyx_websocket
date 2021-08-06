from time import time
from math import sqrt,pi,atan2,sin,cos
import requests
import cv2
from numba import jit
import numpy as np

from pysinewave import SineWave
import simpleaudio as sa
from time import time,sleep
import threading

class AudioPlayer:
    def __init__(self):
        self.sineWave = SineWave(pitch = 12, pitch_per_second = 100)
        self.wave_obj = sa.WaveObject.from_wave_file("Knocking-on-door.wav")
        self.cases = "beep","knock","silent"
        self.freq = 500
        self.case = "silent"

    def knock(self,n=1):
        for _ in range(n):
            self.wave_obj.play().wait_done()

    def beep(self,freq,t=0.01):
        self.sineWave.set_frequency(freq)
        self.sineWave.play()
        sleep(t)

    def loop(self):
        while True:
            if not (self.case in self.cases): break
            if self.case == self.cases[0]: 
                self.beep(self.freq,0.01)
            elif self.case == self.cases[1]: 
                self.sineWave.stop()
                self.knock(1)
            else: 
                self.sineWave.stop()
                sleep(0.01)
                
    def go(self):
        threading.Thread(target=self.loop).start()

class PozyxParam:
    def __init__(self):
        self.isExp = True
        self.isHigh2Low = True
        self.freqLow = 300.0
        self.freqHigh = 1000.0
        self.distMax = 600.0  

    def getFreq(self, d):
        f1 = self.freqLow
        f2 = self.freqHigh
        if self.isHigh2Low:
            f2 = self.freqLow
            f1 = self.freqHigh
        
        if self.isExp: return self.freq_exp(d, f1, f2)
        else: return self.freq_linear(d,f1, f2)
    
    def  freq_linear(self,d, f_min, f_max):
        return f_min + (f_max-f_min)*(d/self.distMax)
    
    def freq_exp(self,d, f_min, f_max):
        return f_min*pow(f_max/f_min,d/self.distMax)
    
@jit(nopython=True)
def find_nearest_barrier(gray,x,y,theta, thrsh = 250):
     #access image as im[x,y] even though this is not idiomatic!
     #assume that x and y are integers
     h,w = gray.shape
     cs, sn = cos(theta), sin(theta)
     x2,y2 = x,y
     while True:
        x2 += cs
        y2 += sn
        ix2, iy2 = round(x2), round(y2)
        if ix2 < 0 or ix2 >= w or iy2 < 0 or iy2 >= h: 
            return ix2, iy2
        if gray[iy2,ix2] < thrsh:
            return ix2, iy2
           
class PozClient:
    t0 = time()
    audioPlayer = AudioPlayer()
    param = PozyxParam()

    audioPlayer.case = "silent"
    audioPlayer.go()
    sz = 3
    xa = np.array([0]*sz)
    ya = np.array([0]*sz)
    
    def __init__(self,fn = "image00.png"):
        self.im0 = cv2.imread(fn)
        self.gray = cv2.cvtColor(self.im0,cv2.COLOR_BGR2GRAY)
        self.row,self.col,_ = self.im0.shape

    def oneStep(self,xf,yf,theta,i):
        i = i%self.sz
        im = self.im0.copy()
        self.xa[i] = xf
        self.ya[i] = yf
        print("xf, yf = {},{}".format(xf,yf))
        if xf<=0 or yf <= 0 or xf >= self.col or yf >= self.row:
            self.audioPlayer.case = "knock"
            pass
        else:
            ix = int(np.mean(self.xa))
            iy = int(np.mean(self.ya))
            pix = self.gray[iy,ix]
            cv2.circle(im,(ix,iy),7,(0,0,255),3)
            if pix > 250:
                ix3,iy3 = find_nearest_barrier(self.gray,ix,iy,theta,thrsh = 250)
                cv2.circle(im,(ix3,iy3),5,(0,200,0),2)
                dx,dy = (ix3-ix), (iy3-iy)
                d = sqrt(dx*dx + dy*dy)
                self.audioPlayer.case = "beep"
                self.audioPlayer.freq = self.param.getFreq(d)
            else: self.audioPlayer.case = "silent"
        return im

if __name__ == "__main__":
    main()
    # PozClient().test0()
