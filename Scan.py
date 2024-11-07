from time import sleep
import RPi.GPIO as gpio
import math
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
import numpy as np
import qwiic_vl53l1x
from gpiozero import LED

# Initialize the sensor
my_sensor = qwiic_vl53l1x.QwiicVL53L1X()
my_sensor.sensor_init()
my_sensor.set_distance_mode(1)

# GPIO pin setup
DIR_PIN = 21
PUL_PIN = 20
ENB_PIN = 12
CW = 0  # Clockwise
CCW = 1  # Counterclockwise
DIAMETER = 1.47  # Diameter in inches
SPR = 400  # Steps per revolution
gpio.setmode(gpio.BCM)
gpio.setup(DIR_PIN, gpio.OUT)
gpio.setup(PUL_PIN, gpio.OUT)
gpio.setup(ENB_PIN, gpio.OUT)
gpio.output(DIR_PIN, CW)
gpio.output(ENB_PIN, 1)

# Camera setup
picamera = Picamera2()
video_config = picamera.create_video_configuration()
picamera.configure(video_config)
picamera.set_controls({"ExposureValue": 0, "FrameRate": 18, "AwbEnable": False})
encoder = H264Encoder(10000000)


# Function to get distance
def get_distance():
    my_sensor.start_ranging()
    sleep(0.1)
    distance = my_sensor.get_distance()  # Get distance in mm
    my_sensor.stop_ranging()
    my_sensor.clear_interrupt()
    distance = (distance / 10) / 2.54  # Convert to inches
    return distance


def get_median(i):
    results = []
    for _ in range(i):
        distance = get_distance()
        results.append(distance)
    return np.median(results)

def callibration():
    start = 13.5
    for i in range(5):
        print("Getting distance...")
        median = get_median(10)
        if median >= (start+0.2) or median <= (start-0.2):
            print(median)
            print("Wrong position")
            if (int(median - start)) > 0:
                stepper_move(int((median - start)/1.47/math.pi*400), CCW, step_delay=0.0030)
            else:
                stepper_move(int((start - median)/1.47/math.pi*400), CW, step_delay=0.0030)
        else:
            print("Correct position")
            print(median)
            return True

    print("Callibration failed")
    return False

def move(direction, inch):
    steps = (inch * 85)
    if steps <= 200:
        stepper_move(steps, direction, accel_steps = 0)
    else:
        stepper_move(steps, directon)

# Function to move stepper motor
def stepper_move(steps, direction, step_delay=0.00075, accel_steps=100):
    if steps < 200:
        accel_steps = 0

    start_time = 0.0017
    end_time = step_delay
    time_delays = np.geomspace(start_time, end_time, accel_steps, endpoint=True)
    time_delays_reversed = time_delays[::-1]

    gpio.output(DIR_PIN, direction)

    picamera.start()

    # Accelerate
    for delay in time_delays:
        gpio.output(PUL_PIN, gpio.HIGH)
        sleep(delay)
        gpio.output(PUL_PIN, gpio.LOW)
        sleep(delay)

    # Maintain constant speed
    for _ in range(steps - 2 * accel_steps):
        gpio.output(PUL_PIN, gpio.HIGH)
        sleep(step_delay)
        gpio.output(PUL_PIN, gpio.LOW)
        sleep(step_delay)

    # Decelerate
    for delay in time_delays_reversed:
        gpio.output(PUL_PIN, gpio.HIGH)
        sleep(delay)
        gpio.output(PUL_PIN, gpio.LOW)
        sleep(delay)

    picamera.stop()

def Motor_on():
    gpio.output(ENB_PIN, 0)
    sleep(0.2)
    
def Motor_off():
    gpio.output(ENB_PIN, 1)
    sleep(0.2)
    
# Scan process function
def scan(file_name, speed=15):
    step_delay = (DIAMETER * math.pi) / (400 * speed)
    step_delay = round(step_delay, 5)

    output = FfmpegOutput(file_name)
    Motor_on()
    picamera.start_recording(encoder, output)

    stepper_move(1240, CW, step_delay)

    stepper_move(1240, CCW, step_delay)

    picamera.stop_recording()
    Motor_off()
    sleep(1.8)
