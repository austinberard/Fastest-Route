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
    print (factorsForMonth)
    print (factorsForHour)
    print (factorsForHourOnWeekdays)
    print (factorsForHourOnWeekend)
    print (factorsForYear)


    allFlow = Flow()
    for stime, sstation, etime, estation in hubway.trips():
        allFlow.countStart(sstation)
        allFlow.countEnd(estation)
    avgFlow = allFlow / (365 * 3 * 24)
    print (str(avgFlow))

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
    samples = [];
    results = []
    
    for trip in sample_trips:
        dt = trip[0]

        year = dt.year
        doy = dt.timetuple().tm_yday
        dow = dt.weekday()
        hour = dt.hour
        isWkEnd = weekend(dt)

        for station, value in enumerate(allFlow.outbound):
            print("%s, %s, %s, %s, %s, %s : %s" %
                 (year, doy, dow, hour, isWkEnd, station, value))
            samples.append([year, doy, dow, hour, isWkEnd, station])
            results.append(value)

    print (len(samples))

    test_samples = samples[0:len(samples)//2]
    held_samples = samples[len(samples)//2:]

    test_results = results[0:len(results)//2]
    held_results = results[len(results)//2:]

    models = [
        linear_model.LinearRegression(),
        linear_model.Lasso(alpha = 0.1),
        linear_model.LassoLars(alpha = 0.1),
        svm.SVR(),
        RandomForestClassifier(n_estimators=10),
        FactorModel()
    ]

    models.extend([linear_model.Ridge(alpha=a) for a in [0.2, 0.4, 0.6, 0.8]])


    for model in models:
        m = model
        print (str(m))
        m.fit(test_samples, test_results)
        error = 0
        print ("Held samples = "+len(held_samples))
        for held in held_samples:
            [year, doy, dow, hour, isWkEnd, station] = held
            prediction = m.predict([year, doy, dow, hour, isWkEnd, station])
            print(prediction)
            newyear = datetime.datetime(year, 1, 1);
            td = datetime.timedelta(days=doy-1, hours=hour);
            print (newyear, doy, hour, td, newyear+td);
            actual = Flow.forHour(newyear+td).outgoing(station)
            error += (prediction-actual)**2;
        print("Error = "+str(error)+"\n")

    # def test_machine(coefs):
    #     dt = datetime.datetime(2013-(RUNS % 3), 12-RUNS, 21-RUNS, RUNS+4)
    #     print(dt)
    #     yearTest = dt.year
    #     print(yearTest)
    #     doyTest = dt.timetuple().tm_yday
    #     print(doyTest)
    #     dowTest = dt.weekday()
    #     print(dowTest)
    #     hourTest = dt.hour
    #     print(hourTest)
    #     isWkEndTest = weekend(dt)
    #     print(isWkEndTest)
    #     station = random.randint(1, 150)
    #     print(station)
    #
    #     total = (yearTest * clf.coef_[0]) \
    #           + (doyTest * clf.coef_[1]) \
    #           + (dowTest * clf.coef_[2]) \
    #           + (hourTest * clf.coef_[3]) \
    #           + (isWkEndTest * clf.coef_[4]) \
    #           + (isWkEndTest * clf.coef_[5])
    #
    #     print(total)
    #
    #
    # test_machine(clf.coef_)


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
