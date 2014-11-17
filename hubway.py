import csv
import gzip

STATIONS = 150

def initializeGrid(size):
  grid = []
  for i in range(0, size):
    grid.append([])
    for j in range(0, size):
        grid[i].append(0)
  return grid

def trip_hours():
  with gzip.open("hubway_trips.csv.gz", mode='rt') as csvfile:
    for row in csv.reader(csvfile, delimiter=","):
      if row[5] == "strt_statn":
        continue
      if row[5] == "" or row[7] == "":
        continue

      start = int(row[5])
      end = int(row[7])
      if start > STATIONS or end > STATIONS:
        print("Ouch "+str(start) + " " + str(end))
        exit()

      rawDate = row[4]
      betterDate = rawDate.replace(" ", "/")
      bettererDate = betterDate.replace(":", "/")
      date = bettererDate.split("/")

      hour = int(date[3])
      yield hour, start, end

def findMax(grid):
  m = 0
  for lst in grid:
    m = max(m, max(lst))
  return m
