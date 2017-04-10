import os.path
import json

from flask import Flask
from flask import request
from flask import render_template, redirect, url_for

app = Flask(__name__)


def get_droide_dir():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if dir_path.endswith("droideagile"):
        return dir_path;
    else:
        return os.path.join(dir_path, '..')


class ConfigData:
    def __init__(self):
        self.sprint_number = 1


def get_config_file():
    return os.path.join(get_droide_dir(), 'config.json')


class Config:
    def __init__(self):
        self.config_data = ConfigData()
        if os.path.isfile(get_config_file()):
            self.load()
        else:
            self.save()

    def load(self):
        with open(get_config_file()) as config_data:
            self.config_data.__dict__ = json.load(config_data)
            print(self.config_data.sprint_number)

    def save(self):
        with open(get_config_file(), 'wb') as outfile:
            str_ = json.dumps(self.config_data.__dict__,
                              indent=4, sort_keys=True,
                              separators=(',', ': '), ensure_ascii=False)
            print ("writing " + str_)
            outfile.write(str_)

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
    app.run()
