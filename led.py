import RPi.GPIO as GPIO
import sys, time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(0, GPIO.OUT, initial=GPIO.LOW)
GPIO.output(0, GPIO.LOW)

def blink(count, sleep1, sleep2):
    for i in range(0, count):
        GPIO.output(0, GPIO.HIGH)
        time.sleep(sleep1)
        GPIO.output(0, GPIO.LOW)
        time.sleep(sleep2)


if sys.argv[1] == 'start':
    blink(10, 0.05, 0.05)

if sys.argv[1] == 'T' or sys.argv[1] == 'A':
    blink(1, 3, 0)

if sys.argv[1] == 'M' or sys.argv[1] == 'H':
    blink(3, 0.5, 0.5)

if sys.argv[1] == 'P' or sys.argv[1] == 'V':
    blink(10, 0.1, 0.1)

if sys.argv[1] == 'N':
    blink(3, 0.1, 1)

if sys.argv[1] == 'C':
    blink(3, 1, 0.1)

if sys.argv[1] == 'B':
    blink(0, 0.00, 0.00)

