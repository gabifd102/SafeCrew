import time
time.sleep(0.1) #wait for USB to become ready

print("SafeCrew Safe System")

from KeypadController import *

c = KeypadController()
c.run()