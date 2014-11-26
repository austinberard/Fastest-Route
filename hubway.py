import csv
from datetime import datetime
import gzip
import re

STATIONS = 150

def initializeGrid(size):
  grid = []
  for i in range(0, size):
    grid.append([])
    for j in range(0, size):
        grid[i].append(0)
  return grid


def time_from_stamp(stamp):
  pp = re.compile(r'(\d{1})/(\d{2})/(\d{4}) (\d{2}):(\d{2})')
  stamp1 = datetime(*map(int, pp.match(stamp).groups()))
  return stamp1
  # return datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S")

def trips():
  with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
      if row[5] == "strt_statn":
        continue
      if row[5] == "" or row[7] == "":
        continue

      start_station = int(row[5])
      end_station = int(row[7])
      if start_station > STATIONS or end_station > STATIONS:
        print("Ouch "+str(start_station) + " " + str(end_station))
        exit()

      start_time = time_from_stamp(row[4])
      end_time = time_from_stamp(row[6])

      yield start_time, start_station, end_time, end_station

def findMax(grid):
  m = 0
  for lst in grid:
    m = max(m, max(lst))
  return m
