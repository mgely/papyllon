from .. import measurement
from .. import qtlabAPI
import numpy as np
import imp

class SingleTone(measurement.Measurement):
    """docstring for SingleTone"""

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name",\
                'X_name',\
                'X_start',\
                'X_stop',\
                'X_points',\
                'X_instrument',\
                'X_instrument_var',\
                'Y_name',\
                'Y_start',\
                'Y_stop',\
                'Y_points',\
                'Y_instrument',\
                'var_att',\
                'power_pna',\
                'ifbw',\
                'averages']

    # Define a list of optional arguments needed in this measurement
    opt_arg_list = []

    # Define a list of used instruments
    inst_list = [['pna',            'PNA_N5221A',               'TCPIP::192.168.1.42::INSTR'],\
                ['curr_source',     'keysight_source_B2961A',   'TCPIP::192.168.1.56::INSTR'],\
                ['var_att',         'agilent_var_attenuator',   'TCPIP::192.168.1.113::INSTR']]


    def __init__(self):
        super(SingleTone, self).__init__()



    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        # Used by the sweeping instrument => defined in QTlab
        self.X_list = self.qt.variable('X_list', 'np.linspace',self.X_start,self.X_stop,self.X_points)

        # Used to control the measurement => defined here
        print self.Y_start,self.Y_stop,self.Y_points
        self.Y_list=np.linspace(self.Y_start,self.Y_stop,self.Y_points) 

    def abort(self):
        super(SingleTone, self).initialize_data_acquisition(filename, directory)




    def initialize_instruments(self):
        # Create all instruments
        super(SingleTone, self).initialize_instruments()

        # Additional procedures
        # PNA
        self.pna.do(        "reset")    
        self.pna.do(        "setup",                    "start_frequency = "+str(self.X_start), \
                                                        "stop_frequency = " +str(self.X_stop), \
                                                        "measurement_format = 'MLOG'")
        self.pna.do(        "set_power",                self.power_pna)
        self.pna.do(        "set_resolution_bandwidth", self.ifbw)
        self.pna.do(        "set_sweeppoints",          self.X_points)
        self.pna.do(        "set_averages_on")
        self.pna.do(        "set_averages",             self.averages)

        # Current source
        self.curr_source.do("set_output_type",          'CURR')
        self.curr_source.do("set_voltage_protection",   0.1)
        self.curr_source.do("set_protection_state",     True)
        self.curr_source.do("set_state",                True)

    def terminate_instruments(self):
        self.curr_source.do('set_bias_current',0.0)
        self.curr_source.do('set_state',False)

        super(SingleTone, self).terminate_instruments()

    def initialize_data_acquisition(self, filename, directory):
        super(SingleTone, self).initialize_data_acquisition(filename, directory)

        self.spyview.name = '3D'
        self.spyview.do('reset=True')

        self.data.do('add_coordinate',  self.X_name)
        self.data.do('add_coordinate',  self.Y_name)
        self.data.do('add_coordinate',  'no Z coordinate')

        self.data.do('add_value',       'Transmission (dBm)')
        self.data.do('add_value',       'f_data [dBm]')
        self.data.do('add_value',       'Phase')

    def terminate_data_acquisition(self):
        super(SingleTone, self).terminate_data_acquisition()




    def measure(self, filename, directory):
        self.initialize_instruments()
        self.initialize_data_acquisition(filename, directory)

        self.acquire_frame(Z = 1.)

        self.terminate_data_acquisition()
        self.terminate_instruments()

    def acquire_frame(self,Z):

        new_outermostblockval_flag=True
        for Y in self.Y_list:
            self.curr_source.do('set_bias_current',Y) 

            if self.MEASURE == True:
                self.acquire_trace(Y,Z)
            
            self.spyview.do(self.data,
                            self.X_start, self.X_stop,
                            self.Y_stop,  self.Y_start,
                            Z, 'newoutermostblockval='+str(new_outermostblockval_flag))
            new_outermostblockval_flag=False
            self.qt.do('qt','msleep',0.01) #wait 10 usec so save etc

    def acquire_trace(self,Y,Z):

        # Setup averaging
        ave_list = np.linspace(1,self.averages,self.averages)
        self.pna.do('reset_averaging')

        # Sweep 
        for i in ave_list:

            # Listen for commands from the operator
            self.process_command()
            if self.MEASURE ==True:
                self.pna.do('sweep')
                self.pna.do('auto_scale')

        self.trace = self.qt.variable('trace', 'pna.fetch_data', 'polar=True')
        self.tr2 = self.qt.variable('tr2', 'pna.data_f')

        # Too complicated, has to be a send statement
        self.qt.send('data.add_data_point(X_list, list('+str(Y)+'*ones(len(X_list))),list('+str(Z)+'*ones(len(X_list))),trace[0], tr2, np.unwrap(trace[1]))')
        self.data.do('new_block')