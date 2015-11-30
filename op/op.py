import time
import zmq
import gui
from os import getcwd

class Op(object):
    """docstring for Operator"""
    def __init__(self):
        self.measurement_communication_port="5556"
        self.setup_communication()
        self.papyllon_folder_address = self.get_papyllon_folder_address()

    def initialize_measurement(self):
        self.run_measurement_method('initialize_measurement()')

    def switch_measurement_off(self):
        self.run_measurement_method('set_state("OFF")')

    def ping_measurement(self):
        self.run_measurement_method('ping()')

    def setup_communication(self):
        context = zmq.Context()
        self.socket = context.socket(zmq.PUB)
        self.socket.bind("tcp://*:%s" % self.measurement_communication_port)

        '''
        Assuming that you launch subscriber first and then publisher, 
        subscriber eternally tries to connect to publisher. 
        When publisher appears, the connection procedure on the subscriber's 
        side takes some time and your publisher doesn't really care about this. 
        While it fires with messages as soon as it can, subscriber is trying 
        to establish connection. When connection is established and subscriber 
        is ready to receive, publisher is already finished its work.

        Solution: give subscriber some time by adding sleep to publisher code
        '''

        time.sleep(1)

    def run_measurement_method(self,function):
        self.socket.send (function)

    def run_in_qtlab(self,code):
        self.run_measurement_method(code)

    def load_settings(self,measurement_type, measurement_name):
        self.run_measurement_method("write_blank_settings('"+measurement_type+"', '"+measurement_name+"')")

    def test(self):
        self.run_measurement_method("test_measurement()")

    def start(self):
        gui.SetupGUI(setup_file_adress = self.get_setup_file_address(), 
            method = self.run_measurement_method)

    def stop(self):
        self.run_measurement_method("stop()")

    def time(self):
        self.run_measurement_method("print_measurement_time()")



    def get_papyllon_folder_address(self):
        module_address = getcwd()

        # extracts the papyllon folder adress
        papyllon_folder_address = module_address.replace('\\op','')

        return papyllon_folder_address

    def get_setup_file_address(self):
        return self.papyllon_folder_address+'\\measurement\\setup.json'
        




# o = Operator()
# # o.ping_measurement()
# o.initialize_measurement()
# time.sleep(0.5)
# # o.switch_measurement_off()
# # o.test()
# o.start()
