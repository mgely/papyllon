# Soufian's read_out and fit module

import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# This function reads in a txt file and makes of each line an element of a list.
# The function sorts the colums in each list and returns 2 colums back

def read_data(filepath):
    numbers = ["0","1","2","3","4","5","6","7","8","9"]

    f = open(filepath)
    a = f.readlines()
    c = []
    # read out which number lines are white lines and the next line is data point
    for i in range(len(a) - 1):
        if a[i] == '\n' and a[i+1][0] in numbers:
            c.append(i)
    # So we know that the number of blocks in de file is equal to len(c)

    # Making lists for each block of data
    num_lists = int(len(c))
    lists=[]

    for p in range(num_lists):
        lists.append([])
        
    # filling each block of data in 1 block
    for i in range(len(c)):
        lists[i] = a[c[i]+1:c[i] + 2002]

    # Making and filling the lists with the lines splitted

    splitlists = []

    for p in range(num_lists):
        splitlists.append([])

    for i in range(len(c)):
        for j in range(len(lists[i])):
            splitlists[i].append(lists[i][j].split())

    # filtering out the right colums

    xlists = []
    ylists = []

    for p in range(num_lists):
        xlists.append([])

    for i in range(len(c)):
        for j in range(len(splitlists[i])):
            xlists[i].append(splitlists[i][j][0])
            
    for p in range(num_lists):
        ylists.append([])

    for i in range(len(c)):
        for j in range(len(splitlists[i])):
            ylists[i].append(splitlists[i][j][2])

    # Mapping the strings in xlists and ylists to floats

    xfloat_lists = []
    yfloat_lists = []

    for p in range(num_lists):
        xfloat_lists.append([])

    for i in range(len(c)):
        xfloat_lists[i] = map(float, xlists[i])

    for p in range(num_lists):
        yfloat_lists.append([])

    for i in range(len(c)):
        yfloat_lists[i] = map(float, ylists[i])

    data_x = []
    data_y = []

    for i in range(len(c)):
        data_x.append(xfloat_lists[i])

    for i in range(len(c)):
        data_y.append(yfloat_lists[i])
        
    return [data_x,data_y]

# functie die de frequentie van de piek aangeeft

def find_fr(xy_data):
    maxx = max(xy_data[1])
    p = [0.001, 0.0025, xy_data[0][xy_data[1].index(maxx)], 1000000.0]
    
    if maxx < 0.0020:
        a = xy_data[0][xy_data[1].index(maxx)]

    elif maxx > 0.0020:
        def func(x,a,b,c,d):
            return a + (b/np.pi)/(1.0 + ((x-c)/d)**2)
    
        popt, pcov = curve_fit(func,xy_data[0],xy_data[1],p)
        a = popt[2]
    return a


