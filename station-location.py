#!/usr/bin/env python3

__author__ = 'Austin'
import matplotlib.pyplot as plt
import random
import csv
from scipy.ndimage import imread

with open("hubway_stations.csv") as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    stations = []
    for rows in readCSV2:
        if rows[0] != 'id':     # Skip first line
            stations.append([float(rows[4]), float(rows[5])])


print(stations)
# put up the map
width = 647
height = 749
ne = [42.4045, -71.0357]
sw = [42.3095, -71.1465]


def ll_to_xy(pt):
    pct = (pt[1]-sw[1]) / (ne[1]-sw[1])
    x = width * pct
    pct = (pt[0]-sw[0]) / (ne[0]-sw[0])
    y = height * pct
    return [x, y]


pts = [ll_to_xy(x) for x in stations]
# List comprehension

x1, y1 = zip(*pts)

plt.xlim(0, 650)
plt.ylim(0, 750)
img = imread("map.png")
plt.imshow(img, zorder=0, extent=[0, 647, 0, 749])
plt.scatter(x1, y1)
plt.show()
