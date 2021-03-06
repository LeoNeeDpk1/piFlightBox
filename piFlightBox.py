import RPi.GPIO as GPIO
from parser import ConfigParser
from potentiometers import Potentiometers
from encoder import Encoder
from send import sender
from datetime import datetime
import string, time, os, sys

#Service variables. More info in config.py
chars = string.ascii_uppercase
red = '\033[31m'
green = '\033[32m'
orangebg = '\033[43m'
reset = '\033[00m'

#Check script start arguments
if "--status" in sys.argv:
    show_status = True
else:
    show_status = False
if  "--log" in sys.argv:
    logging = True
else:
    logging = False
if "--on-display" in sys.argv:
    status_on_disp = True
else:
    status_on_disp = False


#Check pin input status
def i(pin):
    return GPIO.input(pin)


def display_init():
    if settings_list["display"]:
        from display import Display
        global disp
        disp = Display()
        disp.row2 = display_list["greetings"]
        disp.show()
        time.sleep(0.5)
        try:
            disp.t1 = translation_list["modes"][state[display_list["third1pin"]]]
        except:
            disp.t1 = "==X=="
        try:
            disp.t2 = translation_list["modes"][state[display_list["third2pin"]]]
        except:
            disp.t2 = "==X=="
        try:
            disp.t3 = translation_list["modes"][state[display_list["third3pin"]]]
        except:
            disp.t3 = "=X=="
        disp.row2 = str(settings_list["ip"])
        disp.show()


#Display text update. Text of given 1 of 3 thirds of the first row and row 2. Ignoring row update if False.
def display_update(text, third, row2):
    if settings_list["display"]:
        if text:
            if third == 1:
                disp.t1 = text
            elif third == 2:
                disp.t2 = text
            elif third == 3:
                disp.t3 = text

        if row2:
            disp.row2 = row2

        disp.show()


#Show pins status if show_status is True. May cause spontaneous script stucks. For testing only
def status(changed):
    if status_on_disp and changed != "":
        display_update(str(changed) + ":" + str(state[changed]), 2, False)

    if show_status:
        print(gettime() + "|", end="", flush=True)
        for v in state:
            print(str(str(v) + ":" + green + str(state[v]).replace("1","V").replace("0", red + "X"+ reset) + reset +  "|"), end="", flush=True)
        print(orangebg + "<" + str(changed) + reset)


#Get current time for logging
def gettime():
    now = datetime.now().strftime("%H:%M:%S")
    now = str("[" + now + "]")
    return now


#Check pin status and send it via UDP packet to a PC with piFlightListener running on it
def sendToPC(channel):
    #Record pin status to a "state" variable
    if not type(state[channel]) is str:
        time.sleep(0.001) #Small pause to exclude fake button pressing and additional status check
        if state[channel] == i(channel):
            return
        state[channel] = i(channel)

    #Forming message to be sent to a PC
    try:
        message = str(state[translation_list["replacements"][channel]]) + str(state[channel])
    except:
        message = (str(channel) + str(state[channel]))

    sender(message, address)

    if logging:
        os.system('echo ' + gettime() + message + '  >> ' + path + 'log')

    status(channel)


#Rotation processing in "encoder.py"
def encoder(channel):
    for item in encoders_list:
        if str(channel) in item:
            e = encoders[item].rotate(channel, i(encoders_list[item][0]), i(encoders_list[item][1]))
            if e:
                 sendToPC(e)
            break


#Selection of encoder mode
def modeSelect(channel):
    for item in encoders_list:
        if channel == encoders_list[item][3]:
            if encoders_list[item][4].index(state[channel]) == len(encoders_list[item][4])-1:
                state[channel] = encoders_list[item][4][0]
            else:
                state[channel] = encoders_list[item][4][encoders_list[item][4].index(state[channel]) + 1]

            try:
                third = False
                if channel == display_list["third1pin"]:
                    third = 1
                elif channel == display_list["third2pin"]:
                    third = 2
                elif channel == display_list["third3pin"]:
                    third = 3

                if third:
                    display_update(translation_list["modes"][state[channel]], pins_list[channel]["display"], False)
            except:
                pass

            break


#========================= INITITALIZATION START =========================#
print("> init start")
#--------------------------------------------------------------------
#Config reading and main variables init.
conf = ConfigParser()
pins_list = conf.pins
translation_list = conf.translation
settings_list = conf.settings
potentiometers_list = conf.potentiometers
display_list = conf.display

state = {}
encoders_list = {}
encoders = {}
address = (str(settings_list["ip"]), settings_list["port"])
path = settings_list["path"]

#Pins init.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

for item in pins_list:
    GPIO.setup(item, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    if pins_list[item]["type"] == "button":
        GPIO.add_event_detect(item, GPIO.FALLING, callback=sendToPC, bouncetime=pins_list[item]["bouncetime"])
        state[item] = "B"
    elif pins_list[item]["type"] == "switch":
        GPIO.add_event_detect(item, GPIO.BOTH, callback=sendToPC, bouncetime=pins_list[item]["bouncetime"])
        state[item] = i(item)
    elif pins_list[item]["type"] == "mode":
        GPIO.add_event_detect(item, GPIO.FALLING, callback=modeSelect, bouncetime=pins_list[item]["bouncetime"])
        state[item] = pins_list[item]["modes"][0]
    elif "encoder" in pins_list[item]["type"]:
        GPIO.add_event_detect(item, GPIO.BOTH, callback=encoder, bouncetime=pins_list[item]["bouncetime"])
        state[item] = pins_list[item]["type"][-1:]

#Encoders init.
for item in conf.encoders:
    encoders_list[str(conf.encoders[item]["pin_left"]) + "_" + str(conf.encoders[item]["pin_right"])] = conf.encoders[item]["pin_left"], conf.encoders[item]["pin_right"], conf.encoders[item]["pin_push"], conf.encoders[item]["modechanger"], pins_list[(conf.encoders[item]["modechanger"])]["modes"]

for item in encoders_list:
    encoders[item] = Encoder(encoders_list[item][0], encoders_list[item][1])

#Arduino with potentiometers init
if settings_list["potentiometers"]:
    potentiometers = Potentiometers(address, potentiometers_list[1]["name"], potentiometers_list[1]["maxvalue"], potentiometers_list[2]["name"], potentiometers_list[2]["maxvalue"])

#Display initialization
display_init()
#--------------------------------------------------------------------
print("> init complete")
#========================= INITITALIZATION END =========================#

#Script starts here
print("> piFlightBox ready")
try:
    if show_status:
        print(orangebg + red + "               piFlightBox               " + reset)
        status("")

    while True:
        time.sleep(0.001) #Small sleep sequence to avoid high CPU load
        try:
            potentiometers.read(show_status)
        except KeyboardInterrupt:
            disp.quit()
        except:
            pass
except Exception as exc:
    print(exc)
except KeyboardInterrupt:
    if settings_list["display"]:
        disp.quit()
    else:
        exit(1)
