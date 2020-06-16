import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file',
                    type=str,
                    default='Sample1.avi')
parser.add_argument('-p', '--path',
                    type=str,
                    default='./picture/')
parser.add_argument('-st', '--stream',
                    type=str)
FLAGS, unparsed = parser.parse_known_args()
if FLAGS.file:
    cap = cv.VideoCapture(FLAGS.path + FLAGS.file)
elif FLAGS.stream:
    cap = cv.VideoCapture(FLAGS.stream)
ret, image = cap.read()

plt.imshow(image)

points=[]
def onclick(event):
    if event.button==1:
        print(event.xdata, event.ydata)
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))
        points.append([x,y])

    elif event.button==3:
        print("Result = np.array(",points,")")
        del points[:]

plt.gcf().canvas.mpl_connect('button_press_event', onclick)

plt.show()