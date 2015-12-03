# measurement script
f_list = np.linspace(4200000000.0,4350000000.0,401)
pna = qt.instruments.create('pna','PNA_N5221A_sal',address = 'TCPIP::192.168.1.42::INSTR')
curr_source = qt.instruments.create('curr_source','keysight_source_B2961A',address = 'TCPIP::192.168.1.56::INSTR')
var_att = qt.instruments.create('var_att','agilent_var_attenuator',address = 'TCPIP::192.168.1.113::INSTR')
pna.reset()
pna.setup(start_frequency = 4200000000.0,stop_frequency = 4350000000.0,measurement_format = 'MLOG')
pna.set_resolution_bandwidth(5)
pna.set_sweeppoints(401)
pna.set_averages_on()
pna.set_averages(4)
curr_source.set_output_type('CURR')
curr_source.set_voltage_protection(0.1)
curr_source.set_protection_state(True)
curr_source.set_state(True)
var_att.set_var_att(70)
qt.mstart()
data = qt.Data(name='data')
data.create_file(datadirs=r'D:\steelelab-nas\measurement_data\BlueFors\door_computer\Sal\Kurma6A_C\2015_12_3_______17.28.54_____SingleTone__overnight_assp_zoom')
spyview_process_3D(reset=True)
data.add_coordinate('Cavity Frequency [Hz]')
data.add_coordinate('I_coil [A]')
data.add_coordinate('PNA power [dBm]')
data.add_value('Transmission (dBm)')
data.add_value('f_data [dBm]')
data.add_value('Phase')
pna.set_power(-12.0)
curr_source.ramp_source_curr(-0.00048)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00048*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=True)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047976)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047976*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047952)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047952*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047928)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047928*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047904)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047904*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.0004788)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.0004788*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047856)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047856*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047832)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047832*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047808)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047808*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047784)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047784*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.0004776)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.0004776*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047736)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047736*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047712)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047712*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047688)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
trace = pna.fetch_data(polar=True)
tr2 = pna.data_f()
data.add_data_point(f_list, list(-0.00047688*ones(len(f_list))),list(-12.0*ones(len(f_list))),trace[0], tr2, np.unwrap(trace[1]))
data.new_block()
spyview_process_3D(data,4200000000.0,4350000000.0,-0.00042,-0.00048,-12.0,newoutermostblockval=False)
qt.msleep(0.01)
curr_source.ramp_source_curr(-0.00047664)
pna.reset_averaging()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()
pna.auto_scale()
pna.sweep()