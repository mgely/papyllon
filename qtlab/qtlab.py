import IPython 
from  multiprocessing import Process
import os
import time

def start_kernel():
    IPython.start_kernel(file_to_run='source/qtlab_shell.py', connection_file='kernel.json')

def setup_communication_file():
    pass

def start_ipython():
    IPython.start_ipython(argv=['console','--existing',os.path.dirname(os.path.realpath(__file__))+'\kernel.json'])

if __name__ == "__main__":
    Process(target=start_kernel).start()
    time.sleep(2)

    start_ipython()