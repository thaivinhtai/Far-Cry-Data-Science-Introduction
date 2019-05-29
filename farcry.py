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
        return data
    except ValueError, FileNotFoundError, PermissionError:
        return bytes(0)
