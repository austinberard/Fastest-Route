import csv
import gzip
import urllib.request
import simplejson




with open("dates.csv") as csvfile:
    readCSV = csv.reader(csvfile, delimiter=",")
    dates = []

    #appends the start dates to "dates" and splits the month, day, and year
    for row in readCSV:
        date = row[0]
        times = date.split("/")

        dates.append(times)

print(dates)

precip = []
tempature = []
for i in dates:
    token = "a24d167fd246539e"

    year = i[2]
    MM = i[0]
    DD = i[1]

    dateUrl = '20' + year + MM + DD
    print(dateUrl)
    url = "http://api.wunderground.com/api/" + token + "/history_" + dateUrl + "/q/MA/Boston.json"

    json_obj = urllib.request.urlopen(url)
    data = simplejson.load(json_obj)

    temp = data["history"]["dailysummary"][0]["meantempi"]
    rain = data["history"]["dailysummary"][0]["rain"]
    tempature.append(temp)
    precip.append(rain)

print(tempature)
print(precip)




