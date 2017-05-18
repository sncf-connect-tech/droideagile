import importlib

from app.droid_configuration import droidConfig, ensure_configuration_loaded


def should_use_mock():
    ensure_configuration_loaded()
    return droidConfig.getboolean("BrickPi", "UseMock")
