#!/usr/bin/env python3
#Add different color for frequency of station
import matplotlib.pyplot as plt
import random
import csv
from scipy.ndimage import imread
import gzip
import flow
import hubway
import os

__author__ = 'Austin'

currentDir = os.getcwd()
filename = currentDir + "/Data/hubway_stations.csv"
with open(filename) as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    stations = []
    for rows in readCSV2:
        if rows[0] != 'id':     # Skip first line
            stations.append([float(rows[4]), float(rows[5])])




# print(stations)
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



# grid = []
#
# STATIONS = 150
# for i in range(0,STATIONS):
#     grid.append([])
#     for j in range(0,STATIONS):
#         grid[i].append(0)
#
#
# with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
#     for row in csv.reader(csvfile, delimiter=","):
#         if row[5] == "strt_statn":
#             continue
#         if row[5] == "" or row[7] == "":
#             continue
#         start = int(row[5])
#         end = int(row[7])
#
#         if start > STATIONS or end > STATIONS:
#             print("Ouch "+str(start) + " " + str(end))
#             exit()
#         grid[start][end] += 1
#
#
# max = 0
# for i in range(0,STATIONS):
#   for j in range(0,STATIONS):
#       if grid[i][j] > max:
#           max = grid[i][j]
# print(max)
#
# def darkness(d):
#     return str(1-(d/max))
#
# cs = []
# pts = []
# for i in range(0,STATIONS):
#     for j in range(0,STATIONS):
#         pts.append([i,j])
#         cs.append(darkness(grid[i][j]))
#
# xs, ys = zip(*pts)
#
# plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
# plt.xlim(0, 150)
# plt.ylim(0, 150)
# plt.show()
