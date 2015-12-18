INSTALL


Run the following command:

pip install --upgrade google-api-python-client
pip install python-pptx
pip install pypiwin32

LAUNCH

run pappylon.bat



BASIC CONCEPT


A. System architecture


Locally qtlab kernal runs, that is directly accessible through the QTLab console

or is accessible through the QTLabKernalAPI.

The Measurement console controls QTLab, and does not allow direct user input.

Input is applied through the GUI.

Options are:

1) Talk to kernal

direct interface to qtlab through the QtlabKernalAPI

2) Load measurement

Here is standard measurement controls, looks up the settings.json measurement definition.




B. Qtlab control structure

Main object is the QTLabVariable, that defines a variable inside the measurement
kernal (Qtlab hence forth). 

For example:

self.frequency_list = qtlabAPI.QTLabVariable(self.qt,'frequency_list', 
			'np.linspace',
			self.freq_start,
			self.freq_stop,
			self.freq_points)


C. Communication (QtlabKernalAPI)


short note on comms




DATA SCREEN SHOTS

after the measurement a gui request pops-up with spyview that request you 
to take a screenshot.

either use snipping tool (hacked version) + press Done

or go to spyview massage the data, and press ALT-p.




MISCELLANEOUS

PPT

generate_ppt.py is a script to compile a ppt of data snapshots
of a directory with measurements


EMAIL

To switch on e-mail functionalities excecute email_operator_test.py



