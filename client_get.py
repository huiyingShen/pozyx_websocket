from time import time
from math import sqrt,pi
import requests
import cv2
from simpleAudioTest import BeeperManager,getPlayerNew
import nearest_barrier

def bound(val,low,high):
    if val< low: val = low
    elif val > high: val = high
    return val

# fMin,fMax,nSample=300,3000,20
# bm = BeeperManager().setAllBeepers(fMin=fMin, fMax=fMax, nSample=nSample, dur=0.02, trim2Zero=True).addKnock()
# # bm = getPlayerNew()
# bm.playAll()


im0 = cv2.imread('image00.png')
gray = cv2.cvtColor(im0,cv2.COLOR_BGR2GRAY)

# im0 = cv2.imread('dist.png')
# im0 = cv2.imread('output.bmp')
coef = 3
r,c,_ = im0.shape
im0 = cv2.resize(im0, (int(r*coef),int(c*coef)), interpolation = cv2.INTER_AREA)
cv2.waitKey(25)
address = 'http://10.0.0.241:8000'
route = '/xyz'
t0 = time()
ix,iy = 0,0
t1 = t0
tPlay = t0
player = None
while True:
    im = im0.copy()
    c = cv2.waitKey(5)
    if c == 27:
        break
    # cv2.circle(im,(int(ix*coef),int(iy*coef)),5,(0,255,255),3)
    try: r = requests.get(address + route) 
    except: continue
    xyz = r.json()
    ix,iy = int(xyz['x']),int(xyz['y'])
    theta = int(xyz['z'])*pi/180

    isNew = xyz['isNew']
    if isNew == False: continue
    # val = 255 - int(im[iy,ix,0])
    # iPlayer = int((nSample + 1)*val/255)
    ix2,iy2 = nearest_barrier.find_nearest_barrier(gray,ix,iy,theta)
    d = sqrt((ix-ix2)*(ix-ix2) + (iy-iy2)*(iy-iy2))
    dMax = 500
    iPlayer = int((1 - d/dMax)*len(bm.beepers))
    dt = time() - t1
    t1 = time()
    print("dt = {:6.4}, x = {}, y = {}, iPlayer = {}".format(dt,ix,iy,iPlayer))

    if time() - tPlay > 0.05:
        player = bm.playi(iPlayer)
        if player != None: tPlay = time()
    ix = int(ix*coef)
    iy = int(iy*coef)
    ix2 = int(ix2*coef)
    iy2 = int(iy2*coef)
    cv2.circle(im,(ix,iy),10,(0,0,255),7)
    cv2.circle(im,(ix2,iy2),7,(0,0,255),3)
    cv2.line(im,(ix,iy),(ix2,iy2),(0,0,255),3)
    cv2.imshow('im',im)

print(100/(time()-t0))
cv2.waitKey(0)
