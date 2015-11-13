def display_time(time):
    hours = time/3600
    minutes = (time-3600*floor(hours))/60
    seconds = (time-3600*floor(hours)-60*floor(minutes))

    return hours, ':', minutes, ':', seconds
    
def run(file_name):
    while(True):
        execfile(file_name)

def run_list(file_list):
    while(True):
        for i in file_list:
            execfile(i)
