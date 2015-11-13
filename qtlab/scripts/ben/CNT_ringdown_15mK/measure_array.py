def measure(v0_list=[],v0_name='none',v2_name='none',v2_mul=1,delta =0):
    '''
    The idea is to get all values in Array or list form,
    so it can be used for PNAs, as well as a Keithleys..
    v0_list is the list to be sweeped
    v0_name defines what this is i.e. Vg, Vb, RF, RFp, PNA_RF,PNA_POW,...
    v2_name selects the measurement unit: keithley1, Adwin, PNA, ...
    v2_mul is used to scale i.e. dac multipliers... (measured data will be deviced by v2_mul)
        example: measure(x_list,xvar,mvar_1,mmul_1)...
    '''
    if v2_name == 'none':
        return 1
    elif v2_name == 'keithley1':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = float(eval(keithley1.a('READ?')))
            meas_1 = read_0/v2_mul
            i_array[i] = meas_1
            i = i+1
        return i_array
    elif v2_name == 'Adwin':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = adwin.get_ADC(31314)[0] #(averages)[dac]
            meas_1 = read_0/v2_mul
            i_array[i] = meas_1
            i = i+1
        return i_array
    elif v2_name == 'FSV':
        fsv.set_start_frequency(v0_list[0])
        fsv.set_stop_frequency(v0_list[-1])
        fsv.set_sweeppoints(len(v0_list))
        fsv.write('INIT;*WAI')
        trace= fsv.get_trace()
        return trace
    
    elif v2_name == 'HFLockin':
        ''' Only record with Lockin'''
        timec = HFlockin.get_timeconstant0() #used for sleep before measuring

        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        i_array2 = zeros(len(v0_list)) #[0,0..]
        i_array3 = zeros(len(v0_list)) #[0,0..]
        i_array4 = zeros(len(v0_list)) #[0,0..]

        i = 0
        v0 = 0 #the variable to be sweeped
        for v0 in v0_list:
            sweep(v0_name,v0,delta) #set SMB frequencies with difference freq delta.
            i_array0[i] = HFlockin.get_x()
            i_array1[i] = HFlockin.get_y()
            i_array2[i] = HFlockin.get_amplitude()
            i_array3[i] = HFlockin.get_phase()
            i = i+1

        return i_array0,i_array1,i_array2,i_array3

    elif v2_name == 'HFL_Keith':
        '''record with HF-Lockin and Keithley'''
        timec = HFlockin.get_timeconstant0()
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        i_array2 = zeros(len(v0_list)) #[0,0..]
        i_array3 = zeros(len(v0_list)) #[0,0..]
        i_array4 = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0,delta) #set SMB frequencies with difference freq delta.

            i_array4[i] = float(eval(keithley1.a('READ?')))/v2_mul #record DC
            qt.msleep(timec)

            i_array3[i] = HFlockin.get_phase()
            i_array0[i] = HFlockin.get_x()
            i_array1[i] = HFlockin.get_y()
            i_array2[i] = HFlockin.get_amplitude()

            i = i+1

        return i_array0,i_array1,i_array2,i_array3,i_array4

    elif v2_name == 'PNA':
        pna.sweep()
        return pna.fetch_data(polar=True)

    elif v2_name == 'PNA_single':
        i = 0
        v0 = 0 #the variable to be sweeped
        i_array0 = zeros(len(v0_list)) #[0,0..]
        i_array1 = zeros(len(v0_list)) #[0,0..]
        for v0 in v0_list:
            sweep(v0_name,v0)
            read_0 = array(measure([0],'none','PNA',1))
            meas = read_0/v2_mul
            i_array0[i] = meas[0]
            i_array1[i] = meas[1]
            i = i+1
        return i_array0,i_array1

    elif v2_name == 'FieldFox':
        f_start=v0_list[0]*1e6 #in Hz
        f_stop=v0_list[-1]*1e6 #in Hz
        ff.write('FREQ:START '+str(f_start))
        qt.msleep(0.005)
        ff.write('FREQ:STOP '+str(f_stop))
        qt.msleep(0.005)
        ff.write('SWE:POIN '+str(len(v0_list)))
        qt.msleep(0.005)
        ff.write('INIT;*OPC') #initiate sweep
        #wait till sweep is finished
        a = 0
        x = 0
        y = 0
        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(ff.ask('*OPC?'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0
        trace = eval(ff.ask('CALCulate:DATA:SDATA?'))
        x = array(trace[::2])/v2_mul
        y = array(trace[1::2])/v2_mul
        r = sqrt(abs(x**2+y**2))

        i = 0
        nn = 0
        x2 = x
        for i in x2:
            if i == 0:
                x2[nn]=x2[nn-1] #find and change zeros from x2_array
            nn+=1
        t = arctan(y/x2) #in radians
        
        return x,y,r,t

