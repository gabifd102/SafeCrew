""""
ServoController.py This class is what will allow the servo engine to open/close as needed depending on the different states we create. 
It has an initial state where the position is at a closed angle which we define at the beginning of the code.
It also includes an open which will ensure the gate opens based on the angel defined. 
The close state will close the servo motor for the safe. 
Lastly we have a check def which is to ensure the gate is actually closed.
Author: Group6
"""

from Motors import *

OPENANGLE = 90
CLOSEANGLE = 180

class Door:
    """ comments """
    def __init__(self, servopin):
        self._servo = Servo(servopin, 'SafeDoor')
        self._position = CLOSEANGLE

    def open(self):
        self._servo.setAngle(OPENANGLE)
        self._position = OPENANGLE

    def Close(self):
        self._servo.setAngle(CLOSEANGLE)
        
    def isClosed(self)->bool:
        if self._position == CLOSEANGLE:
            return True
        else:
            return False
