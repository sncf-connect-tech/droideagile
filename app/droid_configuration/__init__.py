# Parse configuration:
from __future__ import print_function

import ConfigParser
import atexit
import subprocess
import sys
from os.path import expanduser, join, exists

import os

home = expanduser("~")

droidConfig = ConfigParser.ConfigParser()
droidConfigLoaded = False


# locate droideagile.ini.
def init_configuration():
    config_file = None
    paths = [home, os.getcwd()]

    found = False
    index = 0
    while not found and index < len(paths):
        config_file = join(paths[index], "droideagile.ini")
        print("Searching droideagile.ini in path " + config_file)
        if exists(config_file):
            found = True
        else:
            print("not found !")
        index = index + 1
    if not found:
        print("could not find configuration in any path ! exit now.")
        exit(-1)
    else:
        print("loading configuration from file " + config_file)
        droidConfig.read(config_file)
        global droidConfigLoaded
        droidConfigLoaded = True


# load_image
def path_to_image(image_name):
    asset_path = droidConfig.get("Storage", "AssetsPath")
    return join(asset_path, 'images', image_name)


def path_to_sound(sound_name):
    asset_path = droidConfig.get("Storage", "AssetsPath")
    return join(asset_path, 'sounds', sound_name)


def path_to_resource(resource_name):
    asset_path = droidConfig.get("Storage", "AssetsPath")
    return join(asset_path, 'resources', resource_name)


def path_to_database():
    return join(droidConfig.get("Storage", "DataBasePath"), "droideagile.db")


def path_to_script(script_path):
    path = join(".", "app", script_path)
    print(path)
    return path


def current_host_name():
    import platform
    if platform.system() == 'Windows':
        import socket
        host_name = socket.gethostbyname(socket.gethostname())
    else:
        import commands
        host_name = commands.getoutput("hostname -I")
    print("resolved host name to " + host_name)
    return host_name


def call_script(script_path):
    subprocess.call("python " + path_to_script(script_path))


def call_script_as_process(script_path):
    process = subprocess.Popen([sys.executable, path_to_script(script_path)])
    print("Process was started with Pid " + str(process.pid) + " for script " + script_path)
    atexit.register(kill_process_at_exit, process)


def kill_process_at_exit(process):
    print("Stopping process with pid " + str(process.pid))
    process.kill()


def ensure_configuration_loaded():
    if not droidConfigLoaded:
        init_configuration()
