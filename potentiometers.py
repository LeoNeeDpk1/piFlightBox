import serial
from send import sender

class Potentiometers():
    def __init__(self, address, po1name, pot1maxvalue, pot2name, pot2maxvalue):
        self.ser = serial.Serial('/dev/ttyUSB0', 9600)
        self.pot1value = ""
        self.pot2value = ""
        self.pot1name = po1name
        self.pot2name = pot2name
        self.pot1maxvalue = pot1maxvalue
        self.pot2maxvalue = pot2maxvalue
        self.address = address

    def read(self, show_status):
        self.ser.flushInput()
        serialdata=self.ser.readline()
        s = serialdata.decode('utf-8').split(',')
        s[0] = round(self.pot1maxvalue * (round((int(s[0])/1023)*100)) / 100)
        s[1] = round(self.pot2maxvalue * (round((int(s[1])/1023)*100)) / 100)

        if self.pot1value != s[0]:
            self.pot1value = s[0]
            sender(self.pot1name + ":" + str(s[0]), self.address)
        if self.pot2value != s[1]:
            self.pot2value = s[1]
            sender(self.pot2name + ":" + str(s[1]), self.address)

        if show_status:
            print(s[0],"|",s[1])

            
