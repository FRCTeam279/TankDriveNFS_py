# TankDriveNFSpy

This code shows how to implement a highly refined control scheme for tank drive robots. 
The goal of the code is to make a tank drive robot behave in a predictable manner to someone used
to car driving styles.  

Throttle and steering are controlled in a Need for Speed style, with one axis providing throttle,
and a second providing turn.

It is currently setup to put throttle on a left joystick Y axis, and turn on a right joystick Y
axis, but can easily be switched to a gamepad by editing the oi.py file.

The oi.py file has parameters for the joystick curves deadzones. All other parameters are in the
robotmap.py file.



## What makes this unique?

Speed of turning will be adjusted based on throttle, and spinning one way then reversing
will not happen instantly.

Also, spinning one direction and then taking throttle to full reverse will reverse the 
direction of turn, in the same manner as a car with the wheel turned fully one direction.

Throttle will set the base forward or backward speed, and turn will reduce the speed of the 
slower side.

The amount reduced will be itself reduced based on the throttle. This allows the robot to turn
in an arc as is generally more expected when driving at speed.

All parameters are configurable. Nothing is hard coded in the command file.



## Python???
Yes, we switched from Java to Python in the 2017/2019 PowerUp season. 
A big thanks to the RobotPy team for providing this amazing community project!



## Using, Suggestions, Comments
If you use this code, I'd appreciate it if you sent me an email letting me know!

drakoswraith@gmail.com

Please let us know if you run into any issues or have any suggestions for future refinement.


 