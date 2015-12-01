'''Python script that is called from the paPyllon.bat file
in order to start the measurement kernel

Mario Gely - mario.f.gely@gmail.com
'''

from measurement import Measurement 
from op import Op
from  multiprocessing import Process

def start_operator():
    Op()

if __name__ == "__main__":
    Process(target=start_operator).start()
    Measurement()