from gpiozero import LED

import Scan
import VideoProcess
import ClusterDetection
import relay


from gpiozero import Button
from time import sleep
import threading
import os

def main():

    folder = "/home/blank-168/Desktop/Project/Temp/"
    print("Start scanning ...")
    Scan.scan("./Temp/v.mp4")
    sleep(2)

    #frames = []
    #frames = VideoProcess.get_frames("./Temp/v.mp4")
    #sleep(2)
    #result = ClusterDetection.detect_frames(frames)

    print("Preparing for detection ...")
    VideoProcess.process_video("./Temp/v.mp4", "./Temp/v_p.mp4")
    sleep(2)

    print("Processing scanning result ...")
    result = ClusterDetection.detect("./Temp/v_p.mp4")
    return result

def show(result):

    if result == "Metal" or result == "Battery":
        led_yellow.on()
    else:
        led_white.on()


def blink():
    while not stop_event.is_set():
        sleep(0.25)
        led_green.on()
        sleep(0.25)
        led_green.off()

if __name__ == "__main__":
    
    # Declaration for gpio
    button= Button(26)
    led_green = LED(23)
    led_red = LED(22)
    led_white = LED(27)
    led_blue = LED(18)
    led_yellow = LED(17)


    callibration_pass = Scan.callibration()

    # Callibration
    if True:

        
        #relay.set_relay(True)
        #sleep(.5)
        #relay.set_relay(False)

        #sleep(10)

        led_green.on()


        in_progress = False
        while True:
            if button.is_pressed:
                

                led_white.off()
                led_yellow.off()
                led_red.off()
                led_blue.off()
                led_green.off()
                
                print("button pressed")
                if not in_progress:
                    in_progress = True
                    stop_event = threading.Event()
                    led_thread = threading.Thread(target=blink)
                    led_thread.start()
                    result = main()
                    stop_event.set()
                    led_thread.join()
                    print("thread end")
                    in_progress = False

                    show(result)

    else:
        while True:
            if button.is_pressed:
                os.system('sudo reboot')

            led_red.on()
            sleep(0.25)
            led_red.off()
            sleep(0.25)
