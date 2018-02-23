import math

from wpilib import SmartDashboard
from wpilib.command import Command
import subsystems
import oi
import robotmap


class TankDriveTeleopDefaultNFS(Command):
    """
    This command uses a throttle and turning control scheme in the same manner as Need for Speed
    It's intended to make a robot that uses skid steering feel like a car

    Speed of turning will be adjusted based on throttle, and spinning one way then reversing will not happen instantly
    Also, spinning one direction and then taking throttle to full reverse will reverse the direction of turn
    """

    def __init__(self):
        super().__init__('TankDriveTeleopDefaultNFS')
        self.requires(subsystems.driveline)
        self.setInterruptible(True)
        self.setRunWhenDisabled(False)
        self.targetLeftSpeed = 0.0
        self.targetRightSpeed = 0.0

    def execute(self):
        throttle = oi.filterInputToPower(oi.getRawThrottle(),
                                         oi.config.leftDriverStickNullZone, oi.config.throttleFilterPower)

        turn = oi.filterInputToPower(oi.getRawTurn(), oi.config.rightDriverStickNullZone, oi.config.turnFilterPower)

        if robotmap.nfs.debugTurning:
            SmartDashboard.putNumber("Throttle", throttle)
            SmartDashboard.putNumber("Turn", turn)

        if oi.btnDriveSlow.get():
            throttle *= robotmap.nfs.slowDriveSpeedFactor
            turn *= robotmap.nfs.slowDriveSpeedFactor

        lastLeftSpeed = self.targetLeftSpeed
        lastRightSpeed = self.targetRightSpeed

        self.nfsCalcTrackSpeeds(throttle, turn)
        if robotmap.nfs.debugTurning:
            SmartDashboard.putNumber("targetLeftSpeed", self.targetLeftSpeed)
            SmartDashboard.putNumber("targetRightSpeed", self.targetRightSpeed)


        leftSpeedDiff = lastLeftSpeed - self.targetLeftSpeed
        rightSpeedDiff = lastRightSpeed - self.targetRightSpeed

        if math.fabs(leftSpeedDiff) > robotmap.nfs.maxSpeedChange:
            if leftSpeedDiff > 0.0:
                leftSpeedDiff = robotmap.nfs.maxSpeedChange
            if leftSpeedDiff < 0.0:
                leftSpeedDiff = robotmap.nfs.maxSpeedChange * -1.0

        if math.fabs(rightSpeedDiff) > robotmap.nfs.maxSpeedChange:
            if rightSpeedDiff > 0.0:
                rightSpeedDiff = robotmap.nfs.maxSpeedChange
            if rightSpeedDiff < 0.0:
                rightSpeedDiff = robotmap.nfs.maxSpeedChange * -1.0

        adjustedLeft = lastLeftSpeed - leftSpeedDiff
        adjustedRight = lastRightSpeed - rightSpeedDiff

        if robotmap.nfs.debugTurning:
            SmartDashboard.putNumber("AdjustedLeft", adjustedLeft)
            SmartDashboard.putNumber("AdjustedRight", adjustedRight)

        subsystems.driveline.driveRaw(adjustedLeft, adjustedRight)

    def isFinished(self):
        return False

    def end(self):
        subsystems.driveline.driveRaw(0.0, 0.0)
        self.targetLeftSpeed = 0.0
        self.targetRightSpeed = 0.0
    
    def interrupted(self):
        subsystems.driveline.driveRaw(0.0, 0.0)
        self.targetLeftSpeed = 0.0
        self.targetRightSpeed = 0.0

    def nfsCalcTrackSpeeds(self, rawThrottleSpeed, rawTurnSpeed):
        """
        Throttle will set the base forward or backward speed
        turn will reduce the speed of the slower side

        The amount reduced will be itself reduced based on the throttle
        Example: for full throttle (1.0), and full turn (1.0)
        a reasonably tight arc is found if the fast side is at +1 and the slow side is at +0.3
        The ammount to reduce the turn by, is found by:
            reduction range = 1 - (turnScale * throttle)

        And the actual slow side speed found by
            slowSide = throttle - (turn * range)

        In the above example, if the scale is 0.3, the reduction range = 0.7  from    1 - (0.3 * 1.0)


        Are there any situations in which the fast side would need to be increased?
        Yes - if the throttle is lower than the turn, the turn reduction to the slow side will be out of kilter with the fast side
        This will cause the robot to actually drive a bit in the opposite direction



        :param rawThrottleSpeed: Throttle value after filtering joystick input -1.0 to +1.0
        :param rawTurnSpeed: Turn value after filtering -1.0 to +1.0
        """

        leftSpeed = 0.0
        rightSpeed = 0.0

        throttle = math.fabs(rawThrottleSpeed)
        throttleSign = 0.0
        if rawThrottleSpeed > 0.0:
            throttleSign = 1.0
        if rawThrottleSpeed < 0.0:
            throttleSign = -1.0
        if rawThrottleSpeed == 0.0:
            throttleSign = 1.0

        turn = math.fabs(rawTurnSpeed)
        turnSign = 0.0
        if rawTurnSpeed > 0.0:
            turnSign = 1.0
        if rawTurnSpeed < 0.0:
            turnSign = -1.0
        if rawTurnSpeed == 0.0:
            turnSign = 1.0

        # forward + right = clockwise (+1.0)
        # forward + left = counter clockwise (-1.0)
        # back + right = counter clockwise (-1.0)
        # back + left = clockwise (+1.0)
        spinSign = throttleSign * turnSign

        if turn != 0.0:
            fastSide = rawThrottleSpeed
            if oi.btnDriveSlow.get():
                # heavy scaling when driving slow
                turnScale = robotmap.nfs.highTurnScale
            else:
                # light scaling when driving fast
                turnScale = robotmap.nfs.lowTurnScale

            range = 1 - (turnScale * throttle)
            slowSide = throttle - (turn * range)
            slowSide *= throttleSign

            if throttle == 0.0:
                # if there's zero throttle, a turn should just spin
                if math.fabs(fastSide) < math.fabs(slowSide):
                    fastSide = slowSide * -1.0
            else:
                # Stop driving the opposite direction if a tiny bit of throttle is given, and more turn is
                # overpowering it
                # TODO - This section is experimental
                # It appears to do what we want, but needs more testing.  It makes the robot more inclined to spin
                # at slow throttle speeds, but does seem to stop it driving in the reverse direction due to how turn
                # is accomplished
                if math.fabs(fastSide) < math.fabs(slowSide):
                    if fastSide > 0.0:
                        fastSide = math.fabs(slowSide)
                    else:
                        fastSide = math.fabs(slowSide) * -1.0

            if spinSign == 1.0:
                leftSpeed = fastSide
                rightSpeed = slowSide

            if spinSign == -1.0:
                leftSpeed = slowSide
                rightSpeed = fastSide
        else:
            #straight ahead
            leftSpeed = rawThrottleSpeed
            rightSpeed = rawThrottleSpeed

        self.targetLeftSpeed = leftSpeed
        self.targetRightSpeed = rightSpeed