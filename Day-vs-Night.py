#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import csv
import gzip
import datetime

grid = []
dayGrid = []
nightGrid = []

STATIONS = 150
for i in range(0, STATIONS):
    dayGrid.append([])
    for j in range(0, STATIONS):
        dayGrid[i].append(0)
for i in range(0, STATIONS):
    nightGrid.append([])
    for j in range(0, STATIONS):
        nightGrid[i].append(0)

with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[5] == "strt_statn":
            continue
        if row[5] == "" or row[7] == "":
            continue
        start = int(row[5])
        end = int(row[7])

        rawDate = row[4]
        betterDate = rawDate.replace(" ", "/")
        bettererDate = betterDate.replace(":", "/")
        date = bettererDate.split("/")

        hour = int(date[3])

        if start > STATIONS or end > STATIONS:
            print("Ouch "+str(start) + " " + str(end))
            exit()

        if hour in range(6, 18):
            dayGrid[start][end] += 1
        if hour in range(18, 24) or hour in range(0, 6):
            nightGrid[start][end] += 1


print(dayGrid)
print(nightGrid)
max = 0
for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        if dayGrid[i][j] > max:
            max = dayGrid[i][j]
        elif nightGrid[i][j] > max:
            max = nightGrid[i][j]
print(max)


diffenceGrid = []
STATIONS = 150
for i in range(0, STATIONS):
    diffenceGrid.append([])
    for j in range(0, STATIONS):
        diffenceGrid[i].append(0)

for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        diffenceGrid[i][j] = abs(dayGrid[i][j] - nightGrid[i][j])


def darkness(d):
    return str(1-(d/max))

cs = []
pts = []
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
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
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
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
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
        pts.append([i,j])
        cs.append(darkness(diffenceGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Differences")
plt.show()



