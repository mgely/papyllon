################################
#       DESCRIPTION
################################

#Set of functions to navigate through the qubit parameter space.
#assums the PNA and Adwin are already setup


################################
#       DEVELOPMENT NOTES/LOG
################################



################################
#      IMPORTS
################################

import qt
import numpy as np
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
import pylab
#execfile('metagen2D.py')
execfile('metagen3D.py')
execfile('support_functions.py')


def find_bias_point(n=0, phi_chi=1, phi_coarse=-6.8):
    '''
    Algorithm to tune the qubit to the charge sweetspot (n=0) and with a
    stark shifted cavity of phi_chi [MHz]. Here the qubit is above the cavity
    '''

    #set course phi
    #adwin.set_DAC_2(phi_coarse)

    v_gate = gatescan_sweetspot_detect(datadir)


def gatescan_sweetspot_detect(phi=-6.8,gate_list=np.linspace(-2,2,61), min_stark_shift=.5e6, plot=True, savefig=True, f_cw=5.3218e9):
    '''
    Do a rough gate scan to find the charge sweetspot. Returns the gate voltage
    for the sweetspot. It assumes the qubit parabola is above the cavity and
    causes a significant stark shift.
    '''

    #do coarse gate_scan
    peak_list=[]

    adwin.set_DAC_2(phi)

    for gate in gate_list:

        adwin.set_DAC_1(gate)
        pna.trigger(1)
        pna.auto_scale(window=1,trace=1)
        peak_list.append((eval(pna.get_peak())-f_cw)/1e6)

    np_list = np.array(peak_list)
    delta=np_list.mean() - np_list.min()
    print 'max delta: ' + str(round(delta,2)) + ' mean deviation from f_cw: ' + str(round(np_list.mean(),2)) + ' minimum: ' + str(round(np_list.min(),2)) + ' MHz'

    if(plot):

        pylab.autoscale(tight=True)
        pylab.plot(peak_list)
        pylab.show()


    if(delta
    return np_list
    
    

def sweetspot_optimize():
    '''
    Detailed scan of the stark parabola and finds the sweetspot. Assumes the
    qubit is already biased near the sweet spot.
    '''

    
    
