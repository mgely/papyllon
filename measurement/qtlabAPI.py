from jupyter_client import KernelClient
import logging
import time

class QTLabError(Exception):
    pass

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

        logger = logging.getLogger()

    #################
    #      Core     #
    #################    

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
                    'stop_on_error' : True,
                    }
        }
        self.msg_id += 1
        return msg

    def send(self,code):

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

    def do(self, variable, method, *args):
        code = variable+'.'+method+'(' + parse_args(*args)+')'

        try:
            self.send(code)
        except QTLabError, e:
            raise e

    def time_stamp(self):
        t = time.gmtime()
        return str(t.tm_year)+\
                str(t.tm_mon)+\
                str(t.tm_mday)+\
                str(t.tm_hour)+\
                str(t.tm_min)+\
                str(t.tm_sec)



    #################
    #   Specific    #
    ################# 

    def import_module(self, module):
        self.send('import '+module)    

    def variable(self,name,defining_function, *args):
        return QTLabVariable(self, name, defining_function, *args)

class QTLabVariable(object):
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
        self.qtlabAPI.do(self.name, method, *args)

    

class Data(QTLabVariable):
    """docstring for Data"""
    def __init__(self, qtlabAPI, filename, directory):
        super(Data, self).__init__(qtlabAPI,'data', 'qt.Data',"name='"+filename+"'")

        self.do('create_file', "datadirs=r'"+directory+"'")
        # TODO copy information about the setup in this directory

    def close(self):
        self.do('close_file')

class Instrument(QTLabVariable):
    """docstring for Instrument"""
    def __init__(self, qtlabAPI, local_name, driver_name, address = ''):
        if address == '':
            super(Instrument, self).__init__(qtlabAPI,local_name,'qt.instruments.create', local_name,driver_name)
        else:
            super(Instrument, self).__init__(qtlabAPI,local_name,'qt.instruments.create', local_name,driver_name,"address = '"+address+"'")

    def remove(self):
        self.do('remove')

class SpyviewProcess(object):
    def __init__(self,qtlabAPI,spyview_folder):
        self.qtlabAPI = qtlabAPI
        self.qtlabAPI.send("execfile('"+spyview_folder+"\\metagen.py')")
        self.name = ""

    def do(self,*args):
        self.qtlabAPI.send('spyview_process_'+self.name+'('+parse_args(*args)+')')


#####################
#     Utility       #
#####################

def parse_args(*args):

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