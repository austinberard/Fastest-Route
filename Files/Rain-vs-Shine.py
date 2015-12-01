#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import csv
import gzip
import os

rain = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0]

rainGrid = []
shineGrid = []

STATIONS = 150
for i in range(0,STATIONS):
    rainGrid.append([])
    for j in range(0,STATIONS):
        rainGrid[i].append(0)

for i in range(0,STATIONS):
    shineGrid.append([])
    for j in range(0,STATIONS):
        shineGrid[i].append(0)

i = 0
currentDir = os.getcwd()
filename = currentDir + "/Data/hubway_trips.csv.gz"

with gzip.open(filename, mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[5] == "strt_statn":
            i += 1
            continue
        if row[5] == "" or row[7] == "":
            i += 1
            continue
        start = int(row[5])
        end = int(row[7])
        rawDate = row[4]
        betterDate = rawDate.replace(" ", "/")
        bettererDate = betterDate.replace(":", "/")
        date = bettererDate.split("/")

        if date[2] == "2013":
            print(i)
            if rain[i] > 0:
                rainGrid[start][end] += 1

            elif rain[i] < 0:
                shineGrid[start][end] += 1

            i += 1
print(rainGrid)
max = 0
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
        if rainGrid[i][j] > max:
            max = rainGrid[i][j]
        if shineGrid[i][j] > max:
            shineGrid = rainGrid[i][j]
print(max)

def darkness(d):
    return str(1-(d/max))

cs = []
pts = []
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
        pts.append([i,j])
        cs.append(darkness(shineGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c=cs, s=1000, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.show()


cs = []
pts = []
for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        pts.append([i, j])
        cs.append(darkness(rainGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c=cs, s=1000, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.show()
