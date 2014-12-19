#!/usr/bin/env python3
__author__ = 'Austin'

import datetime
import hubway
import operator

def average(l):
    return sum(l) / len(l)

def normalize(l):
    avg = average(l)
    return [x/avg for x in l]

def poserror(l1, l2):
    assert len(l1) == len(l2)
    return sum(l1)-sum(l2)

def sqerror(l1, l2):
    assert len(l1) == len(l2)
    return sum(map(lambda p: (p[0]-p[1])**2 , zip(l1,l2)))


def weekend(dt):
    dow = dt.weekday()
    return dow == 5 or dow == 6;

class Flow:
    def __init__(self, inb = None, outb = None):
        if inb == None:
            inb = [0] * hubway.STATIONS
        self.inbound = inb

        if outb == None:
            outb = [0] * hubway.STATIONS
        self.outbound = outb

    def countStart(self, station):
        self.outbound[station] += 1

    def countEnd(self, station):
        self.inbound[station] += 1

    @classmethod
    def real(cls, date, hour):
        flow = Flow()
        for stime, sstation, etime, estation in hubway.trips():
            if stime.date() == date and stime.timetuple().tm_hour == hour:
                flow.countStart(sstation)
            if etime.date() == date and etime.timetuple().tm_hour == hour:
                flow.countEnd(estation)
            if stime.date() > date:
                break
        return flow

    def __repr__(self):
        return repr(list(zip(self.inbound, self.outbound)))

    # With these you can add, say, all of the hourly flows for a day
    # up to get the flow for the whole day.

    def __add__(self, other):
        return Flow(map(operator.add, self.inbound, other.inbound),
                    map(operator.add, self.outbound, other.outbound))
    def __iadd__(self, other):
        self.inbound = map(operator.add, self.inbound, other.inbound)
        self.outbound = map(operator.add, self.outbound, other.outbound)
        return self
    def __sub__(self, other):
        return Flow(map(operator.sub, self.inbound, other.inbound),
                    map(operator.sub, self.outbound, other.outbound))
    def __isub__(self, other):
        self.inbound = map(operator.sub, self.inbound, other.inbound)
        self.outbound = map(operator.sub, self.outbound, other.outbound)
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
    def __rtruediv__(self, factor):
        return self * factor
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
    avgFlow = allFlow / (365 * 3 * 24);
    print (str(avgFlow))

    def predict_for_hour_using_hourly_data(hour, date):
        f = factorsForHour[hour]
        print("Multiplying by "+str(f)+" because in hour "+str(hour))
        return avgFlow * f

    # This seems like a nice, simple way to make predictions, but would
    # probably work poorly, because weekend usage has a different "shape"
    # than weekdays, rather than simply being related by a factor.

    # def predict_for_hour_using_all(departure, hour, date):
    #     d = dow_factor[hour];
    #     h = hour_factor[hour];
    #     m = month_factor[month];
    #     return m * d * h * avgFlow;

    def predict_for_hour_using_all(date, hour):
        factors = factorsForHourOnWeekdays
        if (weekend(date)):
            factors = factorsForHourOnWeekend
        f = factors[hour] * factorsForMonth[date.month-1] * factorsForYear[date.year-2011]

        print("Multiplying by {:.2f} for {} {}:00 ({})"\
                  .format(f, date.date(), hour,
                          "Weekend" if weekend(date) else "Weekday"))
        return avgFlow * f;


    total = 0.0
    RUNS = 10
    while (RUNS > 0):
        dt = datetime.datetime(2013-(RUNS%3), 12-RUNS, 21-RUNS)
        hour = RUNS+4
        date = dt.date()
        real = Flow.real(date, hour)

        errs1 = real.errors(avgFlow)
        errs2 = real.errors(predict_for_hour_using_all(dt, hour))

        print(" Improvements {:.2f} {:.2f}"\
                  .format(errs1[0]-errs2[0], abs(errs1[1])-abs(errs2[1])));

        total += errs1[0]-errs2[0]
        RUNS -= 1

    print("Total improvement = {}".format(total))
