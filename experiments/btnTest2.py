#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(36, GPIO.IN, pull_up_down=GPIO.PUD_UP)

oldButtonState1 = True
while True:
    buttonState1 = GPIO.input(36)

    if buttonState1 != oldButtonState1 and buttonState1 == False :
        print("Button Pressed")

    oldButtonState1 = buttonState1

    time.sleep(.1)