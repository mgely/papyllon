import time
import zmq
import gui
from os import getcwd
from Tkinter import *
import ttk
import json

class Op(object):
    """docstring for SetupGUI"""
    def __init__(self):
        self.measurement_communication_port="5556"
        self.setup_communication()
        self.papyllon_folder_address = self.get_papyllon_folder_address()
        self.x = 0
        self.y = 0
        self.loader()

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



    def get_papyllon_folder_address(self):
        module_address = getcwd()

        # extracts the papyllon folder adress
        papyllon_folder_address = module_address.replace('\\measurement','')

        return papyllon_folder_address

    def get_setup_file_address(self):
        return self.papyllon_folder_address+'\\measurement\\setup.json'

    def loader(self):
        self.root = Tk()
        self.root.iconbitmap(default='transparent.ico')
        self.root.lift()


        self.root.title("Start measurement")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("+%d+%d" % (self.x, self.y))


        # Put a main frame in the root, which has a padding (NWES)
        self.mainframe = ttk.Frame(self.root,padding = (3,3,3,3))

        # Put it in column 0, row 0 of the root and have it stick 
        # to all sides upon resizing
        self.mainframe.grid(column = 1, row = 0, sticky = (N,W,E,S))

        self.mainframe.columnconfigure(0,weight = 1)
        self.mainframe.rowconfigure(0,weight = 1)
      


        ttk.Button(self.mainframe,
            text = "Load measurement",
            command = self.go_to_controller,
            width = 30
            ).grid(column = 1, row = 0, sticky = (W,E))

        ttk.Button(self.mainframe,
            text = "Talk to kernel",
            command = self.interface,
            ).grid(column = 1, row = 1, sticky = (W,E))

        # Configure all the widgets to have the same padding
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx = 5, pady = 5)

        # Go
        self.root.mainloop()

    def controller(self):
        self.root = Tk()
        self.root.lift()

        self.root.title("Controller")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry("+%d+%d" % (self.x, self.y))


        # Put a main frame in the root, which has a padding (NWES)
        self.mainframe = ttk.Frame(self.root,padding = (3,3,3,3))

        # Put it in column 0, row 0 of the root and have it stick 
        # to all sides upon resizing
        self.mainframe.grid(column = 1, row = 0, sticky = (N,W,E,S))

        self.mainframe.columnconfigure(0,weight = 1)
        self.mainframe.rowconfigure(0,weight = 1)

        # Time enquiry
        ttk.Button(self.mainframe,
            width = 30,
            text = "Time?",
            command = self.time
            ).grid(column = 1, row = 0, sticky = (W,E))

        # Tests
        ttk.Button(self.mainframe,
            text = "Test",
            command = self.test
            ).grid(column = 1, row = 1, sticky = (W,E))

        # Starts
        ttk.Button(self.mainframe,
            text = "Start",
            command = self.start
            ).grid(column = 1, row = 2, sticky = (W,E))

        # Stops measurement
        ttk.Button(self.mainframe,
            text = "Stop",
            command = self.stop
            ).grid(column = 1, row = 3, sticky = (W,E))

        # Exit measurement
        ttk.Button(self.mainframe,
            text = "Exit measurement",
            command = self.go_to_loader,
            ).grid(column = 1, row = 4, sticky = (W,E))

        ttk.Button(self.mainframe,
            text = "Talk to kernel",
            command = self.interface,
            ).grid(column = 1, row = 5, sticky = (W,E))


        # Configure all the widgets to have the same padding
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx = 5, pady = 5)

        # Go
        self.root.mainloop()

    def interface(self):
        self.interface_root = Tk()
        self.interface_root.lift()


        self.interface_root.title("Talk directly to the measurement kernel")
        screen_width = self.interface_root.winfo_screenwidth()
        screen_height = self.interface_root.winfo_screenheight()
        self.interface_root.geometry("+%d+%d" % (self.x, self.y)) 

        self.interface_mainframe = ttk.Frame(self.interface_root,padding = (3,3,3,3))

        # Put it in column 0, row 0 of the root and have it stick 
        # to all sides upon resizing
        self.interface_mainframe.grid(column = 1, row = 0, sticky = (N,W,E,S))

        self.interface_mainframe.columnconfigure(0,weight = 1)
        self.interface_mainframe.rowconfigure(0,weight = 1)

        self.to_execute = StringVar()
        to_execute_entry = ttk.Entry(self.interface_mainframe,
            width = 50,
            textvariable = self.to_execute)
        to_execute_entry.grid(column = 0, row = 0, sticky = (W, E))
        to_execute_entry.insert(0, 'self.')

        ttk.Button(self.interface_mainframe,
            text = "Go",
            command = self.send_in_interface
            ).grid(column = 1, row = 0, sticky = (W,E)) 

        # Configure all the widgets to have the same padding
        for child in self.mainframe.winfo_children():
            child.grid_configure(padx = 5, pady = 5)
        
        self.interface_root.mainloop()


    def go_to_controller(self):
        self.get_gui_position()
        self.initialize_measurement()
        self.root.destroy()
        self.controller()
    def go_to_loader(self):
        self.get_gui_position()
        self.switch_measurement_off()
        self.root.destroy()
        self.loader()


    def send_in_interface(self):
        self.send(str(self.to_execute.get()))
        self.interface_root.destroy()

    def get_gui_position(self):
        self.x = self.root.winfo_x()
        self.y = self.root.winfo_y()


    def initialize_measurement(self):
        self.send('self.initialize_measurement()')

    def switch_measurement_off(self):
        self.send('self.set_state("OFF")')


    def send(self,code):
        self.socket.send(code)

    def test(self):
        self.send("self.test_measurement()")

    def start(self):
        gui.SetupGUI(setup_file_adress = self.get_setup_file_address(), 
            method = self.send)

    def stop(self):
        self.send("self.stop()")

    def time(self):
        self.send("self.print_measurement_time()")

if __name__ == "__main__":
    Op()