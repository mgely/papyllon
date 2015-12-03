from measurement.utility import create_png, add_measurement_to_ppt
import os
import os.path
from stat import S_ISREG, ST_CTIME, ST_MODE
import os, sys, time


device_directory = 'D:\steelelab-nas\measurement_data\BlueFors\door_computer\Sal\Kurma6A_A'
ppt_name  = 'raw.pptx'


folder_list = [os.path.join(device_directory,o) for o in os.listdir(device_directory) if os.path.isdir(os.path.join(device_directory,o))]

# for data_folder in sorted(folder_list):
#     create_png(data_folder)

for data_folder in sorted(folder_list):
    if '2015_11_17_' in data_folder:
        add_measurement_to_ppt(os.path.join(device_directory,ppt_name),data_folder)

