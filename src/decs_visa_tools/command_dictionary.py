"""
Module that contains the 'command dictionaries" for various
oi:DECS system types
"""

#   A system dictionary that maps 'short' commands to the
#   WAMP uri that provides the functionality

#   Whilst the exact 'short' name is flexible, there is a convention that needs to be followed.
#   This is because the type/format of the uri args and/or the returned WAMP 'record types' may
#   depend on which uri is being called and so some method of grouping the commands to allow
#   parsing is required.

#   GET or SET - it is assumed that all commands either set something on the system, or request
#   information from it, therefore all commands must start with either:
#
#   get_    For a command that is requesting information, or
#   set_    For a command that is setting a value on the system
#
#   With one or two exceptions - the PUBLISH command writes to a topic rather than calling
#   an rRPC, so this is a special case.
#
#   And a version of a *IDN? command is implemented to allow and oi:DECS driver to be implemented
#   in a straightforward way in QCoDeS.

Proteox_cmd_uri:  dict[str, str]
Proteox_cmd_uri = {
    "get_SAMPLE_T"      : "oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_S.temperature",
    "set_SAMPLE_T"      : "oi.decs.temperature_control.DRI_MIX_CL.setpoint",
    "get_MC_T"          : "oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_S.temperature",
    "set_MC_T"          : "oi.decs.temperature_control.DRI_MIX_CL.setpoint",
    "get_MC_T_SP"       : "oi.decs.temperature_control.DRI_MIX_CL.setpoint",
    "get_MC_H"          : "oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power",
    "set_MC_H"          : "oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power",
    "set_MC_H_OFF"      : "oi.decs.temperature_control.DRI_MIX_CL.DRI_MIX_H.power",
    "get_STILL_T"       : "oi.decs.temperature_control.DRI_STL_S.temperature",
    "get_STILL_H"       : "oi.decs.temperature_control.DRI_STL_H.power",
    "set_STILL_H"       : "oi.decs.temperature_control.DRI_STL_H.power",
    'set_STILL_H_OFF'   : "oi.decs.temperature_control.DRI_STL_H.power",
    "get_CP_T"          : "oi.decs.temperature_control.DRI_CLD_S.temperature",
    "get_SRB_T"         : "oi.decs.temperature_control.SRB_GGS_CL.SRB_GGS_S.temperature",
    "get_DR2_T"         : "oi.decs.temperature_control.DRI_PT2_S.temperature",
    "get_PT2_T1"        : "oi.decs.temperature_control.PTR1_PT2_S.temperature",
    "get_DR1_T"         : "oi.decs.temperature_control.DRI_PT1_S.temperature",
    "get_PT1_T1"        : "oi.decs.temperature_control.PTR1_PT1_S.temperature",
    "get_3He_F"         : "oi.decs.flow_control.3CL_FM_01.flow",
    "get_OVC_P"         : "oi.decs.proteox.OVC_PG_01.pressure",
    "get_P1_P"          : "oi.decs.proteox.3CL_PG_01.pressure",
    "get_P2_P"          : "oi.decs.proteox.3CL_PG_02.pressure",
    "get_P3_P"          : "oi.decs.proteox.3CL_PG_03.pressure",
    "get_P4_P"          : "oi.decs.proteox.3CL_PG_04.pressure",
    "get_P5_P"          : "oi.decs.proteox.3CL_PG_05.pressure",
    "get_P6_P"          : "oi.decs.proteox.3CL_PG_06.pressure",
    "get_MAG_T"         : "oi.decs.magnetic_field_control.MAG_MSP_S.temperature",
    "get_MAG_VEC"       : "oi.decs.magnetic_field_control.VRM_01.magnetic_field_vector",
    "get_MAG_STATE"     : "oi.decs.magnetic_field_control.VRM_01.state",
    "get_SWZ_STATE"     : "oi.decs.magnetic_field_control.VRM_01.SWZ.state",
    "set_MAG_TARGET"    : "oi.decs.magnetic_field_control.VRM_01.set_field_target",
    "get_MAG_TARGET"    : "oi.decs.magnetic_field_control.VRM_01.field_target",
    "set_MAG_STATE"     : "oi.decs.magnetic_field_control.VRM_01.set_state",
    "set_MAG_X_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_X.set_state",
    "set_MAG_Y_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_Y.set_state",
    "set_MAG_Z_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_Z.set_state",
    "get_MAG_X_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_X.state",
    "get_MAG_Y_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_Y.state",
    "get_MAG_Z_STATE"   : "oi.decs.magnetic_field_control.VRM_01.MAG_Z.state",
    "get_MAG_CURR_VEC"  : "oi.decs.magnetic_field_control.VRM_01.current_vector",
    "set_CURR_TARGET"   : "oi.decs.magnetic_field_control.VRM_01.set_output_current_target",
    "get_CURR_TARGET"   : "oi.decs.magnetic_field_control.VRM_01.output_current_target",
    "PUBLISH"           : "oi.decs.proteox.eventlog",
    "get_a_WAMP_error"  : "oi.decs.THIS_WONT_WORK", # used for testing only
    "set_a_WAMP_error"  : "oi.decs.THIS_WONT_WORK"
}

Teslatron_cmd_uri:  dict[str, str]
Teslatron_cmd_uri = {
    # coming soon...
}

someOtherSystemType:  dict[str, str]
someOtherSystemType = {
    # Implement other/further cmd_dict(s) as required
    "short_cmd"         : "wamp.uri"
}
