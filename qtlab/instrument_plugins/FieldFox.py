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

##################################
## QTlab driver written by Sal J Bosman
## Steelelab-MED-TNW-TU Delft
## contact: s.bosman@tudelft.nl or saljuabosman@mac.com
##################################


from instrument import Instrument
import visa
import types
import logging
import numpy

import qt

class FieldFox(Instrument):
    '''
    This is a general multi purpose driver to write & read queries with a VISA machine

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'universal_driver',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','universal_driver',
        address='TCPIP0::192.168.1.151::inst0::INSTR'
    '''

    def __init__(self, name, address):
        '''
        Initializes the any_device, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
           
        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)


        # Add parameters to wrapper

        self.add_parameter('start_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz', minval=1, maxval=14e9)
        self.add_parameter('stop_frequency', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz', minval=1, maxval=14e9)
        self.add_parameter('sweeppoints',
                           flags=Instrument.FLAG_GETSET,
                           units=' ', minval=1, maxval=32001,
                           type=types.FloatType)
        self.add_parameter('sweeptime',
                           flags=Instrument.FLAG_GETSET,
                           units='sec',
                           type=types.FloatType)
        self.add_parameter('resolution_bandwidth', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='Hz')
        self.add_parameter('power', type=types.IntType,
                           flags=Instrument.FLAG_GETSET,
                           units='dBm',minval=-30, maxval=30)

        self.add_parameter('mode',type=types.StringType,
                           flags=Instrument.FLAG_GETSET)

        self.add_parameter('sweep',type=types.StringType,
                           flags=Instrument.FLAG_GETSET)
        
        # Add functions to wrapper
        #self.add_function('set_mode_volt_ac')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

# --------------------------------------
#           functions
# --------------------------------------
# going to use Agilent command set
    def startup(self):
        self._visainstrument.write('cmdset agilent')
    def get_function(self):
        return (self._visainstrument.ask('FUNCtion?'))
##    def m_volt_ac(self):
##        return self._visainstrument.ask('MEASure:VOLTage:AC?')


    def value(self):
        return self._visainstrument.ask('READ?')

    def read(self):
        self._visainstrument.read()
    def write(self,string):
        self._visainstrument.write(string)
    def query(self,string):
        return self._visainstrument.ask(string)

    def autoscale(self):
        return self._visainstrument.write("DISP:WIND:TRAC:Y:AUTO")

    
    
        #it sends visa.instrument(adress).ask(string)     ben
    #def conf_volt_dc(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:DC DEF, %s' % (number))
    #def conf_volt_ac(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:AC DEF, %s' % (number))
    

# --------------------------------------
#           parameters
# --------------------------------------

    def do_get_mode(self):
        return self._visainstrument.ask("INST:SEL?")
    def do_get_sweeppoints(self):
        return self._visainstrument.ask('SWE:POIN?')
    def do_get_start_frequency(self): #in Hz
        return float(self._visainstrument.ask('FREQ:STAR?'))
    def do_get_stop_frequency(self): #in Hz
        return float(self._visainstrument.ask('FREQ:STOP?'))
    def do_get_resolution_bandwidth(self):
        return float(self._visainstrument.ask('BAND?'))


    def do_set_mode(self,mode):
        return self._visainstrument.write('INST:SEL "%s"' % (mode))
    def do_set_sweeppoints(self,number):
        return self._visainstrument.write('SWE:POIN %s' %(number))
    def do_set_start_frequency(self,number): #in Hz
        return self._visainstrument.write('FREQ:STAR %s' % (number)) 
    def do_set_stop_frequency(self,number): #in Hz
        return self._visainstrument.write('FREQ:STOP %s' % (number))
    def do_set_resolution_bandwidth(self,number):
        if self._visainstrument.ask("INST:SEL?") == '\"SA\"': # If se are using it as a Spectrum analizer
            return self._visainstrument.write('BAND %s' % (number))
        elif self._visainstrument.ask("INST:SEL?") == '\"NA\"': # If se are using it as a Network analizer
            return self._visainstrument.write('SENS:BWID %s' % (number))


        
    def do_set_power(self,number):
        return self._visainstrument.write('SOUR:POW %s' % (number))
    def set_ref(self, INT_or_EXT):
        return self._visainstrument.write('SENS:ROSC:SOUR %s' % (INT_or_EXT))

# --------------------------------------
#           functions
# --------------------------------------

    def sweep(self):
        self._visainstrument.write('INIT:CONT OFF')
        self._visainstrument.write('INIT:IMM')
        
        a=0
        while a==0:
            qt.msleep(0.05)
            try:
                a=eval(self._visainstrument.ask('*OPC?;'))
                break
            except(KeyboardInterrupt, SystemExit):
                raise
            except:
                a=0
        return 
       

    def fetch_data(self):
        if self._visainstrument.ask("INST:SEL?") == '\"SA\"': # If se are using it as a Spectrum analizer
            trace = self._visainstrument.ask('TRAC:DATA?')
            trace = map(float,trace.split(','))
        elif self._visainstrument.ask("INST:SEL?") == '\"NA\"': # If se are using it as a Network analizer
            trace = [[],[],[]]
            self._visainstrument.write('CALC:FORM MLOG')
            tr = self._visainstrument.ask('CALC:DATA:FDAT?')
            trace[0] = map(float,tr.split(','))

            self._visainstrument.write('CALC:FORM MLIN')
            tr = self._visainstrument.ask('CALC:DATA:FDAT?')
            trace[1] = map(float,tr.split(','))

            self._visainstrument.write('CALC:FORM UPH')
            tr = self._visainstrument.ask('CALC:DATA:FDAT?')
            trace[2] = map(float,tr.split(','))

        return trace

# --------------------------------------
#           Internal Routines
# --------------------------------------
#

    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
#        #set correct commandset
#        self._visainstrument.write('cmdset agilent')
#        return self._visainstrument.write('*IDN?')
##        if self._change_display:
##            self.set_display(False)
##            #Switch off display to get stable timing
##        if self._change_autozero:
##            self.set_autozero(False)
##            #Switch off autozero to speed up measurement

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
##        if self._change_display:
##            self.set_display(True)
##        if self._change_autozero:
##            self.set_autozero(True)
    
