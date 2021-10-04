from pynput.keyboard import Key, Controller
import memcache, time, pyautogui, os
import win32com.client as comclt

#wsh = comclt.Dispatch("WScript.Shell")
#wsh.AppActivate("Microsoft Flight Simulator")
keyboard = Controller()

shared = memcache.Client(['192.168.1.132:11211'], debug=0)
prev_data = shared.get('Value')

while True:
    data = shared.get('Value')
    if not prev_data == data:
        prev_data = data
        print(shared.get('Value'))
        try:
            os.system("keypress.py 66")
            #keyboard.press(str(data))
            #keyboard.release(str(data))
            #wsh.SendKeys(data)
        except exception as e:
            print(e)
            None

    time.sleep(0.1)