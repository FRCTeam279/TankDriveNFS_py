# TankDriveNFSpy

This code implements a highly refined control scheme for tank drive robots. 

It was developed by Michael Lehman for Team 279 TechFusion (www.team279.com) and has been updated, rewritten, and
tweaked over the course of a few competition seasons.

See the github repository for updates (https://github.com/FRCTeam279/TankDriveNFS_py)


The goal of the code is to make a tank drive robot behave in a manner predictable to someone used
to how a car drives. Cars can't spin in place - unlike a robot with a "tank drive" or skid 
steering based driveline, which presents some significant challenges in creating a polished system
for driving.  

Throttle and steering are controlled in the same manner as many video games, such as Need for 
Speed - with one axis providing throttle, and a second providing turn.

It is currently setup to put throttle on a left joystick Y axis, and turn on a right joystick Y
axis, but can easily be switched to a gamepad by editing the oi.py file.




## What makes this unique?

Speed of turning will be adjusted based on throttle, and spinning one way then reversing
will not happen instantly.

Also, spinning one direction and then taking throttle to full reverse will reverse the 
direction of turn, in the same manner as a car with the wheel turned fully one direction.

Throttle will set the base forward or backward speed, and turning will reduce the speed of the 
slower side.

The amount reduced will be itself reduced based on the throttle. This allows the robot to turn
in an arc as is generally more expected when driving at speed.

All parameters are configurable. Nothing is hard coded in the command file.



## Using, Suggestions, Comments
If you use this code, I'd appreciate it if you sent me an email letting me know!

drakoswraith@gmail.com

Please let us know if you run into any issues or have any suggestions for future refinement.



## Python???
Yes, we switched from Java to Python in the 2017/2018 PowerUp season. 
A big thanks to the RobotPy team for providing this amazing community project!



## How to Use
The tankdriveteleopdefaultnfs.py command file fully encapsulates all the driving logic.
It can be copied straight into your RobotPy command based robot.

If you're not using a CommandBased framework, you can use the *execute* and *nfsCalcTrackSpeeds* 
functions separately without any problems.

It expects the following code features to be in place in the driveline, oi.py, and robotmap.py.
If these features aren't in place, or are named differently, then you'll need to edit
the tankdriveteleopdefaultnfs.py appropriately.
 
 


### The driveline subsystem
* The driveline is referenced as subsystems.driveline via the *subsystems/\_\_init\_\_.py* file
* A driveRaw function should exist on the subsystem with this signature:
  * *def driveRaw(self, left, right):*
  * where *left* and *right* are the speeds applied directly to the two speed controllers
* Set TankDriveTeleopDefaultNFS as the default command

```
    # ... inside the driveline subsystem
    def initDefaultCommand(self):
        self.setDefaultCommand(TankDriveTeleopDefaultNFS())
    
    def driveRaw(self, left, right):
        if self.leftSpdCtrl:
            self.leftSpdCtrl.set(left)
        if self.rightSpdCtrl:
            self.rightSpdCtrl.set(right)
```



### In the oi.py file
* A JoystickButton defined to drive slow while held (just define the button on the right index, don't bind it wih the "whileHeld" function)
  * The button's name should be:
  * oi.btnDriveSlow
  * We use the left joystick trigger...
* The config options set below in the code block below
* The filterInputToPower function
  * Copy this from the oi.py to your oi.py file.
  * Function signature:
  * *def filterInputToPower(val, deadZone=0.0, power=2):*  
  
  
Note that the filter parameters shown below will give a logarithmic curve, and not exponential
which most people will expect (if a robot requires 20-30% power applied before it starts moving
this will actually give a better response than the typical curve).  The oi.py file has links to 
Desmos graphs you can play with for curves.

Example: [Desmos filterInputToPower Curves](https://www.desmos.com/calculator/yopfm4gkno)
```
class ConfigHolder:
    pass


config = ConfigHolder()
config.leftDriverStickNullZone = 0.05
config.rightDriverStickNullZone = 0.05

config.throttleFilterPower = 0.4
config.turnFilterPower = 0.4
```



### The robotmap.py file

Copy, and edit (if desired, the defaults work for many robots), these settings from the 
robotmap.py file. See the robotmapy.py file in this project for the comments which
explain the parameters

```
class ConfigHolder:
    pass
    
nfs = ConfigHolder()
nfs.debugTurning = False

nfs.lowTurnScale = 0.3                  # How much to reduce turn speed when driving at full throttle at
nfs.highTurnScale = 0.2
nfs.slowDriveSpeedFactor = 0.7          # Max speed when driving in slow mode

nfs.minTimeFullThrottleChange = 1.5
nfs.maxSpeedChange = (2 * 0.02) / nfs.minTimeFullThrottleChange
```