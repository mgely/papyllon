

################################
#       DESCRIBTION
################################

#Measurement script that does double tone qubit spectroscopy using the SGMA
#as the swept probe frequency


################################
#       DEVELOPMENT NOTES/LOG
################################


#transform into virtual spectrum analyser module
#way to find the path to write offset vector file
#metafile=open('%s.meta.txt' % data.get_filepath()[:-4], 'w')



################################
#      IMPORTS
################################

import qt
import numpy as np
import scipy as sp
import os
from numpy import pi, random, arange, size, array, sin, cos, diff, absolute,zeros, sign,ceil,sqrt,absolute
from time import time, sleep, localtime, strftime
#from scipy.optimize import curve_fit

import data_analyses_vers2 as da

execfile('metagen2D_souf.py')
execfile('metagen3D_ben_souf.py')


################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec

#magnetic field
v_adwin=-10
mag_start=-10
mag_stop=-10
mag_points= 1

maglist=np.linspace(mag_start,mag_stop,mag_points)

#PNA_coarse sweep
start_freq_coarse = 5.50e9
stop_freq_coarse =5.80e9
f_points_coarse =601
bandwidth_coarse=100
power_coarse=-10
ave_coarse=1
#96attenuation outside

flist_coarse=np.linspace(float(start_freq_coarse),float(stop_freq_coarse),f_points_coarse)

# PNA_fine sweep
delta_cav=10e6
f_points_fine =101
bandwidth_fine=100
power_fine=-10
ave_fine=1

flist_std=np.linspace(float(-delta_cav),float(delta_cav),f_points_fine)

#probe_fine_sweep
delta_probe=200
probe_points=800
probe_power=0

plist_std=np.linspace(float(-delta_probe),float(delta_probe),probe_points)


################################
#       QUBIT PREDICTOR
################################

#def qubit_freq_predictor(flux):
  #  return a+b*flux


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP0::A-N5221A-11075::inst0::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'sgs' not in instlist:
    sgs = qt.instruments.create('sgs','RS_SGS100A', address='TCPIP::192.168.1.100::INSTR')

if 'smb' not in instlist:
    smb = qt.instruments.create('smb', 'RS_SMB100A_DEV', address='TCPIP::192.168.1.50::INSTR')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


#measurement information stored in manual in MED instrument
med.set_device('EOS4_standard_transmon_B')
med.set_setup('BF')
med.set_user('Soufian & Sal')

#print smb.query('*IDN?')
#print fsl.query('*IDN?')


#PNA initialization
pna.reset()
pna.setup(start_frequency=start_freq,stop_frequency=stop_freq)
pna.set_power(power)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
sweeptime = pna.get_sweeptime()*1.01
pna.set_averages_on()
pna.set_averages(ave)

#SGS initialization (  alization?)
smb.set_RF_frequency(1000)
smb.set_RF_state(True)
smb.set_RF_power(probe_power)

#SGS initialization
#sgs.set_RF_state(False)
#sgs.set_RF_power(probe_power)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
spyview_process(reset=True) #clear old meta-settings

#Set up data for coarse sweep
filename_cavity = 'bf_souf_qubit_spectroscopy_cavity'
cavitydata = qt.Data(name=filename_cavity)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
cavitydata.add_coordinate('Frequency (Hz)')
cavitydata.add_coordinate('V_adwin (V)')
cavitydata.add_value('Transmission (dBm)')
cavitydata.add_value('f_data [dBm]')
cavitydata.add_value('Phase')
cavitydata.add_value('fitted_data (dBm)')

#hoe slaan we de fitwaardes het makkelijkst op?? Een aparte ASCII file misschien?

cavitydata.create_file()
cavitydata.copy_file('bf_souf_qubit_spectroscopy.py')

#Set up data for fine sweep
filename_qubit = 'bf_souf_qubit_spectroscopy_qubit'
qubitdata = qt.Data(name=filename_qubit)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
qubitdata.add_coordinate('Cavity Frequency (Hz)')
qubitdata.add_coordinate('V_adwin (V)')
qubitdata.add_coordinate('Probe_frequency (MHz)')
qubitdata.add_value('Transmission (dBm)')
qubitdata.add_value('f_data [dBm]')
qubitdata.add_value('Phase')

qubitdata.create_file()
qubitdata.copy_file('bf_souf_qubit_spectroscopy.py')

# Save vector data. Stil need to define path



vector_file = open(os.path.abspath("/qtlab/new/vector_file.txt"),"w+")

########################################
###         MEASUREMENT LOOP
########################################

#variables
run_index=0
tstart = time()

x_time = 0
y_temp =0
measurement_time=0

print 'Start Experiment'

def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    

#variables
run_index=0
tstart = time()

prev_time=tstart
now_time=0
exp_number = len(maglist)*ave


#set ADWIN to right value:


adwin.set_DAC_2(v_adwin)
ave_list=np.linspace(1,ave,ave)


for mag in maglist:

    #set magnetic field
    adwin.set_DAC_2(mag)

    print mag, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]
    
    ##################################
    ## Do cavity detection
    ##################################
    #clear pna
    pna.reset_averaging()
    
    for i in ave_list:
        print 'sweep', i        
        pna.sweep()
        pna.auto_scale()
        qt.msleep(sweeptime)
    trace_sweep1=pna.fetch_data(polar=True)
    tr2=pna.data_f()
    #tr2_parsed = pna.parse_trace(tr2)

    ###################################
    ## Fit cavity frequency
    ###################################
    # Op deze manier de data van de fit opslaan??
    fit_parameters = da.fit_lorentzian(flist,trace_sweep1[0])
    fitted_data = da.lorentzian(flist,*fit_parameters)

    #Store sweep
    cavitydata.add_data_point(flist, list(mag*ones(len(flist))),trace_sweep1[0],tr2,trace_sweep1[1],fitted_data)

    cavitydata.new_block()
    spyview_process_2D(cavitydata,start_freq,stop_freq,magv)
    qt.msleep(0.01) #wait 10 usec so save etc
    #write fitting parameter in ACSII vector_offset file

    #qubit_freq_predictor(mag)
    cavity_freq_0 = fit_parameters[2]
    probe_freq_0 = cavity_freq_0/1e6 + 675
    #vector_file.write(str(probe_freq_0),str(cavity_freq_0)"\n")
    
    ####################################
    ## Do qubit detection
    ####################################
        
    f_small_start = cavity_freq_0 - delta_cav
    f_small_stop = cavity_freq_0 + delta_cav

    f_small_list = np.linspace(f_small_start,f_small_stop,f_points_fine)
    #predict window of f_qubit, probepoints moet boven gedefineerd worden, units SGS zijn Mhz (y-as)

    #f_probe_start = probe_freq_0 - delta_probe 
    #f_probe_stop = probe_freq_0 + delta_probe

    f_probe_start=cavity_freq_0/1e6 + 675
    f_probe_stop=cavity_freq_0/1e6 + 275
    
    f_probe_list = np.linspace(f_probe_start,f_probe_stop,probe_points)


    #now sweep the probelist
    spyview_process_3D(qubitdata,f_points_fine,f_small_start,f_small_stop,
                probe_points,f_probe_start,f_probe_stop,
                mag_points,mag_start,mag_stop)
    print cavity_freq_0

    pna.reset()
    pna.setup(start_frequency=f_small_start,stop_frequency=f_small_stop)
    pna.set_power(power_fine)
    pna.set_resolution_bandwidth(bandwidth_fine)
    pna.set_sweeppoints(f_points_fine)
    sweeptime_fine = pna.get_sweeptime()*1.01
    pna.set_averages_on()
    pna.set_averages(ave_fine)
    
    for probe in f_probe_list:
        smb.set_RF_state(True)
        print probe, 'estimated ready at:', localtime(tstart+exp_time)[3], ':', localtime(tstart+exp_time)[4], ':', localtime(tstart+exp_time)[5]

        ###########################################
        #       SET MACHINE PARAMETERS
        ###########################################

        ave_list_fine=np.linspace(1,ave_fine,ave_fine)
        
        #set SGS
        smb.set_RF_frequency(probe)

        #set PNA
   


        #do pna.sweep
        pna.reset_averaging()
    
        for i in ave_list_fine:
            print 'sweep', i        
            pna.sweep()
            qt.msleep(sweeptime_fine)
            pna.auto_scale()
        trace_sweep_fine=pna.fetch_data(polar=True)
        tr2_fine=pna.data_f()
        
        #store data

        qubitdata.add_data_point(flist_std, list(mag*ones(len(flist_std))),list(probe*ones(len(flist_std))),trace_sweep_fine[0],tr2_fine,trace_sweep_fine[1])
        qubitdata.new_block()
        
        qt.msleep(0.01) #wait 10 usec so save etc
        
        ###################################
        ## Evt. Fit Qubit Frequency
        ###################################    
        
        

data.close_file()
vector_file.close()
qt.mend()
###end of experiment routine

