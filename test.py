#!/usr/bin/env python3
# encoding:utf-8

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

TRIG = 15
ECHO = 14

print("Distance measurement in progress")

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

try:
    while True:
        GPIO.output(TRIG, False)
        print("Waiting For Sensor To Settle")
        time.sleep(2)

        # Send 10us pulse to trigger
        GPIO.output(TRIG, True)
        time.sleep(0.00001)
        GPIO.output(TRIG, False)

        # Wait for echo start
        pulse_start = time.time()
        timeout = pulse_start + 0.04  # 40ms timeout
        while GPIO.input(ECHO) == 0 and time.time() < timeout:
            pulse_start = time.time()

        # Wait for echo end
        pulse_end = time.time()
        timeout = pulse_end + 0.04
        while GPIO.input(ECHO) == 1 and time.time() < timeout:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150
        distance = round(distance, 2)

        if 2 <= distance <= 400:  # sensor’s reliable range
            print("Distance:", distance, "cm")
        else:
            print("Out Of Range")

except KeyboardInterrupt:
    print("\nMeasurement stopped by User")
    GPIO.cleanup()
