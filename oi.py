import math
from wpilib.joystick import Joystick
from wpilib.buttons.joystickbutton import JoystickButton


class T16000M(Joystick):

    def __init__(self, port):
        super().__init__(port)
        self.port = port
        self.setXChannel(0)
        self.setYChannel(1)
        self.setZChannel(2)
        self.setThrottleChannel(3)
        self.setTwistChannel(2)


leftDriverStick = None
rightDriverStick = None

btnDriveSlow = None


class ConfigHolder:
    pass


config = ConfigHolder()
config.leftDriverStickNullZone = 0.05
config.rightDriverStickNullZone = 0.05

config.throttleFilterPower = 0.4
config.turnFilterPower = 0.4


def init():
    """
    Assign commands to button actions, and publish your joysticks so you
    can read values from them later.
    """

    global leftDriverStick
    global rightDriverStick

    leftDriverStick = T16000M(0)
    rightDriverStick = T16000M(1)

    global btnDriveSlow
    btnDriveSlow = JoystickButton(leftDriverStick, 1)


# https://www.desmos.com/calculator/yopfm4gkno
# power should be > 0.1 and less than 4 or 5 ish on the outside
#    If power is < 1.0, the curve is a logarithmic curve to give more power closer to center
#    Powers greater than one give a more traditional curve with less sensitivity near center
def filterInputToPower(val, deadZone=0.0, power=2):
    power = math.fabs(power)
    if power < 0.1:
        power = 0.1
    if power > 5:
        power = 5

    sign = 1.0
    if val < 0.0:
        sign = -1.0

    val = math.fabs(val)
    deadZone = math.fabs(deadZone)

    if val < deadZone:
        val = 0.0
    else:
        val = val * ((val - deadZone) / (1 - deadZone))

    output = val ** power
    return output * sign


# View output: https://www.desmos.com/calculator/uh8th7djep
# to keep a straight line, scale = 0, and filterFactor = 1
# Keep filterFactor between 0 and 1
# Scale can go from 0 up, but values over 3-4 have dubious value
# Nice curve for game pad is filterFactor = 0.2, scale=1.5
def filterInput(val, deadZone, filterFactor, scale):
    """
    Filter an input using a curve that makes the stick less sensitive at low input values
    Take into account any dead zone required for values very close to 0.0
    """

    sign = 1.0
    if val < 0.0:
        sign = -1.0

    val = math.fabs(val)
    deadZone = math.fabs(deadZone)

    if val < deadZone:
        val = 0.0
    else:
        val = val * ((val - deadZone) / (1 - deadZone))

    output = (filterFactor * (val**scale)) + ((1 - filterFactor) * val)
    output *= sign
    return output


def applyDeadZone(val, deadZone):
    """
    Apply a dead zone to an input with no other smoothing. Values outsize the dead zone are correctly scaled for 0 to 1.0
    :return:
    The float value of the adjusted intput
    """
    sign = 1.0
    if val < 0.0:
        sign = -1.0

    val = math.fabs(val)
    deadZone = math.fabs(deadZone)

    if val < deadZone:
        val = 0.0
    else:
        val = val * ((val - deadZone) / (1 - deadZone))

    val *= sign
    return val


def getRawThrottle():
    """
    Use the Y Axis of the left stick for throttle.  Value is reversed so that 1.0 is forward (up on a joystick is usually negative input)
    :return:
    The float value of the throttle between -1.0 and 1.0
    """
    val = leftDriverStick.getY()
    if val != 0.0:
        val *= -1.0
    return val


def getRawTurn():
    return rightDriverStick.getX()

