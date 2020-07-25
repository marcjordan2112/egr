import argparse
import collections
import datetime
import filecmp
from pathlib import Path
import os
import time
import traceback
from utils import MyThread, ThreadSafePrint

from slpp import slpp as lua
try:
    from sqlite3 import dbapi2 as sqlite
except ImportError:
    from pysqlite2 import dbapi2 as sqlite

_POLL_TIME = 3.0

_TAB_STRING='    '
_ESO_ADDON_SAVE_FILE_PATH_DEFAULT = Path('C:/Users/marc/Documents/Elder Scrolls Online/live/SavedVariables/EsoGrinder.lua')
_previous_snapshot_save = ''
_monitor_poll_count = 0

_PREVIOUS_FILE_NAME_DEFAULT = 'temp_previous'

_DB_FILE_NAME_DEFAULT = 'eso_save_file_monitor.db'

_SAVED_VARIABLES_NAME_DEFAULT = 'EsoGrinderSavedVariables'

_ESO_AT_PLAYER_NAME_DEFAULT = 'Gullyable'

_ESO_ADDON_LOOT_VAR_NAME = 'loot_save'

################################################################################
class EsoSaveFileMonError(Exception):
    pass

################################################################################
def _arg_parse():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-a', '--eso_at_player_name',
        default=_ESO_AT_PLAYER_NAME_DEFAULT,
        dest='eso_at_player_name',
        help='ESO @PlayerName',
        required=False,
        type=str)

    parser.add_argument(
        '-f', '--eso_addon_save_file_path',
        default=_ESO_ADDON_SAVE_FILE_PATH_DEFAULT,
        dest='eso_addon_save_file_path',
        help='Path to save file for addon to be monitored',
        required=False,
        type=str)

    parser.add_argument(
        '-b', '--database_file',
        default=_DB_FILE_NAME_DEFAULT,
        dest='database_file',
        help='Database file',
        required=False,
        type=str)

    parser.add_argument(
        '-t', '--previous_file',
        default=_PREVIOUS_FILE_NAME_DEFAULT,
        dest='previous_file',
        help='File for saving previous addon save file.',
        required=False,
        type=str)

    parser.add_argument(
        '-d', '--debug',
        dest='debug',
        help='Enable debug.',
        action='store_true')

    args = parser.parse_args()

    return args

################################################################################
class Loot(object):
    _DB_ADD_LOOT = 'name, quantity, type, quality, status, value, mm, ttc, time, ' \
                   'player_name, x, y, location, zone, subzone, player_status'
    def __init__(self):
        self.name = ''
        self.quantity = ''
        self.typ = ''
        self.quality = ''
        self.status = ''
        self.value = ''
        self.mm = ''
        self.ttc = ''
        self.time = ''
        self.player_name = ''
        self.x = ''
        self.y = ''
        self.location = ''
        self.zone = ''
        self.subzone = ''
        self.player_status = ''

    def get_db_columns_string(self):
        return self._DB_ADD_LOOT

    def get_db_values_string(self):
        s = '"%s"' % self.name + ','
        s += '"%s"' % self.quantity + ','
        s += '"%s"' % self.typ + ','
        s += '"%s"' % self.quality + ','
        s += '"%s"' % self.status + ','
        s += '"%s"' % self.value + ','
        s += '"%s"' % self.mm + ','
        s += '"%s"' % self.ttc + ','
        s += '"%s"' % self.time + ','
        s += '"%s"' % self.player_name + ','
        s += '"%s"' % self.x + ','
        s += '"%s"' % self.y + ','
        s += '"%s"' % self.location + ','
        s += '"%s"' % self.zone + ','
        s += '"%s"' % self.subzone + ','
        s += '"%s"' % self.player_status
        return s

################################################################################
class MonitorThread(MyThread):
    _SAVED_VARIABLES_NAME_STRINGS = [
        _SAVED_VARIABLES_NAME_DEFAULT+' =',
        _SAVED_VARIABLES_NAME_DEFAULT+'=',
    ]

    def __init__(
            self,
            eso_at_player_name=_ESO_AT_PLAYER_NAME_DEFAULT,
            eso_addon_save_file_path=_ESO_ADDON_SAVE_FILE_PATH_DEFAULT,
            database_file=_DB_FILE_NAME_DEFAULT,
            previous_file=_PREVIOUS_FILE_NAME_DEFAULT,
            tsp=ThreadSafePrint(debug=False)):
        super(MonitorThread, self).__init__(tsp=tsp)
        self._eso_at_player_name = eso_at_player_name
        self._eso_addon_save_file_path = eso_addon_save_file_path
        self._database_file = database_file
        self._previous_file = previous_file
        self._tsp = tsp

        self._db_conn = None
        self._prefix = ''
        self._monitor_poll_count = 0
        self._savefile_change_count = 0

        if not os.path.isfile(self._previous_file):
            open(self._previous_file, 'w').close()

        if not os.path.isfile(self._database_file):
            conn = self._db_create(self._database_file)
            self._db_build_tables(conn)

        #self.convert_old_to_new()

    ############################################################################
    def convert_old_to_new(self):
        print('convert_old_to_new')
        old_conn = self._db_open('eso_grinder.db')
        old_curs = old_conn.cursor()

        new_conn = self._db_open('eso_grinder_new.db')
        self._db_build_tables2(new_conn)
        new_curs = new_conn.cursor()

        for i in range(2000):
            old_curs.execute("SELECT * FROM loot where id = %d"%i)
            old_row = old_curs.fetchone()
            if old_row is not None:
                print(old_row)
                data = old_row[1].replace('\\t', '\t').split('\t')
                loot = Loot()
                loot.name = data[0]
                loot.quantity = data[1]
                loot.typ = data[2]
                loot.quality = data[3]
                loot.status = data[4]
                loot.value = data[5]
                loot.mm = data[6]
                loot.ttc = data[7]
                loot.time = data[8]
                loot.player_name = data[9]
                loot.x = data[10]
                loot.y = data[11]
                loot.location = data[12]
                loot.zone = data[13]
                loot.subzone = data[14]
                loot.player_status = data[15]
                self._db_add_loot2(new_conn, loot)

        new_conn.commit()

    ############################################################################
    def _db_add_loot(self, db_conn, loot_string):
        db_curs = db_conn.cursor()

        loot = self._get_loot_obj_from_data_string(loot_string)
        s = 'INSERT INTO loot (%s) VALUES (%s)' % (loot.get_db_columns_string(), loot.get_db_values_string())

        e = None
        try:
            db_curs.execute(s)
        except sqlite.OperationalError as exc:
            e = exc
            traceback.print_exc()
            self._tsp.print_error('failed db insert: %s' % s)
        if e is not None:
            raise e

    ############################################################################
    def _db_build_tables(self, db_conn):
        db_curs = db_conn.cursor()
        db_curs.execute("CREATE TABLE IF NOT EXISTS loot (\
                        id INTEGER PRIMARY KEY,\
                        name TEXT,\
                        quantity TEXT,\
                        type TEXT,\
                        quality TEXT,\
                        status TEXT,\
                        value TEXT,\
                        mm TEXT,\
                        ttc TEXT,\
                        time TEXT,\
                        player_name TEXT,\
                        x TEXT,\
                        y TEXT,\
                        location TEXT,\
                        zone TEXT,\
                        subzone TEXT,\
                        player_status TEXT\
                        )")

    ############################################################################
    def _db_create(self, database_file):
        return sqlite.connect(database_file)

    ############################################################################
    def _db_fetchall(self, db_conn):
        db_curs = db_conn.cursor()
        db_curs.execute("SELECT * FROM loot")
        data = db_curs.fetchall()
        return data

    ############################################################################
    def _db_open(self, database_file):
        return sqlite.connect(database_file)

    ############################################################################
    def _get_loot_dict_from_lua_string(self, s):
        lua_table_dict = lua.decode(s)
        loot_dict = lua_table_dict['Default']['@%s' % self._eso_at_player_name]['$AccountWide'][_ESO_ADDON_LOOT_VAR_NAME]
        loot_tuple_list = sorted(loot_dict.items(), key=lambda kv: kv[0])
        loot_dict = collections.OrderedDict(loot_tuple_list)
        return loot_dict

    ############################################################################
    def _get_loot_obj_from_data_string(self, data_string):
        data = data_string.replace('\\t', '\t').split('\t')
        loot = Loot()
        #:todo: guard against malformed strings
        loot.name = data[0]
        loot.quantity = data[1]
        loot.typ = data[2]
        loot.quality = data[3]
        loot.status = data[4]
        loot.value = data[5]
        loot.mm = data[6]
        loot.ttc = data[7]
        loot.time = data[8]
        loot.player_name = data[9]
        loot.x = data[10]
        loot.y = data[11]
        loot.location = data[12]
        loot.zone = data[13]
        loot.subzone = data[14]
        loot.player_status = data[15]
        return loot

    ############################################################################
    def _process_delta(self):
        time_stamp = datetime.datetime.now()
        prefix = 'SSM '+str(time_stamp)+'> '
        self._tsp.print_debug('Processing file delta %d.' % self._savefile_change_count, prefix=prefix)

        f = open(self._eso_addon_save_file_path)
        new_file_string = f.read()
        f.close()
        ok = False
        temp_split = None
        for saved_variable_name in self._SAVED_VARIABLES_NAME_STRINGS:
            if saved_variable_name in new_file_string:
                temp_split = new_file_string.replace('\n', '').split(saved_variable_name)
                ok = True
                break
        if not ok:
            raise EsoSaveFileMonError('Invalid input file')
        new_lua_table_string = temp_split[1]
        new_loot_dict = self._get_loot_dict_from_lua_string(new_lua_table_string)

        f = open(self._previous_file, 'r')
        prev_file_string = f.read()
        f.close()
        db_conn = None
        if 0 == len(prev_file_string):
            count = 0
            for k, v in new_loot_dict.items():
                count += 1
                v = v.replace('"', '')
                self._tsp.print_debug('    %s' % v)
                if db_conn is None:
                    db_conn = self._db_open(self._database_file)
                self._db_add_loot(db_conn, v)
            if db_conn is not None:
                db_conn.commit()
                db_conn.close()
            self._tsp.print_debug('    %d new loot item(s) added to the database.' % count)
            f = open(self._previous_file, 'w')
            f.write(new_file_string)
            f.close()
            return

        ok = False
        for saved_variable_name in self._SAVED_VARIABLES_NAME_STRINGS:
            if saved_variable_name in prev_file_string:
                temp_string = prev_file_string.replace('\n', '')
                temp_split = temp_string.split(saved_variable_name)
                ok = True
                break
        if not ok:
            raise EsoSaveFileMonError('Invalid input file')
        prev_lua_table_string = temp_split[1]
        prev_loot_dict = self._get_loot_dict_from_lua_string(prev_lua_table_string)

        db_conn = None
        count = 0
        for k, v in new_loot_dict.items():
            if k in prev_loot_dict and v == prev_loot_dict[k]:
                pass
            else:
                count += 1
                v = v.replace('"', '')
                self._tsp.print_debug('    %s' % v)
                if db_conn is None:
                    db_conn = self._db_open(self._database_file)
                self._db_add_loot(db_conn, v)
        if db_conn is not None:
            db_conn.commit()
            db_conn.close()
        self._tsp.print_debug('    %d new loot items added to the database.' % count)

        f = open(self._previous_file, 'w')
        f.write(new_file_string)
        f.close()

    ############################################################################
    def thread_method(self):
        if filecmp.cmp(self._eso_addon_save_file_path, self._previous_file, shallow=False):
           pass
        else:
            self._savefile_change_count += 1
            self._process_delta()
        time.sleep(_POLL_TIME)
        self._monitor_poll_count += 1

################################################################################
def main():
    args = _arg_parse()

    tsp = ThreadSafePrint(debug=args.debug)

    tsp.print('ESO addon save file = %s' % args.eso_addon_save_file_path)
    tsp.print('Database file       = %s' % args.database_file)

    thread = MonitorThread(
        eso_addon_save_file_path=args.eso_addon_save_file_path,
        database_file=args.database_file,
        previous_file=args.previous_file,
        eso_at_player_name=args.eso_at_player_name,
        tsp=tsp)
    thread.start(timeout=5.0)

    while True:
        if thread.is_stopped():
            break

    tsp.print("Exit")
    print("Exit")

################################################################################
if __name__ == '__main__':
    main()
