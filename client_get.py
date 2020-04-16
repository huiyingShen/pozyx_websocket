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


im = cv2.imread('dist.png')
cv2.waitKey(25)
url = 'http://127.0.0.1:8000/xyz'
t0 = time()
ix,iy = 0,0
t1 = t0
while True:
    cv2.circle(im,(ix,iy),5,(0,255,255),3)
    r = requests.get(url) 
    xyz = r.json()
    ix,iy = int(xyz['x']),int(xyz['y'])
    iPlayer = int(xyz['z'])
    # val = 255 - int(im[iy,ix,0])
    # iPlayer = int((nSample + 1)*val/255)

    dt = time() - t1
    t1 = time()
    print("dt = {:6.4}, x = {}, y = {}, iPlayer = {}".format(dt,ix,iy,iPlayer))


    bm.playi(iPlayer)
    cv2.circle(im,(ix,iy),5,(0,0,255),3)
    cv2.imshow('im',im)
    c = cv2.waitKey(25)
    if c == 27:
        break
print(100/(time()-t0))
cv2.waitKey(0)
