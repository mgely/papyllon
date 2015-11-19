import time 
import json
import pdb
import logging
import zmq
import numpy as np
import qtlabAPI
import sys
import traceback
import os

class Measurement(object):

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name"]

    # Define a list of optional arguments needed in this measurement
    opt_arg_list = []

    # Define a list of used instruments
    inst_list = []

    """docstring for Measurement"""
    def __init__(self):
        self.state = "ON"
        self.papyllon_folder_address = self.get_papyllon_folder_address()
        self.settings_file_address = self.get_settings_file_address()
        self.data_address = self.get_date_file_address()
        self.setup_logging(level=logging.DEBUG)

        self.settings = self.get_settings()
        self.apply_settings()

        # For communication from operator
        self.socket = None
        self.communication_port="5556"
        # For communication to QTlab
        self.qt = None
        self.setup_communication()

        # For configuring spyview 
        self.spyview = qtlabAPI.SpyviewProcess(self.qt,spyview_folder = self.papyllon_folder_address+'\\measurement\\spyview')

        # Class specific instructions
        self.initialize()

        self.MEASURE = False
        self.idle()


    #################
    # Core methods  #
    #################

    def idle(self):
        # i = 0
        if self.get_name() == "Measurement":
            logging.info("Measurement kernel switched on")
        else:
            logging.info(self.get_name() + " measurent switched on")
        

        while self.state == "ON": #and i<10:
            time.sleep(0.1)
            self.process_command()
            # i+=1

    def ping(self):
        logging.info('measurement pinged')



    def initialize(self):
        '''Initialization routine that should be overwritten systematically
        for class-specific instructions.

        For example, below are the instructions that should be called only
        once, when the Measurement class is first instaciated.
        '''
        # setting up QTlab
        self.qt.import_module('numpy as np')
        self.qt.import_module('qt')
        self.qt.import_module('time')

    def abort(self):

        logging.info('aborting measurement '+self.get_name())
        if self.get_name() == 'Measurement':
            logging.warning('Tried to initialize measurement from out of kernel (from class:'+self.get_name()+')')
            raise RuntimeError('Measurement kernel cannot be aborted, use ctrl+c if you really want to abort')
            return False



    def initialize_instruments(self):
        for inst in self.inst_list:
            if len(inst) == 2:
                inst.append("")
            setattr(self, inst[0], qtlabAPI.Instrument(self.qt,*inst))

    def terminate_instruments(self):
        for attr, value in self.__dict__.iteritems():
            if isinstance(value, Instrument):
                attr.remove()



    def initialize_data_acquisition(self, filename, directory):
        self.qt.do('qt','mstart')
        self.data = qtlabAPI.Data(self.qt, filename, directory)

    def terminate_data_acquisition(self):
        self.data.close()
        self.qt.do('qt','mend')



    def measure(self, filename, directory):
        pass


    def start_measurement(self):
        self.MEASURE = True

    def test_measurement(self):
        folder = self.data_address + "\\_testing"
        
        for fileName in os.listdir(folder):
            try:
                os.remove(os.path.join(folder,fileName))
            except WindowsError, e:
                logging.warning("Previous test data: '"+fileName+"' could not be removed because it is open in another process")

        self.MEASURE = True
        self.measure('data', folder)

    def stop(self):
        self.MEASURE = False

    #################
    #    Control    #
    #################


    def process_command(self):
        # Read latest entry
        command = self.get_latest_entry()

        if command != None:

            method_to_apply = 'self.'+command
            logging.info("Applying "+method_to_apply)

            # eval(method_to_apply) # Use when debugging, favors information about errors over keeping exp running
            try:
                eval(method_to_apply)

            # Failing to execute a command will not stop the measurement from running
            except Exception, e:
                error_message = 'Error in '+method_to_apply+'\nFailed with error: ' + str(e) + '\n'
                tb = "\n".join(traceback.format_exc().splitlines())
                logging.error(error_message+'\n'+tb+'\n')

    def initialize_measurement(self):
        if self.get_name() == 'Measurement': 

            try:
                exec("import measurements."+self.measurement_type)
            except ImportError, e:
                logging.error("The module measurements."+self.measurement_type+" does not exist.")
                raise e

            exec("measurements."+self.measurement_type+"."+self.measurement_name+"()")


            logging.info("Back to measurement kernel")

        else:
            raise RuntimeError('Measurements can only be initialized from the kernel.')

    def set_state(self, state):


        if state == "ON":
            self.state = "ON"
            self.idle()


        elif state == "OFF":
            logging.info("Aborting measurement...")
            
            try:
                self.abort()
                logging.info("Measurement aborted")
                self.state = "OFF"
                logging.info("Measurent switched off")
            except RuntimeError, e:
                logging.error('Abort failed with error: '+str(e))
                raise e

        else:
            logging.error("Invalid state, available states: \"ON\" and \"OFF\"")

    def get_settings(self):
        with open(self.settings_file_address,"r") as f:
            return byteify(json.load(f)) # dictionary "byteified" to parse unicodes to strings

    def apply_settings(self):

        # Apply default settings
        for x in self.opt_arg_list:
            setattr(self, x[0], x[1])

        # Apply optional settings
        for x in self.opt_arg_list:
            try:
                value = self.settings['opt'][x[0]]
                setattr(self, x[0], value)
            except:
                # The optional argument was not specified in settings..
                # its value specified in the opt_arg_list will be taken
                pass 

        # Apply specified settings
        for arg in self.arg_list:
            try:
                value = self.settings[arg]
            except:
                raise KeyError('No value for argument '+arg+' found in arg_list')

            setattr(self, arg, value)

    def setup_logging(self, level):
        logger = logging.getLogger()
        if not logger.handlers:
            logger.setLevel(level)

            # formatter = logging.Formatter('%(filename)s - in %(funcName)s - line %(lineno)d\n\
            #     %(asctime)s - %(levelname)s - %(message)s')
            formatter = logging.Formatter('%(filename)s - in %(funcName)s - line %(lineno)d - %(message)s')

            log_address = self.papyllon_folder_address+'\\measurement'
            fh = logging.FileHandler(log_address+'\\measurement_log.txt')
            fh.setLevel(level)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            ch = logging.StreamHandler()
            ch.setLevel(level)
            ch.setFormatter(formatter)
            logger.addHandler(ch)

            logging.info('Logging initialized')

    #################
    #    Utility    #
    #################

    def get_papyllon_folder_address(self):
        module_address = __file__

        # extracts the address of the communication log from that
        papyllon_folder_address = module_address.replace('\\measurement\\measurement.pyc','')
        papyllon_folder_address = papyllon_folder_address.replace('\\measurement\\measurement.py','')

        return papyllon_folder_address

    def get_date_file_address(self):
        return self.papyllon_folder_address.replace('\\papyllon\\papyllon','\\papyllon\\data')


    def get_settings_file_address(self):
        return self.papyllon_folder_address+'\\measurement\\settings.json'
    
    def get_name(self):
        return self.__class__.__name__

    def write_blank_settings(self, measurement_type, measurement_name):
        try:
            exec("from measurements."+measurement_type+' import '+measurement_name)
        except ImportError, e:
            logging.error("The class named measurements."+self.measurement_type+'.'+measurement_name+" does not exist.")
            raise e

        exec('arg_list = '+measurement_name+'.arg_list')
        exec('opt_arg_list = '+measurement_name+'.opt_arg_list')

        blank_settings = {}
        for arg in arg_list:
            blank_settings[arg] = None

        opt={}
        for arg in opt_arg_list:
            opt[arg[0]] = arg[1]

        blank_settings['opt'] = opt
        blank_settings['measurement_type'] = measurement_type
        blank_settings['measurement_name'] = measurement_name

        with open(self.settings_file_address,"w") as f:
            json.dump(blank_settings, f, sort_keys=True, indent=4, separators=(',', ': '))



    #################
    # Communication #
    #################

    def setup_communication(self):

        # From operator
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:%s" % self.communication_port)
        self.socket.setsockopt(zmq.SUBSCRIBE,'') # Maybe set up filters?
        self.socket.RCVTIMEO = 1000
        logging.info("Communication socket connected")

        # To QTlab
        communication_file = self.papyllon_folder_address+'\\qtlab\\kernel.json'
        self.qt = qtlabAPI.QTLabKernelAPI(communication_file)

    def get_latest_entry(self):

        try:
            message = self.socket.recv()
            return message
        except zmq.error.Again:
            return None


def byteify(input):
    if isinstance(input, dict):
        return {byteify(key):byteify(value) for key,value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input