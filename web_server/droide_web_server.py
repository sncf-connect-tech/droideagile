import os.path
import json

from droid_database import *

from flask import Flask
from flask import request
from flask import render_template, redirect, url_for, g

app = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class ConfigData:
    def __init__(self):
        self.sprint_number = 1


def get_config_file():
    return os.path.join(get_droide_dir(), 'config.json')


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


@app.route("/")
def hello():
    return redirect(url_for('config_route'))


@app.route("/config", methods=['POST', 'GET'])
def config_route():
    print (request.method)
    if request.method == 'POST':
        print ("test" + str(request.form["sprint_number"]))
        config.apply(request)
        config.save()
        # redirect
        return redirect(url_for('config_route'))
    else:
        config.load()
        return render_template("config.html", config=config.config_data)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
