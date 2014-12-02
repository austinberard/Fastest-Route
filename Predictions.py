#!/usr/bin/env python3
__author__ = 'Austin'
import random
import datetime
import hubway

def realGrid(departure, hour, date):
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
    hourlyGrid = hubway.initializeGrid(hubway.STATIONS)
    f = factorsForHours[hour]
    for i in range(hubway.STATIONS):
        for j in range(hubway.STATIONS):
            hoursFacotred = f * avgGrid[i][j]
            hourlyGrid[i][j] = hoursFacotred
    return hourlyGrid


# def predict_for_hour_using_weekend_data(departure, hour, date):
#     f = dow_factor[hour];
#     return f * avgGrid;
#
# def predict_for_hour_using_both(departure, hour, date):
#     d = dow_factor[hour];
#     h = hour_factor[hour];
#     return d * h * avgGrid;


def square_difference(realGrid, createdGrid):
    differenceGrid = hubway.initializeGrid(hubway.STATIONS)
    sums = 0
    for i in range(0, hubway.STATIONS):
        for j in range(0, hubway.STATIONS):
            err = realGrid[i][j] - createdGrid[i][j]
            differenceGrid[i][j] = abs(err ** 2)
            sums += differenceGrid[i][j]
    return differenceGrid, sums


# Compute a tuple with a factor for each hour, indicating its usual percentage

bins = [0] * 24
for stime, sstation, etime, estation in hubway.trips():
    bins[stime.timetuple().tm_hour] += 1

def average(list):
    sums = 0
    count = 0
    for i in list:
        sums += list[count]
        count += 1
    avg = sums / count
    return avg


avg = average(bins)

factorsForHours = []
for i in range(0, len(bins)):
    factor = bins[i] / avg
    factorsForHours.append(factor)

if __name__ == "__main__":
    departGrid = hubway.initializeGrid(hubway.STATIONS)
    avgGrid = hubway.initializeGrid(hubway.STATIONS)

    for stime, sstation, etime, estation in hubway.trips():
        departGrid[sstation][estation] += 1

    for i in range(0, hubway.STATIONS):
        for j in range(0, hubway.STATIONS):
            avgGrid[i][j] = (departGrid[i][j] / (365 * 3 * 24))

    randYear = random.randint(2011, 2013)
    randMonth = random.randint(1, 12)
    randDay = random.randint(1, 28)
    randHour = random.randint(0, 24)
    rand1 = square_difference(avgGrid,
                     realGrid(True, randHour, datetime.datetime(randYear, randMonth, randDay).date()))
    rand2 = square_difference(predict_for_hour_using_hourly_data(True, randHour, datetime.datetime(randYear, randMonth, randDay).date()),
                                                        realGrid(True, randHour, datetime.datetime(randYear, randMonth, randDay).date()))
    print("The date was " + str(randMonth) + "/" + str(randDay) + "/" + str(randYear) + " at the hour of " + str(randHour) + " , which had an error of " + str(rand1[1]) + " which uses the avgGrid")
    print("The date was " + str(randMonth) + "/" + str(randDay) + "/" + str(randYear) + " at the hour of " + str(randHour) + " , which had an error of " + str(rand2[1]) + " which uses the hour data")
