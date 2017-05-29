import importlib

import logging

from app.droid_configuration import droidConfig, ensure_configuration_loaded


def should_use_mock():
    ensure_configuration_loaded()
    return droidConfig.getboolean("BrickPi", "UseMock")


# facade for all brickpi operation
class BrickPiFacade:
    def __init__(self):
        # setup brick pi
        if should_use_mock() :
            from app.droid_brick_pi.BrickPiMock import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, BrickPiSetupSensors, BrickPiUpdateValues
        else:
            from app.droid_brick_pi.BrickPi import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, BrickPiSetupSensors, BrickPiUpdateValues

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info("Set up brick pi")
        BrickPiSetup()
        self.brick_pi_struct = BrickPi
        self.log.info("Set up brick pi...ok")

        self.log.info("Color sensor should be connected to sensor port 4")
        self.color_sensor_port = PORT_4
        self.brick_pi_struct.SensorType[self.color_sensor_port] = TYPE_SENSOR_EV3_COLOR_M2  # Set the type of sensor at PORT_4.  M2 is Color.

        result = BrickPiSetupSensors()  # Send the properties of sensors to BrickPi.  Set up the BrickPi.
        self.log.info("sensors setup result = " + str(result))
        if result != 0:
            raise Exception("oups.... issue with sensors setup !")

        self.update_value_function = BrickPiUpdateValues

        self.values_are_up_to_date = False

    def update_values(self):
        result = self.update_value_function() # Ask BrickPi to update values for sensors/motors
        if not result:
            self.values_are_up_to_date = True
        else:
            self.values_are_up_to_date = False
        return self.values_are_up_to_date

    def read_color_sensor(self):
        return self.brick_pi_struct.Sensor[self.color_sensor_port]


BRICK_PI = BrickPiFacade()