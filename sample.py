#!/usr/bin/env python3
__author__ = 'Austin'

import datetime
import hubway
from itertools import zip_longest, starmap
import operator
import csv
import hubway
import random
import time

from flow import *

# Create training sets and held sets with things like this:
# ./sample.py 100 > samples.txt
# wc -l samples (to find out how many lines)
# head -LINES > train-set.txt
# tail -LINES > held-set.txt

if __name__ == "__main__":
    allFlow = Flow()
    for stime, sstation, etime, estation in hubway.trips():
        allFlow.countStart(sstation)
        allFlow.countEnd(estation)
    avgFlow = allFlow / (365 * 3 * 24)

    DAYS = 5
    sample_trips = random.sample(hubway.trips(), DAYS)

    for trip in sample_trips:
        dt = trip[0]

        year = dt.year
        doy = dt.timetuple().tm_yday
        dow = dt.weekday()
        hour = dt.hour
        isWkEnd = 1 if weekend(dt) else 0

        forHour = Flow.forHour(dt)
        for station, value in enumerate(allFlow.outbound):
            print(", ".join([str(e) for e in [year, doy, dow, hour, isWkEnd, station, forHour.outgoing(station)]]))


