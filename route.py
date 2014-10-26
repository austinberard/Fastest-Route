#!/usr/bin/env python3
__author__ = 'Austin'
import sys
import csv
import random
import math
import simplejson
from urllib.request import urlopen

stations = []
with open("hubway_stations.csv") as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    for rows in readCSV2:
        if rows[0] != 'id':     # Skip first line
            stations.append([float(rows[4]), float(rows[5])])

start = [random.uniform(42.309467, 42.40449),
         random.uniform(-71.035705, -71.146452)]

finish = [random.uniform(42.309467, 42.40449),
          random.uniform(-71.035705, -71.146452)]


def distance_on_unit_sphere(p1, p2):

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
    arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    km = arc * 6371
    return km


def distance(p1, p2):
    lat1 = p1[0]
    lng1 = p1[1]

    lat2 = p2[0]
    lng2 = p2[1]
    dis = math.sqrt(((lat2 - lat1) ** 2) + ((lng2 - lng1) ** 2))
    return dis


def nearest(origin, pts):
    closest = None
    smallest_distance = sys.float_info.max
    for pt in pts:
        d = distance_on_unit_sphere(origin, pt)
        if d < smallest_distance:
            closest = pt
            smallest_distance = d
    return closest


station1 = nearest(start, stations)
station2 = nearest(finish, stations)


def print_information(start, station1, station2, finish):
    print("Walk {0:.2f}km from {1} to {2}, {3}".format(distance_on_unit_sphere(start, station1), start, station1, travel_time(start, station1)))
    print("Bike {0:.2f}km from {1} to {2}, {3}".format(distance_on_unit_sphere(station1, station2), station1, station2, travel_time(station1, station2)))
    print("Walk {0:.2f}km from {1} to {2}, {3}".format(distance_on_unit_sphere(station2, finish), station2, finish, travel_time(station2, finish)))


def travel_time(start, end):
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=" + str(start[0]) + "," + str(start[1]) + "&destination=" + str(end[0]) + "," + str(end[1]) + "&mode=bicycle&key=AIzaSyCG4JPL7D7eLCnOap0mZnc5KCjOz2WXgf0"
    json_obj = urlopen(url)
    data = simplejson.load(json_obj)
    duration = (data['routes'][0]['legs'][0]['duration'])
    return duration['text']


print_information(start, station1, station2, finish)
# print_time(start, station1, station2, finish)



# Then try comparing several routes using sets of start and end stations
#for station1 in startstations:
#    for station2 in endstations:
#        print_directions(start, station1, station2, finish)

