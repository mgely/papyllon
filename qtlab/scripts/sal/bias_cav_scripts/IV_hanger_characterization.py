################################
#       DESCRIBTION
################################

#Script that measures the frequency response of a MW hanger and finds the Qc, Qi, fres
#it works as follows:

#you enter a scan_range, span
#first the PNA does a quick scan to find the resonance approximately
#then in a second scan the resonance is detailed measured and fitted




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
#execfile('metagen2D.py')
execfile('metagen3D.py')


from pylab import *
from scipy import *
from scipy import optimize
 

################################
#      VARIABLES
################################

#For internal instrument variables see instruments section

#Independent Variables
max_runtime = None #sec
max_sweeptime = None #sec



f_points =501
bandwidth=10
power = -30
averages=1

h_1=5.388e9


f_estimate=h_1
span=40.e6

#start_f=f_estimate-span/2.
#stop_f=f_estimate+span/2.

start_f=5.375e9
stop_f=5.4e9

f_list=np.linspace(start_f,stop_f,f_points)

iteration=1
iteration_list=np.linspace(1,1,iteration)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

##if 'pna' not in instlist:
##    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')
##
##if 'var_att' not in instlist:
##    var_att=qt.instruments.create('var_att','agilent_var_att', address='TCPIP::192.168.1.113::INSTR')

#if 'mysource' not in instlist:
#    mysource = qt.instruments.create('mysource', 'keysight_source_B2961A', address='USB0::2391::36632::MY52350262::0::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


pna.reset()
pna.setup(start_frequency=start_f,stop_frequency=stop_f,measurement_format = 'MLOG')
pna.set_power(power)
pna.set_averages(True)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)
pna.set_power(0)

################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

device_name = 'bias_cav_sapph_IV_4'
port_type = 'S22'


base_path = 'D:\\data\\Sal\\' + device_name + '\\' + port_type + '\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed

#Set up data
filename = 'IV_hanger_characterization'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('Power [dBm]')
data.add_coordinate('Voltage [V]')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')
data.add_value('Current drain [A]')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('IV_hanger_characterization.py')

total_path=base_path+date_path+'_____'+filename

spyview_process(reset=True)



########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'

Z_list=[1]

pna.set_power(0)
var_att.set_var_att(70)
#Y_list = np.linspace(90,20,36)
p_list=[]


#source settings
mysource.set_output_type('VOLT')
mysource.set_current_protection(100e-9)
mysource.set_protection_state(True)

mysource.set_state(True)

Y_list=[90,70]
Z_list=np.linspace(100,100,1)

def ramp_source_voltage(value, wait=0.00000001, step_size=0.015):
    print 'ramp source to ', value, '\n'
    
    ramp_d = value-mysource.get_bias_voltage() 

    ramp_sign = np.sign(ramp_d)

    ramp_bool = True
    while(ramp_bool):
        actual_value=mysource.get_bias_voltage()
        if(abs(value-actual_value)<0.018):
            mysource.set_bias_voltage(value)
            ramp_bool = False
        else:
            mysource.set_bias_voltage(actual_value+ramp_sign*step_size)
            qt.msleep(wait)
    return value
Y=0
#pna.set_
for Z in Z_list:
    
    new_outermostblockval_flag=True
    #adwin.set_DAC_1(gate)
    
    ramp_source_voltage(Z)
    qt.msleep(1)
    

    curr=mysource.get_measure_current()
    print 'voltage \t', Z, '\t current: \t' , curr, 'press enter to continue'
    bla = raw_input("enter something to continue")

    for Y in Y_list:
        var_att.set_var_att(int(Y))
        print var_att.get_var_att()
    

        #print magv
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        #var_att.set_var_att(int(Y))
        
        #Y=var_att.get_var_att()
        #print Y


        
        ave_list = np.linspace(1,averages,averages)
        #Set Voltage

        print 'sweep'
        pna.reset_averaging()
        for k in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
       
        tr2=pna.data_f()

        curr = mysource.get_measure_current()

        
        tr=list(0*ones(len(f_list)))
        
        #tr2_parsed = pna.parse_trace(tr2)
        data.add_data_point(f_list, list(Y*ones(len(f_list))),list(Z*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]), list(curr*ones(len(f_list))))
        #data.add_data_point(f_list, list(Y*ones(len(f_list))),list(Z*ones(len(f_list))),tr, tr, tr, list(curr*ones(len(f_list))))

        data.new_block()
        spyview_process(data,start_f,stop_f,Y_list[-1],Y_list[0],Z,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
        pna.auto_scale()
        #usage of ramy barends formula
        #format p: p[0]=w0, p[1]=Qi, p[2]=Qc, p[3]=unity transmission, p[4]=slope of transmission
        fitfunc_S21 = lambda p, x: p[3] + x*p[4] + 20*np.log10(np.abs((float(p[2])/float(p[2]+p[1])-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))/(1-2j*float(p[1]*p[2])/float(p[1]+p[2])*(f_list-p[0])/float(p[0]))))
        errfunc = lambda p,x, y: fitfunc_S21(p,x)-y
        p0= [f_estimate,350,500,-66,0.1]
        p1, success = optimize.leastsq(errfunc,p0[:],args=(array(f_list),array(tr2)))

        p1[1]=abs(p1[1])
        p1[2]=abs(p1[2])

        
        for z in p1:
            print z

        print '\n'

        p_list.append([Y,p1])
          
        pylab.plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,f_list),"r-")


        # Legend the plot
        pylab.title("Transmission response of " + device_name + ' ' + port_type)
        pylab.xlabel("frequency [Hz]")
        pylab.ylabel("S21 transmission [dB]")
        pylab.legend(('data', 'fit'))
 
        pylab.ax = axes()
 
        pylab.text(0.8, 0.1,'f_res :  %.4f GHz \n Qi :  %u \n Qc : %u \n unity: %.1f dBm' % (p1[0]*1e-9,p1[1],p1[2],p1[3]),
                    fontsize=10,
                    horizontalalignment='left',
                    verticalalignment='center',
                    transform=ax.transAxes)
    
        pylab.savefig(total_path + str(Y) +'_' + str(Z) + '.png')
        pylab.close()

##    df_list=[]
##    Qi_list=[]
##    Qc_list=[]
##    unity_list=[]
##    slope_list=[]
##
##    Ql_list=[]
##    kc_list=[]
##    ki_list=[]
##    kl_list=[]
##
##    
##    for i in p_list:
##        wc=i[1][0]
##        df_list.append(i[1][0])
##        Qi_list.append(i[1][1])
##        Qc_list.append(i[1][2])
##        unity_list.append(i[1][3])
##        slope_list.append(i[1][4])
##
##        Ql_list.append(1/(1/float(i[1][1])+1/float(i[1][2])))
##        kc_list.append(wc/float(i[1][2]))
##        ki_list.append(wc/float(i[1][1]))
##        kl_list.append(wc/float(i[1][2]+ wc/float(i[1][1])))
##
##    df_list=array(df_list)
##    Qi_list=array(Qi_list)
##    Qc_list=array(Qc_list)
##    unity_list=array(unity_list)
##
##    Ql_list=array(Ql_list)
##    kc_list=array(kc_list)
##    ki_list=array(ki_list)
##    kl_list=array(kl_list)
##
####    s11_table.append(Y_list)
####    s11_table.append(df_list)
####    s11_table.append(Qi_list)
####    s11_table.append(Qc_list)
####    s11_table.append(unity_list)
####    s11_table.append(Ql_list)
####    s11_table.append(kc_list)
####    s11_table.append(ki_list)
####    s11_table.append(kl_list)
##    s22_table.append(Y_list)
##    s22_table.append(df_list)
##    s22_table.append(Qi_list)
##    s22_table.append(Qc_list)
##    s22_table.append(unity_list)
##    s22_table.append(Ql_list)
##    s22_table.append(kc_list)
##    s22_table.append(ki_list)
##    s22_table.append(kl_list)
##
##    pylab.plot(Y_list,df_list*1e-9)
##    pylab.title(date_path + "frequency")
##    pylab.xlabel("power")
##    pylab.ylabel("frequency [GHz]")
##    pylab.savefig(total_path+ 'freq' + '.png')
##    pylab.close()
##
##
##    pylab.plot(Y_list,(df_list-df_list[0])*1e-3)
##    pylab.title(date_path + "frequency shift")
##    pylab.xlabel("power")
##    pylab.ylabel("frequency [kHz]")
##    pylab.savefig(total_path+ 'freqshift' + '.png')
##    pylab.close()
##
##
##    pylab.plot(Y_list,Qi_list)
##    pylab.title(date_path + "internal Q")
##    pylab.xlabel("power")
##    pylab.ylabel("internal Q")
##    pylab.savefig(total_path+ 'Qi' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,Qc_list)
##    pylab.title(date_path + "coupling Q")
##    pylab.xlabel("power")
##    pylab.ylabel("coupling Q")
##    pylab.savefig(total_path+ 'Qc' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,unity_list)
##    pylab.title(date_path + "unity transmission")
##    pylab.xlabel("power")
##    pylab.ylabel("unity transmission [dBm]")
##    pylab.savefig(total_path+ 'uni' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,Ql_list)
##    pylab.title(date_path + "loaded Q")
##    pylab.xlabel("power")
##    pylab.ylabel("loaded Q")
##    pylab.savefig(total_path+ 'Ql' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,kc_list*1e-6)
##    pylab.title(date_path + "kappa coupling")
##    pylab.xlabel("power")
##    pylab.ylabel("kappa coupling")
##    pylab.savefig(total_path+ 'kc' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,ki_list*1e-6)
##    pylab.title(date_path + "kappa internal")
##    pylab.xlabel("power")
##    pylab.ylabel("kappa internal")
##    pylab.savefig(total_path+ 'ki' + '.png')
##    pylab.close()
##
##    pylab.plot(Y_list,kl_list*1e-6)
##    pylab.title(date_path + "kappa total")
##    pylab.xlabel("power")
##    pylab.ylabel("kappa total")
##    pylab.savefig(total_path+ 'kl' + '.png')
##    pylab.close()


data.close_file()

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()


#end of experiment routine

