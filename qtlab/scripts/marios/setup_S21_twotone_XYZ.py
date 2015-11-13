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

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


bias_start_cav = 7.5e9
bias_stop_cav = 8.5e9
bias_f_points =501
bias_ifbw = 1e3
bias_pow=-10
bias_aver_cav=1
aver_cav=2
w_bare=7.93e9
bias_aver_cav_list=np.linspace(1,1,aver_cav)


#start_probe=10e9
#stop_probe=9e9
#f_points_probe=501
#ifbw_probe=20
f_cw=7.923e9
pow_cw=0
#pow_probe=-25
aver_probe=1




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
#pna.w("INIT:CONT OFF")
#pna.w("SENS1:SWE:MODE HOLD")
#pna.w("TRIG:SCOP CURR")


#do settings for the bias monitor)
pna.w("SENS:FREQ:START %s" % (bias_start_cav))
pna.w("SENS:FREQ:STOP %s" % (bias_stop_cav))
pna.w("SENS:SWE:POIN %s" % (bias_f_points))
pna.w("SENS:BWID %s" % (bias_ifbw))
pna.w("SOUR:POW1 %s" %(bias_pow))

#do settings for Marker for the bias monitor
##pna.w("CALC1:MARK:REF ON")
##pna.w("CALC1:MARK:REF:X " + str(w_bare))
##pna.w("CALC1:MARK1 ON")
##pna.w("CALC1:MARK1:FUNC MIN")
##pna.w("CALC1:MARK1:FUNC:TRAC ON")
##pna.w("CALC1:MARK1:DELT ON")
##pna.w("CALC1:MARK2 ON")
##pna.w("CALC1:MARK2:FUNC MIN")
##pna.w("CALC1:MARK2:FUNC:TRAC ON")

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



def measure_cav(printout=True, averages=1, voltage=None):
    '''
    function that returns the ac-strark shift.
    '''

    if(voltage!=None):
        print 'set Vadwin to ' + str(round(voltage,2))
        adwin.set_DAC_1(voltage)
    
    #set continuous off
    pna.w("SENS1:SWE:MODE HOLD")
    pna.w("INIT:CONT OFF")

    pna.reset_averaging()
        
    for i in np.linspace(1,1,averages):
        pna.trigger(channel=1)
        pna.auto_scale(window=1,trace=1)

    pna.w("CALC1:MARK2:FUNC MIN")

    peak=eval(pna.q("CALC1:MARK2:X?"))

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

        adwin.set_sec_DAC_1(gate)
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

    adwin.set_sec_DAC_1(current_gate+4*gate_step)
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
        adwin.set_sec_DAC_1(current_gate+trend*gate_step)
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
    adwin.set_sec_DAC_1(current_gate+2*trend_gate_step)
    chi_last=measure_chi()
    #build in a last check whether this is close to the lowest chi found
    return chi_last
        

def find_bias(continuous=False,error=3e6,f_target=6.26e9, set_f_cw=True):
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
                
            if(set_f_cw):
                print 'set pna to f_cw found'
                pna_set_2tone_cw_f(f_target)
            
            return True
    print 'With given gatelist the desired starkshift could not be found'
    return False

def pna_set_2tone_cw_f(frequency):
    pna.w("SENS2:FOM:RANG3:FREQ:CW %s" %(frequency)) #set cw freq to receivers
    pna.w("SENS2:FOM:RANG2:FREQ:CW %s" %(frequency)) #set cw freq to source1
    
def pna_set_2tone_probe_power(power):
    pna.w("SOUR2:POW3 %s" %(power))

def pna_set_2tone_cw_power(power):
    pna.w("SOUR2:POW1 %s" %(power))
    pna.w("SOUR:POW1 %s" %(power))

def pna_set_2tone_probe_frequency(start_frequency=6.5e9,stop_frequency=11e9,points=1001,ifbw=100):
    pna.w("SENS2:FREQ:START %s" % (start_frequency))
    pna.w("SENS2:FREQ:STOP %s" % (stop_frequency))
    pna.w("SENS2:SWE:POIN %s" % (points))
    pna.w("SENS2:BWID %s" % (ifbw))

def pna_get_2tone_cw_f():
    return pna.q("SENS2:FOM:RANG3:FREQ:CW?")

def pna_autoscale():
    pna.w("DISP:WIND1:TRAC1:Y:SCAL:AUTO")
    pna.w("DISP:WIND2:TRAC1:Y:SCAL:AUTO")

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
pna.w("SENS2:AVER:MODE SWEEP")
#pna.w("SENS2:AVER:MODE POIN")
pna.w("SENS2:AVER:COUN %s" % (aver_probe))

pna.w("CALC2:MARK1 ON")
pna.w("CALC2:MARK1:FUNC MAX")
pna.w("CALC2:MARK1:FUNC:TRAC ON")
