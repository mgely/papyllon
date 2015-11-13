timescale = oscil.get_time_scale()
timeoffset = oscil.get_time_offset()
voltagescale =oscil.get_voltage_scale1()
voltageoffset=oscil.get_voltage_offset1()

print timescale,timeoffset,voltagescale,voltageoffset


stringdata =oscil.get_trace('CHAN1')
bytedata=copy(bytearray(stringdata))[10:]
datalength=len(bytedata)
print datalength
indexdata = linspace(1,datalength,datalength)

amplitude = ((240 - bytedata) * (voltagescale / 25) - ((voltageoffset + voltagescale * 4.6)))
time = (indexdata - 1) * (timescale / 50) - ((timescale * 6) - timeoffset)
