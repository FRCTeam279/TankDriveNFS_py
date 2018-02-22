import wpilib
from commandbased import CommandBasedRobot
from wpilib.command import Scheduler
from wpilib.driverstation import DriverStation


# import items in the order they should be initialized to avoid any suprises
import robotmap
import subsystems
import oi


class MyRobot(CommandBasedRobot):
    # for parent code see:
    # https://github.com/robotpy/robotpy-wpilib-utilities/blob/master/commandbased/commandbasedrobot.py

    def robotInit(self):
        print('TankDriveNFSpy - robotInit called')

        # subsystems must be initialized before things that use them
        subsystems.init()
        oi.init()

    def teleopPeriodic(self):
        Scheduler.getInstance().run()

    def testPeriodic(self):
        wpilib.LiveWindow.run()


if __name__ == '__main__':
    wpilib.run(MyRobot)

