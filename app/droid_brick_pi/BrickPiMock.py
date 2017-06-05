import time
from threading import Thread, Event


def BrickPiSetup():
    time.sleep(0.5)
    return 0


def BrickPiSetupSensors():
    time.sleep(0.5)
    mood_sequence()
    return 0


def set_sensor_port_4_to(mocked_value):
    global sensor_4
    print("changing sensor_4 to " + str(mocked_value))
    sensor_4 = mocked_value


class MoodSequence(Thread):
    def __init__(self, event, seq=None):
        Thread.__init__(self)
        if seq is None:
            seq = []
        self.seq = seq
        self.stopped = event
        self.count = 0

    def run(self):
        while not self.stopped.wait(2):
            set_sensor_port_4_to(self.seq[self.count % len(self.seq)])
            self.count += 1


stopFlag = Event()


def mood_sequence():
    print ("starting mood sequence")

    thread = MoodSequence(stopFlag, seq=(0, 4, 0, 2, 0, 3, 0, 1))
    thread.start()


def stop():
    stopFlag.set()


sensor_4 = 0


def BrickPiUpdateValues():
    BrickPi.Sensor[PORT_4] = sensor_4
    return False


PORT_A = 0
PORT_B = 1
PORT_C = 2
PORT_D = 3

PORT_1 = 0
PORT_2 = 1
PORT_3 = 2
PORT_4 = 3

TYPE_SENSOR_EV3_COLOR_M2 = 0


class BrickPiStruct:
    Address = [1, 2]
    MotorSpeed = [0] * 4

    MotorEnable = [0] * 4

    EncoderOffset = [None] * 4
    Encoder = [None] * 4

    Sensor = [None] * 4
    SensorArray = [[None] * 4 for i in range(4)]
    SensorType = [0] * 4
    SensorSettings = [[None] * 8 for i in range(4)]

    SensorI2CDevices = [None] * 4
    SensorI2CSpeed = [None] * 4
    SensorI2CAddr = [[None] * 8 for i in range(4)]
    SensorI2CWrite = [[None] * 8 for i in range(4)]
    SensorI2CRead = [[None] * 8 for i in range(4)]
    SensorI2COut = [[[None] * 16 for i in range(8)] for i in range(4)]
    SensorI2CIn = [[[None] * 16 for i in range(8)] for i in range(4)]
    Timeout = 0


BrickPi = BrickPiStruct()
