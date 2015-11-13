var_att=visa.instrument('TCPIP0::192.168.1.113::INSTR')
print 'FOUND  '+ var_att.ask('*IDN?')
qt.msleep(1)
var_att.write('CONF:X AG8494')
var_att.write('CONF:Y AG8496')

##VARIABLE ATT setup

att_start=18
att_stop=48
att_points=4

att_list=np.linspace(att_start,att_stop,att_points)
for att in att_list:
    attSP=divmod(att,10)
    var_att.write('ATT:X '+str(attSP[1]))
    var_att.write('ATT:Y '+str(attSP[0]*10))
    execfile('bf-PNA_trace_withFixgate_cavityFreq_drive.py')

qt.mend()

