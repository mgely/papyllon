import time
import zmq

class Operator(object):
    """docstring for Operator"""
    def __init__(self):
        self.measurement_communication_port="5556"
        self.setup_communication()

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
        self.run_measurement_method("start_measurement()")



o = Operator()
# o.ping_measurement()
o.initialize_measurement()
time.sleep(0.5)
# o.switch_measurement_off()
# o.test()
o.start()