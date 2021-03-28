from time import time
from math import sqrt,pi,atan2,sin,cos
import requests
import cv2
from numba import jit

class PozyxParam:
    def __init__(self):
        self.isExp = True
        self.isHigh2Low = True
        self.freqLow = 300.0
        self.freqHigh = 1000.0
        self.distMax = 600.0  

    def getFreq(self, d):
        f1 = freqLow
        f2 = freqHigh
        if self.isHigh2Low:
            f2 = freqLow
            f1 = freqHigh
        
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
           

def dist(x1,y1,x2,y2):
    return sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))

class OneFingerTouch:
    
    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.dMin = 10
        self.d2Follow = 20
    
    def touchMoved(self, x,y):
        d = dist(self.x0,self.y0,x,y)
        if d < self.dMin: return False,0
        theta = atan2(y-self.y0,x-self.x0)
        if d > self.d2Follow:
            self.x0 += (d - self.d2Follow)*cos(theta)
            self.y0 += (d - self.d2Follow)*sin(theta)
        return True,theta

im0 = cv2.imread('image00.png')
gray = cv2.cvtColor(im0,cv2.COLOR_BGR2GRAY)


coef = 1.0
row,col,_ = im0.shape
print(row,col)
im0 = cv2.resize(im0, (int(row*coef),int(col*coef)), interpolation = cv2.INTER_AREA)
cv2.waitKey(25)
# cv2.imshow("img",im0)
# cv2.waitKey(0)

address = 'http://10.0.0.242:8000'
route = '/xyz'
t0 = time()
finger = OneFingerTouch()

while True:
    im = im0.copy()
    c = cv2.waitKey(5)
    if c == 27:
        break
    # cv2.circle(im,(int(ix*coef),int(iy*coef)),5,(0,255,255),3)
    try: res = requests.get(address + route) 
    except: continue
    xyz = res.json()
    ix,iy = int(xyz['x']/10),int(xyz['y']/10)
    if ix<=0 or iy <= 0 or ix >= col or iy >= row:
        pass
    else:
        b,theta = finger.touchMoved(ix,iy)
        pix = gray[iy,ix]
        if b :
            ix = int(ix*coef)
            iy = int(iy*coef)
            ix2 = int(finger.x0*coef)
            iy2 = int(finger.y0*coef)
            print(ix,iy)
            cv2.circle(im,(ix,iy),5,(0,0,255),2)
            cv2.circle(im,(ix2,iy2),3,(0,255,0),1)
            if pix > 250:
                ix2,iy2 = find_nearest_barrier(gray,ix,iy,theta,thrsh = 250)
                cv2.circle(im,(ix2,iy2),3,(255,0,0),1)
            cv2.imshow('im',im)
print(100/(time()-t0))
cv2.waitKey(0)
