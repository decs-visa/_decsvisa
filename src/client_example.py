"""
Simple example of a TCP client that communicates with the
DECS<->VISA socket server
"""
import sys
import time

# import the PyVISA library
import pyvisa as visa

# import some settings - to save looking them up
from decs_visa_tools.decs_visa_settings import SHUTDOWN
from decs_visa_tools.decs_visa_settings import READ_DELIM
from decs_visa_tools.decs_visa_settings import WRITE_DELIM
from decs_visa_tools.decs_visa_settings import HOST
from decs_visa_tools.decs_visa_settings import PORT

def main():
    """
	The main TCP/IP client 
	"""
	# set the resource manager to use the PyVISA-py backend
    try:
        rm = visa.ResourceManager('@py')
    except (ModuleNotFoundError, ValueError) as e:
        print(e)
        # perhaps pyvisa-py isn't installed correctly
        sys.exit(1)

    # define the connection parameters for the socket server
    # NB the correct address and port are required
    decs_visa_server_ip = HOST
    decs_visa_server_port = PORT

    # generate the server connection string
    pyvisa_connection = f"TCPIP0::{decs_visa_server_ip}::{decs_visa_server_port}::SOCKET"

    # define the connection, and configure
    decs_visa = rm.open_resource(pyvisa_connection)

    # Note: When running on Windows, outputs from DECS<->VISA are stored in a decs_visa.log file which will be created in your working directory.
    # Check this file if connection between DECS<->VISA and oi.DECS is not established.

    decs_visa.read_termination = WRITE_DELIM # server write == client read
    decs_visa.write_termination = READ_DELIM # server read == client write
    decs_visa.chunk_size = 204800
    decs_visa.timeout = 10000

    get_idn = "*IDN?"
    try:
        print(f'{get_idn} => {decs_visa.query(get_idn)}')
    except (ConnectionRefusedError, BrokenPipeError) as e:
        print(e)
        print(f"Failed to communicate with server: {pyvisa_connection}")
        print("Is DECS<->VISA running?  Are the server details correct?")
        sys.exit(1)
    except visa.errors.VisaIOError as e:
        print(e)
        print("Server connection established, but no reply.")
        print("Was the WAMP connection established by DECS<->VISA?")
        print("Is the server already in use from another connection?")
        sys.exit(1)

    # Define some test queries (get_ and set_) to send to
    # the socket server
    get_test = "get_MC_T"
    set_test ="set_MC_T"
    # NB - these queries should be in the
    # imported 'command_dictionary' for correct operation

    # Call the queries a few times and print the response
    repeat_n = 20
    try:
        for i in range(repeat_n):
            print(f"{get_test} => {decs_visa.query(get_test)}")

            # change set_ setpoint on each loop
            setpoint = 5 + (-1)**(i+1)
            full_set_string = f"{set_test}:{str(setpoint)}"

            print(f'{full_set_string} => {decs_visa.query(full_set_string)}')
            # NB - it can take some time for the temperature contol
            # instrumentation to report updates to its setpoint

            time.sleep(2)
    except (visa.errors.VisaIOError, ConnectionResetError) as e:
        print(e)
        print("Communication issue with DECS<->VISA server")
        sys.exit(1)

    # Optional - shutdown DECS<->VISA (server and WAMP components)
    # Do this if it is not expected that the server should
    # remain open for further client connections.
    close_server = True # False
    if close_server:
        print(f"Sending: {SHUTDOWN}")
        decs_visa.write(SHUTDOWN)   # can get away with a write here
                                    # as a response is not expected

	# close the connection to the server
    decs_visa.close()

if __name__ == "__main__":
    main()
