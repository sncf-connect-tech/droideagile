from __future__ import print_function

import ConfigParser
import atexit
import subprocess
import sys
import tempfile
from os.path import expanduser, join, exists

import os
import pygame

home = expanduser("~")

# logging setup
import logging

root = logging.getLogger()
root.setLevel(logging.DEBUG)

# Rx logger
logging.getLogger("Rx").setLevel(logging.INFO)

# logging to stdout
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root.addHandler(console_handler)

# logging to file
log_file = join(home, "droideagile.log")
print("logging to file " + log_file)
file_handler = logging.FileHandler(log_file, mode="a", encoding="utf-8")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)
root.addHandler(file_handler)

# Parse configuration:

droidConfig = ConfigParser.SafeConfigParser()
droidConfigLoaded = False


# locate droideagile.ini.
def init_configuration():
    logger = logging.getLogger("config")
    config_file = None
    paths = [home, os.getcwd()]

    found = False
    index = 0
    while not found and index < len(paths):
        config_file = join(paths[index], "droideagile.ini")
        logger.info("Searching droideagile.ini in path " + config_file)
        if exists(config_file):
            found = True
        else:
            logger.info("not found !")
        index = index + 1
    if not found:
        logger.info("could not find configuration in any path ! exit now.")
        exit(-1)
    else:
        logger.info("loading configuration from file " + config_file)
        droidConfig.read(config_file)
        global droidConfigLoaded
        droidConfigLoaded = True


def path_to_tmp_file(file_name):
    return join(tempfile.gettempdir(), file_name)


# load_image
def load_image(image_name):
    return pygame.image.load(path_to_image(image_name))


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
    logger = logging.getLogger("config")
    import platform
    if platform.system() == 'Windows':
        import socket
        host_name = socket.gethostbyname(socket.gethostname())
    else:
        import commands
        host_name = commands.getoutput("hostname -I")
    logger.debug("resolved host name to " + host_name)
    return host_name.strip()


def call_script(script_path):
    subprocess.call("python " + path_to_script(script_path))


def call_script_as_process(script_path):
    logger = logging.getLogger("config")
    process = subprocess.Popen([sys.executable, path_to_script(script_path)])
    logger.info("Process was started with Pid " + str(process.pid) + " for script " + script_path)
    atexit.register(kill_process_at_exit, process)


def kill_process_at_exit(process):
    logger = logging.getLogger("config")
    logger.info("Stopping process with pid " + str(process.pid))
    process.kill()


def ensure_configuration_loaded():
    if not droidConfigLoaded:
        init_configuration()
