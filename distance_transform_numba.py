#given binary map (each pixel is ON or OFF),
#make a float-valued distance map where the val at
#each pixel is the distance to the closest ON pixel

 

import numpy as np
import math
from numba import jit, prange
from time import time


from pylab import close, colorbar, figure, gray, hist, imshow, ion, plot, savefig, show
import scipy

#from scipy.misc import imread, imsave
#from scipy.ndimage import imread

import matplotlib
from matplotlib.pyplot import imread

import numpy as np
from imageio import imwrite

binmap = np.zeros((500,500),np.float64)
binmap[1:499, 150:230] = 255
imwrite('binmap.bmp',binmap)
h,w = binmap.shape
print('h,w:',h,w)
distmap = np.zeros((h,w),np.float64)

import numpy as np
import math
from numba import jit, prange

HUGE = 100_000_000
@jit(nopython=True) #numba works well on this function
def find_nearest_pixel(binmap,r,c,h,w):
     d2 = HUGE + 0 #smallest distance (squared) so far
     for r2 in range(h):
           for c2 in range(w):
                if binmap[r2,c2] > 0:
                      dist2 = (r-r2)**2 + (c-c2)**2
                      if dist2 < d2:
                           d2 = dist2 + 0
     return math.sqrt(d2)

    
@jit (nopython=True, parallel=True) #numba helps when image is big
def distance_transform(binmap, distmap):
     h,w = binmap.shape
     for r in prange(h):
           for c in prange(w):
                distmap[r,c] = find_nearest_pixel(binmap,r,c,h,w)
     return distmap

 

@jit (nopython=True) #numba doesn't help much
def distance_transform0(binmap, distmap):
     h,w = binmap.shape
     for r in range(h):
           for c in range(w):
                distmap[r,c] = find_nearest_pixel(binmap,r,c,h,w)
     return distmap

@jit (nopython=True, parallel=True) #numba helps when image is big
def rescale(distmap):
     h,w = distmap.shape
     for r in prange(h):
           for c in prange(w):
                if distmap[r,c] <= 0.1: distmap[r,c] = 255
                elif distmap[r,c]> 50. : distmap[r,c] = 0
                else: distmap[r,c] = 200 - int(distmap[r,c]/10)*40    
     return distmap

imwrite('binmap.bmp',binmap)
print('start')
tic = time()
distmap = distance_transform(binmap,distmap)
distmap = rescale(distmap)
toc = time()
print('finish')
print('time:',toc-tic)

 

imwrite('output.bmp',distmap)

 

# ion()
figure();imshow(distmap);colorbar()