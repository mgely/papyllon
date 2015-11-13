import IPython 
from  multiprocessing import Process
import time

def start_kernel():
    IPython.start_kernel(file_to_run='source/qtlab_shell.py')

def setup_communication_file():
    pass

def start_ipython():
    IPython.start_ipython(argv=['console','--existing'])

if __name__ == "__main__":
    Process(target=start_kernel).start()
    time.sleep(1)

    setup_communication_file()
    start_ipython()