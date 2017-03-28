import time
from random import randint


def BrickPiSetup():
    time.sleep(0.5)
    return 0


def BrickPiSetupSensors():
    time.sleep(0.5)
    return 0


def BrickPiUpdateValues():
    BrickPi.Sensor[PORT_4] = randint(0,7)
    return False


PORT_4 = 3

TYPE_SENSOR_EV3_COLOR_M2 = 0


class BrickPiStruct:
    Address = [ 1, 2 ]
    MotorSpeed  = [0] * 4

    MotorEnable = [0] * 4

    EncoderOffset = [None] * 4
    Encoder       = [None] * 4

    Sensor         = [None] * 4
    SensorArray    = [ [None] * 4 for i in range(4) ]
    SensorType     = [0] * 4
    SensorSettings = [ [None] * 8 for i in range(4) ]

    SensorI2CDevices = [None] * 4
    SensorI2CSpeed   = [None] * 4
    SensorI2CAddr    = [ [None] * 8 for i in range(4) ]
    SensorI2CWrite   = [ [None] * 8 for i in range(4) ]
    SensorI2CRead    = [ [None] * 8 for i in range(4) ]
    SensorI2COut     = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
    SensorI2CIn      = [ [ [None] * 16 for i in range(8) ] for i in range(4) ]
    Timeout = 0

BrickPi = BrickPiStruct()

