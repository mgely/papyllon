##############################
##      Instrument setup for two tone
##############################


#setup PNA & Adwin for two tone spectroscopy

################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A_sal', address='TCPIP::192.168.1.42::INSTR')

if 'med' not in instlist:
    med = qt.instruments.create('med','med')

if 'adwin_DAC' not in instlist:
    adwin = qt.instruments.create('adwin', 'ADwin_DAC',address=0x255)

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)




start_probe=6.5e9
stop_probe=9e9
f_points_probe=501
ifbw_probe=100
f_cw=6.2689e9
pow_cw=0
pow_probe=30
aver_probe=1

#set adwin to slow sweeping, don't forget to build slower in the scripts ---> Fast sweeping also works thus we maintain that

adwin.start_process()       #starts the DAC program
adwin.set_rampsteps(1)


#setup two windows
pna.reset()


#setup two displays
pna.w("DISP:WIND1:STATE ON")
pna.w("DISP:WIND2:STATE ON")

###setup cavity scan (magnitude)
pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_S1', 'B,1'")
pna.w("DISP:WIND1:TRACE1:FEED 'CH1_S21_S1'")
pna.w("CALC1:PAR:SEL 'CH1_S21_S1'")
pna.w("CALC1:FORM MLOG")

#setup triggering per channel
pna.w("INIT:CONT OFF")
pna.w("SENS1:SWE:MODE HOLD")
pna.w("TRIG:SCOP CURR")


#do settings for cavity tone
pna.w("SENS:FREQ:START %s" % (bias_start_cav))
pna.w("SENS:FREQ:STOP %s" % (bias_stop_cav))
pna.w("SENS:SWE:POIN %s" % (bias_f_points))
pna.w("SENS:BWID %s" % (bias_ifbw))
pna.w("SOUR:POW1 %s" %(bias_pow))

#do settings for Marker on the cavity tone
pna.w("CALC1:MARK:REF ON")
pna.w("CALC1:MARK:REF:X " + str(w_bare))
pna.w("CALC1:MARK1 ON")
pna.w("CALC1:MARK1:FUNC MIN")
pna.w("CALC1:MARK1:FUNC:TRAC ON")
pna.w("CALC1:MARK1:DELT ON")

#do settings for averaging of bias monitor
pna.w("SENS1:AVER 1")
pna.w("SENS1:AVER:MODE SWE")
pna.w("SENS1:AVER:COUN %s" % (bias_aver_cav))

def to_MHz(string):
    return str(round(string/1e6,2))

def to_kHz(string):
    return str(round(string/1e3,2))

def to_GHz(string):
    return str(round(string/1e9,2))

def check_bias(continuous=False, error=3e6, f_target=6.25e9):
    '''
    Function that checks if the cavity tone still has the desired Stark shift.
    '''
    pna.reset_averaging()               #change to only resetting for channel 1 to avoid future errors
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")
    pna.w("CALC1:MARK:REF:X " + str(f_target))
    
    
    for i in np.linspace(1,1,aver_cav):
        #print 'trigger'
        pna.trigger(channel=1)
        pna.auto_scale(window=1,trace=1)

    peak=eval(pna.q("CALC1:MARK1:X?"))
    print 'Magv \t' + str(round(adwin.get_DAC_1(),2)) +'\t Distance to target[MHz]: \t' + to_MHz(peak)

    if(continuous):
            print 'set channel 1 to continuous'
            pna.w("SENS1:SWE:MODE CONT")
            pna.w("INIT:CONT ON")
        
    #if(abs(peak-chi)<error):
    if(abs(peak)<error):
        print 'Bias point is still within error limit'
        return True
    else:
        print 'Bias point is out of value'
        return False



def check_bias_manual_power(continuous=False, error=150e3, power=-30,aver=40):
    '''
    Function that checks if the cavity tone still has the desired Stark shift.
    '''
    pna.reset_averaging()               #change to only resetting for channel 1 to avoid future errors

    pna.w("SOUR:POW1 %s" %(power))
    pna.w("SENS1:AVER:COUN %s" %(aver))

    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")

    
    
    for i in np.linspace(1,1,aver):
        print 'trigger'
        pna.trigger(channel=1)
        pna.auto_scale(window=1,trace=1)

    peak=eval(pna.q("CALC1:MARK1:X?"))
    print 'Gate \t' + str(round(adwin.get_DAC_1(),2)) +'\t Starkshift: \t' + to_MHz(peak) + '\t Chi_target ' + to_MHz(chi) + '\t error: ' + to_MHz(peak-chi)

    #set back the values of power and averaging
    pna.w("SOUR:POW1 %s" %(pow_cav))
    pna.w("SENS1:AVER:COUN %s" %(aver_cav))

    if(continuous):
            print 'set channel 1 to continuous'
            pna.w("SENS1:SWE:MODE CONT")
            pna.w("INIT:CONT ON")
        
    if(peak<chi):
        print 'Bias point is still within error limit'
        return True
    else:
        print 'Bias point is out of value'
        return False

def find_fb_bias(continuous=False,error=150e3,chi=-900e3,center_gate_index=40, max_iteration=80):
    '''
    Search around old bias, with feedback, to find the new correct bias point.
    '''
    close_index=center_gate_index
    for i in np.linspace(1,1,max_iteration):

        #check chi for center_gate_index+1

        #check chi for center_gate_index-1

        #which one is closer then move to that one.

        #is that one within the error? then return that one. Now we can still improve on step size.
        print 'bla'
    

def find_max_chi_qubit_above(chi_treshold=-200e3, max_interation=100, max_time=60, coarse_step=0.25, step_factor=20):
    '''
    Routine to search for the maximum AC stark shift (negative) when the qubit line is biased above the cavity
    chi_treshold = value for which we know we are close to n_g is integer
    coarse_step = step_size of the coarse gate_scan
    step_factor = the refining factor from coarse to med to fine step size search

    returns a bool
    '''
    start = time()
    iteration_index=0
    unfinished=True


    print 'Find max chi with qubit above'
    while(True):
        #update variables
        iteration_index=iteration_index+1
        interval = time()-start

        #check if conditions are still valid
        if(interval>max_time):
            print 'search time has exceeded max_time ', str(max_time), 'aborting'
            return False
        if(iteration_index>max_iteration):
            print 'number of iterations passed max number of iterations: ', str(max_iteration)
            return False
        
        print 'Iteration: ', str(iteration_index)

        if(find_coarse_bias_qubit_above):
            #go and find the med
            print 'bla'

def gate_scan(printout=True,gate_list=np.linspace(-2.25,2.25,81)):
    '''
    Function that performs a gatescan over the gate list, it returns the sweetspot + the complete Chi list
    '''
    chi_list= []
    for index, gate in enumerate(gate_list):
        adwin.set_DAC_1(gate)
        qt.msleep(0.01)
        chi_list.append(measure_chi(printout=False))
        #if(printout):
        print 'V_g: ', str(round(gate,2)), '\t Chi:' + to_kHz(chi_list[index]) + ' kHz' 

        #if(printout):
        
        #for index, gate in enumerate(gate_list):
            #print 'V_g: ', round(str(gate,2)), '\t Chi:' + chi_list[index]
    chi_array = np.array(chi_list)
    chi_min = chi_array.min()
    gate_min = gate_list[np.where(chi_array==chi_min)[0][0]]
    print 'charge sweet spot has a chi of: ' + to_kHz(chi_min) + '\t at Voltage: ' + str(round(gate_min,2))
            
    return [chi_list, gate_list, chi_min,gate_min]

def measure_chi(printout=True, averages=1, voltage=None):
    '''
    function that returns the ac-strark shift.
    '''

    if(voltage!=None):
        print 'set Vg to ' + str(round(voltage,2))
        adwin.set_DAC_1(voltage)
    
    #set continuous off
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")

    pna.reset_averaging()
        
    for i in np.linspace(1,1,averages):
        pna.trigger(channel=1)
        pna.auto_scale(window=1,trace=1)

    peak=eval(pna.q("CALC1:MARK1:X?"))

    #if(printout):
    #    print 'V_g: ' + str(round(adwin.get_DAC_1(),2)) +'\t Chi: \t' + to_kHz(peak) +' kHz'
    return peak
        

def find_balanced_bias(continuous=False,error=3e6,chi=-900e3, center_gate_index=40):
    '''
    Search iterative around the given center_gate value in steps first below than higher. etc
    '''

    if(center_gate_index==0):
        return False

    if(center_gate_index==len(gatelist)-1):
        return False

    
    #create a balanced list around the original gate_value
    balanced_gate_list = np.hstack(zip(gatelist[center_gate_index:0:-1],gatelist[center_gate_index:-1:1]))

    balanced_gate_list=balanced_gate_list[1:-1:1] #remove double element
    #print balanced_gate_list
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")
    print 'find_balanced_bias'
    for gate in balanced_gate_list:

        adwin.set_DAC_1(gate)
        pna.reset_averaging()
        

        for i in aver_cav_list:
            pna.trigger(channel=1)
            pna.auto_scale(window=1,trace=1)
        peak=eval(pna.q("CALC1:MARK1:X?"))
        print 'Gate \t' + str(round(gate,2)) +'\t Starkshift: \t' + to_MHz(peak) + '\t Chi_target ' + to_MHz(chi)
        #if(abs(peak-chi)<error):
        if(peak<chi):
            print 'Reached bias point'
            if(continuous):
                print 'set channel 1 to continuous'
                pna.w("SENS1:SWE:MODE CONT")
                pna.w("INIT:CONT ON")
                
                
            return True
    print 'With given balanced gatelist the desired starkshift could not be found'
    return False



def find_charge_sweet_spot(chi_target=-900e3, gate_step=0.05):
    '''Function to find the max AC-Stark shift
    '''

    print 'find chi max, assumes qubit is above'
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")
    print 'find_bias'

    current_gate = adwin.get_DAC_1()
    #detect trend
    chi = measure_chi()

    adwin.set_DAC_1(current_gate+4*gate_step)
    qt.msleep(0.01)
    chi_2 = measure_chi()
    
    current_gate = adwin.get_DAC_1()
    trend = None
    trend_first_change = False
    trend_change = False
    
    if(chi>chi_2):
        print 'trend is downwards in gate'
        trend = -1

    else:
        print 'trend is upwards in gate'
        trend = 1
        
    chi=chi_2
    while(trend_change ==False):
        'walk the ladder'
        adwin.set_DAC_1(current_gate+trend*gate_step)
        chi_2 = measure_chi()
        if(chi_2<chi):
            print'trend persists'
        else:
            if(trend_first_change):
                print 'detect reverse of trend (after second step)'
                trend_change = True
            else:
                print 'detect first change in trend'
                trend_first_change =True
    adwin.set_DAC_1(current_gate+2*trend_gate_step)
    chi_last=measure_chi()
    #build in a last check whether this is close to the lowest chi found
    return chi_last
        
find_bias_bool=False
last_find_bias_error=None

def find_fast_bias(continuous=False,error=1e6,f_target=6.269e9):
    print 'blabla'

def find_bias(continuous=False,error=3e6,f_target=6.26e9):
    '''
    Function to find the magnetic Voltage such that cavity stark shifted away from the
    bare cavity. 
    '''
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")
    pna.w("CALC1:MARK:REF:X " + str(f_target))

    
    print 'find_current_bias'
    for magv in magvlist:

        adwin.set_sec_DAC_1(magv)
        pna.reset_averaging()
        

        for i in bias_aver_cav_list:
            pna.trigger(channel=1)
            pna.auto_scale(window=1,trace=1)
        peak=eval(pna.q("CALC1:MARK1:X?"))
        print 'Magv \t' + str(round(magv,2)) +'\t f_target[MHz]: \t' + to_MHz(f_target) + '\t error[MHz]: \t' + to_MHz(peak)
        #if(abs(peak-chi)<error):
        if(abs(peak)<error):
            print 'Reached bias point'
            if(continuous):
                print 'set channel 1 to continuous'
                pna.w("SENS1:SWE:MODE CONT")
                pna.w("INIT:CONT ON")
                
                
            return True
    print 'With given gatelist the desired starkshift could not be found'
    return False



def pna_cont(boo):
    if(boo):
        
        pna.w("SENS1:SWE:MODE CONT")
        pna.w("INIT:CONT ON")
    else:
        pna.w("SENS1:SWE:MODE HOLD")
        pna.w("INIT:CONT OFF")
 

###setup cavity (real)
##pna.w("CALC1:PAR:DEF:EXT 'CH1_S21_REAL','S21'")
##pna.w("DISP:WIND1:TRACE2:FEED 'CH1_S21_REAL'")
##pna.w("CALC1:PAR:SEL 'CH1_S21_REAL'")
##pna.w("CALC1:FORM REAL")
#qt.msleep(20)       #wait for first trace to complete
##pna.w("DISP:WIND1:TRACE2:Y:SCAL:AUTO")
##pna.w("DISP:WIND1:TRACE1:Y:SCAL:AUTO")

##
###setup two tone scan
pna.w("CALC2:PAR:DEF:EXT 'CH2_S21_S1', 'B,1'")
pna.w("DISP:WIND2:TRACE1:FEED 'CH2_S21_S1'")
pna.w("CALC2:PAR:SEL 'CH2_S21_S1'")
pna.w("CALC2:FORM MLOG")
##
pna.w("SENS2:FREQ:START %s" % (start_probe))
pna.w("SENS2:FREQ:STOP %s" % (stop_probe))
pna.w("SENS2:SWE:POIN %s" % (f_points_probe))
pna.w("SENS2:BWID %s" % (ifbw_probe))

###still switch averaging on
##
##
pna.w("SENS2:FOM:STATE 1")      #switch on Frequency Offset Module
pna.w("SENS2:FOM:RANG3:COUP 0")     #decouple Receivers
pna.w("SENS2:FOM:RANG2:COUP 0")     #decouple Source 
##
pna.w("SENS2:FOM:RANG3:SWE:TYPE CW")    #set Receivers in CW mode
pna.w("SENS2:FOM:RANG2:SWE:TYPE CW")    #set Source in CW mode
##
pna.w("SENS2:FOM:RANG3:FREQ:CW %s" %(f_cw)) #set cw freq to receivers
pna.w("SENS2:FOM:RANG2:FREQ:CW %s" %(f_cw)) #set cw freq to source1
##
pna.w("SENS2:FOM:DISP:SEL 'Primary'")       #set x-axis to primary 
##
pna.w("SOUR2:POW:COUP 0")                   #decouple powers
pna.w("SOUR2:POW1 %s" %(pow_cw))
pna.w("SOUR2:POW3 %s" %(pow_probe))
pna.w("SOUR2:POW3:MODE ON")                 #switch on port3

pna.w("SENS2:AVER 1")
pna.w("SENS2:AVER:MODE POIN")
pna.w("SENS2:AVER:COUN %s" % (aver_probe))

