import json, time
import urllib as urllib2
from datetime import datetime
from time import mktime

import time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

import matplotlib
import pylab

def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1] # cause the diff is 1 shorter

        if delta>0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up*(n-1) + upval)/n
        down = (down*(n-1) + downval)/n

        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)

    return rsi

def getHistoricalData(stockSymbol):
    historicalPrices = []
    
    # login to API
    urllib2.urlopen("http://api.kibot.com/?action=login&user=guest&password=guest")

    # get 14 days of data from API (business days only, could be < 10)
    url = "http://api.kibot.com/?action=history&symbol=" + stockSymbol + "&interval=daily&period=365&unadjusted=1&regularsession=1"
    apiData = urllib2.urlopen(url).read().decode("utf-8").split("\n")
    i = 0
    for line in apiData:
        i = i + 1
        if(len(line) > 0):
            tempLine = line.split(',')
            price = float(tempLine[1])
            historicalPrices.append(price)
    print (i)
    return historicalPrices
def getRSI(SYM):
    return rsiFunc(getHistoricalData('AAPL'))

