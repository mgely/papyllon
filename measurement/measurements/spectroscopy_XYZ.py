import measurement
import qtlabAPI
import numpy as np

class Spectroscopy(measurement.Measurement):

    bandwidth = [1,2,3,5,7,10,15,20,30,50,70,100,
                150,200,300,500,700,1000,1.5e3,2e3,3e3,5e3,
                7e3,10e3,15e3,20e3,30e3,50e3,70e3,100e3,
                150e3,200e3,280e3,360e3,600e3,1e6,1.5e6,
                2e6,3e6,5e6,7e6,10e6,15e6]  

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name",\
                'var_att_attenuation',\
                'Y_instrument',\
                'Y_coord',\
                'Y_start',\
                'Y_stop',\
                'Y_points',\
                'Z_instrument',\
                'Z_coord',\
                'Z_start',\
                'Z_stop',\
                'Z_points']

    opt_arg_list = []

    # Define a list of used instruments, which are automatically instantiated upon measurement start()/test().
    inst_list = [['pna',            'PNA_N5221A_sal',           'TCPIP::192.168.1.42::INSTR'],\
                ['var_att',         'agilent_var_attenuator',   'TCPIP::192.168.1.113::INSTR']]

    YZ_instrument_options = ['None','curr_source']

    ##################
    # Initialization #
    ##################

    def initialize_instruments(self):
        # Create all instruments
        super(Spectroscopy, self).initialize_instruments()

        self.initialize_sweep_instrument()

        # Var_attenuation
        self.var_att.do("set_var_att",  self.var_att_attenuation)

        # Initialize the Y and Z instruments
        self.initialize_YZ_instruments(self.Y_instrument,'Y')
        self.initialize_YZ_instruments(self.Z_instrument,'Z')

    def initialize_YZ_instruments(self, instrument_name, Y_or_Z):
        if instrument_name not in self.YZ_instrument_options:
            raise Exception(Y_or_Z + '_instrument not a valid option, please choose from the following list:'+\
                str(self.YZ_instrument_options))


        if instrument_name == 'None':
            # Loop function
            def dummy_function(arg):
                pass
            setattr(self, Y_or_Z+'_func',dummy_function) 

        if instrument_name == 'curr_source':
            # Initialization
            self.curr_source = qtlabAPI.Instrument(
                qtlabAPI = self.qt, 
                local_name = 'curr_source', 
                driver_name = 'keysight_source_B2961A', 
                address = 'TCPIP::192.168.1.56::INSTR'
                )
            self.curr_source.do("set_output_type",          'CURR')
            self.curr_source.do("set_voltage_protection",   0.1)
            self.curr_source.do("set_protection_state",     True)
            self.curr_source.do("set_state",                True)

            # Loop function
            def curr_source_function(I):
                self.process_command() # Check if the operator wants to stop the measurement
                if self.MEASURE == True:
                    self.curr_source.do('ramp_source_curr',I)
            setattr(self, Y_or_Z+'_func',curr_source_function) 

    def initialize_data_acquisition(self, directory):
        super(Spectroscopy, self).initialize_data_acquisition(directory)

        self.spyview.name = '3D'
        self.spyview.do(reset=True)


        #depending on Y/Z settings dynamically create the right axes.
        self.data.do('add_coordinate',  "Frequency [Hz]")
        self.data.do('add_coordinate',  self.Y_coord)
        self.data.do('add_coordinate',  self.Z_coord)

    ##################
    #   Measurement  #
    ##################

    def measure(self):
        for Z in self.Z_list:
            self.set_Z(Z)
            for Y in self.Y_list:
                self.set_Y(Y)

                self.sweep()
                self.acquire_data()
                self.print_progress()

    def set_Z(self,Z):
        '''function that sets the frame coordinate '''
        self.Z = Z
        self.new_outermostblockval_flag=True
        self.Z_func(Z)

    def set_Y(self,Y):
        '''function that sets the trace coordinate '''
        self.Y = Y
        self.Y_func(Y)

    ##################
    #    Terminate   #
    ##################

    def terminate_instruments(self): 
        self.pna.do("set_power",-10)
        self.var_att.do("set_var_att",  70)

        self.terminate_YZ_instruments(self.Y_instrument,'Y')
        self.terminate_YZ_instruments(self.Z_instrument,'Z')

        super(Spectroscopy, self).terminate_instruments()


    def terminate_YZ_instruments(self, intrument_name, Y_or_Z):
        pass

    def terminate_data_acquisition(self):
        super(Spectroscopy, self).terminate_data_acquisition()







class SingleTone(Spectroscopy):
    """docstring for SingleTone"""

    # Define a list of arguments needed in this measurement
    arg_list = Spectroscopy.arg_list +\
                ['f_start',\
                'f_stop',\
                'f_points',\
                'ifbw_first_frame',\
                'adaptive_ifbw',\
                'averages',
                'pna_power']

    YZ_instrument_options = Spectroscopy.YZ_instrument_options +\
                            ['pna_power']

    ##################
    # Initialization #
    ##################

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        if self.ifbw_first_frame not in self.bandwidth:
            raise Exception('ifbw_first_frame is not in the available bandwidth of the PNA.\
            Please choose from the following list: \n'+str(self.bandwidth))

        # Used by the sweeping instrument => defined in QTLabVariable
        self.f_list = qtlabAPI.QTLabVariable(self.qt,'f_list', 'np.linspace', self.f_start, self.f_stop, self.f_points)

        # Used to control the measurement => defined here
        self.Y_list = np.linspace(self.Y_start,self.Y_stop,self.Y_points) 
        self.Z_list = np.linspace(self.Z_start,self.Z_stop,self.Z_points) 

        self.pow_dep_axis = None

    def initialize_sweep_instrument(self):
        '''Will be called in the initialize_instruement method of the Spectroscopy class.
        '''
        # Initialize the spectroscopy
        self.pna.do(        "reset")    
        self.pna.do(        "setup",                    start_frequency = self.f_start, \
                                                        stop_frequency = self.f_stop, \
                                                        measurement_format = 'MLOG')
        self.pna.do(        "set_resolution_bandwidth", self.ifbw_first_frame)
        self.pna.do(        "set_sweeppoints",          self.f_points)
        self.pna.do(        "set_averages_on")
        self.pna.do(        "set_averages",             self.averages)
        self.pna.do(        "set_power",                self.pna_power)


    def initialize_YZ_instruments(self, instrument_name, Y_or_Z):
        super(SingleTone, self).initialize_YZ_instruments(instrument_name, Y_or_Z)

        if instrument_name == 'pna_power':
            # Initialization
            self.pow_dep_axis = Y_or_Z

            # Loop function
            def pna_power_function(P):
                self.adapt_ifbw(P)
                self.pna.do("set_power",P)
            setattr(self, Y_or_Z+'_func',pna_power_function) 

    def initialize_data_acquisition(self, directory):
        super(SingleTone, self).initialize_data_acquisition(directory)

        self.data.do('add_value',       'Transmission')
        self.data.do('add_value',       'f_data [dBm]')
        self.data.do('add_value',       'Phase')

    ##################
    #   Measurement  #
    ##################

    def sweep(self):

        # Setup averaging
        self.pna.do('reset_averaging')

        for i in xrange(self.averages):

            # Listen for commands from the operator
            self.process_command()

            if self.MEASURE == True:
                self.pna.do('sweep')
                self.pna.do('auto_scale')

    def acquire_data(self):
        self.trace = qtlabAPI.QTLabVariable(self.qt,'trace', 'pna.fetch_data', 'polar=True')
        self.tr2 = qtlabAPI.QTLabVariable(self.qt,'tr2', 'pna.data_f')
        
        self.qt.send('data.add_data_point(f_list,'+\
                    ' list('+str(self.Y)+'*ones(len(f_list))),'+\
                    ' list('+str(self.Z)+'*ones(len(f_list))),'+\
                    ' trace[0],'+\
                    ' tr2,'+\
                    ' np.unwrap(trace[1]))') 

        self.data.do('new_block')
        self.spyview.do(self.data,
                self.f_start, self.f_stop,
                self.Y_stop,  self.Y_start,
                self.Z, newoutermostblockval = self.new_outermostblockval_flag)
        self.new_outermostblockval_flag=False
        self.qt.do('qt.msleep',0.01) #wait 10 usec so save etc

    def adapt_ifbw(self,P):
        if self.adaptive_ifbw == True:
            new_bandwidth = self.compute_bandwidth(P)
            self.pna.do("set_resolution_bandwidth", new_bandwidth)

    def compute_bandwidth(self,power):
        if self.pow_dep_axis == 'Y':
                first_power = self.Y_start
        elif Y_or_Z =='Z':
            first_power = self.Z_start

        index = self.bandwidth.index(self.ifbw_first_frame) + int((power - first_power[0])/3)

        # Add bounds to the bandwidth
        if index < 0:
            index = 0
        elif index >= len(self.bandwidth):
            index = len(self.bandwidth) -1

        return float(self.bandwidth[index])

    ##################
    #    Terminate   #
    ##################

    def terminate_YZ_instruments(self, intrument_name, Y_or_Z):
        super(SingleTone, self).terminate_YZ_instruments(intrument_name, Y_or_Z)

    def terminate_data_acquisition(self):
        super(SingleTone, self).terminate_data_acquisition()

    ##################
    #    Timing      #
    ##################

    def compute_progress(self):

        if self.pow_dep_axis == None:
            self.progress = 1.
            if self.Z_stop != self.Z_start:
                self.progress *= (self.Z - self.Z_start) / (self.Z_stop - self.Z_start) 
            if self.Y_stop != self.Y_start:
                self.progress *= (self.Y - self.Y_start) / (self.Y_stop - self.Y_start)


        else:
            if self.pow_dep_axis == 'Y':
                power_list = self.Y_list
                current_power = self.Y
                frame_progress = (self.Z - self.Z_start) / (self.Z_stop - self.Z_start)
            elif self.pow_dep_axis =='Z':
                power_list = self.Z_list
                current_power = self.Z
                frame_progress = (self.Y - self.Y_start) / (self.Y_stop - self.Y_start)
            

            
            i = 0
            power = power_list[0]
            numerator = 0
            denominator = 0
            while power != current_power:
                bw = self.compute_bandwidth(power)
                numerator += 1/bw
                denominator += 1/bw
                i += 1
                power  = power_list[i]

            power  = power_list[i]
            bw = self.compute_bandwidth(power)
            numerator += frame_progress * 1/bw
            denominator += 1/bw
            i += 1

            while i<len(power_list):
                power  = power_list[i]
                bw = compute_bandwidth(power)
                denominator += 1/bw
                i += 1

            self.progress = numerator/denominator
        
    def compute_measurement_time(self):

        if self.pow_dep_axis == None:
            self.measurement_time = self.averages * self.f_points * self.Y_points * self.Z_points / self.ifbw_first_frame
        else:
            if self.pow_dep_axis == 'Y':
                power_list = self.Y_list
                frames = self.Z_points
            elif self.pow_dep_axis =='Z':
                power_list = self.Z_list
                frames = self.Y_points

            self.measurement_time = 0
            for power in power_list:
                bw = self.compute_bandwidth(Z)
                self.measurement_time += self.averages * self.f_points * frames / bw

    def print_progress(self):
        super(SingleTone, self).print_progress()




class TwoTone(Spectroscopy):
    """docstring for TwoTone"""

    # Define a list of arguments needed in this measurement
    arg_list = Spectroscopy.arg_list +\
                ['cav_start',\
                'cav_stop',\
                'cav_points',\
                'cav_ifbw',\
                'cav_power',\
                'cav_averaging',\
                'qubit_start',\
                'qubit_stop',\
                'qubit_points',\
                'qubit_ifbw',\
                'qubit_power',\
                'qubit_averaging']

    YZ_instrument_options = Spectroscopy.YZ_instrument_options +\
                            ['qubit_power','cav_power']

    ##################
    # Initialization #
    ##################

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        if self.qubit_ifbw not in self.bandwidth:
            raise Exception('qubit_ifbw is not in the available bandwidth of the PNA.\
            Please choose from the following list: \n'+str(self.bandwidth))

        if self.cav_ifbw not in self.bandwidth:
            raise Exception('cav_ifbw is not in the available bandwidth of the PNA.\
            Please choose from the following list: \n'+str(self.bandwidth))

        # Used by the sweeping instrument => defined in QTlab
        self.qubit_list = qtlabAPI.QTLabVariable(self.qt,'qubit_list', 'np.linspace',self.qubit_start,self.qubit_stop,self.qubit_points)

        # Used to control the measurement => defined here
        self.Y_list = np.linspace(self.Y_start,self.Y_stop,self.Y_points) 
        self.Z_list = np.linspace(self.Z_start,self.Z_stop,self.Z_points) 

    def initialize_sweep_instrument(self):

        self.pna.do("reset")    
        self.pna.do("setup_two_tone",
                        self.cav_start,
                        self.cav_stop,
                        self.cav_points,
                        self.cav_averaging,
                        self.cav_ifbw,
                        self.cav_power,
                        self.qubit_start,
                        self.qubit_stop,
                        self.qubit_points,
                        self.qubit_averaging,
                        self.qubit_ifbw,
                        self.qubit_power)  
        # self.pna.do("reset_two_tone_cavity")

    def initialize_YZ_instruments(self, instrument_name, Y_or_Z):
        super(TwoTone, self).initialize_YZ_instruments(instrument_name, Y_or_Z)

        if instrument_name == 'qubit_power':

            # Loop function
            def qubit_power_function(P):
                self.pna.do('w',"SOUR2:POW3 %s" %(P))
            setattr(self, Y_or_Z+'_func',qubit_power_function) 

        if instrument_name == 'cav_power':

            def cav_power_function(P):
                self.pna.do('w',"SOUR2:POW1 %s" %(P))
            setattr(self, Y_or_Z+'_func',cav_power_function) 

    def initialize_data_acquisition(self, directory):
        super(TwoTone, self).initialize_data_acquisition(directory)

        self.data.do('add_value',       'linmag')
        self.data.do('add_value',       'phase')
        self.data.do('add_value',       'f_cav [Hz]')


    ##################
    #   Measurement  #
    ##################

    def sweep(self):

        self.pna.do('reset_averaging')

        # Find cavity frequency
        self.process_command() # Check if the operator wants to stop the measurement
        if self.MEASURE == True:
            self.pna.do('reset_two_tone_cavity')

        # Autoscale first screen
        self.pna.do('w',"DISP:WIND1:TRAC1:Y:SCAL:AUTO")

        # Sweep Qubit
        for i in xrange(self.qubit_averaging):
            self.process_command() # Check if the operator wants to stop the measurement
            if self.MEASURE == True:
                self.pna.do('trigger',channel = 2)

                # Autoscale second screen
                self.pna.do('w',"CALC2:FORM PHASE")
                self.pna.do('w',"DISP:WIND2:TRAC1:Y:SCAL:AUTO")

    def acquire_data(self):
        
        self.trace = qtlabAPI.QTLabVariable(
            qtlabAPI = self.qt,
            name = 'trace', 
            defining_function = 'pna.fetch_data', 
            channel=2, 
            polar=True)

        # sending a raw python command to qtlab, it is a string, the '+\' are there to concatenate the string over
        # multiple inputlines.
        self.qt.send('data.add_data_point(qubit_list,'+\
            ' list('+str(self.Y)+'*ones(len(qubit_list))),'+\
            ' list('+str(self.Z)+'*ones(len(qubit_list))),'+\
            ' trace[0], np.unwrap(trace[1]),'+\
            ' list(0.*ones(len(qubit_list))) )')
        self.data.do('new_block')
        self.spyview.do(self.data,
                        self.qubit_start, self.qubit_stop,
                        self.Y_stop,  self.Y_start,
                        self.Z, newoutermostblockval=self.new_outermostblockval_flag)
        self.new_outermostblockval_flag=False
        self.qt.do('qt.msleep',0.01) #wait 10 usec so save etc

    ##################
    #    Terminate   #
    ##################

    def terminate_YZ_instruments(self, intrument_name, Y_or_Z):
        super(TwoTone, self).terminate_YZ_instruments(intrument_name, Y_or_Z)

    def terminate_data_acquisition(self):
        super(TwoTone, self).terminate_data_acquisition()

    ##################
    #    Timing      #
    ##################

    def compute_progress(self):
        self.progress = 1.
        if self.Z_stop != self.Z_start:
            self.progress *= (self.Z - self.Z_start) / (self.Z_stop - self.Z_start) 
        if self.Y_stop != self.Y_start:
            self.progress *= (self.Y - self.Y_start) / (self.Y_stop - self.Y_start)

    def compute_measurement_time(self):
        trace_time = self.qubit_points * self.qubit_averaging / float(self.qubit_ifbw) + self.cav_points * self.cav_averaging / float(self.cav_ifbw)
        self.measurement_time = self.Y_points * self.Z_points * trace_time
