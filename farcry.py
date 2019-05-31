#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Far Cry: Data science introduction.

Introduction
------------
Far Cry is a first-person shooter (FPS) video game with amazing graphics,
developed by Crytek and published by Ubisoft. The game was released in 2004 for
Microsoft Windows and was a huge commercial success. Ubisoft closed the online
servers almost 12 years later.

Far Cry features several multiplayer modes in which players basically score
points by killing other players. One of these multiplayer modes is deathmatch,
also known as free for all (FFA), where the goal is to kill (or frag, from the
military term) as many other players as possible within a limited period of
time. Basically, everything that moves SHOULD be killed…

Multiplayer FFA Session
-----------------------
Players can join an online multiplayer session by connecting to a Far Cry
server. A session starts for a configurable limited period of time,
for example: 30 minutes, during which each player tries their best to seek out
and kill other players.

Weapons
-------
Players have access to a large arsenal of real-world weapons in Far Cry, from
grenades and pistols, to rocket launchers, machines guns and sniper rifles.
Check out all of the weapons from good old Far Cry! They sound so cool!
"""

import datetime


class Cvars:
    cvars = {}
    bytes_list = []


def __get_cvar(log_data):
    """Get console variable.

    This function gets cvar from the log file and stores in a dictionary.

    Parameters
    ----------
    log_data : bytes
        bytes object from content in log file.

    Returns
    -------
    Dictionary
        a dictionary of cvar and its value.
    List
        a list of lines of log data.
    """
    cvars = {}
    str_data = log_data.split(b'\n')
    Cvars.bytes_list = str_data
    cvar_lines = [line for line in str_data if b'cvar' in line]
    for cvar in cvar_lines:
        cvars[cvar[(cvar.find(b'(') + 1):(cvar.find(b','))]] =\
            cvar[cvar.find(b','):len(cvar) - 2]
    Cvars.cvars.update(cvars)
    print(Cvars.cvars)
    return cvars, str_data


def read_log_file(log_file_pathname):
    """Read the Far Cry log file.

    This function takes an argument log_file_pathname, representing
    the pathname of a Far Cry server log file, and reads and returns
    all the bytes from the file.

    Parameter
    ---------
    log_file_pathname : str
        pathname of a Far Cry server log file.

    Returns
    -------
    bytes
        all the bytes from the Far Cry server log file.
    """
    try:
        log_file_pathname = str(log_file_pathname)
        in_file = open(log_file_pathname, "rb")
        data = in_file.read()
        __get_cvar(data)
        return data
    except (ValueError, OSError):
        return bytes(0)


def parse_log_start_time(log_data):
    """Parse date and time information.

    This function takes an argument log_data, representing the data read from a
    Far Cry server's log file, and returns a datetime.datetime object
    representing the time the Far Cry engine began to log events.

    Parameters
    ----------
    log_data : bytes
        all the bytes from the Far Cry server log file.

    Returns
    -------
    object
        datetime.datetime object representing the time the Far Cry engine began
        to log events.
    """
    if not isinstance(log_data, bytes):
        return print("Type error, it must be bytes!")
    date_time_str = log_data.split(b'\n')[0].decode('utf-8').\
                        replace("Log Started at ", "")
    pivot = date_time_str.find(",")
    weekday = date_time_str[:3]
    date_time_str = date_time_str.replace(date_time_str[:pivot], weekday)
    try:
        date_time_obj = datetime.datetime.\
                            strptime(date_time_str, "%a, %B %d, %Y %H:%M:%S\r")
    except ValueError:
        return print("Can't convert to datetime.")
    return date_time_obj
