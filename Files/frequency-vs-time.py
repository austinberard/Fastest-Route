#!/usr/bin/env python3

__author__ = 'Austin'
from collections import defaultdict
import csv
from datetime import datetime
import gzip
import matplotlib.pyplot as plt
import numpy as np
import os
from scipy.interpolate import spline

last_date = None
last_day = None


def dayNum(date):
    global last_date
    global last_day
    date_time = date.split(" ")
    if date_time[0] == last_date:
        return last_day

    dt = datetime.strptime(date_time[0], "%m/%d/%Y")
    last_date = date_time[0]
    last_day = dt.timetuple().tm_yday
    return last_day

temps = [29, 21, 16, 30, 35, 36, 34, 37, 37, 41, 36, 41, 46, 52, 39, 33, 36, 25, 37, 42, 27, 20, 13, 13, 17, 19, 23, 26, 31, 47, 46, # jan
         29, 25, 25, 27, 25, 33, 24, 27, 18, 26, 33, 40, 36, 37, 39, 35, 25, 25, 36, 35, 29, 32, 35, 34, 35, 35, 39, 39,
         38, 38, 38, 36, 38, 38, 34, 35, 35, 33, 43, 46, 45, 31, 31, 35, 32, 27, 32, 33, 33, 35, 37, 41, 39, 42, 46, 43, 48, 47, 47, # mar
         49, 37, 39, 44, 48, 40, 43, 55, 59, 50, 46, 41, 44, 49, 44, 52, 57, 54, 64, 55, 44, 43, 42, 56, 57, 48, 49, 54, 58, 54,
         53, 53, 49, 48, 47, 49, 60, 60, 58, 63, 66, 62, 53, 52, 56, 68, 62, 59, 57, 69, 59, 56, 65, 61, 48, 51, 60, 58, 64, 77, 83, # may
         81, 78, 70, 64, 65, 63, 57, 67, 71, 64, 60, 64, 60, 64, 71, 69, 75, 65, 65, 68, 73, 75, 79, 83, 81, 74, 64, 72, 77, 77,
         78, 72, 77, 85, 87, 86, 84, 76, 69, 77, 78, 70, 69, 81, 83, 84, 84, 84, 89, 88, 74, 72, 75, 77, 63, 67, 73, 71, 74, 75, 74, # july
         74, 76, 74, 74, 70, 67, 70, 73, 74, 76, 72, 75, 70, 70, 69, 71, 69, 71, 74, 78, 78, 80, 72, 66, 72, 76, 71, 67, 65, 74, 76,
         75, 75, 75, 73, 64, 62, 68, 67, 62, 68, 83, 78, 69, 63, 64, 60, 52, 63, 63, 63, 67, 64, 58, 58, 58, 59, 62, 62, 57, 58, # sep
         64, 72, 70, 63, 64, 59, 69, 60, 55, 55, 59, 57, 55, 53, 58, 57, 64, 63, 59, 57, 57, 60, 50, 50, 46, 47, 51, 50, 46, 46, 52,
         66, 58, 44, 37, 40, 52, 56, 44, 41, 50, 47, 40, 32, 41, 50, 50, 47, 59, 41, 36, 39, 45, 41, 26, 26, 38, 51, 33, 29, 28, # nov
         41, 39, 43, 40, 47, 46, 37, 30, 37, 33, 28, 23, 23, 21, 31, 25, 19, 28, 35, 42, 48, 45, 37, 34, 22, 29, 32, 38, 39, 32, 20]

dayCount = defaultdict(int)
currentDir = os.getcwd()
filename = currentDir + "/Data/hubway_trips.csv.gz"
with gzip.open(filename, mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[0] == "seq_id":
            continue
        day = dayNum(row[4])
        dayCount[day] += 1

rain = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 0]


days = []
trips = []
noRainTrips = []
rainTrips = []

ts = []
noRainTs = []
rainTs = []

for day, count in dayCount.items():
    days.append(day)
    trips.append(count)
    if rain[day-1] == 0:
        noRainTs.append(temps[day-1])
        noRainTrips.append(count)
    else:
        rainTs.append(temps[day-1])
        rainTrips.append(count)

    # ts.append(temps[day-1])


arrayDays = np.array(days)
arrayTrips = np.array(trips)
arrayTs = np.array(ts)

arrayNoRainTrips = np.array(noRainTrips)
arrayRainTrips = np.array(rainTrips)
arrayNoRainTs = np.array(noRainTs)
arrayRainTs = np.array(rainTs)


daySmooth = np.linspace(arrayDays.min(), arrayDays.max(), 25)
tripSmooth = spline(arrayDays, arrayTrips, daySmooth)

plt.plot(arrayDays, arrayTrips, ".")
plt.plot(daySmooth, tripSmooth)

plt.xlim(0, 365)
plt.ylim(0, arrayTrips.max())
plt.xlabel("Day of Year")
plt.ylabel("Number of Trips")
plt.show()

plt.scatter(arrayNoRainTs, arrayNoRainTrips, color='blue')
plt.scatter(arrayRainTs, arrayRainTrips, color='red')
plt.xlim(0, 100)
plt.ylim(0, (arrayTrips.max() + 100))
plt.xlabel("Day of Year")
plt.ylabel("Number of Trips")
plt.show()
