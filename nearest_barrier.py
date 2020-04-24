import numpy as np
from math import sin, cos, sqrt, pi
from numba import jit
from time import time
import cv2


@jit(nopython=True)
def find_nearest_barrier(gray,x,y,theta):
    h,w = gray.shape
    c, s = cos(theta), sin(theta)
    x2, y2 = x, y
    ix2, iy2 = round(x2), round(y2)
    while ix2>0 and iy2>0 and ix2<w-1 and iy2<h-1:
        x2 += c
        y2 += s
        ix2, iy2 = round(x2), round(y2)
        if gray[iy2,ix2] == 0:
            return ix2,iy2         
    return ix2,iy2  

def test0():
    # h,w = 500,500
    # gray = np.zeros((h,w,1), np.uint8)
    # gray[10:490, 150:200,0] = 255
    im = cv2.imread('binmap.bmp')
    gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
    x2,y2 = find_nearest_barrier(gray,175,380,pi/4)
    # bgr = cv2.cvtColor(gray,cv2.COLOR_GRAY2RGB)
    cv2.circle(im,(x2,y2),5,(0,0,255),3)
    cv2.imshow('bgr',im)
    cv2.waitKey(0)

if __name__ == "__main__":
    test0()
