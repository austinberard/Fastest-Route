__author__ = 'Austin'
import csv
from datetime import datetime
import gzip

male = 0
female = 0
neither = 0

with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
        if row[5] == "strt_statn":
            continue
        if row[5] == "" or row[7] == "":
            continue
        gender = str(row[12])
        if gender == "Male":
            print("Male")
            male += 1
        elif gender == "Female":
            print("Female")
            female += 1
        else:
            print("Not registered")
            neither += 1

print(male, female, neither)