def keithley_drivers():
    if 'vm' not in instlist:
        vm = qt.instruments.create('vm','Keithley_2700',address='GPIB::17')

    if 'vm2' not in instlist:
        vm2 = qt.instruments.create('vm','Keithley_2700',address='GPIB::16')

def keithley_test1():
    vm.write('*RST')
    vm.set_nplc(1) #sets measuremnt time to n powerline cycle by keithley  1 = 20ms
    vm.set_display(0)                               #turn display off
    vm.write('SENSe:FUNCtion "VOLTage:DC"')
    vm.write(':FORM:ELEM READ') #just getting the values nothing else.. :)
    #vm.write('INITiate:CONTinuous OFF;:ABORt')      #vm.set_trigger_continuous(False)
    vm.write('INITiate:CONTinuous ON')      #vm.set_trigger_continuous(False)
    vm.write('SYSTem:AZERo:STATe OFF')               #Turn autozero off for speed (will result in voltage offsets over time!!)
    vm.write('SENSe:VOLTage:DC:AVERage:STATe OFF')  #Turn off filter for speed
    vm.write('SENSe:VOLTage:DC:RANGe 1')          #give it a fixed range to max speed
    vm.write('TRIG:DEL:AUTO OFF')                   #set triger delay to manual
    vm.write('TRIG:DEL 0')                          #TRIGger:DELay to 0 sec
    vm.write('TRIGger:COUNt 1')
    vm.get_all()
    #vm.write('INIT') #send 1 triger

    NSteps = 100
    start= time()
    for xvar in linspace(1,1000,NSteps):
        
        a=time()
        #i=eval(vm.query('READ?'))/current_gain # this give a clear good data point!
        i=eval(vm.query('FETCH?'))/current_gain #
        qt.msleep(0.01)
        b= time()
        print b-a, i,xvar
    print 'time req: ',time()-start,'time per point: ',(time-start)/NSteps

def keithley_test2():
    #TEST double keithley speed!!! !!! !!!! :)

    #setup buffers..
    counter = 0 #to be used later... cant remember where......
    pptrigger = 1 #how many points to aquire per triger..
    buffersize = NSteps/2 #required buffer for each keithley
    t_read= 0.010 #waiting time per point

    #Keithley 1
    vm.write('TRAC:CLE') #clear old buffer
    vm.write('TRAC:POIN '+str(buffersize)) #set buffer size
    vm.write('TRAC:FEED SENS') #fill buffer with data points
    vm.write('TRAC:FEED:CONTROL NEXT') #activate buffer now fill buffer once then turn off again..
    vm.write('SAMP:COUN '+str(pptrigger)) #take only 1 data point per triger
    #Keithley 2
    vm2.write('TRAC:CLE') #clear old buffer
    vm2.write('TRAC:POIN '+str(buffersize)) #set buffer size
    vm2.write('TRAC:FEED SENS') #fill buffer with data points
    vm2.write('TRAC:FEED:CONTROL NEXT') #activate buffer now fill buffer once then turn off again..
    vm2.write('SAMP:COUN '+str(pptrigger)) #take only 1 data point per triger

    for xvar in linspace(1,1000,NSteps):
        a=time()
        
        if counter%2 == 0:
            vm.write('INIT')

        else:
            vm2.write('INIT')
        counter +=1
        qt.msleep(t_read)
        b= time()
        print b-a, i,xvar
    print 'time req: ',time()-start,'time per point: ',(time-start)/NSteps

    #Readout Keithley 1 buffer
    #will give an error if buffer is not filled..
    buffstatus1 = int(vm.query('TRAC:NEXT?'))
    i_array = vm.query('TRAC:DATA:SEL? 0, '+str(buffstatus))
    i_array = np.array(eval(i_array))/current_gain
    #Readout Keithley 2 buffer
    buffstatus2 = int(vm2.query('TRAC:NEXT?'))
    i2_array = vm2.query('TRAC:DATA:SEL? 0, '+str(buffstatus2))
    i2_array = np.array(eval(i2_array))/current_gain
    print buffstatus,buffstatus2,buffersize

    print 'time req: ',time()-start,'time per point: ',(time-start)/NSteps

    print len(i_array), len(i2_array)

    #just some parsing of the two arrays is remaining to obtain the req. data...
    ii_array=ones(NSteps) #create a simple array of ones
    counter = 0
    for i in linspace(1,1000,NSteps):
        if counter%2 == 0:
            ii_array[counter]= i_array[round(counter/2)]
        else:
            ii_array[counter]= i_array[round(counter/2+1)]
        counter +=1

    print ii_array
