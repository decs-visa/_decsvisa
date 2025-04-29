"""
 Module to provide some utility methods for mapping 'short'
 commands recieved from the socket server into the correct
 WAMP uri / argument lists.
"""

import time
import typing 

from .base_logger import logger

from .command_dictionary import Proteox_cmd_uri as cmd_uri

def decs_request_parser(cmd: str) -> str:
    """
    From the cmd string passed to the socket server, determine the correct
    WAMP uri to call - requests shouldn't have a :<payload>
    """
    # assume it is a get_ command
    uri = cmd_uri.get(cmd)
    try:
        assert isinstance(uri, str), "uri not returned from command_dictionary"
    except AssertionError as e:
        raise ValueError(e) from e
    # if the uri is found, it can be returned
    return uri

def decs_command_parser(cmd: str) -> tuple [str, list]:
    """
    From the cmd string passed to the socket server, determine the correct
    WAMP uri to call/publish and package the arguments to suit
    """

    # Check to see if there is a 'payload' for a
    # 'set_' command - delimiter :
    cmd_parts = cmd.split(':')
    try:
        assert len(cmd_parts) > 1, "set_ commands must have a :<payload>"
    except AssertionError as e:
        raise ValueError(e) from e
    uri = cmd_uri.get(cmd_parts[0].strip())
    try:
        assert isinstance(uri, str), "uri not returned from cmd_dict"
    except AssertionError as e:
        raise ValueError(e) from e
    args: list[typing.Any]
    args = []
    # Given the cmd and the uri - decide how to process the information
    # to form the correct WAMP messages for DECS
    if "temperature_control" in uri and uri.endswith("setpoint"):
        # set_ command for temperature
        args.append(float(str(cmd_parts[1]).strip()))
        args.append(1)
    elif "temperature_control" in uri and uri.endswith("power"):
        # set_ command for power
        args.append(float(str(cmd_parts[1]).strip()))
        if cmd_parts[0].endswith("OFF"):
            # utility function to ensure heater output is disabled
            args.append(False)
        else:
            # ensure heater output is enabled
            args.append(True)
            
    elif uri.endswith("circulate_rate") or uri.endswith("circulate_sample_temperature"):
        args.append(float(str(cmd_parts[1]).strip()))
    elif uri.endswith("circulate_linked"):
        if cmd_parts[1].strip() == 'true' or cmd_args[6].strip() == 'True':
            args.append(True)
        elif cmd_parts[1].strip() == 'false' or cmd_args[6].strip() == 'False':
            args.append(False)
            
    elif "pressure_control" in uri and uri.endswith("setpoint"):
        # set_ command for pressure
        args.append(float(str(cmd_parts[1]).strip()))
        args.append(1)
    
    elif uri.endswith("set_valve_open_percentage") or uri.endswith("set_target_position") or uri.endswith("pulse_width"):
        # set_ command for valves / rotators
        args.append(float(str(cmd_parts[1]).strip()))
    elif "magnetic_field_control" in uri and uri.endswith("set_field_target"):
        # set_ command for magnetic field setpoint
        # cmd_parts[1] should be a , delimited list
        cmd_args = (cmd_parts[1].strip()).split(',')
        try:
            assert len(cmd_args) == 7, "Incorrect arguments to set field"
        except AssertionError as e:
            raise ValueError(e) from e
        args.append(int(cmd_args[0].strip('[')))
        args.append(float(cmd_args[1]))
        args.append(float(cmd_args[2]))
        args.append(float(cmd_args[3]))
        args.append(int(cmd_args[4]))
        args.append(float(cmd_args[5]))
        if cmd_args[6].strip(']') == 'true' or cmd_args[6].strip(']') == ' True':
            args.append(True)
        elif cmd_args[6].strip(']') == 'false' or cmd_args[6].strip(']') == ' False':
            args.append(False)
    elif "magnetic_field_control" in uri and uri.endswith("set_output_current_target"):
        # set_ command for psu current setpoint
        # cmd_parts[1] should be a , delimited list
        cmd_args = (cmd_parts[1].strip()).split(',')
        try:
            assert len(cmd_args) == 6, "Incorrect arguments to set current"
        except AssertionError as e:
            raise ValueError(e) from e
        args.append(float(cmd_args[0].strip('[')))
        args.append(float(cmd_args[1]))
        args.append(float(cmd_args[2]))
        args.append(int(cmd_args[3]))
        args.append(float(cmd_args[4]))
        if cmd_args[5].strip(']') == 'true' or cmd_args[5].strip(']') == ' True':
            args.append(True)
        elif cmd_args[5].strip(']') == 'false' or cmd_args[5].strip(']') == ' False':
            args.append(False)
    elif "magnetic_field_control" in uri and uri.endswith("set_state"):
        args.append((int(str(cmd_parts[1]).strip())))
    elif "PUBLISH" in cmd:
        # A publication to the event log
        cmd_args = (cmd_parts[1].strip()).split(',')
        try:
            assert len(cmd_args) == 2, "Incorrect arguments for publication"
        except AssertionError as e:
            raise ValueError(e) from e
        ts = str(int(time.time()))
        args.append(int(10008))
        args.append(int(0))
        args.append(int(ts))
        args.append(int(0))
        args.append(int(0))
        args.append(int(10008))
        args.append(str((cmd_args[0]).strip('[')))
        args.append(str((cmd_args[1]).strip(']')))
    else:
        # currently no match for command
        raise NotImplementedError("Command / uri pattern incorrect, or not yet implemented")

    return uri, args

