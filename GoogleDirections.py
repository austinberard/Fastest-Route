__author__ = 'Austin'
from urllib.request import urlopen
import simplejson
import re


def Directions(start, end, mode):
    formattedStart = start.replace(" ", "_")
    formattedEnd = end.replace(" ", "_")
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=%s&destination=%s&mode=%s&key=AIzaSyCG4JPL7D7eLCnOap0mZnc5KCjOz2WXgf0" % (formattedStart, formattedEnd, mode)
    json_obj = urlopen(url)
    data = simplejson.load(json_obj)
    duration = (data['routes'][0]['legs'][0]['duration'])
    print(duration['text'])
    for step in data['routes'][0]['legs'][0]['steps']:
        print(re.sub('<[^<]+?>', '', step['html_instructions']))


# Directions("42.3426261192002,-71.095690425241", "providence", "bicycle")
