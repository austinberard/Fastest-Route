#!/usr/bin/env python3
import matplotlib.pyplot as plt
import csv
import gzip
import datetime
import os

__author__ = 'Austin'

grid = []
weekGrid = []
weekendGrid = []

STATIONS = 150
for i in range(0, STATIONS):
    weekGrid.append([])
    for j in range(0, STATIONS):
        weekGrid[i].append(0)
for l in range(0, STATIONS):
    weekendGrid.append([])
    for m in range(0, STATIONS):
        weekendGrid[l].append(0)

currentDir = os.getcwd()
filename = currentDir + "/Data/hubway_trips.csv.gz"

with gzip.open(filename, mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[5] == "strt_statn":
            continue
        if row[5] == "" or row[7] == "":
            continue
        start = int(row[5])
        end = int(row[7])

        rawDate = row[4]
        betterDate = rawDate.replace(" ", "/")
        date = betterDate.split("/")

        if start > STATIONS or end > STATIONS:
            print("Ouch "+str(start) + " " + str(end))
            exit()

        dates = datetime.datetime(int(date[2]), int(date[0]), int(date[1]))
        if dates.isoweekday() < 6:
            weekGrid[start][end] += 1
        elif dates.isoweekday() > 5:
            weekendGrid[start][end] += 1

print(weekendGrid)
print(weekGrid)
MAX = 0
for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        if weekGrid[i][j] > MAX:
            MAX = weekGrid[i][j]
        elif weekendGrid[i][j] > MAX:
            MAX = weekendGrid[i][j]
print(MAX)


differenceGrid = []
STATIONS = 150
for i in range(0, STATIONS):
    differenceGrid.append([])
    for j in range(0, STATIONS):
        differenceGrid[i].append(0)

for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        differenceGrid[i][j] = abs(weekGrid[i][j] - weekendGrid[i][j])


def darkness(d):
    return str(1-(d/max))

cs = []
pts = []
for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        pts.append([i, j])
        cs.append(darkness(weekGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c=cs, s=4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Week Day Trips")
plt.show()


cs = []
pts = []

for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        pts.append([i, j])
        cs.append(darkness(weekendGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c=cs, s=4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Weekend Trips")
plt.show()


for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        pts.append([i, j])
        cs.append(darkness(differenceGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c=cs, s=4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Differences")
plt.show()
