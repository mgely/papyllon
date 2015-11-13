# RS_SMB100A.py driver for Rohde & Schwarz SMB100A signal generator
# Harold Meerwaldt <H.B.Meerwaldt@tudelft.nl>, 2012
# Scott Johnston <jot@mit.edu>, 2012

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import visa
import types
import logging
import numpy

import qt

def bool_to_str(val):
    '''
    Function to convert boolean to 'ON' or 'OFF'
    '''
    if val == True:
        return "ON"
    else:
        return "OFF"

class RS_SMB100A(Instrument):
    '''
    This is the driver for the Rohde & Schwarz SMB100A signal generator

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'RS_SMB100A',
        address='<GBIP address>',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','universal_driver',
        address='TCPIP0::192.168.1.43::inst0::INSTR'
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the SMB100A, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Rohde & Schwarz FSL spectrum analyzer')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)

        # Add parameters to wrapper
        #State parameters (turn on/off instrument states)
        self.add_parameter('RF_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        self.add_parameter('Modulation_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        self.add_parameter('LF_output_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        self.add_parameter('AM_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        self.add_parameter('FM_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        self.add_parameter('pulse_state',
                           flags=Instrument.FLAG_GETSET, units='',
                           type=types.BooleanType)
        #Measurement parameters
        self.add_parameter('RF_frequency',
                            flags=Instrument.FLAG_GETSET,
                            units='MHz', minval=0.009, maxval=12700,
                            type=types.FloatType)
        self.add_parameter('RF_power',
                            flags=Instrument.FLAG_GETSET,
                            units='dBm', minval=-110, maxval=30,
                            type=types.FloatType)
        self.add_parameter('RF_phase',
                           flags=Instrument.FLAG_GETSET,
                           units='degrees',minval=-720,maxval=720,
                           type=types.FloatType)

        self.add_parameter('LF_output_voltage',
                           flags=Instrument.FLAG_GETSET,
                           units='V',minval=0.0,maxval=3.0,
                           type=types.FloatType)
        self.add_parameter('LF_frequency',
                           flags=Instrument.FLAG_GETSET,
                           units='KHz',minval=0.0001,maxval=1000,
                           type=types.FloatType)

        self.add_parameter('AM_depth',
                           flags=Instrument.FLAG_GETSET,
                           units='%',minval=-100,maxval=100,
                           type=types.FloatType)
        self.add_parameter('FM_deviation',
                           flags=Instrument.FLAG_GETSET,
                           units='kHz',minval=0.0,maxval=10000,
                           type=types.FloatType)
        self.add_parameter('reference',
                           flags=Instrument.FLAG_GETSET,
                           type=types.StringType)
        self.add_parameter('pulse_source',
                           flags=Instrument.FLAG_GETSET,
                           type=types.StringType)
        self.add_parameter('pulse_period',
                           flags=Instrument.FLAG_GETSET,units='us',
                           type=types.FloatType)
        self.add_parameter('pulse_width',
                           flags=Instrument.FLAG_GETSET,units='us',
                           type=types.FloatType)                
        self.add_parameter('AM_source',
                           flags=Instrument.FLAG_GETSET,
                           type=types.StringType)
        self.add_parameter('FM_source',
                           flags=Instrument.FLAG_GETSET,
                           type=types.StringType)
        
        # Add functions to wrapper
##        self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        self.add_function('reset')
        self.add_function('get_all')
                
        if reset:
           self.reset()
        else:
           self.get_all()


# --------------------------------------
#           functions
# --------------------------------------
    def reset(self):
        self._visainstrument.write('*RST')

    def get_all(self):
        self.get_LF_output_voltage()
        self.get_AM_depth()
        self.get_LF_output_state()
        self.get_RF_power()
        self.get_LF_frequency()
        self.get_RF_phase()
        self.get_FM_state()
        self.get_RF_state()
        self.get_Modulation_state()
        self.get_AM_state()
        self.get_FM_deviation()
        self.get_RF_frequency()


    def do_get_RF_frequency(self):
	return float(self._visainstrument.ask('FREQ?'))/1e6

    def do_set_RF_frequency(self,frequency):
        return self._visainstrument.write('FREQ %sMHz' % frequency)

    def do_get_RF_power(self):
	return self._visainstrument.ask('POW?') # in dBm

    def do_set_RF_power(self,power):
        return self._visainstrument.write('POW %s' % power) # in dBm
	
    def do_get_RF_state(self):
	return bool(int(self._visainstrument.ask('OUTP?')))

    def do_set_RF_state(self, state):
        '''
        Turn ON/OFF RF output
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('OUTP %s' % state)

    def do_get_RF_phase(self):
        return float(self._visainstrument.ask('PHAS?'))

    def do_set_RF_phase(self,phase):
        return self._visainstrument.write('PHAS %s' % phase)
                     
    def do_get_Modulation_state(self):
        return bool(int(self._visainstrument.ask('MOD:STAT?')))

    def do_set_Modulation_state(self,state):
        '''
        Activate all modulation options currently on (AM,FM,PM)
        '''
        state=bool_to_str(state)     
        return self._visainstrument.write('MOD:STAT %s' % state)

    def do_get_LF_output_state(self):
        return bool(int(self._visainstrument.ask('LFO:STAT?')))

    def do_set_LF_output_state(self,state):
        '''
        Turn ON/OFF LF output. Has no effect on RF modulation.
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('LFO:STAT %s' % state)

    def do_get_LF_output_voltage(self):
        return float(self._visainstrument.ask('LFO:VOLT?'))

    def do_set_LF_output_voltage(self,volts):
        return self._visainstrument.write('LFO:VOLT %s' % volts)

    def do_get_LF_frequency(self):
        return float(self._visainstrument.ask('LFO:FREQ?'))/1e3

    def do_set_LF_frequency(self,frequency): #kHz
        return self._visainstrument.write('LFO:FREQ %skHz' % frequency)

    def do_get_AM_state(self):
        return bool(int(self._visainstrument.ask('AM:STAT?')))

    def do_set_AM_state(self,state):
        '''
        Turn ON/OFF AM modulation. Not active unless Modulation_state==True.
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('AM:STAT %s' % state)

    def do_get_AM_depth(self):
        return float(self._visainstrument.ask('AM:DEPT?'))

    def do_set_AM_depth(self,depth): #percent
        return self._visainstrument.write('AM:DEPT %s' % depth)

    def do_get_AM_source(self):
        return self._visainstrument.ask('AM:SOUR?')

    def do_set_AM_source(self,value): 
        if value != 'INT' and value != 'EXT':
            print "Allowed values are: 'INT', 'EXT'"
        return self._visainstrument.write('AM:SOUR ' + value)


    def do_get_FM_state(self):
        return bool(int(self._visainstrument.ask('FM:STAT?')))

    def do_set_FM_state(self,state):
        '''
        Turn ON/OFF FM modulation. Not active unless Modulation_state==True.
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('FM:STAT %s' % state)

    def do_get_FM_deviation(self):
        return float(self._visainstrument.ask('FM?'))/1e3

    def do_set_FM_deviation(self,frequency): #kHz
        return self._visainstrument.write('FM %sKHz' % frequency)

    def do_get_FM_source(self):
        return self._visainstrument.ask('FM:SOUR?')

    def do_set_FM_source(self,value): 
        if value != 'INT' and value != 'EXT':
            print "Allowed values are: 'INT', 'EXT'"
        return self._visainstrument.write('FM:SOUR ' + value)

    def do_get_reference(self):
        return self._visainstrument.ask('ROSC:SOUR?')

    def do_set_reference(self,value): #kHz
        if value != 'INT' and value != 'EXT':
            print "Allowed values are: 'INT', 'EXT'"
        return self._visainstrument.write('ROSC:SOUR ' + value)

    def do_get_pulse_state(self):
        return bool(int(self._visainstrument.ask('PULM:STAT?')))

    def do_set_pulse_state(self,state):
        '''
        Turn ON/OFF pulse modulation. Not active unless Modulation_state==True.
        '''
        state=bool_to_str(state)
        return self._visainstrument.write('PULM:STAT %s' % state)


    def do_get_pulse_source(self):
        return self._visainstrument.ask('PULM:SOUR?')

    def do_set_pulse_source(self,value):
        if value != 'INT' and value != 'EXT':
            print "Allowed values are: 'INT', 'EXT'"
        return self._visainstrument.write('PULM:SOUR ' + value)

    def do_get_pulse_period(self):
        return self._visainstrument.ask('PULM:PER?')

    def do_set_pulse_period(self,value): #us
        return self._visainstrument.write('PULM:PER %s us ' % value)

    def do_get_pulse_width(self):
        return self._visainstrument.ask('PULM:WIDT?')

    def do_set_pulse_width(self,value): #us
        return self._visainstrument.write('PULM:WIDT %s us' % value)

        
    def write(self,string):
        self._visainstrument.write(string)

    def query(self,string):
        return self._visainstrument.ask(string)

# --------------------------------------
#           Internal Routines
# --------------------------------------

    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''


    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
