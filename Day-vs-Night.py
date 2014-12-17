#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import hubway

dayGrid = hubway.initializeGrid()
nightGrid = hubway.initializeGrid()

for stime, sstation, etime, estation in hubway.trips():
    sh = stime.timetuple().tm_hour

    if sh in range(6, 18):
        dayGrid[sstation][estation] += 1
    if sh in range(18, 24) or sh in range(0, 6):
        nightGrid[sstation][estation] += 1


print(dayGrid)
print(nightGrid)

max = max(hubway.findMax(dayGrid), hubway.findMax(nightGrid))
print(max)

differenceGrid = hubway.initializeGrid()
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



