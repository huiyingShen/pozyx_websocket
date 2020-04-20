from time import time
import requests
import cv2
from simpleAudioTest import BeeperManager

def bound(val,low,high):
    if val< low: val = low
    elif val > high: val = high
    return val

fMin,fMax,nSample=300,3000,20
bm = BeeperManager().setAllBeepers(fMin=fMin, fMax=fMax, nSample=nSample, dur=0.02, trim2Zero=True)


im0 = cv2.imread('dist.png')
im0 = cv2.resize(im0, (1200,1200), interpolation = cv2.INTER_AREA)
cv2.waitKey(25)
url = 'http://10.0.0.241:8000/xyz'
t0 = time()
ix,iy = 0,0
t1 = t0
while True:
    im = im0.copy()
    c = cv2.waitKey(5)
    if c == 27:
        break
    cv2.circle(im,(ix*2,iy*2),5,(0,255,255),3)
    r = requests.get(url) 
    xyz = r.json()
    ix,iy = int(xyz['x']),int(xyz['y'])
    iPlayer = int(xyz['z'])
    isNew = xyz['isNew']
    if isNew == False: continue
    # val = 255 - int(im[iy,ix,0])
    # iPlayer = int((nSample + 1)*val/255)

    dt = time() - t1
    t1 = time()
    print("dt = {:6.4}, x = {}, y = {}, iPlayer = {}".format(dt,ix,iy,iPlayer))


    bm.playi(iPlayer)
    cv2.circle(im,(ix*2,iy*2),7,(0,0,255),4)
    cv2.imshow('im',im)

print(100/(time()-t0))
cv2.waitKey(0)
