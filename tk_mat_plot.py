from tkinter import * 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, 
NavigationToolbar2Tk)
  
import numpy as np

# import matplotlib.pyplot as plt
# import matplotlib.image as mpimg

# plot function is created for 
# plotting the graph in 
# tkinter window
coef = 1.0
fig = Figure(figsize = (5, 5),  dpi = 100)
y = [i**2 for i in range(101)]
y = np.array(y)
plot1 = fig.add_subplot(111)
def plot():
    global coef
    plot1.clear()
    coef = coef*1.1
    plot1.plot(y*coef)

    # img = mpimg.imread('image00.png')
    # imgplot = plt.imshow(img)

    canvas = FigureCanvasTkAgg(fig, master = window)  
    canvas.draw()
  
    # placing the canvas on the Tkinter window
    canvas.get_tk_widget().pack()
  
    # creating the Matplotlib toolbar
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
  
    # placing the toolbar on the Tkinter window
    canvas.get_tk_widget().pack()
  
# the main Tkinter window
window = Tk()
window.title('Plotting in Tkinter')
window.geometry("500x500")
plot_button = Button(master = window, command = plot, height = 2,  width = 10, text = "Plot")
plot_button.pack()
window.mainloop()