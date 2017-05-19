# fix pour que le script trouve les modules app.*
import sys

import os
from flask import Flask
from flask import render_template, redirect, url_for, g
from flask import request

sys.path.insert(0, os.getcwd())

from app.droid_configuration import init_configuration, current_host_name, call_script_as_process
from app.droid_database import get_raw_db_connection, SprintConfig

web_server = Flask(__name__, static_url_path='/static')

config = None


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = get_raw_db_connection()
    return db


@web_server.before_first_request
def load_config():
    global config
    config = SprintConfig()


@web_server.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@web_server.route("/")
def hello():
    return redirect(url_for('config_route'))


@web_server.route("/remote_control")
def remote_control_route():
    return render_template("remote_control.html", web_socket_server=current_host_name() + ":9093")


@web_server.route("/config", methods=['POST', 'GET'])
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
    init_configuration()
    web_server.run(host='0.0.0.0')

WebServerProcess = None


def start_web_server():
    call_script_as_process("web_server/droide_web_server.py")
