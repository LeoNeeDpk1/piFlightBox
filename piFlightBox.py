import RPi.GPIO as GPIO
import config, string, time, os, sys, display
from led import scenario as led
from send import sender
from encoder import Encoder
from datetime import datetime



#Service variables. More info in config.py
chars = string.ascii_uppercase
red = '\033[31m'
green = '\033[32m'
orangebg = '\033[43m'
reset = '\033[00m'
ignorestatus = config.ignore

#Check script start arguments
if "-status" in sys.argv:
    show_status = True
else:
    show_status = False
if  "-log" in sys.argv:
    logging = True
else:
    logging = False


#Check pin input status
def i(pin):
    return GPIO.input(pin)


def display_init():
    global disp
    disp = display.Display()
    disp.row2 = "piFlightBox up"
    disp.show()
    time.sleep(1)
    disp.t1 = state[25].replace("A", "ALT  ").replace("H", "HDG  ").replace("V", "VS   ")
    disp.row2 = str(config.address[0])
    disp.show()


#Display text update. Text of given 1 of 3 thirds of the first row and row 2. Ignoring row update if False.
def display_update(text, third, row2):
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
    global show_status
    if not show_status:
        return
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
    global state
    global ingnorestatus

    #Small pause to exclude fake button pressing and additional status check
    time.sleep(0.001)
    if state[channel] == i(channel) and not channel in ignorestatus:
        return

    #Record pin status to a "state" variable
    if not channel in ignorestatus:
        state[channel] = i(channel)

    #Forming message to be sent to a PC
    message = (str(channel) + str(state[channel])).replace("17", state[16]).replace("18", state[16]).replace("26", state[25]).replace("27", state[25])
    sender(message)

    if logging:
        os.system('echo ' + gettime() + message + '  >> ' + config.path + 'log')

    status(channel)


#Rotation processing in "encoder.py"
#>Add new if statement for new encoder<
def encoder(channel):
    if 17 <= channel <= 18:
        e = enc1.rotate(channel, i(17), i(18))
    if 26 <= channel <= 27:
        e = enc2.rotate(channel, i(26), i(27))

    if e:
        sendToPC(e)


#Selection of encoder mode or piFlightListener mode
#piFlightListener modes should start with "!m_" prefix
#Encoder1: T = thrust; M = mixture; P = propeller; E = elevator (pitch trim)
#Encoder2: A = alt; H = heading; V = VS; N = nav; C = com; B = baro
def modeSelect(channel):
    enc1modes = ["A", "H", "V"]

    if channel == 25:
        if enc1modes.index(state[channel]) == len(enc1modes)-1:
            state[channel] = enc1modes[0]
        else:
            state[channel] = enc1modes[enc1modes.index(state[channel]) + 1]

    m = state[channel].replace("A", "ALT  ").replace("H", "HDG  ").replace("V", "VS   ")
    display_update(m, 1, False)


#========================= INITITALIZATION =========================#
#Pins init. >Add your buttons/switches/encoder/etc here<
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Flaps up button
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Flaps down button
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Anti-Ice button
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_push_mode_select: ALT, HDG, NAV, COM
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate

#Encoders init. Encoder(pin_of_left_rotation, pin_of_right_rotation) >Add your encoders here<
enc1 = Encoder(17, 18)
enc2 = Encoder(26, 27)

#Main variable with pin status. Pins in "ignorestatus" ignore state changes. >Add your buttons/switches/etc here<
state = {1:i(1), 4:i(4), 5:i(5), 6:i(6), 7:i(7), 8:i(8), 9:i(9), 10:i(10), 11:i(11), 12:i(12),
13:"B", 14:"B", 15:i(15), 16:"E", 17:"-", 18:"+", 19:"B", 20:"B", 24:"B", 25:"A", 26:"-", 27:"+"}

#Event triggers. >Add your buttons/switches/etc here<
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
#GPIO.add_event_detect(16, GPIO.RISING, callback=modeSelect, bouncetime=250)
GPIO.add_event_detect(17, GPIO.BOTH, callback=encoder, bouncetime=10)
GPIO.add_event_detect(18, GPIO.BOTH, callback=encoder, bouncetime=10)
#===
GPIO.add_event_detect(19, GPIO.RISING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(20, GPIO.RISING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(24, GPIO.RISING, callback=sendToPC, bouncetime=550)
#Encoder2
GPIO.add_event_detect(25, GPIO.RISING, callback=modeSelect, bouncetime=450)
GPIO.add_event_detect(26, GPIO.BOTH, callback=encoder, bouncetime=10)
GPIO.add_event_detect(27, GPIO.BOTH, callback=encoder, bouncetime=10)
#===

#Script starts here
try:
    if show_status:
        print(orangebg + red + "               piFlightBox               " + reset)
        status("")

    display_init()

    while True:
        time.sleep(0.001) #Small sleep sequence to avoid high CPU load
except Exception as exc:
    print(exc)
except KeyboardInterrupt:
    disp.quit()
