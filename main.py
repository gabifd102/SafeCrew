import time
time.sleep(0.1) #wait for USB to become ready

print("SafeCrew Safe System")

from ServoController import *

c = ServoController()
c.run()