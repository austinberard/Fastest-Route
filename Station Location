__author__ = 'Austin'
import matplotlib.pyplot as plt
import csv
with open("hubway_stations.csv") as csvfile2:
    readCSV2 = csv.reader(csvfile2, delimiter = ",")
    lng = []
    lat = []

    for rows in readCSV2:
        lngg = rows[5]
        lng.append(lngg)

        latt = rows[4]
        lat.append(latt)

del lng[0]
del lat[0]
print(min(lng))
print(max(lng))
print(min(lat))
print(max(lat))
x = lng
y = lat

plt.plot(x, y, ".")

plt.show()
