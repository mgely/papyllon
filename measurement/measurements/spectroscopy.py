import measurement
import qtlabAPI
import numpy as np


class SingleTone(measurement.Measurement):
    """docstring for SingleTone"""

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name",\
                'f_start',\
                'f_stop',\
                'f_points',\
                'I_start',\
                'I_stop',\
                'I_points',\
                'power_start',\
                'power_stop',\
                'power_points',\
                'var_att_attenuation',\
                'ifbw_first_power_frame',\
                "adaptive_ifbw",\
                'averages']

    # Define a list of optional arguments needed in this measurement
    opt_arg_list = []

    # Define a list of used instruments
    inst_list = [['pna',            'PNA_N5221A',               'TCPIP::192.168.1.42::INSTR'],\
                ['curr_source',     'keysight_source_B2961A',   'TCPIP::192.168.1.56::INSTR'],\
                ['var_att',         'agilent_var_attenuator',   'TCPIP::192.168.1.113::INSTR']]


    bandwidth = [1,2,3,5,7,10,15,20,30,50,70,100,
                        150,200,300,500,700,1000,1.5e3,2e3,3e3,5e3,
                        7e3,10e3,15e3,20e3,30e3,50e3,70e3,100e3,
                        150e3,200e3,280e3,360e3,600e3,1e6,1.5e6,
                        2e6,3e6,5e6,7e6,10e6,15e6]

    def __init__(self):
        super(SingleTone, self).__init__()

    ##################
    # Initialization #
    ##################

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        if self.ifbw_first_power_frame not in self.bandwidth:
            raise Error('ifbw_first_power_frame is not in the available bandwidth of the PNA.\
            Please choose from the following list: \n'+str(self.bandwidth))

        # Used by the sweeping instrument => defined in QTlab
        self.f_list = qtlabAPI.QTLabVariable(self.qt,'f_list', 'np.linspace',self.f_start,self.f_stop,self.f_points)

        # Used to control the measurement => defined here
        self.I_list=np.linspace(self.I_start,self.I_stop,self.I_points) 
        self.power_list=np.linspace(self.power_start,self.power_stop,self.power_points) 

        # Used to indicate frame progress
        self.frame_progress = 0

    def initialize_instruments(self):
        # Create all instruments
        super(SingleTone, self).initialize_instruments()

        # Additional procedures
        # PNA
        self.pna.do(        "reset")    
        self.pna.do(        "setup",                    "start_frequency = "+str(self.f_start), \
                                                        "stop_frequency = " +str(self.f_stop), \
                                                        "measurement_format = 'MLOG'")
        self.pna.do(        "set_resolution_bandwidth", self.ifbw_first_power_frame)
        self.pna.do(        "set_sweeppoints",          self.f_points)
        self.pna.do(        "set_averages_on")
        self.pna.do(        "set_averages",             self.averages)

        # Current source
        self.curr_source.do("set_output_type",          'CURR')
        self.curr_source.do("set_voltage_protection",   0.1)
        self.curr_source.do("set_protection_state",     True)
        self.curr_source.do("set_state",                True)

        # Var_attenuation
        self.var_att.do("set_var_att",  self.var_att_attenuation)

    def initialize_data_acquisition(self, directory):
        super(SingleTone, self).initialize_data_acquisition(directory)

        self.spyview.name = '3D'
        self.spyview.do('reset=True')

        self.data.do('add_coordinate',  "Cavity Frequency [Hz]")
        self.data.do('add_coordinate',  "I_coil [A]")
        self.data.do('add_coordinate',  'PNA power [dBm]')

        self.data.do('add_value',       'Transmission (dBm)')
        self.data.do('add_value',       'f_data [dBm]')
        self.data.do('add_value',       'Phase')


    ##################
    #   Measurement  #
    ##################

    def measure(self):
        for Z in self.power_list:
            self.Z = Z # Needed to compute the progress     
            self.pna.do("set_power",Z)
            self.adapt_power(Z)
            self.acquire_frame(Z)

    def acquire_frame(self,Z):

        new_outermostblockval_flag=True
        for Y in self.I_list:
            if self.MEASURE == True:

                self.Y = Y # Needed to compute the progress               
                self.curr_source.do('ramp_source_curr',Y) 

                
                self.acquire_trace(Y,Z)
                
                self.spyview.do(self.data,
                                self.f_start, self.f_stop,
                                self.I_stop,  self.I_start,
                                Z, 'newoutermostblockval='+str(new_outermostblockval_flag))
                new_outermostblockval_flag=False
                self.qt.do('qt.msleep',0.01) #wait 10 usec so save etc

                self.print_progress()

    def acquire_trace(self,Y,Z):

        # Setup averaging
        ave_list = np.linspace(1,self.averages,self.averages)
        self.pna.do('reset_averaging')

        # Sweep 
        for i in ave_list:
            # Listen for commands from the operator
            self.process_command()
            if self.MEASURE == True:
                self.pna.do('sweep')
                self.pna.do('auto_scale')

        self.trace = qtlabAPI.QTLabVariable(self.qt,'trace', 'pna.fetch_data', 'polar=True')
        self.tr2 = qtlabAPI.QTLabVariable(self.qt,'tr2', 'pna.data_f')

        # Too complicated, has to be a send statement
        self.qt.send('data.add_data_point(f_list, list('+str(Y)+'*ones(len(f_list))),list('+str(Z)+'*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))')
        self.data.do('new_block')

    def adapt_power(self,Z):
        if self.adaptive_ifbw == True:
            new_bandwidth = self.compute_bandwidth(Z)
            self.pna.do("set_resolution_bandwidth", new_bandwidth)

    def compute_bandwidth(self,power):
        index = self.bandwidth.index(self.ifbw_first_power_frame) + int((power - self.power_list[0])/3)

        # Add bounds to the bandwidth
        if index < 0:
            index = 0
        elif index >= len(self.bandwidth):
            index = len(self.bandwidth) -1

        return float(self.bandwidth[index])


    ##################
    #    Terminate   #
    ##################

    def terminate_instruments(self):
        self.curr_source.do('ramp_source_curr',0.0)
        self.curr_source.do('set_state',False)

        super(SingleTone, self).terminate_instruments()

    def terminate_data_acquisition(self):
        super(SingleTone, self).terminate_data_acquisition()

    ##################
    #    Timing      #
    ##################

    def compute_progress(self):
        self.frame_progress = (self.Y - self.I_start) / (self.I_stop - self.I_start)

        i = 0
        power = self.power_list[0]
        numerator = 0
        denominator = 0
        while power != self.Z:
            bw = self.compute_bandwidth(power)
            numerator += 1/bw
            denominator += 1/bw
            i += 1
            power  = self.power_list[i]

        power  = self.power_list[i]
        bw = self.compute_bandwidth(power)
        numerator += self.frame_progress * 1/bw
        denominator += 1/bw
        i += 1

        while i<len(self.power_list):
            power  = self.power_list[i]
            bw = self.compute_bandwidth(power)
            denominator += 1/bw
            i += 1

        self.progress = numerator/denominator
        

    def compute_measurement_time(self):
        self.measurement_time = 0
        for Z in self.power_list:
            bw = self.compute_bandwidth(Z)
            self.measurement_time += self.f_points * self.I_points / bw


    def print_progress(self):
        super(SingleTone, self).print_progress()
        print "Power : %f dBm" % (self.Z)
        print "Magnet : %f Amps" % (self.Y)

class TwoTone(measurement.Measurement):
    """docstring for TwoTone"""

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name",\
                'cav_start',\
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
                'qubit_averaging',\
                'I_start',\
                'I_stop',\
                'I_points',\
                'var_att_attenuation']

    # Define a list of optional arguments needed in this measurement
    opt_arg_list = [['f_cw',6.2689e9],\
                    ['pow_cw',-10],\
                    ['w_bare',4.601e9],\
                    ['qubit_power_dep',False],\
                    ['qubit_power_start',0.],\
                    ['qubit_power_stop',0.],\
                    ['qubit_power_points',1]]

    # Define a list of used instruments
    inst_list = [['pna',            'PNA_N5221A_sal',           'TCPIP::192.168.1.42::INSTR'],\
                ['curr_source',     'keysight_source_B2961A',   'TCPIP::192.168.1.56::INSTR'],\
                ['var_att',         'agilent_var_attenuator',   'TCPIP::192.168.1.113::INSTR']]


    def __init__(self):
        super(TwoTone, self).__init__()

    ##################
    # Initialization #
    ##################

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        # Used by the sweeping instrument => defined in QTlab
        self.qubit_list = qtlabAPI.QTLabVariable(self.qt,'qubit_list', 'np.linspace',self.qubit_start,self.qubit_stop,self.qubit_points)

        # Used to control the measurement => defined here
        self.I_list=np.linspace(self.I_start,self.I_stop,self.I_points)
        if self.qubit_power_dep == True:
            self.qubit_power_list=np.linspace(self.qubit_power_start,
                                                self.qubit_power_stop,
                                                self.qubit_power_points)

        # Used to indicate frame progress
        self.frame_progress = 0

    def initialize_instruments(self):
        # Create all instruments
        super(TwoTone, self).initialize_instruments()

        # PNA
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
                        self.qubit_power,
                        self.w_bare,
                        self.f_cw,
                        self.pow_cw)  

        # Current source
        self.curr_source.do("set_output_type",          'CURR')
        self.curr_source.do("set_voltage_protection",   0.1)
        self.curr_source.do("set_protection_state",     True)
        self.curr_source.do("set_state",                True)

        # Var_attenuation
        self.var_att.do("set_var_att",  self.var_att_attenuation)

    def initialize_data_acquisition(self, directory):
        super(TwoTone, self).initialize_data_acquisition(directory)

        self.spyview.name = '3D'
        self.spyview.do('reset=True')

        self.data.do('add_coordinate',  "Frequency [Hz]")
        self.data.do('add_coordinate',  "I_coil [A]")
        if self.qubit_power_dep == True:
            self.data.do('add_coordinate',  'Qubit power [dBm]')
        else:
            self.data.do('add_coordinate',  'no Z coordinate')

        self.data.do('add_value',       'linmag')
        self.data.do('add_value',       'phase')
        self.data.do('add_value',       'f_cav [Hz]')


    ##################
    #   Measurement  #
    ##################

    def measure(self):
        if self.qubit_power_dep == True:
            for Z in self.qubit_power_list:
                self.Z = Z # Needed to compute the progress     
                self.pna.do('w',"SOUR2:POW3 %s" %(Z))
                self.acquire_frame(Z)
        else:      
            self.pna.do('w',"SOUR2:POW3 %s" %(self.qubit_power))
            self.acquire_frame(Z = 0.)

    def acquire_frame(self,Z):

        new_outermostblockval_flag=True
        for Y in self.I_list:
            if self.MEASURE == True:

                self.Y = Y # Needed to compute the progress               
                self.curr_source.do('ramp_source_curr',Y) 

                
                self.acquire_trace(Y,Z)
                
                self.spyview.do(self.data,
                                self.qubit_start, self.qubit_stop,
                                self.I_stop,  self.I_start,
                                Z, 'newoutermostblockval='+str(new_outermostblockval_flag))
                new_outermostblockval_flag=False
                self.qt.do('qt.msleep',0.01) #wait 10 usec so save etc

                self.print_progress()

    def acquire_trace(self,Y,Z):

        # Setup averaging
        self.pna.do('reset_averaging')
        ave_list = np.linspace(1,self.qubit_averaging,self.qubit_averaging)

        # Find cavity frequency
        self.process_command() # Check if the operator wants to stop the measurement
        if self.MEASURE == True:
            self.pna.do('reset_two_tone_cavity')

        # Autoscale first screen
        self.pna.do('w',"DISP:WIND1:TRAC1:Y:SCAL:AUTO")

        # Sweep Qubit
        for i in ave_list:
            self.process_command() # Check if the operator wants to stop the measurement
            if self.MEASURE == True:
                self.pna.do('trigger','channel = %s' % (2))

                # Autoscale second screen
                self.pna.do('w',"DISP:WIND2:TRAC1:Y:SCAL:AUTO")




        self.trace = qtlabAPI.QTLabVariable(self.qt,'trace', 'pna.fetch_data', "channel  = %s" % (2), 'polar=True')

        self.qt.send('data.add_data_point(qubit_list,'+\
            ' list('+str(Y)+'*ones(len(qubit_list))),'+\
            ' list('+str(Z)+'*ones(len(qubit_list))),'+\
            ' trace[0], np.unwrap(trace[1]),'+\
            ' list(0.*ones(len(qubit_list))) )')
        self.data.do('new_block')


    ##################
    #    Terminate   #
    ##################

    def terminate_instruments(self):
        self.curr_source.do('ramp_source_curr',0.0)
        self.curr_source.do('set_state',False)

        super(TwoTone, self).terminate_instruments()

    def terminate_data_acquisition(self):
        super(TwoTone, self).terminate_data_acquisition()

    ##################
    #    Timing      #
    ##################

    def compute_progress(self):
        if self.I_stop != self.I_start:
            self.progress = (self.Y - self.I_start) / (self.I_stop - self.I_start)
        else:
            self.progress = 1.

        if self.qubit_power_dep == True:
            self.progress *= (self.Z - self.qubit_power_start) / (self.qubit_power_stop - self.qubit_power_start)
        

    def compute_measurement_time(self):
        self.measurement_time = (self.qubit_points * self.qubit_averaging / float(self.qubit_ifbw) + self.cav_points * self.cav_averaging / float(self.cav_ifbw)) * self.I_points

        if self.qubit_power_dep == True:
            self.measurement_time *= self.qubit_power_points
        