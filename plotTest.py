import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
import random

# style.use('fivethirtyeight')
fig = plt.figure()
ax1 = fig.add_subplot(1,1,1)

def animate(i):
     xs = []
     ys = []
     for k in range(10):
           x, y = random.random(), random.random()
           xs.append(x)
           ys.append(y)
     ax1.clear()
     ax1.plot(xs, ys)

ani = animation.FuncAnimation(fig, animate, interval=500)
plt.show()