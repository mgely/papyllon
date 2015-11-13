import time 
import json
import pdb
import logging
import zmq
import qt 
import numpy as np

class Measurement(object):
    """docstring for Measurement"""
    def __init__(self, arg_list = ["measurement_type","measurement_name"], opt_arg_list = []):
        self.state = "ON"
        self.qtlab_folder_adress = self.get_qtlab_folder_adress()
        self.settings_file_adress = self.get_settings_file_adress()

        self.arg_list = arg_list
        self.opt_arg_list = opt_arg_list
        self.settings = self.get_settings()
        self.apply_settings()

        self.socket = None
        self.setup_logging(level=logging.DEBUG)

        self.communication_port="5556"
        self.setup_communication()

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

    def abort(self):
        # Sould be rewritten in all measurement subclasses, 
        # adding safety measures such as ramping current/voltage sources down to zero

        logging.info('aborting measurement, class name: '+self.get_name())
        if self.get_name() == 'Measurement':
            logging.warning('Tried to initialize measurement from out of kernel (from class:'+self.get_name()+')')
            raise RuntimeError('Measurement kernel cannot be aborted, use ctrl+c if you really want to abort')
            return False


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
                logging.info(error_message)

    def initialize_measurement(self):
        if self.get_name() == 'Measurement': 

            # try:
            #     exec("import measurements."+self.measurement_type)
            # except ImportError, e:
            #     logging.error("The module measurements."+self.measurement_type+" does not exist.")
            #     raise e

            # exec("measurements."+self.measurement_type+"."+self.measurement_name+"()")

            import measurements.spectroscopy
            measurements.spectroscopy.SingleTone()

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
        f = open(self.settings_file_adress,"r")
        settings = json.loads(f.read())
        f.close()
        return settings

    def apply_settings(self):

        # Apply default settings
        for x in self.opt_arg_list:
            setattr(self, x[0], x[1])

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

            formatter = logging.Formatter('%(filename)s - in %(funcName)s - line %(lineno)d\n\
                %(asctime)s - %(levelname)s - %(message)s')

            log_adress = self.qtlab_folder_adress+'\\measurement'
            fh = logging.FileHandler(log_adress+'\\measurement_log.txt')
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

    def get_qtlab_folder_adress(self):
        module_adress = __file__

        # extracts the adress of the communication log from that
        qtlab_folder_adress = module_adress.replace('\\measurement\\measurement.pyc','')
        qtlab_folder_adress = qtlab_folder_adress.replace('\\measurement\\measurement.py','')

        return qtlab_folder_adress

    def get_settings_file_adress(self):
        return self.qtlab_folder_adress+'\\measurement\\settings.json'
    
    def get_name(self):
        return self.__class__.__name__


    #################
    # Communication #
    #################

    def setup_communication(self, forced = False):
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect("tcp://localhost:%s" % self.communication_port)
        self.socket.setsockopt(zmq.SUBSCRIBE,'') # TO DO
        self.socket.RCVTIMEO = 1000
        logging.info("Communication socket connected")

    def get_latest_entry(self):

        try:
            message = self.socket.recv()
            return message
        except zmq.error.Again:
            return None