import RPi.GPIO as gpio
import qwiic_vl53l1x

import numpy as np
from time import sleep

import math
import Camera

# Initialize the dtance sensor
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

# Convert inch to steps
def inch_2_steps(inch):
    return int(((inch * SPR)/ DIAMETER) / math.pi)

# Convert mm to inch
def mm_2_inch(mm):
    return ((mm / 10) / 2.54)

# Functions for Motor Control
def motor_on():
    gpio.output(ENB_PIN, 0)
    sleep(0.25)

def motor_off():
    gpio.output(ENB_PIN, 1)
    sleep(0.25)

# Function to get distance
def get_distance():
    my_sensor.start_ranging()
    sleep(0.05)
    distance = my_sensor.get_distance()  # Get distance in mm
    my_sensor.stop_ranging()
    my_sensor.clear_interrupt()
    return mm_2_inch(distance)

# Get median among i distance measurements
def get_median_dis(i):
    results = []
    for _ in range(i):
        distance = get_distance()
        results.append(distance)
    return np.median(results)

# Callibration at every beginning of the scan
def callibration():
    # Starting position
    start = 13.5
    range = 0.2

    # Check position for 5 times
    for i in range(5):
        print("Getting distance...")
        median = get_median_dis(10)
        if median >= (start + range) or median <= (start - range):
            print(median)
            print("Wrong position")

            d = (median - start) if (median > start) else (start - median)

            motor_on()
            stepper_move(inch_2_steps(d), CCW, step_delay=0.003)
            motor_off()

        else:
            print(median)
            print("Correct position")
            return True

    print("Callibration failed")
    return False

# Function to move stepper motor
def stepper_move(steps, direction, step_delay=0.00075, accel_steps=50):

    # Enable acceleration only when steps > 200
    if steps < 200:
        accel_steps = 0

    start_time = 0.0017
    end_time = step_delay
    time_delays = np.geomspace(start_time, end_time, accel_steps, endpoint=True)
    time_delays_reversed = time_delays[::-1]

    gpio.output(DIR_PIN, direction)

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

# Scan process function
def scan(filename, speed=15):
    step_delay = (DIAMETER * math.pi) / (400 * speed)
    step_delay = round(step_delay, 5)

    Camera.start_video(filename)
    motor_on()

    stepper_move(1240, CW, step_delay, 100)

    stepper_move(1240, CCW, step_delay, 100)

    motor_off()
    Camera.stop_video()

    sleep(1.8)