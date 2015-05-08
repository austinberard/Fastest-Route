#!/usr/bin/env python3
__author__ = 'Austin'
import datetime
from flow import *
import sys
import time

# Create training sets and held sets with things like this:
# ./sample.py 100 > samples.txt || python sample.py 10 > samples.txt
# wc -l samples (to find out how many lines) ||  Get-Content C:\Users\Austin\Fastest-Route\samples.txt | Measure-Object -Line
# head -LINES > training-set.txt || (Get-Content C:\Users\Austin\Fastest-Route\samples.txt)[0 .. 364] > training-set.txt
# tail -LINES > held-set.txt || (Get-Content C:\Users\Austin\Fastest-Route\samples.txt)[-1 .. -365] > held-set.txt
# python predict.py training-set.txt held-set.txt
if __name__ == "__main__":
    Start = time.time()
    allFlow = Flow()
    for stime, sstation, etime, estation in hubway.trips():
        allFlow.countStart(sstation)
        allFlow.countEnd(estation)
    avgFlow = allFlow / (365 * 3 * 24)

    DAYS = 50
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
            print(", ".join(str(e) for e in [year, doy, dow, hour, isWkEnd, station, forHour.outgoing(station)]))
    end = time.time()
    print(end-Start)