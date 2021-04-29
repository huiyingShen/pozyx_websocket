from time import time
from math import sqrt,pi,atan2,sin,cos

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
        self.alpha = 1.0

    def getFreq(self, d):
        f1 = self.freqLow
        f2 = self.freqHigh
        if self.isHigh2Low:
            f1,f2 = f2,f1
        
        if self.isExp: return self.freq_exp(d, f1, f2)
        else: return self.freq_linear(d,f1, f2)

    def getScaledD(self,d):
        return pow(d/self.distMax,self.alpha)
    
    def  freq_linear(self,d, f_min, f_max):
        return f_min + (f_max-f_min)*self.getScaledD(d)
    

    def freq_exp(self,d, f_min, f_max):
        return f_min*pow(f_max/f_min,self.getScaledD(d))
    

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
           

def dist(x1,y1,x2,y2):
    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

class OneFingerTouch:
    
    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.dMin = 10
        self.d2Follow = 20
        self.theta = 0
    
    def touchMoved(self, x,y):
        d = dist(self.x0,self.y0,x,y)
        if d < self.dMin: return False, self.theta
        self.theta = atan2(y-self.y0,x-self.x0)
        if d > self.d2Follow:
            self.x0 += (d - self.d2Follow)*cos(self.theta)
            self.y0 += (d - self.d2Follow)*sin(self.theta)
        return True,self.theta

def main(recv_conn, fn_im = 'image00.png'):
    im0 = cv2.imread('image00.png')
    gray = cv2.cvtColor(im0,cv2.COLOR_BGR2GRAY)


    row,col,_ = im0.shape
    print(row,col)
    cv2.waitKey(25)
    # cv2.imshow("img",im0)
    # cv2.waitKey(10)

    t0 = time()
    finger = OneFingerTouch()
    audioPlayer = AudioPlayer()
    param = PozyxParam()

    audioPlayer.case = "silent"
    audioPlayer.go()
    sz = 10
    xa = np.array([0]*sz)
    ya = np.array([0]*sz)
    
    i = 0
    while True:
        i = (i+1)%sz
        im = im0.copy()
        c = cv2.waitKey(5)
        if c == 27:
            audioPlayer.case = "quit"
            break
        # cv2.circle(im,(int(ix*coef),int(iy*coef)),5,(0,255,255),3)
        x,y,theta = recv_conn.recv()
        if x == -1 and y == -1:       break
        print("x: {:6.2f}, y: {:6.2f}, theta: {:6.2f}".format(x,y,theta))
        ix,iy = int(x/10),int(y/10)
        iy = 600 - iy
        theta = theta/180*3.14
        xa[i] = ix
        ya[i] = iy
        if ix<=0 or iy <= 0 or ix >= col or iy >= row:
            audioPlayer.case = "knock"
            pass
        else:
            # b,theta = finger.touchMoved(ix,iy)
            b,_ = finger.touchMoved(ix,iy)
            pix = gray[iy,ix]
            if b :
                ix = int(np.mean(xa))
                iy = int(np.mean(ya))
                # ix2 = int(finger.x0)
                # iy2 = int(finger.y0)
                print(ix,iy)
                cv2.circle(im,(ix,iy),7,(0,0,255),3)
                # cv2.circle(im,(ix2,iy2),3,(0,255,0),1)
                if pix > 250:
                    ix3,iy3 = find_nearest_barrier(gray,ix,iy,theta,thrsh = 250)
                    cv2.circle(im,(ix3,iy3),5,(0,200,0),2)
                    dx,dy = (ix3-ix), (iy3-iy)
                    d = sqrt(dx*dx + dy*dy)
                    audioPlayer.case = "beep"
                    audioPlayer.freq = param.getFreq(d)
                else: audioPlayer.case = "silent"
                # im = cv2.flip(im,1)
                coef = 1.0
                im = cv2.resize(im, (int(row*coef),int(col*coef)), interpolation = cv2.INTER_AREA)
 
                cv2.imshow('im',im)
    print(100/(time()-t0))
    audioPlayer.case = "silent"