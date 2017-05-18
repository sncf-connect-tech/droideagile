import sqlite3
from os.path import isfile

from app.droid_configuration import path_to_resource, path_to_database


def init_db():
    if not isfile(path_to_database()):
        db = sqlite3.connect(path_to_database())
        with open(path_to_resource("schema.sql")) as f:
            db.cursor().executescript(f.read())
        db.commit()
        db.close()
        print("database created at " + path_to_database())
    else:
        print("will connect to database at " + path_to_database())


def get_db_connection():
    cnx = sqlite3.connect(path_to_database())
    cnx.row_factory = sqlite3.Row
    return cnx


def get_raw_db_connection():
    return sqlite3.connect(path_to_database())


def update(sql, params=None):
    if params is None:
        params = []
    cnx = get_db_connection()
    cnx.cursor().execute(sql, params)
    cnx.commit()
    cnx.close()


def select_for_one(sql, params=None):
    if params is None:
        params = []
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute(sql, params)
    result = cursor.fetchone()
    cnx.close()
    return result


class SprintConfigData:
    def __init__(self):
        self.sprint_number = 1


class SprintConfig:
    def __init__(self):
        self.config_data = SprintConfigData()
        self.load()

    def load(self):
        one = select_for_one("SELECT * FROM configuration")
        print (one)
        self.config_data.sprint_number = one['sprint_number']

    def save(self):
        update("UPDATE configuration SET sprint_number = ?", [self.config_data.sprint_number])

    def sprint_number(self):
        return self.config_data.sprint_number

    def apply(self, request):
        self.config_data.sprint_number = request.form["sprint_number"]
