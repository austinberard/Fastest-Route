#!/usr/bin/env python3
__author__ = 'Austin'

import datetime
import hubway
from itertools import zip_longest, starmap
import operator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import csv
from scipy.ndimage import imread
import hubway
import random
import time
start_time = time.time()

from sklearn import linear_model
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier

def average(l):
    return sum(l) / len(l)


def normalize(l):
    avg = average(l)
    return [x/avg for x in l]


def poserror(l1, l2):
    return sum(l1)-sum(l2)


def sqerror(l1, l2):
    return sum(map(lambda p: (p[0]-p[1])**2,
                   zip_longest(l1, l2, fillvalue=0)))

def weekend(dt):
    dow = dt.weekday()
    return dow == 5 or dow == 6

class Flow:
    def __init__(self, inb=None, outb=None):
        if inb is None:
            inb = []
        self.inbound = inb

        if outb is None:
            outb = []
        self.outbound = outb
        assert len(self.inbound) == len(self.outbound)

    def ensure(self, n):
        l = len(self.inbound)
        if l < n + 1:
            tail = [0] * (1+n-l)
            self.inbound.extend(tail)
            self.outbound.extend(tail)

    def countStart(self, station):
        self.ensure(station)
        self.outbound[station] += 1

    def countEnd(self, station):
        self.ensure(station)
        self.inbound[station] += 1

    @classmethod
    def forHour(cls, dt):
        flow = Flow()
        day = dt.date()
        last = dt + datetime.timedelta(hours=1)
        for stime, sstation, etime, estation in hubway.trips():
            if stime.date() == day and stime.timetuple().tm_hour == dt.hour:
                flow.countStart(sstation)
            if etime.date() == day and etime.timetuple().tm_hour == dt.hour:
                flow.countEnd(estation)
            if stime > last:
                break
        return flow

    def outgoing(self, station):
        if station >= len(self.outbound):
            return 0
        return self.outbound[station]
    def incoming(self, station):
        if station >= len(self.inbound):
            return 0
        return self.inbound[station]


    def __repr__(self):
        return repr(list(zip(self.inbound, self.outbound)))

    # With these you can add, say, all of the hourly flows for a day
    # up to get the flow for the whole day.

    def __add__(self, other):
        return Flow(list(starmap(operator.add,
                                 zip_longest(self.inbound, other.inbound,
                                             fillvalue=0))),
                    list(starmap(operator.add,
                                 zip_longest(self.outbound, other.outbound,
                                             fillvalue=0)))),
    def __iadd__(self, other):
        self.inbound = list(starmap(operator.add,
                                    zip_longest(self.inbound, other.inbound,
                                                fillvalue=0)))
        self.outbound = list(starmap(operator.add,
                                     zip_longest(self.outbound, other.outbound,
                                                 fillvalue=0)))
        return self
    def __sub__(self, other):
        return Flow(list(map(operator.sub, self.inbound, other.inbound)),
                    list(map(operator.sub, self.outbound, other.outbound)))
    def __isub__(self, other):
        self.inbound = list(map(operator.sub, self.inbound, other.inbound))
        self.outbound = list(map(operator.sub, self.outbound, other.outbound))
        return self

    # Multiplication and division are defined for element-wise
    # modification by a scalar, not for Flow * Flow.

    def __mul__(self, factor):
        return Flow([x * factor for x in self.inbound],
                    [x * factor for x in self.outbound])
    def __rmul__(self, factor):
        return self * factor
    def __imul__(self, factor):
        self.inbound = [x * factor for x in self.inbound]
        self.outbound = [x * factor for x in self.outbound]
        return self
    def __truediv__(self, factor):
        return Flow([x / factor for x in self.inbound],
                    [x / factor for x in self.outbound])
    def __itruediv__(self, factor):
        self.inbound = [x / factor for x in self.inbound]
        self.outbound = [x / factor for x in self.outbound]
        return self

    def errors(f1, f2):
        sq = sqerror(f1.inbound, f2.inbound) + \
            sqerror(f1.outbound, f2.outbound)
        pos = poserror(f1.inbound, f2.inbound) + \
            poserror(f1.outbound, f2.outbound)
        return sq, pos

class FactorModel:
    def fit(self, samples, results):
        pass

    def predict(sample):
        return predict_for_hour_using_all(datetime.datetime(sample))



if __name__ == "__main__":
    monthBins = [0] * 12
    hourBins = [0] * 24
    weekdayBins = [0] * 24
    weekendBins = [0] * 24
    yearBins = [0] * 3
    for stime, sstation, etime, estation in hubway.trips():
        hr = stime.timetuple().tm_hour
        hourBins[hr] += 1
        if weekend(stime):
            weekendBins[hr] += 1
        else:
            weekdayBins[hr] += 1
        m = stime.timetuple().tm_mon - 1
        monthBins[m] += 1
        y = stime.timetuple().tm_year - 2011
        yearBins[y] += 1


    factorsForMonth = normalize(monthBins)
    factorsForHour = normalize(hourBins)
    factorsForHourOnWeekdays = normalize(weekdayBins)
    factorsForHourOnWeekend = normalize(weekendBins)
    factorsForYear = normalize(yearBins)
    # print(factorsForMonth)
    # print(factorsForHour)
    # print(factorsForHourOnWeekdays)
    # print(factorsForHourOnWeekend)
    # print(factorsForYear)


    allFlow = Flow()
    for stime, sstation, etime, estation in hubway.trips():
        allFlow.countStart(sstation)
        allFlow.countEnd(estation)
    avgFlow = allFlow / (365 * 3 * 24)

    def predict_for_hour_using_hourly_data(dt):
        f = factorsForHour[dt.hour]
        print("Multiplying by "+str(f)+" because in hour "+str(dt.hour))
        return avgFlow * f

    # This seems like a nice, simple way to make predictions, but would
    # probably work poorly, because weekend usage has a different "shape"
    # than weekdays, rather than simply being related by a factor.

    # def predict_for_hour_using_all(departure, dt):
    #     d = factorsForDow[dt.weekday()];
    #     h = factorsForHour[dt.hour];
    #     m = factorsForMonth[dt.month-1];
    #     return m * d * h * avgFlow;

    def predict_for_hour_using_all(dt):
        factors = factorsForHourOnWeekdays
        if weekend(dt):
            factors = factorsForHourOnWeekend

        f = factors[dt.hour] * factorsForMonth[dt.month-1] * factorsForYear[dt.year-2011]

        print("Multiplying by {:.2f} for {} ({})"\
                  .format(f, dt, "Weekend" if weekend(dt) else "Weekday"))
        return avgFlow * f

    def compare(real, prediction):
        errs1 = real.errors(avgFlow)
        errs2 = real.errors(prediction)
        print(" Improvement {:.2f} {:.0f}% {:.2f} {:.0f}%"\
              .format(errs1[0]-errs2[0],
                      100 * (errs1[0]-errs2[0]) / errs1[0],
                      abs(errs1[1])-abs(errs2[1]),
                      100 * (abs(errs1[1])-abs(errs2[1])) / abs(errs1[1])
                  ))

    SAMPLES = 10
    sample_trips = random.sample(hubway.trips(), SAMPLES)
    print("testtstetststettstettsts")
    print(sample_trips)
    samples = []
    results = []

    print(allFlow.outbound)

    for trip in sample_trips:
        dt = trip[0]

        year = dt.year
        doy = dt.timetuple().tm_yday
        dow = dt.weekday()
        hour = dt.hour
        isWkEnd = weekend(dt)

        for station, value in enumerate(allFlow.outbound):
            print("%s, %s, %s, %s, %s, %s : %s" %
                 (year, doy, dow, hour, isWkEnd, station, Flow.forHour(dt).outgoing(station)))
            samples.append([year, doy, dow, hour, isWkEnd, station])
            results.append(Flow.forHour(dt).outgoing(station))
    print(len(samples))

    # test_samples = samples[0:len(samples)//2]
    # held_samples = samples[len(samples)//2:]
    test_samples = [[2012, 93, 0, 7, False, 0], [2012, 93, 0, 7, False, 1], [2012, 93, 0, 7, False, 2], [2012, 93, 0, 7, False, 3], [2012, 93, 0, 7, False, 4], [2012, 93, 0, 7, False, 5], [2012, 93, 0, 7, False, 6], [2012, 93, 0, 7, False, 7], [2012, 93, 0, 7, False, 8], [2012, 93, 0, 7, False, 9], [2012, 93, 0, 7, False, 10], [2012, 93, 0, 7, False, 11], [2012, 93, 0, 7, False, 12], [2012, 93, 0, 7, False, 13], [2012, 93, 0, 7, False, 14], [2012, 93, 0, 7, False, 15], [2012, 93, 0, 7, False, 16], [2012, 93, 0, 7, False, 17], [2012, 93, 0, 7, False, 18], [2012, 93, 0, 7, False, 19], [2012, 93, 0, 7, False, 20], [2012, 93, 0, 7, False, 21], [2012, 93, 0, 7, False, 22], [2012, 93, 0, 7, False, 23], [2012, 93, 0, 7, False, 24], [2012, 93, 0, 7, False, 25], [2012, 93, 0, 7, False, 26], [2012, 93, 0, 7, False, 27], [2012, 93, 0, 7, False, 28], [2012, 93, 0, 7, False, 29], [2012, 93, 0, 7, False, 30], [2012, 93, 0, 7, False, 31], [2012, 93, 0, 7, False, 32], [2012, 93, 0, 7, False, 33], [2012, 93, 0, 7, False, 34], [2012, 93, 0, 7, False, 35], [2012, 93, 0, 7, False, 36], [2012, 93, 0, 7, False, 37], [2012, 93, 0, 7, False, 38], [2012, 93, 0, 7, False, 39], [2012, 93, 0, 7, False, 40], [2012, 93, 0, 7, False, 41], [2012, 93, 0, 7, False, 42], [2012, 93, 0, 7, False, 43], [2012, 93, 0, 7, False, 44], [2012, 93, 0, 7, False, 45], [2012, 93, 0, 7, False, 46], [2012, 93, 0, 7, False, 47], [2012, 93, 0, 7, False, 48], [2012, 93, 0, 7, False, 49], [2012, 93, 0, 7, False, 50], [2012, 93, 0, 7, False, 51], [2012, 93, 0, 7, False, 52], [2012, 93, 0, 7, False, 53], [2012, 93, 0, 7, False, 54], [2012, 93, 0, 7, False, 55], [2012, 93, 0, 7, False, 56], [2012, 93, 0, 7, False, 57], [2012, 93, 0, 7, False, 58], [2012, 93, 0, 7, False, 59], [2012, 93, 0, 7, False, 60], [2012, 93, 0, 7, False, 61], [2012, 93, 0, 7, False, 62], [2012, 93, 0, 7, False, 63], [2012, 93, 0, 7, False, 64], [2012, 93, 0, 7, False, 65], [2012, 93, 0, 7, False, 66], [2012, 93, 0, 7, False, 67], [2012, 93, 0, 7, False, 68], [2012, 93, 0, 7, False, 69], [2012, 93, 0, 7, False, 70], [2012, 93, 0, 7, False, 71], [2012, 93, 0, 7, False, 72], [2012, 93, 0, 7, False, 73], [2012, 93, 0, 7, False, 74], [2012, 93, 0, 7, False, 75], [2012, 93, 0, 7, False, 76], [2012, 93, 0, 7, False, 77], [2012, 93, 0, 7, False, 78], [2012, 93, 0, 7, False, 79], [2012, 93, 0, 7, False, 80], [2012, 93, 0, 7, False, 81], [2012, 93, 0, 7, False, 82], [2012, 93, 0, 7, False, 83], [2012, 93, 0, 7, False, 84], [2012, 93, 0, 7, False, 85], [2012, 93, 0, 7, False, 86], [2012, 93, 0, 7, False, 87], [2012, 93, 0, 7, False, 88], [2012, 93, 0, 7, False, 89], [2012, 93, 0, 7, False, 90], [2012, 93, 0, 7, False, 91], [2012, 93, 0, 7, False, 92], [2012, 93, 0, 7, False, 93], [2012, 93, 0, 7, False, 94], [2012, 93, 0, 7, False, 95], [2012, 93, 0, 7, False, 96], [2012, 93, 0, 7, False, 97], [2012, 93, 0, 7, False, 98], [2012, 93, 0, 7, False, 99], [2012, 93, 0, 7, False, 100], [2012, 93, 0, 7, False, 101], [2012, 93, 0, 7, False, 102], [2012, 93, 0, 7, False, 103], [2012, 93, 0, 7, False, 104], [2012, 93, 0, 7, False, 105], [2012, 93, 0, 7, False, 106], [2012, 93, 0, 7, False, 107], [2012, 93, 0, 7, False, 108], [2012, 93, 0, 7, False, 109], [2012, 93, 0, 7, False, 110], [2012, 93, 0, 7, False, 111], [2012, 93, 0, 7, False, 112], [2012, 93, 0, 7, False, 113], [2012, 93, 0, 7, False, 114], [2012, 93, 0, 7, False, 115], [2012, 93, 0, 7, False, 116], [2012, 93, 0, 7, False, 117], [2012, 93, 0, 7, False, 118], [2012, 93, 0, 7, False, 119], [2012, 93, 0, 7, False, 120], [2012, 93, 0, 7, False, 121], [2012, 93, 0, 7, False, 122], [2012, 93, 0, 7, False, 123], [2012, 93, 0, 7, False, 124], [2012, 93, 0, 7, False, 125], [2012, 93, 0, 7, False, 126], [2012, 93, 0, 7, False, 127], [2012, 93, 0, 7, False, 128], [2012, 93, 0, 7, False, 129], [2012, 93, 0, 7, False, 130], [2012, 93, 0, 7, False, 131], [2012, 93, 0, 7, False, 132], [2012, 93, 0, 7, False, 133], [2012, 93, 0, 7, False, 134], [2012, 93, 0, 7, False, 135], [2012, 93, 0, 7, False, 136], [2012, 93, 0, 7, False, 137], [2012, 93, 0, 7, False, 138], [2012, 93, 0, 7, False, 139], [2012, 93, 0, 7, False, 140], [2012, 93, 0, 7, False, 141], [2012, 93, 0, 7, False, 142], [2012, 93, 0, 7, False, 143], [2012, 93, 0, 7, False, 144], [2012, 93, 0, 7, False, 145], [2013, 195, 6, 16, True, 0], [2013, 195, 6, 16, True, 1], [2013, 195, 6, 16, True, 2], [2013, 195, 6, 16, True, 3], [2013, 195, 6, 16, True, 4], [2013, 195, 6, 16, True, 5], [2013, 195, 6, 16, True, 6], [2013, 195, 6, 16, True, 7], [2013, 195, 6, 16, True, 8], [2013, 195, 6, 16, True, 9], [2013, 195, 6, 16, True, 10], [2013, 195, 6, 16, True, 11], [2013, 195, 6, 16, True, 12], [2013, 195, 6, 16, True, 13], [2013, 195, 6, 16, True, 14], [2013, 195, 6, 16, True, 15], [2013, 195, 6, 16, True, 16], [2013, 195, 6, 16, True, 17], [2013, 195, 6, 16, True, 18], [2013, 195, 6, 16, True, 19], [2013, 195, 6, 16, True, 20], [2013, 195, 6, 16, True, 21], [2013, 195, 6, 16, True, 22], [2013, 195, 6, 16, True, 23], [2013, 195, 6, 16, True, 24], [2013, 195, 6, 16, True, 25], [2013, 195, 6, 16, True, 26], [2013, 195, 6, 16, True, 27], [2013, 195, 6, 16, True, 28], [2013, 195, 6, 16, True, 29], [2013, 195, 6, 16, True, 30], [2013, 195, 6, 16, True, 31], [2013, 195, 6, 16, True, 32], [2013, 195, 6, 16, True, 33], [2013, 195, 6, 16, True, 34], [2013, 195, 6, 16, True, 35], [2013, 195, 6, 16, True, 36], [2013, 195, 6, 16, True, 37], [2013, 195, 6, 16, True, 38], [2013, 195, 6, 16, True, 39], [2013, 195, 6, 16, True, 40], [2013, 195, 6, 16, True, 41], [2013, 195, 6, 16, True, 42], [2013, 195, 6, 16, True, 43], [2013, 195, 6, 16, True, 44], [2013, 195, 6, 16, True, 45], [2013, 195, 6, 16, True, 46], [2013, 195, 6, 16, True, 47], [2013, 195, 6, 16, True, 48], [2013, 195, 6, 16, True, 49], [2013, 195, 6, 16, True, 50], [2013, 195, 6, 16, True, 51], [2013, 195, 6, 16, True, 52], [2013, 195, 6, 16, True, 53], [2013, 195, 6, 16, True, 54], [2013, 195, 6, 16, True, 55], [2013, 195, 6, 16, True, 56], [2013, 195, 6, 16, True, 57], [2013, 195, 6, 16, True, 58], [2013, 195, 6, 16, True, 59], [2013, 195, 6, 16, True, 60], [2013, 195, 6, 16, True, 61], [2013, 195, 6, 16, True, 62], [2013, 195, 6, 16, True, 63], [2013, 195, 6, 16, True, 64], [2013, 195, 6, 16, True, 65], [2013, 195, 6, 16, True, 66], [2013, 195, 6, 16, True, 67], [2013, 195, 6, 16, True, 68], [2013, 195, 6, 16, True, 69], [2013, 195, 6, 16, True, 70], [2013, 195, 6, 16, True, 71], [2013, 195, 6, 16, True, 72], [2013, 195, 6, 16, True, 73], [2013, 195, 6, 16, True, 74], [2013, 195, 6, 16, True, 75], [2013, 195, 6, 16, True, 76], [2013, 195, 6, 16, True, 77], [2013, 195, 6, 16, True, 78], [2013, 195, 6, 16, True, 79], [2013, 195, 6, 16, True, 80], [2013, 195, 6, 16, True, 81], [2013, 195, 6, 16, True, 82], [2013, 195, 6, 16, True, 83], [2013, 195, 6, 16, True, 84], [2013, 195, 6, 16, True, 85], [2013, 195, 6, 16, True, 86], [2013, 195, 6, 16, True, 87], [2013, 195, 6, 16, True, 88], [2013, 195, 6, 16, True, 89], [2013, 195, 6, 16, True, 90], [2013, 195, 6, 16, True, 91], [2013, 195, 6, 16, True, 92], [2013, 195, 6, 16, True, 93], [2013, 195, 6, 16, True, 94], [2013, 195, 6, 16, True, 95], [2013, 195, 6, 16, True, 96], [2013, 195, 6, 16, True, 97], [2013, 195, 6, 16, True, 98], [2013, 195, 6, 16, True, 99], [2013, 195, 6, 16, True, 100], [2013, 195, 6, 16, True, 101], [2013, 195, 6, 16, True, 102], [2013, 195, 6, 16, True, 103], [2013, 195, 6, 16, True, 104], [2013, 195, 6, 16, True, 105], [2013, 195, 6, 16, True, 106], [2013, 195, 6, 16, True, 107], [2013, 195, 6, 16, True, 108], [2013, 195, 6, 16, True, 109], [2013, 195, 6, 16, True, 110], [2013, 195, 6, 16, True, 111], [2013, 195, 6, 16, True, 112], [2013, 195, 6, 16, True, 113], [2013, 195, 6, 16, True, 114], [2013, 195, 6, 16, True, 115], [2013, 195, 6, 16, True, 116], [2013, 195, 6, 16, True, 117], [2013, 195, 6, 16, True, 118], [2013, 195, 6, 16, True, 119], [2013, 195, 6, 16, True, 120], [2013, 195, 6, 16, True, 121], [2013, 195, 6, 16, True, 122], [2013, 195, 6, 16, True, 123], [2013, 195, 6, 16, True, 124], [2013, 195, 6, 16, True, 125], [2013, 195, 6, 16, True, 126], [2013, 195, 6, 16, True, 127], [2013, 195, 6, 16, True, 128], [2013, 195, 6, 16, True, 129], [2013, 195, 6, 16, True, 130], [2013, 195, 6, 16, True, 131], [2013, 195, 6, 16, True, 132], [2013, 195, 6, 16, True, 133], [2013, 195, 6, 16, True, 134], [2013, 195, 6, 16, True, 135], [2013, 195, 6, 16, True, 136], [2013, 195, 6, 16, True, 137], [2013, 195, 6, 16, True, 138], [2013, 195, 6, 16, True, 139], [2013, 195, 6, 16, True, 140], [2013, 195, 6, 16, True, 141], [2013, 195, 6, 16, True, 142], [2013, 195, 6, 16, True, 143], [2013, 195, 6, 16, True, 144], [2013, 195, 6, 16, True, 145], [2012, 324, 0, 17, False, 0], [2012, 324, 0, 17, False, 1], [2012, 324, 0, 17, False, 2], [2012, 324, 0, 17, False, 3], [2012, 324, 0, 17, False, 4], [2012, 324, 0, 17, False, 5], [2012, 324, 0, 17, False, 6], [2012, 324, 0, 17, False, 7], [2012, 324, 0, 17, False, 8], [2012, 324, 0, 17, False, 9], [2012, 324, 0, 17, False, 10], [2012, 324, 0, 17, False, 11], [2012, 324, 0, 17, False, 12], [2012, 324, 0, 17, False, 13], [2012, 324, 0, 17, False, 14], [2012, 324, 0, 17, False, 15], [2012, 324, 0, 17, False, 16], [2012, 324, 0, 17, False, 17], [2012, 324, 0, 17, False, 18], [2012, 324, 0, 17, False, 19], [2012, 324, 0, 17, False, 20], [2012, 324, 0, 17, False, 21], [2012, 324, 0, 17, False, 22], [2012, 324, 0, 17, False, 23], [2012, 324, 0, 17, False, 24], [2012, 324, 0, 17, False, 25], [2012, 324, 0, 17, False, 26], [2012, 324, 0, 17, False, 27], [2012, 324, 0, 17, False, 28], [2012, 324, 0, 17, False, 29], [2012, 324, 0, 17, False, 30], [2012, 324, 0, 17, False, 31], [2012, 324, 0, 17, False, 32], [2012, 324, 0, 17, False, 33], [2012, 324, 0, 17, False, 34], [2012, 324, 0, 17, False, 35], [2012, 324, 0, 17, False, 36], [2012, 324, 0, 17, False, 37], [2012, 324, 0, 17, False, 38], [2012, 324, 0, 17, False, 39], [2012, 324, 0, 17, False, 40], [2012, 324, 0, 17, False, 41], [2012, 324, 0, 17, False, 42], [2012, 324, 0, 17, False, 43], [2012, 324, 0, 17, False, 44], [2012, 324, 0, 17, False, 45], [2012, 324, 0, 17, False, 46], [2012, 324, 0, 17, False, 47], [2012, 324, 0, 17, False, 48], [2012, 324, 0, 17, False, 49], [2012, 324, 0, 17, False, 50], [2012, 324, 0, 17, False, 51], [2012, 324, 0, 17, False, 52], [2012, 324, 0, 17, False, 53], [2012, 324, 0, 17, False, 54], [2012, 324, 0, 17, False, 55], [2012, 324, 0, 17, False, 56], [2012, 324, 0, 17, False, 57], [2012, 324, 0, 17, False, 58], [2012, 324, 0, 17, False, 59], [2012, 324, 0, 17, False, 60], [2012, 324, 0, 17, False, 61], [2012, 324, 0, 17, False, 62], [2012, 324, 0, 17, False, 63], [2012, 324, 0, 17, False, 64], [2012, 324, 0, 17, False, 65], [2012, 324, 0, 17, False, 66], [2012, 324, 0, 17, False, 67], [2012, 324, 0, 17, False, 68], [2012, 324, 0, 17, False, 69], [2012, 324, 0, 17, False, 70], [2012, 324, 0, 17, False, 71], [2012, 324, 0, 17, False, 72], [2012, 324, 0, 17, False, 73], [2012, 324, 0, 17, False, 74], [2012, 324, 0, 17, False, 75], [2012, 324, 0, 17, False, 76], [2012, 324, 0, 17, False, 77], [2012, 324, 0, 17, False, 78], [2012, 324, 0, 17, False, 79], [2012, 324, 0, 17, False, 80], [2012, 324, 0, 17, False, 81], [2012, 324, 0, 17, False, 82], [2012, 324, 0, 17, False, 83], [2012, 324, 0, 17, False, 84], [2012, 324, 0, 17, False, 85], [2012, 324, 0, 17, False, 86], [2012, 324, 0, 17, False, 87], [2012, 324, 0, 17, False, 88], [2012, 324, 0, 17, False, 89], [2012, 324, 0, 17, False, 90], [2012, 324, 0, 17, False, 91], [2012, 324, 0, 17, False, 92], [2012, 324, 0, 17, False, 93], [2012, 324, 0, 17, False, 94], [2012, 324, 0, 17, False, 95], [2012, 324, 0, 17, False, 96], [2012, 324, 0, 17, False, 97], [2012, 324, 0, 17, False, 98], [2012, 324, 0, 17, False, 99], [2012, 324, 0, 17, False, 100], [2012, 324, 0, 17, False, 101], [2012, 324, 0, 17, False, 102], [2012, 324, 0, 17, False, 103], [2012, 324, 0, 17, False, 104], [2012, 324, 0, 17, False, 105], [2012, 324, 0, 17, False, 106], [2012, 324, 0, 17, False, 107], [2012, 324, 0, 17, False, 108], [2012, 324, 0, 17, False, 109], [2012, 324, 0, 17, False, 110], [2012, 324, 0, 17, False, 111], [2012, 324, 0, 17, False, 112], [2012, 324, 0, 17, False, 113], [2012, 324, 0, 17, False, 114], [2012, 324, 0, 17, False, 115], [2012, 324, 0, 17, False, 116], [2012, 324, 0, 17, False, 117], [2012, 324, 0, 17, False, 118], [2012, 324, 0, 17, False, 119], [2012, 324, 0, 17, False, 120], [2012, 324, 0, 17, False, 121], [2012, 324, 0, 17, False, 122], [2012, 324, 0, 17, False, 123], [2012, 324, 0, 17, False, 124], [2012, 324, 0, 17, False, 125], [2012, 324, 0, 17, False, 126], [2012, 324, 0, 17, False, 127], [2012, 324, 0, 17, False, 128], [2012, 324, 0, 17, False, 129], [2012, 324, 0, 17, False, 130], [2012, 324, 0, 17, False, 131], [2012, 324, 0, 17, False, 132], [2012, 324, 0, 17, False, 133], [2012, 324, 0, 17, False, 134], [2012, 324, 0, 17, False, 135], [2012, 324, 0, 17, False, 136], [2012, 324, 0, 17, False, 137], [2012, 324, 0, 17, False, 138], [2012, 324, 0, 17, False, 139], [2012, 324, 0, 17, False, 140], [2012, 324, 0, 17, False, 141], [2012, 324, 0, 17, False, 142], [2012, 324, 0, 17, False, 143], [2012, 324, 0, 17, False, 144], [2012, 324, 0, 17, False, 145], [2013, 176, 1, 22, False, 0], [2013, 176, 1, 22, False, 1], [2013, 176, 1, 22, False, 2], [2013, 176, 1, 22, False, 3], [2013, 176, 1, 22, False, 4], [2013, 176, 1, 22, False, 5], [2013, 176, 1, 22, False, 6], [2013, 176, 1, 22, False, 7], [2013, 176, 1, 22, False, 8], [2013, 176, 1, 22, False, 9], [2013, 176, 1, 22, False, 10], [2013, 176, 1, 22, False, 11], [2013, 176, 1, 22, False, 12], [2013, 176, 1, 22, False, 13], [2013, 176, 1, 22, False, 14], [2013, 176, 1, 22, False, 15], [2013, 176, 1, 22, False, 16], [2013, 176, 1, 22, False, 17], [2013, 176, 1, 22, False, 18], [2013, 176, 1, 22, False, 19], [2013, 176, 1, 22, False, 20], [2013, 176, 1, 22, False, 21], [2013, 176, 1, 22, False, 22], [2013, 176, 1, 22, False, 23], [2013, 176, 1, 22, False, 24], [2013, 176, 1, 22, False, 25], [2013, 176, 1, 22, False, 26], [2013, 176, 1, 22, False, 27], [2013, 176, 1, 22, False, 28], [2013, 176, 1, 22, False, 29], [2013, 176, 1, 22, False, 30], [2013, 176, 1, 22, False, 31], [2013, 176, 1, 22, False, 32], [2013, 176, 1, 22, False, 33], [2013, 176, 1, 22, False, 34], [2013, 176, 1, 22, False, 35], [2013, 176, 1, 22, False, 36], [2013, 176, 1, 22, False, 37], [2013, 176, 1, 22, False, 38], [2013, 176, 1, 22, False, 39], [2013, 176, 1, 22, False, 40], [2013, 176, 1, 22, False, 41], [2013, 176, 1, 22, False, 42], [2013, 176, 1, 22, False, 43], [2013, 176, 1, 22, False, 44], [2013, 176, 1, 22, False, 45], [2013, 176, 1, 22, False, 46], [2013, 176, 1, 22, False, 47], [2013, 176, 1, 22, False, 48], [2013, 176, 1, 22, False, 49], [2013, 176, 1, 22, False, 50], [2013, 176, 1, 22, False, 51], [2013, 176, 1, 22, False, 52], [2013, 176, 1, 22, False, 53], [2013, 176, 1, 22, False, 54], [2013, 176, 1, 22, False, 55], [2013, 176, 1, 22, False, 56], [2013, 176, 1, 22, False, 57], [2013, 176, 1, 22, False, 58], [2013, 176, 1, 22, False, 59], [2013, 176, 1, 22, False, 60], [2013, 176, 1, 22, False, 61], [2013, 176, 1, 22, False, 62], [2013, 176, 1, 22, False, 63], [2013, 176, 1, 22, False, 64], [2013, 176, 1, 22, False, 65], [2013, 176, 1, 22, False, 66], [2013, 176, 1, 22, False, 67], [2013, 176, 1, 22, False, 68], [2013, 176, 1, 22, False, 69], [2013, 176, 1, 22, False, 70], [2013, 176, 1, 22, False, 71], [2013, 176, 1, 22, False, 72], [2013, 176, 1, 22, False, 73], [2013, 176, 1, 22, False, 74], [2013, 176, 1, 22, False, 75], [2013, 176, 1, 22, False, 76], [2013, 176, 1, 22, False, 77], [2013, 176, 1, 22, False, 78], [2013, 176, 1, 22, False, 79], [2013, 176, 1, 22, False, 80], [2013, 176, 1, 22, False, 81], [2013, 176, 1, 22, False, 82], [2013, 176, 1, 22, False, 83], [2013, 176, 1, 22, False, 84], [2013, 176, 1, 22, False, 85], [2013, 176, 1, 22, False, 86], [2013, 176, 1, 22, False, 87], [2013, 176, 1, 22, False, 88], [2013, 176, 1, 22, False, 89], [2013, 176, 1, 22, False, 90], [2013, 176, 1, 22, False, 91], [2013, 176, 1, 22, False, 92], [2013, 176, 1, 22, False, 93], [2013, 176, 1, 22, False, 94], [2013, 176, 1, 22, False, 95], [2013, 176, 1, 22, False, 96], [2013, 176, 1, 22, False, 97], [2013, 176, 1, 22, False, 98], [2013, 176, 1, 22, False, 99], [2013, 176, 1, 22, False, 100], [2013, 176, 1, 22, False, 101], [2013, 176, 1, 22, False, 102], [2013, 176, 1, 22, False, 103], [2013, 176, 1, 22, False, 104], [2013, 176, 1, 22, False, 105], [2013, 176, 1, 22, False, 106], [2013, 176, 1, 22, False, 107], [2013, 176, 1, 22, False, 108], [2013, 176, 1, 22, False, 109], [2013, 176, 1, 22, False, 110], [2013, 176, 1, 22, False, 111], [2013, 176, 1, 22, False, 112], [2013, 176, 1, 22, False, 113], [2013, 176, 1, 22, False, 114], [2013, 176, 1, 22, False, 115], [2013, 176, 1, 22, False, 116], [2013, 176, 1, 22, False, 117], [2013, 176, 1, 22, False, 118], [2013, 176, 1, 22, False, 119], [2013, 176, 1, 22, False, 120], [2013, 176, 1, 22, False, 121], [2013, 176, 1, 22, False, 122], [2013, 176, 1, 22, False, 123], [2013, 176, 1, 22, False, 124], [2013, 176, 1, 22, False, 125], [2013, 176, 1, 22, False, 126], [2013, 176, 1, 22, False, 127], [2013, 176, 1, 22, False, 128], [2013, 176, 1, 22, False, 129], [2013, 176, 1, 22, False, 130], [2013, 176, 1, 22, False, 131], [2013, 176, 1, 22, False, 132], [2013, 176, 1, 22, False, 133], [2013, 176, 1, 22, False, 134], [2013, 176, 1, 22, False, 135], [2013, 176, 1, 22, False, 136], [2013, 176, 1, 22, False, 137], [2013, 176, 1, 22, False, 138], [2013, 176, 1, 22, False, 139], [2013, 176, 1, 22, False, 140], [2013, 176, 1, 22, False, 141], [2013, 176, 1, 22, False, 142], [2013, 176, 1, 22, False, 143], [2013, 176, 1, 22, False, 144], [2013, 176, 1, 22, False, 145], [2013, 222, 5, 6, True, 0], [2013, 222, 5, 6, True, 1], [2013, 222, 5, 6, True, 2], [2013, 222, 5, 6, True, 3], [2013, 222, 5, 6, True, 4], [2013, 222, 5, 6, True, 5], [2013, 222, 5, 6, True, 6], [2013, 222, 5, 6, True, 7], [2013, 222, 5, 6, True, 8], [2013, 222, 5, 6, True, 9], [2013, 222, 5, 6, True, 10], [2013, 222, 5, 6, True, 11], [2013, 222, 5, 6, True, 12], [2013, 222, 5, 6, True, 13], [2013, 222, 5, 6, True, 14], [2013, 222, 5, 6, True, 15], [2013, 222, 5, 6, True, 16], [2013, 222, 5, 6, True, 17], [2013, 222, 5, 6, True, 18], [2013, 222, 5, 6, True, 19], [2013, 222, 5, 6, True, 20], [2013, 222, 5, 6, True, 21], [2013, 222, 5, 6, True, 22], [2013, 222, 5, 6, True, 23], [2013, 222, 5, 6, True, 24], [2013, 222, 5, 6, True, 25], [2013, 222, 5, 6, True, 26], [2013, 222, 5, 6, True, 27], [2013, 222, 5, 6, True, 28], [2013, 222, 5, 6, True, 29], [2013, 222, 5, 6, True, 30], [2013, 222, 5, 6, True, 31], [2013, 222, 5, 6, True, 32], [2013, 222, 5, 6, True, 33], [2013, 222, 5, 6, True, 34], [2013, 222, 5, 6, True, 35], [2013, 222, 5, 6, True, 36], [2013, 222, 5, 6, True, 37], [2013, 222, 5, 6, True, 38], [2013, 222, 5, 6, True, 39], [2013, 222, 5, 6, True, 40], [2013, 222, 5, 6, True, 41], [2013, 222, 5, 6, True, 42], [2013, 222, 5, 6, True, 43], [2013, 222, 5, 6, True, 44], [2013, 222, 5, 6, True, 45], [2013, 222, 5, 6, True, 46], [2013, 222, 5, 6, True, 47], [2013, 222, 5, 6, True, 48], [2013, 222, 5, 6, True, 49], [2013, 222, 5, 6, True, 50], [2013, 222, 5, 6, True, 51], [2013, 222, 5, 6, True, 52], [2013, 222, 5, 6, True, 53], [2013, 222, 5, 6, True, 54], [2013, 222, 5, 6, True, 55], [2013, 222, 5, 6, True, 56], [2013, 222, 5, 6, True, 57], [2013, 222, 5, 6, True, 58], [2013, 222, 5, 6, True, 59], [2013, 222, 5, 6, True, 60], [2013, 222, 5, 6, True, 61], [2013, 222, 5, 6, True, 62], [2013, 222, 5, 6, True, 63], [2013, 222, 5, 6, True, 64], [2013, 222, 5, 6, True, 65], [2013, 222, 5, 6, True, 66], [2013, 222, 5, 6, True, 67], [2013, 222, 5, 6, True, 68], [2013, 222, 5, 6, True, 69], [2013, 222, 5, 6, True, 70], [2013, 222, 5, 6, True, 71], [2013, 222, 5, 6, True, 72], [2013, 222, 5, 6, True, 73], [2013, 222, 5, 6, True, 74], [2013, 222, 5, 6, True, 75], [2013, 222, 5, 6, True, 76], [2013, 222, 5, 6, True, 77], [2013, 222, 5, 6, True, 78], [2013, 222, 5, 6, True, 79], [2013, 222, 5, 6, True, 80], [2013, 222, 5, 6, True, 81], [2013, 222, 5, 6, True, 82], [2013, 222, 5, 6, True, 83], [2013, 222, 5, 6, True, 84], [2013, 222, 5, 6, True, 85], [2013, 222, 5, 6, True, 86], [2013, 222, 5, 6, True, 87], [2013, 222, 5, 6, True, 88], [2013, 222, 5, 6, True, 89], [2013, 222, 5, 6, True, 90], [2013, 222, 5, 6, True, 91], [2013, 222, 5, 6, True, 92], [2013, 222, 5, 6, True, 93], [2013, 222, 5, 6, True, 94], [2013, 222, 5, 6, True, 95], [2013, 222, 5, 6, True, 96], [2013, 222, 5, 6, True, 97], [2013, 222, 5, 6, True, 98], [2013, 222, 5, 6, True, 99], [2013, 222, 5, 6, True, 100], [2013, 222, 5, 6, True, 101], [2013, 222, 5, 6, True, 102], [2013, 222, 5, 6, True, 103], [2013, 222, 5, 6, True, 104], [2013, 222, 5, 6, True, 105], [2013, 222, 5, 6, True, 106], [2013, 222, 5, 6, True, 107], [2013, 222, 5, 6, True, 108], [2013, 222, 5, 6, True, 109], [2013, 222, 5, 6, True, 110], [2013, 222, 5, 6, True, 111], [2013, 222, 5, 6, True, 112], [2013, 222, 5, 6, True, 113], [2013, 222, 5, 6, True, 114], [2013, 222, 5, 6, True, 115], [2013, 222, 5, 6, True, 116], [2013, 222, 5, 6, True, 117], [2013, 222, 5, 6, True, 118], [2013, 222, 5, 6, True, 119], [2013, 222, 5, 6, True, 120], [2013, 222, 5, 6, True, 121], [2013, 222, 5, 6, True, 122], [2013, 222, 5, 6, True, 123], [2013, 222, 5, 6, True, 124], [2013, 222, 5, 6, True, 125], [2013, 222, 5, 6, True, 126], [2013, 222, 5, 6, True, 127], [2013, 222, 5, 6, True, 128], [2013, 222, 5, 6, True, 129], [2013, 222, 5, 6, True, 130], [2013, 222, 5, 6, True, 131], [2013, 222, 5, 6, True, 132], [2013, 222, 5, 6, True, 133], [2013, 222, 5, 6, True, 134], [2013, 222, 5, 6, True, 135], [2013, 222, 5, 6, True, 136], [2013, 222, 5, 6, True, 137], [2013, 222, 5, 6, True, 138], [2013, 222, 5, 6, True, 139], [2013, 222, 5, 6, True, 140], [2013, 222, 5, 6, True, 141], [2013, 222, 5, 6, True, 142], [2013, 222, 5, 6, True, 143], [2013, 222, 5, 6, True, 144], [2013, 222, 5, 6, True, 145]]
    held_samples = [[2013, 311, 3, 9, False, 0], [2013, 311, 3, 9, False, 1], [2013, 311, 3, 9, False, 2], [2013, 311, 3, 9, False, 3], [2013, 311, 3, 9, False, 4], [2013, 311, 3, 9, False, 5], [2013, 311, 3, 9, False, 6], [2013, 311, 3, 9, False, 7], [2013, 311, 3, 9, False, 8], [2013, 311, 3, 9, False, 9], [2013, 311, 3, 9, False, 10], [2013, 311, 3, 9, False, 11], [2013, 311, 3, 9, False, 12], [2013, 311, 3, 9, False, 13], [2013, 311, 3, 9, False, 14], [2013, 311, 3, 9, False, 15], [2013, 311, 3, 9, False, 16], [2013, 311, 3, 9, False, 17], [2013, 311, 3, 9, False, 18], [2013, 311, 3, 9, False, 19], [2013, 311, 3, 9, False, 20], [2013, 311, 3, 9, False, 21], [2013, 311, 3, 9, False, 22], [2013, 311, 3, 9, False, 23], [2013, 311, 3, 9, False, 24], [2013, 311, 3, 9, False, 25], [2013, 311, 3, 9, False, 26], [2013, 311, 3, 9, False, 27], [2013, 311, 3, 9, False, 28], [2013, 311, 3, 9, False, 29], [2013, 311, 3, 9, False, 30], [2013, 311, 3, 9, False, 31], [2013, 311, 3, 9, False, 32], [2013, 311, 3, 9, False, 33], [2013, 311, 3, 9, False, 34], [2013, 311, 3, 9, False, 35], [2013, 311, 3, 9, False, 36], [2013, 311, 3, 9, False, 37], [2013, 311, 3, 9, False, 38], [2013, 311, 3, 9, False, 39], [2013, 311, 3, 9, False, 40], [2013, 311, 3, 9, False, 41], [2013, 311, 3, 9, False, 42], [2013, 311, 3, 9, False, 43], [2013, 311, 3, 9, False, 44], [2013, 311, 3, 9, False, 45], [2013, 311, 3, 9, False, 46], [2013, 311, 3, 9, False, 47], [2013, 311, 3, 9, False, 48], [2013, 311, 3, 9, False, 49], [2013, 311, 3, 9, False, 50], [2013, 311, 3, 9, False, 51], [2013, 311, 3, 9, False, 52], [2013, 311, 3, 9, False, 53], [2013, 311, 3, 9, False, 54], [2013, 311, 3, 9, False, 55], [2013, 311, 3, 9, False, 56], [2013, 311, 3, 9, False, 57], [2013, 311, 3, 9, False, 58], [2013, 311, 3, 9, False, 59], [2013, 311, 3, 9, False, 60], [2013, 311, 3, 9, False, 61], [2013, 311, 3, 9, False, 62], [2013, 311, 3, 9, False, 63], [2013, 311, 3, 9, False, 64], [2013, 311, 3, 9, False, 65], [2013, 311, 3, 9, False, 66], [2013, 311, 3, 9, False, 67], [2013, 311, 3, 9, False, 68], [2013, 311, 3, 9, False, 69], [2013, 311, 3, 9, False, 70], [2013, 311, 3, 9, False, 71], [2013, 311, 3, 9, False, 72], [2013, 311, 3, 9, False, 73], [2013, 311, 3, 9, False, 74], [2013, 311, 3, 9, False, 75], [2013, 311, 3, 9, False, 76], [2013, 311, 3, 9, False, 77], [2013, 311, 3, 9, False, 78], [2013, 311, 3, 9, False, 79], [2013, 311, 3, 9, False, 80], [2013, 311, 3, 9, False, 81], [2013, 311, 3, 9, False, 82], [2013, 311, 3, 9, False, 83], [2013, 311, 3, 9, False, 84], [2013, 311, 3, 9, False, 85], [2013, 311, 3, 9, False, 86], [2013, 311, 3, 9, False, 87], [2013, 311, 3, 9, False, 88], [2013, 311, 3, 9, False, 89], [2013, 311, 3, 9, False, 90], [2013, 311, 3, 9, False, 91], [2013, 311, 3, 9, False, 92], [2013, 311, 3, 9, False, 93], [2013, 311, 3, 9, False, 94], [2013, 311, 3, 9, False, 95], [2013, 311, 3, 9, False, 96], [2013, 311, 3, 9, False, 97], [2013, 311, 3, 9, False, 98], [2013, 311, 3, 9, False, 99], [2013, 311, 3, 9, False, 100], [2013, 311, 3, 9, False, 101], [2013, 311, 3, 9, False, 102], [2013, 311, 3, 9, False, 103], [2013, 311, 3, 9, False, 104], [2013, 311, 3, 9, False, 105], [2013, 311, 3, 9, False, 106], [2013, 311, 3, 9, False, 107], [2013, 311, 3, 9, False, 108], [2013, 311, 3, 9, False, 109], [2013, 311, 3, 9, False, 110], [2013, 311, 3, 9, False, 111], [2013, 311, 3, 9, False, 112], [2013, 311, 3, 9, False, 113], [2013, 311, 3, 9, False, 114], [2013, 311, 3, 9, False, 115], [2013, 311, 3, 9, False, 116], [2013, 311, 3, 9, False, 117], [2013, 311, 3, 9, False, 118], [2013, 311, 3, 9, False, 119], [2013, 311, 3, 9, False, 120], [2013, 311, 3, 9, False, 121], [2013, 311, 3, 9, False, 122], [2013, 311, 3, 9, False, 123], [2013, 311, 3, 9, False, 124], [2013, 311, 3, 9, False, 125], [2013, 311, 3, 9, False, 126], [2013, 311, 3, 9, False, 127], [2013, 311, 3, 9, False, 128], [2013, 311, 3, 9, False, 129], [2013, 311, 3, 9, False, 130], [2013, 311, 3, 9, False, 131], [2013, 311, 3, 9, False, 132], [2013, 311, 3, 9, False, 133], [2013, 311, 3, 9, False, 134], [2013, 311, 3, 9, False, 135], [2013, 311, 3, 9, False, 136], [2013, 311, 3, 9, False, 137], [2013, 311, 3, 9, False, 138], [2013, 311, 3, 9, False, 139], [2013, 311, 3, 9, False, 140], [2013, 311, 3, 9, False, 141], [2013, 311, 3, 9, False, 142], [2013, 311, 3, 9, False, 143], [2013, 311, 3, 9, False, 144], [2013, 311, 3, 9, False, 145], [2011, 278, 2, 5, False, 0], [2011, 278, 2, 5, False, 1], [2011, 278, 2, 5, False, 2], [2011, 278, 2, 5, False, 3], [2011, 278, 2, 5, False, 4], [2011, 278, 2, 5, False, 5], [2011, 278, 2, 5, False, 6], [2011, 278, 2, 5, False, 7], [2011, 278, 2, 5, False, 8], [2011, 278, 2, 5, False, 9], [2011, 278, 2, 5, False, 10], [2011, 278, 2, 5, False, 11], [2011, 278, 2, 5, False, 12], [2011, 278, 2, 5, False, 13], [2011, 278, 2, 5, False, 14], [2011, 278, 2, 5, False, 15], [2011, 278, 2, 5, False, 16], [2011, 278, 2, 5, False, 17], [2011, 278, 2, 5, False, 18], [2011, 278, 2, 5, False, 19], [2011, 278, 2, 5, False, 20], [2011, 278, 2, 5, False, 21], [2011, 278, 2, 5, False, 22], [2011, 278, 2, 5, False, 23], [2011, 278, 2, 5, False, 24], [2011, 278, 2, 5, False, 25], [2011, 278, 2, 5, False, 26], [2011, 278, 2, 5, False, 27], [2011, 278, 2, 5, False, 28], [2011, 278, 2, 5, False, 29], [2011, 278, 2, 5, False, 30], [2011, 278, 2, 5, False, 31], [2011, 278, 2, 5, False, 32], [2011, 278, 2, 5, False, 33], [2011, 278, 2, 5, False, 34], [2011, 278, 2, 5, False, 35], [2011, 278, 2, 5, False, 36], [2011, 278, 2, 5, False, 37], [2011, 278, 2, 5, False, 38], [2011, 278, 2, 5, False, 39], [2011, 278, 2, 5, False, 40], [2011, 278, 2, 5, False, 41], [2011, 278, 2, 5, False, 42], [2011, 278, 2, 5, False, 43], [2011, 278, 2, 5, False, 44], [2011, 278, 2, 5, False, 45], [2011, 278, 2, 5, False, 46], [2011, 278, 2, 5, False, 47], [2011, 278, 2, 5, False, 48], [2011, 278, 2, 5, False, 49], [2011, 278, 2, 5, False, 50], [2011, 278, 2, 5, False, 51], [2011, 278, 2, 5, False, 52], [2011, 278, 2, 5, False, 53], [2011, 278, 2, 5, False, 54], [2011, 278, 2, 5, False, 55], [2011, 278, 2, 5, False, 56], [2011, 278, 2, 5, False, 57], [2011, 278, 2, 5, False, 58], [2011, 278, 2, 5, False, 59], [2011, 278, 2, 5, False, 60], [2011, 278, 2, 5, False, 61], [2011, 278, 2, 5, False, 62], [2011, 278, 2, 5, False, 63], [2011, 278, 2, 5, False, 64], [2011, 278, 2, 5, False, 65], [2011, 278, 2, 5, False, 66], [2011, 278, 2, 5, False, 67], [2011, 278, 2, 5, False, 68], [2011, 278, 2, 5, False, 69], [2011, 278, 2, 5, False, 70], [2011, 278, 2, 5, False, 71], [2011, 278, 2, 5, False, 72], [2011, 278, 2, 5, False, 73], [2011, 278, 2, 5, False, 74], [2011, 278, 2, 5, False, 75], [2011, 278, 2, 5, False, 76], [2011, 278, 2, 5, False, 77], [2011, 278, 2, 5, False, 78], [2011, 278, 2, 5, False, 79], [2011, 278, 2, 5, False, 80], [2011, 278, 2, 5, False, 81], [2011, 278, 2, 5, False, 82], [2011, 278, 2, 5, False, 83], [2011, 278, 2, 5, False, 84], [2011, 278, 2, 5, False, 85], [2011, 278, 2, 5, False, 86], [2011, 278, 2, 5, False, 87], [2011, 278, 2, 5, False, 88], [2011, 278, 2, 5, False, 89], [2011, 278, 2, 5, False, 90], [2011, 278, 2, 5, False, 91], [2011, 278, 2, 5, False, 92], [2011, 278, 2, 5, False, 93], [2011, 278, 2, 5, False, 94], [2011, 278, 2, 5, False, 95], [2011, 278, 2, 5, False, 96], [2011, 278, 2, 5, False, 97], [2011, 278, 2, 5, False, 98], [2011, 278, 2, 5, False, 99], [2011, 278, 2, 5, False, 100], [2011, 278, 2, 5, False, 101], [2011, 278, 2, 5, False, 102], [2011, 278, 2, 5, False, 103], [2011, 278, 2, 5, False, 104], [2011, 278, 2, 5, False, 105], [2011, 278, 2, 5, False, 106], [2011, 278, 2, 5, False, 107], [2011, 278, 2, 5, False, 108], [2011, 278, 2, 5, False, 109], [2011, 278, 2, 5, False, 110], [2011, 278, 2, 5, False, 111], [2011, 278, 2, 5, False, 112], [2011, 278, 2, 5, False, 113], [2011, 278, 2, 5, False, 114], [2011, 278, 2, 5, False, 115], [2011, 278, 2, 5, False, 116], [2011, 278, 2, 5, False, 117], [2011, 278, 2, 5, False, 118], [2011, 278, 2, 5, False, 119], [2011, 278, 2, 5, False, 120], [2011, 278, 2, 5, False, 121], [2011, 278, 2, 5, False, 122], [2011, 278, 2, 5, False, 123], [2011, 278, 2, 5, False, 124], [2011, 278, 2, 5, False, 125], [2011, 278, 2, 5, False, 126], [2011, 278, 2, 5, False, 127], [2011, 278, 2, 5, False, 128], [2011, 278, 2, 5, False, 129], [2011, 278, 2, 5, False, 130], [2011, 278, 2, 5, False, 131], [2011, 278, 2, 5, False, 132], [2011, 278, 2, 5, False, 133], [2011, 278, 2, 5, False, 134], [2011, 278, 2, 5, False, 135], [2011, 278, 2, 5, False, 136], [2011, 278, 2, 5, False, 137], [2011, 278, 2, 5, False, 138], [2011, 278, 2, 5, False, 139], [2011, 278, 2, 5, False, 140], [2011, 278, 2, 5, False, 141], [2011, 278, 2, 5, False, 142], [2011, 278, 2, 5, False, 143], [2011, 278, 2, 5, False, 144], [2011, 278, 2, 5, False, 145], [2013, 232, 1, 15, False, 0], [2013, 232, 1, 15, False, 1], [2013, 232, 1, 15, False, 2], [2013, 232, 1, 15, False, 3], [2013, 232, 1, 15, False, 4], [2013, 232, 1, 15, False, 5], [2013, 232, 1, 15, False, 6], [2013, 232, 1, 15, False, 7], [2013, 232, 1, 15, False, 8], [2013, 232, 1, 15, False, 9], [2013, 232, 1, 15, False, 10], [2013, 232, 1, 15, False, 11], [2013, 232, 1, 15, False, 12], [2013, 232, 1, 15, False, 13], [2013, 232, 1, 15, False, 14], [2013, 232, 1, 15, False, 15], [2013, 232, 1, 15, False, 16], [2013, 232, 1, 15, False, 17], [2013, 232, 1, 15, False, 18], [2013, 232, 1, 15, False, 19], [2013, 232, 1, 15, False, 20], [2013, 232, 1, 15, False, 21], [2013, 232, 1, 15, False, 22], [2013, 232, 1, 15, False, 23], [2013, 232, 1, 15, False, 24], [2013, 232, 1, 15, False, 25], [2013, 232, 1, 15, False, 26], [2013, 232, 1, 15, False, 27], [2013, 232, 1, 15, False, 28], [2013, 232, 1, 15, False, 29], [2013, 232, 1, 15, False, 30], [2013, 232, 1, 15, False, 31], [2013, 232, 1, 15, False, 32], [2013, 232, 1, 15, False, 33], [2013, 232, 1, 15, False, 34], [2013, 232, 1, 15, False, 35], [2013, 232, 1, 15, False, 36], [2013, 232, 1, 15, False, 37], [2013, 232, 1, 15, False, 38], [2013, 232, 1, 15, False, 39], [2013, 232, 1, 15, False, 40], [2013, 232, 1, 15, False, 41], [2013, 232, 1, 15, False, 42], [2013, 232, 1, 15, False, 43], [2013, 232, 1, 15, False, 44], [2013, 232, 1, 15, False, 45], [2013, 232, 1, 15, False, 46], [2013, 232, 1, 15, False, 47], [2013, 232, 1, 15, False, 48], [2013, 232, 1, 15, False, 49], [2013, 232, 1, 15, False, 50], [2013, 232, 1, 15, False, 51], [2013, 232, 1, 15, False, 52], [2013, 232, 1, 15, False, 53], [2013, 232, 1, 15, False, 54], [2013, 232, 1, 15, False, 55], [2013, 232, 1, 15, False, 56], [2013, 232, 1, 15, False, 57], [2013, 232, 1, 15, False, 58], [2013, 232, 1, 15, False, 59], [2013, 232, 1, 15, False, 60], [2013, 232, 1, 15, False, 61], [2013, 232, 1, 15, False, 62], [2013, 232, 1, 15, False, 63], [2013, 232, 1, 15, False, 64], [2013, 232, 1, 15, False, 65], [2013, 232, 1, 15, False, 66], [2013, 232, 1, 15, False, 67], [2013, 232, 1, 15, False, 68], [2013, 232, 1, 15, False, 69], [2013, 232, 1, 15, False, 70], [2013, 232, 1, 15, False, 71], [2013, 232, 1, 15, False, 72], [2013, 232, 1, 15, False, 73], [2013, 232, 1, 15, False, 74], [2013, 232, 1, 15, False, 75], [2013, 232, 1, 15, False, 76], [2013, 232, 1, 15, False, 77], [2013, 232, 1, 15, False, 78], [2013, 232, 1, 15, False, 79], [2013, 232, 1, 15, False, 80], [2013, 232, 1, 15, False, 81], [2013, 232, 1, 15, False, 82], [2013, 232, 1, 15, False, 83], [2013, 232, 1, 15, False, 84], [2013, 232, 1, 15, False, 85], [2013, 232, 1, 15, False, 86], [2013, 232, 1, 15, False, 87], [2013, 232, 1, 15, False, 88], [2013, 232, 1, 15, False, 89], [2013, 232, 1, 15, False, 90], [2013, 232, 1, 15, False, 91], [2013, 232, 1, 15, False, 92], [2013, 232, 1, 15, False, 93], [2013, 232, 1, 15, False, 94], [2013, 232, 1, 15, False, 95], [2013, 232, 1, 15, False, 96], [2013, 232, 1, 15, False, 97], [2013, 232, 1, 15, False, 98], [2013, 232, 1, 15, False, 99], [2013, 232, 1, 15, False, 100], [2013, 232, 1, 15, False, 101], [2013, 232, 1, 15, False, 102], [2013, 232, 1, 15, False, 103], [2013, 232, 1, 15, False, 104], [2013, 232, 1, 15, False, 105], [2013, 232, 1, 15, False, 106], [2013, 232, 1, 15, False, 107], [2013, 232, 1, 15, False, 108], [2013, 232, 1, 15, False, 109], [2013, 232, 1, 15, False, 110], [2013, 232, 1, 15, False, 111], [2013, 232, 1, 15, False, 112], [2013, 232, 1, 15, False, 113], [2013, 232, 1, 15, False, 114], [2013, 232, 1, 15, False, 115], [2013, 232, 1, 15, False, 116], [2013, 232, 1, 15, False, 117], [2013, 232, 1, 15, False, 118], [2013, 232, 1, 15, False, 119], [2013, 232, 1, 15, False, 120], [2013, 232, 1, 15, False, 121], [2013, 232, 1, 15, False, 122], [2013, 232, 1, 15, False, 123], [2013, 232, 1, 15, False, 124], [2013, 232, 1, 15, False, 125], [2013, 232, 1, 15, False, 126], [2013, 232, 1, 15, False, 127], [2013, 232, 1, 15, False, 128], [2013, 232, 1, 15, False, 129], [2013, 232, 1, 15, False, 130], [2013, 232, 1, 15, False, 131], [2013, 232, 1, 15, False, 132], [2013, 232, 1, 15, False, 133], [2013, 232, 1, 15, False, 134], [2013, 232, 1, 15, False, 135], [2013, 232, 1, 15, False, 136], [2013, 232, 1, 15, False, 137], [2013, 232, 1, 15, False, 138], [2013, 232, 1, 15, False, 139], [2013, 232, 1, 15, False, 140], [2013, 232, 1, 15, False, 141], [2013, 232, 1, 15, False, 142], [2013, 232, 1, 15, False, 143], [2013, 232, 1, 15, False, 144], [2013, 232, 1, 15, False, 145], [2013, 263, 4, 8, False, 0], [2013, 263, 4, 8, False, 1], [2013, 263, 4, 8, False, 2], [2013, 263, 4, 8, False, 3], [2013, 263, 4, 8, False, 4], [2013, 263, 4, 8, False, 5], [2013, 263, 4, 8, False, 6], [2013, 263, 4, 8, False, 7], [2013, 263, 4, 8, False, 8], [2013, 263, 4, 8, False, 9], [2013, 263, 4, 8, False, 10], [2013, 263, 4, 8, False, 11], [2013, 263, 4, 8, False, 12], [2013, 263, 4, 8, False, 13], [2013, 263, 4, 8, False, 14], [2013, 263, 4, 8, False, 15], [2013, 263, 4, 8, False, 16], [2013, 263, 4, 8, False, 17], [2013, 263, 4, 8, False, 18], [2013, 263, 4, 8, False, 19], [2013, 263, 4, 8, False, 20], [2013, 263, 4, 8, False, 21], [2013, 263, 4, 8, False, 22], [2013, 263, 4, 8, False, 23], [2013, 263, 4, 8, False, 24], [2013, 263, 4, 8, False, 25], [2013, 263, 4, 8, False, 26], [2013, 263, 4, 8, False, 27], [2013, 263, 4, 8, False, 28], [2013, 263, 4, 8, False, 29], [2013, 263, 4, 8, False, 30], [2013, 263, 4, 8, False, 31], [2013, 263, 4, 8, False, 32], [2013, 263, 4, 8, False, 33], [2013, 263, 4, 8, False, 34], [2013, 263, 4, 8, False, 35], [2013, 263, 4, 8, False, 36], [2013, 263, 4, 8, False, 37], [2013, 263, 4, 8, False, 38], [2013, 263, 4, 8, False, 39], [2013, 263, 4, 8, False, 40], [2013, 263, 4, 8, False, 41], [2013, 263, 4, 8, False, 42], [2013, 263, 4, 8, False, 43], [2013, 263, 4, 8, False, 44], [2013, 263, 4, 8, False, 45], [2013, 263, 4, 8, False, 46], [2013, 263, 4, 8, False, 47], [2013, 263, 4, 8, False, 48], [2013, 263, 4, 8, False, 49], [2013, 263, 4, 8, False, 50], [2013, 263, 4, 8, False, 51], [2013, 263, 4, 8, False, 52], [2013, 263, 4, 8, False, 53], [2013, 263, 4, 8, False, 54], [2013, 263, 4, 8, False, 55], [2013, 263, 4, 8, False, 56], [2013, 263, 4, 8, False, 57], [2013, 263, 4, 8, False, 58], [2013, 263, 4, 8, False, 59], [2013, 263, 4, 8, False, 60], [2013, 263, 4, 8, False, 61], [2013, 263, 4, 8, False, 62], [2013, 263, 4, 8, False, 63], [2013, 263, 4, 8, False, 64], [2013, 263, 4, 8, False, 65], [2013, 263, 4, 8, False, 66], [2013, 263, 4, 8, False, 67], [2013, 263, 4, 8, False, 68], [2013, 263, 4, 8, False, 69], [2013, 263, 4, 8, False, 70], [2013, 263, 4, 8, False, 71], [2013, 263, 4, 8, False, 72], [2013, 263, 4, 8, False, 73], [2013, 263, 4, 8, False, 74], [2013, 263, 4, 8, False, 75], [2013, 263, 4, 8, False, 76], [2013, 263, 4, 8, False, 77], [2013, 263, 4, 8, False, 78], [2013, 263, 4, 8, False, 79], [2013, 263, 4, 8, False, 80], [2013, 263, 4, 8, False, 81], [2013, 263, 4, 8, False, 82], [2013, 263, 4, 8, False, 83], [2013, 263, 4, 8, False, 84], [2013, 263, 4, 8, False, 85], [2013, 263, 4, 8, False, 86], [2013, 263, 4, 8, False, 87], [2013, 263, 4, 8, False, 88], [2013, 263, 4, 8, False, 89], [2013, 263, 4, 8, False, 90], [2013, 263, 4, 8, False, 91], [2013, 263, 4, 8, False, 92], [2013, 263, 4, 8, False, 93], [2013, 263, 4, 8, False, 94], [2013, 263, 4, 8, False, 95], [2013, 263, 4, 8, False, 96], [2013, 263, 4, 8, False, 97], [2013, 263, 4, 8, False, 98], [2013, 263, 4, 8, False, 99], [2013, 263, 4, 8, False, 100], [2013, 263, 4, 8, False, 101], [2013, 263, 4, 8, False, 102], [2013, 263, 4, 8, False, 103], [2013, 263, 4, 8, False, 104], [2013, 263, 4, 8, False, 105], [2013, 263, 4, 8, False, 106], [2013, 263, 4, 8, False, 107], [2013, 263, 4, 8, False, 108], [2013, 263, 4, 8, False, 109], [2013, 263, 4, 8, False, 110], [2013, 263, 4, 8, False, 111], [2013, 263, 4, 8, False, 112], [2013, 263, 4, 8, False, 113], [2013, 263, 4, 8, False, 114], [2013, 263, 4, 8, False, 115], [2013, 263, 4, 8, False, 116], [2013, 263, 4, 8, False, 117], [2013, 263, 4, 8, False, 118], [2013, 263, 4, 8, False, 119], [2013, 263, 4, 8, False, 120], [2013, 263, 4, 8, False, 121], [2013, 263, 4, 8, False, 122], [2013, 263, 4, 8, False, 123], [2013, 263, 4, 8, False, 124], [2013, 263, 4, 8, False, 125], [2013, 263, 4, 8, False, 126], [2013, 263, 4, 8, False, 127], [2013, 263, 4, 8, False, 128], [2013, 263, 4, 8, False, 129], [2013, 263, 4, 8, False, 130], [2013, 263, 4, 8, False, 131], [2013, 263, 4, 8, False, 132], [2013, 263, 4, 8, False, 133], [2013, 263, 4, 8, False, 134], [2013, 263, 4, 8, False, 135], [2013, 263, 4, 8, False, 136], [2013, 263, 4, 8, False, 137], [2013, 263, 4, 8, False, 138], [2013, 263, 4, 8, False, 139], [2013, 263, 4, 8, False, 140], [2013, 263, 4, 8, False, 141], [2013, 263, 4, 8, False, 142], [2013, 263, 4, 8, False, 143], [2013, 263, 4, 8, False, 144], [2013, 263, 4, 8, False, 145], [2012, 128, 0, 16, False, 0], [2012, 128, 0, 16, False, 1], [2012, 128, 0, 16, False, 2], [2012, 128, 0, 16, False, 3], [2012, 128, 0, 16, False, 4], [2012, 128, 0, 16, False, 5], [2012, 128, 0, 16, False, 6], [2012, 128, 0, 16, False, 7], [2012, 128, 0, 16, False, 8], [2012, 128, 0, 16, False, 9], [2012, 128, 0, 16, False, 10], [2012, 128, 0, 16, False, 11], [2012, 128, 0, 16, False, 12], [2012, 128, 0, 16, False, 13], [2012, 128, 0, 16, False, 14], [2012, 128, 0, 16, False, 15], [2012, 128, 0, 16, False, 16], [2012, 128, 0, 16, False, 17], [2012, 128, 0, 16, False, 18], [2012, 128, 0, 16, False, 19], [2012, 128, 0, 16, False, 20], [2012, 128, 0, 16, False, 21], [2012, 128, 0, 16, False, 22], [2012, 128, 0, 16, False, 23], [2012, 128, 0, 16, False, 24], [2012, 128, 0, 16, False, 25], [2012, 128, 0, 16, False, 26], [2012, 128, 0, 16, False, 27], [2012, 128, 0, 16, False, 28], [2012, 128, 0, 16, False, 29], [2012, 128, 0, 16, False, 30], [2012, 128, 0, 16, False, 31], [2012, 128, 0, 16, False, 32], [2012, 128, 0, 16, False, 33], [2012, 128, 0, 16, False, 34], [2012, 128, 0, 16, False, 35], [2012, 128, 0, 16, False, 36], [2012, 128, 0, 16, False, 37], [2012, 128, 0, 16, False, 38], [2012, 128, 0, 16, False, 39], [2012, 128, 0, 16, False, 40], [2012, 128, 0, 16, False, 41], [2012, 128, 0, 16, False, 42], [2012, 128, 0, 16, False, 43], [2012, 128, 0, 16, False, 44], [2012, 128, 0, 16, False, 45], [2012, 128, 0, 16, False, 46], [2012, 128, 0, 16, False, 47], [2012, 128, 0, 16, False, 48], [2012, 128, 0, 16, False, 49], [2012, 128, 0, 16, False, 50], [2012, 128, 0, 16, False, 51], [2012, 128, 0, 16, False, 52], [2012, 128, 0, 16, False, 53], [2012, 128, 0, 16, False, 54], [2012, 128, 0, 16, False, 55], [2012, 128, 0, 16, False, 56], [2012, 128, 0, 16, False, 57], [2012, 128, 0, 16, False, 58], [2012, 128, 0, 16, False, 59], [2012, 128, 0, 16, False, 60], [2012, 128, 0, 16, False, 61], [2012, 128, 0, 16, False, 62], [2012, 128, 0, 16, False, 63], [2012, 128, 0, 16, False, 64], [2012, 128, 0, 16, False, 65], [2012, 128, 0, 16, False, 66], [2012, 128, 0, 16, False, 67], [2012, 128, 0, 16, False, 68], [2012, 128, 0, 16, False, 69], [2012, 128, 0, 16, False, 70], [2012, 128, 0, 16, False, 71], [2012, 128, 0, 16, False, 72], [2012, 128, 0, 16, False, 73], [2012, 128, 0, 16, False, 74], [2012, 128, 0, 16, False, 75], [2012, 128, 0, 16, False, 76], [2012, 128, 0, 16, False, 77], [2012, 128, 0, 16, False, 78], [2012, 128, 0, 16, False, 79], [2012, 128, 0, 16, False, 80], [2012, 128, 0, 16, False, 81], [2012, 128, 0, 16, False, 82], [2012, 128, 0, 16, False, 83], [2012, 128, 0, 16, False, 84], [2012, 128, 0, 16, False, 85], [2012, 128, 0, 16, False, 86], [2012, 128, 0, 16, False, 87], [2012, 128, 0, 16, False, 88], [2012, 128, 0, 16, False, 89], [2012, 128, 0, 16, False, 90], [2012, 128, 0, 16, False, 91], [2012, 128, 0, 16, False, 92], [2012, 128, 0, 16, False, 93], [2012, 128, 0, 16, False, 94], [2012, 128, 0, 16, False, 95], [2012, 128, 0, 16, False, 96], [2012, 128, 0, 16, False, 97], [2012, 128, 0, 16, False, 98], [2012, 128, 0, 16, False, 99], [2012, 128, 0, 16, False, 100], [2012, 128, 0, 16, False, 101], [2012, 128, 0, 16, False, 102], [2012, 128, 0, 16, False, 103], [2012, 128, 0, 16, False, 104], [2012, 128, 0, 16, False, 105], [2012, 128, 0, 16, False, 106], [2012, 128, 0, 16, False, 107], [2012, 128, 0, 16, False, 108], [2012, 128, 0, 16, False, 109], [2012, 128, 0, 16, False, 110], [2012, 128, 0, 16, False, 111], [2012, 128, 0, 16, False, 112], [2012, 128, 0, 16, False, 113], [2012, 128, 0, 16, False, 114], [2012, 128, 0, 16, False, 115], [2012, 128, 0, 16, False, 116], [2012, 128, 0, 16, False, 117], [2012, 128, 0, 16, False, 118], [2012, 128, 0, 16, False, 119], [2012, 128, 0, 16, False, 120], [2012, 128, 0, 16, False, 121], [2012, 128, 0, 16, False, 122], [2012, 128, 0, 16, False, 123], [2012, 128, 0, 16, False, 124], [2012, 128, 0, 16, False, 125], [2012, 128, 0, 16, False, 126], [2012, 128, 0, 16, False, 127], [2012, 128, 0, 16, False, 128], [2012, 128, 0, 16, False, 129], [2012, 128, 0, 16, False, 130], [2012, 128, 0, 16, False, 131], [2012, 128, 0, 16, False, 132], [2012, 128, 0, 16, False, 133], [2012, 128, 0, 16, False, 134], [2012, 128, 0, 16, False, 135], [2012, 128, 0, 16, False, 136], [2012, 128, 0, 16, False, 137], [2012, 128, 0, 16, False, 138], [2012, 128, 0, 16, False, 139], [2012, 128, 0, 16, False, 140], [2012, 128, 0, 16, False, 141], [2012, 128, 0, 16, False, 142], [2012, 128, 0, 16, False, 143], [2012, 128, 0, 16, False, 144], [2012, 128, 0, 16, False, 145]]
    # test_results = results[0:len(results)//2]
    # held_results = results[len(results)//2:]
    test_results = [0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 4, 1, 0, 0, 4, 0, 0, 0, 2, 0, 5, 2, 2, 2, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 16, 1, 3, 2, 0, 4, 0, 1, 2, 1, 0, 1, 0, 0, 2, 1, 0, 0, 0, 1, 3, 1, 2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 8, 3, 1, 2, 2, 5, 0, 1, 0, 2, 1, 3, 0, 1, 4, 8, 6, 5, 0, 0, 4, 6, 1, 0, 0, 4, 5, 4, 1, 0, 0, 13, 0, 0, 2, 3, 4, 13, 6, 3, 2, 6, 6, 0, 0, 5, 0, 12, 13, 5, 6, 0, 4, 15, 2, 0, 0, 2, 0, 1, 2, 1, 11, 8, 1, 4, 1, 1, 1, 10, 10, 6, 0, 1, 4, 2, 1, 0, 0, 3, 0, 3, 1, 0, 0, 1, 1, 0, 0, 1, 1, 3, 0, 0, 4, 0, 0, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 2, 3, 8, 2, 2, 0, 4, 0, 6, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 3, 2, 1, 0, 0, 1, 4, 0, 0, 4, 0, 2, 0, 1, 0, 2, 2, 15, 0, 2, 1, 0, 2, 0, 1, 0, 5, 2, 2, 0, 0, 4, 0, 0, 1, 3, 1, 5, 7, 2, 0, 1, 5, 6, 2, 7, 0, 3, 1, 2, 3, 0, 0, 1, 2, 0, 0, 0, 0, 9, 0, 0, 11, 1, 1, 0, 0, 3, 1, 3, 1, 1, 0, 0, 1, 2, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 1, 0, 0, 0, 3, 0, 0, 2, 2, 0, 1, 0, 0, 0, 0, 0, 2, 7, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 3, 1, 0, 2, 4, 1, 0, 0, 0, 0, 0, 1, 0, 2, 3, 2, 1, 0, 0, 1, 1, 0, 0, 0, 4, 1, 5, 7, 0, 0, 0, 0, 0, 2, 1, 0, 1, 0, 1, 8, 0, 3, 2, 2, 0, 0, 2, 0, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 3, 0, 2, 2, 1, 0, 0, 0, 0, 1, 0, 0, 3, 0, 1, 0, 2, 0, 0, 1, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 3, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
    held_results = [0, 0, 0, 1, 3, 0, 1, 2, 1, 1, 1, 1, 2, 0, 1, 0, 5, 4, 0, 3, 6, 2, 7, 0, 3, 2, 3, 2, 0, 0, 1, 0, 0, 6, 0, 0, 1, 0, 0, 1, 2, 4, 2, 0, 2, 3, 8, 2, 1, 0, 1, 0, 4, 3, 3, 2, 0, 1, 4, 3, 0, 0, 1, 0, 0, 1, 4, 1, 2, 0, 1, 0, 0, 0, 4, 4, 2, 2, 0, 1, 2, 2, 0, 1, 3, 0, 1, 4, 4, 4, 2, 4, 0, 1, 3, 1, 7, 0, 1, 3, 0, 0, 2, 2, 1, 0, 0, 0, 0, 1, 2, 2, 4, 4, 13, 1, 2, 0, 1, 0, 1, 0, 0, 1, 1, 1, 1, 3, 6, 1, 1, 6, 3, 4, 1, 1, 0, 1, 2, 3, 1, 1, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 4, 2, 4, 2, 3, 3, 0, 2, 1, 0, 2, 0, 3, 1, 2, 0, 4, 1, 6, 0, 1, 5, 0, 1, 0, 0, 2, 1, 2, 1, 0, 0, 5, 0, 0, 2, 4, 1, 6, 8, 1, 2, 4, 1, 3, 3, 4, 0, 3, 10, 2, 4, 0, 1, 2, 2, 0, 0, 3, 0, 2, 0, 2, 6, 4, 0, 0, 1, 3, 8, 3, 6, 3, 0, 0, 0, 6, 0, 0, 1, 4, 0, 2, 0, 1, 2, 2, 1, 3, 0, 0, 2, 0, 0, 3, 9, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 1, 6, 13, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 4, 2, 2, 1, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 5, 0, 13, 2, 1, 2, 1, 1, 1, 0, 3, 2, 17, 6, 1, 3, 13, 7, 31, 0, 1, 8, 6, 1, 0, 0, 1, 3, 2, 4, 0, 0, 8, 0, 0, 13, 5, 4, 5, 11, 7, 1, 5, 8, 4, 6, 7, 1, 2, 10, 1, 3, 0, 7, 6, 3, 0, 0, 1, 6, 4, 3, 2, 4, 6, 10, 1, 1, 3, 1, 3, 14, 5, 3, 6, 8, 0, 3, 0, 2, 3, 0, 6, 5, 9, 5, 4, 3, 0, 1, 4, 6, 2, 0, 7, 6, 0, 0, 9, 12, 0, 1, 0, 0, 0, 0, 0, 17, 5, 7, 16, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 6, 9, 1, 1, 4, 1, 2, 4, 10, 1, 5, 4, 2, 1, 1, 2, 2, 7, 0, 0, 0, 0, 0, 2, 0, 1, 4, 0, 2, 1, 1, 1, 2, 6, 0, 2, 1, 0, 0, 2, 5, 9, 4, 1, 4, 0, 0, 0, 0, 2, 3, 3, 6, 2, 5, 6, 0, 2, 0, 2, 0, 2, 1, 2, 3, 0, 2, 6, 2, 5, 0, 1, 1, 0, 2, 0, 0, 6, 2, 3, 4, 6, 0, 3, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    models = [
        linear_model.LinearRegression(),
        linear_model.Lasso(alpha = 0.1),
        linear_model.LassoLars(alpha = 0.1),
        svm.SVR(),
        RandomForestClassifier(n_estimators=10)
        # FactorModel()
    ]

    # models.extend([linear_model.Ridge(alpha=a) for a in [0.2, 0.4, 0.6, 0.8]])
    print("11111111111111111111111111111111111111111111111111111111111111111111111")
    print(held_samples)
    for model in models:
        m = model
        print("The model is:" + str(m))
        m.fit(test_samples, test_results)
        error = 0
        print("Held samples = " + str(len(held_samples)))
        for held in held_samples:
            [year, doy, dow, hour, isWkEnd, station] = held
            prediction = m.predict([year, doy, dow, hour, isWkEnd, station])
            newyear = datetime.datetime(year, 1, 1)
            td = datetime.timedelta(days=doy-1, hours=hour)
            print(newyear+td)
            print("Prediction: " + str(prediction))
            actual = Flow.forHour(newyear+td).outgoing(station)
            print("Actual: " + str(actual))
            error += (prediction-actual)**2
        print("Square Error = "+str(error))
        print("Relative Square Error = " + str(error/len(held_samples)) + "\n")
    print("--- %s seconds ---" % (time.time() - start_time))

def make_maps():
    with open("hubway_stations.csv") as csvfile2:
        readCSV2 = csv.reader(csvfile2, delimiter = ",")
        stations = []
        for rows in readCSV2:
            if rows[0] != 'id':     # Skip first line
                stations.append([float(rows[4]), float(rows[5])])




    # print(stations)
    # put up the map
    width = 647
    height = 749
    ne = [42.4045, -71.0357]
    sw = [42.3095, -71.1465]

    def ll_to_xy(pt):
        pct = (pt[1]-sw[1]) / (ne[1]-sw[1])
        x = width * pct
        pct = (pt[0]-sw[0]) / (ne[0]-sw[0])
        y = height * pct
        return [x, y]

    pts = [ll_to_xy(x) for x in stations]
    # List comprehension

    x1, y1 = zip(*pts)

    for i in range(0, 24):
        print(i)
        print("#################################################################################")

        real = Flow()
        for d in range(1,30):
            dt = datetime.datetime(2013, 5, d, i)
            if not weekend(dt):
                f = Flow.forHour(dt)
                real += f

        print(real.inbound)
        print(real.outbound)

        inbound = real.inbound
        outbound = real.outbound
        bIn = [0] * len(real.inbound)
        colours = [0] * len(real.inbound)

        for j in range(0, len(inbound)):
            bIn[j] = (inbound[j] - outbound[j])
            if (inbound[j] - outbound[j]) > 0:
                colours[j] = "red"
            elif (inbound[j] - outbound[j]) < 0:
                colours[j] = "blue"
            else:
                colours[j] = "green"


        print(bIn)

        plt.xlim(0, 650)
        plt.ylim(0, 750)
        img = imread("map.png")
        plt.imshow(img, zorder=0, extent=[0, 647, 0, 749])
        plt.scatter(x1, y1, s=40, c=colours, edgecolors='none')
        plt.title("Hour-" + str(i))
        plt.savefig("month-%02d" % i)
        plt.show()

#make_maps()
