#!/usr/bin/python

import sys
import scipy
import numpy
import ransac

if(len(sys.argv) < 4):
    print "Args needed: [estimation file] [tail sensitivity] [slope sensitivity]"
    sys.exit(0)

def actualapprox(data, index):
    offset = 0
    while offset < 100:
        if(index+offset in data):
            return data[index+offset]
        if(index-offset in data):
            return data[index-offset]
        offset = offset + 1

    raise Exception("No matching idx found")

def minVar(data):
    thresh = numpy.var(data[1:20])**.5
    candidate = range(len(data))
    candidate.reverse()
    for i in candidate:
        if(data[i] < (int(sys.argv[2]) * thresh) + numpy.mean(data[1:20])):
            return data[:i]
    raise Exception("No variance change found:" + str(thresh))

#timeseries = {}
#with open(sys.argv[3]) as f:
#    for line in f.readlines():
#        entry = line.split();
#        timeseries[int(entry[0])] = (int(entry[1]), float(entry[2]))

#with open(sys.argv[2]) as f:
#    idx = []
#    for line in f.readlines():
#        idx.append(int(line))

with open(sys.argv[1]) as f:
    c = 0
    basket = []
    estimated_result = 0
    estimated_lms = 0
    cnt=0
    for line in f.readlines():
        content = line.split()
        basket.append(content[8])

        if(content[0] == '9.60'):
            cnt=cnt+1;
            #estimated_lms= estimated_lms+lms.lms(map(float,basket))

            #bitrate = iterlms.iterlms(scipy.linspace(0.1,9.6,96), map(float,basket), len(basket)/3, 0.25);
            basket = map(float, basket)
            basket = minVar(basket)
            try:
                bitrate = ransac.findFitMaxX(scipy.linspace(0.1,0.1+0.1*(len(basket)-1),len(basket)), basket, float(sys.argv[3]))
                currentMin = c + int((bitrate-0.1)*10)
                c = int(c + (9.7-0.1)*10)
                #time,actual = actualapprox(timeseries, idx[currentMin])
                #print time,idx[currentMin],bitrate,10.-actual
                estimated_result = estimated_result + bitrate
                
                basket = []
            except ValueError:
                print "No convergence, skipping"
                basket = [] 

    estimated_result = estimated_result / cnt
    #estimated_lms = estimated_lms / cnt
    print '-----available bandwidth----'
    print estimated_result
    print '----------------------------'
