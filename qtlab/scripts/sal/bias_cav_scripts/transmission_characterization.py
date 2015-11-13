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



f_points =1001
bandwidth=10
power = -30
averages=1

h_1=5.388e9


f_estimate=h_1
span=80.e6

start_f=f_estimate-span/2.
stop_f=f_estimate+span/2.

f_list=np.linspace(start_f,stop_f,f_points)

iteration=1
iteration_list=np.linspace(1,1,iteration)


################################
#      INSTRUMENTS
################################

instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)

if 'pna' not in instlist:
    pna = qt.instruments.create('pna','PNA_N5221A', address='TCPIP::192.168.1.42::INSTR')
if 'var_att' not in instlist:
    var_att=qt.instruments.create('var_att','agilent_var_att', address='TCPIP::192.168.1.113::INSTR')

#Check and load instrument plugins
instlist = qt.instruments.get_instrument_names()
print "Available instruments: "+" ".join(instlist)


pna.reset()
pna.setup(start_frequency=start_f,stop_frequency=stop_f,measurement_format = 'MLOG')
pna.set_power(power)
pna.set_averages(True)
pna.set_resolution_bandwidth(bandwidth)
pna.set_sweeppoints(f_points)


################################
#      DATA INITIALIZATION
################################

#normalization routine
qt.mstart()
#spyview_process(reset=True) #clear old meta-settings

device_name = 'bias_cav_sapph4'
port_type = 'S12'

base_path = 'D:\\data\\Sal\\' + device_name + '\\' + port_type + '\\'

now=localtime()

date_path = str(now.tm_year) + '_' + str(now.tm_mon) + '_' + str(now.tm_mday) + '_______' + str(now.tm_hour) + '.' + str(now.tm_min) + '.' + str(now.tm_sec)

#data struct to optimize scanspeed

#Set up data
filename = 'transmission_characterization'
data = qt.Data(name=filename)
#data.add_coordinate('Frequency (MHz)',size=sweep_points)
#data.add_coordinate('Absolute time [s]')
data.add_coordinate('Frequency (Hz)')
data.add_coordinate('iteration1')
data.add_coordinate('iteration2')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')

data.create_file(datadirs=base_path+date_path+'_____'+filename)
data.copy_file('transmission_characterization.py')

total_path=base_path+date_path+'_____'+filename

spyview_process(reset=True)

########################################
###         MEASUREMENT LOOP
########################################

print 'Start Experiment'

Z_list=[1]

pna.set_power(0)

Y_list = np.linspace(90,70,11)
p_list=[]
for i in Z_list:
    
    new_outermostblockval_flag=True
    #adwin.set_DAC_1(gate)
   
    for Y in Y_list:
        #print magv
        now_time = time()
        time_int = now_time-prev_time
        prev_time = now_time

        var_att.set_var_att(int(Y))
        Y=var_att.get_var_att()
        print Y
        
        ave_list = np.linspace(1,averages,averages)
        #Set Voltage
        #adwin.set_DAC_2(magv)
        #print 'wait to settle'
        #
        qt.msleep(.2)
        #qt.msleep(.2*sweeptime)
        
        #print 'sweep'
        pna.reset_averaging()
        for k in ave_list:
            pna.sweep()
            pna.auto_scale()

        trace=pna.fetch_data(polar=True)
       
        tr2=pna.data_f()
        
        #tr2_parsed = pna.parse_trace(tr2)
        data.add_data_point(f_list, list(Y*ones(len(f_list))),list(i*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))

        data.new_block()
        spyview_process(data,start_f,stop_f,iteration, 1,Y,newoutermostblockval=new_outermostblockval_flag)
        new_outermostblockval_flag=False
        qt.msleep(0.01) #wait 10 usec so save etc
        pna.auto_scale()

        #transmission cavity formula in Schuster's thesis p.51/52
        #format p: p[0]=w0, p[1]=k_out, k_in has to be supplied by hand...
        a=array(tr2)


        f_index = np.where(a==a.max())[0][0]
        print f_index

        f_estimate=f_list[f_index]
        print 'fest ', f_estimate

        T0 =a[f_index]

        max_dB = a.max()

        print 'peak max: ', max_dB, T0

        #transmission cavity formula in Schuster's thesis p.51/52, modified to Rami's type
        #format p: p[0]=w0, p[1]=T0, p[2]=Ql, k_in has to be supplied by hand...

        
        fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(p[1]/(1+2j*p[2]*(x-p[0])/(p[0]))))
        #fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(np.sqrt((k_in*p[1])/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
        #fitfunc_S21 = lambda p,x: 20*np.log10(np.abs(2*np.sqrt(k_in*p[1])/(k_in+p[1])/(1-2j*(x-p[0])/(k_in+p[1]))))#(k_in*p[1]/(k_in+p[1])))/(1-2j*(x-p[0])/(k_in+p[1]))))
        
        errfunc = lambda p,x,y: fitfunc_S21(p,x)-y
        p0=[f_estimate,T0,400]
        p1, success = optimize.leastsq(errfunc,p0[:],args=(array(f_list),array(tr2)))

        print Y
        for z in p1:
            print z

        p_list.append([Y,p1])

        plotsave=True
        if(plotsave):
            pylab.plot(f_list,tr2,"ro", f_list,fitfunc_S21(p1,array(f_list)),"r-")


            # Legend the plot
            pylab.title("Transmission response")
            pylab.xlabel("frequency [Hz]")
            pylab.ylabel("S21 transmission [dB]")
            pylab.legend(('data', 'fit'))
     
            ax = pylab.axes()
     
            pylab.text(0.8, 0.5,'f_res :  %.4f GHz \n T0 :  %.1f \n Ql %.4f' % (p1[0]*1e-9,20*np.log10(p1[1]),p1[2]),
                        fontsize=10,
                        horizontalalignment='left',
                        verticalalignment='top',
                        transform=ax.transAxes)

            pylab.savefig(total_path + str(Y) + '.png')
            pylab.close()

    df_list=[]
    Ql_list=[]
    T0_list=[]

    for i in p_list:
        df_list.append(i[1][0])
        T0_list.append(i[1][1])
        Ql_list.append(i[1][2])

    df_list = array(df_list)
    Ql_list = array(Ql_list)
    T0_list = array(T0_list)

    pylab.plot(Y_list,df_list*1e-9)
    pylab.title(date_path + "frequency")
    pylab.xlabel("power")
    pylab.ylabel("frequency [GHz]")
    pylab.savefig(total_path+ 'freq' + '.png')
    pylab.close()

    
    pylab.plot(Y_list,(df_list-df_list[0])*1e-3)
    pylab.title(date_path + "frequency shift")
    pylab.xlabel("power")
    pylab.ylabel("frequency [kHz]")
    pylab.savefig(total_path+ 'freqshift' + '.png')
    pylab.close()


    pylab.plot(Y_list,Ql_list)
    pylab.title(date_path + "loaded Q")
    pylab.xlabel("power")
    pylab.ylabel("loaded Q")
    pylab.savefig(total_path+ 'Ql' + '.png')
    pylab.close()

    pylab.plot(Y_list,T0_list)
    pylab.title(date_path + "T0 (max power)")
    pylab.xlabel("power")
    pylab.ylabel("max transmission")
    pylab.savefig(total_path+ 'T0' + '.png')
    pylab.close()

        
            #pylab.show()            

data.close_file()

#adwin.set_DAC_1(0)
#adwin.set_DAC_2(0)

qt.mend()


#end of experiment routine

