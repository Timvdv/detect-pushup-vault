
# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Servo standard servo example"""
import time
import board
import pwmio
from adafruit_motor import servo

# create a PWMOut object on Pin A2.
pwm = pwmio.PWMOut(board.D4, duty_cycle=2 ** 15, frequency=50)

# Create a servo object, my_servo.
my_servo = servo.Servo(pwm)

while True:
    my_servo.angle = 90
    # for angle in range(0, 180, 5):  # 0 - 180 degrees, 5 degrees at a time.
    #     my_servo.angle = angle
    #     time.sleep(0.05)
    # for angle in range(180, 0, -5): # 180 - 0 degrees, 5 degrees at a time.
    #     my_servo.angle = angle
    #     time.sleep(0.05)

# import RPi.GPIO as GPIO
# import time

# GPIO.setwarnings(False)
# servoPIN = 4
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servoPIN, GPIO.OUT)

# p = GPIO.PWM(servoPIN, 50) # GPIO 17 for PWM with 50Hz
# p.start(2.5) # Initialization
# try:
#   while True:
#     p.ChangeDutyCycle(5)
#     time.sleep(0.5)
# #    p.ChangeDutyCycle(7.5)
# #    time.sleep(0.5)
# #    p.ChangeDutyCycle(10)
# #    time.sleep(0.5)
# #    p.ChangeDutyCycle(12.5)
# #    time.sleep(0.5)
#     p.ChangeDutyCycle(10)
#     time.sleep(0.5)
# #    p.ChangeDutyCycle(7.5)
# #    time.sleep(0.5)
# #    p.ChangeDutyCycle(5)
# #    time.sleep(0.5)
# #    p.ChangeDutyCycle(2.5)
# #    time.sleep(0.5)
# except KeyboardInterrupt:
#   p.stop()
#   GPIO.cleanup()
