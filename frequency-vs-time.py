#!/usr/bin/env python3

__author__ = 'Austin'
import csv
import datetime
import gzip
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import spline

#Opens the csv
with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=",")
    dates = []

    #appends the start dates to "dates" and splits the month, day, and year
    for row in readCSV:
        date = row[4]
        reformed = date.split(" ")
        times = reformed[0].split("/")

        dates.append(times)

#deletes the first date because it is the label in the csv
del dates[0]

dayCount = {}
dayList = []
number = 0

# Look into command line parsing, to get the year

year = 2012

for i in dates:

    #checks if the year value in the dates is 2013
    if i[2] == str(year):

        #calculates the datetime difference between the given date and the begining of the year
        day = datetime.date(int(i[2]), int(i[0]), int(i[1])) - datetime.date(year, 1, 1)

        #calls the day value of the datetime
        actualDays = day.days

        #creates a list of all the days
        dayList.append(actualDays)

        #checks if the day of the year is in a dictionary
        if actualDays in dayCount:

            #if key is in dictionary, add 1 to the value
            dayCount[actualDays] += 1
        else:
            #if key is not in dictionary set the value to 1
            dayCount[actualDays] = 1
    else:
        pass

x = []
y = []

for key in dayCount.keys():
    x.append(key)
for val in dayCount.values():
    y.append(val)

print(x)
print(y)

arrayX = np.array(x)
arrayY = np.array(y)

xSmooth = np.linspace(arrayX.min(), arrayX.max(), 25)
ySmooth = spline(arrayX, arrayY, xSmooth)

plt.plot(arrayX, arrayY, ".")
plt.plot(xSmooth, ySmooth)

plt.xlim(0, 365)
plt.ylim(0, 6000)

plt.show()