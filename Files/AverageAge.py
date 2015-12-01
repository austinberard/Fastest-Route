import csv
import gzip
from collections import defaultdict
import os

__author__ = 'Austin'

test = defaultdict(lambda: 0)
tot = 0
agetot = 0
currentDir = os.getcwd()
filename = currentDir + '/Data/hubway_trips.csv.gz'
with gzip.open(filename, mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[5] == "strt_statn":
            continue
        if row[11] == '':
            continue
        year = int(row[11])
        age = 2015 - year
        agetot += age
        print(age)
        test[age] += 1
        tot += 1

print(test)
print("Average age is: " + str(agetot/tot))
