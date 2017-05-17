# Parse configuration:
from __future__ import print_function
import ConfigParser

from os.path import expanduser, join, exists
import os

home = expanduser("~")

droidConfig = None


def config():
    global droidConfig
    if droidConfig is None:
        droidConfig = ConfigParser.ConfigParser()
        try_to_find_config_or_die()
    return droidConfig


# locate droideagile.ini.
def try_to_find_config_or_die():
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
