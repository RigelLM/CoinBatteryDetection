from gpiozero import LED
from time import sleep


def light_ctl(color, t):

    if color == "white":
        gpio = 27
    elif color == "yellow":
        gpio = 17
    elif color == "red":
        gpio = 22
    elif color == "green":
        gpio = 23
    else:
        gpio = 18
    
    led = LED(gpio)
    led.on()
    if t != 0:
        sleep(t)
        led.off()


