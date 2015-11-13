# This file contains user-specific settings for qtlab.
# It is run as a regular python script.

# Do not change the following line unless you know what you are doing
config.remove([
            'datadir',
            'startdir',
            'startscript',
            'scriptdirs',
            'user_ins_dir',
            'startgui',
            'gnuplot_terminal',
            ])

## This sets a default location for data-storage
#config['datadir'] = 'd:/data'

## This sets a default directory for qtlab to start in
#config['startdir'] = 'd:/scripts'

## This sets a default script to run after qtlab started
#config['startscript'] = 'initscript.py'

# Add directories containing scripts here. All scripts will be added to the
# global namespace as functions.
config['scriptdirs'] = [
        'examples/scripts',
#        'd:/scripts',
]

## This sets a user instrument directory
## Any instrument drivers placed here will take
## preference over the general instrument drivers
#config['user_insdir'] = 'd:/instruments'

## For adding additional folders to the 'systm path'
## so python can find your modules
#import sys
#sys.path.append('d:/folder1')
#sys.path.append('d:/folder2')

# Whether to start the GUI automatically
config['startgui'] = True

# Default gnuplot terminal
#config['gnuplot_terminal'] = 'x11'
#config['gnuplot_terminal'] = 'wxt'
#config['gnuplot_terminal'] = 'windows'
