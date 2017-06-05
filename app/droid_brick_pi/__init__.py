from __future__ import print_function

import logging

from rx import Observable

from app.droid_configuration import droidConfig, ensure_configuration_loaded


def should_use_mock():
    ensure_configuration_loaded()
    return droidConfig.getboolean("BrickPi", "UseMock")


class DroidSensors():
    def __init__(self, color):
        self.color = color


# facade for all brickpi operation
class BrickPiFacade:
    def __init__(self):
        # setup brick pi
        if should_use_mock():
            from app.droid_brick_pi.BrickPiMock import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, \
                BrickPiSetupSensors, BrickPiUpdateValues, stop
            self.stop_function = stop
        else:
            from app.droid_brick_pi.BrickPi import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, \
                BrickPiSetupSensors, BrickPiUpdateValues
            self.stop_function = None

        self.log = logging.getLogger(self.__class__.__name__)
        self.log.info("Set up brick pi")
        BrickPiSetup()
        self.brick_pi_struct = BrickPi
        self.log.info("Set up brick pi...ok")

        self.log.info("Color sensor should be connected to sensor port 4")
        self.color_sensor_port = PORT_4
        self.brick_pi_struct.SensorType[
            self.color_sensor_port] = TYPE_SENSOR_EV3_COLOR_M2  # Set the type of sensor at PORT_4.  M2 is Color.

        result = BrickPiSetupSensors()  # Send the properties of sensors to BrickPi.  Set up the BrickPi.
        self.log.info("sensors setup result = " + str(result))
        if result != 0:
            raise Exception("oups.... issue with sensors setup !")

        self.update_value_function = BrickPiUpdateValues
        # The color sensor will go to sleep and not return proper values if it is left for longer than 100 ms: 0.01
        self.droid_sensors = Observable.interval(100).map(lambda i: self.__read_current())

        def update_sample_with_color(sample, current_color):
            sample[current_color] += 1
            return sample

        self.buffered_color_sensor_observable = self.droid_sensors \
            .buffer_with_time(timespan=1000) \
            .flat_map(lambda b: Observable.from_(b)
                      .map(lambda d: d.color)
                      .filter(lambda c: c < 7)
                      .reduce(update_sample_with_color, [0] * 7)
                      .map(lambda sample: sample.index(max(sample)))
                      )

    def __read_current(self):
        # You must be sure to poll the color sensor every 100 ms!
        if self.__update_values():
            # ok values are up to date
            color = self.__read_color_sensor()
            return DroidSensors(color)
        return None

    def __update_values(self):
        return not self.update_value_function()  # Ask BrickPi to update values for sensors/motors

    def __read_color_sensor(self):
        return self.brick_pi_struct.Sensor[self.color_sensor_port]

    def done(self):
        if self.stop_function is not None:
            self.stop_function()


BRICK_PI = BrickPiFacade()
