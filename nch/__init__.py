import os

import appdirs


APPNAME = 'NewGRF Cargo Helper'
APPAUTHOR = 'NewGRF'
CONFIG_PATH = os.path.join(appdirs.user_data_dir(APPNAME, APPAUTHOR), 'config')
