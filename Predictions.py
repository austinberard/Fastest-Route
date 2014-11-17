#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import hubway

realGrid = hubway.initializeGrid(hubway.STATIONS)
hourGrid = hubway.initializeGrid(hubway.STATIONS)

for h, start, end in hubway.trip_hours():
    if h in range(0, 24):
        realGrid[start][end] += 1

print(realGrid)

for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        hourGrid[i][j] = (realGrid[i][j] / (365 * 3 * 24))


print(hourGrid)

max = 0
for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        if hourGrid[i][j] > max:
            max = hourGrid[i][j]
print(max)