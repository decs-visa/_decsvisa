"""
Contains the main DECS<->VISA application.

Starts the simple_socket_server in its own thread and then
starts the WAMP component - providing each with two queue
objects for IPC
"""
import queue
import threading
import os
import sys
from sys import version_info

from dotenv import load_dotenv

from autobahn._version import __version__ as autobahn_version

from autobahn.asyncio.wamp import ApplicationRunner

from decs_visa_components.simple_socket_server import simple_server
from decs_visa_components.wamp_component import Component
from decs_visa_tools.base_logger import logger

# Import some settings
from decs_visa_tools.decs_visa_settings import PYTHON_MIN_MAJOR
from decs_visa_tools.decs_visa_settings import PYTHON_MIN_MINOR
from decs_visa_tools.decs_visa_settings import PYTHON_MAX_MAJOR
from decs_visa_tools.decs_visa_settings import PYTHON_MAX_MINOR
from decs_visa_tools.decs_visa_settings import AUTOBAHN_MAX_VERSION
from decs_visa_tools.decs_visa_settings import SHUTDOWN
# and the path to the system settings .env file
from decs_visa_tools.decs_visa_settings import DOT_ENV_PATH

def main():
    """
    The application loop
    """
    logger.info('DECS<->VISA start up')

    # Read in user / router / server details
    load_dotenv(DOT_ENV_PATH, verbose=True)
    # there isn't really much in the way of useful error reporting
    # from load_dotenv, so check that something was read after this
    user =         os.getenv("WAMP_USER")
    user_secret =  os.getenv("WAMP_USER_SECRET")
    url =          os.getenv("WAMP_ROUTER_URL")
    realm =        os.getenv("WAMP_REALM")
    interface =    os.getenv("BIND_SERVER_TO_INTERFACE")
    port =         os.getenv("SERVER_PORT")

    try:
        assert isinstance(user,
                          str), f"Failed to read WAMP_USER from .env {DOT_ENV_PATH}"
        assert isinstance(user_secret,
                          str), f"Failed to read WAMP_USER_SECRET from .env {DOT_ENV_PATH}"
        assert isinstance(url,
                          str), f"Failed to read WAMP_ROUTER_URL from .env {DOT_ENV_PATH}"
        assert isinstance(realm,
                          str), f"Failed to read WAMP_REALM from .env {DOT_ENV_PATH}"
        assert isinstance(interface,
                          str), f"Failed to read BIND_SERVER_TO_INTERFACE from .env {DOT_ENV_PATH}"
        assert isinstance(port,
                          str), f"Failed to read SERVER_PORT from .env {DOT_ENV_PATH}"
    except AssertionError as e:
        logger.info(e)
        # we know we don't have the info to run, so as this cannot work
        logger.info("Abort and exit 1")
        sys.exit(1)

    # Create the shared queues and launch socket server thread
    queries = queue.Queue(maxsize=1)
    responses = queue.Queue(maxsize=1)

    # Start the socket server thread
    server_thread = threading.Thread(target = simple_server,
                                     args =(interface, port, queries, responses, ))
    server_thread.start()

    # Start the WAMP session
    runner = ApplicationRunner(url, realm, extra=dict(
                                            input_queue=queries,
                                            output_queue=responses,
                                            user_name=user,
                                            user_secret=user_secret))
    try:
        # Run the WAMP component
        # ideally disable logging from autobahn
        # but that doesn't quite work...
        runner.run(Component, log_level='critical')
        # if running in a linux terminal you could always
        # python3 ./decs_visa.py > /dev/null
    # Some WAMP methods raise at the Exception level
    except (KeyboardInterrupt, Exception) as e:
        # Catch keyboard / kernel interrupt here.
        # as well as any other more fundamental WAMP
        # error - shut down the socket server via
        # its input queue to exit.
        if isinstance(e, KeyboardInterrupt):
            logger.info("Keyboard Interrupt - shutdown")
        else:
            logger.info("WAMP component error: %s", e)
        try:
            # WAMP component may have requested
            # the socket server to close on exit
            # unless the WAMP connection was never
            # established, so just in case
            _ = responses.get_nowait()
        except queue.Empty:
            pass
        # Will cause the socket server to
        # close so the thread can join() below
        responses.put(SHUTDOWN)

    server_thread.join()
    logger.info("DECS<->VISA stopped")
    sys.exit(0)

if __name__ == "__main__":
    if version_info < (PYTHON_MIN_MAJOR, PYTHON_MIN_MINOR):
        print("Python version not compatible")
        print(f"System is running: Major: {version_info.major}; Minor: {version_info.minor}")
        print(f"Minimum requirements: Major: {PYTHON_MIN_MAJOR}; Minor: { PYTHON_MIN_MINOR}")
    elif version_info > (PYTHON_MAX_MAJOR, PYTHON_MAX_MINOR):
        print("Python version not compatible")
        print(f"System is running: Major: {version_info.major}; Minor: {version_info.minor}")
        print(f"Maximum requirements: Major: {PYTHON_MAX_MAJOR}; Minor: { PYTHON_MAX_MINOR}")
    elif autobahn_version > AUTOBAHN_MAX_VERSION:
        print("autobahn version not compatible")
        print(f"System is running: {autobahn_version}")
        print(f"Maximum requirements: {AUTOBAHN_MAX_VERSION}")       
    else:
        main()
