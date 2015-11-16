import time 
import json
import pdb
import logging
import zmq
import numpy as np
from jupyter_client import KernelClient

class Measurement(object):
    """docstring for Measurement"""
    def __init__(self, arg_list = ["measurement_type","measurement_name"], opt_arg_list = []):
        self.state = "ON"
        self.papyllon_folder_adress = self.get_papyllon_folder_adress()
        self.settings_file_adress = self.get_settings_file_adress()

        self.arg_list = arg_list
        self.opt_arg_list = opt_arg_list
        self.settings = self.get_settings()
        self.apply_settings()

        self.setup_logging(level=logging.DEBUG)

        # For communication from operator
        self.socket = None
        self.communication_port="5556"
        # For communication to QTlab
        self.qtlabAPI = None

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
                logging.error(error_message)

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

            log_adress = self.papyllon_folder_adress+'\\measurement'
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

    def get_papyllon_folder_adress(self):
        module_adress = __file__

        # extracts the adress of the communication log from that
        papyllon_folder_adress = module_adress.replace('\\measurement\\measurement.pyc','')
        papyllon_folder_adress = papyllon_folder_adress.replace('\\measurement\\measurement.py','')

        return papyllon_folder_adress

    def get_settings_file_adress(self):
        return self.papyllon_folder_adress+'\\measurement\\settings.json'
    
    def get_name(self):
        return self.__class__.__name__


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
        communication_file = self.papyllon_folder_adress+'\\qtlab\\kernel.json'
        self.qtlabAPI = QTLabKernelAPI(communication_file)

    def get_latest_entry(self):

        try:
            message = self.socket.recv()
            return message
        except zmq.error.Again:
            return None

    def send_to_qtlab(self, code):
        self.qtlabAPI.send(code)


class QTLabKernelAPI(object):
    """docstring for IpythonKernelAPI"""
    def __init__(self, connection_file, username = 'TUD202834'):
        self.username = username
        self.session = int(self.time_stamp()) 
        self.msg_id = 0

        client = KernelClient(connection_file = connection_file)
        blocking_client = client.blocking_client()
        blocking_client.connection_file='C:\papyllon\papyllon\qtlab\kernel.json'
        blocking_client.load_connection_file()
        self.channel = blocking_client.shell_channel

    def build_message(self, code):

        # Information from http://jupyter-client.readthedocs.org/en/latest/messaging.html
        # May change with different versions of ipython
        # ==> need to get it working via the API to garantee compatibility with later versions

        msg = {
        # The message header contains a pair of unique identifiers for the
        # originating session and the actual message id, in addition to the
        # username for the process that generated the message. This is useful in
        # collaborative settings where multiple users may be interacting with the
        # same kernel simultaneously, so that frontends can label the various
        # messages in a meaningful way.
        'header' : {
                    'msg_id' : self.msg_id,
                    'username' : self.username,
                    'session' : self.session,
                    # ISO 8601 timestamp for when the message is created
                    'date': self.time_stamp(),
                    # All recognized message type strings are listed below.
                    'msg_type' : 'execute_request',
                    # the message protocol version
                    'version' : '5.0',
                    },
        # In a chain of messages, the header from the parent is copied so that
        # clients can track where messages come from.
        'parent_header' : {},
        # Any metadata associated with the message.
        'metadata' : {},
        # The actual content of the message must be a dict, whose structure
        # depends on the message type.

        'content' : {
                    # Source code to be executed by the kernel, one or more lines.
                    'code' : code,
                    # A boolean flag which, if True, signals the kernel to execute
                    # this code as quietly as possible.
                    # silent=True forces store_history to be False,
                    # and will *not*:
                    # - broadcast output on the IOPUB channel
                    # - have an execute_result
                    # The default is False.
                    'silent' : False,
                    # A boolean flag which, if True, signals the kernel to populate history
                    # The default is True if silent is False. If silent is True, store_history
                    # is forced to be False.
                    'store_history' : True,
                    # A dict mapping names to expressions to be evaluated in the
                    # user's dict. The rich display-data representation of each will be evaluated after execution.
                    # See the display_data content for the structure of the representation data.
                    'user_expressions' : {},
                    # Some frontends do not support stdin requests.
                    # If raw_input is called from code executed from such a frontend,
                    # a StdinNotImplementedError will be raised.
                    'allow_stdin' : True,
                    # A boolean flag, which, if True, does not abort the execution queue, if an exception is encountered.
                    # This allows the queued execution of multiple execute_requests, even if they generate exceptions.
                    'stop_on_error' : False,
                    }
        }
        self.msg_id += 1
        return msg

    def send(self,code):
        msg = self.build_message(code)
        self.channel.send(msg)

    def time_stamp(self):
        t = time.gmtime()
        return str(t.tm_year)+\
                str(t.tm_mon)+\
                str(t.tm_mday)+\
                str(t.tm_hour)+\
                str(t.tm_min)+\
                str(t.tm_sec)
