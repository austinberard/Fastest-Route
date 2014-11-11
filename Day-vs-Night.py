#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import hubway

dayGrid = hubway.initializeGrid(hubway.STATIONS)
nightGrid = hubway.initializeGrid(hubway.STATIONS)

for h, start, end in hubway.trip_hours():
    if h in range(6, 18):
        dayGrid[start][end] += 1
    if h in range(18, 24) or h in range(0, 6):
        nightGrid[start][end] += 1


print(dayGrid)
print(nightGrid)
max = 0
for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        if dayGrid[i][j] > max:
            max = dayGrid[i][j]
        elif nightGrid[i][j] > max:
            max = nightGrid[i][j]
print(max)


differenceGrid = hubway.initializeGrid(hubway.STATIONS)

for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        differenceGrid[i][j] = abs(dayGrid[i][j] - nightGrid[i][j])


def darkness(d):
    return str(1-(d/max))

cs = []
pts = []
for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        pts.append([i,j])
        cs.append(darkness(dayGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Day Usage")
plt.show()




cs = []
pts = []
for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        pts.append([i,j])
        cs.append(darkness(nightGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Night Usage")
plt.show()



cs = []
pts = []
for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        pts.append([i,j])
        cs.append(darkness(differenceGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Differences")
plt.show()



