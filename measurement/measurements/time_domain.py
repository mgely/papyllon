'''Template for a measurement class.
The name of this module should be the type of measurement (written in small letters
by convention), the specific measurements should be classes of this module (names written in 
capital letters by convention).

Mario Gely - mario.f.gely@gmail.com
'''

import measurement
import qtlabAPI
import numpy as np
# Add any import needed in this module

class TimeDomainDrivenRabi(measurement.Measurement):
    """docstring for the time domain Rabi measurement to calibrate the qubit drive power and rotation speed.
    """

    # Define a list of arguments needed in this measurement
    # measurement_type and measurement name are obligatory arguments
    # measurement_type must equal to filename, second equal to class
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
                'pulse_length',\
                'measurement_time',\
                'var_att_attenuation']

    # Define a list of optional arguments needed in this measurement
    # Leave empty opt_arg_list = [] if no optional arguments are needed.
    opt_arg_list = [["I_coil",0.15e-3]]

    # Define a list of used instruments
    # Leave empty inst_list = [] if no instruments are needed.
    inst_list = [['pna',            'PNA_N5221A_sal',           'TCPIP::192.168.1.42::INSTR'],\
                ['curr_source',     'keysight_source_B2961A',   'TCPIP::192.168.1.56::INSTR'],\
                ['var_att',         'agilent_var_attenuator',   'TCPIP::192.168.1.113::INSTR']]
    
    # def __init__(self):
    #     # Any other initialization should be performed in initialize()
    #     # i.e you shouldn't have to touch this method
    #     super(TimeDomainDrivenRabi, self).__init__()

        

    ##################
    # Initialization #
    ##################

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        a  = QTlabVariable(a,int)


        # For example:

        # # Import modules in qtlab
        # self.qtlabAPI.import_module('numpy as np')

        # # Initialize extra variables
        # self.my_extra_var = self.opt_arg_1_value *2

        pass

    def initialize_instruments(self):
        # Create all the instruments:
        super(TimeDomainDrivenRabi, self).initialize_instruments()

        # # Define additional procedures
        # example_instrument.switch_on()

        pass

    def initialize_data_acquisition(self, directory):
        super(TimeDomainDrivenRabi, self).initialize_data_acquisition(directory)

        # Define the name of the spyview_process, for example if we set
        # self.spyview.name = '3D', then from now on we will be using the 
        # method spyview_process_3D defined in spyview/metagen.py

        # Reset spyview? With self.spyview.do('reset=True')

        # Add values/coordinates to the data
        # self.data.do('add_coordinate',  'coordinate name')
        # self.data.do('add_value',       'coordinate value')

        pass

    ##################
    #   Measurement  #
    ##################

    def measure(self):
        # Define the measurement procedure

        # Note:
        #  - Add self.process_command() at points where you would like to receive
        # instructions from the operator (for example interrupting the measurement)

        #  - Add "if self.MEASURE == True" statements for all parts of the script
        #  that should be skipped in case of a measurement interruption

        pass

    ##################
    #    Terminate   #
    ##################

    def terminate_instruments(self):
        # Add termination procedure for instruments, for example
        # ramping down DC sources

        super(TimeDomainDrivenRabi, self).terminate_instruments()

    def terminate_data_acquisition(self):
        # Prepend any additional procedures here

        super(TimeDomainDrivenRabi, self).terminate_data_acquisition()
