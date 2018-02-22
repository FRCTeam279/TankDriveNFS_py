import math
import wpilib
from wpilib.command.subsystem import Subsystem
from wpilib import PIDController
from wpilib.interfaces import PIDSource, PIDOutput

import subsystems
import robotmap
from commands.tankdriveteleopdefaultnfs import TankDriveTeleopDefaultNFS as TankDriveTeleopDefaultNFS


class TankPID(PIDSource, PIDOutput):

    def __init__(self, minSpeed=0.0):
        self.minSpeed = minSpeed
        pass

    def getPIDSourceType(self):
        return wpilib.pidcontroller.PIDController.PIDSourceType.kDisplacement

    def setPIDSourceType(self, pidSource):
        pass

    def pidGet(self):
        return subsystems.driveline.getPIDEncoderCount()

    def pidWrite(self, output):
        if math.fabs(output) < self.minSpeed:
            if output < 0.0:
                subsystems.driveline.driveRaw(-1.0 * self.minSpeed, -1.0 * self.minSpeed)
            else:
                subsystems.driveline.driveRaw(self.minSpeed, self.minSpeed)
        else:
            subsystems.driveline.driveRaw(output, output)


class TankPIDTurn(PIDSource, PIDOutput):

    def __init__(self, minSpeed, scaleSpeed):
        self.scaleSpeed = scaleSpeed
        self.minSpeed = minSpeed

    def getPIDSourceType(self):
        return wpilib.pidcontroller.PIDController.PIDSourceType.kDisplacement

    def setPIDSourceType(self, pidSource):
        pass

    def pidGet(self):
        return robotmap.sensors.ahrs.getYaw()

    def pidWrite(self, output):
        raw = math.fabs(output)
        raw *= self.scaleSpeed
        if raw < self.minSpeed:
            raw = self.minSpeed

        if output > 0.0:
            subsystems.driveline.driveRaw(raw, -raw)
        else:
            subsystems.driveline.driveRaw(-raw, raw)


class TankDrive(Subsystem):

    def __init__(self):
        print('TankDrive: init called')
        super().__init__('TankDrive')
        self.debug = False
        self.logPrefix = "TankDrive: "

        # Speed controllers
        if robotmap.driveLine.speedControllerType == "VICTORSP":
            try:
                self.leftSpdCtrl = wpilib.VictorSP(robotmap.driveLine.leftMotorPort)
                if robotmap.driveLine.invertLeft:
                    self.leftSpdCtrl.setInverted(True)
            except Exception as e:
                print("{}Exception caught instantiating left speed controller. {}".format(self.logPrefix, e))
                if not wpilib.DriverStation.getInstance().isFmsAttached():
                    raise

            try:
                self.rightSpdCtrl = wpilib.VictorSP(robotmap.driveLine.rightMotorPort)
                if robotmap.driveLine.invertRight:
                    self.rightSpdCtrl.setInverted(True)
            except Exception as e:
                print("{}Exception caught instantiating right speed controller. {}".format(self.logPrefix, e))
                if not wpilib.DriverStation.getInstance().isFmsAttached():
                    raise
        elif robotmap.driveLine.speedControllerType == "TALON":
            try:
                self.leftSpdCtrl = wpilib.Talon(robotmap.driveLine.leftMotorPort)
                if robotmap.driveLine.invertLeft:
                    self.leftSpdCtrl.setInverted(True)
            except Exception as e:
                print("{}Exception caught instantiating left speed controller. {}".format(self.logPrefix, e))
                if not wpilib.DriverStation.getInstance().isFmsAttached():
                    raise

            try:
                self.rightSpdCtrl = wpilib.Talon(robotmap.driveLine.rightMotorPort)
                if robotmap.driveLine.invertRight:
                    self.rightSpdCtrl.setInverted(True)
            except Exception as e:
                print("{}Exception caught instantiating right speed controller. {}".format(self.logPrefix, e))
                if not wpilib.DriverStation.getInstance().isFmsAttached():
                    raise
        else:
            print("{}Configured speed controller type in robotmap not recognized - {}".format(self.logPrefix, robotmap.driveLine.speedControllerType))
            if not wpilib.DriverStation.getInstance().isFmsAttached():
                raise RuntimeError('Driveline speed controller specified in robotmap not valid: ' + robotmap.driveLine.speedControllerType)

        # Encoders
        try:
            self.leftEncoder = wpilib.Encoder(robotmap.driveLine.leftEncAPort, robotmap.driveLine.leftEncBPort,
                                              robotmap.driveLine.leftEncReverse, robotmap.driveLine.leftEncType)
            self.leftEncoder.setDistancePerPulse(robotmap.driveLine.inchesPerTick)
        except Exception as e:
            print("{}Exception caught instantiating left encoder. {}".format(self.logPrefix, e))
            if not  wpilib.DriverStation.getInstance().isFmsAttached():
                raise

        try:
            self.rightEncoder = wpilib.Encoder(robotmap.driveLine.rightEncAPort, robotmap.driveLine.rightEncBPort,
                                               robotmap.driveLine.rightEncReverse, robotmap.driveLine.rightEncType)
            self.rightEncoder.setDistancePerPulse(robotmap.driveLine.inchesPerTick)
        except Exception as e:
            print("{}Exception caught instantiating left encoder. {}".format(self.logPrefix, e))
            if not  wpilib.DriverStation.getInstance().isFmsAttached():
                raise

        # PID Setup
        self.tankPID = TankPID()
        self.pidController = PIDController(0.0, 0.0, 0.0, self.tankPID, self.tankPID)

        self.turnPID = TankPIDTurn(0.0, 0.5)
        self.pidTurnController = PIDController(0.0, 0.0, 0.0, self.turnPID, self.turnPID)

    # ------------------------------------------------------------------------------------------------------------------
    def initDefaultCommand(self):
            self.setDefaultCommand(TankDriveTeleopDefaultNFS())
            print("{}Default command set to DriveTeleopDefaultNFS".format(self.logPrefix))

    def driveRaw(self, left, right):
        if self.debug:
            if self.leftSpdCtrl:
                self.leftSpdCtrl.set(0.0)
            if self.rightSpdCtrl:
                self.rightSpdCtrl.set(0.0)
        else:
            if self.leftSpdCtrl:
                self.leftSpdCtrl.set(left)
            if self.rightSpdCtrl:
                self.rightSpdCtrl.set(right)

    def stop(self):
        if self.leftSpdCtrl:
            self.leftSpdCtrl.set(0.0)
        if self.rightSpdCtrl:
            self.rightSpdCtrl.set(0.0)

    def resetEncoders(self):
        self.leftEncoder.reset()
        self.rightEncoder.reset()

    def getAvgEncoder(self):
        return int(round((self.leftEncoder.get() + self.rightEncoder.get()) / 2, 0))

    def getPIDEncoderCount(self):
        return self.leftEncoder.get()
