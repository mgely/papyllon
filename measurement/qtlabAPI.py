'''Home built API for qtlab based on the ipython "shell channel" to communicate
with the qtlab kernel.

Mario Gely - mario.f.gely@gmail.com
'''

from jupyter_client import KernelClient
import logging
import time

class QTLabError(Exception):
    '''Error raised when a command raises an error in the qtlab kernel
    '''
    pass

class QTLabKernelAPI(object):
    """Allows the user to send instructions to be executed in the qtlab kernel"""
    def __init__(self, connection_file, username = 'TUD202834'):

        self.username = username
        self.session = int(self.time_stamp()) 
        self.msg_id = 0

        client = KernelClient(connection_file = connection_file)
        blocking_client = client.blocking_client()
        blocking_client.connection_file='C:\papyllon\papyllon\qtlab\kernel.json'
        blocking_client.load_connection_file()
        self.channel = blocking_client.shell_channel
        
        # The logging is done in measurement_log.txt
        logger = logging.getLogger()


    def build_message(self, code):
        '''Formats the code to be sent to comply with the jupyter protocol
        '''

        # Information from http://jupyter-client.readthedocs.org/en/latest/messaging.html
        # May change with different versions of ipython
        # ==> need to get it working via the official API to garantee compatibility with later versions

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
                    'stop_on_error' : True,
                    }
        }
        self.msg_id += 1
        return msg

    def send(self,code):
        '''Sends a string to be executed in the qtlab kernel, will raise QTLabError
        if the code raises a qtlab error
        '''

        logging.info(code)

        # build message
        msg = self.build_message(code)

        # send message
        self.channel.send(msg)

        # await for reply
        msgs = []
        while msgs == []:
            msgs = self.channel.get_msgs()

        time.sleep(0.1)
        for msg in msgs:
            if msg['header']['msg_type'] == 'execute_reply':

                # check for error
                if msg['content']['status'] == 'error':
                    raise QTLabError(msg['content']['ename']+': '+msg['content']['evalue']) 

    def do(self, method, *args):
        ''' Will execute the code "method(*args)" in the qtlab terminal

        Check the docstring for parse_args(*args) for details on how to 
        enter arguments.
        '''

        code = method+'(' + parse_args(*args)+')'

        try:
            self.send(code)
        except QTLabError, e:
            raise e

    def time_stamp(self):
        '''Utility function that will return a string timestamp.

        This method is used a unique ID for the communication with the kernel as no
        two IDs should be identical in the communication protocol.
        '''
        t = time.gmtime()
        return str(t.tm_year)+\
                str(t.tm_mon)+\
                str(t.tm_mday)+\
                str(t.tm_hour)+\
                str(t.tm_min)+\
                str(t.tm_sec)

    def import_module(self, module):
        '''Will import the specified module in qtlab
        '''
        self.send('import '+module)    


class QTLabVariable(object):
    '''Creates a qtlab variable.

    Inputs:
     - qtlabAPI for communication

     - name (str) of the variable in qtlab (should be the same as the local name)
       For example 'a'

     - defining_function (str)
       For example 'int'

     - *args (Check the docstring for parse_args(*args) for details on how to enter arguments.)
       For example '3'

    Will execute "name = defining_function(*args)" in qtlab
    For example: a = int('3')

    '''
    def __init__(self,qtlabAPI,name,defining_function, *args):

        self.name = name
        self.qtlabAPI = qtlabAPI
        code = self.name+' = '+defining_function+'(' + parse_args(*args)+')'

        try:
            self.qtlabAPI.send(code)
        except QTLabError, e:
            raise e

    def __str__(self):
        return self.name

    def do(self,method,*args):
        '''Will execute a method of the variable: name.method(*args)
        '''
        self.qtlabAPI.do(self.name+'.'+method, *args)

    

class Data(QTLabVariable):
    """Analog of the data variable in qtlab. Inherits from QTLabVariable
    with not much added apart from the close method. 

    Inputs:
     - qtlabAPI for communication
     - name of the data file (usually set to 'data')
     - directory in which to save data
    """

    def __init__(self, qtlabAPI, filename, directory):
        super(Data, self).__init__(qtlabAPI,'data', 'qt.Data',"name='"+filename+"'")

        self.do('create_file', "datadirs=r'"+directory+"'")
        # TODO copy information about the setup in this directory

    def close(self):
        self.do('close_file')

class Instrument(QTLabVariable):
    """Analog of an instrument in qtlab. Inherits from QTLabVariable
    with not much added apart from the remove method.

    Inputs:
     - qtlabAPI for communication
     - name of the qtlab variable (str) (should be the same as the local name)
     - directory in which to save data (str)
     - (optional) (str) adress needed to communicate with the physical instrument
    """

    def __init__(self, qtlabAPI, local_name, driver_name, address = ''):
        if address == '':
            super(Instrument, self).__init__(qtlabAPI,local_name,'qt.instruments.create', local_name,driver_name)
        else:
            super(Instrument, self).__init__(qtlabAPI,local_name,'qt.instruments.create', local_name,driver_name,"address = '"+address+"'")

    def remove(self):
        self.do('remove')

class SpyviewProcess(object):
    """Analog of an instrument in qtlab. Inherits from QTLabVariable
    with not much added apart from the remove method.

    Inputs:
     - qtlabAPI for communication
     - spyview_folder (str) adress of the directory where the metagen.py file
       is stored

    The name should be set in initialize_data() in measurement classes and 
    corresponds to the name at the end of the "spyview_process_name" method.
    For example, if we specify name = '3D', we will be calling 
    the method 'spyview_process_3D'
    """
    def __init__(self,qtlabAPI,spyview_folder):
        self.qtlabAPI = qtlabAPI
        self.qtlabAPI.send("execfile('"+spyview_folder+"\\metagen.py')")
        self.name = ""

    def do(self,*args):
        '''Calls the "spyview_process_name" method with the given arguments.
        (Check the docstring for parse_args(*args) for details on how to enter arguments)
        '''
        self.qtlabAPI.send('spyview_process_'+self.name+'('+parse_args(*args)+')')


#####################
#     Utility       #
#####################

def parse_args(*args):
    '''Parses arguments when sending instructions to the qtlab kernel.

    - int, strings, floats should be entered un-altered
    - QTLabVariable as well (the method __str__ takes care of yielding the right expression)
    - larger data structures such as arrays should not be entered but a qtlab variable should
        be used instead (otherwise all the variables in the array have to be sent via the comunication
        channel with the kernel and this could lead to bugs)
    - IMPORTANT: keyword arguments have to be entered as strings.
        arg1 = 3 should be entered as "arg1 = 3"
        arg2 = my_float should be enetered as "arg2 = "+str(my_float)
        arg3 = 'hello' should be entered as "arg3 = 'hello'"
        arg4 = my_string should be entered as "arg4 = '"+my_string+"'"
    '''

    parsed_args = ""
    for arg in args:

        if isinstance(arg, str):
            if '=' in arg:
                parsed_args = parsed_args + arg + ","
            else:
                parsed_args = parsed_args + "'"+arg+"',"
        else:
            parsed_args = parsed_args + str(arg) + ","
    parsed_args = parsed_args[:-1] #remove last comma
    return parsed_args