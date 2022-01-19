import serial, time

#ser = serial.Serial('/dev/ttyUSB0', timeout=None, baudrate=9600, xonxoff=False, rtscts=False, dsrdtr=False)
ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
    ser.flushInput()
    serialdata=ser.readline()
    s = serialdata.decode('utf-8').split(',')
    s[0] = int(s[0])
    s[1] = int(s[1])

    print(s[0],"|",s[1])

    #time.sleep(0.01)
