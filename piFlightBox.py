import RPi.GPIO as GPIO
import config, memcache, random, string, time, os, sys
from datetime import datetime

pc = memcache.Client([config.address], debug=0)

chars = str(string.ascii_uppercase) + str(string.digits)
red = '\033[31m'
green = '\033[32m'
orangebg = '\033[43m'
reset = '\033[00m'

e = 0
k = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #switch
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #button(encoder_mode_select)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder_push
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder_rotate
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder_rotate

ignorestatus = config.ignore

if "-status" in sys.argv:
    show_status = True
else:
    show_status = False


def i(pin):
    return GPIO.input(pin)


def status(changed):
    global show_status
    if not show_status:
        return
    print(gettime() + "|", end="", flush=True)
    for v in state:
        print(str(str(v) + ":" + green + str(state[v]).replace("1","V").replace("0", red + "X"+ reset) + reset +  "|"), end="", flush=True)
    print(orangebg + "<" + str(changed) + reset)


def gettime():
    now = datetime.now().strftime("%H:%M:%S")
    now = str("[" + now + "]")
    return now


def sendToPC(channel):
    time.sleep(0.1)
    global state
    global ingnorestatus

    if state[channel] == i(channel) and not channel in ignorestatus: #Дополнительная проверка состояния пина
        return

    if not channel in ignorestatus:
        state[channel] = i(channel)

    message = str(channel) + str(state[channel])
    to_send = ('*' + randchars() + '*' + message).replace("25", state[24]).replace("26", state[24]).replace("27", state[24])
    pc.set('input', to_send)
    os.system('echo ' + gettime() + to_send + '  >> ' + config.path + 'log')
    status(channel)

#==================ENCODER START===========
def encoder(channel):
    global e
    global k
    #Практически полностью исключаются вкрапления одного показания среди другого.
    #Побочный эффект - некоторая "инерция" показаний при начале вращения ручки в другую сторону.
    if e != 0:
        e = 0
        return
    else:
        if channel == 26:
            if k < 3:
                k += 1
        else:
            if k > -3:
                k -= 1

        if channel == 26 and k > 2:
            sendToPC(channel)
        if channel == 27 and k < -2:
            sendToPC(channel)


def modeSelect(channel):
#A = alt; H = heading; N = nav; C = com; B = baro
    if state[channel] == "A":
        state[channel] = "H"
        status(channel)
        return

    if state[channel] == "H":
        state[channel] = "N"
        status(channel)
        return

    if state[channel] == "N":
        state[channel] = "C"
        status(channel)
        return

    if state[channel] == "C":
        state[channel] = "B"
        status(channel)
        return

    if state[channel] == "B":
        state[channel] = "A"
        status(channel)
        return

#================ENCODER END===================

def randchars():
    global chars
    r = ''.join(random.choice(chars) for _ in range(6))
    return r


state = {1:i(1), 4:i(4), 5:i(5), 6:i(6), 7:i(7), 8:i(8), 9:i(9), 10:i(10), 11:i(11), 24:"A", 25:"B", 26:"-", 27:"+"}

GPIO.add_event_detect(1, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(4, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(5, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(6, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(7, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(8, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(9, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(10, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(11, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(24, GPIO.RISING, callback=modeSelect, bouncetime=500)
GPIO.add_event_detect(25, GPIO.FALLING, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(26, GPIO.BOTH, callback=encoder, bouncetime=10)
GPIO.add_event_detect(27, GPIO.BOTH, callback=encoder, bouncetime=10)

if show_status:
    print(orangebg + red + "               piFlightBox               " + reset)
    status("")

try:
    while True:
        time.sleep(0.1)
except Exception as exc:
    print(exc)
