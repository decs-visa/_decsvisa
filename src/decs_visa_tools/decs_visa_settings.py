"""
Utility module that holds some useful settings
"""

from pathlib import Path

#############################################
#    Configuration settings required     #
#############################################

# path to the system settings .env file
file_path = Path(".env")
#file_path = Path("../../src/qcodes_contrib_drivers/drivers/OxfordInstruments/_decsvisa/src/.env")

# NB this can also be an
# /absolute/path/to/file/.env

DOT_ENV_PATH = file_path

##############################################

# required for features such as match/case
PYTHON_MIN_MAJOR = 3
PYTHON_MIN_MINOR = 10

# required at least for now due to an issue
# with autobahn asyncio wamp with python 3.14

PYTHON_MAX_MAJOR = 3
PYTHON_MAX_MINOR = 13

# required at least for now due to an issue
# with autobahn asyncio wamp with autobahn > 24

AUTOBAHN_MAX_VERSION = '24.4.2'


# Connection details for the socket_server
# These values should be consistent with
# those in the .env file.
PORT = 33576
HOST = "localhost"

# queue message to indicate system should stop
# this can be sent from the client.
SHUTDOWN = "SHUTDOWN"

# socket server write delimiter
WRITE_DELIM = "\n"

# socket server read delimiter
READ_DELIM = "\n"