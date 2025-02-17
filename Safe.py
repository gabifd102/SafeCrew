"""This class will manage validating whether the pin the user is putting is correct, as well as number of attempts, admin overrides and 
checking whether the safe is locked or unlocked
"""

from Pin import *

class Safe:
    def __init__(self, user_pin):
        self.pin = Pin(user_pin)
        self.locked = True
        self.attempts = 0
        self.max_attempts = 3

    def reset_pin(self, new_pin):
        self.pin.reset_user_pin(new_pin)

    def is_locked(self):
        return self.locked

    def unlock(self, pin):
        if self.pin.verify_user_pin(pin):
            self.locked = False
            self.attempts = 0
            return True
        else:
            self.attempts += 1
            if self.attempts >= self.max_attempts:
                self.locked = True
            return False

    def admin_override(self, pin):
        if self.pin.verify_admin_pin(pin):
            self.locked = False
            self.attempts = 0
            return True
        return False

    def lock(self):
        self.locked = True

