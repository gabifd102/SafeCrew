"""
A basic template file for using the Model class in PicoLibrary
This will allow you to implement simple Statemodels with some basic
event-based transitions.
"""

# Import whatever Library classes you need - StateModel is obviously needed
# Counters imported for Timer functionality, Button imported for button events
import time
import random
from Log import *
from StateModel import *
from Counters import *
from ServoController import *
from Motors import *
from Pin import *
from Safe import *
from Keypad import *
from Displays import *
from CompositeLights import *
from Buzzer import *

"""
This is the template for a Controller - you should rename this class to something
that is supported by your class diagram. This should associate with your other
classes, and any PicoLibrary classes. If you are using Buttons, you will implement
buttonPressed and buttonReleased.

To implement the state model, you will need to implement __init__ and 4 other methods
to support model start, stop, entry actions, exit actions, and state actions.

The following methods must be implemented:
__init__: create instances of your View and Business model classes, create an instance
of the StateModel with the necessary number of states and add the transitions, buttons
and timers that the StateModel needs

stateEntered(self, state, event) - Entry actions
stateLeft(self, state, event) - Exit actions
stateDo(self, state) - do Activities

# A couple other methods are available - but they can be left alone for most purposes

run(self) - runs the State Model - this will start at State 0 and drive the state model
stop(self) - stops the State Model - will stop processing events and stop the timers

This template currently implements a very simple state model that uses a button to
transition from state 0 to state 1 then a 5 second timer to go back to state 0.
"""


class KeypadController:

    TONE1 = RE
    TONE2 = DO
    TONE3 = FA

    def __init__(self):
        print("Initializing KeypadController...")
        
        # Instantiate whatever classes from your own model that you need to control
        self.door = ServoController(servopin=16)
        self.safe = Safe(user_pin="1234")
        row_pins = [9, 8, 7, 6]
        col_pins = [5, 4, 3, 2]
        self.keypad = Keypad(row_pins, col_pins)
        self.lcd_display = LCDDisplay(sda=0, scl=1)
        self.rgb_light = Pixel(Rpin=26, Gpin=22, Bpin=27)
        self._model = StateModel(6, self, debug=True)
        self._timer = SoftwareTimer(name="timer1", handler=None)
        self._model.addTimer(self._timer)
        self.buzzer = PassiveBuzzer(pin=28)

        
        # Add custom events
        self._model.addCustomEvent("close")
        self._model.addCustomEvent("key_entered")
        self._model.addCustomEvent("pin_valid")
        self._model.addCustomEvent("pin_invalid")
        self._model.addCustomEvent("pin_reset")
        self._model.addCustomEvent("admin_override")
        
        # Add transitions
        self._model.addTransition(0, ["key_entered"], 1)  # idle -> pin validation
        self._model.addTransition(1, ["pin_valid"], 2)    # pin validation -> unlocked
        self._model.addTransition(1, ["pin_invalid"], 4)  # pin validation -> locked out
        self._model.addTransition(2, ["close"], 0)  # unlocked -> idle
        self._model.addTransition(3, ["pin_reset"], 0)        # pin reset -> idle
        self._model.addTransition(3, ["key_entered"], 0)  # pin reset -> idle
        self._model.addTransition(4, ["admin_override"], 5)  # locked out -> admin override
        self._model.addTransition(5, ["close"], 0) 
        self._model.addTransition(0, ["pin_reset"], 3)  # idle -> pin reset
        
        self.entered_pin = ""
    
    def stateEntered(self, state, event):
        Log.d(f'State {state} entered on event {event}')
        if state == 0:
            self.door.close()
            self.lcd_display.clear()
            self.lcd_display.showText("Safe Crew", 0, 0)
            self.lcd_display.showText("Please Input Pin", 1, 0)
            self.rgb_light.setColor((0, 0, 255))  # Blue
            print("Safe is locked.")
        elif state == 1:
            self.lcd_display.showText("Validating...", 0, 0)
        elif state == 2:
            self.door.open()
            self.play_song()
            self.lcd_display.clear()
            self.lcd_display.showText("Safe", 0, 0)
            self.lcd_display.showText("Unlocked!", 1, 0)   
            self.rgb_light.setColor((0, 255, 0))  # Green
            print("Safe is unlocked.")
        elif state == 3:
            self.entered_pin = ""
            self.lcd_display.clear()
            self.lcd_display.showText("Pin: ", 1, 0)
        elif state == 4:
            self.lcd_display.showText("Locked Out", 0, 0)
            self.lcd_display.showText("Contact Admin", 1, 0)
            self.rgb_light.setColor((255, 0, 0))  # Red
            self.play_long_beeps()
        elif state == 5:
            self.lcd_display.showText("Admin Override", 0, 0)
            self.door.open()
            self.play_song()
            self.lcd_display.clear()
            self.lcd_display.showText("Safe", 0, 0)
            self.lcd_display.showText("Unlocked!", 1, 0)   
            self.rgb_light.setColor((0, 255, 0))  # Green
            print("Safe is unlocked.")

    def stateLeft(self, state, event):
        Log.d(f'State {state} exited on event {event}')
        if state == 2:
            self.lcd_display.clear()
            # self.lcd_display.showText("Safe Closed", 0, 0)

        if state == 3:
            self.play_song()
    
    def stateEvent(self, state, event) -> bool:
        Log.d(f'State {state} received event {event}')
        return False

    def stateDo(self, state):
        if state in [0, 1, 2, 3, 4, 5]:
            key = self.keypad.scanKey()
            if key:
                self.process_key(key)

    def run(self):
        self._model.run()

    def stop(self):
        self._model.stop()
    
    def process_key(self, key):
        Log.d(f'Processing key: {key}')
        self.buzzer.beep()  # Beep anytime a key is pressed
        if key == "#":
            self.entered_pin = "#"
        elif self.entered_pin == "#" and key == "6":
            self.entered_pin += key
        elif self.entered_pin == "#6" and key == "1":
            self.entered_pin += key
        elif self.entered_pin == "#61" and key == "0":
            self.entered_pin += key
        elif self.entered_pin == "#610" and key == "6":
            self._model.processEvent("pin_reset")
            self.entered_pin = ""
        elif key == "*":
            self._model.processEvent("close")
            self.entered_pin = ""
        else:
            self.entered_pin += key
            self.lcd_display.clear()
            self.lcd_display.showText(f"Pin: {'*' * len(self.entered_pin)}", 1, 0)
            print(f"Entered PIN: {self.entered_pin}")
            if len(self.entered_pin) == 4:
                if self._model._curState == 3:  # PIN reset state
                    self.safe.reset_pin(self.entered_pin)
                    self.lcd_display.showText("Pin Reset", 0, 0)
                    self._model.processEvent("key_entered")
                else:
                    self._model.processEvent("key_entered")
                    if self.safe.admin_override(self.entered_pin):
                        Log.d('Admin PIN is valid')
                        if self._model._curState == 4:
                            self._model.processEvent("admin_override")
                        else:
                            self._model.processEvent("pin_valid")
                    elif self.safe.pin.verify_user_pin(self.entered_pin):  # Check for user PIN
                        Log.d('User PIN is valid')
                        self._model.processEvent("pin_valid")
                    else:
                        Log.d('PIN is invalid')
                        self.play_single_long_beep()  # Call play_single_long_beep method
                        self.safe.attempts += 1
                        if self.safe.attempts >= self.safe.max_attempts:
                            self._model.processEvent("pin_invalid")
                        else:
                            self.lcd_display.showText("Incorrect Pin", 0, 0)
                            self.lcd_display.showText("Try again", 1, 0)
                            self.rgb_light.setColor((255, 165, 0))  # Orange
                self.entered_pin = ""

    def play_song(self):
        self.buzzer.play(self.TONE1)
        time.sleep(0.2)
        self.buzzer.stop()
        time.sleep(0.1)
        self.buzzer.play(self.TONE2)
        time.sleep(0.2)
        self.buzzer.stop()
        time.sleep(0.1)
        self.buzzer.play(self.TONE3)
        time.sleep(0.2)
        self.buzzer.stop()

    def play_long_beeps(self):
        for _ in range(5):
            self.buzzer.play(500)  # Play a tone at 500 Hz
            time.sleep(0.5)  # Beep duration
            self.buzzer.stop()
            time.sleep(0.2)  # Pause between beeps

    def play_single_long_beep(self):
        self.buzzer.play(500)  # Play a tone at 500 Hz
        time.sleep(1)  # Beep duration
        self.buzzer.stop()

if __name__ == '__main__':
    p = KeypadController()
    try:
        p.run()
        while True:
            key = p.keypad.scanKey()
            if key:
                p.process_key(key)
            time.sleep(0.1)
    except KeyboardInterrupt:
        p.stop()
        print("Keypad test stopped.")
