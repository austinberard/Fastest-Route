#!/usr/bin/env python3
__author__ = 'Austin'

import datetime
import matplotlib.pyplot as plt
import hubway

def grid_for_hour(departure, hour, date):
    grid = hubway.initializeGrid(hubway.STATIONS)
    for stime, sstation, etime, estation in hubway.trips():
        if departure:
            time = stime
        else:
            time = etime
        if time.date() == date and time.timetuple().tm_hour == hour:
            grid[sstation][estation] += 1
        if time.date() > date:
            break
    return grid


def predict_for_hour_using_hourly_data(departure, hour, date):
    f = hour_factor[hour];
    return f * avgHourGrid;

def predict_for_hour_using_weekend_data(departure, hour, date):
    f = dow_factor[hour];
    return f * avgHourGrid;

def predict_for_hour_using_both(departure, hour, date):
    d = dow_factor[hour];
    h = hour_factor[hour];
    return d * h * avgHourGrid;

def square_difference(realGrid, createdGrid):
    differenceGrid = hubway.initializeGrid(hubway.STATIONS)
    sums = 0
    for i in range(0, hubway.STATIONS):
        for j in range(0, hubway.STATIONS):
            err = realGrid[i][j] - createdGrid[i][j];
            differenceGrid[i][j] = err ** 2
            sums += differenceGrid[i][j]
    return differenceGrid, sums


# Compute a tuple with a factor for each hour, indicating its usual percentage

bins = [0] * 24
for stime, sstation, etime, estation in hubway.trips():
    bins[stime.timetuple().tm_hour] += 1
avg = avg(bins)
factors = bins / avg;


if __name__ == "__main__":
    departGrid = hubway.initializeGrid(hubway.STATIONS)
    avgHourGrid = hubway.initializeGrid(hubway.STATIONS)

    for stime, sstation, etime, estation in hubway.trips():
        departGrid[sstation][estation] += 1

    for i in range(0, hubway.STATIONS):
        for j in range(0, hubway.STATIONS):
            avgHourGrid[i][j] = (departGrid[i][j] / (365 * 3 * 24))

    ten = square_difference(avgHourGrid,
                            grid_for_hour(True, 10, datetime.datetime(2012, 8, 4).date()))
    print(ten[1])
    eleven = square_difference(avgHourGrid,
                               grid_for_hour(True, 11, datetime.datetime(2012, 8, 4).date()))
    print(eleven[1])
