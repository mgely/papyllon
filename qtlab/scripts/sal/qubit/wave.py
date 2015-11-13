############################################
# Rabi Oscillation
#
#
#

import numpy as np


def addnoise(x, variance):
    return x+variance*random.randn(size(x))

def tone(frequency, sample_rate=1e9, number_of_waves=100,variance=0):
    '''Create Tone to send to AWG'''
    Nsamples=int(number_of_waves*sample_rate/(frequency))

    T_total=number_of_waves/frequency

    tlist=np.linspace(0,T_total,Nsamples)

    markerlist=np.linspace(1,1,Nsamples)


    return addnoise(np.sin(2*np.pi*frequency*tlist),variance)
    
    


def waveform(f_AWG=30,t_relax=4000,t_pulse=100,t_measure=400,delta_stitch=0):
    '''Create waveform, plus marker traces in the form [waveform,m1,m2],
    default values are f_AWG=30 MHz, t_relax=4000ns, t_pulse=100ns, other wise
    the format is  [pulse_length, t_wait, pulse_length, t_wait, ...]
    '''
    
    wave = []
    marker1 = []
    marker2 = []
    
    relax = np.linspace(0.0,0.0,t_relax).tolist()
    marker1_relax = np.linspace(0,0,t_relax).tolist()
    marker2_relax = np.linspace(0,0,t_relax).tolist()

    pulse=[]
    marker1_pulse = np.linspace(0,0,t_pulse).tolist()
    marker2_pulse = np.linspace(0,0,t_pulse).tolist()

    measure = np.linspace(0.0,0.0,t_relax).tolist()
    marker1_measure = np.linspace(1,1,t_measure).tolist()
    marker2_measure = np.linspace(0,0,t_measure).tolist()
    
    for i in range(len(relax)):
        wave.append(relax[i])

    for i in range(len(marker1_relax)):
        marker1.append(marker1_relax[i])

    for i in range(len(marker2_relax)):
        marker2.append(marker2_relax[i])

    for i in range(len(marker1_pulse)):
        marker1.append(marker1_pulse[i])

    for i in range(len(marker2_pulse)):
        marker2.append(marker2_pulse[i])
        
    for i in range(len(measure)):
        wave.append(measure[i])
        
    for i in range(len(marker1_measure)):
        marker1.append(marker1_measure[i])

    for i in range(len(marker2_measure)):
        marker2.append(marker2_measure[i])

    return awg.sendwaveform(wave,marker1,marker2,'wave.pat',1000000000)



