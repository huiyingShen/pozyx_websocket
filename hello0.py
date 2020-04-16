from time import time,sleep
import numpy as np
import cv2
from multiprocessing import Process

# im = cv2.imread('pozyx_tags.jpg')
# dim = (640, 480)
# # resize image
# resized = cv2.resize(im, dim, interpolation = cv2.INTER_AREA)
# cv2.imwrite('resized.jpg',resized)
im = cv2.imread('resized.jpg')
clone = im.copy()
# print(im.shape)

def oneStep(title,clone):
    clone[i:i+20,i*2:i*2+50,:] = 0
    cv2.line(clone,(i,2*i),(2*i,4*i),(0,0,255),3)
    resized = cv2.resize(clone, (1280,960), interpolation = cv2.INTER_AREA)
    cv2.imshow(title,resized)

t0 = time()
for i in range(100):
    clone = im.copy()
    clone[i:i+20,i*2:i*2+50,:] = 0
    cv2.line(clone,(i,2*i),(2*i,4*i),(0,0,255),3)
    resized = cv2.resize(clone, (1280,960), interpolation = cv2.INTER_AREA)
    cv2.imshow('tag',resized)
    cv2.waitKey(1)
print(100/(time()-t0))
cv2.waitKey(0)