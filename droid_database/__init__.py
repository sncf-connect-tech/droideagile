import os
import sqlite3


def get_droide_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir_path.endswith("droideagile"):
        return dir_path;
    else:
        return os.path.join(dir_path, '..')


def get_resource(resource_name):
    return os.path.join(get_droide_dir(), resource_name)


def init_db():
    db = sqlite3.connect(DATABASE)
    with open(get_resource("droid_database/schema.sql")) as f:
        db.cursor().executescript(f.read())
    db.commit()


DATABASE = get_resource('droideagile.db')


class ConfigData:
    def __init__(self):
        self.sprint_number = 1

class Config:
    def __init__(self):
        self.config_data = ConfigData()
        if os.path.isfile(DATABASE):
            self.load()
        else:
            init_db()
            self.save()

    def load(self):
        cnx = sqlite3.connect(DATABASE)
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM configuration")
        one = cursor.fetchone()
        print (one)
        self.config_data.sprint_number = one['sprint_number']

    def save(self):
        cnx = sqlite3.connect(DATABASE)
        cnx.row_factory = sqlite3.Row
        cursor = cnx.cursor()
        cursor.execute("UPDATE configuration SET sprint_number = ?", [self.config_data.sprint_number])
        cnx.commit()

    def sprint_number(self):
        return self.config_data.sprint_number

    def apply(self, request):
        self.config_data.sprint_number = request.form["sprint_number"]


config = Config()
