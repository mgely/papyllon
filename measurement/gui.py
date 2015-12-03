from Tkinter import *
import ttk
import json
from utility import byteify

class SetupGUI(object):
    """docstring for SetupGUI"""
    def __init__(self, setup_file_adress, method):

        self.setup_file_adress = setup_file_adress
        self.method = method


        with open(self.setup_file_adress,"r") as f:
            previous_setup =  byteify(json.load(f))
        
        entry_width = 60

        self.root = Tk()
        self.root.title("Start measurement")
        self.root.lift()

        # Put a main frame in the root, which has a padding (NWES)
        mainframe = ttk.Frame(self.root,padding = (3,3,3,3))

        # Put it in column 0, row 0 of the root and have it stick 
        # to all sides upon resizing
        mainframe.grid(column = 0, row = 0, sticky = (N,W,E,S))

        mainframe.columnconfigure(0,weight = 1)
        mainframe.rowconfigure(0,weight = 1)

        ttk.Label(mainframe,
            text = "Your name: "
            ).grid(column = 0, row = 0, sticky = E)

        self.name = StringVar()
        name_entry = ttk.Entry(mainframe,
            width = entry_width,
            textvariable = self.name)
        name_entry.grid(column = 1, row = 0, sticky = (W, E))
        name_entry.insert(0, previous_setup["name"])



        ttk.Label(mainframe,
            text = "Device name: "
            ).grid(column = 0, row = 1, sticky = E)

        self.device = StringVar()
        device_entry = ttk.Entry(mainframe,
            textvariable = self.device)
        device_entry.grid(column = 1, row = 1, sticky = (W, E))
        device_entry.insert(0, previous_setup["device"])



        ttk.Label(mainframe,
            text = "Experiment name: "
            ).grid(column = 0, row = 2, sticky = E)

        self.experiment = StringVar()
        experiment_entry = ttk.Entry(mainframe,
            textvariable = self.experiment)
        experiment_entry.grid(column = 1, row = 2, sticky = (W, E))
        experiment_entry.insert(0, previous_setup["experiment"])



        ttk.Label(mainframe,
            text = "Data saved in C:/papyllon/data/your_name/device_name/(time_stamp)_experiment_name"
            ).grid(columnspan = 2, row = 3, sticky = W)




        ttk.Label(mainframe,
            text = "Notes: "
            ).grid(column = 0, row = 4, sticky = E)

        self.notes_entry = Text(mainframe,
            height = 13,
            font = ("Arial", "9"))
        self.notes_entry.grid(column = 1, row = 4, sticky = (W, E))
        self.notes_entry.insert('1.0', previous_setup["notes"])
        # To get text use: notes = self.notes_entry.get("1.0",'end-1c')



        ttk.Label(mainframe,
            text = "When finished, notify the following email adresses:"
            ).grid(columnspan = 2, row = 5, sticky = W)

        self.emails = StringVar()
        emails_entry = ttk.Entry(mainframe,
            textvariable = self.emails)
        emails_entry.grid(columnspan = 2, row = 6, sticky = (W, E))
        emails_entry.insert(0, previous_setup["emails"])

        # Button that calls the function
        ttk.Button(mainframe,
            text = "Start",
            command = self.start
            ).grid(column = 2, row = 7, sticky = W)

        # # Keyboard shortcut for start
        # root.bind('<Return>',start)

        # Configure all the widgets to have the same padding
        for child in mainframe.winfo_children():
            child.grid_configure(padx = 5, pady = 5)

        # Define where the cursor will be initially
        name_entry.focus()

        # All of the expansion will happen in the middle when you expand
        # the window
        mainframe.columnconfigure(1,weight = 1)

        # Go
        self.root.mainloop()

    def save_to_file(self,file_adress):
        d = {
        'name': str(self.name.get()),
        'device': str(self.device.get()),
        'experiment': str(self.experiment.get()),
        'notes': str(self.notes_entry.get("1.0",'end-1c')),
        'emails': str(self.emails.get())
        }

        with open(file_adress,"w") as f:
            json.dump(d, f, sort_keys=True, indent=4, separators=(',', ': '))

    def start(self,*args):
        self.save_to_file(self.setup_file_adress)
        self.method("self.start_measurement('"+self.name.get()+"','"+str(self.device.get())+"','"+str(self.experiment.get())+"')")
        self.root.destroy()

