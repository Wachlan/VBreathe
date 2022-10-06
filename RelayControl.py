# Script for 3-ch RPi Relay Board
import RPi.GPIO as GPIO
from time import sleep
import datetime
import csv
import os
import keyboard


pressCounter = 0

# Relay channel definitions
relay1 = 26
#relay2 = 20 but not in use
#relay3 = 21 but not in use

# Initialise GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(relay1,GPIO.OUT)
#GPIO.setup(relay2,GPIO.OUT) but relay 2 not in use
#GPIO.setup(relay3,GPIO.OUT) but relay 3 not in use


try:
    while True:
        
        # Relays are active-low
        GPIO.output(relay1,True)
        sleep(3)

        print("Cycling relays #", pressCounter)
        GPIO.output(relay1,False)
        sleep(5)
        pressCounter = pressCounter + 1
    
except KeyboardInterrupt:
    print("Buttons were pressed", pressCounter, "times")
    GPIO.cleanup()
