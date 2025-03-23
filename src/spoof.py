"""
this file's purpose is:
the server should activate this script in a distinct process, 
and than kills it, when shutting down.
"""





import sys
import signal
import time
import random

from netwroking import Spoofer

if (len(sys.argv) != 3):
    print("Wrong usage. Usage- spoof.py <host_ip> <target_ip> <router_ip>")
    sys.exit(0)


host_ip,target_ip,router_ip = sys.argv




def signal_handler(sig,frame):
    print("Shutting down....")
    spoof_obj.checkout()
    sys.exit(0)
signal.signal(signal.SIGTERM,signal_handler)

spoof_obj : Spoofer = Spoofer(*sys.argv)
while True:
    spoof_obj.spoof()
    time.sleep(random.random()/5) # wait a random number between 0-0.2

