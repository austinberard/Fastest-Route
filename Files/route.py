#!/usr/bin/env python3
__author__ = 'Austin'
import sys
import csv
import random
import math
import simplejson
from urllib.request import urlopen
import GoogleDirections
import datetime
import os

random.seed(a=1234)
# Input something like 42.3426261192002 -71.095690425241 42.36551399422333 -71.11044709619608
try:
    start1 = float(sys.argv[1])
    start2 = float(sys.argv[2])
    finish1 = float(sys.argv[3])
    finish2 = float(sys.argv[4])

    start = [start1, start2]
    finish = [finish1, finish2]
except IndexError:
    start = [random.uniform(42.309467, 42.40449),
             random.uniform(-71.035705, -71.146452)]

    finish = [random.uniform(42.309467, 42.40449),
              random.uniform(-71.035705, -71.146452)]

stations = []
currentDir = os.getcwd()
filename = currentDir + "/Data/hubway_stations.csv"
with open(filename) as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter=",")
    for rows in readCSV2:
        if rows[0] != 'id':     # Skip first line
            stations.append([float(rows[4]), float(rows[5])])


def distance_on_earth(p1, p2):

    lat1 = p1[0]
    lng1 = p1[1]

    lat2 = p2[0]
    lng2 = p2[1]

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = lng1*degrees_to_radians
    theta2 = lng2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    km = arc * 6371
    return km


def nearest(origin, pts):
    closest = None
    smallest_distance = sys.float_info.max
    for pt in pts:
        d = distance_on_earth(origin, pt)
        if d < smallest_distance:
            closest = pt
            smallest_distance = d
    return closest


station1 = nearest(start, stations)
station2 = nearest(finish, stations)


def print_information(start, station1, station2, finish):
    print("Utilizing Hubway: \n")
    print("Walk {0:.2f}km from {1} to {2}, {3} seconds"
          .format(distance_on_earth(start, station1),
                  start, station1, travel_time(start, station1, "walking")))
    print(GoogleDirections.Directions("{!s},{!s}".format(start[0], start[1]),
                                     "{!s},{!s}".format(station1[0], station1[1]), "walking"))
    print("\n")
    print("Bike {0:.2f}km from {1} to {2}, {3} seconds".format(distance_on_earth(station1, station2), station1, station2, travel_time(station1, station2, "bicycle")))
    print(GoogleDirections.Directions("{!s},{!s}".format(station1[0], station1[1]), "{!s},{!s}".format(station2[0], station2[1]), "bicycle"))
    print("\n")
    print("Walk {0:.2f}km from {1} to {2}, {3} seconds".format(distance_on_earth(station2, finish), station2, finish, travel_time(station2, finish, "walking")))
    print(GoogleDirections.Directions("{!s},{!s}".format(station2[0], station2[1]), "{!s},{!s}".format(finish[0], finish[1]), "walking"))
    print("\n")
    print("Without Hubway total time is: {} seconds".format(timeWithout))
    print("With Hubway total time is: {} seconds".format(timeWith))
    print("Time saved: {}".format(timeSaved))


def travel_time(start, end, mode):
    url = "https://maps.googleapis.com/maps/api/directions/json?origin={!s},{!s}&destination={!s},{!s}&mode={}&key=AIzaSyCG4JPL7D7eLCnOap0mZnc5KCjOz2WXgf0".format(start[0], start[1], end[0], end[1], mode)
    json_obj = urlopen(url)
    data = simplejson.load(json_obj)
    duration = (data['routes'][0]['legs'][0]['duration'])
    return int(duration['value'])

timeWithoutSeconds = travel_time(start, finish, "walking")
timeWithout = datetime.timedelta(seconds=timeWithoutSeconds)
timeWithSeconds = travel_time(start, station1, "walking") +\
                  travel_time(station1, station2, "bicycle") +\
                  travel_time(station2, finish, "walking")
timeWith = datetime.timedelta(seconds=timeWithSeconds)
timeSaved = datetime.timedelta(seconds=timeWithoutSeconds-timeWithSeconds)
print_information(start, station1, station2, finish)


# Then try comparing several routes using sets of start and end stations
# for station1 in startstations:
#    for station2 in endstations:
#        print_directions(start, station1, station2, finish)
