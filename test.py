__author__ = 'Austin'
from random import randint
import re
import nltk
# from nltk.book import *
# print(text5.count("lol"))
import csv
def CollatzConjecture(n):
    count = 0
    while n != 1:
        print(int(n))
        if float(n) % 2 == 0:
            count += 1
            n /= 2
        else:
            count += 1
            n = (3 * n) + 1
    print(count)

def domain_name(url):
    # test = re.match('[http]s?[://][www]?/S', url)
    # print(test.group())
    try:
        url = url.split('/')[2]
    except IndexError:
        pass

    url = url.strip('.com')
    url = url.strip('www.')
    print(url)

def fib():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

for index, fibonacci_number in enumerate(fib()):
     print('{i:3}: {f:3}'.format(i=index, f=fibonacci_number))
     if index == 10:
         break

# listed_dictionary = list(csv.DictReader(open('hubway_trips.csv', 'r')))
# print(listed_dictionary)
import string

import re

import re

class Mod:
    mod4 = re.compile("\[[+]?[-]?\d+\]") #Your regular expression here

import re
def validPhoneNumber(phoneNumber):
    if re.match("[(][\d]{3}[)][ ][\d]{3}-[\d]{4}", phoneNumber):
        print("True")
        return True
    else:
        print("False")
        return False

validPhoneNumber("(1111)555 2345")