#!/usr/bin/env python3
#Add different color for frequency of station
__author__ = 'Austin'
import matplotlib.pyplot as plt
import random
import csv
from scipy.ndimage import imread
import gzip

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

# with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
#     xs = []
#     ys = []
#     for row in csv.reader(csvfile, delimiter=","):
#         if row[5] != "strt_statn":
#             k = 0
#             while k <= 10:
#                 xs.append((row[5]))
#                 ys.append((row[7]))
#                 k = k + 1
#
# print(xs)
# print(ys)

# plt.scatter(xs, ys)
# plt.show()
