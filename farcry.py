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

import csv
from datetime import datetime, timezone, timedelta
from json import dumps
from sqlite3 import connect, DatabaseError, Connection


__VEHICLE__ = ["Vehicle"]

__GUN__ = [
    "Falcon",
    "Shotgun",
    "P90",
    "MP5",
    "M4",
    "AG36",
    "OICW",
    "SniperRifle",
    "M249",
    "MG",
    "VehicleMountedAutoMG",
    "VehicleMountedMG"
]

__GRENADE__ = [
    "HandGrenade",
    "AG36Grenade",
    "OICWGrenade",
    "StickyExplosive"
]

__ROCKET__ = [
    "Rocket",
    "VehicleMountedRocketMG",
    "VehicleRocket"
]

__MACHETE__ = ["Machete"]

__BOAT__ = ["Boat"]


class Cvars:
    """store cvar."""
    cvars = {}


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
    cvar_lines = [line for line in str_data if b'cvar' in line]
    for cvar in cvar_lines:
        cvars[cvar[(cvar.find(b'(') + 1):(cvar.find(b','))]] =\
            cvar[cvar.find(b',') + 1:len(cvar) - 2]
    Cvars.cvars.update(cvars)
    return cvars


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
    except (ValueError, OSError, NameError):
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
    utc_time = Cvars.cvars[b'g_timezone'].decode('utf-8')
    try:
        date_time_obj = datetime.strptime(date_time_str,
                                          "%a, %B %d, %Y %H:%M:%S\r")
        date_time_obj_utc = date_time_obj.\
            replace(tzinfo=timezone(timedelta(hours=int(utc_time))))
    except (NameError, ValueError, OSError):
        return print("Can't convert to datetime.")
    return date_time_obj_utc


def parse_match_mode_and_map(log_data):
    """Parse Match Session's Mode and Map.

    Far Cry features several multiplayer modes:

        - ASSAULT: There are two teams, one is defending a flag and the other
          team is attacking it. Each maps has 3 flags and if after 20 minutes
          not all flags are captured the teams switch sides. The flags are on
          fixed positions in the map and only one flag at a time is active;

        - TDM (Team DeathMatch): There are two teams. Players of one team kill
          members of the other team;

        - FFA (Free-For-All): Players kill anyone they can find.

    There are also several maps available such as mp_surf, mp_radio and
    mp_jungle to name a few.

    This function takes an argument log_data, representing the data read from a
    Far Cry server's log file, and returns a tuple (mode, map) where:

        - mode: indicates the multiplayer mode that was played, either ASSAULT,
          TDM, or FFA;

        - map: the name of the map that was used, for instance mp_surf.

    Parameters
    ----------
    log_data : bytes
        all the bytes from the Far Cry server log file.

    Returns
    -------
    tuple
        (mode, map)
    """
    if not isinstance(log_data, bytes):
        return print("Type error, it must be bytes!")
    level_line = ""
    list_bytes_by_line = log_data.split(b'\n')
    for line in list_bytes_by_line:
        if b'Loading level' in line:
            level_line = line.decode('utf-8')
            break
    loading_position = level_line.find("Loading level")
    level_line = level_line.replace(level_line[:loading_position], "")
    while "-" in level_line:
        level_line = level_line.replace("-", "")
    try:
        slash_position = level_line.find("/")
        commas_position = level_line.find(",")
        mission_position = level_line.find("mission")
        _map = level_line[slash_position + 1:commas_position]
        _mode = level_line[mission_position + 8: len(level_line) - 2]
        return (_mode, _map)
    except (IndexError, NameError, OSError):
        print("Can not parse Match Session's Mode and Map.")


def parse_frags(log_data):
    """Parse Frag History.

    This function takes an argument log_data, representing the data read from
    a Far Cry server's log file, and returns a list of frags.

    Parameters
    ----------
    log_data : bytes
        all the bytes from the Far Cry server log file.

    Returns
    -------
    list
        list of tuple of (frag_time, killer_name, victim_name, weapon_code)
    """
    if not isinstance(log_data, bytes):
        return print("Type error, it must be bytes!")
    list_bytes_by_line = log_data.split(b'\n')
    list_frag_history = [line.decode('utf-8') for line in list_bytes_by_line
                         if b'<Lua>' in line and b'killed' in line]
    frag_history = []
    human_readable = []
    timestamp = parse_log_start_time(log_data)
    try:
        for line in list_frag_history:
            frag_time = timestamp

            time_start_position = line.find("<")
            time_end_position = line.find(">")
            lua_postion = line.find("<Lua>")
            killed_position = line.find("killed")
            with_position = line.find("with")

            frag_time_string = line[time_start_position + 1:time_end_position]
            minute_and_second = frag_time_string.split(":")
            current_minute = int(minute_and_second[0])
            current_second = int(minute_and_second[1])

            if current_minute == 0 and frag_time.minute != 0:
                frag_time = frag_time.replace(hour=frag_time.hour + 1)
            frag_time = frag_time.replace(minute=current_minute,
                                          second=current_second)
            killer_name = line[lua_postion + 6:killed_position - 1]
            if "itself" in line:
                frag_history.append((frag_time, killer_name))
                human_readable.append((frag_time.isoformat(), killer_name))
                continue
            victim_name = line[killed_position + 7:with_position - 1]
            weapon_code = line[with_position + 5:len(line) - 1]
            frag_history.append((frag_time, killer_name,
                                 victim_name, weapon_code))
            human_readable.append((frag_time.isoformat(), killer_name,
                                   victim_name, weapon_code))
        print(*human_readable, sep="\n")
        return frag_history
    except (IndexError, NameError, OSError):
        print("Can not parse frag history.")


def prettify_frags(frags):
    """Prettify Frag History.

    Emojis are pictographs (pictorial symbols) that are typically presented in
    a colorful form and used inline with text. They represent things such as
    faces, weather, vehicles and buildings, food and drink, animals and plants,
    or icons that represent emotions, feelings, or activities.

    This function  takes one argument frags, an array of tuples of frags parsed
    from a Far Cry server's log file, and that returns a list of strings,
    each with the following format:

        [frag_time] 😛 killer_name weapon_icon 😦 victim_name

    or, the simpler form, if the player committed suicide:

        [frag_time] 😦 victim_name ☠

    Parameters
    ----------
    frags : list
        list of tuple of (frag_time, killer_name, victim_name, weapon_code)

    Returns
    -------
    list
        a list of strings
    """
    if not isinstance(log_data, list):
        return print("Type error, it must be list!")
    list_formated_strings = []
    try:
        for element in frags:
            line = ""
            if len(element) == 2:
                line += ("[" + str(element[0].isoformat()) + "]" +
                         " 😦 " + element[1] + " ☠")
                list_formated_strings.append(line)
                continue
            a = ""
            if element[3] in __VEHICLE__:
                a = "🚙"
            if element[3] in __GUN__:
                a = "🔫"
            if element[3] in __GRENADE__:
                a = "💣"
            if element[3] in __ROCKET__:
                a = "🚀"
            if element[3] in __MACHETE__:
                a = "🔪"
            if element[3] in __BOAT__:
                a = "🚤"
            line += ("[" + str(element[0].isoformat()) + "]" + " 😛 " +
                     element[1] + " " + a + " 😦 " + element[3])
            list_formated_strings.append(line)
        return list_formated_strings
    except (IndexError, NameError, OSError, TypeError):
        print("can not prettify frag history.")


def parse_match_start_and_end_times(log_data, *arg):
    """Determine Game Session's Start and End Times.

    This function takes an argument log_data representing the data read from
    a Far Cry server's log file  and returns the approximate start and end time
    of the game session.

    Parameters
    ----------
    log_data : bytes
        all the bytes from the Far Cry server log file.

    returns
    -------
    object
        datetime.datetime object representing the time start and end time
        of the game session.
    """
    if not isinstance(log_data, bytes):
        return print("Type error, it must be list!")
    list_bytes_by_line = log_data.split(b'\n')
    line_contain_start_game = ""
    line_contain_end_game = ""
    for line in list_bytes_by_line:
        if b'Precaching level' in line:
            line_contain_start_game = line.decode("utf-8")
        if b'Statistics' in line:
            line_contain_end_game = line.decode("utf-8")
            break
    if line_contain_end_game == "":
        return None, None
    timestamp = parse_log_start_time(log_data)
    start_minute =\
        int(line_contain_start_game
            [line_contain_start_game.find("Precaching level") + 22:
             line_contain_start_game.find("done") - 5])
    start_second =\
        int(line_contain_start_game
            [line_contain_start_game.find("Precaching level") + 25:
             line_contain_start_game.find("done") - 2])
    end_minute = int(line_contain_end_game[1:3])
    end_second = int(line_contain_end_game[4:6])
    start_time = timestamp.replace(minute=start_minute, second=start_second)
    end_time = timestamp.replace(minute=end_minute, second=end_second)
    return start_time, end_time


def write_frag_csv_file(log_file_pathname, frags):
    """Create Frag History CSV File.

    This function takes an argument log_file_pathname representing the pathname
    of the CSV file to store the frags in, and an argument frags, an array of
    tuples of the frags.

    Each frag is represented by a comma-separated value (CSV) string.

    Parameters
    ----------
    log_file_pathname : str
        the path name of the CSV file to store the frags in.
    frags : list
        list of tuple of (frag_time, killer_name, victim_name, weapon_code)

    Returns
    -------
    NONE
        The file log_file_pathname will be create or overwrite if it's existed
    """
    try:
        with open(log_file_pathname, mode='w') as frag_file:
            frag_file = csv.writer(frag_file, delimiter=',',
                                   quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for element in frags:
                row_content = []
                if len(element) == 4:
                    row_content = [str(element[0]), element[1],
                                   element[2], element[3]]
                if len(element) == 2:
                    row_content = [str(element[0]), element[1]]
                frag_file.writerow(row_content)
    except (IndexError, NameError, TypeError, PermissionError, OSError):
        print("Cant not create frag history CSV file.")


def insert_match_to_sqlite(file_pathname, start_time, end_time,
                           game_mode, map_name, frags):
    """Insert Game Session Data into SQLite.

    This function inserts a new record into the table match with the arguments
    start_time, end_time, game_mode, and map_name, using an INSERT statement.
    You need to use the Python module sqlite3.

    Parameters
    ----------
    file_pathname : str
        The path and name of the Far Cry's SQLite database.
    start_time : datetime.datetime
        time zone information corresponding to the start of the game session.
    end_time : datetime.datetime
        time zone information corresponding to the end of the game session.
    game_mode : str
        Multiplayer mode of the game session.
    map_name : str
        Name of the map that was played.
    frags : list
        A list of tuples of the following form:
            (frag_time, killer_name[, victim_name, weapon_code])

    Returns
    -------
    the identifier of the match that has been inserted. This information is
    retrieved from the SQLite database using the method lastrowid.
    """
    command = """INSERT INTO match (start_time, end_time, game_mode,
                 map_name) VALUES (?,?,?,?)"""
    try:
        with connect(file_pathname) as conn:
            cursor = conn.cursor()
            cursor.execute(command, (start_time, end_time,
                                     game_mode, map_name))
            insert_frags_to_sqlite(conn, cursor.lastrowid, frags)
            return cursor.lastrowid
    except DatabaseError:
        print("Can not insert to database.")


def insert_frags_to_sqlite(connection, match_id, frags):
    """Insert Match Frags into SQLite.

    This function  inserts new records into the table match_frag.

    Parameters
    ----------
    connection : sqlite3 Connection object
    match_id : int
        the identifier of a match
    frags : list
        a list of frags, as passed to the function insert_match_to_sqlite,
        that occurred during this match.

    Returns
    -------
    inserts new records into the table match_frag.
    """
    command1 = """INSERT INTO match_frag (match_id, frag_time,
                  killer_name, victim_name, weapon_code) VALUES (?,?,?,?,?)"""
    command2 = """INSERT INTO match_frag (match_id, frag_time, killer_name)
                  VALUES (?,?,?)"""
    cursor = connection.cursor()
    for frag in frags:
        if len(frag) > 2:
            cursor.execute(command1, (match_id, *frag))
            continue
        cursor.execute(command2, (match_id, *frag))
