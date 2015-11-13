from lib import config, lockfile
import os
from IPython.lib.kernel import get_connection_file

_lockname = os.path.join(config.get_execdir(), 'qtlab.lock')
lockfile.set_filename(_lockname)
del _lockname

msg = "QTlab already running, start with '-f' to force start.\n"
msg += "Press s<enter> to start anyway or just <enter> to quit."
lockfile.check_lockfile(msg)
