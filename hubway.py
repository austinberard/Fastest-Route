import csv
from datetime import datetime
import gzip
import re

STATIONS = 150

def initializeGrid(size=STATIONS):
  grid = []
  for i in range(0, size):
    grid.append([])
    for j in range(0, size):
        grid[i].append(0)
  return grid


pp = re.compile(r'(\d+)/(\d+)/(\d{4}) (\d{2}):(\d{2})')
def time_from_stamp(stamp):
  l = list(map(int, pp.match(stamp).groups()));
  return datetime(l[2], l[0], l[1], l[3], l[4])
  # Equivalent, but slower: return datetime.strptime(stamp, "%m/%d/%Y %H:%M:%S")

cached_trips = []
def trips():
  if len(cached_trips) != 0:
    return cached_trips

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

      cached_trips.append([start_time, start_station, end_time, end_station])
  return cached_trips

def trip_sample(n):
  return trips[0:n]
  

def findMax(grid):
  m = 0
  for lst in grid:
    m = max(m, max(lst))
  return m
