#does calibrate the oscilloscope channel in test
def calibrate(self,channel):
    header= HFoscil.get_header(channel)
    exec('HFoscil.set_voltage_position'+str(channel)+'(0)')
    exec('HFoscil.set_voltage_scale'+str(channel)+'(10)')
    trace = HFoscil.get_trace(channel,header[2])
    min_v=trace.min()
    max_v=trace.max()
    #10 steps in y
    range_v = max_v - min_v
    newscale = range_v/20
    round(newscale,2)
    exec('HFoscil.set_voltage_scale'+str(channel)+'('+str(newscale)+')')
