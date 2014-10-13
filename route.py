__author__ = 'Austin'
import csv
import random
import math

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

# print(lng)
# print(lat)
#
# print(min(lng))
# print(max(lng))
# print(min(lat))
# print(max(lat))


startLocation = []
finishLocation = []

startLng = random.uniform(-71.035705, -71.146452)
startLat = random.uniform(42.309467, 42.40449)

startLocation.append(startLng)
startLocation.append(startLat)

finishLng = random.uniform(-71.035705, -71.146452)
finishLat = random.uniform(42.309467, 42.40449)

finishLocation.append(finishLng)
finishLocation.append(finishLat)


print(startLocation)
print(finishLocation)


def distance(x1, y1, x2, y2):
    xs = (abs(x2 - x1)) ** 2
    ys = (abs(y2 - y1)) ** 2

    xPlusy = xs + ys

    dist = math.sqrt(xPlusy)

    print(dist)

distance(-71.06051998544072, 42.33363229107746, -71.10821497085833, 42.340575044581286)

distance(startLocation[0], startLocation[1], finishLocation[0], finishLocation[1])

j = 0

def NearestStartStation(x, y):
    for i in lng:
        global j
        j+=1
        print(i)
        print(j)

NearestStartStation(-71.06051998544072, 42.33363229107746)
