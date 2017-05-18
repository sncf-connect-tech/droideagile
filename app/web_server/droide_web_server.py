import atexit
import subprocess
import sys

from flask import Flask
from flask import render_template, redirect, url_for, g
from flask import request

from app.droid_configuration import path_to_script
from app.droid_database import get_raw_db_connection, SprintConfig

web_server = Flask(__name__)


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = get_raw_db_connection()
    return db


config = None


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
    web_server.run(host='0.0.0.0')

WebServerProcess = None


def start_web_server():
    global WebServerProcess
    WebServerProcess = subprocess.Popen([sys.executable, path_to_script("web_server\droide_web_server.py")])
    print("WebServer was started with Pid " + str(WebServerProcess.pid))
    atexit.register(stop_web_server)


def stop_web_server():
    print("Stopping webserver with pid " + str(WebServerProcess.pid))
    WebServerProcess.kill()
