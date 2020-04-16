from time import time
import requests
import cv2

im = cv2.imread('dist.png')
url = 'http://127.0.0.1:8000/xyz'
t0 = time()
x,y = 0,0
for i in range(100):
    cv2.circle(im,(x,y),5,(0,255,255),3)
    r = requests.get(url) 
    xyz = r.json()
    x,y = xyz['x'],xyz['y']
    cv2.circle(im,(x,y),5,(0,0,255),3)
    cv2.imshow('im',im)
    cv2.waitKey(1)
print(100/(time()-t0))
cv2.waitKey(0)
