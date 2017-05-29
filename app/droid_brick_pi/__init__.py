import logging
import time
from Queue import Queue, LifoQueue, Full
from threading import Thread

from app.droid_configuration import droidConfig, ensure_configuration_loaded


def should_use_mock():
    ensure_configuration_loaded()
    return droidConfig.getboolean("BrickPi", "UseMock")


class ColorSensorReader(Thread):
    def __init__(self, brick_pi):
        super(ColorSensorReader, self).__init__()
        self.log = logging.getLogger(self.__class__.__name__)
        self.should_run = True
        self.brick_pi = brick_pi
        self.start()

    def run(self):
        self.log.debug("Start reading...")
        while self.should_run:
            time.sleep(0.01)  # sleep for 10 ms
            # The color sensor will go to sleep and not return proper values if it is left for longer than 100 ms.
            # You must be sure to poll the color sensor every 100 ms!
            if self.brick_pi.update_values():
                # ok values are up to date
                color = self.brick_pi.read_color_sensor()
                # self.log.debug("read" + str(color))
                if self.brick_pi.color_sensor_queue.full():
                    self.brick_pi.color_sensor_queue.get()
                else:
                    self.brick_pi.color_sensor_queue.put(color, block=False )

        self.log.debug("Stop reading...")

    def stop(self):
        self.should_run = False

    def start_reading(self):
        self.should_run = True


# facade for all brickpi operation
class BrickPiFacade:
    def __init__(self):
        # setup brick pi
        if should_use_mock():
            from app.droid_brick_pi.BrickPiMock import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, \
                BrickPiSetupSensors, BrickPiUpdateValues
        else:
            from app.droid_brick_pi.BrickPi import BrickPiSetup, BrickPi, PORT_4, TYPE_SENSOR_EV3_COLOR_M2, \
                BrickPiSetupSensors, BrickPiUpdateValues

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

        # create Queue where updated values are posted.
        self.color_sensor_queue = LifoQueue(maxsize=100)

        self.color_sensor_reader = None

    def start_reading_colors(self):
        self.color_sensor_reader = ColorSensorReader(self)

    def stop_reading_colors(self):
        if self.color_sensor_reader is not None:
            self.color_sensor_reader.stop()

    def update_values(self):
        return not self.update_value_function()  # Ask BrickPi to update values for sensors/motors

    def read_color_sensor(self):
        return self.brick_pi_struct.Sensor[self.color_sensor_port]

    def done(self):
        self.stop_reading_colors()


BRICK_PI = BrickPiFacade()
