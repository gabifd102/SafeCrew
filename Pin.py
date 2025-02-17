"""
This class will store the pin data for the managing the user pin as well as store the admin override pin. 
We will use this class on the Safe class which will be responsible for validating the pins, checking how many attempts have been done, 
checking if the safe is locked, and doing the admin override if needed.
"""
class Pin:
    def __init__(self, user_pin):
        self.user_pin = user_pin
        self.admin_pin = "6106"

    def verify_user_pin(self, pin):
        return pin == self.user_pin

    def verify_admin_pin(self, pin):
        return pin == self.admin_pin

    def reset_user_pin(self, new_pin):
        self.user_pin = new_pin