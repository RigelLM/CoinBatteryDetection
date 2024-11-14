import RPi.GPIO as gpio
import gpiozero

import Camera
import VideoProcess

from time import sleep

# GPIO pin setup
ON = True
OFF = not ON

RELAY_PIN = 24
gpio.setmode(gpio.BCM)

relay = gpiozero.OutputDevice(RELAY_PIN, active_high=True, initial_value=False)

# Mimic pressing sensor button for i seconds
def press_sensor_btn(i):
    relay.on()
    sleep(i)
    relay.off()

# Set the sensor display
def set_sensor(on):
    sensor_image = Camera.get_image_2_array()
    currently_on = VideoProcess.check_display(sensor_image)
    if currently_on:
        if on:
            print("Sensor already on")
        else:
            press_sensor_btn(0.5)
            print("Sensor off")
    else:
        if on:
            press_sensor_btn(0.5)
            print("Sensor on")
            # Wait til display is ready
            sleep(10)
        else:
            print("Sensor already off")
