'''Class for handling communication between the operator and the qtlab kernel

Mario Gely - mario.f.gely@gmail.com
'''

import py_compile
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
import datetime
from shutil import copy
from utility import byteify, add_measurement_to_ppt, ask_user_to_generate_png



class Measurement(object):
    '''Handles communication with the operator and the qtlab kernel.

    Typical usage:

    > (Automatic initialization): load settings and setup communication

    > initialize_measurement: go to a measurement class (ex:SingleTone)

    > test_measurement: you start measuring but you see that a 
    setting should be changed by looking at the data in data/_testing 

    > stop: you stop the measurement and change the settings.json file

    > initialize_measurement: reload settings 

    (iterate as long as you want)

    > start_measurement(name,device,detail): measure and save data in 
      data/name/device/__(time information)__MeasurementName__detail__/
    '''

    # Define a list of arguments needed in this measurement
    arg_list = ["measurement_type",\
                "measurement_name"]

    # Define a list of optional arguments needed in this measurement
    opt_arg_list = []

    # Define a list of used instruments
    inst_list = []


    def __init__(self):
        with open("global.json","r") as f:
            self.global_setup =  byteify(json.load(f))

        self.state = "ON"
        self.papyllon_folder_address = self.get_papyllon_folder_address()
        self.settings_file_address = self.get_settings_file_address()
        self.data_address = self.global_setup["data_directory"]
        self.setup_logging(level=logging.DEBUG)

        self.apply_settings()

        # For communication from operator
        self.socket = None
        self.communication_port="5556"
        # For communication to QTlab
        self.qt = None
        self.setup_communication()

        # For configuring spyview 
        self.spyview = qtlabAPI.SpyviewProcess(self.qt,spyview_folder = self.papyllon_folder_address+'\\measurement\\spyview')

        # Measurement timing
        self.measurement_time = 0 # in seconds
        self.progress = 0 # between 0 and 1

        # Class specific instructions => overwritten in each measurement
        self.initialize()

        self.MEASURE = False

        # Wait for instructins from the operator
        self.idle()

    #########################################
    # To be modified in measurement classes #
    #########################################

    # Append to
    def initialize(self):
        '''Initialization routine that should be overwritten systematically
        for class-specific instructions. This method is run at instanciation in __init__
        or when we run re-initialize a measurement inside a specific class

        Below are the instructions that should be called only
        once, when the Measurement class is first instaciated 
        (ie. when one has started the Measurement kernel).
        '''
        # setting up QTlab with some always used modules
        self.qt.import_module('numpy as np')
        self.qt.import_module('qt')
        self.qt.import_module('time')

    # Append to
    def initialize_instruments(self):
        '''Run at the beginning of every measurement or test. It creates qtlab instruments
        specified in the class variable int_list.

        Should be appended in measurement classes to include instrument-specific
        initializations.
        '''
        for inst in self.inst_list:
            if len(inst) == 2:
                inst.append("")
            setattr(self, inst[0], qtlabAPI.Instrument(self.qt,*inst))

    # Append to
    def initialize_data_acquisition(self, directory):
        '''Run at the beginning of every measurement or test. It informs
        qtlab that this is the moment to start acquiring data in the 
        specified directory.

        Should be appended in measurement classes to include any specific
        initialization procedure
        '''
        self.qt.do('qt.mstart')
        self.data = qtlabAPI.Data(self.qt, 'data', directory)

    # Overwrite
    def measure(self):
        '''Run in every measurement or test between data&instrument initialization
        and termination. This is where you want to sweep over some parameters
        with your instruments and acquire data.

        Should be overwritten in every measurement class.

        Note:
         - Add self.process_command() at points where you would like to receive
        instructions from the operator (for example interrupting the measurement)

         - Add "if self.MEASURE == True" statements for all parts of the script
         that should be skipped in case of a measurement interruption
        '''
        pass

    # Preppend to
    def terminate_instruments(self):
        '''Run at the end of every measurement or test. It removes
        all qtlab instruments

        Should be PREpended in measurement classes (write instructions then
        call super()) to include instrument-specific procedures. 
        Ex: ramping down slowly a current source to avoid discrete
        jumps that could harm the experiment
        '''
        for attr, value in self.__dict__.iteritems():
            if isinstance(value, qtlabAPI.Instrument):
                eval('self.'+attr+'.remove()')

    # Preppend to
    def terminate_data_acquisition(self):
        '''Run at the end of every measurement or test. It informs
        qtlab that this is the moment to stop acquiring data.

        Should be PREpended in measurement classes (write instructions then
        call super()) to include specific procedures. 
        '''
        self.data.close()
        self.qt.do('qt.mend')

    # Overwrite
    def compute_progress(self):
        logging.warning("\nMethod to compute progress not overwritten in \
            measurement class or you havn't initialized the measurement")

    # Overwrite
    def compute_measurement_time(self):
        logging.warning("\nMethod to compute measurement time not overwritten in \
            measurement class")








    ############################################
    # Methods called by user with the operator #
    ############################################

    def ping(self):
        '''Check if the connection between the operator and this class
        has been correctly established by logging 'measurement pinged'
        '''
        logging.info('measurement pinged')

    def initialize_measurement(self):
        '''Loads the settings from settings.json and goes/initializes the measurement
        class specified by measurement_name and measurement_type.
        '''
        if self.get_name() == 'Measurement':
            self.apply_settings()
            
            if self.get_name() == 'Measurement': 

                try:
                    exec("import measurements."+self.measurement_type)
                    exec("reload(measurements."+self.measurement_type+")")
                except ImportError, e:
                    logging.error("The module measurements."+self.measurement_type+" does not exist.")
                    raise e

                exec("measurements."+self.measurement_type+"."+self.measurement_name+"()")
                logging.info("Back to measurement kernel")

            else:
                raise RuntimeError('Measurements can only be initialized from the kernel.')

        else:
            self.apply_settings()
            self.initialize()

    def start_measurement(self,name,device,detail,testing = False):
        '''Method to call after testing the setup to run a full measurement.
        Will go through the following procedure:

        0. Initialize measurement (load settings)
        1. Initialize instruments
        2. Initialize data acquisition
        3. Measures
        4. Terminates data acquisition
        5. Removes all instruments
        '''

        start = time.time()
        logging.info("Measurement started")
        self.print_measurement_time()

        # Create data folder
        now=time.localtime()
        date_path = str(now.tm_year) + '_' +\
                    str(now.tm_mon) + '_' +\
                    str(now.tm_mday) + '_______' +\
                    str(now.tm_hour) + '.' +\
                    str(now.tm_min) + '.' +\
                    str(now.tm_sec)
        if testing == False:
            device_folder = self.data_address + '\\'+\
                        name + '\\'+\
                        device
            folder = self.data_address + '\\'+\
                        name + '\\'+\
                        device + '\\'+\
                        date_path+'_____'+\
                        self.measurement_name+'__'+\
                        detail
        elif testing == True:
            folder = self.data_address + '\\'+\
                        "_testing" + '\\'+\
                        date_path


        # Initialization

        # Prepare sript
        self.qt.SCRIPT = True
        self.qt.script_adress = self.papyllon_folder_address+'\\measurement\\script.py'
        with open(self.qt.script_adress,'w') as s:
            s.write('# measurement script')

            
        self.initialize_measurement()
        self.initialize_instruments()
        self.initialize_data_acquisition(folder)

        # Measurement                
        self.MEASURE = True
        self.measure()

        # Stopping everything
        self.terminate_data_acquisition()
        self.terminate_instruments()
        end = time.time()
        self.qt.SCRIPT = False

        logging.info('Measurement ended.')

        start_str = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))
        end_str = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end)))
        duration = str(datetime.timedelta(seconds=end - start))

        print "Started: "+start_str
        print "Ended: "+end_str
        print "Measurement time: "+duration

        # Save settings
        copy(self.settings_file_address, folder)

        # Save setup in data folder
        copy(self.get_setup_file_address(), folder)

        # Save script in data folder
        copy(self.qt.script_adress, folder)
        os.remove(self.qt.script_adress)

        # Save time information
        time_info = {
        'duration' : duration,
        'start' : start_str,
        'end' : end_str
        }
        with open(folder+'\\timing.json',"w") as f:
            json.dump(time_info, f, sort_keys=True, indent=4, separators=(',', ': '))

        if testing == False:
            self.add_data_to_ppt(device_folder, folder)

    def test_measurement(self):
        '''Method to test the setup before running a full measurement.
        Will go through the following procedure:

        0. Initialize measurement (load settings)
        1. Initialize instruments
        2. Initialize data acquisition
        3. Measures
        4. Terminates data acquisition
        5. Removes all instruments

        Measurement data will be stored in the data/_testing directory

        Should be PREpended (write instructions then call super()) to, for 
        example, divide the number of sweep points for a fast scan
        '''
        self.start_measurement(None,None,None, testing = True)

    def stop(self):
        '''Stops the measurement by skipping all the code in the measure method
        that was put in a "if self.MEASURE == True" statement. 

        Data and instruments are still terminated as in a normal measurement
        '''
        self.MEASURE = False

    def process_command(self):
        '''Runs any command emitted by the operator.
        If the command leads to an error, the measurement is not stopped, but 
        and error message will be printed
        '''

        # Read latest entry
        command = self.get_latest_entry()

        if command != None:

            logging.info("Applying "+command)

            # eval(command) # Use when debugging, favors information about errors over keeping exp running
            try:
                eval(command)

            # Failing to execute a command will not stop the measurement from running
            except Exception, e:
                error_message = 'Error in '+command+'\nFailed with error: ' + str(e) + '\n'
                tb = "\n".join(traceback.format_exc().splitlines())
                logging.error(error_message+'\n'+tb+'\n')

    ###########
    # Utility #
    ###########

    def set_state(self, state):
        '''Should be used to turn a specific measurement OFF, and thus return 
        to the idling of the mother Measurement class. This is uselful when changing
        the type/name of measurement one wants to perform
        '''

        if state == "ON":
            self.state = "ON"
            self.idle()


        elif state == "OFF":
            logging.info("Exiting measurement...")

            if self.get_name() == 'Measurement':
                logging.warning('Tried to initialize measurement from out of kernel (from class:'+self.get_name()+')')
                raise RuntimeError('Measurement kernel cannot be aborted, use ctrl+c if you really want to abort')

            else:
                self.state = "OFF"
                logging.info("Measurement exited")

        else:
            logging.error("Invalid state, available states: \"ON\" and \"OFF\"")

    def apply_settings(self):
        '''Loads and applies the settings specified in the settings.json file
        '''

        with open(self.settings_file_address,"r") as f:
            settings =  byteify(json.load(f)) # dictionary "byteified" to parse unicodes to strings

        # Apply default settings
        for x in self.opt_arg_list:
            setattr(self, x[0], x[1])

        # Apply optional settings
        for x in self.opt_arg_list:
            try:
                value = settings['opt'][x[0]]
                setattr(self, x[0], value)
            except:
                # The optional argument was not specified in settings..
                # its value specified in the opt_arg_list will be taken
                pass 

        # Apply specified settings
        for arg in self.arg_list:
            try:
                value = settings[arg]
            except:
                raise KeyError('No value for argument '+arg+' found in arg_list')

            setattr(self, arg, value)

    def setup_logging(self, level):
        '''Sets up the logging for this class, the QTlabAPI and all other measurement
        classes.
        '''
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

    def get_papyllon_folder_address(self):
        module_address = __file__

        # extracts the address of the communication log from that
        papyllon_folder_address = module_address.replace('\\measurement\\measurement.pyc','')
        papyllon_folder_address = papyllon_folder_address.replace('\\measurement\\measurement.py','')

        return papyllon_folder_address

    def get_data_file_address(self):
        return self.papyllon_folder_address.replace('\\papyllon\\papyllon','\\papyllon\\data')

    def get_settings_file_address(self):
        return self.papyllon_folder_address+'\\measurement\\settings.json'

    def get_setup_file_address(self):
        return self.papyllon_folder_address+'\\measurement\\setup.json'
    
    def get_name(self):
        '''Returns the name of the current class, for exemple 'Measurement'
        or 'SingleTone'
        '''
        return self.__class__.__name__

    def write_blank_settings(self, measurement_type, measurement_name):
        '''Creates a settings.json file where all the settings are set to None
        and all the optional settings are set to their default value
        '''
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
        '''Returns the latest instruction sent by the operator or 'None' if
        there is no instruction.
        '''

        try:
            message = self.socket.recv()
            return message
        except zmq.error.Again:
            return None

    def idle(self):
        '''Whilst the state of the measurement is set to "ON", wait for 
        instructions from the operator, carry out the instruction, then wait 
        for a new instruction.

        Exiting this function can only be done by setting the state of the
        measurement to "OFF" via the set_state method. This is not allowed
        in the Measurement mother class (this one), but allows one to exit
        a specific measurement (ex: SingleTone) and return to this class in 
        order to load a different measurement. That process would look like:
        > set_state("OFF")
        change name and type of measurement in settings.json
        > initialize_measurement
        '''
        if self.get_name() == "Measurement":
            logging.info("Measurement kernel switched on")
        else:
            logging.info(self.get_name() + " measurent switched on")
        

        while self.state == "ON":
            time.sleep(0.1)
            self.process_command()

    def print_measurement_time(self):

        try:
            self.initialize_measurement()
            self.compute_measurement_time()

            print "Expected time of measurement: \t"+\
                str(datetime.timedelta(seconds=self.measurement_time))

            print "Expected end of measurement: \t"+\
                str(datetime.datetime.now()+datetime.timedelta(seconds=self.measurement_time))
        except Exception, e:
            logging.error('Could not print measurement time')
            logging.error(str(e))

    # Append in measurement class to include additional information about progress
    def print_progress(self):

        # Try to not interrupt measurement in case of failure
        try:
            # Calculating progress
            self.compute_progress()

            # Building the progress bar
            prog_bar = ""
            i = 0.05
            while i<self.progress:
                prog_bar += "="
                i += 0.05
            prog_bar += ">"
            while i<1.:
                prog_bar += " "
                i += 0.05

            # Calculating finishing time
            self.compute_measurement_time()
            time_left = (1-self.progress)*self.measurement_time
            end_time = str(datetime.datetime.now()+datetime.timedelta(seconds=time_left))


            print "-----------------------------------------------"
            print "[" + prog_bar + "] (%2.f %%)" % (self.progress * 100)
            print "Finished at "+end_time
            print "-----------------------------------------------"

        except Exception, e:
            logging.error('Could not print progress')
            logging.error(str(e))

    def add_data_to_ppt(self, device_folder, measurement_folder):
        raw_ppt_address = os.path.join(device_folder,'raw.pptx')
        if not os.path.isfile(raw_ppt_address):
            copy(os.path.join(self.papyllon_folder_address,'measurement','raw.pptx'), device_folder)

        ask_user_to_generate_png(measurement_folder)
        add_measurement_to_ppt(raw_ppt_address, measurement_folder)

