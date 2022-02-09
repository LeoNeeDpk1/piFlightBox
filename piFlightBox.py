import RPi.GPIO as GPIO
import config, string, time, os, sys, display, potentiometers
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
    global disp
    disp = display.Display()
    disp.row2 = "piFlightBox up"
    disp.show()
    time.sleep(0.5)
    disp.t1 = state[22].replace("A", "ALT").replace("H", "HDG").replace("V", "VS")
    disp.t3 = state[23].replace("E", "ELEV").replace("B", "BARO")
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
    global status_on_disp

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
    global state

    #Small pause to exclude fake button pressing and additional status check
    time.sleep(0.001)
    if state[channel] == i(channel):
        return

    #Record pin status to a "state" variable
    if not type(state[channel]) is str:
        state[channel] = i(channel)

    #Forming message to be sent to a PC
    message = (str(channel) + str(state[channel])).replace("16", state[22]).replace("17", state[22]).replace("18", state[22]).replace("25", state[23]).replace("26", state[23]).replace("27", state[23])
    sender(message)

    if logging:
        os.system('echo ' + gettime() + message + '  >> ' + config.path + 'log')

    status(channel)


#Rotation processing in "encoder.py"
#>Add new if statement for new encoder<
def encoder(channel):
    if enc1.p_l <= channel <= enc1.p_r:
        e = enc1.rotate(channel, i(enc1.p_l), i(enc1.p_r))
    if enc2.p_l <= channel <= enc2.p_r:
        e = enc2.rotate(channel, i(enc2.p_l), i(enc2.p_r))


    if e:
        sendToPC(e)


#Selection of encoder mode or piFlightListener mode
def modeSelect(channel):
    print (encoders["17"].test())
    pass
    #print(enc1.__class__.__name__)


#========================= INITITALIZATION START =========================#
#--------------------------------------------------------------------

#Pins init. >Add your buttons/switches/encoder/etc here<
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Master switch
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Alternator switch
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Avionics switch
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Parking break
GPIO.setup(7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Beacon lights
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Strobe lights
GPIO.setup(9, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Taxi lights
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Landing lights
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #AP
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #NAV lights
GPIO.setup(14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Pitot heat
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Landing gear switch
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_push
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_rotate
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder1_rotate
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Flaps up button
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #Flaps down button
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #enc1 mode
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #enc2 mode
GPIO.setup(24, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_push
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate
GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) #encoder2_rotate

#Event triggers. >Add your buttons/switches/etc here<
GPIO.add_event_detect(1, GPIO.FALLING, callback=sendToPC, bouncetime=250)
GPIO.add_event_detect(4, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(5, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(6, GPIO.BOTH, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(7, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(8, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(9, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(10, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(11, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(12, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(13, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(14, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(15, GPIO.BOTH, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(19, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(20, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(22, GPIO.FALLING, callback=modeSelect, bouncetime=550)
GPIO.add_event_detect(23, GPIO.FALLING, callback=modeSelect, bouncetime=550)
GPIO.add_event_detect(24, GPIO.FALLING, callback=sendToPC, bouncetime=550)
#Encoder1 pins
GPIO.add_event_detect(16, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(17, GPIO.BOTH, callback=encoder, bouncetime=10)
GPIO.add_event_detect(18, GPIO.BOTH, callback=encoder, bouncetime=10)
#Encoder2 pins
GPIO.add_event_detect(25, GPIO.FALLING, callback=sendToPC, bouncetime=550)
GPIO.add_event_detect(26, GPIO.BOTH, callback=encoder, bouncetime=10)
GPIO.add_event_detect(27, GPIO.BOTH, callback=encoder, bouncetime=10)

#Encoders init. Encoder(pin_of_left_rotation, pin_of_right_rotation) >Add your encoders here<
encoders = {}

encoders[str((config.encoders[0])[0])] = Encoder((config.encoders[0])[0], (config.encoders[0])[1], (config.encoders[0])[2], (config.encoders[0])[3])


'''for item in config.encoders:
    l = []
    for k in item:
        print(k)

print((config.encoders[1])[2])'''




'''encoders = {
    "1":Encoder(17, 18, 22, ["A", "H", "V"])
    

}'''
#enc1 = Encoder(17, 18, 22, ["A", "H", "V"])
#print((enc1).__name__)
#enc2 = Encoder(26, 27, 23, ["E", "B"])
#enc1modes = ["A", "H", "V"]
#enc2modes = ["E", "B"]

#Arduino with potentiometers init
potentiometers = potentiometers.Listener()

#Main variable with pin status. >Add your buttons/switches/etc here<
state = {1:"B", 4:"B", 5:"B", 6:i(6), 7:"B", 8:"B", 9:"B", 10:"B", 11:"B", 12:"B",
13:"B", 14:"B", 15:i(15), 16:"B", 17:"-", 18:"+", 19:"B", 20:"B", 22:"A", 23:"E", 24:"B", 25:"B", 26:"-", 27:"+"}

#Display initialization
display_init()

#--------------------------------------------------------------------
#========================= INITITALIZATION END =========================#


#Script starts here
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
    disp.quit()
