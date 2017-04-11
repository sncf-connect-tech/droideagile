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
