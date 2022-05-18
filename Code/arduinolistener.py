import serial, time, sys
from send import sender

class ArduinoListener():
    def __init__(self):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.pot1 = ""
        self.pot2 = ""

    def read(self, show_status):
        self.ser.flushInput()
        serialdata=self.ser.readline()
        s = serialdata.decode('utf-8').split(',')
        s[0] = int(s[0])
        s[1] = int(s[1])

        if self.pot1 != s[0]:
            self.pot1 = s[0]
            sender("POT1_" + str(s[0]))
        if self.pot2 != s[1]:
            self.pot2 = s[1]
            sender("POT2_" + str(s[1]))

        if show_status:
            print(s[0],"|",s[1])
