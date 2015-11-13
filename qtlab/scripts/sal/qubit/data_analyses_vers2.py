##################################################
# Soufian's read_out and fit module
#
# Development notes:
# 1) read_data is possibly very slow for big files, because it reads in complete file at once.
#
#



import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy import special

def read_data(filepath,column_sorted=True, float_conversion=True):
    '''This function reads in a standard qtlab *.dat file, and returns a
    a list of the following format: data[block_number][column_nr][line_item] (columnsorted true)
    and data[block_number][line_item][column_nr] (column_sorted false).
    Makes of each data line an element of a list.
    The function sorts the colums in each list and returns 2 colums back.
    Possibly function is very slow on large dat files.'''


    #help variable to skip header part of the *.dat file.
    numbers = ["0","1","2","3","4","5","6","7","8","9"]

    file_object = open(filepath)
    data = file_object.readlines()
    block_list = []
    count_list = []
    
    #construct block list
    for i in range(len(data) - 1):
        if data[i] == '\n':
            count_list.append(i)
    
    for i in range(len(data) - 1):
        if data[i] == '\n' and data[i+1][0] in numbers:
            block_list.append(i)
    # So we know that the number of blocks in de file is equal to len(c)
    
    # Making lists for each block of data, whereby format lists[blocknr][lineitem]
    
    number_of_blocks = int(len(block_list))
    lists=[]

    for p in range(number_of_blocks):
        lists.append([])

        
    # filling each block of data in 1 block
    for i in range(len(block_list)):
        lists[i] = data[block_list[i]+1:block_list[i] + (count_list[2] - count_list[1])]
    
    # Making and filling the lists with the lines splitted format: splitlist[blocknr][line_item][column_nr]

    splitlists = []

    for p in range(number_of_blocks):
        splitlists.append([])

    for i in range(len(block_list)):
        for j in range(len(lists[i])):
            splitlists[i].append(lists[i][j].split())

    number_of_lines=int(len(splitlists[0]))
    number_of_columns=int(len(splitlists[0][0]))
    
    if(column_sorted==False):

        #implement float mapping
        if(float_conversion==True):
            return_data=[]
            for i in range(number_of_blocks):
                return_data.append([])
                for j in range(number_of_lines):
                    return_data[i].append(map(float,splitlists[i][j]))
            return return_data
            
                
        return splitlists

    #Do a column sort



    return_data=[]

    for i in range(number_of_blocks):
        return_data.append([])
        for j in range(number_of_columns):
            return_data[i].append([])

    for i in range(number_of_blocks):
        for j in range(number_of_columns):
            for k in range(number_of_lines):
                return_data[i][j].append(splitlists[i][k][j])

    if(float_conversion==True):
        final_data=[]
        for i in range(number_of_blocks):
            final_data.append([])
            for j in range(number_of_columns):
              final_data[i].append(map(float,return_data[i][j]))
        return final_data

    return return_data

def fit_lorentzian(x_list,y_list):
    '''
    Function that fits a lorentzian to a list x-axis is x_list and y-axis is y_list
    '''
    
    maxx = max(y_list)
    ave=np.mean(y_list)
    std=np.std(y_list)
   
    #initial guess
    p = [ave,maxx, x_list[y_list.index(maxx)],np.std(x_list)]

    #result=[]
    
##    if maxx < (ave+2*std):
##        print 'fit seems problematic'
##        a = x_list[y_list.index(maxx)]
##        result.append(a)

##    elif maxx > (ave+2*std):
        
    popt, pcov = curve_fit(lorentzian,x_list,y_list,p)
##    
####        result.append(popt)
####        result.append(pcov)
####
####    for i in enumerate(y_list):
####        y_fit = lorentzian(x_list,*popt)
####        y_residual = y_list - y_fit
##    try:
####        print "Correlation Matrix :"
####        for i,row in enumerate(pcov):
####            for j in range(len(popt)) :
####                print "%10f"%(pcov[i,j]/np.sqrt(pcov[i,i]*pcov[j,j])),
####                    # Note: comma at end of print statement suppresses new line
####            print 
##        # Calculate Chi-squared
##        chisq = sum(((y_list-lorentzian(x_list,*popt))/1)**2)
##       # print chisq
####        print "\nEstimated parameters and uncertainties (with initial guesses)"
####        for i in range(len(popt)) :
####            print ("   p[%d] = %10.5f +/- %10.5f      (%10.5f)"
####                       %(i,popt[i],pcov[i,i]**0.5,
####                           p[i]))
##       
##    # If cov has not been calculated because of a bad fit, the above block
##    #   will cause a python TypeError which is caught by this try-except structure.
##    except TypeError:
##        print "**** BAD FIT ****"
##        print "Parameters were: ",popt
##        # Calculate Chi-squared for current parameters
##        chisq = sum(((y_list-func(x_list,*popt))/1)**2)
####        print "Chi-Squared/dof for these parameter values = %10.5f, CDF = %10.5f%%"\
####            %(chisq/dof, 100.*float(sp.special.chdtrc(dof,chisq)))
##        print "Uncertainties not calculated."
##        print
##        print "Try a different initial guess for the fit parameters."
##        print "Or if these parameters appear close to a good fit, try giving"
##        print "    the fitting program more time by increasing the value of maxfev."
##        chisq = None

    return popt

def gaussian(x,*p) :
    '''
    A gaussian peak with:
    Constant Background          : p[0]
    Peak height above background : p[1]
    Central value                : p[2]
    Standard deviation           : p[3]
    '''
    return p[0]+p[1]*np.exp(-1*(x-p[2])**2/(2*p[3]**2))
def lorentzian(x,*p) :
    ''' A lorentzian peak with:
     Constant Background          : p[0]
     Peak height above background : p[1]
     Central value                : p[2]
     Full Width at Half Maximum   : p[3]
     '''
    return p[0]+(p[1]/np.pi)/(1.0+((x-p[2])/p[3])**2)
def linear(x,*p) :
    '''A linear fit with:
      Intercept                    : p[0]
      Slope                        : p[1]
    '''
    return p[0]+p[1]*x
def power(x,*p) :
    '''A power law fit with:
     Normalization                : p[0]
      Offset                       : p[1]
      Constant                     : p[3]
    '''
    return p[0]*(x-p[1])**p[2]+p[3]
