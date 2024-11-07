import RPi.GPIO as gpio
from time import sleep
import gpiozero
import os


RELAY_PIN = 24

gpio.setmode(gpio.BCM)

relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

def set_relay(status):
    if status:
        print("Setting relay: ON")
        relay.on()
    else:
        print("Setting relay: OFF")
        relay.off()

# if not os.path.exists("monitor_on"):
#     with open("monitor_on", 'w') as file:
#         pass

