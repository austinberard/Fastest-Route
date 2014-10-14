#!/usr/bin/env python3
__author__ = 'Austin'
import sys
import csv
import random
import math

stations = []
with open("hubway_stations.csv") as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    for rows in readCSV2:
        if rows[0] != 'id':     # Skip first line
            stations.append([float(rows[4]), float(rows[5])])
print(stations)

start = [random.uniform(42.309467, 42.40449),
         random.uniform(-71.035705, -71.146452)]
         

finish = [random.uniform(42.309467, 42.40449),
          random.uniform(-71.035705, -71.146452)]
          


def distance(p1, p2):
    lat1 = p1[0]
    lng1 = p1[1]

    lat2 = p2[0]
    lng2 = p2[1]
    dis = math.sqrt(((lat2 - lat1) ** 2) + ((lng2 - lng1) ** 2))
    return dis

distance([42.33363229107746, -71.06051998544072],
         [42.340575044581286, -71.10821497085833])

distance(start, finish)

def NearestStartStation(origin, sts):
    closest = None
    smallest_distance = sys.float_info.max
    for pt in sts:
        d = distance(origin, pt)
        if d < smallest_distance:
            closest = pt
            smallest_distance = d
    return closest



nearest = NearestStartStation(start, stations)
print('The closest station to %s is %s' % (start, nearest))
