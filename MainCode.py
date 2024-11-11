from gpiozero import LED
from gpiozero import Button

import Scan
import VideoProcess
import ClusterDetection
import Relay


from time import sleep
import threading
import os

# GPIO pin setup
button= Button(26)
led_green = LED(23)
led_red = LED(22)
led_white = LED(27)
led_blue = LED(18)
led_yellow = LED(17)

def main():
    print("Start scanning ...")
    Scan.scan("./Temp/v.mp4")
    sleep(2)

    print("Preparing for detection ...")
    VideoProcess.crop_video("./Temp/v.mp4", "./Temp/v_p.mp4")
    sleep(2)

    print("Processing scanning result ...")
    return ClusterDetection.detect("./Temp/v_p.mp4")

def show(result):
    if result == "Metal" or result == "Battery":
        led_yellow.on()
    else:
        led_white.on()

def green_blink():
    while not stop_event.is_set():
        sleep(0.25)
        led_green.on()
        sleep(0.25)
        led_green.off()

def red_blink():
    led_red.on()
    sleep(0.25)
    led_red.off()
    sleep(0.25)

def lights_off():
    led_white.off()
    led_yellow.off()
    led_red.off()
    led_blue.off()
    led_green.off()

if __name__ == "__main__":

    # Callibration
    callibration_pass = Scan.callibration()

    if callibration_pass:
        # Turn on sensor display
        Relay.set_sensor(Relay.ON)

        led_green.on()

        in_progress = False
        while callibration_pass:
            if button.is_pressed:
                print("Button pressed")

                if not in_progress:
                    in_progress = True

                    lights_off()

                    stop_event = threading.Event()
                    led_thread = threading.Thread(target=green_blink)
                    led_thread.start()
                    result = main()
                    stop_event.set()
                    led_thread.join()
                    print("Thread end")

                    show(result)
                    in_progress = False
                else:
                    print("Already in progress")
                # Do callibration after every scan
                callibration_pass = Scan.callibration()
        # If callibration fails, pause the whole system and wait for reboot
        while True:
            # Reboot the whole system if button is pressed
            if button.is_pressed:
                os.system('sudo reboot')
            red_blink()
    else:
        # If callibration fails, pause the whole system and wait for reboot
        while True:
            # Reboot the whole system if button is pressed
            if button.is_pressed:
                os.system('sudo reboot')
            red_blink()
