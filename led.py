import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(0, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(21, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(22, GPIO.OUT, initial=GPIO.LOW)

def blink(count, sleep1, sleep2, pin):
    for i in range(0, count):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(sleep1)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(sleep2)

def scenario(s):
    if s == 'start':
        blink(10, 0.05, 0.05, 0)

    if s == 'E' or s == 'A':
        blink(1, 0.5, 0, 0)

    if s == 'T' or s == 'H':
        blink(1, 0.5, 0, 21)

    if s == 'M' or s == 'V':
        blink(1, 0.5, 0, 22)

    if s == 'P' or s == 'N':
        blink(1, 0.1, 0, 0)
        blink(1, 0.1, 0, 21)
        blink(1, 0.1, 0, 22)

    if s == 'C':
        blink(2, 1, 0.1)

    if s == 'B':
        blink(0, 0.00, 0.00)

