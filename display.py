from rpi_lcd import LCD
import time

lcd = LCD()

class Display:
    def __init__(self):
        self.t1 = "     "
        self.t2 = "     "
        self.t3 = "    "
        self.row2 = " "


    def show(self):
        lcd.text(self.t1+"|"+self.t2+"|"+self.t3, 1)
        lcd.text(self.row2, 2)


    def quit(self):
        lcd.text("piFlightBox",1)
        lcd.text("terminated", 2)
        time.sleep(1)
        lcd.clear()
        exit(1)
