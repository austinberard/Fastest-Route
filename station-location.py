#!/usr/bin/env python3

__author__ = 'Austin'
import matplotlib.pyplot as plt
import csv
with open("hubway_stations.csv") as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    lng = []
    lat = []

    for rows in readCSV2:
        lngg = rows[5]
        lng.append(lngg)

        latt = rows[4]
        lat.append(latt)

del lng[0]
del lat[0]
print(min(lng))
print(max(lng))
print(min(lat))
print(max(lat))
x = lng
y = lat

# put up the map
width = 800
height = 600;
ne = []
sw = []

def ll_to_xy(pt):
    pct = (pt[0]-ne[0]) / (ne[0]-sw[0])
    y = height * pct
    pct = (pt[1]-ne[1]) / (ne[1]-sw[1])
    x = width * pct
    return [x, y]

pts = map(ll_to_xy, stations)

plt.plot(pts ".")

plt.show()
