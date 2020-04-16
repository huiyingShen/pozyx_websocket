from time import time
import requests
url = 'http://127.0.0.1:8000/xyz'
t0 = time()
for i in range(1000):
    k = i%100
    x,y = k*2,k*3
    r = requests.post(url, data ={'x':x,'y':y,'z':0}) 
    # print(r.json() )
print(1000/(time()-t0))