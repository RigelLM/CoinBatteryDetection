from gpiozero import LED
from gpiozero import Button

import Scan
import VideoProcess
import ClusterDetection
import Relay


from time import sleep
import threading
import os
from datetime import datetime

# GPIO pin setup
button= Button(26)
led_green = LED(23)
led_red = LED(22)
led_white = LED(27)
led_blue = LED(18)
led_yellow = LED(17)

def write_reference(file_name, result):
    if not os.path.exists('Temp/Reference.txt'):
        with open('Temp/Reference.txt', "w") as file:
            file.write(datetime.now().strftime("%Y%m%d_%H%M%S"))

    with open("Temp/Reference.txt", "a") as file:
        # Write file_name and result
        file.write(f"{file_name} {result}\n")

def main():

    print("Setting up storage folders")
    if not os.path.exists('Temp'):
        os.makedirs('Temp')
        os.makedirs('Temp/Original')
        os.makedirs('Temp/Processed')
    if os.path.exists('Temp'):
        if not os.path.exists('Temp/Original'):
            os.makedirs('Temp/Original')
        if not os.path.exists('Temp/Processed'):
            os.makedirs('Temp/Processed')

    ori_filename = "./Temp/Original/" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".mp4"
    pro_filename = "./Temp/Processed/" + datetime.now().strftime("%Y%m%d_%H%M%S") + "_p.mp4"

    print("Start scanning ...")
    Scan.scan(ori_filename)
    sleep(2)

    print("Preparing for detection ...")
    VideoProcess.crop_video(ori_filename, pro_filename)
    sleep(2)

    print("Processing scanning result ...")
    return ClusterDetection.detect("./Temp/v_p.mp4")
    result =  ClusterDetection.detect(pro_filename)

    write_reference(ori_filename, result)

    return result

def show(result):
    if result == "Metal":
        led_yellow.on()
    elif result == "Battery":
        led_blue.on()
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

                # Do callibration before every scan
                callibration_pass = Scan.callibration()
                if not callibration_pass:
                    break

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
