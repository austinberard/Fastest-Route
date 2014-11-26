#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import hubway

departGrid = hubway.initializeGrid(hubway.STATIONS)
avgHourGrid = hubway.initializeGrid(hubway.STATIONS)

for stime, sstation, etime, estation in hubway.trips():
    departGrid[sstation][estation] += 1

print(departGrid)

for i in range(0, hubway.STATIONS):
    for j in range(0, hubway.STATIONS):
        avgHourGrid[i][j] = (departGrid[i][j] / (365 * 3 * 24))

def grid_for_hour(departure, hour, date):
    grid = hubway.initializeGrid(hubway.STATIONS)
    for stime, sstation, etime, estation in hubway.trips():
        if departure:
            if stime.date == date and stime.timetuple().tm_hour == hour:
                grid[sstation][estation] += 1
        else:
            if etime.date == date and etime.timetuple().tm_hour == hour:
                grid[sstation][estation] += 1
    return grid

differenceGrid = hubway.initializeGrid(hubway.STATIONS)


def square_difference(realGrid, createdGrid):
    sums = 0
    for i in range(0, hubway.STATIONS):
        for j in range(0, hubway.STATIONS):
            differenceGrid[i][j] = ((abs(realGrid[i][j] - createdGrid[i][j])) ** 2)
            sums = ((abs(realGrid[i][j] - createdGrid[i][j])) ** 2) + sums
    return differenceGrid, sums