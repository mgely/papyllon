from .. import measurement

class MeasurementName(measurement.Measurement):
    """docstring for Measurement
    """

    # Define a list of arguments needed in this measurement
    # measurement_type and measurement name are obligatory arguments
    arg_list = ["measurement_type",\
                "measurement_name"]

    # Define a list of optional arguments needed in this measurement
    # opt_arg_list = [["opt_arg_1",opt_arg_1_value],\
    #               ["opt_arg_2",opt_arg_2_value]]

    # Define a list of used instruments
    # inst_list = [["local_name","driver_name", (optional) "adress"]]
    def __init__(self):


        # Any other initialization should be performed in initialize()

        super(SingleTone, self).__init__()

    def initialize(self):
        """Overwrites some of the initialization procedures
        present in the Measurement mother class. 
        Will be called in __init__ automatically.
        """

        # For example:

        # # Import modules in qtlab
        # self.qtlabAPI.import_module('numpy as np')

        # # Initialize extra variables
        # self.my_extra_var = self.opt_arg_1_value *2

    def initialize_instruments(self):

        # Create all the instruments
        super(SingleTone, self).initialize_instruments()

        # # Define additional procedures
        # example_instrument.switch_on()

        pass

    def acquire_trace(self,Y,Z):

        # Listen for commands from the operator 
        self.process_command() # to be place so that the measurement is as responsive as possible