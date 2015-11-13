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
import numpy as np

import qt


def bool_to_str(val):
    '''
    Function to convert boolean to 'ON' or 'OFF'
    '''
    if val == True:
        return "ON"
    else:
        return "OFF"


class keysight_source_B2961A(Instrument):
    '''
    This is a general multi purpose driver to write & read queries with a VISA machine

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'universal_driver',
        address='',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    i.e. any_device= qt.instruments.create('any_device','universal_driver',address='USB0::0x1AB1::0x0588::DM3L125000570::INSTR')
                                                                             address='TCPIP::192.168.100.21::INSTR'
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
        # Add functions to wrapper
        #self.add_function('set_mode_volt_ac')

        self.current_max = None
        self.voltage_max = None
        
        self.add_function('reset')

        self.add_parameter('bias_current', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='A')

        self.add_parameter('state', type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET, units='')

        self.add_parameter('output_type', type=types.StringType,
                          flags=Instrument.FLAG_GETSET, units='')

        self.add_parameter('bias_voltage', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,
                           units='V')

        self.add_parameter('protection_state', type=types.BooleanType,
                           flags=Instrument.FLAG_GETSET,units='')

        self.add_parameter('voltage_protection', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,units='V')

        self.add_parameter('current_protection', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,units='A')


        self.add_parameter('voltage_max', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,units='V')

        self.add_parameter('current_max', type=types.FloatType,
                           flags=Instrument.FLAG_GETSET,units='A')

        

        self.add_parameter('measure_voltage', type=types.FloatType,
                           flags=Instrument.FLAG_GET,units='V')

        self.add_parameter('measure_current', type=types.FloatType,
                           flags=Instrument.FLAG_GET,units='A')

        self.add_parameter('steady_state_mode', type=types.StringType,
                           flags=Instrument.FLAG_GETSET,units='')
                           
        
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
    def w(self,string):
        self._visainstrument.write(string)
    def q(self,string):
        return self._visainstrument.ask(string)
        #it sends visa.instrument(adress).ask(string)     ben
    #def conf_volt_dc(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:DC DEF, %s' % (number))
    #def conf_volt_ac(self,number):
    #    return self._visainstrument.write('CONFigure:VOLTage:AC DEF, %s' % (number))

    

# --------------------------------------
#           parameters
# --------------------------------------

    def do_get_bias_current(self):
        return float(self._visainstrument.ask("SOUR:CURR?"))

    def do_set_bias_current(self,bias):

        if(self.current_max is not None):
            if(abs(bias)>self.current_max):
                print 'bias current set above above current_max, please set below: ',self.current_max
                return

        self._visainstrument.write('SOUR:CURR %s' % bias)

        new_setting = float(self._visainstrument.ask("SOUR:CURR?"))
        #print 'after setting it is ', new_setting
                
        return new_setting




    def do_get_steady_state_mode(self):
        return self._visainstrument.ask("VOLT:MODE?")

    def do_set_steady_state_mode(self,mode):
        self._visainstrument.write('VOLT:MODE %s' % mode)

        new_setting = self._visainstrument.ask("VOLT:MODE?")
        #print 'after setting it is ', new_setting
                
        return new_setting


    def do_get_voltage_protection(self):
        return float(self._visainstrument.ask("SENS:VOLT:PROT?"))

    def do_set_voltage_protection(self,bias):
        self._visainstrument.write('SENS:VOLT:PROT %s' % bias)

        new_setting = float(self._visainstrument.ask("SENS:VOLT:PROT?"))
        #print 'after setting it is ', new_setting
                
        return new_setting

    def do_get_current_protection(self):
        return float(self._visainstrument.ask("SENS:CURR:PROT?"))

    def do_set_current_protection(self,bias):
        self._visainstrument.write('SENS:CURR:PROT %s' % bias)

        new_setting = float(self._visainstrument.ask("SENS:CURR:PROT?"))
        #print 'after setting it is ', new_setting
                
        return new_setting


    def do_get_current_max(self):
        return self.current_max


    def do_set_current_max(self,value):
        self.current_max = value


    def do_get_voltage_max(self):
        return self.voltage_max


    def do_set_voltage_max(self,value):
        self.voltage_max = value




    def do_get_measure_voltage(self):
        return float(self._visainstrument.ask("MEAS:VOLT?"))

    def do_get_measure_current(self):
        return float(self._visainstrument.ask("MEAS:CURR?"))


    def do_get_bias_voltage(self):
        return float(self._visainstrument.ask("SOUR:VOLT?"))

    def do_set_bias_voltage(self,bias):

        if(self.voltage_max is not None):
            if(abs(bias)>self.voltage_max):
                print 'bias voltage set above above voltage_max, please set below: ',self.voltage_max
                return
    
        self._visainstrument.write('SOUR:VOLT %s' % bias)

        new_setting = float(self._visainstrument.ask("SOUR:VOLT?"))
        #print 'after setting it is ', new_setting
                
        return new_setting


    def do_get_protection_state(self):
        return bool(int(self._visainstrument.ask("OUTP:PROT?")))

    def do_set_protection_state(self,state):
        state=bool_to_str(state)
        return self._visainstrument.write('OUTP:PROT %s' % state)

    def do_get_state(self):
        return bool(int(self._visainstrument.ask("OUTP:STAT?")))

    def do_set_state(self,state):

        if state == False:
            self.ramp_source_curr(0.)

        state=bool_to_str(state)
        return self._visainstrument.write('OUTP:STAT %s' % state)
        
    def do_set_output_type(self, output):
        if output != 'VOLT' and output != 'CURR':
            print 'allowed values are: "VOLT", "CURR"'
        return self._visainstrument.write("SOURCE:FUNC:MODE %s" %output)

    def do_get_output_type(self):
        return self._visainstrument.ask("SOUR:FUNC:MODE?")
    

# --------------------------------------
#           Internal Routines
# --------------------------------------
#

    def reset(self):
        return self._visainstrument.write('SYST:PRES')
        
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

    def ramp_source_curr(self,value, wait=10e-3, step_size=1e-6):
        print 'ramp source to ', value, '\n'
        
        ramp_d = value-self.get_bias_current() 
        ramp_sign = np.sign(ramp_d)

        ramp_bool = True
        while(ramp_bool):
            actual_value=self.get_bias_current()
            if(abs(value-actual_value)<2*step_size):
                self.set_bias_current(value)
                ramp_bool = False
            else:
                self.set_bias_current(actual_value+ramp_sign*step_size)
                qt.msleep(wait)
        return value

    
