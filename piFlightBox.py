import RPi.GPIO as GPIO
import config, memcache, random, string, time, os, sys
from datetime import datetime

pc = memcache.Client([config.address], debug=0)

chars = string.ascii_uppercase
red = '\033[31m'
green = '\033[32m'
orangebg = '\033[43m'
reset = '\033[00m'

enc1 = 0
enck1 = 0
enc2 = 0
enck2 = 0

GPIO.setmode(GPIO.BCM)
GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Master switch
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Alternator switch
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Avionics switch
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Parking break
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Nav lights switch
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Beacon lights switch
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Strobe lights switch
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Taxi lights switch
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Landing lights switch
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Pitot heat switch
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #AP button
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #APPR button
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Landing gear switch

GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_push_mode_select: Thrust, Mixture, Prop
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_rotate
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_rotate

GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #button(encoder2_mode_dependency: AP ALT, AP HDG, AP NAV)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_push_mode_select: ALT, HDG, NAV, COM
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate

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
    to_send = ('*' + randchars() + '*' + message).replace("17", state[16]).replace("18", state[16]).replace("24", state[25]).replace("26", state[25]).replace("27", state[25])
    pc.set('input', to_send)
    os.system('echo ' + gettime() + to_send + '  >> ' + config.path + 'log')
    status(channel)


#==================ENCODERS START===========
def encoder1(channel):
    global enc1
    global enck1
    if i(17) == i(18):
        return
    if enc1 != 0:
        enc1 = 0
        return
    else:
        enc1 = 1
        if channel == 17:
            if enck1 < 1:
               enck1 += 1
        else:
            if enck1 > -1:
                enck1 -= 1

        if channel == 17 and enck1 > 0:
            sendToPC(channel)
        if channel == 18 and enck1 < 0:
            sendToPC(channel)


def encoder2(channel):
    global enc2
    global enck2
    if i(26) == i(27):
        return
    if enc2 != 0:
        enc2 = 0
        return
    else:
        enc2 = 1
        if channel == 26:
            if enck2 < 1:
                enck2 += 1
        else:
            if enck2 > -1:
                enck2 -= 1

        if channel == 26 and enck2 > 0:
            sendToPC(channel)
        if channel == 27 and enck2 < 0:
            sendToPC(channel)


def modeSelect(channel):
#Encoder1
#T = thrust; M = mixture; P = propeller

#Encoder2
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

    if state[channel] == "T":
        state[channel] = "M"
        status(channel)
        return

    if state[channel] == "M":
        state[channel] = "P"
        status(channel)
        return

    if state[channel] == "P":
        state[channel] = "T"
        status(channel)
        return
#================ENCODERS END===================


def randchars():
    global chars
    r = ''.join(random.choice(chars) for c in range(6))
    return r


state = {1:i(1), 4:i(4), 5:i(5), 6:i(6), 7:i(7), 8:i(8), 9:i(9), 10:i(10), 11:i(11), 12:i(12),
13:"B", 14:"B", 15:i(15), 16:"T", 17:"-", 18:"+", 24:"B", 25:"A", 26:"-", 27:"+"}

GPIO.add_event_detect(1, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(4, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(5, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(6, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(7, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(8, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(9, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(10, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(11, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(12, GPIO.BOTH, callback=sendToPC, bouncetime=100)
GPIO.add_event_detect(13, GPIO.RISING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(14, GPIO.RISING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(15, GPIO.BOTH, callback=sendToPC, bouncetime=100)
#Encoder1
GPIO.add_event_detect(16, GPIO.RISING, callback=modeSelect, bouncetime=250)
GPIO.add_event_detect(17, GPIO.BOTH, callback=encoder1, bouncetime=10)
GPIO.add_event_detect(18, GPIO.BOTH, callback=encoder1, bouncetime=10)
#===
GPIO.add_event_detect(24, GPIO.RISING, callback=sendToPC, bouncetime=550)
#Encoder2
GPIO.add_event_detect(25, GPIO.RISING, callback=modeSelect, bouncetime=250)
GPIO.add_event_detect(26, GPIO.BOTH, callback=encoder2, bouncetime=10)
GPIO.add_event_detect(27, GPIO.BOTH, callback=encoder2, bouncetime=10)
#===

if show_status:
    print(orangebg + red + "               piFlightBox               " + reset)
    status("")

try:
    while True:
        time.sleep(0.1)
except Exception as exc:
    print(exc)
