from __future__ import print_function

import logging
import threading
import time
from threading import Thread

import sys
from rx import Observable
from rx.subjects import Subject

from app.droid_configuration import droidConfig, ensure_configuration_loaded


def should_use_mock():
    ensure_configuration_loaded()
    return droidConfig.getboolean("BrickPi", "UseMock")


class DroidSensors():
    def __init__(self, color):
        self.color = color


class BrickPiFacadeThread(Thread):
    def __init__(self):
        super(BrickPiFacadeThread, self).__init__()
        self.log = logging.getLogger(str(self))

        self.ready = Subject()
        self.sensors = Subject()
        self._should_run = True
        self.done_event = threading.Event()

        # setup brick pi
        if should_use_mock():
            from app.droid_brick_pi.BrickPiMock import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, PORT_A, \
                PORT_B, PORT_C, BrickPiSetupSensors, BrickPiUpdateValues, stop
            self.stop_function = stop
        else:
            from app.droid_brick_pi.BrickPi import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, PORT_A, \
                PORT_B, PORT_C, BrickPiSetupSensors, BrickPiUpdateValues
            self.stop_function = lambda: print('done')

        self.bp_struct = BrickPi
        self.bp_setup = BrickPiSetup
        self.bp_setup_sensors = BrickPiSetupSensors
        self.bp_update_values = BrickPiUpdateValues

        self.bp_COLOR_SENSOR_PORT = PORT_4
        self.bp_HEAD_MOTOR_PORT = PORT_C
        self.bp_LEFT_MOTOR_PORT = PORT_A
        self.bp_RIGHT_MOTOR_PORT = PORT_B

        self.bp_TYPE_SENSOR_EV3_COLOR_M2 = TYPE_SENSOR_EV3_COLOR_M2

        self.update_value_function = BrickPiUpdateValues

        def update_sample_with_color(sample, current_color):
            sample[current_color] += 1
            return sample

        self.buffered_color_sensor_observable = self.sensors \
            .buffer_with_time(timespan=1500) \
            .filter(lambda buffer: len(buffer) > 0) \
            .flat_map(lambda b: Observable.from_(b)
                      .map(lambda d: d.color)
                      .filter(lambda c: c < 7)
                      .reduce(update_sample_with_color, [0] * 7)
                      .map(lambda sample: sample.index(max(sample)))
                      )

    def run(self):
        self.log.debug("running")

        self.setup()

        while self._should_run:
            # self.log.debug("reading")
            time.sleep(0.09)
            # You must be sure to poll the color sensor every 100 ms!
            if self.update_value_function() == 0:
                # ok values are up to date
                color = self.bp_struct.Sensor[self.bp_COLOR_SENSOR_PORT]
                self.sensors.on_next(DroidSensors(color))

        self.log.debug("stopping...")
        self.sensors.on_completed()
        self.sensors.dispose()
        self.stop_function()
        self.done_event.set()
        self.log.debug("stopped...ok")

    def stop(self):
        self.log.debug("waiting for stop...")
        self._should_run = False
        result = self.done_event.wait(2)
        if not result:
            self.log.error("timeout waiting for app to stop")
            sys.exit(-1)
        self.log.debug("waiting for stop...ok")

    def setup(self):
        self.log.info("Set up brick pi")
        result = self.bp_setup()
        if result != 0:
            self.ready.on_error(Exception("oups.... issue with sensors setup !"))
            self._should_run = False
            return

        self.log.info("Set up brick pi...ok")
        self.ready.on_next("set up brick ok")

        self.log.info("Color sensor should be connected to sensor port 4")
        self.bp_struct.SensorType[
            self.bp_COLOR_SENSOR_PORT] = self.bp_TYPE_SENSOR_EV3_COLOR_M2  # Set the type of sensor at PORT_4.  M2 is Color.

        self.ready.on_next("set up sensors")
        result = self.bp_setup_sensors()  # Send the properties of sensors to BrickPi.  Set up the BrickPi.
        self.log.info("sensors setup result = " + str(result))
        if result != 0:
            self.ready.on_error(Exception("oups.... issue with sensors setup !"))
            self._should_run = False
            return

        self.ready.on_next("set up sensors done.")

        self.log.info("set up motors")
        self.ready.on_next("set up motors")

        self.bp_struct.MotorEnable[self.bp_LEFT_MOTOR_PORT] = 1  # Enable the Motor
        self.bp_struct.MotorEnable[self.bp_RIGHT_MOTOR_PORT] = 1  # Enable the Motor
        self.bp_struct.MotorEnable[self.bp_HEAD_MOTOR_PORT] = 1  # Enable the Motor

        self.log.info("set up motors done")
        self.ready.on_next("set up motors done.")

        self.ready.on_completed()
        self.ready.dispose()

        self.log.debug("setup done")

    def set_left_speed(self, new_speed):
        self.bp_struct.MotorSpeed[self.bp_LEFT_MOTOR_PORT] = new_speed

    def set_right_speed(self, new_speed):
        self.bp_struct.MotorSpeed[self.bp_RIGHT_MOTOR_PORT] = new_speed

    def set_head_speed(self, new_speed):
        self.bp_struct.MotorSpeed[self.bp_HEAD_MOTOR_PORT] = new_speed


BRICK_PI = BrickPiFacadeThread()
