import serial, config
from send import sender

class Listener():
    def __init__(self, address):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.pot1 = ""
        self.pot2 = ""
        self.address = address

    def read(self, show_status):
        self.ser.flushInput()
        serialdata=self.ser.readline()
        s = serialdata.decode('utf-8').split(',')
        s[0] = round(config.pot1maxvalue * (round((int(s[0])/1023)*100)) / 100)
        s[1] = round(config.pot2maxvalue * (round((int(s[1])/1023)*100)) / 100)

        if self.pot1 != s[0]:
            self.pot1 = s[0]
            sender(config.pot1name + ":" + str(s[0]), self.address)
        if self.pot2 != s[1]:
            self.pot2 = s[1]
            sender(config.pot2name + ":" + str(s[1]), self.address)

        if show_status:
            print(s[0],"|",s[1])

            
