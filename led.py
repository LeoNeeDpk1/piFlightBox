import RPi.GPIO as GPIO
import sys, time

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

if sys.argv[1] == 'start':
    blink(10, 0.05, 0.05, 0)

if sys.argv[1] == 'E' or sys.argv[1] == 'A':
    #blink(1, 2, 0)
    blink(1, 0.5, 0, 0)

if sys.argv[1] == 'T' or sys.argv[1] == 'H':
    #blink(2, 0.5, 0.5)
    blink(1, 0.5, 0, 21)

if sys.argv[1] == 'M' or sys.argv[1] == 'V':
    #blink(10, 0.1, 0.1)
    blink(1, 0.5, 0, 22)

if sys.argv[1] == 'P' or sys.argv[1] == 'N':
    #blink(2, 0.1, 1)
    blink(1, 0.1, 0, 0)
    blink(1, 0.1, 0, 21)
    blink(1, 0.1, 0, 22)

if sys.argv[1] == 'C':
    blink(2, 1, 0.1)

if sys.argv[1] == 'B':
    blink(0, 0.00, 0.00)

