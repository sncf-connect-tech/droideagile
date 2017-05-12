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
