#!/usr/bin/env python3
__author__ = 'Austin'

import matplotlib.pyplot as plt
import csv
import gzip


morningGrid = []
eveningGrid = []

STATIONS = 150
for i in range(0, STATIONS):
    morningGrid.append([])
    for j in range(0, STATIONS):
        morningGrid[i].append(0)
for i in range(0, STATIONS):
    eveningGrid.append([])
    for j in range(0, STATIONS):
        eveningGrid[i].append(0)

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

        if hour in range(5, 10):
            morningGrid[start][end] += 1
        if hour in range(16, 20):
            eveningGrid[start][end] += 1


print(morningGrid)
print(eveningGrid)
max = 0
for i in range(0, STATIONS):
    for j in range(0, STATIONS):
        if morningGrid[i][j] > max:
            max = morningGrid[i][j]
        elif eveningGrid[i][j] > max:
            max = eveningGrid[i][j]
print(max)

def darkness(d):
    return str(1-(d/max))

cs = []
pts = []
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
        pts.append([i,j])
        cs.append(darkness(morningGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Morning Usage")
plt.show()




cs = []
pts = []
for i in range(0,STATIONS):
    for j in range(0,STATIONS):
        pts.append([i,j])
        cs.append(darkness(eveningGrid[i][j]))

xs, ys = zip(*pts)

plt.scatter(xs, ys, c = cs, s = 4, edgecolors='none')
plt.xlim(0, 150)
plt.ylim(0, 150)
plt.title("Evening Usage")
plt.show()



